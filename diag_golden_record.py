"""
Diagnóstico (solo lectura): compara campo a campo el F_FAC (y sus líneas
F_LFA) de una factura de prueba contra una Nota de Crédito creada A MANO
desde la propia UI de Factusol sobre esa misma factura (serie NC, ej. "9").

Objetivo: responder empíricamente preguntas que la documentación de esquema
no puede (está desactualizada -- ver diag_schema_nc.py):
  - Qué valor usa Factusol en ESTFAC para una NC.
  - Qué pone en TDRFAC/CDRFAC/EDRFAC (vínculo con el documento rectificado).
  - Si DT1LFA/DT2LFA/DT3LFA se copian tal cual de la factura original o van a 0.
  - Si Factusol YA revierte el stock (F_STO) solo al grabar la NC desde su
    propia UI -- si es así, create_credit_note_invoice() NO debería tocar
    F_STO cuando el comprobante se generó por este camino (no aplica a
    nuestro INSERT programático, pero confirma si Factusol tiene lógica de
    cliente que actualiza F_STO al detectar cantidad negativa).

Procedimiento:
  1. En la propia app de Factusol, sobre una factura de prueba de bajo
     importe, generar una NC a mano eligiendo la serie NC (ej. "9").
  2. Anotar (tipfac, codfac) de la factura original y (tipfac_nc, codfac_nc)
     de la NC recién creada.
  3. Correr:
       venv\\Scripts\\python.exe diag_golden_record.py <tipfac_orig> <codfac_orig> <tipfac_nc> <codfac_nc>

Solo lee la base; no modifica nada.
"""
import sys
sys.path.insert(0, ".")

from app.services.factusol_service import _get_connection
from app.config import get_config

if len(sys.argv) != 5:
    print(__doc__)
    print("Uso: python diag_golden_record.py <tipfac_orig> <codfac_orig> <tipfac_nc> <codfac_nc>")
    sys.exit(1)

tipfac_orig, codfac_orig, tipfac_nc, codfac_nc = sys.argv[1:5]

print("Factusol db_path =", get_config().get("factusol", {}).get("db_path"))
print()

con = _get_connection()
cur = con.cursor()


def dump_fac(tipfac, codfac, label):
    cur.execute("SELECT * FROM F_FAC WHERE TIPFAC = ? AND CODFAC = ?", [tipfac, codfac])
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    print(f"--- F_FAC {label} (TIPFAC={tipfac!r} CODFAC={codfac!r}) ---")
    if row is None:
        print("  (no encontrado -- revisar los valores pasados)")
        return None
    valores = dict(zip(cols, row))
    for c, v in valores.items():
        print(f"  {c:12} = {v!r}")
    print()
    return valores


def dump_lfa(tipfac, codfac, label):
    cur.execute(
        "SELECT * FROM F_LFA WHERE TIPLFA = ? AND CODLFA = ? ORDER BY POSLFA",
        [tipfac, codfac],
    )
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    print(f"--- F_LFA {label} (TIPLFA={tipfac!r} CODLFA={codfac!r}) -- {len(rows)} línea(s) ---")
    parsed = []
    for row in rows:
        valores = dict(zip(cols, row))
        parsed.append(valores)
        for c, v in valores.items():
            print(f"    {c:12} = {v!r}")
        print()
    return parsed


orig_header = dump_fac(tipfac_orig, codfac_orig, "ORIGINAL")
nc_header = dump_fac(tipfac_nc, codfac_nc, "NC (creada a mano en Factusol)")

orig_lines = dump_lfa(tipfac_orig, codfac_orig, "ORIGINAL")
nc_lines = dump_lfa(tipfac_nc, codfac_nc, "NC (creada a mano en Factusol)")

if orig_header and nc_header:
    print("=== Comparación rápida de campos clave (header) ===")
    for campo in ("ESTFAC", "TDRFAC", "CDRFAC", "EDRFAC", "TOTFAC", "ALMFAC"):
        vo = orig_header.get(campo)
        vn = nc_header.get(campo)
        print(f"  {campo:10} original={vo!r:20} nc={vn!r}")
    print()

if orig_lines and nc_lines:
    print("=== Comparación rápida de la primera línea ===")
    lo, ln = orig_lines[0], nc_lines[0]
    for campo in ("CANLFA", "TOTLFA", "PRELFA", "PIVLFA", "IVALFA", "DT1LFA", "DT2LFA", "DT3LFA"):
        print(f"  {campo:10} original={lo.get(campo)!r:20} nc={ln.get(campo)!r}")
    print()

print("=== F_STO del/los artículo(s) de la factura original (estado ACTUAL, post-NC) ===")
if orig_lines:
    almacen = orig_header.get("ALMFAC") if orig_header else None
    for ln in orig_lines:
        articulo = ln.get("ARTLFA")
        cur.execute(
            "SELECT ARTSTO, ALMSTO, ACTSTO, DISSTO FROM F_STO WHERE ARTSTO = ? AND ALMSTO = ?",
            [articulo, almacen],
        )
        row = cur.fetchone()
        print(f"  articulo={articulo!r} almacen={almacen!r} -> {row}")
print()
print("Si el stock de estos artículos YA refleja la devolución (subió respecto")
print("a como hubiera quedado solo con la factura original), Factusol revierte")
print("stock solo al grabar la NC desde su propia UI. Si no, confirma que nuestra")
print("reversión programática en create_credit_note_invoice() es necesaria.")

con.close()
