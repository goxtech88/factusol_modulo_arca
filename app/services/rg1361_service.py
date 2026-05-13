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


def _normalize_doc(doc_raw: str) -> tuple[str, str]:
    """
    Devuelve (codigo_doc, numero_doc) según RG 1361 - Tabla E.7.
    11 dígitos → CUIT (80). 7-8 dígitos → DNI (96). Otro/vacío → 99.
    """
    s = "".join(c for c in (doc_raw or "") if c.isdigit())
    if len(s) == 11:
        return "80", s.zfill(12)
    if 7 <= len(s) <= 8:
        return "96", s.zfill(12)
    return "99", "0" * 12


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
    """Registro tipo 1 del archivo CABECERA - 307 caracteres."""
    cod_doc, nro_doc = _normalize_doc(cuit_cliente_raw)

    parts = [
        "1",                                      # 1) Tipo registro
        _date_yyyymmdd(fecha),                    # 2) Fecha cbte
        _num(tipo_cbte, 2),                       # 3) Tipo cbte
        " ",                                      # 4) Controlador fiscal (no aplica)
        _num(pv, 4),                              # 5) Punto de venta
        _num(nro_cbte, 8),                        # 6) Nro comprobante
        _num(nro_cbte, 8),                        # 7) Nro cbte registrado
        _num(1, 3),                               # 8) Cantidad de hojas
        cod_doc,                                  # 9) Cod documento comprador
        nro_doc,                                  # 10) Nro identificación comprador
        _ascii(razon_social, 50),                 # 11) Apellido y nombre / razón social
        _amount(imp_total),                       # 12) Importe total operación
        _amount(imp_no_grav),                     # 13) Conceptos no gravados
        _amount(imp_neto),                        # 14) Neto gravado
        _amount(imp_iva),                         # 15) Impuesto liquidado (IVA)
        _amount(0),                               # 16) IVA liquidado a RNI
        _amount(imp_exento),                      # 17) Operaciones exentas
        _amount(0),                               # 18) Percepciones / pagos imp. nacionales
        _amount(0),                               # 19) Percepción ingresos brutos
        _amount(0),                               # 20) Percepción imp. municipales
        _amount(0),                               # 21) Impuestos internos
        _amount(imp_total),                       # 22) Transporte (sumatoria items)
        _resp_from_cfecli(cfecli),                # 23) Tipo responsable
        "PES",                                    # 24) Cod moneda
        "0001000000",                             # 25) Tipo cambio (1.000000)
        _num(cant_alicuotas or 1, 2),             # 26) Cantidad alícuotas IVA
        " ",                                      # 27) Cód operación (Z/X/E/blanco)
        _num(0, 9),                               # 28) CAI (impresión preimpresa - no aplica)
        _date_yyyymmdd(cae_vto),                  # 29) Fecha vto
        "0" * 8,                                  # 30) Fecha anulación
    ]
    line = "".join(parts)
    assert len(line) == 307, f"CABECERA tipo 1 debe ser 307 chars, fue {len(line)}"
    return line


def _build_cabecera_tipo2(
    *,
    periodo_yyyymm: str,
    cant_tipo1: int,
    cuit_emisor: str,
    totales: dict,
) -> str:
    """
    Registro tipo 2 del archivo CABECERA - 307 caracteres.
    Resumen: período + cantidad tipo 1 + CUIT informante + sumatorias de campos
    numéricos del tipo 1 (campos 12-22).
    """
    parts = [
        "2",                                      # 1) Tipo registro
        periodo_yyyymm,                           # 2) Período (AAAAMM)
        " " * 17,                                 # 3) Relleno (hasta pos 24)
        _num(cant_tipo1, 8),                      # 4) Cantidad registros tipo 1 (8 dígitos)
        " " * 17,                                 # 5) Relleno (hasta pos 49)
        cuit_emisor.zfill(11),                    # 6) CUIT informante (pos 50-60)
        " " * 39,                                 # 7) Relleno (hasta pos 99)
        _amount(totales.get("imp_total", 0)),     # 8) Total importe operación
        _amount(totales.get("imp_no_grav", 0)),   # 9) Total no gravado
        _amount(totales.get("imp_neto", 0)),      # 10) Total neto gravado
        _amount(totales.get("imp_iva", 0)),       # 11) Total impuesto liquidado
        _amount(0),                               # 12) Total IVA RNI
        _amount(totales.get("imp_exento", 0)),    # 13) Total exento
        _amount(0),                               # 14) Total percepciones nacionales
        _amount(0),                               # 15) Total percepción IIBB
        _amount(0),                               # 16) Total percepción municipal
        _amount(0),                               # 17) Total impuestos internos
        _amount(totales.get("imp_total", 0)),     # 18) Total transporte
    ]
    line = "".join(parts)
    # Padding hasta 307 (mismo largo que tipo 1)
    line = line.ljust(307)[:307]
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
    alicuota_iva: float,    # porcentaje (ej 21.0)
    imp_iva: float,
    imp_exento: float,
    cfecli: int,
    cae: str,
    cae_vto: str,
) -> str:
    """Registro tipo 1 del archivo VENTAS - 308 caracteres."""
    cod_doc, nro_doc_12 = _normalize_doc(cuit_cliente_raw)
    # VENTAS pide 20 chars para el numero de documento (no 12 como CABECERA)
    nro_doc = str(int(nro_doc_12) if nro_doc_12.isdigit() else 0).zfill(20)

    # Alicuota: 5 chars, 3 enteros + 2 decimales sin separador
    # Ej: 21.00 -> "02100", 10.50 -> "01050", 0.00 -> "00000"
    try:
        a = float(alicuota_iva or 0)
    except (TypeError, ValueError):
        a = 0.0
    alicuota_str = str(int(round(a * 100))).zfill(5)[-5:]

    parts = [
        "1",                                # 1) Tipo registro
        _date_yyyymmdd(fecha),              # 2) Fecha cbte (8)
        _num(tipo_cbte, 2),                 # 3) Tipo cbte
        " ",                                # 4) Controlador fiscal
        _num(pv, 4),                        # 5) Punto de venta
        _num(nro_cbte, 8),                  # 6) Nro cbte desde
        _num(nro_cbte, 8),                  # 7) Nro cbte hasta
        cod_doc,                            # 8) Cod doc comprador (2)
        nro_doc,                            # 9) Nro identif comprador (20)
        _ascii(razon_social, 30),           # 10) Apellido/denominacion (30)
        _amount(imp_total),                 # 11) Importe total operacion (15)
        _amount(imp_no_grav),               # 12) Conceptos no gravados (15)
        _amount(imp_neto),                  # 13) Neto gravado (15)
        alicuota_str,                       # 14) Alicuota IVA (5)
        _amount(imp_iva),                   # 15) Impuesto liquidado (15)
        _amount(0),                         # 16) IVA RNI / No categorizados
        _amount(imp_exento),                # 17) Operaciones exentas
        _amount(0),                         # 18) Percepciones nacionales
        _amount(0),                         # 19) Percepcion IIBB
        _amount(0),                         # 20) Percepcion municipal
        _amount(0),                         # 21) Impuestos internos
        _resp_from_cfecli(cfecli),          # 22) Tipo responsable
        "PES",                              # 23) Cod moneda
        "0001000000",                       # 24) Tipo cambio (1.000000)
        "1",                                # 25) Cant alicuotas IVA (1 char)
        " ",                                # 26) Cod operacion
        " " * 16,                           # 27) CAI (16 chars, no aplica para CAE)
        _date_yyyymmdd(cae_vto),            # 28) Fecha vencimiento (8)
        "0" * 8,                            # 29) Fecha anulacion (8)
        " " * 20,                           # 30) Info adicional (20)
    ]
    line = "".join(parts)
    # El registro debe tener 308 chars (pos 1-308)
    if len(line) != 308:
        line = line.ljust(308)[:308]
    return line


def _build_ventas_tipo2(
    *,
    periodo_yyyymm: str,
    cant_tipo1: int,
    cuit_emisor: str,
    totales: dict,
) -> str:
    """Registro tipo 2 (resumen) del archivo VENTAS - 308 caracteres."""
    parts = [
        "2",                                      # 1) Tipo registro
        periodo_yyyymm,                           # 2) Periodo AAAAMM (6)
        " " * 11,                                 # 3) Relleno hasta pos 18
        _num(cant_tipo1, 10),                     # 4) Cantidad registros tipo 1 (10)
        " " * 8,                                  # 5) Relleno hasta pos 36
        cuit_emisor.zfill(11),                    # 6) CUIT informante (11) pos 37-47
        " " * 6,                                  # 7) Relleno hasta pos 53
        _amount(totales.get("imp_total", 0)),     # 8) Total importe operacion
        _amount(totales.get("imp_no_grav", 0)),   # 9) Total no gravado
        _amount(totales.get("imp_neto", 0)),      # 10) Total neto gravado
        " " * 6,                                  # 11) Relleno hasta pos 104
        _amount(totales.get("imp_iva", 0)),       # 12) Total impuesto liquidado
        _amount(0),                               # 13) Total IVA RNI
        _amount(totales.get("imp_exento", 0)),    # 14) Total exento
        _amount(0),                               # 15) Total percepciones nacionales
        _amount(0),                               # 16) Total percepcion IIBB
        _amount(0),                               # 17) Total percepcion municipal
        _amount(0),                               # 18) Total impuestos internos
    ]
    line = "".join(parts)
    line = line.ljust(308)[:308]  # padding al ancho del tipo 1
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
    cod_alicuota: str,
    indicador_exento: str,
    descripcion: str,
) -> str:
    """Registro tipo 1 del archivo DETALLE - 95 caracteres + diseño libre."""
    parts = [
        _num(tipo_cbte, 2),                  # 1) Tipo cbte
        " ",                                 # 2) Controlador fiscal
        _date_yyyymmdd(fecha),               # 3) Fecha cbte
        _num(pv, 4),                         # 4) Punto de venta
        _num(nro_cbte, 8),                   # 5) Nro cbte
        _num(nro_cbte, 8),                   # 6) Nro cbte registrado
        _amount(cantidad, total_len=12, decimals=5),  # 7) Cantidad
        _num(unidad_medida or 7, 2),         # 8) Unidad de medida
        _amount(precio_unitario, total_len=16, decimals=3),  # 9) Precio unitario
        _amount(bonificacion),               # 10) Bonificación
        _amount(subtotal),                   # 11) Subtotal por registro
        cod_alicuota,                        # 12) Alícuota IVA aplicable
        indicador_exento or " ",             # 13) Indicación exento/gravado (E/G/blanco)
        " ",                                 # 14) Indicador anulación
        _ascii(descripcion, 100),            # 15) Diseño libre (descripción del ítem)
    ]
    line = "".join(parts)
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
        # Datos del header de Factusol (para fecha emisión, no_grav, exento, etc.)
        try:
            raw_lines, header_fs = _build_lines_from_factusol(log.tipfac, log.codfac)
            cliente_fs = _build_cliente_from_factusol(log.tipfac, log.codfac)
            # Descartar lineas-leyenda (cantidad=0 precio=0): son texto descriptivo
            # que Factusol acepta como item pero no son items reales. Se omiten en
            # el DETALLE para no generar ruido en el archivo RG 1361.
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
        # Calcular imp_exento desde el header Factusol usando el mapeo:
        # cada slot BAS{i}FAC marcado como "exento" en iva_mapping suma al exento.
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
        cabecera_lines.append(_build_cabecera_tipo1(
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
        ))

        # ── DETALLE tipo 1: una línea por cada ítem de la factura ──
        if lines_fs:
            for ln in lines_fs:
                cantidad = float(ln.get("CANLFA") or 0)
                precio = float(ln.get("PRELFA") or 0)
                # Bonificación: usar TOTLFA - (cantidad * precio) si existe
                tot_linea = float(ln.get("TOTLFA") or 0)
                bonif = max(0.0, (cantidad * precio) - tot_linea)
                piv = float(ln.get("PIVLFA") or 0)
                desc = ln.get("DESLFA") or ""
                cod_alic = _cod_alicuota(piv)
                ind_ex = "E" if abs(piv) < 0.01 else "G"
                detalle_lines.append(_build_detalle_tipo1(
                    fecha=fecha_cbte,
                    tipo_cbte=log.tipo_comprobante,
                    pv=log.punto_venta,
                    nro_cbte=log.voucher_number,
                    cantidad=cantidad,
                    unidad_medida=7,
                    precio_unitario=precio,
                    bonificacion=bonif,
                    subtotal=tot_linea,
                    cod_alicuota=cod_alic,
                    indicador_exento=ind_ex,
                    descripcion=desc,
                ))
        else:
            # Si no se pudo leer Factusol, generar una línea sintética con totales
            cod_alic = _cod_alicuota(21.0 if imp_iva > 0 else 0.0)
            ind_ex = "G" if imp_iva > 0 else "E"
            detalle_lines.append(_build_detalle_tipo1(
                fecha=fecha_cbte,
                tipo_cbte=log.tipo_comprobante,
                pv=log.punto_venta,
                nro_cbte=log.voucher_number,
                cantidad=1.0,
                unidad_medida=7,
                precio_unitario=imp_neto,
                bonificacion=0.0,
                subtotal=imp_neto,
                cod_alicuota=cod_alic,
                indicador_exento=ind_ex,
                descripcion="Comprobante",
            ))

        # ── VENTAS tipo 1: 1 registro por cbte (alicuota principal del log) ──
        # Si neto > 0, calcular alicuota implicita; si no, asumir 0 (exento)
        if imp_neto > 0:
            alicuota_calc = round((imp_iva / imp_neto) * 100, 2)
        else:
            # Si no hay neto, usar la alicuota mas comun encontrada en lineas (si hay)
            alicuota_calc = round(sorted(alicuotas_set)[0], 2) if alicuotas_set else 0.0
        ventas_lines.append(_build_ventas_tipo1(
            fecha=fecha_cbte,
            tipo_cbte=log.tipo_comprobante,
            pv=log.punto_venta,
            nro_cbte=log.voucher_number,
            cuit_cliente_raw=nif,
            razon_social=razon,
            imp_total=imp_total,
            imp_no_grav=imp_no_grav,
            imp_neto=imp_neto,
            alicuota_iva=alicuota_calc,
            imp_iva=imp_iva,
            imp_exento=imp_exento,
            cfecli=cfecli,
            cae=log.cae or "",
            cae_vto=log.cae_vto or "",
        ))

        # Totales del tipo 2
        totales["imp_total"] += imp_total
        totales["imp_neto"] += imp_neto
        totales["imp_iva"] += imp_iva
        totales["imp_no_grav"] += imp_no_grav
        totales["imp_exento"] += imp_exento

    # ── Tipo 2 (footer) ──
    cabecera_lines.append(_build_cabecera_tipo2(
        periodo_yyyymm=periodo,
        cant_tipo1=len(logs),
        cuit_emisor=cuit_emisor,
        totales=totales,
    ))
    ventas_lines.append(_build_ventas_tipo2(
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
