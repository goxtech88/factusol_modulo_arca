"""
Auto-validación de facturas en ARCA.
Background task que cada N segundos busca facturas sin CAE y las valida automáticamente.
"""
import asyncio
import logging
from datetime import datetime

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


def get_status() -> dict:
    """Devuelve el estado actual del auto-validador."""
    config = get_config()
    enabled = config.get("auto_validate", {}).get("enabled", False)
    interval = config.get("auto_validate", {}).get("interval_seconds", 60)
    return {
        "enabled": enabled,
        "running": _running,
        "interval_seconds": interval,
        "last_run": _last_run,
        "last_result": _last_result,
        "log": _log_lines[-20:],  # últimas 20 líneas
    }


def toggle(enabled: bool) -> dict:
    """Enciende o apaga el auto-validador."""
    config = load_config()
    if "auto_validate" not in config:
        config["auto_validate"] = {"enabled": False, "interval_seconds": 60}
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
    """Cambia el intervalo de chequeo."""
    config = load_config()
    if "auto_validate" not in config:
        config["auto_validate"] = {"enabled": False, "interval_seconds": 60}
    config["auto_validate"]["interval_seconds"] = max(30, min(600, seconds))
    save_config(config)
    return get_status()


async def _auto_validate_loop():
    """Loop principal de auto-validación."""
    global _running, _last_run, _last_result

    while True:
        config = get_config()
        av_config = config.get("auto_validate", {})
        if not av_config.get("enabled", False):
            _running = False
            await asyncio.sleep(5)
            continue

        _running = True
        interval = av_config.get("interval_seconds", 60)

        try:
            count = await _validate_pending()
            _last_run = datetime.now().strftime("%H:%M:%S")
            if count > 0:
                _last_result = f"{count} factura(s) validada(s)"
            else:
                _last_result = "Sin pendientes"
        except Exception as e:
            _last_result = f"Error: {str(e)[:100]}"
            _add_log(f"Error en ciclo: {e}", "error")

        await asyncio.sleep(interval)


async def _validate_pending() -> int:
    """Busca facturas sin CAE y las valida. Retorna cantidad validada."""
    db = SessionLocal()
    validated = 0

    try:
        # Buscar todos los PV configurados
        pvs = db.query(UserPuntoVenta).all()
        if not pvs:
            return 0

        for pv_config in pvs:
            tipfac = pv_config.serie_factusol

            # Obtener facturas de esta serie
            invoices = factusol_service.get_invoices(tipfac)

            for inv in invoices:
                codfac = inv.get("CODFAC")
                bnofac = str(inv.get("BNOFAC", "") or "").strip()

                # Ya tiene CAE en Factusol?
                if bnofac and len(bnofac) > 3:
                    continue

                # Ya validada en nuestro log?
                existing = db.query(CAELog).filter(
                    CAELog.tipfac == tipfac,
                    CAELog.codfac == codfac,
                ).first()
                if existing:
                    continue

                # ── Validar ──
                try:
                    result = await _validate_single(
                        tipfac, codfac, pv_config, db
                    )
                    if result:
                        validated += 1
                        _add_log(
                            f"CAE {tipfac}-{codfac}: {result.get('cae', '?')}",
                            "success",
                        )
                except Exception as e:
                    _add_log(f"Error {tipfac}-{codfac}: {str(e)[:80]}", "error")

                # Pequeña pausa entre facturas para no saturar AFIP
                await asyncio.sleep(2)

    finally:
        db.close()

    return validated


async def _validate_single(
    tipfac: int, codfac: int, pv_config: UserPuntoVenta, db
) -> dict | None:
    """Valida una factura individual. Retorna resultado o None."""
    from app.config import get_config as _get_config

    detail = factusol_service.get_invoice_detail(tipfac, codfac)
    if not detail:
        return None

    config = _get_config()
    cond_emisor = config.get("empresa", {}).get("condicion_iva", "Responsable Inscripto")
    cfecli = detail.get("cliente", {}).get("CFECLI", 0) or 0

    # Tipo comprobante: fijo del PV o auto por CFECLI
    if pv_config.tipo_comprobante and pv_config.tipo_comprobante != 0:
        tipo_comprobante = pv_config.tipo_comprobante
    else:
        tipo_comprobante = arca_service.determine_tipo_comprobante(cfecli, cond_emisor)

    _add_log(f"Validando {tipfac}-{codfac} (tipo {tipo_comprobante}, PV {pv_config.punto_venta})...")

    # Validar en ARCA
    result = arca_service.validate_invoice(
        invoice_header=detail["header"],
        invoice_lines=detail["lines"],
        cliente=detail["cliente"],
        punto_venta=pv_config.punto_venta,
        tipo_comprobante=tipo_comprobante,
    )

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
        from datetime import datetime as _dt
        _fecha_str = _dt.now().strftime("%Y-%m-%d")

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

    try:
        factusol_service.write_cae_to_factura(
            tipfac=tipfac, codfac=codfac,
            cae=result.get("CAE", ""),
            voucher_number=_pedfac,
            cae_vto=result.get("CAEFchVto", ""),
            qr_img_path=qr_path,
        )
    except Exception:
        pass

    return {
        "cae": result.get("CAE"),
        "voucher_number": result.get("voucher_number"),
    }


def start_background_task():
    """Inicia el task en background si no existe."""
    global _task
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        return  # No hay loop, se iniciará después
    if _task is None or _task.done():
        _task = loop.create_task(_auto_validate_loop())


def stop_background_task():
    """Para el task."""
    global _task
    if _task and not _task.done():
        _task.cancel()
        _task = None
