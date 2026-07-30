"""
Auto-validación de facturas en ARCA.
Background task que cada N segundos busca facturas de HOY sin CAE y las valida.
"""
import asyncio
import logging
import time
from datetime import datetime, date

from app.config import get_config, save_config, load_config
from app.database import SessionLocal
from app.models.user import User, UserPuntoVenta
from app.models.cae_log import CAELog
from app.services import factusol_service, arca_service

logger = logging.getLogger("auto_validate")

# Estado del auto-validador
_task: asyncio.Task | None = None
_running = False
_last_run: str | None = None
_last_result: str = ""
_log_lines: list[dict] = []   # últimas N líneas de log

# Momento en que se vio por primera vez cada factura pendiente:
#   {(tipfac, codfac): timestamp monotonic}
# Se usa para la "espera de gracia" del modo mostrador: no validar una factura
# recien creada hasta que lleve N segundos estable, asi no se manda a AFIP a
# medio cargar (el operador todavia esta agregando lineas).
_first_seen: dict[tuple, float] = {}

DEFAULT_INTERVAL = 60
DEFAULT_GRACE = 10
MIN_INTERVAL = 5
MAX_INTERVAL = 600


def _add_log(msg: str, level: str = "info"):
    """Agrega línea al log circular (max 50)."""
    _log_lines.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "msg": msg,
        "level": level,
    })
    if len(_log_lines) > 50:
        _log_lines.pop(0)
    prefix = "⚠️" if level == "error" else "✅" if level == "success" else "🔄"
    logger.info(f"{prefix} [AutoCAE] {msg}")


def _defaults() -> dict:
    return {
        "enabled": False,
        "interval_seconds": DEFAULT_INTERVAL,
        "grace_seconds": DEFAULT_GRACE,
    }


def get_status() -> dict:
    """Devuelve el estado actual del auto-validador."""
    av = get_config().get("auto_validate", {})
    return {
        "enabled": av.get("enabled", False),
        "running": _running,
        "interval_seconds": av.get("interval_seconds", DEFAULT_INTERVAL),
        "grace_seconds": av.get("grace_seconds", DEFAULT_GRACE),
        "last_run": _last_run,
        "last_result": _last_result,
        "log": _log_lines[-20:],
    }


def toggle(enabled: bool) -> dict:
    """Enciende o apaga el auto-validador."""
    config = load_config()
    if "auto_validate" not in config:
        config["auto_validate"] = _defaults()
    config["auto_validate"]["enabled"] = enabled
    save_config(config)

    if enabled:
        _add_log("Modo automático ACTIVADO", "success")
        start_background_task()
    else:
        _add_log("Modo automático DESACTIVADO", "info")
        stop_background_task()

    return get_status()


def set_interval(seconds: int) -> dict:
    """Cambia el intervalo de chequeo (5-600 segundos).

    Los valores por debajo de 30s son el "modo mostrador": la consulta a
    Factusol esta acotada a las facturas de HOY, asi que es barata y se puede
    repetir cada pocos segundos sin castigar la base.
    """
    config = load_config()
    if "auto_validate" not in config:
        config["auto_validate"] = _defaults()
    config["auto_validate"]["interval_seconds"] = max(MIN_INTERVAL, min(MAX_INTERVAL, int(seconds)))
    save_config(config)
    _add_log(f"Intervalo de chequeo: cada {config['auto_validate']['interval_seconds']}s", "info")
    return get_status()


def set_grace(seconds: int) -> dict:
    """Cambia la espera de gracia (0-300 segundos).

    Una factura recien aparecida en Factusol no se valida hasta que lleve al
    menos estos segundos visible. Protege del caso mostrador: el operador crea
    la factura y sigue cargando lineas, y un chequeo muy rapido la mandaria a
    AFIP incompleta (error fiscal que despues hay que corregir con una NC).
    0 = validar apenas aparece.
    """
    config = load_config()
    if "auto_validate" not in config:
        config["auto_validate"] = _defaults()
    config["auto_validate"]["grace_seconds"] = max(0, min(300, int(seconds)))
    save_config(config)
    g = config["auto_validate"]["grace_seconds"]
    _add_log(f"Espera de gracia: {'sin espera' if g == 0 else f'{g}s'}", "info")
    return get_status()


def set_payment_filters(fopfac_codes: list[str]) -> dict:
    """Guarda las formas de pago permitidas para auto-validación.
    Lista vacía = todas permitidas.
    """
    config = load_config()
    if "auto_validate" not in config:
        config["auto_validate"] = _defaults()
    config["auto_validate"]["fopfac_codes"] = fopfac_codes
    save_config(config)
    _add_log(
        f"Filtro formas de pago: {'todas' if not fopfac_codes else f'{len(fopfac_codes)} seleccionada(s)'}",
        "info",
    )
    return {"fopfac_codes": fopfac_codes}


def get_payment_filters() -> dict:
    """Devuelve las formas de pago configuradas."""
    config = get_config()
    codes = config.get("auto_validate", {}).get("fopfac_codes", [])
    return {"fopfac_codes": codes}


# ── Background loop ──────────────────────────────────────────────────────────

async def _auto_validate_loop():
    """Loop principal de auto-validación."""
    global _running, _last_run, _last_result

    _add_log("Loop de auto-validación iniciado", "info")

    while True:
        config = get_config()
        av_config = config.get("auto_validate", {})
        if not av_config.get("enabled", False):
            _running = False
            await asyncio.sleep(5)
            continue

        _running = True
        interval = av_config.get("interval_seconds", DEFAULT_INTERVAL)

        # Auto-validacion disponible en todos los planes desde v1.5.0
        try:
            count = await asyncio.to_thread(_validate_pending_sync)
            _last_run = datetime.now().strftime("%H:%M:%S")
            if count > 0:
                _last_result = f"{count} factura(s) validada(s)"
                _add_log(f"Ciclo completado: {count} validada(s)", "success")
            else:
                _last_result = "Sin pendientes"
        except Exception as e:
            _last_result = f"Error: {str(e)[:100]}"
            _add_log(f"Error en ciclo: {e}", "error")

        await asyncio.sleep(interval)


# ── Sync validation (runs in thread) ─────────────────────────────────────────

def _is_today(fecfac) -> bool:
    """Verifica si la fecha de la factura es hoy."""
    today = date.today()
    if hasattr(fecfac, "date"):
        return fecfac.date() == today
    if hasattr(fecfac, "year"):
        return fecfac == today
    # String format: "2026-03-23" o "20260323"
    s = str(fecfac or "").replace("-", "").strip()[:8]
    if len(s) == 8:
        try:
            return s == today.strftime("%Y%m%d")
        except Exception:
            pass
    return False


def _validate_pending_sync() -> int:
    """Busca facturas de HOY sin CAE y las valida (sync).
    Solo procesa puntos de venta de usuarios con auto_validate_enabled=True.
    Respeta el filtro de formas de pago configurado.
    """
    db = SessionLocal()
    validated = 0

    try:
        # Leer filtro de formas de pago
        config = get_config()
        av_config = config.get("auto_validate", {})
        allowed_fopfac = set(str(c) for c in av_config.get("fopfac_codes", []))
        # Lista vacía = todas permitidas
        filter_by_fopfac = len(allowed_fopfac) > 0
        grace = int(av_config.get("grace_seconds", DEFAULT_GRACE) or 0)
        now = time.monotonic()
        seen_now: set[tuple] = set()

        # Solo PVs de usuarios activos con auto-validación habilitada
        pvs = (
            db.query(UserPuntoVenta)
            .join(User)
            .filter(User.is_active == True, User.auto_validate_enabled == True)
            .all()
        )
        if not pvs:
            return 0

        for pv_config in pvs:
            tipfac = pv_config.serie_factusol
            # Acotar la consulta a HOY en el propio SQL: el auto-validador solo
            # mira facturas del dia, y traer la serie entera se vuelve cada vez
            # mas caro con el correr del año (bloqueaba bajar el intervalo).
            invoices = factusol_service.get_invoices(tipfac, date_filter="today")

            for inv in invoices:
                codfac = inv.get("CODFAC")
                fecfac = inv.get("FECFAC")

                # Solo facturas de HOY
                if not _is_today(fecfac):
                    continue

                # Filtro por forma de pago
                if filter_by_fopfac:
                    fopfac = str(inv.get("FOPFAC", ""))
                    if fopfac not in allowed_fopfac:
                        continue

                # Ya tiene CAE en Factusol?
                bnofac = str(inv.get("BNOFAC", "") or "").strip()
                if bnofac and len(bnofac) > 3:
                    continue

                # Ya validada en nuestro log?
                existing = db.query(CAELog).filter(
                    CAELog.tipfac == tipfac,
                    CAELog.codfac == codfac,
                ).first()
                if existing:
                    continue

                # ── Espera de gracia ──
                # La factura ya paso todos los filtros: es candidata. Anotamos
                # cuando la vimos por primera vez y no la validamos hasta que
                # lleve `grace` segundos, para no mandarla a AFIP mientras el
                # operador todavia le agrega lineas.
                key = (tipfac, codfac)
                seen_now.add(key)
                first = _first_seen.setdefault(key, now)
                if grace > 0 and (now - first) < grace:
                    continue

                # ── Validar ──
                try:
                    result = _validate_single_sync(tipfac, codfac, pv_config, db)
                    if result:
                        validated += 1
                        _first_seen.pop(key, None)
                        seen_now.discard(key)
                        _add_log(
                            f"CAE {tipfac}-{codfac}: {result.get('cae', '?')}",
                            "success",
                        )
                except Exception as e:
                    _add_log(f"Error {tipfac}-{codfac}: {str(e)[:80]}", "error")

                # Pausa entre facturas para no saturar AFIP
                time.sleep(2)

        # Olvidar las facturas que ya no estan pendientes (validadas a mano,
        # borradas, o cambio de dia): si vuelven a aparecer, la gracia arranca
        # de cero.
        for stale in set(_first_seen) - seen_now:
            _first_seen.pop(stale, None)

    finally:
        db.close()

    return validated


def _validate_single_sync(
    tipfac: int, codfac: int, pv_config: UserPuntoVenta, db
) -> dict | None:
    """Valida una factura individual (sync)."""

    detail = factusol_service.get_invoice_detail(tipfac, codfac)
    if not detail:
        return None

    # Filtrar lineas-leyenda (cantidad=0 Y precio=0): texto descriptivo de
    # Factusol que no debe bloquear la validacion en ARCA.
    raw_lines = detail.get("lines") or []
    detail["lines"] = arca_service.filter_real_lines(raw_lines)
    n_legends = len(raw_lines) - len(detail["lines"])
    if n_legends > 0:
        _add_log(f"📝 {tipfac}-{codfac}: omitidas {n_legends} linea(s) leyenda (cant=0 precio=0)")

    # Auto-ajustar fecha si esta fuera del rango AFIP (evita error 10016)
    fecha_orig = detail.get("header", {}).get("FECFAC")
    fecha_final, was_adjusted, ajuste_msg, _info = arca_service.auto_adjust_invoice_date(fecha_orig, concepto=1)
    if was_adjusted:
        try:
            factusol_service.update_invoice_date(tipfac, codfac, fecha_final)
            detail["header"]["FECFAC"] = fecha_final
            _add_log(f"🗓 {tipfac}-{codfac}: {ajuste_msg}")
        except Exception as e:
            _add_log(f"⚠️  {tipfac}-{codfac}: no pude actualizar fecha en F_FAC ({e}), continuo con fecha ajustada")
            detail["header"]["FECFAC"] = fecha_final

    # Auto-enriquecimiento de padron desactivado (v1.5.1) — genera errores
    # al no ser datos oficiales. El CFECLI debe configurarse en Factusol.
    cliente = detail.get("cliente") or {}
    cfecli = cliente.get("CFECLI", 0) or 0

    config = get_config()
    cond_emisor = config.get("empresa", {}).get("condicion_iva", "Responsable Inscripto")
    mono_como_a = bool(config.get("empresa", {}).get("facturar_mono_como_a", True))

    # NIF limpio para determinar tipo de comprobante
    nifcli_clean = str(detail.get("cliente", {}).get("NIFCLI", "") or "").replace("-", "").strip()

    if pv_config.tipo_comprobante and pv_config.tipo_comprobante != 0:
        tipo_comprobante = pv_config.tipo_comprobante
    else:
        tipo_comprobante = arca_service.determine_tipo_comprobante(cfecli, cond_emisor, nifcli_clean, mono_como_a)

    _add_log(f"Validando {tipfac}-{codfac} (tipo {tipo_comprobante}, PV {pv_config.punto_venta})...")

    result = arca_service.validate_invoice(
        invoice_header=detail["header"],
        invoice_lines=detail["lines"],
        cliente=detail["cliente"],
        punto_venta=pv_config.punto_venta,
        tipo_comprobante=tipo_comprobante,
    )

    # Fecha enviada a ARCA (= FECFAC en memoria tras el auto-ajuste). El export
    # RG 1361 la prefiere sobre la FECFAC de Factusol.
    _fch_arca = arca_service._parse_fecha(detail["header"].get("FECFAC"))
    _fecha_cbte_str = _fch_arca.isoformat() if _fch_arca else None

    # Guardar log en DB
    cae_log = CAELog(
        user_id=pv_config.user_id,
        tipfac=tipfac,
        codfac=codfac,
        punto_venta=pv_config.punto_venta,
        tipo_comprobante=tipo_comprobante,
        voucher_number=result.get("voucher_number", 0),
        cae=result.get("CAE", ""),
        cae_vto=result.get("CAEFchVto", ""),
        fecha_cbte=_fecha_cbte_str,
        imp_total=detail["header"].get("TOTFAC"),
        cliente_nombre=detail["header"].get("CNOFAC"),
        cliente_doc=detail.get("cliente", {}).get("NIFCLI") if detail.get("cliente") else None,
    )
    db.add(cae_log)
    db.commit()

    # Generar QR
    _cuit = str(config.get("empresa", {}).get("cuit", "")).replace("-", "").strip()
    _voucher_data = arca_service.build_voucher_data(
        detail["header"], detail["lines"], detail["cliente"],
        pv_config.punto_venta, tipo_comprobante,
    )
    _fecha_raw = detail["header"].get("FECFAC", "")
    if hasattr(_fecha_raw, "strftime"):
        _fecha_str = _fecha_raw.strftime("%Y-%m-%d")
    elif isinstance(_fecha_raw, str) and len(_fecha_raw) >= 8:
        _fecha_str = _fecha_raw[:10]
    else:
        _fecha_str = datetime.now().strftime("%Y-%m-%d")

    qr_path = arca_service.generate_afip_qr(
        cuit_emisor=_cuit,
        punto_venta=pv_config.punto_venta,
        voucher_number=result.get("voucher_number", 0),
        fecha_cbte=_fecha_str,
        tipo_comprobante=tipo_comprobante,
        tipo_doc_receptor=_voucher_data["tipo_doc"],
        nro_doc_receptor=_voucher_data["nro_doc"],
        imp_total=_voucher_data["imp_total"],
        cae=result.get("CAE", ""),
        cae_vto=result.get("CAEFchVto", ""),
        tipfac=tipfac,
        codfac=codfac,
    )

    # Grabar en Factusol
    _letra_map = {1: "A", 6: "B", 11: "C", 2: "NDA", 3: "NCA", 7: "NDB", 8: "NCB"}
    _letra = _letra_map.get(tipo_comprobante, "X")
    _pedfac = f"{_letra}-{str(pv_config.punto_venta).zfill(4)}-{str(result.get('voucher_number', 0)).zfill(8)}"

    # Código de barras AFIP
    _cuit_bc = str(config.get("empresa", {}).get("cuit", "")).replace("-", "").strip().zfill(11)
    _vto_bc = str(result.get("CAEFchVto", "")).replace("-", "")[:8]
    _barcode = f"{_cuit_bc}{str(tipo_comprobante).zfill(3)}{str(pv_config.punto_venta).zfill(5)}{str(result.get('CAE', '')).zfill(14)}{_vto_bc}"

    try:
        factusol_service.write_cae_to_factura(
            tipfac=tipfac, codfac=codfac,
            cae=result.get("CAE", ""),
            voucher_number=_pedfac,
            cae_vto=result.get("CAEFchVto", ""),
            qr_img_path=qr_path,
            barcode=_barcode,
        )
    except Exception:
        pass

    return {
        "cae": result.get("CAE"),
        "voucher_number": result.get("voucher_number"),
    }


# ── Task management ──────────────────────────────────────────────────────────

def start_background_task():
    """Inicia el task en background."""
    global _task
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return  # No hay loop corriendo, se iniciará en el lifespan
    if _task is None or _task.done():
        _task = loop.create_task(_auto_validate_loop())
        logger.info("🤖 Background task de auto-validación creado")


def stop_background_task():
    """Para el task."""
    global _task, _running
    _running = False
    if _task and not _task.done():
        _task.cancel()
        _task = None
