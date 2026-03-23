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
) -> list[dict]:
    """
    Obtiene facturas de Factusol filtradas por serie (TIPFAC).
    date_filter admite: 'all', 'today', 'yesterday', 'last7'
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
                   f.BNOFAC, f.BNUFAC
            FROM F_FAC f
            WHERE f.TIPFAC = ?
        """
        params: list = [tipfac]

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
                   f.BNOFAC, f.BNUFAC, f.IMGFAC
            FROM F_FAC f
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


def get_customers(search: str = "", limit: int = 200) -> list[dict]:
    """Obtiene lista de clientes con datos fiscales."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        query = """SELECT CODCLI, NOFCLI, DOMCLI, POBCLI, CPOCLI, PROCLI,
                          NIFCLI, TELCLI, IVACLI, CFECLI, EMACLI
                   FROM F_CLI"""
        params = []
        if search:
            query += " WHERE NOFCLI LIKE ? OR NIFCLI LIKE ? OR CODCLI LIKE ?"
            params = [f"%{search}%", f"%{search}%", f"%{search}%"]
        query += " ORDER BY NOFCLI"
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
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

