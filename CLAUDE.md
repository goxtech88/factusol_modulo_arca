# CLAUDE.md — Factusol ARCA Sync

Módulo de facturación electrónica ARCA (AFIP) para Factusol. Backend FastAPI
(`app/`) + frontend estático (`app/static/`). Se empaqueta como `ARCA.exe`
(PyInstaller) y se distribuye a clientes con auto-updater.

## Estado actual
- Versión en `main`: **1.7.5** (definida en `app/main.py` → `version=`).
- Últimas features agregadas:
  - **v1.7.4** — botón "Grabar datos en Factusol": re-graba el CAE en `F_FAC`
    cuando se obtuvo en ARCA pero no quedó grabado en Factusol. Endpoint
    `POST /api/arca/write-factusol/{tipfac}/{codfac}`. Helper reutilizable
    `_grabar_cae_en_factusol` en `app/routers/arca_router.py`.
  - **v1.7.5** — botón "Imprimir" en Notas de Crédito: comprobante con info
    fiscal mínima + QR AFIP, listo para PDF. Endpoint
    `GET /api/credit-notes/{nc_id}/comprobante`. `arca_service.generate_afip_qr`
    acepta `filename` (el QR de la NC se guarda como `nc-<pv>-<nro>.png` para
    no pisar el de la factura, que comparte `tipfac/codfac`).

## PENDIENTE — deploy de la v1.7.5
El código está en `main` pero **NO está deployado a los clientes todavía**.
El deploy debe correrse **desde Windows**, NO desde el entorno cloud/Linux
(no hay PyInstaller, ni `venv/` ni `*.spec` —están gitignored—, ni acceso al
jump host `192.168.1.201`, que solo se alcanza por LAN/Tailscale).

Pasos (en la carpeta del repo, en Windows, con LAN o Tailscale activo):
1. `git checkout main && git pull origin main`
2. `build_desktop.bat`  (compila `ARCA.exe` con `venv\` + `arca.spec`)
3. `powershell -Command "Compress-Archive -Path dist\ARCA -DestinationPath dist\ARCA_v1.7.5.zip -Force"`
4. `python deploy_upload.py --dry-run`  (preview, no sube nada)
5. `python deploy_upload.py`  (sube el ZIP + actualiza `arca-latest.json`)

`deploy_upload.py` detecta la versión del CHANGELOG (primer `## vX.Y.Z`), por
eso el ZIP debe llamarse `ARCA_v<version>.zip`. Los clientes actualizan desde
el botón "Verificar última versión" (manifest en
`goxtechlabs.com.ar/downloads/arca-latest.json`).

## Notas de entorno
- El entorno remoto (Claude Code on the web) corre en una **VM Linux aislada en
  la nube**, no en la notebook Windows del usuario. Build y deploy requieren una
  sesión local de Claude Code en Windows.
- GitHub: usar herramientas MCP (`mcp__github__*`); no hay `gh` CLI.
- Rama de desarrollo asignada: `claude/fix-invoice-factusol-save-piPFU`.
