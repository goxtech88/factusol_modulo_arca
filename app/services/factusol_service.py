"""
Servicio de acceso a la base de datos Factusol (MS Access via pyodbc).
"""
import pyodbc
from typing import Optional
from app.config import get_config


def _get_connection():
    """Crea una conexión ODBC a la base de datos Factusol."""
    config = get_config()
    db_path = config["factusol"]["db_path"]
    if not db_path:
        raise ValueError("No se ha configurado la ruta a la base de datos Factusol. Ir a Configuración.")

    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={db_path};"
        r"ExtendedAnsiSQL=1;"
    )
    return pyodbc.connect(conn_str, readonly=True)


def get_invoices(tipfac: int, search: str = "", limit: int = 100, offset: int = 0) -> list[dict]:
    """
    Obtiene facturas de Factusol filtradas por serie (TIPFAC).
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT f.TIPFAC, f.CODFAC, f.FECFAC, f.CLIFAC, f.CNOFAC,
                   f.TOTFAC, f.ESTFAC, f.ALMFAC, f.PEDFAC
            FROM F_FAC f
            WHERE f.TIPFAC = ?
        """
        params = [tipfac]

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
    Obtiene el detalle completo de una factura: header + líneas.
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()

        # Header
        cursor.execute("""
            SELECT f.TIPFAC, f.CODFAC, f.FECFAC, f.CLIFAC, f.CNOFAC,
                   f.TOTFAC, f.ESTFAC, f.ALMFAC, f.PEDFAC, f.BENFAC,
                   f.NET1FAC, f.NET2FAC, f.NET3FAC,
                   f.IVA1FAC, f.IVA2FAC, f.IVA3FAC,
                   f.PIV1FAC, f.PIV2FAC, f.PIV3FAC
            FROM F_FAC f
            WHERE f.TIPFAC = ? AND f.CODFAC = ?
        """, [tipfac, codfac])

        header_cols = [desc[0] for desc in cursor.description]
        header_row = cursor.fetchone()
        if not header_row:
            return None

        header = dict(zip(header_cols, header_row))

        # Líneas
        cursor.execute("""
            SELECT l.POSLFA, l.ARTLFA, l.DESLFA, l.CANLFA, l.PRELFA,
                   l.TOTLFA, l.PIVLFA, l.DT1LFA, l.DT2LFA, l.DT3LFA,
                   l.BASLFA, l.IVALFA
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
                       c.CPOCLI, c.PROCLI, c.NIFCLI, c.TELCLI
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


def get_customers(search: str = "", limit: int = 50) -> list[dict]:
    """Obtiene lista de clientes."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT CODCLI, NOFCLI, DOMCLI, POBCLI, NIFCLI, TELCLI FROM F_CLI"
        params = []
        if search:
            query += " WHERE NOFCLI LIKE ? OR NIFCLI LIKE ?"
            params = [f"%{search}%", f"%{search}%"]
        query += " ORDER BY NOFCLI"
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
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
        # Contar facturas
        cursor.execute("SELECT COUNT(*) FROM F_FAC")
        total_fac = cursor.fetchone()[0]
        # Contar clientes
        cursor.execute("SELECT COUNT(*) FROM F_CLI")
        total_cli = cursor.fetchone()[0]
        # Contar artículos
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
