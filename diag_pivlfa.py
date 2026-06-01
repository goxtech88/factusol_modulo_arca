"""
Diagnóstico: encuentra líneas de Factusol con una alícuota de IVA (PIVLFA)
fuera de las válidas para AFIP (0, 2.5, 5, 10.5, 21, 27). Una de esas líneas
es la que rompía la exportación RG 1361 / PAMI ACE ("DETALLE debe ser 189
chars, fue 192").

Uso (en la máquina donde corre la instancia, con su venv):
    venv\\Scripts\\python.exe diag_pivlfa.py

Solo lee la base; no modifica nada.
"""
import sys
sys.path.insert(0, ".")

from app.services.factusol_service import _get_connection
from app.config import get_config

VALIDAS = (0.0, 2.5, 5.0, 10.5, 21.0, 27.0)

print("Factusol db_path =", get_config().get("factusol", {}).get("db_path"))
print()

con = _get_connection()
cur = con.cursor()

# 1) Panorama: qué valores de PIVLFA existen
cur.execute("SELECT PIVLFA, COUNT(*) FROM F_LFA GROUP BY PIVLFA ORDER BY PIVLFA")
print("=== Valores distintos de PIVLFA en F_LFA ===")
for piv, n in cur.fetchall():
    flag = "" if (piv is not None and float(piv) in VALIDAS) else "   <-- ANOMALO"
    print(f"  PIVLFA = {str(piv):>14}   ({n} líneas){flag}")
print()

# 2) Detalle de las líneas anómalas, con el comprobante al que pertenecen
cur.execute(
    """
    SELECT l.TIPLFA, l.CODLFA, l.POSLFA, l.DESLFA,
           l.CANLFA, l.PRELFA, l.TOTLFA, l.PIVLFA,
           f.FECFAC, f.CNOFAC
    FROM F_LFA l
    LEFT JOIN F_FAC f ON l.TIPLFA = f.TIPFAC AND l.CODLFA = f.CODFAC
    WHERE l.PIVLFA IS NOT NULL
      AND l.PIVLFA NOT IN (0, 2.5, 5, 10.5, 21, 27)
    ORDER BY l.TIPLFA, l.CODLFA, l.POSLFA
    """
)
rows = cur.fetchall()
print(f"=== {len(rows)} línea(s) con PIVLFA fuera de las alícuotas válidas ===")
for r in rows:
    tip, cod, pos, desc, can, pre, tot, piv, fec, cli = r
    print(
        f"  Serie {tip} · Comprobante {cod} · línea {pos} · "
        f"fecha {fec} · cliente {str(cli)[:30]!r}"
    )
    print(
        f"      desc={str(desc)[:40]!r}  cant={can}  precio={pre}  "
        f"total={tot}  PIVLFA={piv}  <-- corregir esta alícuota en Factusol"
    )

if not rows:
    print("  (ninguna — la base ya está limpia)")

con.close()
