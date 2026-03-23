"""
Servicio de integración con ARCA (AFIP) via pyafipws de Mariano Reingart.

Flujo de autenticación AFIP:
  1. WSAA: Con cert+key genera un Ticket de Acceso (TA) firmado digitalmente
  2. WSFEv1: Usa el TA para consultar/enviar comprobantes electronicos
  3. WS Padrón A4: Consulta datos fiscales de contribuyentes por CUIT

Documentación:
  https://github.com/reingart/pyafipws
"""
import os
import json
import base64
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

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

# URLs del Padrón Alcance 4
PADRON_A4_URL_HOMO = "https://awshomo.afip.gov.ar/sr-padron/webservices/personaServiceA4?wsdl"
PADRON_A4_URL_PROD = "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA4?wsdl"




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


def determine_tipo_comprobante(cond_iva_cliente: str, cond_iva_emisor: str = "Responsable Inscripto") -> int:
    """
    Determina el tipo de comprobante AFIP según la condición de IVA del cliente.

    Tipos principales:
      1  = Factura A   (RI emite a RI)
      6  = Factura B   (RI emite a Consumidor Final, Monotributista, Exento)
      11 = Factura C   (Monotributista emite a cualquiera)

    Condiciones IVA en Factusol (IVACLI):
      0 = Responsable Inscripto
      1 = Responsable No Inscripto
      2 = Exento
      3 = No Responsable
      4 = Consumidor Final
      5 = Monotributo
    """
    # Normalizar
    cond = str(cond_iva_cliente).strip()

    if cond_iva_emisor == "Monotributista":
        return 11  # Factura C

    if cond in ("0", "Responsable Inscripto"):
        return 1   # Factura A
    else:
        return 6   # Factura B (consumidor final, monotributo, exento, etc.)


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

    IMPORTANTE: Los campos de IVA de las LÍNEAS (PIVLFA, BASLFA, IVALFA) son
    poco confiables en Factusol. Usamos los campos del HEADER que son los
    totales correctos por alícuota: BAS1-4FAC, IIVA1-4FAC, PIVA1-3FAC.
    """
    # Fecha del comprobante
    fecha = invoice_header.get("FECFAC")
    if isinstance(fecha, datetime):
        fecha_str = fecha.strftime("%Y%m%d")
    elif isinstance(fecha, str):
        fecha_str = fecha.replace("-", "")[:8]
    else:
        fecha_str = datetime.now().strftime("%Y%m%d")

    # ── Calcular IVA desde el HEADER (campos BASxFAC, IIVAxFAC, PIVAxFAC) ──
    # Factusol guarda hasta 4 bases imponibles con sus IVAs en el header:
    #   BAS1FAC/IIVA1FAC/PIVA1FAC  (alícuota 1)
    #   BAS2FAC/IIVA2FAC  ← PIVA2FAC contiene el % de esta alícuota
    #   BAS3FAC/IIVA3FAC  ← PIVA3FAC contiene el % de esta alícuota
    #   BAS4FAC/IIVA4FAC  (rara vez se usa)
    pct_to_id = {0: 3, 2.5: 9, 5: 8, 10.5: 4, 21: 5, 27: 6}

    iva_array = []
    total_neto = 0.0
    total_iva = 0.0

    for i in range(1, 5):
        base = float(invoice_header.get(f"BAS{i}FAC", 0) or 0)
        iva_imp = float(invoice_header.get(f"IIVA{i}FAC", 0) or 0)
        pct = float(invoice_header.get(f"PIVA{i}FAC", 0) or 0) if i <= 3 else 0

        if base <= 0 and iva_imp <= 0:
            continue

        # Si no hay %, intentar calcular desde base e importe
        if pct == 0 and base > 0 and iva_imp > 0:
            pct = round(iva_imp / base * 100, 1)

        total_neto += base
        total_iva += iva_imp

        afip_id = pct_to_id.get(pct, 5)  # default 21%
        if pct > 0 and base > 0:
            iva_array.append({
                "Id": afip_id,
                "BaseImp": round(base, 2),
                "Importe": round(iva_imp, 2),
            })

    # Si no pudimos extraer nada del header, fallback a las líneas
    if total_neto == 0 and total_iva == 0:
        for line in invoice_lines:
            piv = float(line.get("PIVLFA", 0) or 0)
            base = float(line.get("BASLFA", 0) or 0)
            iva_amount = float(line.get("IVALFA", 0) or 0)
            if base == 0 and iva_amount == 0:
                total_line = float(line.get("TOTLFA", 0) or 0)
                if piv > 0:
                    base = round(total_line / (1 + piv / 100), 2)
                    iva_amount = round(total_line - base, 2)
                else:
                    base = total_line
            total_neto += base
            total_iva += iva_amount
            if piv > 0 and base > 0:
                afip_id = pct_to_id.get(piv, 5)
                iva_array.append({"Id": afip_id, "BaseImp": round(base, 2), "Importe": round(iva_amount, 2)})

    # ImpTotal: usar el TOTFAC del header como fuente de verdad
    imp_total = float(invoice_header.get("TOTFAC", 0) or 0)
    if imp_total == 0:
        imp_total = round(total_neto + total_iva, 2)

    # Documento del cliente
    doc_tipo = 80   # CUIT
    doc_nro = str(cliente.get("NIFCLI", "") or "").replace("-", "").strip() if cliente else ""
    if not doc_nro or not doc_nro.isdigit():
        doc_tipo = 99  # Sin identificar (consumidor final)
        doc_nro = "0"

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
        "imp_op_ex": 0,
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
    wsfe = _create_wsfe_instance()
    data = build_voucher_data(invoice_header, invoice_lines, cliente, punto_venta, tipo_comprobante)

    # Obtener próximo número de comprobante
    next_cbte = get_last_voucher_number(punto_venta, tipo_comprobante) + 1

    # Armar comprobante en WSFEv1
    wsfe.CrearFactura(
        concepto=data["concepto"],
        tipo_doc=data["tipo_doc"],
        nro_doc=data["nro_doc"],
        tipo_cbte=data["tipo_cbte"],
        punto_vta=data["punto_vta"],
        cbte_desde=next_cbte,
        cbte_hasta=next_cbte,
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
        fecha_vto_pago=data.get("fch_vto_pago"),
    )

    # Agregar alícuotas de IVA
    for iva_item in data.get("iva", []):
        wsfe.AgregarIva(
            id=iva_item["Id"],
            base_imp=iva_item["BaseImp"],
            importe=iva_item["Importe"],
        )

    # Solicitar CAE
    wsfe.CAESolicitar()

    if wsfe.Excepcion:
        raise ValueError(f"Error WSFE al solicitar CAE: {wsfe.Excepcion}")
    if wsfe.ErrMsg:
        raise ValueError(f"Error AFIP: {wsfe.ErrMsg}")

    return {
        "CAE": wsfe.CAE,
        "CAEFchVto": wsfe.Vencimiento,
        "voucher_number": next_cbte,
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
) -> str:
    """
    Genera la imagen QR estándar AFIP para comprobante electrónico.

    URL del QR:
      https://www.afip.gob.ar/fe/qr/?p=<base64(json)>

    Retorna la ruta relativa dentro de static/qr/   ej: "qr/8-4093.png"
    Si no se puede generar (qrcode no instalado), retorna "".
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

        filename = f"{tipfac}-{codfac}.png"
        out_path = QR_DIR / filename
        img.save(str(out_path))

        return f"qr/{filename}"   # ruta relativa dentro de static/

    except ImportError:
        return ""
    except Exception as e:
        # No romper el flujo de validación si el QR falla
        print(f"⚠️ Error generando QR AFIP: {e}")
        return ""



def consultar_padron(cuit_consulta: str) -> dict:
    """
    Consulta el Padrón Alcance 4 de ARCA para obtener datos fiscales de un CUIT.

    Retorna un dict con:
      - cuit: str
      - razon_social: str
      - nombre: str  (si es persona física)
      - apellido: str
      - tipo_persona: str  ('FISICA' | 'JURIDICA')
      - condicion_iva: str  (ej: 'Responsable Inscripto')
      - condicion_iva_id: int  (código AFIP 1-7)
      - domicilio_fiscal: dict  (calle, numero, piso, depto, localidad, provincia, cp)
      - estado_cuit: str  (ej: 'ACTIVO')
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
    padron_url = PADRON_A4_URL_PROD if env == "production" else PADRON_A4_URL_HOMO

    # El Padrón A4 requiere su propio TA (servicio distinto a wsfe)
    # Cacheamos con clave específica para padron_a4
    cache_key = f"{cuit_emisor}_{env}_padron_a4"
    cached = _load_cached_ta(cache_key, "")
    if cached:
        token, sign = cached["token"], cached["sign"]
    else:
        from pyafipws.wsaa import WSAA
        wsaa = WSAA()
        wsaa.Conectar(wsdl=wsaa_url)
        tra = wsaa.CreateTRA(service="ws_sr_padron_a4")
        cms = wsaa.SignTRA(tra, cert_path, key_path)
        wsaa.LoginCMS(cms)
        if wsaa.Excepcion:
            raise ValueError(f"Error WSAA Padrón: {wsaa.Excepcion}")
        token = wsaa.Token
        sign = wsaa.Sign
        # Guardar en caché
        path = CACHE_DIR / f"ta_{hashlib.md5(cache_key.encode()).hexdigest()}.json"
        expiry = datetime.now() + timedelta(hours=11)
        path.write_text(json.dumps({"token": token, "sign": sign, "expiry": expiry.isoformat()}))

    # Consultar padrón
    from pyafipws.ws_sr_padron_a4 import WSSrPadronA4
    padron = WSSrPadronA4()
    padron.Conectar(wsdl=padron_url)
    padron.Cuit = cuit_emisor
    padron.Token = token
    padron.Sign = sign

    cuit_limpio = str(cuit_consulta).replace("-", "").replace(" ", "").strip()
    padron.Consultar(cuit_limpio)

    if padron.Excepcion:
        raise ValueError(f"Error Padrón ARCA: {padron.Excepcion}")

    # Mapear condición IVA
    CONDICION_IVA_MAP = {
        1: "Responsable Inscripto",
        2: "Responsable No Inscripto",
        3: "Exento",
        4: "No Responsable",
        5: "Consumidor Final",
        6: "Responsable Monotributo",
        7: "Sujeto No Categorizado",
    }

    # Extraer condicion IVA del resultado
    cond_iva_id = None
    cond_iva_str = "Sin datos"
    # pyafipws expone los datos en atributos del objeto
    try:
        # Intentar obtener de los datos de caracterizaciones
        if hasattr(padron, "datos") and padron.datos:
            datos = padron.datos
            # Buscar IVA en caracterizaciones
            for car in datos.get("caracterizaciones", []):
                code = car.get("idCaracterizacion", 0)
                if code in (1, 2, 3, 4, 5, 6, 7):
                    cond_iva_id = code
                    cond_iva_str = CONDICION_IVA_MAP.get(code, "Desconocido")
                    break
    except Exception:
        pass

    # Construir domicilio fiscal
    domicilio = {}
    try:
        dom = getattr(padron, "domicilio", None) or {}
        if isinstance(dom, dict):
            domicilio = {
                "calle": dom.get("direccion", ""),
                "numero": dom.get("numero", ""),
                "piso": dom.get("piso", ""),
                "depto": dom.get("departamento", ""),
                "localidad": dom.get("localidad", ""),
                "provincia": dom.get("descripcionProvincia", ""),
                "cp": dom.get("codPostal", ""),
            }
    except Exception:
        pass

    return {
        "cuit": cuit_limpio,
        "razon_social": getattr(padron, "denominacion", "") or "",
        "nombre": getattr(padron, "nombre", "") or "",
        "apellido": getattr(padron, "apellido", "") or "",
        "tipo_persona": getattr(padron, "tipoClave", "") or "",
        "condicion_iva": cond_iva_str,
        "condicion_iva_id": cond_iva_id,
        "domicilio_fiscal": domicilio,
        "estado_cuit": getattr(padron, "estadoClave", "") or "",
        "raw": {
            "denominacion": getattr(padron, "denominacion", None),
            "tipoClave": getattr(padron, "tipoClave", None),
            "estadoClave": getattr(padron, "estadoClave", None),
        }
    }
