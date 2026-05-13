"""
Unifica el nav en las 9 paginas v3.

Menu canonico (8 items + CTA Hablemos):
  /                  Inicio
  /factusol/         Factusol
  /modulo-arca/      Modulo ARCA
  /power-bi/         Power BI
  /consultoria/      Consultoria
  /industrias/       Industrias
  /descargas/        Descargas
  /contacto/         Contacto
  + boton "Hablemos →" con WA

Aplica class="active" segun la pagina actual.
"""
import re
from pathlib import Path

LOGO_MAIN = "https://goxtech.com.ar/arca_factusol/api/uploads/site/logo_main-1778620488.png"

ITEMS = [
    ("/",              "Inicio",       "home"),
    ("/factusol/",     "Factusol",     "factusol"),
    ("/modulo-arca/",  "Módulo ARCA",  "modulo-arca"),
    ("/power-bi/",     "Power BI",     "power-bi"),
    ("/consultoria/",  "Consultoría",  "consultoria"),
    ("/industrias/",   "Industrias",   "industrias"),
    ("/descargas/",    "Descargas",    "descargas"),
    ("/contacto/",     "Contacto",     "contacto"),
]

# Filename → key activa
PAGE_KEY = {
    "home-v3.html":        "home",
    "factusol-v3.html":    "factusol",
    "consultoria-v3.html": "consultoria",
    "contacto-v3.html":    "contacto",
    "industrias-v3.html":  "industrias",
    "descargas-v3.html":   "descargas",
    "resenas-v3.html":     None,  # /resenas/ no esta en el menu principal, sin active
    "modulo-arca-v3.html": "modulo-arca",
    "power-bi-v3.html":    "power-bi",
}


def build_nav(active_key: str | None) -> str:
    links = []
    for href, text, key in ITEMS:
        cls = ' class="active"' if key == active_key else ''
        links.append(f'            <a href="{href}"{cls}>{text}</a>')
    nav_html = (
        '<nav class="nav">\n'
        '    <div class="nav-inner">\n'
        f'        <a class="nav-brand" href="/"><img src="{LOGO_MAIN}" alt="Goxtech" style="height:30px;width:auto;display:block;" onerror="this.outerHTML=&quot;Goxtech&quot;"></a>\n'
        '        <div class="nav-links">\n'
        + '\n'.join(links) + '\n'
        '        </div>\n'
        '        <a href="https://wa.me/5493541651038?text=Hola!%20Quiero%20información%20sobre%20Goxtech." target="_blank" rel="noopener" class="nav-cta">Hablemos <i data-lucide="arrow-right"></i></a>\n'
        '    </div>\n'
        '</nav>'
    )
    return nav_html


def apply(path: Path):
    src = path.read_text(encoding="utf-8")
    key = PAGE_KEY.get(path.name)
    new_nav = build_nav(key)
    # Reemplazar el primer <nav class="nav">...</nav>
    pat = re.compile(r'<nav class="nav">.*?</nav>', re.DOTALL)
    if not pat.search(src):
        return False
    src2 = pat.sub(lambda _m: new_nav, src, count=1)
    if src2 == src:
        return False
    path.write_text(src2, encoding="utf-8")
    return True


base = Path("web_register")
for name in PAGE_KEY:
    p = base / name
    if not p.exists():
        print(f"SKIP {name}")
        continue
    changed = apply(p)
    print(f"{name}: {'CHANGED' if changed else 'unchanged'}")
