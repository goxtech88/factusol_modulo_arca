"""
Diagnóstico (solo lectura): vuelca el esquema REAL de F_FAC, F_LFA y F_STO
según la metadata que entrega el propio driver ODBC (Jet/ACE), no el export
Factusol_Base_Datos.md — que está comprobadamente desactualizado para F_LFA
(glosas cruzadas, y campos reales como DT1LFA/DT2LFA/DT3LFA/IVALFA/F_FAC.FECFAC
que ni figuran ahí pero se usan con éxito en producción).

Se usa como paso previo a escribir el INSERT de create_credit_note_invoice()
(clonado de Nota de Crédito en Factusol) — antes de fijar la lista de columnas
a setear hay que confirmar que existen tal cual se supone.

También reporta si existe un índice único sobre (TIPFAC, CODFAC) en F_FAC:
determina si una colisión de CODFAC calculado a mano (no hay autonumérico)
falla con excepción -- se puede reintentar -- o permite un duplicado
silencioso -- grave, hay que evitarlo por otra vía.

Uso (en la máquina donde corre la instancia, con su venv):
    venv\\Scripts\\python.exe diag_schema_nc.py

Solo lee la base; no modifica nada.
"""
import sys
sys.path.insert(0, ".")

from app.services.factusol_service import _get_connection
from app.config import get_config

print("Factusol db_path =", get_config().get("factusol", {}).get("db_path"))
print()

con = _get_connection()
cur = con.cursor()

for table in ("F_FAC", "F_LFA", "F_STO"):
    print(f"=== Columnas reales de {table} (via ODBC catalog) ===")
    try:
        cols = list(cur.columns(table=table))
    except Exception as e:
        print(f"  ERROR consultando columnas: {e}")
        continue
    if not cols:
        print("  (sin resultados -- revisar que el nombre de tabla sea correcto)")
    for row in cols:
        nullable = "NULL" if row.nullable else "NOT NULL"
        print(f"  {row.column_name:15} {row.type_name:15} size={row.column_size:<6} {nullable}")
    print()

    print(f"=== Índices de {table} ===")
    try:
        stats = list(cur.statistics(table=table))
    except Exception as e:
        print(f"  ERROR consultando índices: {e}")
        print()
        continue
    if not stats:
        print("  (sin índices reportados)")
    for row in stats:
        # pyodbc: non_unique == 0 significa índice UNICO
        es_unico = (row.non_unique == 0) if row.non_unique is not None else None
        print(f"  index={row.index_name!s:20} unique={es_unico!s:6} col={row.column_name}")
    print()

print("=== Pregunta clave: ¿hay índice único sobre (TIPFAC, CODFAC) en F_FAC? ===")
print("Revisar arriba en la sección de índices de F_FAC -- si aparecen ambas")
print("columnas bajo el mismo index_name con unique=True, un INSERT con CODFAC")
print("duplicado va a fallar con excepción (bien, se puede reintentar).")
print("Si no aparece, un duplicado podría insertarse silenciosamente (grave).")

con.close()
