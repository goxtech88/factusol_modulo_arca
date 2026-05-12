# Changelog - Factusol ARCA Sync

## v1.6.5 (2026-05-12)

### RG 1361 - Archivo VENTAS
- **Tercer archivo agregado al exportador RG 1361: `VENTAS_AAAAMM.txt`** (Libro IVA Ventas electronico segun Anexo II RG 1361). Algunos validadores tributarios y portales de proveedores (ej PAMI ACE) lo requieren ademas de CABECERA y DETALLE.
  - 30 campos / 308 chars por registro tipo 1 (1 linea por comprobante con alicuota IVA principal).
  - Registro tipo 2 con resumen del periodo y totales.
  - El ZIP que descarga el boton "Exportar RG 1361" ahora incluye los 3 archivos.

### UX - Filtros y busqueda
- **Nuevo filtro ESTA SEMANA en Facturas** (lunes a domingo de la semana actual).
- **Default de Facturas cambiado a HOY** (antes mostraba todas las facturas — al abrir cargaba muchos datos y se sentia lento).
- **Boton TODO removido de Facturas**: cargar el historico entero contra la base de Factusol (MS Access) congelaba la UI. La facturacion se usa como maximo durante la semana, asi que dejamos hasta "ESTE AÑO" como maximo.
- **Filtros rapidos por fecha en CAE Emitidos**: HOY / ESTA SEMANA / ESTE MES / MES PASADO / ESTE AÑO / TODO (antes solo habia un dropdown por mes especifico). Default arranca en HOY. Se mantiene "TODO" en esta vista porque los CAE estan en SQLite local y son rapidos de listar.
- **Buscador en CAE Emitidos**: por numero de factura (`tipfac-codfac`), nro de comprobante AFIP, CAE, nombre del cliente o CUIT/DNI. Filtra en vivo mientras tipeas.

### Backend
- `factusol_service.get_invoices()` ahora acepta `date_filter=this_week` (rango lunes-domingo de la semana actual).

---

## v1.6.4 (2026-05-12)

### CRITICO - Bug fix de actualizacion
- **Fix: la DB del usuario se pisaba al actualizar.** En versiones <= 1.6.3 la lista de archivos preservados del updater tenia el nombre incorrecto de la DB (`arca.db` en vez del nombre real `app_data.db`). Al actualizar, la DB con usuarios y CAE historicos NO se preservaba — si una version traia un `app_data.db` o si el usuario re-extraia el ZIP encima, perdia todo.
- **Backup ZIP completo pre-update**: antes de aplicar cualquier actualizacion ahora se crea `backups/backup_pre-vX.Y.Z_YYYYMMDD_HHMMSS.zip` con config.json + DB + certs + licencia. Si algo sale mal, restauras desde ahi.
- **`copy` reemplaza `move`**: el preserve ahora usa COPY (no move) — el original queda en su lugar como red de seguridad mientras se hace el update.
- **`xcopy /e /i /h /y` para directorios**: `move` no maneja directorios con handles abiertos; xcopy es robusto.
- **Logging detallado del update** a `update_YYYYMMDD_HHMMSS.log` en el dir de la app — permite diagnosticar si algo falla.
- **Pausa extra de 2s** tras detectar que ARCA.exe se cerro, para que SQLite y otros liberen handles del filesystem.
- **`.arca_browser/` preservado** tambien (user-data-dir de Chrome/Edge embedded) — evita re-loguear despues de cada update.

### Que pasa si ya perdiste config al actualizar a una version anterior
- Esta version NO recupera lo perdido (los datos viejos ya no estan).
- A partir de v1.6.4 cada update genera un backup, asi que de aca en adelante esta cubierto.

---

## v1.6.3 (2026-05-12)

### UX
- **Boton "Actualizar"** en CAE Emitidos: refresca la lista desde el server sin reabrir la app. Util cuando el WebView cachea contenido viejo.
- **Boton "Diagnostico"** en CAE Emitidos: muestra al instante cuantos CAE hay en la DB, el rol/id del user actual y los ultimos 5 CAE. Permite distinguir entre tabla vacia, problema de permisos o cache.
- El `load()` ahora muestra un toast con la cantidad de comprobantes cargados (warning si esta vacio).

### Backend
- Nuevo endpoint `GET /api/arca/diagnostic` que devuelve user actual + estadisticas de la tabla `cae_logs` + ultimos 5 registros + version + path de la DB.

---

## v1.6.2 (2026-05-11)

### Nuevas funcionalidades
- **Auto-ajuste de fecha del comprobante (AFIP RG 4291)**: Si la fecha de la factura en Factusol esta fuera del rango aceptado por AFIP (+/- 5 dias para productos, +/- 10 para servicios), la app la ajusta automaticamente al limite valido mas cercano (hoy-5 o hoy+5) en vez de devolver el error tecnico 10016. Tambien actualiza `F_FAC.FECFAC` en Factusol para que la fecha del CAE quede sincronizada con la de la factura.
  - Aplica a validacion manual, validacion en lote y auto-validador.
  - La respuesta del endpoint incluye `fecha_ajustada: true` y un mensaje informativo cuando se hizo el ajuste.
  - Si el `UPDATE` en Factusol falla, sigue de todos modos con la fecha ajustada (sin romper el flujo).

### UX
- **Mensajes de error multilinea**: Los toasts ahora respetan saltos de linea y se autoajustan en duracion segun el largo del mensaje. Antes los errores estructurados aparecian como "[object Object]".
- API client extrae automaticamente `message` / `error` de respuestas FastAPI con `detail` estructurado.

---

## v1.6.1 (2026-05-06)

### Nuevas funcionalidades
- **Exportador RG 1361 (Duplicado Electronico)**: Genera CABECERA_AAAAMM.txt y DETALLE_AAAAMM.txt en el formato exacto del Anexo II de la RG (AFIP) 1361/2002, listos para subir a sistemas de validacion tributaria.
  - Boton "Exportar RG 1361" en seccion CAE Emitidos. Toma el periodo del filtro de mes activo (o el mes en curso).
  - Registros tipo 1 + tipo 2 (resumen) en CABECERA, ASCII, padding numerico con ceros, alfanumerico con blancos a derecha, fin de registro CRLF (0D0A).
  - Mapeo automatico de codigos: tipo de responsable (Tabla E.4), alicuota IVA (Tabla E.6), documento (Tabla E.7).
  - Endpoint: `GET /api/arca/rg1361/export?year=YYYY&month=MM[&pv=NNNN]` -> ZIP con ambos archivos.

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
