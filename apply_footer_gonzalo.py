"""Agrega el link a Gonzalo Sarubilo en el footer text de las 8 paginas simples."""
import re
from pathlib import Path

PAGES = [
    "factusol-v3.html",
    "consultoria-v3.html",
    "contacto-v3.html",
    "industrias-v3.html",
    "descargas-v3.html",
    "resenas-v3.html",
    "modulo-arca-v3.html",
    "power-bi-v3.html",
]

base = Path("web_register")
for name in PAGES:
    p = base / name
    if not p.exists(): continue
    src = p.read_text(encoding="utf-8")
    # El footer común tiene el patron: <p>&copy; 2026 Goxtech · Córdoba, Argentina</p>
    # Voy a reemplazarlo con un texto que incluya el link a Gonzalo
    old = '<p>&copy; 2026 Goxtech · Córdoba, Argentina</p>'
    new = '<p>&copy; 2026 <strong>Goxtech</strong> · Fundada por <a href="/gonzalo-sarubilo/" style="color: var(--primary);">Gonzalo Sarubilo</a> · Córdoba, Argentina</p>'
    # Solo verificar si el footer ya tiene el link visible (no en JSON-LD ni meta)
    has_footer_link = '<a href="/gonzalo-sarubilo/"' in src.split('<footer')[-1] if '<footer' in src else False
    if old in src and not has_footer_link:
        src = src.replace(old, new, 1)
        p.write_text(src, encoding="utf-8")
        print(f"{name}: CHANGED")
    elif has_footer_link:
        print(f"{name}: skip (footer ya tiene link)")
    else:
        print(f"{name}: SKIP (copyright no encontrado en patron)")
