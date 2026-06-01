"""
Generación de archivos CABECERA y DETALLE de Facturas Emitidas
según RG (AFIP) 1361/2002 - Anexo II - Régimen Especial de
Almacenamiento Electrónico de Registraciones (Duplicado Electrónico).

Diseños de registro extraídos del Anexo II vigente.

Reglas generales:
  - Codificación: ASCII puro (sin acentos / Ñ → N).
  - Padding: alfanuméricos con BLANCOS a derecha; numéricos con CEROS a izquierda.
  - Importes: signo implícito (positivos). 13 enteros + 2 decimales sin separador
    decimal (los 2 últimos dígitos son los centavos). Total 15 caracteres.
  - Cantidad línea: 7 enteros + 5 decimales sin separador. Total 12 caracteres.
  - Precio unitario: 13 enteros + 3 decimales sin separador. Total 16 caracteres.
  - Tipo de cambio: 4 enteros + 6 decimales sin separador. Total 10 caracteres.
  - Fin de registro: secuencia 0D0A (CRLF) entre líneas. Sin BOM.
  - Orden de archivos: por fecha + tipo cbte + PV + nro cbte (ascendente).

Tablas usadas (AFIP - RG 1415 / RG 1361 - Anexo IV):
  E.1 Tipo de comprobante:
      01=FA, 02=NDA, 03=NCA, 06=FB, 07=NDB, 08=NCB, 11=FC, 12=NDC, 13=NCC.
  E.4 Tipo de responsable: 01=RI, 04=Exento, 05=CF, 06=Monotributo.
  E.5 Moneda: PES = pesos argentinos.
  E.6 Alícuota IVA: 03=0%, 04=10.5%, 05=21%, 06=27%, 08=5%, 09=2.5%.
  E.7 Documento: 80=CUIT, 86=CUIL, 96=DNI, 99=sin identificar (CF).
  E.9 Unidad medida: 7=unidades (default).
"""
from __future__ import annotations

import io
import zipfile
from datetime import datetime, date
from typing import Iterable, Optional

from sqlalchemy.orm import Session

from app.models.cae_log import CAELog
from app.services import factusol_service
from app.config import get_config


# ─── Tablas RG 1361 ────────────────────────────────────────────────────────

# Mapeo CFECLI Factusol → tipo de responsable RG 1361 (Tabla E.4)
#   CFECLI: 0=no config, 1=CF, 2=RI, 3=Mono, 4=Exento
CFECLI_TO_RESP = {
    0: "05",  # default → CF
    1: "05",  # Consumidor Final
    2: "01",  # Responsable Inscripto
    3: "06",  # Monotributo
    4: "04",  # Exento
}

# Alícuota IVA → código RG 1361 (Tabla E.6)
ALICUOTA_TO_CODIGO = {
    0.0:  "03",
    2.5:  "09",
    5.0:  "08",
    10.5: "04",
    21.0: "05",
    27.0: "06",
}


# ─── Helpers de formateo ───────────────────────────────────────────────────

def _ascii(text: object, length: int) -> str:
    """Convierte a ASCII (sin tildes ni Ñ), recorta y rellena con blancos a derecha."""
    if text is None:
        s = ""
    else:
        s = str(text)
    # Reemplazos comunes ES/AR
    repl = (
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
        ("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U"),
        ("ñ", "n"), ("Ñ", "N"), ("ü", "u"), ("Ü", "U"),
    )
    for a, b in repl:
        s = s.replace(a, b)
    s = s.encode("ascii", errors="ignore").decode("ascii")
    return s.ljust(length)[:length]


def _num(value: object, length: int) -> str:
    """Entero con ceros a izquierda."""
    try:
        n = int(value or 0)
    except (TypeError, ValueError):
        n = 0
    if n < 0:
        n = 0  # importes positivos siempre
    return str(n).zfill(length)[-length:]


def _amount(value: object, total_len: int = 15, decimals: int = 2) -> str:
    """
    Importe con signo implícito positivo: enteros + decimales sin separador.
    Ej: 1234.56 con total_len=15, decimals=2 → '000000000123456'.
    """
    try:
        v = float(value or 0.0)
    except (TypeError, ValueError):
        v = 0.0
    if v < 0:
        v = 0.0
    cents = int(round(v * (10 ** decimals)))
    return str(cents).zfill(total_len)[-total_len:]


def _date_yyyymmdd(d: object) -> str:
    """Convierte date / datetime / 'YYYY-MM-DD' a 'YYYYMMDD'. Vacío → '00000000'."""
    if not d:
        return "0" * 8
    if isinstance(d, datetime):
        return d.strftime("%Y%m%d")
    if isinstance(d, date):
        return d.strftime("%Y%m%d")
    s = str(d).strip()
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:4] + s[5:7] + s[8:10]
    if len(s) == 8 and s.isdigit():
        return s
    return "0" * 8


def _normalize_doc(doc_raw: str, length: int = 11) -> tuple[str, str]:
    """
    Devuelve (codigo_doc, numero_doc) según RG 1361 - Tabla E.7.
    11 dígitos → CUIT (80). 7-8 dígitos → DNI (96). Otro/vacío → 99.
    El nro_doc se zfilla al ancho indicado (CABECERA=11, VENTAS=20).
    """
    s = "".join(c for c in (doc_raw or "") if c.isdigit())
    if len(s) == 11:
        return "80", s.zfill(length)
    if 7 <= len(s) <= 8:
        return "96", s.zfill(length)
    return "99", "0" * length


def _resp_from_cfecli(cfecli: int) -> str:
    return CFECLI_TO_RESP.get(int(cfecli or 0), "05")


def _cod_alicuota(porc: float) -> str:
    """Mapea un porcentaje de IVA al código de tabla E.6. Ajusta a la más cercana."""
    if porc is None:
        return "03"
    try:
        p = float(porc)
    except (TypeError, ValueError):
        return "03"
    # Aproximación tolerante (algunos sistemas guardan 21.00, 10.50, etc.)
    for k, code in ALICUOTA_TO_CODIGO.items():
        if abs(p - k) < 0.01:
            return code
    return "03"


# ─── Construcción de registros ─────────────────────────────────────────────

def _build_cabecera_tipo1(
    *,
    fecha: date,
    tipo_cbte: int,
    pv: int,
    nro_cbte: int,
    cuit_cliente_raw: str,
    razon_social: str,
    imp_total: float,
    imp_no_grav: float,
    imp_neto: float,
    imp_iva: float,
    imp_exento: float,
    cfecli: int,
    cant_alicuotas: int,
    cae: str,
    cae_vto: str,
) -> str:
    """
    Registro tipo 1 del archivo CABECERA - 290 caracteres.
    Layout reverse-engineered de los archivos de referencia AFIP (RG 1361).
    """
    cod_doc, nro_doc = _normalize_doc(cuit_cliente_raw, length=11)
    is_exento = imp_neto <= 0 and imp_exento > 0
    cae_digits = "".join(c for c in (cae or "") if c.isdigit()).zfill(14)[-14:]

    parts = [
        "1",                                      # pos 1     - Tipo registro
        _date_yyyymmdd(fecha),                    # pos 2-9   - Fecha cbte (8)
        _num(tipo_cbte, 2),                       # pos 10-11 - Tipo cbte (2)
        " ",                                      # pos 12    - Ctrl fiscal (1)
        _num(pv, 4),                              # pos 13-16 - PV (4)
        _num(nro_cbte, 8),                        # pos 17-24 - Nro cbte desde (8)
        _num(nro_cbte, 8),                        # pos 25-32 - Nro cbte hasta (8)
        "001",                                    # pos 33-35 - Cantidad hojas (3)
        cod_doc,                                  # pos 36-37 - Cod doc receptor (2)
        nro_doc,                                  # pos 38-48 - Nro doc receptor (11)
        _ascii(razon_social, 30),                 # pos 49-78 - Razón social (30)
        _amount(imp_total),                       # pos 79-93  - Imp total operación
        _amount(imp_no_grav),                     # pos 94-108 - Conceptos no gravados
        _amount(imp_neto),                        # pos 109-123 - Neto gravado
        _amount(imp_iva),                         # pos 124-138 - IVA liquidado
        _amount(0),                               # pos 139-153 - IVA RNI
        _amount(imp_exento),                      # pos 154-168 - Operaciones exentas
        _amount(0),                               # pos 169-183 - Percep imp. nacionales
        _amount(0),                               # pos 184-198 - Percep IIBB
        _amount(0),                               # pos 199-213 - Percep municipal
        _amount(0),                               # pos 214-228 - Impuestos internos
        _amount(0),                               # pos 229-243 - Transporte (0 para 1 hoja)
        _resp_from_cfecli(cfecli),                # pos 244-245 - Tipo responsable (2)
        "PES",                                    # pos 246-248 - Moneda (3)
        "0001000000",                             # pos 249-258 - Tipo cambio (10)
        "1",                                      # pos 259    - Cant alícuotas (1)
        ("E" if is_exento else " "),              # pos 260    - Cod operación (1)
        cae_digits,                               # pos 261-274 - CAE (14)
        _date_yyyymmdd(cae_vto),                  # pos 275-282 - Fecha vto CAE (8)
        " " * 8,                                  # pos 283-290 - Fecha anulación (8 blancos)
    ]
    line = "".join(parts)
    assert len(line) == 290, f"CABECERA tipo 1 debe ser 290 chars, fue {len(line)}"
    return line


def _build_cabecera_tipo2(
    *,
    periodo_yyyymm: str,
    cant_tipo1: int,
    cuit_emisor: str,
    totales: dict,
) -> str:
    """
    Registro tipo 2 del archivo CABECERA - 290 caracteres.
    Resumen: período + cantidad tipo 1 + CUIT informante + sumatorias.
    """
    parts = [
        "2",                                      # pos 1     - Tipo registro
        periodo_yyyymm,                           # pos 2-7   - Período AAAAMM (6)
        " " * 13,                                 # pos 8-20  - blanks (13)
        _num(cant_tipo1, 8),                      # pos 21-28 - Cantidad tipo 1 (8)
        " " * 17,                                 # pos 29-45 - blanks (17)
        cuit_emisor.zfill(11),                    # pos 46-56 - CUIT informante (11)
        " " * 22,                                 # pos 57-78 - blanks (22)
        _amount(totales.get("imp_total", 0)),     # pos 79-93   - Total operación
        _amount(totales.get("imp_no_grav", 0)),   # pos 94-108  - Total no gravado
        _amount(totales.get("imp_neto", 0)),      # pos 109-123 - Total neto
        _amount(totales.get("imp_iva", 0)),       # pos 124-138 - Total IVA
        _amount(0),                               # pos 139-153 - Total IVA RNI
        _amount(totales.get("imp_exento", 0)),    # pos 154-168 - Total exento
        _amount(0),                               # pos 169-183 - Total percep nac
        _amount(0),                               # pos 184-198 - Total IIBB
        _amount(0),                               # pos 199-213 - Total municipal
        _amount(0),                               # pos 214-228 - Total imp internos
    ]
    line = "".join(parts)
    # Padding con blancos hasta 290
    line = line.ljust(290)[:290]
    assert len(line) == 290, f"CABECERA tipo 2 debe ser 290 chars, fue {len(line)}"
    return line


# ─── Archivo VENTAS (Libro IVA Ventas electronico) ──────────────────────────

def _build_ventas_tipo1(
    *,
    fecha: date,
    tipo_cbte: int,
    pv: int,
    nro_cbte: int,
    cuit_cliente_raw: str,
    razon_social: str,
    imp_total: float,
    imp_no_grav: float,
    imp_neto: float,
    imp_iva: float,
    imp_exento: float,
) -> str:
    """
    Registro VENTAS por comprobante - 266 caracteres.
    Layout reverse-engineered de los archivos AFIP de referencia.
    Notas:
      - NO lleva tipo registro al inicio (empieza directo en fecha).
      - tipo cbte se codifica en 3 chars (zfilled): 6 → '006'.
      - ctrl fiscal va con '0' (numérico), no espacio.
      - nros de cbte son 20 chars (no 8).
      - nro doc receptor es 20 chars (zfilled).
      - 8 amounts: total, no_grav, neto, exento, percepNac, IIBB, munic, internos.
      - CAE no se incluye en VENTAS (14 ceros).
    """
    cod_doc, nro_doc = _normalize_doc(cuit_cliente_raw, length=20)
    is_exento = imp_neto <= 0 and imp_exento > 0

    parts = [
        _date_yyyymmdd(fecha),                # pos 1-8   - Fecha cbte (8)
        _num(tipo_cbte, 3),                   # pos 9-11  - Tipo cbte (3, zfilled)
        "0",                                  # pos 12    - Ctrl fiscal (1, "0")
        _num(pv, 4),                          # pos 13-16 - PV (4)
        _num(nro_cbte, 20),                   # pos 17-36 - Nro cbte desde (20)
        _num(nro_cbte, 20),                   # pos 37-56 - Nro cbte hasta (20)
        cod_doc,                              # pos 57-58 - Cod doc receptor (2)
        nro_doc,                              # pos 59-78 - Nro doc receptor (20)
        _ascii(razon_social, 30),             # pos 79-108 - Razón social (30)
        _amount(imp_total),                   # pos 109-123 - Imp total
        _amount(imp_no_grav),                 # pos 124-138 - No gravado
        _amount(imp_neto),                    # pos 139-153 - Neto gravado
        _amount(imp_exento),                  # pos 154-168 - Exento
        _amount(0),                           # pos 169-183 - Percep nac
        _amount(0),                           # pos 184-198 - Percep IIBB
        _amount(0),                           # pos 199-213 - Percep municipal
        _amount(0),                           # pos 214-228 - Imp internos
        "PES",                                # pos 229-231 - Moneda (3)
        "0001000000",                         # pos 232-241 - Tipo cambio (10)
        "1",                                  # pos 242     - Cant alícuotas (1)
        ("E" if is_exento else "0"),          # pos 243     - Cod operación (1)
        "0" * 14,                             # pos 244-257 - CAE (14, ceros)
        "0",                                  # pos 258     - Filler (1, "0")
        _date_yyyymmdd(fecha),                # pos 259-266 - Fecha (repite cbte)
    ]
    line = "".join(parts)
    assert len(line) == 266, f"VENTAS debe ser 266 chars, fue {len(line)}"
    return line


def _build_detalle_tipo1(
    *,
    fecha: date,
    tipo_cbte: int,
    pv: int,
    nro_cbte: int,
    cantidad: float,
    unidad_medida: int,
    precio_unitario: float,
    bonificacion: float,
    subtotal: float,
    alicuota_porc: float,
    descripcion: str,
    nro_item: int = 1,
) -> str:
    """
    Registro DETALLE por ítem - 189 caracteres (fixed).
    Layout reverse-engineered del archivo AFIP de referencia:
      pos 1-2    Tipo cbte (2)
      pos 3      Ctrl fiscal (1, espacio)
      pos 4-11   Fecha cbte (8)
      pos 12-15  PV (4)
      pos 16-23  Nro cbte desde (8)
      pos 24-31  Nro cbte hasta (8)
      pos 32-43  Cantidad (12, 5 decimales)
      pos 44-45  Unidad medida (2)
      pos 46-61  Precio unitario (16, 3 decimales)
      pos 62-76  Bonificación (15, 2 decimales)
      pos 77-91  Reservado/ajuste (15, ceros)
      pos 92-106 Subtotal (15, 1 decimal — observado en refs AFIP)
      pos 107-110 Cod alícuota (4, % zfilled — '0021' para 21%, '0000' exento)
      pos 111    Indicador exento (1, '0')
      pos 112    Indicador anulación (1, '0')
      pos 113    Indicador G/E (1, 'G' gravado, 'E' exento)
      pos 114    Espacio (1)
      pos 115-118 Nro item / línea (4, zfilled)
      pos 119    Espacio (1)
      pos 120-189 Descripción (70 chars)
    """
    # Ajustar a la alícuota AFIP válida más cercana (Tabla E.6). Esto protege
    # el ancho del campo (4 chars) contra valores anómalos de PIVLFA en Factusol
    # —p.ej. una línea con PIVLFA de 7 dígitos rompía el registro a 192 chars—
    # y a la vez garantiza que se informe siempre una alícuota legal. Para los
    # valores normales (0, 10.5, 21, 27…) el resultado es idéntico al anterior.
    try:
        _porc = abs(float(alicuota_porc or 0))
    except (TypeError, ValueError):
        _porc = 0.0
    alic = min(ALICUOTA_TO_CODIGO.keys(), key=lambda v: abs(v - _porc))
    is_exento = alic == 0.0
    cod_alic = f"{int(round(alic)):04d}"

    parts = [
        _num(tipo_cbte, 2),                                # pos 1-2
        " ",                                               # pos 3
        _date_yyyymmdd(fecha),                             # pos 4-11
        _num(pv, 4),                                       # pos 12-15
        _num(nro_cbte, 8),                                 # pos 16-23
        _num(nro_cbte, 8),                                 # pos 24-31
        _amount(cantidad, total_len=12, decimals=5),       # pos 32-43
        _num(unidad_medida or 7, 2),                       # pos 44-45
        _amount(precio_unitario, total_len=16, decimals=3),# pos 46-61
        _amount(bonificacion),                             # pos 62-76 (15, 2dec)
        "0" * 15,                                          # pos 77-91
        _amount(subtotal, total_len=15, decimals=1),       # pos 92-106 (1 decimal!)
        cod_alic,                                          # pos 107-110
        "0",                                               # pos 111
        "0",                                               # pos 112
        ("E" if is_exento else "G"),                       # pos 113
        " ",                                               # pos 114
        _num(nro_item, 4),                                 # pos 115-118
        " ",                                               # pos 119
        _ascii(descripcion, 70),                           # pos 120-189
    ]
    line = "".join(parts)
    assert len(line) == 189, f"DETALLE debe ser 189 chars, fue {len(line)}"
    return line


# ─── API pública ──────────────────────────────────────────────────────────

def _iter_logs_for_period(
    db: Session,
    *,
    year: int,
    month: int,
    pv: Optional[int] = None,
    user_id: Optional[int] = None,
) -> list[CAELog]:
    """Devuelve los logs CAE del período, ordenados según RG 1361."""
    from sqlalchemy import extract, func

    q = db.query(CAELog).filter(
        extract("year", CAELog.created_at) == year,
        extract("month", CAELog.created_at) == month,
    )
    if pv is not None:
        q = q.filter(CAELog.punto_venta == pv)
    if user_id is not None:
        q = q.filter(CAELog.user_id == user_id)
    # Orden: fecha emisión, tipo cbte, PV, nro cbte
    q = q.order_by(
        CAELog.created_at.asc(),
        CAELog.tipo_comprobante.asc(),
        CAELog.punto_venta.asc(),
        CAELog.voucher_number.asc(),
    )
    return q.all()


def _build_lines_from_factusol(tipfac: int, codfac: int) -> tuple[list[dict], dict]:
    """Lee el detalle de la factura desde Factusol. Devuelve (líneas, header)."""
    detail = factusol_service.get_invoice_detail(tipfac, codfac)
    if not detail:
        return [], {}
    return detail.get("lines", []) or [], detail.get("header", {}) or {}


def _build_cliente_from_factusol(tipfac: int, codfac: int) -> dict:
    detail = factusol_service.get_invoice_detail(tipfac, codfac)
    if not detail:
        return {}
    return detail.get("cliente") or {}


def _compute_log_records(log: CAELog) -> dict:
    """
    Computa los registros tipo-1 (cabecera, detalle, ventas) y los importes de
    un único CAELog. Reutilizado por la exportación mensual (RG 1361) y por la
    exportación por comprobante (PAMI ACE) para que ambas usen exactamente la
    misma lógica de armado.
    """
    # Datos del header de Factusol (para fecha emisión, no_grav, exento, etc.)
    try:
        raw_lines, header_fs = _build_lines_from_factusol(log.tipfac, log.codfac)
        cliente_fs = _build_cliente_from_factusol(log.tipfac, log.codfac)
        # Descartar lineas-leyenda (cantidad=0 precio=0): son texto descriptivo
        # que Factusol acepta como item pero no son items reales.
        from app.services.arca_service import filter_real_lines
        lines_fs = filter_real_lines(raw_lines)
    except Exception:
        lines_fs, header_fs, cliente_fs = [], {}, {}

    # Fecha del comprobante: preferir FECFAC; si no, created_at del CAE
    fecha_cbte = header_fs.get("FECFAC") or log.created_at
    if hasattr(fecha_cbte, "date"):
        fecha_cbte = fecha_cbte.date() if isinstance(fecha_cbte, datetime) else fecha_cbte

    # Importes
    imp_total = float(log.imp_total or 0)
    imp_neto = float(log.imp_neto or 0)
    imp_iva = float(log.imp_iva or 0)
    # imp_exento desde el header Factusol: cada slot BAS{i}FAC marcado como
    # "exento" en iva_mapping suma al exento.
    iva_map_cfg = get_config().get("iva_mapping", {}) or {}
    imp_exento = 0.0
    for i in (1, 2, 3, 4):
        raw = str(iva_map_cfg.get(f"tipo_{i}", "")).strip().lower()
        if raw == "exento":
            imp_exento += float(header_fs.get(f"BAS{i}FAC") or 0)
    # No gravado: lo que sobra entre el total y (neto + iva + exento)
    imp_no_grav = max(0.0, imp_total - imp_neto - imp_iva - imp_exento)

    # Cliente
    nif = (cliente_fs.get("NIFCLI") or log.cliente_doc or "")
    cfecli = int(cliente_fs.get("CFECLI") or 0)
    razon = cliente_fs.get("NOFCLI") or log.cliente_nombre or ""

    # Cantidad de alícuotas distintas en el comprobante
    alicuotas_set = set()
    for ln in lines_fs:
        piv = ln.get("PIVLFA")
        if piv is not None:
            alicuotas_set.add(round(float(piv), 2))
    cant_alic = max(1, len(alicuotas_set)) if lines_fs else 1

    # ── CABECERA tipo 1 ──
    cabecera = _build_cabecera_tipo1(
        fecha=fecha_cbte,
        tipo_cbte=log.tipo_comprobante,
        pv=log.punto_venta,
        nro_cbte=log.voucher_number,
        cuit_cliente_raw=nif,
        razon_social=razon,
        imp_total=imp_total,
        imp_no_grav=imp_no_grav,
        imp_neto=imp_neto,
        imp_iva=imp_iva,
        imp_exento=imp_exento,
        cfecli=cfecli,
        cant_alicuotas=cant_alic,
        cae=log.cae or "",
        cae_vto=log.cae_vto or "",
    )

    # ── DETALLE: una línea por cada ítem de la factura ──
    detalle: list[str] = []
    if lines_fs:
        for idx, ln in enumerate(lines_fs, start=1):
            cantidad = float(ln.get("CANLFA") or 0)
            precio = float(ln.get("PRELFA") or 0)
            tot_linea = float(ln.get("TOTLFA") or 0)
            bonif = max(0.0, (cantidad * precio) - tot_linea)
            piv = float(ln.get("PIVLFA") or 0)
            desc = ln.get("DESLFA") or ""
            detalle.append(_build_detalle_tipo1(
                fecha=fecha_cbte,
                tipo_cbte=log.tipo_comprobante,
                pv=log.punto_venta,
                nro_cbte=log.voucher_number,
                cantidad=cantidad,
                unidad_medida=7,
                precio_unitario=precio,
                bonificacion=bonif,
                subtotal=tot_linea,
                alicuota_porc=piv,
                descripcion=desc,
                nro_item=idx,
            ))
    else:
        # Si no se pudo leer Factusol, generar una línea sintética con totales
        alic_porc = 21.0 if imp_iva > 0 else 0.0
        detalle.append(_build_detalle_tipo1(
            fecha=fecha_cbte,
            tipo_cbte=log.tipo_comprobante,
            pv=log.punto_venta,
            nro_cbte=log.voucher_number,
            cantidad=1.0,
            unidad_medida=7,
            precio_unitario=imp_neto,
            bonificacion=0.0,
            subtotal=imp_neto,
            alicuota_porc=alic_porc,
            descripcion="Comprobante",
            nro_item=1,
        ))

    # ── VENTAS: 1 registro por comprobante ──
    ventas = _build_ventas_tipo1(
        fecha=fecha_cbte,
        tipo_cbte=log.tipo_comprobante,
        pv=log.punto_venta,
        nro_cbte=log.voucher_number,
        cuit_cliente_raw=nif,
        razon_social=razon,
        imp_total=imp_total,
        imp_no_grav=imp_no_grav,
        imp_neto=imp_neto,
        imp_iva=imp_iva,
        imp_exento=imp_exento,
    )

    # Período propio del comprobante (AAAAMM) para el registro tipo 2
    if isinstance(fecha_cbte, (datetime, date)):
        periodo = f"{fecha_cbte.year:04d}{fecha_cbte.month:02d}"
    else:
        periodo = _date_yyyymmdd(fecha_cbte)[:6]

    return {
        "cabecera": cabecera,
        "detalle": detalle,
        "ventas": ventas,
        "totales": {
            "imp_total": imp_total,
            "imp_neto": imp_neto,
            "imp_iva": imp_iva,
            "imp_no_grav": imp_no_grav,
            "imp_exento": imp_exento,
        },
        "periodo": periodo,
        "tipo_cbte": log.tipo_comprobante,
        "pv": log.punto_venta,
        "nro_cbte": log.voucher_number,
        "cuit_receptor": "".join(c for c in str(nif or "") if c.isdigit()),
    }


def generate_files(
    db: Session,
    *,
    year: int,
    month: int,
    pv: Optional[int] = None,
    user_id: Optional[int] = None,
) -> dict:
    """
    Genera los archivos CABECERA_AAAAMM.txt y DETALLE_AAAAMM.txt en memoria.
    Retorna dict con 'cabecera', 'detalle' (bytes), 'periodo' (AAAAMM),
    'count' y 'totales'.
    """
    config = get_config()
    cuit_emisor = "".join(c for c in str(config.get("empresa", {}).get("cuit", "")) if c.isdigit())
    cuit_emisor = cuit_emisor.zfill(11)

    periodo = f"{year:04d}{month:02d}"
    logs = _iter_logs_for_period(db, year=year, month=month, pv=pv, user_id=user_id)

    cabecera_lines: list[str] = []
    detalle_lines: list[str] = []
    ventas_lines: list[str] = []
    totales = {"imp_total": 0.0, "imp_neto": 0.0, "imp_iva": 0.0, "imp_no_grav": 0.0, "imp_exento": 0.0}

    for log in logs:
        rec = _compute_log_records(log)
        cabecera_lines.append(rec["cabecera"])
        detalle_lines.extend(rec["detalle"])
        ventas_lines.append(rec["ventas"])
        for k in totales:
            totales[k] += rec["totales"][k]

    # ── Tipo 2 (footer) ──
    # Sólo CABECERA lleva tipo 2 (resumen). VENTAS y DETALLE no.
    cabecera_lines.append(_build_cabecera_tipo2(
        periodo_yyyymm=periodo,
        cant_tipo1=len(logs),
        cuit_emisor=cuit_emisor,
        totales=totales,
    ))

    # Unir con CRLF (0D0A) y agregar CRLF final tras cada registro
    cabecera_bytes = ("\r\n".join(cabecera_lines) + "\r\n").encode("ascii", errors="replace")
    detalle_bytes = ("\r\n".join(detalle_lines) + ("\r\n" if detalle_lines else "")).encode("ascii", errors="replace")
    ventas_bytes = ("\r\n".join(ventas_lines) + "\r\n").encode("ascii", errors="replace")

    return {
        "periodo": periodo,
        "count": len(logs),
        "cabecera": cabecera_bytes,
        "detalle": detalle_bytes,
        "ventas": ventas_bytes,
        "totales": totales,
        "cuit_emisor": cuit_emisor,
    }


def generate_zip(
    db: Session,
    *,
    year: int,
    month: int,
    pv: Optional[int] = None,
    user_id: Optional[int] = None,
) -> tuple[bytes, str, int]:
    """
    Empaqueta CABECERA_AAAAMM.txt + DETALLE_AAAAMM.txt + VENTAS_AAAAMM.txt
    en un ZIP en memoria. Devuelve (zip_bytes, filename, count).
    """
    data = generate_files(db, year=year, month=month, pv=pv, user_id=user_id)
    periodo = data["periodo"]

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"CABECERA_{periodo}.txt", data["cabecera"])
        zf.writestr(f"DETALLE_{periodo}.txt", data["detalle"])
        zf.writestr(f"VENTAS_{periodo}.txt", data["ventas"])

    pv_suffix = f"_PV{pv:04d}" if pv else ""
    filename = f"RG1361_{periodo}{pv_suffix}.zip"
    return buf.getvalue(), filename, data["count"]


# ─── Exportación por comprobante (portal PAMI ACE) ──────────────────────────
# PAMI ACE exige, POR CADA comprobante, un PDF + 3 TXT nombrados con la clave
# del comprobante: {CUIT_EMISOR}_{TIPO}_{PV}_{NRO}. El TIPO va en 2 dígitos
# (ej 06=FB), el PV en 4 (ej 0003) y el número en 8 (ej 00000032).

def _comprobante_basename(cuit_emisor: str, tipo_cbte: int, pv: int, nro_cbte: int) -> str:
    """Nombre base PAMI ACE de un comprobante (sin extensión)."""
    return f"{cuit_emisor}_{_num(tipo_cbte, 2)}_{_num(pv, 4)}_{_num(nro_cbte, 8)}"


# CUIT del INSSJP (PAMI) — el portal PAMI ACE sólo acepta comprobantes
# emitidos a este receptor.
PAMI_INSSJP_CUIT = "30522763922"


def generate_pami_files(
    db: Session,
    *,
    year: int,
    month: int,
    pv: Optional[int] = None,
    user_id: Optional[int] = None,
    only_pami: bool = True,
) -> dict:
    """
    Genera, POR COMPROBANTE, los 3 archivos TXT con el nombre que exige PAMI ACE:
        {CUIT_EMISOR}_{TIPO}_{PV}_{NRO}_CABECERA.txt
        {CUIT_EMISOR}_{TIPO}_{PV}_{NRO}_DETALLE.txt
        {CUIT_EMISOR}_{TIPO}_{PV}_{NRO}_VENTAS.txt

    Cada archivo contiene SOLO los registros de ese comprobante:
      - CABECERA: tipo 1 + tipo 2 (resumen del propio comprobante, cant=1).
      - DETALLE:  un registro tipo 1 por cada ítem.
      - VENTAS:   un registro tipo 1 (sin tipo 2).
    El PDF lo aporta Factusol con el mismo nombre base + ".pdf".

    Si only_pami=True (default), filtra y exporta solamente comprobantes cuyo
    receptor sea INSSJP (CUIT 30522763922); el portal rechaza cualquier otro.

    Devuelve dict con 'files', 'count', 'skipped_no_pami', 'cuit_emisor', 'periodo'.
    """
    config = get_config()
    cuit_emisor = "".join(c for c in str(config.get("empresa", {}).get("cuit", "")) if c.isdigit())
    cuit_emisor = cuit_emisor.zfill(11)

    periodo = f"{year:04d}{month:02d}"
    logs = _iter_logs_for_period(db, year=year, month=month, pv=pv, user_id=user_id)

    files: dict[str, bytes] = {}
    count_included = 0
    skipped_no_pami = 0
    for log in logs:
        rec = _compute_log_records(log)

        if only_pami and rec.get("cuit_receptor") != PAMI_INSSJP_CUIT:
            skipped_no_pami += 1
            continue

        base = _comprobante_basename(cuit_emisor, rec["tipo_cbte"], rec["pv"], rec["nro_cbte"])

        cab_tipo2 = _build_cabecera_tipo2(
            periodo_yyyymm=rec["periodo"],
            cant_tipo1=1,
            cuit_emisor=cuit_emisor,
            totales=rec["totales"],
        )

        cabecera_bytes = ("\r\n".join([rec["cabecera"], cab_tipo2]) + "\r\n").encode("ascii", errors="replace")
        detalle_bytes = ("\r\n".join(rec["detalle"]) + ("\r\n" if rec["detalle"] else "")).encode("ascii", errors="replace")
        ventas_bytes = (rec["ventas"] + "\r\n").encode("ascii", errors="replace")

        files[f"{base}_CABECERA.txt"] = cabecera_bytes
        files[f"{base}_DETALLE.txt"] = detalle_bytes
        files[f"{base}_VENTAS.txt"] = ventas_bytes
        count_included += 1

    return {
        "files": files,
        "count": count_included,
        "skipped_no_pami": skipped_no_pami,
        "cuit_emisor": cuit_emisor,
        "periodo": periodo,
    }


def generate_pami_zip(
    db: Session,
    *,
    year: int,
    month: int,
    pv: Optional[int] = None,
    user_id: Optional[int] = None,
    only_pami: bool = True,
) -> tuple[bytes, str, int, int]:
    """
    Empaqueta en un ZIP los TXT por comprobante (formato PAMI ACE).
    Devuelve (zip_bytes, filename, count, skipped_no_pami).
    """
    data = generate_pami_files(
        db, year=year, month=month, pv=pv, user_id=user_id, only_pami=only_pami,
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in data["files"].items():
            zf.writestr(name, content)

    pv_suffix = f"_PV{pv:04d}" if pv else ""
    filename = f"PAMI_ACE_{data['periodo']}{pv_suffix}.zip"
    return buf.getvalue(), filename, data["count"], data["skipped_no_pami"]
