# Marketing — Carruseles ARCA Sync para Instagram

Sistema para crear y publicar carruseles de Instagram que venden el módulo
ARCA Sync, usando **Pillow** (generación local), **Google Drive** (storage) y
**n8n** (publicación automática).

**Importante:** esto no toca el código de la app ARCA. Es contenido + workflow,
vive en `marketing/` aislado del módulo de facturación.

---

## 📁 Estructura

```
marketing/
├── README.md                  ← este archivo
├── carruseles.md              ← guiones de los 8 carruseles (slide a slide)
├── setup_credenciales.md      ← cómo conectar IG + Drive + n8n
├── n8n_workflow.json          ← workflow importable en n8n
├── generador_slides.py        ← script Pillow que genera los .jpg
├── plantillas/                ← YAML/JSON por carrusel (textos editables)
│   └── carrusel_01.yaml
├── assets/                    ← logo, QR de WhatsApp, fuentes (opcional)
└── salida/                    ← .jpg generados (ignorado en git)
```

---

## 🚀 Flujo completo

```
┌────────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ 1. Editás un YAML  │ →  │ 2. Pillow genera │ →  │ 3. Subís a Drive │
│ en plantillas/     │    │   slides .jpg    │    │   ARCA_Marketing/│
└────────────────────┘    └──────────────────┘    └────────┬─────────┘
                                                            │
                                                            ▼
                                                  ┌─────────────────┐
                                                  │ 4. n8n cron     │
                                                  │ (Lun-Mie-Vie    │
                                                  │  10:00) detecta │
                                                  │ meta.json       │
                                                  │ pendiente       │
                                                  └────────┬────────┘
                                                            │
                                                            ▼
                                                  ┌─────────────────┐
                                                  │ 5. n8n publica  │
                                                  │ vía Graph API   │
                                                  │ y marca         │
                                                  │ "publicado"     │
                                                  └─────────────────┘
```

---

## 🏁 Quick start

### Pre-requisitos
- Python 3.10+
- Cuenta IG **Business** + Página FB vinculada
- Google Drive con una carpeta `ARCA_Marketing/` compartida públicamente
- Instancia de n8n (cloud o self-hosted)

### Setup (una sola vez)
1. Leer **`setup_credenciales.md`** y seguir paso a paso.
2. Instalar dependencias locales:
   ```bash
   pip install pillow pyyaml
   ```
3. (Opcional) Colocar `assets/qr_whatsapp.png` y el logo de GoxTech en `assets/`.

### Crear un carrusel nuevo
1. Mirar **`carruseles.md`** y elegir cuál (o inventar uno propio).
2. Crear `plantillas/carrusel_NN.yaml` con la estructura del ejemplo
   (`carrusel_01.yaml` sirve de molde).
3. Generar las imágenes:
   ```bash
   python generador_slides.py --carrusel 2
   ```
   Sale todo en `salida/carrusel_02_<slug>/`.
4. Revisar las imágenes en `salida/`. Si algún slide quedó mal, ajustar el YAML
   y volver a generar.
5. Subir la carpeta completa a `ARCA_Marketing/` en Drive.
6. Listo: el cron de n8n lo agarra el próximo Lun/Mié/Vie a las 10:00 (o
   ejecutar el webhook a mano).

### Generar los 8 de una
```bash
python generador_slides.py --todos
```
(necesita los 8 YAML en `plantillas/`)

---

## 🎨 Personalizar el estilo de los slides

Todo está en `generador_slides.py`, sección "Configuración visual":

```python
COLOR_PRIMARIO = "#0D47A1"   # azul GoxTech
COLOR_ACENTO = "#FFC107"     # amarillo
COLOR_FONDO = "#FFFFFF"
```

Tipos de slide soportados (en el YAML):
- `hook` — pantalla azul de portada con título grande
- `contenido` — fondo blanco con bullets
- `numero` — número/dato gigante centrado (para slides de impacto)
- `cta` — call-to-action con QR opcional

Si necesitás otros layouts, agregalos como funciones nuevas en `generador_slides.py`
y referencialos con un `tipo:` nuevo en el YAML.

---

## 📅 Calendario sugerido

Definido al final de `carruseles.md`. Resumen:

- **Sem 1:** Carruseles 1, 3, 5 (hook, productividad, contador)
- **Sem 2:** Carruseles 4, 7, 2 (dashboard, errores ARCA, multi-empresa)
- **Sem 3:** Carruseles 6, 8 + repost (seguridad, caso real)

Después del primer mes, mirar métricas (saves > likes) y duplicar los 2 más
guardados con variantes.

---

## ❓ FAQ

**¿Por qué no usar Canva?**
Podés. Pero el flujo automatizado requiere consistencia visual y bulk. Canva sirve
para 1-2 carruseles puntuales. Pillow + YAML es para hacer 40 carruseles este año
sin esfuerzo.

**¿Por qué Drive y no S3?**
Drive es gratis hasta 15 GB y el cliente lo puede ver/editar visualmente. Para
escalar a +200 carruseles conviene migrar a S3 o Cloudinary.

**¿Por qué n8n y no Zapier/Make?**
Self-hosteable, sin costo por ejecución, y la lógica de "esperar 30s entre
container y publish" es trivial. En Zapier sale caro y en Make tiene timeouts.

**¿Cuánto tarda en publicar?**
~45-60 segundos por carrusel (10 slides). El cuello de botella es Instagram, no
n8n.

**¿Funciona con Reels o solo carruseles?**
Solo carruseles (image carousel). Para Reels el flow es distinto (video URL +
`media_type=REELS`).
