"""
Conexión a la base de datos de Factusol (.MDB / Access).
Maneja la lectura de facturas pendientes de CAE.
"""
import logging
import datetime
from dataclasses import dataclass
from typing import Optional, List

log = logging.getLogger(__name__)

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    log.warning("pyodbc no disponible. Instale con: pip install pyodbc")


class FactusolDBError(Exception):
    pass


@dataclass
class FacturaFactusol:
    """Representación de una factura leída desde la BD de Factusol."""
    id_factura: int
    numero: str                  # Ej: "0001-00001234"
    tipo: str                    # Ej: "FA", "FB", "FC"
    punto_venta: int
    nro_comprobante: int
    fecha: datetime.date
    cuit_receptor: str
    nombre_receptor: str
    condicion_iva_receptor: str  # Leída desde Factusol
    imp_total: float
    imp_neto: float
    imp_iva: float
    imp_exento: float = 0.0
    imp_no_gravado: float = 0.0
    cae: Optional[str] = None
    cae_fecha_vto: Optional[str] = None
    estado_cae: str = "PENDIENTE"   # PENDIENTE | APROBADO | RECHAZADO | ERROR

    def __str__(self):
        return (
            f"{self.tipo} {self.punto_venta:04d}-{self.nro_comprobante:08d} | "
            f"{self.nombre_receptor} | ${self.imp_total:,.2f} | CAE: {self.cae or 'Pendiente'}"
        )


class FactusolDB:
    """
    Acceso a la base de datos de Factusol (Microsoft Access / .MDB).

    Estructura de tablas Factusol relevantes:
      - FACEMI  : Facturas emitidas (cabecera)
      - FACCLI  : Clientes (datos del receptor)
      - FACLIN  : Líneas de factura (detalle)
      - EMPRESA : Datos del emisor
    """

    # ── Nombres de tablas y campos en Factusol (versión española) ──────────────
    # Nota: Los nombres exactos pueden variar según versión de Factusol.
    # Se incluye compatibilidad con las más comunes.
    TABLE_FACTURAS   = "FACEMI"
    TABLE_CLIENTES   = "FACCLI"
    TABLE_LINEAS     = "FACLIN"
    TABLE_EMPRESA    = "EMPRESA"

    # Campos clave en FACEMI
    CAMPO_ID         = "FAEID"
    CAMPO_TIPO       = "FAETIP"
    CAMPO_PV         = "FAESER"
    CAMPO_NRO        = "FAENUM"
    CAMPO_FECHA      = "FAEFEC"
    CAMPO_COD_CLI    = "FAECLI"
    CAMPO_IMP_TOTAL  = "FAETOT"
    CAMPO_IMP_NETO   = "FAENET"
    CAMPO_IMP_IVA    = "FAEIVA"
    CAMPO_IMP_EXENTO = "FAEEXE"
    CAMPO_CAE        = "FAECAE"
    CAMPO_CAE_VTO    = "FAECAEVTO"

    # Campos clave en FACCLI
    CAMPO_CLI_COD    = "CLICOD"
    CAMPO_CLI_NOM    = "CLINOM"
    CAMPO_CLI_CUIT   = "CLICIT"    # CUIT del cliente
    CAMPO_CLI_IVA    = "CLIIVA"    # Condición IVA

    def __init__(self, mdb_path: str, driver: str = "Microsoft Access Driver (*.mdb, *.accdb)"):
        if not PYODBC_AVAILABLE:
            raise FactusolDBError("pyodbc no está instalado. Ejecute: pip install pyodbc")
        self.mdb_path = mdb_path
        # Detectar driver adecuado según extensión
        ext = str(mdb_path).lower().split(".")[-1]
        if ext == "accdb":
            self.driver = "Microsoft Access Driver (*.mdb, *.accdb)"
        else:
            self.driver = driver
        self._conn    = None

    # ──────────────────────────────────────────────────────────────────────────
    # Conexión
    # ──────────────────────────────────────────────────────────────────────────

    def connect(self):
        """Establece la conexión con la base de datos de Factusol."""
        conn_str = (
            f"DRIVER={{{self.driver}}};"
            f"DBQ={self.mdb_path};"
            "ReadOnly=False;"
        )
        try:
            self._conn = pyodbc.connect(conn_str)
            self._conn.autocommit = True
            log.info("Conectado a Factusol DB: %s", self.mdb_path)
        except pyodbc.Error as e:
            raise FactusolDBError(f"No se pudo conectar a {self.mdb_path}: {e}") from e

    def disconnect(self):
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def _cursor(self):
        if not self._conn:
            self.connect()
        return self._conn.cursor()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()

    # ──────────────────────────────────────────────────────────────────────────
    # Consultas
    # ──────────────────────────────────────────────────────────────────────────

    def obtener_facturas_pendientes(self) -> List[FacturaFactusol]:
        """
        Retorna todas las facturas emitidas que aún no tienen CAE asignado.
        Filtra por: FAECAE IS NULL o FAECAE = ''
        """
        sql = f"""
            SELECT
                f.{self.CAMPO_ID},
                f.{self.CAMPO_TIPO},
                f.{self.CAMPO_PV},
                f.{self.CAMPO_NRO},
                f.{self.CAMPO_FECHA},
                f.{self.CAMPO_COD_CLI},
                f.{self.CAMPO_IMP_TOTAL},
                f.{self.CAMPO_IMP_NETO},
                f.{self.CAMPO_IMP_IVA},
                f.{self.CAMPO_IMP_EXENTO},
                c.{self.CAMPO_CLI_NOM},
                c.{self.CAMPO_CLI_CUIT},
                c.{self.CAMPO_CLI_IVA}
            FROM {self.TABLE_FACTURAS} f
            LEFT JOIN {self.TABLE_CLIENTES} c
                ON f.{self.CAMPO_COD_CLI} = c.{self.CAMPO_CLI_COD}
            WHERE (f.{self.CAMPO_CAE} IS NULL OR f.{self.CAMPO_CAE} = '')
              AND f.{self.CAMPO_TIPO} IN ('FA','FB','FC','FM','NCA','NCB','NCC','NDA','NDB','NDC')
            ORDER BY f.{self.CAMPO_FECHA} ASC, f.{self.CAMPO_NRO} ASC
        """
        return self._ejecutar_query_facturas(sql)

    def obtener_factura_por_id(self, id_factura: int) -> Optional[FacturaFactusol]:
        """Retorna una factura específica por su ID interno de Factusol."""
        sql = f"""
            SELECT
                f.{self.CAMPO_ID},
                f.{self.CAMPO_TIPO},
                f.{self.CAMPO_PV},
                f.{self.CAMPO_NRO},
                f.{self.CAMPO_FECHA},
                f.{self.CAMPO_COD_CLI},
                f.{self.CAMPO_IMP_TOTAL},
                f.{self.CAMPO_IMP_NETO},
                f.{self.CAMPO_IMP_IVA},
                f.{self.CAMPO_IMP_EXENTO},
                c.{self.CAMPO_CLI_NOM},
                c.{self.CAMPO_CLI_CUIT},
                c.{self.CAMPO_CLI_IVA}
            FROM {self.TABLE_FACTURAS} f
            LEFT JOIN {self.TABLE_CLIENTES} c
                ON f.{self.CAMPO_COD_CLI} = c.{self.CAMPO_CLI_COD}
            WHERE f.{self.CAMPO_ID} = ?
        """
        resultados = self._ejecutar_query_facturas(sql, (id_factura,))
        return resultados[0] if resultados else None

    def obtener_ultimas_facturas(self, limite: int = 50) -> List[FacturaFactusol]:
        """Retorna las últimas N facturas (con y sin CAE)."""
        sql = f"""
            SELECT TOP {limite}
                f.{self.CAMPO_ID},
                f.{self.CAMPO_TIPO},
                f.{self.CAMPO_PV},
                f.{self.CAMPO_NRO},
                f.{self.CAMPO_FECHA},
                f.{self.CAMPO_COD_CLI},
                f.{self.CAMPO_IMP_TOTAL},
                f.{self.CAMPO_IMP_NETO},
                f.{self.CAMPO_IMP_IVA},
                f.{self.CAMPO_IMP_EXENTO},
                c.{self.CAMPO_CLI_NOM},
                c.{self.CAMPO_CLI_CUIT},
                c.{self.CAMPO_CLI_IVA},
                f.{self.CAMPO_CAE},
                f.{self.CAMPO_CAE_VTO}
            FROM {self.TABLE_FACTURAS} f
            LEFT JOIN {self.TABLE_CLIENTES} c
                ON f.{self.CAMPO_COD_CLI} = c.{self.CAMPO_CLI_COD}
            ORDER BY f.{self.CAMPO_FECHA} DESC, f.{self.CAMPO_NRO} DESC
        """
        return self._ejecutar_query_facturas(sql, include_cae=True)

    def obtener_series(self) -> list:
        """Retorna las series/puntos de venta disponibles en Factusol."""
        sql = f"""
            SELECT DISTINCT {self.CAMPO_PV}, {self.CAMPO_TIPO}
            FROM {self.TABLE_FACTURAS}
            WHERE {self.CAMPO_TIPO} IN ('FA','FB','FC','FM','NCA','NCB','NCC','NDA','NDB','NDC')
            ORDER BY {self.CAMPO_PV}, {self.CAMPO_TIPO}
        """
        cur = self._cursor()
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            return [{"punto_venta": int(r[0] or 0), "tipo": (r[1] or "").strip()} for r in rows]
        except Exception as e:
            log.warning("No se pudieron obtener series: %s", e)
            return []
        finally:
            cur.close()

    def obtener_facturas_por_serie(self, punto_venta: int, tipo: str) -> list:
        """
        Retorna facturas pendientes de CAE filtrando por punto de venta y tipo.
        Útil para el modo manual donde el usuario elige serie por serie.
        """
        sql = f"""
            SELECT
                f.{self.CAMPO_ID},
                f.{self.CAMPO_TIPO},
                f.{self.CAMPO_PV},
                f.{self.CAMPO_NRO},
                f.{self.CAMPO_FECHA},
                f.{self.CAMPO_COD_CLI},
                f.{self.CAMPO_IMP_TOTAL},
                f.{self.CAMPO_IMP_NETO},
                f.{self.CAMPO_IMP_IVA},
                f.{self.CAMPO_IMP_EXENTO},
                c.{self.CAMPO_CLI_NOM},
                c.{self.CAMPO_CLI_CUIT},
                c.{self.CAMPO_CLI_IVA}
            FROM {self.TABLE_FACTURAS} f
            LEFT JOIN {self.TABLE_CLIENTES} c
                ON f.{self.CAMPO_COD_CLI} = c.{self.CAMPO_CLI_COD}
            WHERE (f.{self.CAMPO_CAE} IS NULL OR f.{self.CAMPO_CAE} = '')
              AND f.{self.CAMPO_PV} = ?
              AND f.{self.CAMPO_TIPO} = ?
            ORDER BY f.{self.CAMPO_NRO} ASC
        """
        return self._ejecutar_query_facturas(sql, (punto_venta, tipo.upper()))

    def guardar_cae(self, id_factura: int, cae: str, cae_fecha_vto: str):
        """
        Actualiza la factura en Factusol con el CAE obtenido de AFIP.
        cae_fecha_vto: formato AAAAMMDD → lo convertimos a fecha de Access
        """
        # Convertir fecha CAE a formato Access (MM/DD/YYYY)
        try:
            fecha_vto = datetime.datetime.strptime(cae_fecha_vto, "%Y%m%d").strftime("%m/%d/%Y")
        except ValueError:
            fecha_vto = cae_fecha_vto

        sql = f"""
            UPDATE {self.TABLE_FACTURAS}
            SET {self.CAMPO_CAE} = ?,
                {self.CAMPO_CAE_VTO} = ?
            WHERE {self.CAMPO_ID} = ?
        """
        cur = self._cursor()
        try:
            cur.execute(sql, (cae, fecha_vto, id_factura))
            log.info("CAE guardado en Factusol: factura %d → %s (vto %s)", id_factura, cae, fecha_vto)
        except pyodbc.Error as e:
            raise FactusolDBError(f"Error guardando CAE en Factusol: {e}") from e
        finally:
            cur.close()

    def obtener_datos_empresa(self) -> dict:
        """Obtiene los datos del emisor desde la tabla EMPRESA de Factusol."""
        sql = f"SELECT * FROM {self.TABLE_EMPRESA}"
        cur = self._cursor()
        try:
            cur.execute(sql)
            row = cur.fetchone()
            if row:
                cols = [col[0] for col in cur.description]
                return dict(zip(cols, row))
            return {}
        except pyodbc.Error as e:
            log.warning("No se pudo leer tabla EMPRESA: %s", e)
            return {}
        finally:
            cur.close()

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _ejecutar_query_facturas(self, sql: str, params=None, include_cae: bool = False) -> List[FacturaFactusol]:
        """Ejecuta una query y retorna lista de FacturaFactusol."""
        cur = self._cursor()
        try:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            resultado = []
            for row in rows:
                fac = self._row_to_factura(row, include_cae)
                if fac:
                    resultado.append(fac)
            return resultado
        except pyodbc.Error as e:
            raise FactusolDBError(f"Error consultando facturas: {e}") from e
        finally:
            cur.close()

    def _row_to_factura(self, row, include_cae: bool = False) -> Optional[FacturaFactusol]:
        """Convierte una fila de BD en un objeto FacturaFactusol."""
        try:
            if include_cae:
                (id_fac, tipo, pv, nro, fecha, cod_cli,
                 total, neto, iva, exento,
                 nombre, cuit, cond_iva, cae, cae_vto) = row
            else:
                (id_fac, tipo, pv, nro, fecha, cod_cli,
                 total, neto, iva, exento,
                 nombre, cuit, cond_iva) = row
                cae = None
                cae_vto = None

            # Normalizar valores
            tipo  = (tipo or "").strip().upper()
            cuit  = (cuit or "").replace("-", "").strip()
            pv    = int(pv or 0)
            nro   = int(nro or 0)

            if isinstance(fecha, str):
                try:
                    fecha = datetime.datetime.strptime(fecha, "%m/%d/%Y").date()
                except ValueError:
                    fecha = datetime.date.today()

            return FacturaFactusol(
                id_factura=int(id_fac),
                numero=f"{pv:04d}-{nro:08d}",
                tipo=tipo,
                punto_venta=pv,
                nro_comprobante=nro,
                fecha=fecha,
                cuit_receptor=cuit,
                nombre_receptor=(nombre or "").strip(),
                condicion_iva_receptor=(cond_iva or "").strip(),
                imp_total=float(total or 0),
                imp_neto=float(neto or 0),
                imp_iva=float(iva or 0),
                imp_exento=float(exento or 0),
                cae=cae,
                cae_fecha_vto=cae_vto,
                estado_cae="APROBADO" if cae else "PENDIENTE",
            )
        except Exception as e:
            log.warning("Error convirtiendo fila a FacturaFactusol: %s | Row: %s", e, row)
            return None
