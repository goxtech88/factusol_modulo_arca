"""
Aplica fixes de logos a las 9 paginas v3:
1. Reemplaza favicon roto (/img/logo-dark.png) por data: SVG inline naranja G
2. Agrega loader de /site/config que pisa el favicon y el nav-brand con
   los logos dinamicos del backend (si existen).
"""
import re
from pathlib import Path

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

FAVICON_OLD = '<link rel="icon" type="image/png" href="/img/logo-dark.png">'
FAVICON_NEW = '<link rel="icon" type="image/png" id="favicon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'%3E%3Crect width=\'100\' height=\'100\' rx=\'20\' fill=\'%23FF6B00\'/%3E%3Ctext x=\'50\' y=\'66\' text-anchor=\'middle\' font-size=\'52\' font-weight=\'800\' fill=\'white\' font-family=\'sans-serif\'%3EG%3C/text%3E%3C/svg%3E">'

LOGO_LOADER = """
<script>
(function() {
    var API_BASE = "https://goxtech.com.ar/arca_factusol/api";
    function assetUrl(p) {
        if (!p) return "";
        if (p.indexOf("http") === 0) return p;
        if (p.indexOf("/arca_factusol/") === 0) return "https://goxtech.com.ar" + p;
        return API_BASE + p;
    }
    fetch(API_BASE + "/site/config").then(function(r) { return r.json(); }).then(function(cfg) {
        if (cfg.favicon_url) {
            var ico = document.getElementById("favicon");
            if (ico) ico.href = assetUrl(cfg.favicon_url);
        }
        if (cfg.logo_url || cfg.logo_dark_url) {
            var url = assetUrl(cfg.logo_url || cfg.logo_dark_url);
            document.querySelectorAll(".nav-brand").forEach(function(el) {
                el.innerHTML = '<img src="' + url + '" alt="Goxtech" style="height:28px;width:auto;vertical-align:middle;">';
            });
            // footer brand tambien
            document.querySelectorAll(".footer .brand").forEach(function(el) {
                if (el.tagName === "SPAN" || el.tagName === "DIV") {
                    el.innerHTML = '<img src="' + url + '" alt="Goxtech" style="height:32px;width:auto;">';
                }
            });
        }
    }).catch(function() { /* silent */ });
})();
</script>
"""


def apply(file_path: Path):
    src = file_path.read_text(encoding="utf-8")
    original_len = len(src)
    changed = False

    # 1. Reemplazar favicon roto
    if FAVICON_OLD in src:
        src = src.replace(FAVICON_OLD, FAVICON_NEW, 1)
        changed = True
    elif 'id="favicon"' not in src:
        # Buscar cualquier <link rel="icon" ...> y reemplazarlo
        pat = re.compile(r'<link rel="icon"[^>]*>')
        if pat.search(src):
            src = pat.sub(FAVICON_NEW, src, count=1)
            changed = True

    # 2. Inyectar loader de logo antes de </body> si no esta
    if "loadSiteConfig" not in src and "site/config" not in src.split("</style>")[0]:
        # Solo inyectar si no hay ya un loader de site/config en el head
        # Insertar antes de </body>
        if "</body>" in src and LOGO_LOADER.strip() not in src:
            src = src.replace("</body>", LOGO_LOADER + "</body>", 1)
            changed = True

    if changed:
        file_path.write_text(src, encoding="utf-8")
    return original_len, len(src), changed


base = Path(__file__).parent / "web_register"
for name in PAGES:
    p = base / name
    if not p.exists():
        print(f"SKIP {name}")
        continue
    before, after, ch = apply(p)
    status = "CHANGED" if ch else "skip"
    print(f"{name}: {before:,} -> {after:,} bytes [{status}]")
