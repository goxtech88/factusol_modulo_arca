"""
Inyecta el logo HARDCODED en el HTML inicial (sin flicker).
- nav-brand: pasa de texto "Goxtech" a <img src="logo_main_url">
- footer .brand: idem
- favicon: pasa del data-URI fallback al PNG real del backend

El loader fetch ya inyectado en apply_logos.py se queda como auto-update
para cuando el admin cambia el logo.

URLs hardcoded (cache-busted con timestamp en el filename):
    logo_main:   .../uploads/site/logo_main-1778620488.png
    logo_dark:   .../uploads/site/logo_dark-1778620494.png
    favicon:     .../uploads/site/favicon-1778620503.png
"""
import re
from pathlib import Path

LOGO_MAIN = "https://goxtech.com.ar/arca_factusol/api/uploads/site/logo_main-1778620488.png"
LOGO_DARK = "https://goxtech.com.ar/arca_factusol/api/uploads/site/logo_dark-1778620494.png"
FAVICON = "https://goxtech.com.ar/arca_factusol/api/uploads/site/favicon-1778620503.png"

PAGES = [
    "home-v3.html",
    "factusol-v3.html",
    "consultoria-v3.html",
    "contacto-v3.html",
    "industrias-v3.html",
    "descargas-v3.html",
    "resenas-v3.html",
    "modulo-arca-v3.html",
    "power-bi-v3.html",
]


def apply_page(file_path: Path):
    src = file_path.read_text(encoding="utf-8")
    changed = False

    # 1. Favicon hardcoded (reemplazar el data-URI)
    pat_favicon = re.compile(
        r'<link rel="icon"[^>]*id="favicon"[^>]*href="[^"]+"[^>]*>'
    )
    new_favicon = f'<link rel="icon" type="image/png" id="favicon" href="{FAVICON}">'
    if pat_favicon.search(src):
        src = pat_favicon.sub(new_favicon, src, count=1)
        changed = True

    # 2. nav-brand: <a class="nav-brand" href="/">Goxtech</a>  →  con <img>
    # Match flexible para distintas variaciones que pueden haber con o sin atributos extra
    pat_brand = re.compile(
        r'(<a class="nav-brand"[^>]*?href="/"[^>]*?>)\s*Goxtech\s*(</a>)'
    )
    new_brand = (
        r'\1<img src="' + LOGO_MAIN + r'" alt="Goxtech" '
        r'style="height:30px;width:auto;display:block;" '
        r'onerror="this.outerHTML=&quot;Goxtech&quot;">\2'
    )
    if pat_brand.search(src):
        src = pat_brand.sub(new_brand, src)
        changed = True

    # 3. Footer brand (en home-v3 hay un .brand grande)
    # <div class="brand">Goxtech</div>
    pat_footer_brand = re.compile(
        r'(<div class="brand">)Goxtech(</div>)'
    )
    new_footer_brand = (
        r'\1<img src="' + LOGO_DARK + r'" alt="Goxtech" '
        r'style="height:36px;width:auto;display:block;" '
        r'onerror="this.outerHTML=&quot;Goxtech&quot;">\2'
    )
    if pat_footer_brand.search(src):
        src = pat_footer_brand.sub(new_footer_brand, src)
        changed = True

    if changed:
        file_path.write_text(src, encoding="utf-8")
    return changed


base = Path(__file__).parent / "web_register"
for name in PAGES:
    p = base / name
    if not p.exists():
        print(f"SKIP {name}")
        continue
    ch = apply_page(p)
    print(f"{name}: {'CHANGED' if ch else 'no change'}")

# Admin v3 (estructura un poco distinta)
admin_path = base / "admin-v3.html"
if admin_path.exists():
    src = admin_path.read_text(encoding="utf-8")
    changed = False

    # Favicon
    pat_fav = re.compile(r'<link rel="icon"[^>]*id="favicon"[^>]*href="[^"]+"[^>]*>')
    new_fav = f'<link rel="icon" type="image/png" id="favicon" href="{FAVICON}">'
    if pat_fav.search(src):
        src = pat_fav.sub(new_fav, src, count=1)
        changed = True

    # Sidebar logo del admin: <div id="sidebar-logo"><span class="brand">Goxtech</span></div>
    pat_sb = re.compile(
        r'<div id="sidebar-logo"><span class="brand">Goxtech</span></div>'
    )
    new_sb = (
        f'<div id="sidebar-logo">'
        f'<img src="{LOGO_DARK}" alt="Goxtech" '
        f'style="height:30px;width:auto;display:block;filter:brightness(1.2);" '
        f'onerror="this.outerHTML=&quot;&lt;span class=\\&quot;brand\\&quot;&gt;Goxtech&lt;/span&gt;&quot;">'
        f'</div>'
    )
    if pat_sb.search(src):
        src = pat_sb.sub(new_sb, src, count=1)
        changed = True

    # Login screen brand: <span class="brand">Goxtech</span>
    pat_login = re.compile(
        r'<div class="logo-row">\s*<span class="brand">Goxtech</span>'
    )
    new_login = (
        f'<div class="logo-row">'
        f'<img src="{LOGO_MAIN}" alt="Goxtech" '
        f'style="height:36px;width:auto;display:block;" '
        f'onerror="this.outerHTML=&quot;&lt;span class=\\&quot;brand\\&quot;&gt;Goxtech&lt;/span&gt;&quot;">'
    )
    if pat_login.search(src):
        src = pat_login.sub(new_login, src, count=1)
        changed = True

    if changed:
        admin_path.write_text(src, encoding="utf-8")
    print(f"admin-v3.html: {'CHANGED' if changed else 'no change'}")
