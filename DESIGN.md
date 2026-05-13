# DESIGN.md — Goxtech web v3

## Paleta (CSS custom properties)

```css
:root {
    --primary:        #FF6B00;  /* Naranja Goxtech (CTAs, links activos, icons primarios) */
    --primary-light:  #FF9A44;  /* Hover / gradient stop */
    --primary-dark:   #E55F00;  /* Botones pressed / footer CTA */
    --accent:         #10B981;  /* Verde "disponible" / badges success / dot pulsante hero */
    --warn:           #f59e0b;  /* Naranja-amarillo de warning, ratings ★ */
    --error:          #dc2626;  /* Rojo de error en forms */
    --info:           #3b82f6;  /* Azul info (poco uso) */

    --bg-app:         #F8FAFC;  /* Fondo página */
    --bg-panel:       #FFFFFF;  /* Cards, modals, nav background */
    --bg-soft:        #FFF8F2;  /* Naranja muy diluido para hero gradients y badges */
    --bg-sidebar:     #0B0B0D;  /* Admin sidebar (oscuro) */

    --border:         #E5E7EB;
    --border-strong:  #D1D5DB;

    --text-main:      #0B0B0D;  /* H1-H4 */
    --text-body:      #1F1F23;  /* Párrafos */
    --text-muted:     #6B7280;  /* Eyebrows, captions, footer text */
    --text-sidebar:   #94A3B8;  /* Admin sidebar items */

    --code-bg:        #1F1F23;  /* Code blocks fondo */
    --code-text:      #E5E7EB;  /* Code blocks texto */

    --shadow:         0 10px 40px rgba(0, 0, 0, 0.08);
    --shadow-strong:  0 20px 60px rgba(255, 107, 0, 0.15);
}
```

## Tipografía
- **Plus Jakarta Sans** (Google Fonts) — pesos 300, 400, 500, 600, 700, 800. Default del sitio.
- **JetBrains Mono** (Google Fonts) — pesos 400, 600. Solo para "details técnicos": eyebrows, paths, version numbers, code references, DAX, snippets, contadores numéricos.

Clase utilitaria: `.mono { font-family: "JetBrains Mono", monospace; }`

### Escala
- H1: 48-56px, weight 800, letter-spacing -1px / -1.5px
- H2: 32-36px, weight 800
- H3: 20-24px, weight 700-800
- H4: 16-17px, weight 700
- Body: 14-15px, line-height 1.5-1.6
- Lead/intro: 17-19px
- Eyebrow mono: 11-12px, uppercase, letter-spacing 1-1.5px, color primary
- Small/caption: 11-13px, color muted

## Espaciado y radius
- **Grid principal:** `max-width: 1200px; padding: 0 24px`
- **Section padding vertical:** 60-80px (hero un poco más)
- **Card padding:** 22-32px
- **Gaps grid:** 16-24px (lista de items), 36-60px (grid hero)
- **Radius:**
  - Botones: 8-10px
  - Cards: 12-16px
  - Inputs: 8px
  - Badges/pills: 4-6px
  - Logo/brand: sin radius (rectangular)

## Iconografía
- **Lucide via CDN**: `<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>`
- Uso: `<i data-lucide="icon-name"></i>` + `lucide.createIcons()` después de cualquier `innerHTML` dinámico
- Tamaños por contexto:
  - Default (1em del padre)
  - `.icon`, `.ico`: 22px
  - `.nav-cta`, `.btn-primary`, `.btn-secondary`, `.btn-wa`: 16px, stroke-width 2.5
  - `.wa-float`: 28px
  - `.product-card .link`, `.sector-card .link`: 14px

**Iconos por contexto semántico (mantener consistencia):**
- ARCA / facturación → `shield-check`
- Factusol → `file-spreadsheet`
- Power BI / reportes → `bar-chart-3`
- Tienda Nube → `shopping-bag` / `shopping-cart`
- Stack técnico → `server`, `database`, `terminal`, `cloud`, `monitor`
- Servicios → `target` (ads), `flask-conical` (labs)
- Industrias → `shirt`, `hard-hat`, `truck`, `ship`, `factory`, `home`
- Contacto → `mail`, `map-pin`, `clock`, `message-circle`
- Catálogo → `package`, `download`, `receipt`, `users`, `landmark`

**Excepción:** el logo de WhatsApp se mantiene como SVG inline (marca registrada de Meta), no como Lucide.

## Componentes

### Nav
- Sticky top con `backdrop-filter: blur(12px)` y bg semi-transparente
- Logo izquierda (img del backend, 30px alto)
- 8 items: Inicio · Factusol · Módulo ARCA · Power BI · Consultoría · Industrias · Descargas · Contacto
- CTA "Hablemos →" a la derecha (gradient primary)
- Mobile: `display: none` en links a < 1000px (hamburger no implementado aún)

### Hero
- Padding 80px 0 60px
- Gradient diagonal `linear-gradient(180deg, #FFF8F2 0%, var(--bg-app) 100%)`
- Blob naranja decorativo top-right (`rgba(255,107,0,0.08)` blur 80px)
- Eyebrow mono accent (verde) con dot pulsante optional
- H1 con palabra clave en `.accent` (naranja)
- Lead 17-19px
- 2 CTAs (primary + secondary)

### Cards
- `.product-card`, `.service-card`, `.module-card`, etc.
- `border: 1px solid var(--border)` → en hover cambia a `var(--primary)` + `transform: translateY(-2px o -3px)` + `box-shadow: var(--shadow)`
- Padding 22-32px, radius 12-16px

### Botones
- `.btn-primary`: gradient `135deg, var(--primary), var(--primary-light)`, box-shadow naranja, hover `translateY(-1px)` + box-shadow más intensa
- `.btn-secondary`: bg blanco, border-color en hover pasa a primary
- `.btn-wa`: background `#25D366` (verde WA oficial)
- `.btn-icon`: padding 8px, min-width 32px

### Code blocks
- Background `#1F1F23` (no naranja, contraste sobre fondo claro)
- Padding 24px, radius 12px
- JetBrains Mono 13px
- Highlighting tokens: keyword `#79c0ff`, function `#d2a8ff`, string `#a5d6ff`, number `#f2c811`, comment `#8b94a8 italic`

### Footer
- Border top, padding 40-48px 0, bg `var(--bg-panel)`
- Estructura grid 4 columnas (brand+contacto, productos, servicios, empresa)
- En home muestra logo grande (dark version)

### CTA final por página
- Background gradient naranja `135deg, var(--primary), var(--primary-dark)`
- Radius 16px, padding 48px 32px
- Texto blanco
- 1-2 botones (uno WhatsApp principal, otro email/secundario)

## Animaciones
- Transiciones cortas: 0.1s (transform), 0.15s (color, border, shadow)
- Hover de cards: `translateY(-2px)` o `-3px`
- WhatsApp float: `transform: scale(1.05)` en hover
- Dot pulsante hero: `@keyframes pulse` opacity 1 → 0.4 → 1, 2s infinite
- Sin animaciones de entrada (fade-up etc.) en v3 — minimalismo

## Responsive
- Breakpoints:
  - 1000px: oculta nav-links (mobile menu pendiente)
  - 960px / 900px: grids 2-3 columnas → 1
  - 800px: cards two-col → 1
  - 700px: hero H1 baja a 38px
  - 600px: oculta nav-cta
  - 540px / 500px: process / sector grids → 1 columna

## Backend y assets
- Logos servidos desde el backend en URL absoluta con timestamp (cache busting natural):
  - `https://goxtech.com.ar/arca_factusol/api/uploads/site/logo_main-1778620488.png`
  - `https://goxtech.com.ar/arca_factusol/api/uploads/site/logo_dark-1778620494.png`
  - `https://goxtech.com.ar/arca_factusol/api/uploads/site/favicon-1778620503.png`
- HTML inicial los embebe directo (sin flicker). El loader `/site/config` los actualiza si el admin sube un logo nuevo.
- `<img>` tiene `onerror="this.outerHTML='Goxtech'"` como fallback texto.

## Accesibilidad
- `aria-label` en botones de iconos puros (WA float, modal close)
- Form inputs con `<label>` explícito
- Color contraste (a verificar): naranja `#FF6B00` sobre blanco — pasa WCAG AA para texto grande/UI, no para body text 14px.

## Anti-patterns a evitar
- Texto en gris claro sobre fondo claro (< 4.5:1 contraste)
- Botones sin altura mínima 44px en mobile (touch target)
- Líneas de texto > 75 caracteres
- Iconos sin etiqueta semántica para screen readers
- CSS inline color-hardcoded en lugar de variables
- Imágenes sin `alt` o con `alt=""` cuando son significativas
- Stack photos / emojis decorativos sin propósito
- Animaciones que parpadean (epilepsia)
- Cualquier elemento que no respete la paleta `#FF6B00` / `#10B981` / `#0B0B0D`
