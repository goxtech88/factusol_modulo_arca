# Setup de credenciales — Instagram + Google Drive + n8n

Esta guía deja todo listo para que el workflow de `n8n_workflow.json` corra solo.
Hacelo una vez y olvidate.

> ⏱ Tiempo estimado: 45 minutos la primera vez.

---

## 1. Instagram Business + Página de Facebook

Instagram Graph API **no funciona con cuentas personales**. Necesitás:

### 1.1 — Convertir IG a Business
1. App de Instagram → Configuración → Cuenta → "Cambiar a cuenta profesional"
2. Elegir **Empresa** (no Creador)
3. Categoría: "Servicio empresarial" o "Software"

### 1.2 — Crear Página de Facebook
1. https://www.facebook.com/pages/create
2. Categoría: "Software"
3. Vincularla a tu cuenta personal (es solo administrativa, no se publica nada acá)

### 1.3 — Vincular IG ↔ FB Page
1. Instagram → Configuración → Cuenta → "Compartir en otras apps" → conectar Página FB
2. O desde la Página FB: Configuración → Instagram → Conectar cuenta

---

## 2. App en Meta for Developers

### 2.1 — Crear la app
1. https://developers.facebook.com/apps/ → "Create App"
2. Use case: **"Other"** → siguiente
3. Tipo de app: **"Business"**
4. Nombre: `ARCA Sync Marketing`
5. Email de contacto: el tuyo

### 2.2 — Agregar producto "Instagram Graph API"
1. En el dashboard de la app → "Add Product"
2. Buscar **Instagram Graph API** → "Set up"

### 2.3 — Permisos requeridos
En "App Review" → "Permissions and Features", agregar:
- `instagram_basic`
- `instagram_content_publish`
- `pages_show_list`
- `pages_read_engagement`
- `business_management`

> Para uso propio (no app pública) **no hace falta App Review** si la cuenta IG está en modo "Development" y vos sos admin de la app. Funciona limitado a 25 usuarios test, suficiente.

---

## 3. Generar el Access Token de larga duración

### 3.1 — Token de usuario corto (1 hora)
1. https://developers.facebook.com/tools/explorer/
2. App: seleccionar `ARCA Sync Marketing`
3. User or Page: **"Get User Access Token"**
4. Permisos: marcar los 5 de arriba
5. Click "Generate Access Token" → copiar (válido 1h)

### 3.2 — Convertirlo a long-lived (60 días)
```bash
curl -X GET "https://graph.facebook.com/v21.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id={APP_ID}&\
client_secret={APP_SECRET}&\
fb_exchange_token={SHORT_TOKEN}"
```
Te devuelve `access_token` de 60 días. **Guardalo.**

### 3.3 — Token de Página (este es el que usa el workflow)
```bash
curl -X GET "https://graph.facebook.com/v21.0/me/accounts?access_token={LONG_USER_TOKEN}"
```
Te lista tus páginas FB. Buscá el `access_token` de la página donde está vinculada tu cuenta IG.
**Este token no expira** mientras no cambies tu contraseña ni revoques permisos.

### 3.4 — Obtener el IG User ID
```bash
curl -X GET "https://graph.facebook.com/v21.0/{PAGE_ID}?\
fields=instagram_business_account&\
access_token={PAGE_TOKEN}"
```
Te devuelve `{"instagram_business_account": {"id": "17841401234567890"}}`.
Ese ID es el **IG_USER_ID** que usa el workflow.

---

## 4. Google Drive

### 4.1 — Estructura de la carpeta
Crear en Drive:
```
ARCA_Marketing/                  ← carpeta raíz (esta es la que apunta el workflow)
  carrusel_01_autovalidacion/
    slide_01.jpg
    ...
    slide_10.jpg
    caption.txt
    meta.json
  carrusel_02_multiempresa/
    ...
```

### 4.2 — Compartir la carpeta como "cualquiera con el link"
Esto es **obligatorio** porque Instagram Graph API necesita URLs públicas de las imágenes.

1. Click derecho en `ARCA_Marketing/` → "Compartir"
2. "Acceso general" → cambiar a **"Cualquier persona con el enlace"**
3. Permiso: **Lector** (no editor)

Las imágenes quedan accesibles por `https://drive.google.com/uc?export=view&id={FILE_ID}`.

> ⚠️ Si tu carpeta tiene contenido sensible, mejor usar otro host (S3 público, Cloudinary, Bunny CDN). El workflow soporta cualquiera, solo cambiá el armado de URL en el node "Ordenar slides y armar URLs".

### 4.3 — Credencial OAuth de Drive en n8n
1. n8n → Credentials → "New" → "Google Drive OAuth2 API"
2. Seguir el wizard, conectar con tu cuenta Google
3. Anotar el nombre que le pongas — debe coincidir con el del workflow (`Google Drive ARCA Marketing`)
4. Conceder acceso

### 4.4 — Obtener el ID de la carpeta raíz
Abrir `ARCA_Marketing/` en Drive. La URL es:
```
https://drive.google.com/drive/folders/1abc...XYZ
                                       ↑
                                  Este es el ID
```

---

## 5. Variables de entorno en n8n

En tu instancia de n8n (Settings → Variables, o `.env` si es self-hosted):

| Variable | Valor | De dónde |
|----------|-------|----------|
| `IG_ACCESS_TOKEN` | token de Página de FB | sección 3.3 |
| `IG_USER_ID` | id del IG Business Account | sección 3.4 |
| `DRIVE_PARENT_FOLDER_ID` | id de `ARCA_Marketing/` | sección 4.4 |
| `NOTIF_WEBHOOK_URL` | webhook de Slack/Telegram/Discord (opcional) | la que uses para avisos |

> En n8n cloud: usar el panel **Variables**. En self-hosted: agregar al `.env` y reiniciar.

---

## 6. Importar el workflow

1. n8n → Workflows → "Import from File"
2. Subir `marketing/n8n_workflow.json`
3. Revisar que cada node de Google Drive tenga la credencial correcta seleccionada
4. **Activar** el workflow (toggle arriba a la derecha)

---

## 7. Probar end-to-end

### 7.1 — Generar un carrusel localmente
```bash
cd marketing/
pip install pillow pyyaml
python generador_slides.py --carrusel 1
```
Sale en `marketing/salida/carrusel_01_autovalidacion/`.

### 7.2 — Subir a Drive
Subí esa carpeta completa adentro de `ARCA_Marketing/` en Drive.

### 7.3 — Editar fecha de publicación
Abrir `meta.json` en Drive y dejarlo con:
```json
{
  "status": "pendiente",
  "fecha_publicacion": "2026-05-11"
}
```
(fecha de hoy o anterior → se publica en la próxima ejecución del cron).

### 7.4 — Ejecutar el workflow manualmente
En n8n → workflow → "Execute Workflow".
O hacer POST al webhook:
```bash
curl -X POST https://tu-n8n.com/webhook/publicar-carrusel-arca
```

### 7.5 — Verificar
- En IG: aparece el carrusel publicado
- En Drive: `meta.json` ahora dice `"status": "publicado"` con el `ig_post_id`
- Recibís la notif por Slack/Telegram

---

## 8. Mantenimiento

| Tarea | Cada cuánto | Cómo |
|-------|-------------|------|
| Renovar long-lived user token | 60 días | repetir paso 3.2 (el de Page no expira mientras la cuenta esté activa) |
| Verificar permisos de la app FB | si Meta cambia políticas | dashboard de developers.facebook.com |
| Limpiar carruseles publicados | trimestral | mover de `ARCA_Marketing/` a `ARCA_Marketing_Archivo/` |
| Rotar contenido | mensual | crear nuevos carruseles + plantillas YAML, generar y subir |

---

## 9. Troubleshooting

**"The image format is not supported"**
La URL de Drive devuelve HTML, no JPG. Verificá que la carpeta esté en "Cualquier persona con el enlace". Probá la URL en una ventana incógnito.

**"Subject does not have permission to perform this action"**
El access token no tiene `instagram_content_publish`. Volver a la sección 3.1.

**"Media ID not available"**
Pasaste muy rápido del `media` al `media_publish`. El node de Wait de 30s del workflow ya está para esto — no lo saques.

**El carrusel publicó solo 1 imagen**
Las imágenes individuales tienen que ir con `is_carousel_item=true`. Si las marcaste solas como POST normal, IG las publica como single. Revisar el node "POST container por slide".
