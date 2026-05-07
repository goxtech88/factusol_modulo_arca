# Changelog - Factusol ARCA Sync

## v1.6.0 (2026-04-22)

### Nuevas funcionalidades
- **Gestor de actualizaciones**: Boton "Verificar ultima version" en Configuracion que consulta el manifest en goxtechlabs.com.ar. Si hay nueva version, muestra changelog y boton "Actualizar ahora" que descarga, extrae y reemplaza los archivos automaticamente, preservando config.json, arca.db, certificados y licencia. La app se cierra y reinicia sola.
- Nuevo router `/api/updates/` (check, apply).
- Manifest de versiones en `https://goxtechlabs.com.ar/downloads/arca-latest.json`.

## v1.5.1 (2026-04-22)

### Correcciones
- **Padron desactivado**: Removido el auto-enriquecimiento de clientes desde padron ARCA (generaba errores al no ser datos oficiales). El CFECLI debe configurarse manualmente en Factusol.
- **NC solo con CAE**: El boton NC ahora solo aparece en facturas que tienen CAE validado. Facturas sin CAE no muestran el boton.
- **NC ya emitida**: Si una factura ya tiene NC emitida, se muestra badge "NC" en la tabla en vez del boton. No permite emitir NC duplicada.
- **Re-validacion bloqueada**: Una factura que ya tiene NC emitida no se puede volver a validar en ARCA (error 400 en backend + bloqueo en frontend).
- **Status endpoint mejorado**: `/api/arca/status/{tipfac}/{codfac}` ahora distingue entre factura original y NC, devolviendo `has_nc` y `nc_cae`.

## v1.5.0 (2026-04-15)

### Nuevas funcionalidades
- **Modulo Notas de Credito**: Nueva seccion dedicada "Notas de Credito" en el sidebar. Permite listar, filtrar (por fecha y cliente) y emitir NC asociadas a facturas originales ya validadas.
- Soporte para **NC parcial**: se puede indicar un importe menor al de la factura original y los montos (neto, IVA, total) se recalculan proporcionalmente manteniendo la misma alicuota.
- Nuevo endpoint REST `/api/credit-notes/` (listar, buscar factura original, emitir).
- Campos nuevos en `cae_logs`: `motivo`, `cmp_asoc_tipo`, `cmp_asoc_pv`, `cmp_asoc_nro` (auto-migracion al iniciar).
- **Modulo Compras (placeholder)**: seccion preliminar "Compras" en el sidebar, anticipa la gestion futura de comprobantes de compras y credito fiscal.
- **Boton flotante de soporte WhatsApp**: FAB visible solo para clientes con plan pago, abre un chat prellenado con datos de usuario/empresa hacia el numero de soporte de GoxTech.

### Cambios en el modelo de licenciamiento
- El **Plan Basico** ahora incluye **todas las funcionalidades** (gestion multi-usuario, auto-validacion, multi punto de venta, NC). La unica diferencia con los planes pagos es la ausencia de soporte tecnico.
- Los planes pagos se diferencian por incluir **soporte por WhatsApp** con GoxTech (modalidad Mensual o Vitalicia).
- Removidas las restricciones por `has_completa()` en: creacion de PV, gestion de usuarios, auto-validacion.

### Cambios tecnicos
- `arca_service.validate_credit_note` acepta nuevo parametro `importe_override: float | None` que reescala proporcionalmente los importes y alicuotas de IVA.
- Nuevo router `app/routers/credit_notes_router.py`.
- Auto-migracion SQLite simple basada en `PRAGMA table_info` + `ALTER TABLE ADD COLUMN` en `app/database.py`.
- Nuevo componente frontend `app/static/js/components/credit_notes.js`.
- Version bump a 1.5.0.

## v1.4.1 (2026-04-15)

### Nuevas funcionalidades
- **RG 5022/21 (AFIP)**: Factura A a Monotributistas. Por default, los RI ahora emiten Factura A a clientes CFECLI=3 (Monotributo), cumpliendo con la RG 5022/21 y RG 5003.
- **Tilde de configuracion** en Ajustes > Empresa: "Emitir Factura A a Monotributistas (RG 5022/21)". Activado por default. Si se desactiva, se sigue emitiendo Factura B a Monotributo (comportamiento legacy).
- Nota en la UI recordando configurar en Factusol la leyenda obligatoria: *"Receptor del comprobante - Responsable Monotributo"*.

### Cambios tecnicos
- `determine_tipo_comprobante()` ahora acepta parametro `mono_como_a: bool` (default True).
- Nuevo campo en config: `empresa.facturar_mono_como_a` (bool, default True).
- Actualizados call sites en `auto_validate.py` y `arca_router.py` para leer el flag.

## v1.4.0 (2026-04-13)

### Nuevas funcionalidades
- **Nota de Credito AFIP**: Posibilidad de emitir NC (A/B/C) desde la UI para anular facturas ya validadas. La NC referencia al comprobante original via `AgregarCmpAsoc` de WSFEv1.
- Boton "NC" en tabla de facturas y "Emitir Nota de Credito" en modal de detalle.
- Validacion: no permite emitir NC duplicada para la misma factura.

### Correcciones
- **Consumidor Final**: Facturas sin NIF ahora se emiten correctamente como Factura B con `doc_tipo=99` (sin identificar).
- **DNI vs CUIT**: Se distingue correctamente DNI (< 11 digitos, `doc_tipo=96`) de CUIT (11 digitos, `doc_tipo=80`).
- **CFECLI=0**: Ahora se trata como Consumidor Final (Factura B), no como Responsable Inscripto (Factura A).
- **Auto-validacion**: Corregido `determine_tipo_comprobante` en `auto_validate.py` para que tambien reciba `nifcli` y detecte consumidor final.
- **Dependencia `past`**: Agregado modulo `future` (python-future) como dependencia de pyafipws.

### Logica de tipo de comprobante

| NIF | doc_tipo | Factura |
|-----|----------|---------|
| Vacio | 99 (sin identificar) | B - Consumidor final (tope AFIP vigente) |
| DNI (< 11 dig) | 96 (DNI) | B - Consumidor final con DNI |
| CUIT (11 dig) + CFECLI=0 | 80 (CUIT) | B - Consumidor final |
| CUIT (11 dig) + CFECLI=2 | 80 (CUIT) | A - Responsable Inscripto |
| CUIT (11 dig) + CFECLI=3 | 80 (CUIT) | B - Monotributista |
| CUIT (11 dig) + CFECLI=4 | 80 (CUIT) | B - Exento |

---

## v1.3.1

- Auto-validacion por usuario con flag `auto_validate_enabled`
- Launcher robusto para produccion (Chrome/Edge app mode)
- Filtro por forma de pago en auto-validacion

## v1.3.0

- Sistema de licencias por CUIT
- Nuevo icono con transparencia

## v1.2.0

- Multi-instancia (DATA_DIR=CWD)
- Launcher desktop PyWebView
- Spec PyInstaller

## v1.1.0

- Seccion Clientes con padron ARCA
- CAE Emitidos con filtro mes, totales PV y posicion IVA
- BIBFAC, AATFAC, REAFAC (barcode AFIP)
