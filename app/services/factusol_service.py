"""
Servicio de acceso a la base de datos Factusol (MS Access via pyodbc).
"""
import pyodbc
from typing import Optional
from app.config import get_config


def _get_connection(readonly: bool = True):
    """Crea una conexión ODBC a la base de datos Factusol."""
    config = get_config()
    db_path = config["factusol"]["db_path"]
    if not db_path:
        raise ValueError("No se ha configurado la ruta a la base de datos Factusol. Ir a Configuración.")

    # Mode=Share Deny None: permite abrir aunque Factusol esté corriendo.
    # En modo escritura NO usamos readonly=True en pyodbc, éste es solo informativo.
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={db_path};"
        r"Mode=Share Deny None;"
        r"ExtendedAnsiSQL=1;"
    )
    return pyodbc.connect(conn_str)


def get_invoices(
    tipfac: int,
    search: str = "",
    date_filter: str = "all",  # all | today | yesterday | last7
    fopfac: str = "",  # filtro por forma de pago (código)
) -> list[dict]:
    """
    Obtiene facturas de Factusol filtradas por serie (TIPFAC).
    date_filter admite: 'all', 'today', 'yesterday', 'last7'
    fopfac: código de forma de pago para filtrar (vacío = todas)
    """
    from datetime import date, timedelta

    today = date.today()

    # Calcular rango de fechas
    fecha_desde = None
    fecha_hasta = None
    if date_filter == "today":
        fecha_desde = today
        fecha_hasta = today
    elif date_filter == "yesterday":
        fecha_desde = today - timedelta(days=1)
        fecha_hasta = today - timedelta(days=1)
    elif date_filter == "last7":
        fecha_desde = today - timedelta(days=6)
        fecha_hasta = today
    elif date_filter == "this_week":
        # Semana actual: lunes a domingo (semana ISO)
        dow = today.weekday()  # 0 = lunes, 6 = domingo
        fecha_desde = today - timedelta(days=dow)
        fecha_hasta = fecha_desde + timedelta(days=6)
    elif date_filter == "this_month":
        fecha_desde = today.replace(day=1)
        fecha_hasta = today
    elif date_filter == "last_month":
        first_this = today.replace(day=1)
        last_prev = first_this - timedelta(days=1)
        fecha_desde = last_prev.replace(day=1)
        fecha_hasta = last_prev
    elif date_filter == "this_year":
        fecha_desde = today.replace(month=1, day=1)
        fecha_hasta = today

    conn = _get_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT f.TIPFAC, f.CODFAC, f.FECFAC, f.CLIFAC, f.CNOFAC,
                   f.TOTFAC, f.ESTFAC, f.ALMFAC, f.PEDFAC, f.CNIFAC,
                   f.BNOFAC, f.BNUFAC, f.FOPFAC, fp.DESFPA
            FROM F_FAC f
            LEFT JOIN F_FPA fp ON f.FOPFAC = fp.CODFPA
            WHERE f.TIPFAC = ?
        """
        params: list = [tipfac]

        if fopfac:
            query += " AND f.FOPFAC = ?"
            params.append(fopfac)

        if fecha_desde:
            # Access ODBC acepta datetime.date directamente via pyodbc
            query += " AND f.FECFAC >= ? AND f.FECFAC < ?"
            params.append(fecha_desde)
            params.append(fecha_hasta + timedelta(days=1))  # hasta fin del dia

        if search:
            query += " AND (f.CNOFAC LIKE ? OR CStr(f.CODFAC) LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])

        query += " ORDER BY f.CODFAC DESC"
        cursor.execute(query, params)

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()


def get_invoice_detail(tipfac: int, codfac: int) -> Optional[dict]:
    """
    Obtiene el detalle completo de una factura: header + líneas + cliente.
    Solo selecciona campos que existen en F_FAC y F_LFA según el schema real.
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()

        # Header — solo campos confirmados en schema Factusol
        cursor.execute("""
            SELECT f.TIPFAC, f.CODFAC, f.FECFAC, f.CLIFAC, f.CNOFAC,
                   f.TOTFAC, f.ESTFAC, f.ALMFAC, f.PEDFAC, f.CNIFAC,
                   f.NET1FAC, f.NET2FAC, f.NET3FAC, f.NET4FAC,
                   f.BAS1FAC, f.BAS2FAC, f.BAS3FAC, f.BAS4FAC,
                   f.IIVA1FAC, f.IIVA2FAC, f.IIVA3FAC,
                   f.PIVA1FAC, f.PIVA2FAC, f.PIVA3FAC,
                   f.BNOFAC, f.BNUFAC, f.IMGFAC, f.FOPFAC, fp.DESFPA
            FROM F_FAC f
            LEFT JOIN F_FPA fp ON f.FOPFAC = fp.CODFPA
            WHERE f.TIPFAC = ? AND f.CODFAC = ?
        """, [tipfac, codfac])

        header_cols = [desc[0] for desc in cursor.description]
        header_row = cursor.fetchone()
        if not header_row:
            return None

        header = dict(zip(header_cols, header_row))

        # Líneas — solo campos que existen en F_LFA
        cursor.execute("""
            SELECT l.POSLFA, l.ARTLFA, l.DESLFA, l.CANLFA, l.PRELFA,
                   l.TOTLFA, l.PIVLFA, l.DT1LFA, l.DT2LFA, l.DT3LFA,
                   l.IVALFA
            FROM F_LFA l
            WHERE l.TIPLFA = ? AND l.CODLFA = ?
            ORDER BY l.POSLFA
        """, [tipfac, codfac])

        line_cols = [desc[0] for desc in cursor.description]
        lines = [dict(zip(line_cols, row)) for row in cursor.fetchall()]

        # Datos del cliente
        cliente = None
        if header.get("CLIFAC"):
            cursor.execute("""
                SELECT c.CODCLI, c.NOFCLI, c.DOMCLI, c.POBCLI,
                       c.CPOCLI, c.PROCLI, c.NIFCLI, c.TELCLI, c.IVACLI, c.CFECLI
                FROM F_CLI c
                WHERE c.CODCLI = ?
            """, [header["CLIFAC"]])
            cli_cols = [desc[0] for desc in cursor.description]
            cli_row = cursor.fetchone()
            if cli_row:
                cliente = dict(zip(cli_cols, cli_row))

        return {
            "header": header,
            "lines": lines,
            "cliente": cliente,
        }
    finally:
        conn.close()



def update_customer_fiscal(codcli: int, data: dict) -> bool:
    """Actualiza datos fiscales del cliente en F_CLI."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        sets = []
        params = []
        field_map = {
            "NOFCLI": str, "DOMCLI": str, "POBCLI": str, "CPOCLI": str,
            "PROCLI": str, "NIFCLI": str, "CFECLI": int, "IVACLI": int,
        }
        for field, cast in field_map.items():
            if field in data and data[field] is not None:
                sets.append(f"{field} = ?")
                params.append(cast(data[field]))

        if not sets:
            return False

        params.append(codcli)
        cursor.execute(
            f"UPDATE F_CLI SET {', '.join(sets)} WHERE CODCLI = ?",
            params,
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()



def get_articles(search: str = "", limit: int = 50) -> list[dict]:
    """Obtiene lista de artículos."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT CODART, DESART, FAMART, PHAART, IVALIN FROM F_ART"
        params = []
        if search:
            query += " WHERE DESART LIKE ? OR CODART LIKE ?"
            params = [f"%{search}%", f"%{search}%"]
        query += " ORDER BY DESART"
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        conn.close()


def test_connection() -> dict:
    """Prueba la conexión a Factusol y retorna info básica."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM F_FAC")
        total_fac = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM F_CLI")
        total_cli = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM F_ART")
        total_art = cursor.fetchone()[0]
        conn.close()
        return {
            "status": "ok",
            "facturas": total_fac,
            "clientes": total_cli,
            "articulos": total_art,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def write_cae_to_factura(
    tipfac: int,
    codfac: int,
    cae: str,
    voucher_number: int,
    cae_vto: str,
    qr_img_path: str = "",
    barcode: str = "",
) -> bool:
    """
    Graba los datos del CAE AFIP de vuelta en F_FAC de Factusol:

      BNOFAC  = Número de CAE  (ej: "12345678901234")
      PEDFAC  = Número de comprobante ARCA  (ej: "B-0002-00006486")
      BIBFAC  = Número de comprobante ARCA  (duplicado para impresión)
      BNUFAC  = Vencimiento del CAE  (ej: "20240131")
      IMGFAC  = Ruta imagen QR
      AATFAC  = Código de barras AFIP (CUIT+TipoCbte+PV+CAE+VtoCae)
      REAFAC  = Código de barras AFIP (duplicado)

    Retorna True si se actualizó correctamente.
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE F_FAC
            SET BNOFAC = ?, PEDFAC = ?, BIBFAC = ?,
                BNUFAC = ?, IMGFAC = ?,
                AATFAC = ?, REAFAC = ?
            WHERE TIPFAC = ? AND CODFAC = ?
        """, [
            str(cae)[:50],               # BNOFAC  — CAE
            str(voucher_number),          # PEDFAC  — Nro Cbte formateado
            str(voucher_number),          # BIBFAC  — Nro Cbte (impresión)
            str(cae_vto)[:20],            # BNUFAC  — Vto CAE
            str(qr_img_path)[:255],       # IMGFAC  — Ruta QR
            str(barcode)[:60],            # AATFAC  — Código de barras
            str(barcode)[:60],            # REAFAC  — Código de barras
            tipfac,
            codfac,
        ])
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_invoice_date(tipfac: int, codfac: int, nueva_fecha) -> bool:
    """
    Actualiza FECFAC en F_FAC para que la factura quede con la fecha realmente
    enviada a ARCA. Imprescindible para que la fecha de Factusol coincida con
    la del CAE cuando se autoajusto por estar fuera del rango AFIP.

    `nueva_fecha` puede ser date, datetime o string 'YYYY-MM-DD'.
    """
    from datetime import datetime, date
    if isinstance(nueva_fecha, datetime):
        f = nueva_fecha.date()
    elif isinstance(nueva_fecha, date):
        f = nueva_fecha
    elif isinstance(nueva_fecha, str):
        s = nueva_fecha.strip()
        if len(s) >= 10 and s[4] == "-" and s[7] == "-":
            f = date(int(s[:4]), int(s[5:7]), int(s[8:10]))
        elif len(s) == 8 and s.isdigit():
            f = date(int(s[:4]), int(s[4:6]), int(s[6:8]))
        else:
            raise ValueError(f"Fecha invalida: {nueva_fecha!r}")
    else:
        raise ValueError(f"Tipo de fecha no soportado: {type(nueva_fecha).__name__}")

    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE F_FAC SET FECFAC = ? WHERE TIPFAC = ? AND CODFAC = ?",
            [f, tipfac, codfac],
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Notas de Credito: clonado del comprobante en Factusol ──────────────────
#
# Factusol (software espanol) no tiene un tipo de comprobante nativo para
# "Nota de Credito AFIP": modela esto como "factura rectificativa" -- otra
# fila de F_FAC en una serie propia, con los importes en negativo, vinculada
# a la factura original via TDRFAC/CDRFAC/EDRFAC. Es el mismo procedimiento
# que usa la propia UI de Factusol al pedir una NC ("elegis la serie, cantidad
# en negativo").
#
# IMPORTANTE: los valores de ESTFAC/TDRFAC/CDRFAC/EDRFAC de abajo son el mejor
# valor conocido a partir del schema documentado + campos ya usados en
# produccion, pero no estan 100% verificados contra una NC creada a mano en
# Factusol real. Correr diag_golden_record.py (raiz del repo) antes de
# confiar en produccion, y ajustar aca si el resultado difiere.
_ESTFAC_NC_DEFAULT = 2  # placeholder: "Cobrada" en el enum ESTFAC -- confirmar con diag_golden_record.py


def _live_columns(cursor, table: str) -> set[str]:
    """Columnas realmente existentes en `table` segun la metadata ODBC (no el .md exportado)."""
    return {row.column_name.upper() for row in cursor.columns(table=table)}


def _filter_existing(fields: dict, live_cols: set[str]) -> dict:
    """Descarta campos que no existen en el schema real de esta instancia de Factusol."""
    missing = [c for c in fields if c.upper() not in live_cols]
    if missing:
        import logging
        logging.getLogger("factusol_service").warning(
            f"create_credit_note_invoice: columnas ausentes en el schema real, se omiten: {missing}"
        )
    return {c: v for c, v in fields.items() if c.upper() in live_cols}


def create_credit_note_invoice(
    original_header: dict,
    original_lines: list[dict],
    serie_nc,
) -> dict:
    """
    Clona la factura original (`original_header`/`original_lines`, tal como
    los devuelve get_invoice_detail) como un nuevo comprobante de Factusol en
    la serie NC configurada, con cantidades e importes en negativo, vinculado
    a la factura original via TDRFAC/CDRFAC/EDRFAC. Tambien revierte el stock
    (F_STO) de cada articulo -- negocio con stock simple, sin talla/color/lote.

    Solo pensada para NC TOTALES (clonado 1:1 de la factura completa) -- no
    recibe factor de escala para NC parciales.

    No graba datos de CAE (eso lo hace write_cae_to_factura, reusado con el
    tipfac/codfac que retorna esta funcion, una vez que ARCA ya autorizo la NC).

    Atomico: una sola conexion/cursor, un solo commit al final; cualquier
    excepcion revierte todo (header + lineas + stock, todo o nada).

    Retorna {"tipfac": int, "codfac": int} del comprobante NC recien creado.
    """
    from datetime import date as _date

    tipfac_nc = int(serie_nc)
    almacen = original_header.get("ALMFAC")
    fecfac_orig = original_header.get("FECFAC")
    ejercicio = getattr(fecfac_orig, "year", None) or _date.today().year

    conn = _get_connection()
    try:
        cursor = conn.cursor()
        live_fac_cols = _live_columns(cursor, "F_FAC")
        live_lfa_cols = _live_columns(cursor, "F_LFA")

        def _neg(campo: str) -> float:
            return -round(float(original_header.get(campo) or 0), 2)

        nuevo_codfac = None
        last_err = None
        for _intento in range(5):
            cursor.execute("SELECT MAX(CODFAC) FROM F_FAC WHERE TIPFAC = ?", [tipfac_nc])
            candidato = int(cursor.fetchone()[0] or 0) + 1

            header_fields = _filter_existing({
                "TIPFAC": tipfac_nc,
                "CODFAC": candidato,
                "FECFAC": fecfac_orig,
                "CLIFAC": original_header.get("CLIFAC"),
                "CNOFAC": original_header.get("CNOFAC"),
                "ALMFAC": almacen,
                "FOPFAC": original_header.get("FOPFAC"),
                "CNIFAC": original_header.get("CNIFAC"),
                "ESTFAC": _ESTFAC_NC_DEFAULT,
                "TDRFAC": original_header.get("TIPFAC"),
                "CDRFAC": original_header.get("CODFAC"),
                "EDRFAC": ejercicio,
                "NET1FAC": _neg("NET1FAC"), "NET2FAC": _neg("NET2FAC"),
                "NET3FAC": _neg("NET3FAC"), "NET4FAC": _neg("NET4FAC"),
                "BAS1FAC": _neg("BAS1FAC"), "BAS2FAC": _neg("BAS2FAC"),
                "BAS3FAC": _neg("BAS3FAC"), "BAS4FAC": _neg("BAS4FAC"),
                "IIVA1FAC": _neg("IIVA1FAC"), "IIVA2FAC": _neg("IIVA2FAC"), "IIVA3FAC": _neg("IIVA3FAC"),
                "PIVA1FAC": original_header.get("PIVA1FAC"),
                "PIVA2FAC": original_header.get("PIVA2FAC"),
                "PIVA3FAC": original_header.get("PIVA3FAC"),
                "TOTFAC": _neg("TOTFAC"),
            }, live_fac_cols)

            cols = list(header_fields.keys())
            sql = f"INSERT INTO F_FAC ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})"
            try:
                cursor.execute(sql, [header_fields[c] for c in cols])
                nuevo_codfac = candidato
                break
            except pyodbc.Error as e:
                last_err = e
                conn.rollback()
                msg = str(e).lower()
                if "duplicate" not in msg and "indice" not in msg and "index" not in msg and "clave" not in msg:
                    raise
        if nuevo_codfac is None:
            raise RuntimeError(
                f"No se pudo asignar CODFAC en la serie NC {tipfac_nc} tras 5 intentos: {last_err}"
            )

        for i, ln in enumerate(original_lines, start=1):
            cantidad = float(ln.get("CANLFA") or 0)
            total = float(ln.get("TOTLFA") or 0)
            line_fields = _filter_existing({
                "TIPLFA": tipfac_nc,
                "CODLFA": nuevo_codfac,
                "POSLFA": i,
                "ARTLFA": ln.get("ARTLFA"),
                "DESLFA": ln.get("DESLFA"),
                "CANLFA": -cantidad,
                "PRELFA": ln.get("PRELFA"),
                "TOTLFA": -total,
                "PIVLFA": ln.get("PIVLFA"),
                "IVALFA": ln.get("IVALFA"),
                "DT1LFA": ln.get("DT1LFA"),
                "DT2LFA": ln.get("DT2LFA"),
                "DT3LFA": ln.get("DT3LFA"),
            }, live_lfa_cols)
            cols = list(line_fields.keys())
            sql = f"INSERT INTO F_LFA ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})"
            cursor.execute(sql, [line_fields[c] for c in cols])

            # Reversion de stock: la cantidad original (positiva) vuelve al almacen.
            articulo = ln.get("ARTLFA")
            if articulo and cantidad and almacen:
                cursor.execute(
                    "UPDATE F_STO SET ACTSTO = ACTSTO + ?, DISSTO = DISSTO + ? "
                    "WHERE ARTSTO = ? AND ALMSTO = ?",
                    [cantidad, cantidad, articulo, almacen],
                )

        conn.commit()
        return {"tipfac": tipfac_nc, "codfac": nuevo_codfac}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_payment_methods() -> list[dict]:
    """Obtiene todas las formas de pago de la tabla F_FPA."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT CODFPA, DESFPA FROM F_FPA ORDER BY CODFPA")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        conn.close()


def infer_iva_mapping() -> dict:
    """
    Infiere el mapeo Tipo IVA (slot 1-4 Factusol) -> alicuota AFIP desde F_FAC.

    Estrategia:
      1. Detecta series fiscales: TIPFAC con al menos 1 factura con IVA cobrado
         (IIVA1+IIVA2+IIVA3 > 0). Filtra operaciones internas/presupuestos.
      2. Para cada slot 1-3, cuenta el % mas frecuente (PIVAxFAC) en facturas
         donde BASxFAC > 0. Snap al valor AFIP mas cercano si esta dentro de
         tolerancia (1.5%).
      3. Slot 4 (BAS4FAC sin PIVA): exento por convencion si hay facturas que
         lo usen.

    Retorna dict con:
      - mapping: {tipo_1, tipo_2, tipo_3, tipo_4} con valor AFIP o None si sin uso
      - stats: detalle de facturas analizadas y distribucion por slot
    """
    from collections import Counter

    AFIP_PCTS = [0.0, 2.5, 5.0, 10.5, 21.0, 27.0]

    def _closest_afip(pct: float) -> str | None:
        if pct < 0.01:
            return "0"
        closest = min(AFIP_PCTS, key=lambda x: abs(x - pct))
        if abs(closest - pct) <= 1.5:
            return str(closest) if closest != int(closest) else str(int(closest))
        return None

    conn = _get_connection()
    try:
        cursor = conn.cursor()

        # 1) Detectar series fiscales
        cursor.execute("""
            SELECT TIPFAC
            FROM F_FAC
            WHERE (IIVA1FAC + IIVA2FAC + IIVA3FAC) > 0
            GROUP BY TIPFAC
        """)
        series_fiscales = [r[0] for r in cursor.fetchall()]

        if not series_fiscales:
            return {
                "mapping": {},
                "stats": {
                    "series_fiscales": [],
                    "facturas_analizadas": 0,
                    "mensaje": "No se encontraron facturas con IVA cobrado. Configure el mapeo manualmente.",
                },
            }

        # 2) Leer facturas de esas series
        placeholders = ",".join("?" * len(series_fiscales))
        cursor.execute(
            f"""
            SELECT BAS1FAC, BAS2FAC, BAS3FAC, BAS4FAC,
                   PIVA1FAC, PIVA2FAC, PIVA3FAC
            FROM F_FAC
            WHERE TIPFAC IN ({placeholders})
            """,
            series_fiscales,
        )
        rows = cursor.fetchall()

        piv_counter = {1: Counter(), 2: Counter(), 3: Counter()}
        slot4_used = 0
        for r in rows:
            bases = [float(r[0] or 0), float(r[1] or 0), float(r[2] or 0), float(r[3] or 0)]
            pivs = [float(r[4] or 0), float(r[5] or 0), float(r[6] or 0)]
            for i in range(3):
                if bases[i] > 0:
                    piv_counter[i + 1][round(pivs[i], 2)] += 1
            if bases[3] > 0:
                slot4_used += 1

        # 3) Construir mapping
        mapping: dict[str, str | None] = {}
        slot_stats: dict[str, dict] = {}
        for slot in (1, 2, 3):
            c = piv_counter[slot]
            total = sum(c.values())
            slot_stats[f"tipo_{slot}"] = {
                "facturas": total,
                "top": [{"pct": p, "count": n} for p, n in c.most_common(3)],
            }
            if total == 0:
                mapping[f"tipo_{slot}"] = None
                continue
            top_pct = c.most_common(1)[0][0]
            mapping[f"tipo_{slot}"] = _closest_afip(top_pct)

        # Slot 4: exento si esta en uso, o None si no
        mapping["tipo_4"] = "exento" if slot4_used > 0 else None
        slot_stats["tipo_4"] = {"facturas": slot4_used}

        return {
            "mapping": mapping,
            "stats": {
                "series_fiscales": series_fiscales,
                "facturas_analizadas": len(rows),
                "por_slot": slot_stats,
            },
        }
    finally:
        conn.close()
