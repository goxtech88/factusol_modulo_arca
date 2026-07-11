"""
Servicio de integración con ARCA (AFIP) via pyafipws de Mariano Reingart.

Flujo de autenticación AFIP:
  1. WSAA: Con cert+key genera un Ticket de Acceso (TA) firmado digitalmente
  2. WSFEv1: Usa el TA para consultar/enviar comprobantes electronicos
  3. WS Constancia de Inscripción (Padrón A5): Consulta datos fiscales de contribuyentes por CUIT

Documentación:
  https://github.com/reingart/pyafipws
"""
import os
import re
import json
import base64
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import httpx
from html.parser import HTMLParser

from app.config import get_config

# Directorio para cachear los tickets de autenticación (expiran cada 12h)
CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Directorio donde se guardan los QR generados (servido como estático)
QR_DIR = Path(__file__).resolve().parent.parent / "static" / "qr"
QR_DIR.mkdir(exist_ok=True)

# URLs de los WS de AFIP
WSAA_URL_HOMO = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms"
WSAA_URL_PROD = "https://wsaa.afip.gov.ar/ws/services/LoginCms"
WSFE_URL_HOMO = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx"
WSFE_URL_PROD = "https://servicios1.afip.gov.ar/wsfev1/service.asmx"

# URLs de Constancia de Inscripción (Padrón Alcance 5, ws_sr_constancia_inscripcion)
# Servicio oficial de ARCA disponible para cualquier contribuyente con certificado digital.
CONSTANCIA_A5_URL_HOMO = "https://awshomo.afip.gov.ar/sr-padron/webservices/personaServiceA5?wsdl"
CONSTANCIA_A5_URL_PROD = "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA5?wsdl"

# URL de CuitOnline (fallback público para consulta de datos fiscales)
CUIT_ONLINE_SEARCH_URL = "https://www.cuitonline.com/search.php?q={cuit}"
CUIT_ONLINE_DETAIL_URL = "https://www.cuitonline.com/detalle/{cuit}/{slug}.html"

logger = logging.getLogger(__name__)




def _get_urls() -> tuple[str, str]:
    """Retorna (wsaa_url, wsfe_url) según el entorno configurado."""
    config = get_config()
    env = config.get("arca", {}).get("environment", "development")
    if env == "production":
        return WSAA_URL_PROD, WSFE_URL_PROD
    return WSAA_URL_HOMO, WSFE_URL_HOMO


def _get_ta_cache_path(cuit: str, env: str) -> Path:
    key = hashlib.md5(f"{cuit}_{env}".encode()).hexdigest()
    return CACHE_DIR / f"ta_{key}.json"


def _load_cached_ta(cuit: str, env: str) -> Optional[dict]:
    """Carga el Ticket de Acceso cacheado si todavía es válido."""
    path = _get_ta_cache_path(cuit, env)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        expiry = datetime.fromisoformat(data["expiry"])
        # Margen de 10 minutos antes del vencimiento
        if datetime.now() < expiry - timedelta(minutes=10):
            return data
    except Exception:
        pass
    return None


def _save_ta_cache(cuit: str, env: str, token: str, sign: str, expiry_str: str):
    path = _get_ta_cache_path(cuit, env)
    # Parsear fecha de expiración del TA (formato: 2024-01-01T12:00:00)
    try:
        expiry = datetime.fromisoformat(expiry_str.replace("-03:00", ""))
    except Exception:
        expiry = datetime.now() + timedelta(hours=11)
    data = {"token": token, "sign": sign, "expiry": expiry.isoformat()}
    path.write_text(json.dumps(data))


def _get_wsaa_ta(wsaa_url: str, cert_path: str, key_path: str, cuit: str, env: str) -> tuple[str, str]:
    """
    Obtiene Token + Sign del WSAA.
    Cachea el TA para evitar solicitudes innecesarias (válido ~12h).
    """
    cached = _load_cached_ta(cuit, env)
    if cached:
        return cached["token"], cached["sign"]

    from pyafipws.wsaa import WSAA
    wsaa = WSAA()

    # Conectar al WSAA.
    # IMPORTANTE: Conectar() agrega '?wsdl' automáticamente — NO pasar '?WSDL' manualmente.
    wsaa.Conectar(wsdl=wsaa_url)

    # Generar Ticket de Requerimiento de Acceso (TRA)
    tra = wsaa.CreateTRA(service="wsfe")

    # Firmar el TRA con el certificado y clave privada
    cms = wsaa.SignTRA(tra, cert_path, key_path)

    # Enviar al WSAA y obtener el Ticket de Acceso (TA)
    ta_xml = wsaa.LoginCMS(cms)

    if wsaa.Excepcion:
        raise ValueError(f"Error WSAA: {wsaa.Excepcion}")

    token = wsaa.Token
    sign = wsaa.Sign

    # Cachear para siguientes llamadas
    expiry_str = wsaa.ExpirationTime if hasattr(wsaa, 'ExpirationTime') else ""
    _save_ta_cache(cuit, env, token, sign, expiry_str)

    return token, sign


def _create_wsfe_instance() -> "WSFEv1":
    """
    Crea e inicializa una instancia de WSFEv1 autenticada.
    """
    from pyafipws.wsfev1 import WSFEv1

    config = get_config()
    empresa = config.get("empresa", {})
    arca = config.get("arca", {})
    env = arca.get("environment", "development")

    cuit = str(empresa.get("cuit", "")).replace("-", "").strip()
    if not cuit:
        raise ValueError("No se ha configurado el CUIT de la empresa.")

    cert_path = arca.get("cert_path", "")
    key_path = arca.get("key_path", "")

    if not cert_path or not os.path.exists(cert_path):
        raise ValueError(f"Certificado no encontrado: {cert_path}")
    if not key_path or not os.path.exists(key_path):
        raise ValueError(f"Clave privada no encontrada: {key_path}")

    wsaa_url, wsfe_url = _get_urls()

    # Obtener Token de Acceso
    token, sign = _get_wsaa_ta(wsaa_url, cert_path, key_path, cuit, env)

    # Inicializar WSFEv1
    wsfe = WSFEv1()
    # Conectar() también agrega '?wsdl' automáticamente — NO usar '?WSDL'
    wsfe.Conectar(wsdl=wsfe_url)
    wsfe.Cuit = cuit
    wsfe.Token = token
    wsfe.Sign = sign

    return wsfe


def get_server_status() -> dict:
    """Verifica el estado del servidor WSFEv1 de ARCA."""
    try:
        wsfe = _create_wsfe_instance()
        # Dummy() retorna True (bool); los estados quedan en atributos del objeto
        wsfe.Dummy()
        if wsfe.Excepcion:
            raise ValueError(f"Error WSFE Dummy: {wsfe.Excepcion}")
        return {
            "status": "ok",
            "detail": {
                "AppServer": wsfe.AppServerStatus,
                "DbServer": wsfe.DbServerStatus,
                "AuthServer": wsfe.AuthServerStatus,
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_last_voucher_number(punto_venta: int, tipo_comprobante: int) -> int:
    """Obtiene el último número de comprobante emitido en WSFEv1."""
    wsfe = _create_wsfe_instance()
    last = wsfe.CompUltimoAutorizado(tipo_comprobante, punto_venta)
    if wsfe.Excepcion:
        raise ValueError(f"Error WSFE: {wsfe.Excepcion}")
    return int(last or 0)


# ── Validación de fecha de comprobante (AFIP) ──────────────────────────────
# AFIP solo permite emitir CAE con fecha de comprobante dentro de un rango
# relativo a la fecha actual del servidor:
#   - Concepto 1 (Productos):           ±5 días
#   - Concepto 2/3 (Servicios / Mixto): ±10 días
# Fuente: RG 4291 / Manual WSFEv1. Si se manda fuera de rango → error 10016/10017.

AFIP_FECHA_MARGEN_PRODUCTOS = 5   # días hacia atrás / adelante
AFIP_FECHA_MARGEN_SERVICIOS = 10


def _parse_fecha(fecha_cbte):
    """Normaliza date/datetime/str a date. Retorna None si no se puede parsear."""
    from datetime import datetime as _dt, date as _date
    if fecha_cbte is None:
        return None
    if isinstance(fecha_cbte, _dt):
        return fecha_cbte.date()
    if isinstance(fecha_cbte, _date):
        return fecha_cbte
    if isinstance(fecha_cbte, str):
        s = fecha_cbte.strip()
        try:
            if len(s) >= 10 and s[4] == "-" and s[7] == "-":
                return _date(int(s[:4]), int(s[5:7]), int(s[8:10]))
            if len(s) == 8 and s.isdigit():
                return _date(int(s[:4]), int(s[4:6]), int(s[6:8]))
            return _dt.fromisoformat(s).date()
        except Exception:
            return None
    return None


# Alias para timedelta en mensajes (evita import en cada llamada)
from datetime import timedelta as _td
from datetime import date as _date


def auto_adjust_invoice_date(fecha_cbte, concepto: int = 1) -> tuple:
    """
    Si la fecha del comprobante está fuera del rango AFIP, devuelve la fecha
    AJUSTADA al límite válido más cercano (no bloquea, ARREGLA).

    Retorna (fecha_final: date, was_adjusted: bool, mensaje_info: str, info: dict)

    Lógica:
      - Si fecha está dentro de ±margen → devuelve la original sin cambios.
      - Si está MÁS de `margen` días en el pasado → ajusta a `hoy - margen`.
        (preserva el "intento" del usuario de fechar atrás, pero al límite válido)
      - Si está MÁS de `margen` días en el futuro → ajusta a `hoy + margen`.
      - Si no se puede parsear → ajusta a `hoy` y avisa.
    """
    margen = AFIP_FECHA_MARGEN_SERVICIOS if concepto in (2, 3) else AFIP_FECHA_MARGEN_PRODUCTOS
    hoy = _date.today()
    limite_atras = hoy - _td(days=margen)
    limite_adelante = hoy + _td(days=margen)

    f = _parse_fecha(fecha_cbte)
    if f is None:
        info = {"original": str(fecha_cbte), "ajustada": hoy.isoformat(), "motivo": "parse_error"}
        return hoy, True, f"Fecha invalida ({fecha_cbte!r}), usando hoy {hoy.strftime('%d/%m/%Y')}.", info

    delta = (f - hoy).days
    info = {
        "original": f.isoformat(),
        "hoy": hoy.isoformat(),
        "dias_diferencia": delta,
        "margen_dias": margen,
        "concepto": concepto,
    }

    if abs(delta) <= margen:
        info["ajustada"] = f.isoformat()
        return f, False, "", info

    # Fuera de rango → ajustar al límite más cercano
    if delta < 0:
        ajustada = limite_atras
        msg = (
            f"Fecha de Factusol ({f.strftime('%d/%m/%Y')}) era de {abs(delta)} dias atras, "
            f"fuera del rango AFIP. Se ajusto a {ajustada.strftime('%d/%m/%Y')} (limite valido)."
        )
    else:
        ajustada = limite_adelante
        msg = (
            f"Fecha de Factusol ({f.strftime('%d/%m/%Y')}) era de {delta} dias en el futuro, "
            f"fuera del rango AFIP. Se ajusto a {ajustada.strftime('%d/%m/%Y')} (limite valido)."
        )
    info["ajustada"] = ajustada.isoformat()
    return ajustada, True, msg, info


def determine_tipo_comprobante(
    cfecli: int,
    cond_iva_emisor: str = "Responsable Inscripto",
    nifcli: str = "",
    mono_como_a: bool = True,
    explain: bool = False,
):
    """
    Determina el tipo de comprobante AFIP según CFECLI y NIF del cliente.

    Tipos de comprobante AFIP:
      1  = Factura A   (RI emite a RI o a Mono con RG 5022/21)
      6  = Factura B   (RI emite a CF, Exento, o Mono si se desactiva RG 5022)
      11 = Factura C   (Monotributista emite a cualquiera)

    CFECLI en Factusol (F_CLI):
      0 = No configurado
      1 = Consumidor Final (DNI)       → Factura B
      2 = Responsable Inscripto (CUIT) → Factura A
      3 = Monotributista (CUIT)        → Factura A si mono_como_a, sino B
      4 = Exento (CUIT)                → Factura B

    Lógica de NIF:
      - Vacío              → Consumidor final sin identificar → Factura B
      - < 11 dígitos (DNI) → Consumidor final con DNI        → Factura B
      - 11 dígitos (CUIT)  → usar CFECLI para decidir A o B

    Nota RG 5022/21 (AFIP): los RI deben emitir Factura A a Monotributistas
    con la leyenda "Receptor del comprobante - Responsable Monotributo".
    La leyenda debe imprimirse en el comprobante desde Factusol.
    """
    CFECLI_LABELS = {
        0: "No configurado",
        1: "Consumidor Final",
        2: "Responsable Inscripto",
        3: "Monotributo",
        4: "Exento",
        5: "No Responsable / No Alcanzado",
    }

    def _ret(tipo, razon):
        if explain:
            return tipo, {
                "tipo": tipo,
                "razon": razon,
                "cfecli": cfecli,
                "cfecli_label": CFECLI_LABELS.get(cfecli, f"Desconocido({cfecli})"),
                "nifcli": nifcli,
                "mono_como_a": mono_como_a,
            }
        return tipo

    # ── Emisor Monotributista: siempre Factura C ──────────────────────
    if cond_iva_emisor == "Monotributista":
        return _ret(11, "Emisor Monotributista → Factura C")

    cfecli = int(cfecli or 0)
    nifcli_clean = str(nifcli or "").replace("-", "").strip()

    # ── Sin NIF / NIF no numerico → CF sin identificar ────────────────
    if not nifcli_clean or not nifcli_clean.isdigit():
        return _ret(6, f"Sin NIF / NIF no numerico ('{nifcli}') → CF sin identificar → Factura B")

    # ── DNI (< 11 digitos) → CF con DNI ───────────────────────────────
    if len(nifcli_clean) < 11:
        return _ret(6, f"NIF de {len(nifcli_clean)} digitos → DNI → Factura B")

    # ── CUIT (11 digitos): regla EXPLICITA por CFECLI ─────────────────
    # Cada CFECLI se trata por separado para evitar que el flag mono_como_a
    # afecte a clientes que NO son Monotributo (especialmente Exentos).

    if cfecli == 2:
        return _ret(1, "CFECLI=2 (Responsable Inscripto) con CUIT → Factura A (siempre)")

    if cfecli == 3:
        if mono_como_a:
            return _ret(1, "CFECLI=3 (Monotributo) + mono_como_a=True (RG 5022/21) → Factura A")
        return _ret(6, "CFECLI=3 (Monotributo) + mono_como_a=False (legacy) → Factura B")

    if cfecli == 4:
        # Exento: el flag mono_como_a NO aplica. Siempre B.
        return _ret(6, "CFECLI=4 (Exento) → Factura B (SIEMPRE, mono_como_a no aplica a exentos)")

    if cfecli == 5:
        return _ret(6, "CFECLI=5 (No Responsable / No Alcanzado) → Factura B (siempre)")

    # CFECLI=0 (no configurado) o 1 (CF con CUIT) o desconocido → B
    return _ret(6, f"CFECLI={cfecli} ({CFECLI_LABELS.get(cfecli, '?')}) con CUIT → Factura B (default seguro)")



def is_legend_line(line: dict) -> bool:
    """
    Detecta lineas que el usuario carga en Factusol solo como leyendas / texto
    descriptivo (cantidad=0 Y precio=0 Y total=0). Estas lineas no son items
    reales y deben omitirse al validar la factura en ARCA y al exportar el
    DETALLE de RG 1361.
    """
    try:
        cant = float(line.get("CANLFA") or 0)
        prec = float(line.get("PRELFA") or 0)
        tot = float(line.get("TOTLFA") or 0)
    except (TypeError, ValueError):
        return False
    return cant == 0 and prec == 0 and tot == 0


def filter_real_lines(lines: list[dict]) -> list[dict]:
    """Devuelve las lineas reales descartando las que son solo leyendas."""
    return [ln for ln in (lines or []) if not is_legend_line(ln)]


def build_voucher_data(
    invoice_header: dict,
    invoice_lines: list[dict],
    cliente: dict,
    punto_venta: int,
    tipo_comprobante: int,
) -> dict:
    """
    Construye el payload de comprobante para WSFEv1.CompAgregarDetalle / CompFECAESolicitar.

    Alícuotas IVA AFIP:
      Id 3 → 0%     Id 4 → 10.5%   Id 5 → 21%
      Id 6 → 27%    Id 8 → 5%      Id 9 → 2.5%

    Mapeo de tipos de IVA Factusol (slot 1-4 en header BAS{i}FAC / valor IVALFA
    en lineas): se resuelve desde config["iva_mapping"]. Si el slot esta marcado
    como "exento" en el mapeo, su base va a imp_op_ex (no a imp_neto) y no se
    informa alicuota.
    """
    # Fecha del comprobante
    fecha = invoice_header.get("FECFAC")
    if isinstance(fecha, datetime):
        fecha_str = fecha.strftime("%Y%m%d")
    elif isinstance(fecha, str):
        fecha_str = fecha.replace("-", "")[:8]
    else:
        fecha_str = datetime.now().strftime("%Y%m%d")

    # ── Resolver mapeo Tipo Factusol (1..4) → alicuota AFIP ──
    # Cada entrada es float (%) o None (exento). pct_to_id mapea % → Id AFIP.
    pct_to_id = {0: 3, 2.5: 9, 5: 8, 10.5: 4, 21: 5, 27: 6}
    iva_map_cfg = get_config().get("iva_mapping", {}) or {}
    tipo_to_pct: dict[int, float | None] = {}
    for i in (1, 2, 3, 4):
        raw = str(iva_map_cfg.get(f"tipo_{i}", "")).strip().lower()
        if raw == "exento":
            tipo_to_pct[i] = None
        else:
            try:
                tipo_to_pct[i] = float(raw) if raw else 0.0
            except ValueError:
                tipo_to_pct[i] = 0.0

    # ── Calcular IVA desde el HEADER (BAS{i}FAC + IIVA{i}FAC por slot 1..4) ──
    # El slot N del header corresponde al tipo N del mapeo.
    iva_array = []
    total_neto = 0.0
    total_iva = 0.0
    total_exento = 0.0

    for i in range(1, 5):
        base = float(invoice_header.get(f"BAS{i}FAC", 0) or 0)
        iva_imp = float(invoice_header.get(f"IIVA{i}FAC", 0) or 0)
        if base <= 0 and iva_imp <= 0:
            continue

        pct = tipo_to_pct.get(i, 0.0)

        if pct is None:
            # Slot marcado como Exento en el mapeo → va a imp_op_ex
            total_exento += base
            continue

        total_neto += base
        total_iva += iva_imp
        if base > 0:
            afip_id = pct_to_id.get(pct, 5)  # default 21%
            iva_array.append({
                "Id": afip_id,
                "BaseImp": round(base, 2),
                "Importe": round(iva_imp, 2),
            })

    # Si no pudimos extraer nada del header, fallback a las líneas usando IVALFA
    # (codigo de tipo 1..4 al que pertenece la linea) para agrupar correctamente.
    if total_neto == 0 and total_iva == 0 and total_exento == 0:
        real_lines = filter_real_lines(invoice_lines)
        # Agrupar BASLFA + IVA por tipo (IVALFA)
        por_tipo: dict[int, dict[str, float]] = {}
        for line in real_lines:
            try:
                tipo = int(line.get("IVALFA") or 0)
            except (TypeError, ValueError):
                tipo = 0
            if tipo < 1 or tipo > 4:
                tipo = 1  # fallback al primer tipo si esta fuera de rango

            piv = float(line.get("PIVLFA", 0) or 0)
            base_line = float(line.get("BASLFA", 0) or 0)
            total_line = float(line.get("TOTLFA", 0) or 0)
            if base_line == 0 and total_line > 0:
                if piv > 0:
                    base_line = round(total_line / (1 + piv / 100), 2)
                else:
                    base_line = total_line
            iva_line = round(base_line * piv / 100, 2) if piv > 0 else 0.0

            d = por_tipo.setdefault(tipo, {"base": 0.0, "iva": 0.0})
            d["base"] += base_line
            d["iva"] += iva_line

        for tipo, sums in por_tipo.items():
            base = round(sums["base"], 2)
            if base <= 0:
                continue
            pct = tipo_to_pct.get(tipo, 0.0)
            if pct is None:
                total_exento += base
                continue
            iva_amount = round(sums["iva"], 2)
            total_neto += base
            total_iva += iva_amount
            afip_id = pct_to_id.get(pct, 5)
            iva_array.append({"Id": afip_id, "BaseImp": base, "Importe": iva_amount})

    # ImpTotal: usar el TOTFAC del header como fuente de verdad
    imp_total = float(invoice_header.get("TOTFAC", 0) or 0)
    if imp_total == 0:
        imp_total = round(total_neto + total_iva + total_exento, 2)

    # Documento del cliente
    # Distinguir: vacío → sin identificar (99), DNI < 11 dígitos (96), CUIT 11 dígitos (80)
    doc_nro_raw = str(cliente.get("NIFCLI", "") or "").replace("-", "").strip() if cliente else ""

    if not doc_nro_raw or not doc_nro_raw.isdigit():
        # NIF vacío o no numérico → consumidor final sin identificar
        doc_tipo = 99
        doc_nro = "0"
    elif len(doc_nro_raw) < 11:
        # DNI u otro doc de menos de 11 dígitos → doc tipo DNI
        doc_tipo = 96
        doc_nro = doc_nro_raw
    else:
        # CUIT (exactamente 11 dígitos)
        doc_tipo = 80
        doc_nro = doc_nro_raw

    # Concepto de facturación (1=Productos, 2=Servicios, 3=Ambos)
    config = get_config()
    concepto = int(config.get("empresa", {}).get("concepto_facturacion", 1))

    result = {
        "tipo_cbte": tipo_comprobante,
        "punto_vta": punto_venta,
        "fecha_cbte": fecha_str,
        "concepto": concepto,
        "tipo_doc": doc_tipo,
        "nro_doc": int(doc_nro),
        "imp_total": round(imp_total, 2),
        "imp_tot_conc": 0,
        "imp_neto": round(total_neto, 2),
        "imp_op_ex": round(total_exento, 2),
        "imp_iva": round(total_iva, 2),
        "imp_trib": 0,
        "moneda_id": "PES",
        "moneda_ctz": 1,
        "iva": iva_array,
    }

    # Si concepto = 2 o 3 (Servicios), ARCA exige fechas de servicio y vto pago
    if concepto in (2, 3):
        result["fch_serv_desde"] = fecha_str
        result["fch_serv_hasta"] = fecha_str
        result["fch_vto_pago"] = fecha_str

    return result




def validate_invoice(
    invoice_header: dict,
    invoice_lines: list[dict],
    cliente: dict,
    punto_venta: int,
    tipo_comprobante: int,
) -> dict:
    """
    Solicita CAE para una factura en AFIP via WSFEv1.

    Retorna: {"CAE": str, "CAEFchVto": str, "voucher_number": int}
    """
    import logging
    log = logging.getLogger("arca_service")

    wsfe = _create_wsfe_instance()
    data = build_voucher_data(invoice_header, invoice_lines, cliente, punto_venta, tipo_comprobante)

    # Obtener próximo número de comprobante (reusar misma instancia)
    last = wsfe.CompUltimoAutorizado(tipo_comprobante, punto_venta)
    if wsfe.Excepcion:
        raise ValueError(f"Error al consultar último comprobante: {wsfe.Excepcion}")
    next_cbte = int(last or 0) + 1

    log.info(f"[ARCA] PV={punto_venta} TipoCbte={tipo_comprobante} UltCbte={last} NextCbte={next_cbte}")
    log.info(f"[ARCA] ImpTotal={data['imp_total']} Neto={data['imp_neto']} IVA={data['imp_iva']} "
             f"DocTipo={data['tipo_doc']} DocNro={data['nro_doc']} Concepto={data['concepto']}")
    log.info(f"[ARCA] IVA array: {data.get('iva', [])}")

    # Armar comprobante en WSFEv1
    wsfe.CrearFactura(
        concepto=data["concepto"],
        tipo_doc=data["tipo_doc"],
        nro_doc=data["nro_doc"],
        tipo_cbte=data["tipo_cbte"],
        punto_vta=data["punto_vta"],
        cbt_desde=next_cbte,
        cbt_hasta=next_cbte,
        imp_total=data["imp_total"],
        imp_tot_conc=data["imp_tot_conc"],
        imp_neto=data["imp_neto"],
        imp_iva=data["imp_iva"],
        imp_trib=data["imp_trib"],
        imp_op_ex=data["imp_op_ex"],
        fecha_cbte=data["fecha_cbte"],
        moneda_id=data["moneda_id"],
        moneda_ctz=data["moneda_ctz"],
        fecha_serv_desde=data.get("fch_serv_desde"),
        fecha_serv_hasta=data.get("fch_serv_hasta"),
        fecha_venc_pago=data.get("fch_vto_pago"),
    )


    # Agregar alícuotas de IVA
    for iva_item in data.get("iva", []):
        wsfe.AgregarIva(
            iva_id=iva_item["Id"],
            base_imp=iva_item["BaseImp"],
            importe=iva_item["Importe"],
        )

    # Solicitar CAE
    wsfe.CAESolicitar()

    log.info(f"[ARCA] Resultado={wsfe.Resultado} CAE={wsfe.CAE} Vto={wsfe.Vencimiento}")
    if wsfe.Obs:
        log.warning(f"[ARCA] Observaciones: {wsfe.Obs}")
    if wsfe.ErrMsg:
        log.error(f"[ARCA] ErrMsg: {wsfe.ErrMsg}")

    if wsfe.Excepcion:
        raise ValueError(f"Error WSFE al solicitar CAE: {wsfe.Excepcion}")
    if wsfe.ErrMsg:
        raise ValueError(f"Error AFIP: {wsfe.ErrMsg}")

    # Si fue rechazado sin ErrMsg pero con observaciones
    if wsfe.Resultado == "R" and not wsfe.CAE:
        raise ValueError(f"Rechazado por AFIP: {wsfe.Obs or 'Sin detalle'}")

    return {
        "CAE": wsfe.CAE,
        "CAEFchVto": wsfe.Vencimiento,
        "voucher_number": next_cbte,
        "resultado": wsfe.Resultado,
        "obs": wsfe.Obs,
    }



def tipo_factura_to_nota_credito(tipo_factura: int) -> int:
    """Convierte tipo de factura AFIP al tipo de nota de crédito correspondiente.
    Factura A (1) → NC A (3), Factura B (6) → NC B (8), Factura C (11) → NC C (13)
    """
    mapping = {1: 3, 6: 8, 11: 13}
    nc_tipo = mapping.get(tipo_factura)
    if nc_tipo is None:
        raise ValueError(f"No se puede hacer NC para tipo de comprobante {tipo_factura}")
    return nc_tipo


def validate_credit_note(
    invoice_header: dict,
    invoice_lines: list[dict],
    cliente: dict,
    punto_venta: int,
    tipo_comprobante_original: int,
    voucher_number_original: int,
    punto_venta_original: int,
    importe_override: float | None = None,
) -> dict:
    """
    Emite una Nota de Crédito en AFIP asociada a una factura previamente validada.

    La NC lleva los mismos importes que la factura original y referencia
    al comprobante asociado (tipo, PV, número).

    Retorna: {"CAE": str, "CAEFchVto": str, "voucher_number": int, "tipo_nc": int}
    """
    import logging
    log = logging.getLogger("arca_service")

    tipo_nc = tipo_factura_to_nota_credito(tipo_comprobante_original)

    wsfe = _create_wsfe_instance()
    data = build_voucher_data(invoice_header, invoice_lines, cliente, punto_venta, tipo_nc)

    # NC parcial: reescalar importes proporcionalmente al total original
    if importe_override is not None and importe_override > 0:
        original_total = float(data.get("imp_total") or 0)
        if original_total <= 0:
            raise ValueError("No se puede emitir NC parcial: la factura original tiene total 0")
        nuevo_total = round(float(importe_override), 2)
        if nuevo_total > original_total + 0.01:
            raise ValueError(f"El importe de la NC ({nuevo_total}) supera el total de la factura original ({original_total})")
        factor = nuevo_total / original_total
        data["imp_total"] = nuevo_total
        data["imp_neto"] = round(float(data.get("imp_neto") or 0) * factor, 2)
        data["imp_iva"] = round(float(data.get("imp_iva") or 0) * factor, 2)
        data["imp_tot_conc"] = round(float(data.get("imp_tot_conc") or 0) * factor, 2)
        data["imp_op_ex"] = round(float(data.get("imp_op_ex") or 0) * factor, 2)
        data["imp_trib"] = round(float(data.get("imp_trib") or 0) * factor, 2)
        # Reescalar alicuotas manteniendo mismo Id (tasa de IVA)
        nuevas_iva = []
        for iva_item in data.get("iva", []):
            nuevas_iva.append({
                "Id": iva_item["Id"],
                "BaseImp": round(float(iva_item["BaseImp"]) * factor, 2),
                "Importe": round(float(iva_item["Importe"]) * factor, 2),
            })
        data["iva"] = nuevas_iva
        log.info(f"[ARCA-NC] Parcial: factor={factor:.4f} nuevo_total={nuevo_total}")

    # Obtener próximo número de NC
    last = wsfe.CompUltimoAutorizado(tipo_nc, punto_venta)
    if wsfe.Excepcion:
        raise ValueError(f"Error al consultar último comprobante NC: {wsfe.Excepcion}")
    next_cbte = int(last or 0) + 1

    log.info(f"[ARCA-NC] PV={punto_venta} TipoNC={tipo_nc} UltCbte={last} NextCbte={next_cbte}")
    log.info(f"[ARCA-NC] Asociada a: Tipo={tipo_comprobante_original} PV={punto_venta_original} Nro={voucher_number_original}")
    log.info(f"[ARCA-NC] ImpTotal={data['imp_total']} Neto={data['imp_neto']} IVA={data['imp_iva']}")

    # Fecha de hoy para la NC
    fecha_hoy = datetime.now().strftime("%Y%m%d")

    wsfe.CrearFactura(
        concepto=data["concepto"],
        tipo_doc=data["tipo_doc"],
        nro_doc=data["nro_doc"],
        tipo_cbte=tipo_nc,
        punto_vta=punto_venta,
        cbt_desde=next_cbte,
        cbt_hasta=next_cbte,
        imp_total=data["imp_total"],
        imp_tot_conc=data["imp_tot_conc"],
        imp_neto=data["imp_neto"],
        imp_iva=data["imp_iva"],
        imp_trib=data["imp_trib"],
        imp_op_ex=data["imp_op_ex"],
        fecha_cbte=fecha_hoy,
        moneda_id=data["moneda_id"],
        moneda_ctz=data["moneda_ctz"],
        fecha_serv_desde=data.get("fch_serv_desde"),
        fecha_serv_hasta=data.get("fch_serv_hasta"),
        fecha_venc_pago=data.get("fch_vto_pago"),
    )

    # Agregar comprobante asociado (la factura original)
    wsfe.AgregarCmpAsoc(
        tipo=tipo_comprobante_original,
        pto_vta=punto_venta_original,
        nro=voucher_number_original,
    )

    # Agregar alícuotas de IVA
    for iva_item in data.get("iva", []):
        wsfe.AgregarIva(
            iva_id=iva_item["Id"],
            base_imp=iva_item["BaseImp"],
            importe=iva_item["Importe"],
        )

    # Solicitar CAE
    wsfe.CAESolicitar()

    log.info(f"[ARCA-NC] Resultado={wsfe.Resultado} CAE={wsfe.CAE} Vto={wsfe.Vencimiento}")
    if wsfe.Obs:
        log.warning(f"[ARCA-NC] Observaciones: {wsfe.Obs}")
    if wsfe.ErrMsg:
        log.error(f"[ARCA-NC] ErrMsg: {wsfe.ErrMsg}")

    if wsfe.Excepcion:
        raise ValueError(f"Error WSFE al solicitar CAE para NC: {wsfe.Excepcion}")
    if wsfe.ErrMsg:
        raise ValueError(f"Error AFIP: {wsfe.ErrMsg}")

    if wsfe.Resultado == "R" and not wsfe.CAE:
        raise ValueError(f"NC Rechazada por AFIP: {wsfe.Obs or 'Sin detalle'}")

    return {
        "CAE": wsfe.CAE,
        "CAEFchVto": wsfe.Vencimiento,
        "voucher_number": next_cbte,
        "tipo_nc": tipo_nc,
        "resultado": wsfe.Resultado,
        "obs": wsfe.Obs,
    }


def get_voucher_info(punto_venta: int, tipo_comprobante: int, voucher_number: int) -> dict:
    """Obtiene información de un comprobante ya emitido."""
    wsfe = _create_wsfe_instance()
    wsfe.CompConsultar(tipo_comprobante, punto_venta, voucher_number)
    if wsfe.Excepcion:
        raise ValueError(f"Error WSFE: {wsfe.Excepcion}")
    return {
        "CAE": wsfe.CAE,
        "CAEFchVto": wsfe.Vencimiento,
        "resultado": wsfe.Resultado,
        "imp_total": wsfe.ImpTotal,
        "fecha_cbte": wsfe.FechaCbte,
    }


def generate_afip_qr(
    cuit_emisor: str,
    punto_venta: int,
    voucher_number: int,
    fecha_cbte: str,
    tipo_comprobante: int,
    tipo_doc_receptor: int,
    nro_doc_receptor: int,
    imp_total: float,
    cae: str,
    cae_vto: str,
    tipfac: int,
    codfac: int,
    filename: str = None,
) -> str:
    """
    Genera la imagen QR estándar AFIP para comprobante electrónico.

    Guarda el QR en carpeta ARCA_QR junto a la base de datos de Factusol.
    Retorna la ruta absoluta del archivo QR (para IMGFAC en Factusol).
    """
    try:
        import qrcode

        # Payload estándar AFIP
        payload = {
            "ver": 1,
            "fecha": fecha_cbte[:10] if len(fecha_cbte) >= 8 else fecha_cbte,
            "cuit": int(cuit_emisor),
            "ptoVta": punto_venta,
            "tipoCmp": tipo_comprobante,
            "nroCmp": voucher_number,
            "importe": round(float(imp_total), 2),
            "moneda": "PES",
            "ctz": 1,
            "tipoDocRec": tipo_doc_receptor,
            "nroDocRec": nro_doc_receptor,
            "tipoCodAut": "E",  # E = CAE
            "codAut": int(cae),
        }

        payload_b64 = base64.b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()
        qr_url = f"https://www.afip.gob.ar/fe/qr/?p={payload_b64}"

        # Generar imagen
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Guardar en carpeta ARCA_QR junto a la DB de Factusol
        config = get_config()
        db_path = config.get("factusol", {}).get("db_path", "")
        if db_path:
            qr_dir = Path(db_path).parent / "ARCA_QR"
        else:
            qr_dir = QR_DIR  # fallback a static/qr/

        qr_dir.mkdir(exist_ok=True)

        filename = filename or f"{tipfac}-{codfac}.png"
        out_path = qr_dir / filename
        img.save(str(out_path))

        # También guardar copia en static/qr/ para el módulo web
        static_qr = QR_DIR / filename
        img.save(str(static_qr))

        return str(out_path.resolve())   # Ruta ABSOLUTA para Factusol

    except ImportError:
        return ""
    except Exception as e:
        # No romper el flujo de validación si el QR falla
        print(f"⚠️ Error generando QR AFIP: {e}")
        return ""




def _fetch_html(url: str) -> str:
    """Descarga HTML usando httpx (ya incluido en PyInstaller)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "es-AR,es;q=0.9",
    }
    try:
        with httpx.Client(follow_redirects=True, timeout=15) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.text
    except Exception as e:
        raise ValueError(f"Error al consultar {url}: {e}")


def _extract_links(html: str, pattern: str) -> list[str]:
    """Extrae hrefs de links que contienen el patrón dado."""
    return re.findall(r'href=["\']([^"\']*' + re.escape(pattern) + r'[^"\']*)["\']', html)


def _extract_text_from_html(html: str) -> str:
    """Extrae texto plano del HTML eliminando tags."""
    # Eliminar scripts y styles
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Reemplazar <br>, <p>, <div>, <li>, <tr> con saltos de línea
    text = re.sub(r'<(?:br|/p|/div|/li|/tr|/h[1-6])[^>]*>', '\n', text, flags=re.IGNORECASE)
    # Eliminar todos los tags restantes
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decodificar entidades HTML comunes
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&nbsp;', ' ').replace('&aacute;', 'á').replace('&eacute;', 'é')
    text = text.replace('&iacute;', 'í').replace('&oacute;', 'ó').replace('&uacute;', 'ú')
    text = text.replace('&ntilde;', 'ñ').replace('&Aacute;', 'Á').replace('&Eacute;', 'É')
    text = text.replace('&Iacute;', 'Í').replace('&Oacute;', 'Ó').replace('&Uacute;', 'Ú')
    text = text.replace('&Ntilde;', 'Ñ')
    # Limpiar espacios múltiples
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()


def _extract_h1(html: str) -> str:
    """Extrae el contenido del primer tag <h1>."""
    match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
    if match:
        return re.sub(r'<[^>]+>', '', match.group(1)).strip()
    return ""


def validar_cuit(cuit: str) -> bool:
    """Valida que el CUIT tenga 11 dígitos exactos y dígito verificador correcto (mod 11)."""
    c = re.sub(r"\D", "", str(cuit or ""))
    if len(c) != 11:
        return False
    multiplicadores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    total = sum(int(c[i]) * multiplicadores[i] for i in range(10))
    esperado = 11 - (total % 11)
    if esperado == 11:
        esperado = 0
    elif esperado == 10:
        # CUIT con dígito verificador 10 es inválido — no se asignan
        return False
    return int(c[10]) == esperado


def consultar_cuit(cuit_consulta: str) -> dict:
    """
    Consulta datos fiscales de un CUIT con cadena de fuentes (de más a menos confiable):
      1. ARCA oficial — Constancia de Inscripción (Padrón A5), usa el mismo
         certificado digital ya configurado para facturar.
      2. afip.tangofactura.com — API JSON pública.
      3. cuitonline.com — scraping HTML, último recurso.

    Antes de consultar valida formato (11 dígitos) y dígito verificador,
    así un CUIT mal cargado en Factusol falla rápido con mensaje claro.
    """
    cuit_limpio = re.sub(r"[^0-9]", "", str(cuit_consulta).strip())
    if len(cuit_limpio) != 11:
        raise ValueError(
            f"CUIT inválido: '{cuit_consulta}' tiene {len(cuit_limpio)} dígitos y un CUIT tiene 11. "
            f"Si es un DNI, complete el CUIT/CUIL real del cliente en Factusol."
        )
    if not validar_cuit(cuit_limpio):
        raise ValueError(
            f"CUIT inválido: {cuit_limpio[:2]}-{cuit_limpio[2:10]}-{cuit_limpio[10]} "
            f"no pasa la verificación del dígito verificador. "
            f"Revise el número cargado en Factusol (probablemente haya un dígito mal tipeado)."
        )

    errores = []

    # Fuente 1: webservice oficial de ARCA (constancia de inscripción)
    try:
        return consultar_constancia(cuit_limpio)
    except Exception as e:
        logger.warning(f"Constancia ARCA falló para {cuit_limpio}: {e}")
        errores.append(f"ARCA oficial: {e}")

    # Fuente 2: tangofactura (API JSON)
    try:
        data = _consultar_tangofactura(cuit_limpio)
        if data:
            return data
        errores.append("tangofactura.com: sin datos")
    except Exception as e:
        errores.append(f"tangofactura.com: {e}")

    # Fuente 3: cuitonline (scraping)
    try:
        return _consultar_cuitonline_scraping(cuit_limpio)
    except Exception as e:
        errores.append(f"cuitonline.com: {e}")

    detalle = " | ".join(errores)
    hint = ""
    if any(x in detalle.lower() for x in ["no autorizado", "computador", "unauthorized", "cee"]):
        hint = (
            " NOTA: el error de ARCA sugiere que falta autorizar el servicio "
            "'Consulta de Constancia de Inscripción' para su certificado digital. "
            "Ingrese a ARCA con clave fiscal → Administrador de Relaciones de Clave Fiscal → "
            "adherir el servicio al mismo alias de certificado que usa para facturar (se hace una sola vez)."
        )
    raise ValueError(
        f"No se pudieron obtener datos del CUIT {cuit_limpio}. Detalle: {detalle}.{hint}"
    )


def consultar_constancia(cuit_consulta: str) -> dict:
    """
    Consulta la Constancia de Inscripción (Padrón A5, ws_sr_constancia_inscripcion) de ARCA.

    Fuente OFICIAL: usa el mismo certificado digital configurado para wsfe.
    Requiere que el servicio 'Consulta de Constancia de Inscripción' esté autorizado
    para el certificado en el Administrador de Relaciones de ARCA (trámite único).
    A diferencia del Padrón A4 (que pide un permiso especial de AFIP), el A5 está
    disponible para cualquier contribuyente.
    """
    config = get_config()
    empresa = config.get("empresa", {})
    arca = config.get("arca", {})
    env = arca.get("environment", "development")

    cuit_emisor = str(empresa.get("cuit", "")).replace("-", "").strip()
    if not cuit_emisor:
        raise ValueError("No se ha configurado el CUIT de la empresa.")

    cert_path = arca.get("cert_path", "")
    key_path = arca.get("key_path", "")
    if not cert_path or not os.path.exists(cert_path):
        raise ValueError(f"Certificado no encontrado: {cert_path}")
    if not key_path or not os.path.exists(key_path):
        raise ValueError(f"Clave privada no encontrada: {key_path}")

    wsaa_url, _ = _get_urls()
    padron_url = CONSTANCIA_A5_URL_PROD if env == "production" else CONSTANCIA_A5_URL_HOMO

    # El servicio requiere su propio TA (distinto a wsfe) — cacheado ~12h
    cache_key = f"{cuit_emisor}_{env}_constancia_a5"
    cached = _load_cached_ta(cache_key, "")
    if cached:
        token, sign = cached["token"], cached["sign"]
    else:
        from pyafipws.wsaa import WSAA
        wsaa = WSAA()
        wsaa.Conectar(wsdl=wsaa_url)
        tra = wsaa.CreateTRA(service="ws_sr_constancia_inscripcion")
        cms = wsaa.SignTRA(tra, cert_path, key_path)
        wsaa.LoginCMS(cms)
        if wsaa.Excepcion:
            raise ValueError(f"Error WSAA Constancia: {wsaa.Excepcion}")
        token, sign = wsaa.Token, wsaa.Sign
        expiry_str = getattr(wsaa, "ExpirationTime", "") or ""
        _save_ta_cache(cache_key, "", token, sign, expiry_str)

    # pyafipws.ws_sr_padron usa SafeConfigParser, removido en Python 3.12+
    import configparser
    if not hasattr(configparser, "SafeConfigParser"):
        configparser.SafeConfigParser = configparser.ConfigParser

    from pyafipws.ws_sr_padron import WSSrPadronA5
    padron = WSSrPadronA5()
    padron.LanzarExcepciones = True
    padron.Conectar(wsdl=padron_url)
    padron.Cuit = cuit_emisor
    padron.Token = token
    padron.Sign = sign

    cuit_limpio = re.sub(r"[^0-9]", "", str(cuit_consulta))
    padron.Consultar(cuit_limpio)
    if padron.Excepcion:
        raise ValueError(f"ARCA: {padron.Excepcion}")

    razon_social = (padron.denominacion or "").strip()
    if not razon_social:
        raise ValueError(f"ARCA no devolvió datos para el CUIT {cuit_limpio}.")

    tipo_persona = (padron.tipo_persona or "JURIDICA").upper()
    nombre = apellido = ""
    if tipo_persona == "FISICA" and "," in razon_social:
        apellido, nombre = [p.strip() for p in razon_social.split(",", 1)]
        razon_social = f"{apellido} {nombre}".strip()

    CAT_IVA_MAP = {
        1: "Responsable Inscripto",
        4: "Exento",
        5: "Consumidor Final",
        6: "Responsable Monotributo",
    }
    cat_iva = padron.cat_iva if isinstance(padron.cat_iva, int) else None
    condicion_iva = CAT_IVA_MAP.get(cat_iva, "Sin datos")

    # Separar "CALLE 1234" en calle + número
    direccion = (padron.direccion or "").strip()
    calle, numero = direccion, ""
    match = re.match(r"(.+?)\s+(\d{1,5})\s*$", direccion)
    if match:
        calle, numero = match.group(1).strip(), match.group(2)

    domicilio = {
        "calle": calle,
        "numero": numero,
        "piso": "",
        "depto": "",
        "localidad": (padron.localidad or "").strip(),
        "provincia": (padron.provincia or "").strip(),
        "cp": str(padron.cod_postal or "").strip(),
    }

    return {
        "cuit": cuit_limpio,
        "razon_social": razon_social,
        "nombre": nombre,
        "apellido": apellido,
        "tipo_persona": tipo_persona,
        "condicion_iva": condicion_iva,
        "condicion_iva_id": cat_iva,
        "domicilio_fiscal": domicilio,
        "estado_cuit": (padron.estado or "").strip() or "ACTIVO",
        "source": "ARCA (constancia de inscripción oficial)",
        "raw": {
            "denominacion": razon_social,
            "tipoClave": tipo_persona,
            "estadoClave": padron.estado or "",
            "impuestos": list(padron.impuestos or []),
            "monotributo": padron.monotributo,
        },
    }


def _consultar_cuitonline_scraping(cuit_limpio: str) -> dict:
    """
    Consulta datos fiscales de un CUIT usando cuitonline.com (scraping).
    No requiere certificado digital ni autenticación AFIP.
    Usa httpx (ya incluido en PyInstaller) y regex para parsing HTML.
    Último recurso de la cadena de consultar_cuit().
    """
    # Paso 1: Buscar el CUIT para obtener el slug (nombre en URL)
    search_url = CUIT_ONLINE_SEARCH_URL.format(cuit=cuit_limpio)
    search_html = _fetch_html(search_url)

    # Buscar el link al detalle: detalle/{cuit}/{slug}.html (puede ser relativo o absoluto)
    detail_links = _extract_links(search_html, f"detalle/{cuit_limpio}")
    detail_link = None
    for href in detail_links:
        if href.endswith(".html"):
            detail_link = href
            break

    if not detail_link:
        # Intentar extraer datos mínimos de la búsqueda
        search_text = _extract_text_from_html(search_html)
        razon_social = ""
        condicion_iva = ""

        # Buscar nombre cerca del CUIT en el texto
        match = re.search(rf'{cuit_limpio}[^a-zA-Z]*([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s,\.]+)', search_text)
        if match:
            razon_social = match.group(1).strip()

        condicion_iva = _extract_condicion_iva(search_text)

        if razon_social:
            return _build_cuitonline_result(cuit_limpio, razon_social, condicion_iva, {})

        raise ValueError(
            f"No se encontraron datos para el CUIT {cuit_limpio}. "
            f"El CUIT puede ser muy nuevo o no estar indexado. "
            f"Cargue los datos manualmente."
        )

    # Paso 2: Obtener detalle completo
    if detail_link.startswith("http"):
        detail_url = detail_link
    elif detail_link.startswith("/"):
        detail_url = f"https://www.cuitonline.com{detail_link}"
    else:
        detail_url = f"https://www.cuitonline.com/{detail_link}"
    detail_html = _fetch_html(detail_url)
    page_text = _extract_text_from_html(detail_html)

    # Extraer razón social (del <h1> o del contenido)
    razon_social = _extract_h1(detail_html)
    # Limpiar el CUIT del nombre si aparece
    razon_social = re.sub(r"\d{2}-\d{8}-\d", "", razon_social).strip()
    # Quitar prefijos comunes
    razon_social = re.sub(r"^(Constancia de |CUIT\s+)", "", razon_social, flags=re.IGNORECASE).strip()

    # Extraer condición IVA
    condicion_iva = _extract_condicion_iva(page_text)

    # Extraer domicilio fiscal
    domicilio = _extract_domicilio(page_text)

    # Extraer tipo persona
    tipo_persona = "JURIDICA" if any(x in razon_social.upper() for x in ["SRL", "S.R.L", "S.A.", " SA ", "SAS", "S.A.S"]) else "FISICA"

    return _build_cuitonline_result(cuit_limpio, razon_social, condicion_iva, domicilio, tipo_persona)


def _consultar_tangofactura(cuit: str) -> Optional[dict]:
    """Intenta consultar afip.tangofactura.com como fuente alternativa."""
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"https://afip.tangofactura.com/Rest/GetContribuyenteFull?cuit={cuit}")
            if resp.status_code != 200:
                return None
            data = resp.json()
            if data.get("errorGetData"):
                return None
            razon = data.get("Contribuyente", {}).get("nombre", "") or data.get("denominacion", "")
            if not razon:
                return None
            # Mapear condición IVA
            tipo_iva = data.get("Contribuyente", {}).get("tipoPersona", "")
            condicion = "Sin datos"
            if data.get("condicionIVA"):
                cond = data["condicionIVA"].lower()
                if "inscripto" in cond:
                    condicion = "Responsable Inscripto"
                elif "monotributo" in cond:
                    condicion = "Responsable Monotributo"
                elif "exento" in cond:
                    condicion = "Exento"
            domicilio_str = data.get("Contribuyente", {}).get("domicilioFiscal", "")
            domicilio = {"calle": domicilio_str, "numero": "", "piso": "", "depto": "",
                         "localidad": "", "provincia": "", "cp": ""}
            tipo = "JURIDICA" if any(x in razon.upper() for x in ["SRL", "S.R.L", "S.A.", " SA ", "SAS"]) else "FISICA"
            result = _build_cuitonline_result(cuit, razon, condicion, domicilio, tipo)
            result["source"] = "tangofactura.com"
            return result
    except Exception:
        return None


def _extract_condicion_iva(text: str) -> str:
    """Extrae la condición IVA del texto de la página."""
    text_lower = text.lower()
    # Buscar patrones comunes
    if "iva exento" in text_lower or "iva - exento" in text_lower:
        return "Exento"
    if "monotributo" in text_lower and ("iva" not in text_lower or "iva inscripto" not in text_lower):
        return "Responsable Monotributo"
    if "iva inscripto" in text_lower or "responsable inscripto" in text_lower:
        return "Responsable Inscripto"
    if "consumidor final" in text_lower:
        return "Consumidor Final"
    if "monotributo" in text_lower:
        return "Responsable Monotributo"
    return "Sin datos"


def _extract_domicilio(text: str) -> dict:
    """Extrae el domicilio fiscal del texto de la página."""
    domicilio = {"calle": "", "numero": "", "piso": "", "depto": "", "localidad": "", "provincia": "", "cp": ""}

    lines = text.split("\n")
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        # Buscar "Domicilio" seguido de la dirección
        if "domicilio" in line_stripped.lower() and "fiscal" in line_stripped.lower():
            # La dirección suele estar en la misma línea o la siguiente
            for j in range(i, min(i + 3, len(lines))):
                candidate = lines[j].strip()
                # Buscar patrón de dirección: texto con número
                if re.search(r"\d{2,5}", candidate) and len(candidate) > 10 and "domicilio" not in candidate.lower():
                    domicilio["calle"] = candidate
                    break
            continue

        # Buscar localidad/provincia en formato "Ciudad, Provincia"
        if any(prov in line_stripped for prov in [
            "Buenos Aires", "Córdoba", "Santa Fe", "Mendoza", "Tucumán",
            "Entre Ríos", "Salta", "Misiones", "Chaco", "Corrientes",
            "Santiago del Estero", "San Juan", "Jujuy", "Río Negro",
            "Neuquén", "Formosa", "Chubut", "San Luis", "Catamarca",
            "La Rioja", "La Pampa", "Santa Cruz", "Tierra del Fuego",
            "CABA", "Capital Federal"
        ]):
            parts = line_stripped.split(",")
            if len(parts) >= 2:
                domicilio["localidad"] = parts[0].strip()
                domicilio["provincia"] = parts[-1].strip()
            elif not domicilio["provincia"]:
                domicilio["provincia"] = line_stripped.strip()

    # Si la calle tiene formato "Calle 123", separar
    if domicilio["calle"]:
        match = re.match(r"(.+?)\s+(\d{1,5})\s*$", domicilio["calle"])
        if match:
            domicilio["calle"] = match.group(1).strip()
            domicilio["numero"] = match.group(2)

    return domicilio


def _build_cuitonline_result(cuit: str, razon_social: str, condicion_iva: str,
                              domicilio: dict, tipo_persona: str = "JURIDICA") -> dict:
    """Construye el resultado en el mismo formato que consultar_constancia()."""
    CONDICION_TO_ID = {
        "Responsable Inscripto": 1,
        "Responsable No Inscripto": 2,
        "Exento": 3,
        "No Responsable": 4,
        "Consumidor Final": 5,
        "Responsable Monotributo": 6,
        "Sujeto No Categorizado": 7,
    }

    nombre = ""
    apellido = ""
    if tipo_persona == "FISICA":
        parts = razon_social.split(" ", 1)
        if len(parts) == 2:
            apellido = parts[0]
            nombre = parts[1]

    return {
        "cuit": cuit,
        "razon_social": razon_social,
        "nombre": nombre,
        "apellido": apellido,
        "tipo_persona": tipo_persona,
        "condicion_iva": condicion_iva,
        "condicion_iva_id": CONDICION_TO_ID.get(condicion_iva),
        "domicilio_fiscal": domicilio or {
            "calle": "", "numero": "", "piso": "", "depto": "",
            "localidad": "", "provincia": "", "cp": ""
        },
        "estado_cuit": "ACTIVO",
        "source": "cuitonline.com",
        "raw": {
            "denominacion": razon_social,
            "tipoClave": tipo_persona,
            "estadoClave": "ACTIVO",
        }
    }
