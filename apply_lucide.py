"""
Aplica Lucide icons a las paginas v3.

Cambios:
1. Inserta <script> de Lucide CDN despues de los Google Fonts
2. Inserta CSS base [data-lucide] despues del reset * {}
3. Reemplaza emojis comunes por <i data-lucide="...">
4. Reemplaza SVGs inline conocidos (por path d) por <i data-lucide="...">
5. Inserta renderIcons() al final del JS

Se ejecuta sobre TODAS las paginas v3 menos home-v3 (ya hecho a mano).
"""
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

# Emoji -> Lucide icon name
EMOJI_MAP = {
    "👕": "shirt",
    "🏗": "hard-hat",
    "📦": "truck",
    "🚢": "ship",
    "🏭": "factory",
    "🏠": "home",
    "📧": "mail",
    "📍": "map-pin",
    "⏱": "clock",
    "📊": "file-spreadsheet",
    "📈": "bar-chart-3",
    "📉": "trending-down",
    "🛒": "shopping-cart",
    "📋": "clipboard-list",
    "🐍": "terminal",
    "🐬": "database",
    "🐘": "database",
    "🪟": "monitor",
    "☁": "cloud",
    "☁️": "cloud",
    "🗄": "archive",
    "🇦🇷": "landmark",
    "💰": "wallet",
}

# Map SVG paths (d attr) to lucide names. Solo los muy comunes.
SVG_D_MAP = {
    # arrow right (CTA)
    "M17 8l4 4m0 0l-4 4m4-4H3": "arrow-right",
    # external link
    "M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14": "external-link",
}


def lucide_css_block():
    return """/* Lucide base — los SVG generados heredan width/height del contenedor */
[data-lucide] { width: 1em; height: 1em; stroke-width: 2; vertical-align: middle; flex-shrink: 0; }
.icon [data-lucide], .ico [data-lucide] { width: 22px; height: 22px; }
.nav-cta [data-lucide], .btn-primary [data-lucide], .btn-secondary [data-lucide], .btn-wa [data-lucide] { width: 16px; height: 16px; stroke-width: 2.5; }
.wa-float [data-lucide] { width: 28px; height: 28px; }
.link [data-lucide], .arrow [data-lucide] { width: 14px; height: 14px; }
.channel-card .icon [data-lucide] { width: 24px; height: 24px; }
.product-card .link [data-lucide], .sector-card .link [data-lucide] { width: 14px; height: 14px; }"""


def apply(file_path: Path):
    src = file_path.read_text(encoding="utf-8")
    original_len = len(src)

    # 1. Lucide CDN script — agregar despues de Google Fonts si no esta
    if "lucide@latest" not in src:
        cdn = '\n<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>'
        src = re.sub(
            r'(<link href="https://fonts\.googleapis\.com[^>]+>)',
            r'\1' + cdn,
            src, count=1,
        )

    # 2. CSS [data-lucide] — insertar despues del primer "* { ... }"
    if "[data-lucide]" not in src:
        reset_pat = re.compile(r"(\* \{ box-sizing: border-box; margin: 0; padding: 0; \})")
        if reset_pat.search(src):
            src = reset_pat.sub(lambda m: m.group(1) + "\n" + lucide_css_block(), src, count=1)

    # 3. Emoji -> Lucide
    for em, name in EMOJI_MAP.items():
        # Solo dentro de elementos con class "ico" o "icon" (no en cualquier lugar)
        # Patron: class="ico">EMOJI</  o  class="icon">EMOJI</
        for cls in ["ico", "icon"]:
            pattern = re.compile(rf'(class="{cls}"[^>]*>)\s*{re.escape(em)}\s*(</)')
            src = pattern.sub(rf'\1<i data-lucide="{name}"></i>\2', src)

    # 4. SVGs comunes: arrow-right
    # Patron: <svg ...><path ... d="..."></path></svg>
    for d_attr, lucide_name in SVG_D_MAP.items():
        pattern = re.compile(
            r'<svg\b[^>]*>\s*<path\b[^>]*d="' + re.escape(d_attr) + r'"[^>]*/?>(?:</path>)?\s*</svg>',
            re.DOTALL,
        )
        src = pattern.sub(f'<i data-lucide="{lucide_name}"></i>', src)

    # 5. renderIcons() en el JS final (si no esta ya)
    if "renderIcons" not in src and "lucide.createIcons" not in src:
        # Buscar el ultimo </script> antes de </body>
        # Y agregar antes del cierre
        script_pat = re.compile(r"(</script>\s*</body>)", re.DOTALL)
        if script_pat.search(src):
            inject = '\n\n<script>\nif (typeof lucide !== "undefined") lucide.createIcons();\n</script>\n'
            src = src.replace("</body>", inject + "</body>", 1)
        else:
            # No hay <script> al final — agregamos uno antes de </body>
            inject = '\n<script>\nif (typeof lucide !== "undefined") lucide.createIcons();\n</script>\n'
            src = src.replace("</body>", inject + "</body>", 1)

    file_path.write_text(src, encoding="utf-8")
    return original_len, len(src)


base = Path(__file__).parent / "web_register"
for name in PAGES:
    p = base / name
    if not p.exists():
        print(f"SKIP {name} (no existe)")
        continue
    before, after = apply(p)
    print(f"{name}: {before:,} -> {after:,} bytes (diff {after-before:+,})")

print("\nListo.")
