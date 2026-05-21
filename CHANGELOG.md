# Changelog - Factusol ARCA Sync

## v1.7.5 (2026-05-21)

### Nueva funcionalidad - Imprimir / PDF de Notas de Credito
- **Problema**: las NC emitidas no se podian imprimir. Al emitirlas se obtenia el CAE pero no se generaba el QR ni habia forma de imprimir el comprobante desde la app.
- **Boton "Imprimir"** en la lista de Notas de Credito: abre el comprobante con la **informacion fiscal minima** listo para imprimir o guardar como PDF (el navegador permite "Guardar como PDF").
  - Incluye: emisor (razon social, CUIT, domicilio, condicion IVA), letra y codigo AFIP del comprobante, Nro (PV-numero), fecha, datos del receptor (nombre, CUIT/DNI, condicion IVA, domicilio), comprobante asociado (factura origen), motivo, importes (neto/IVA/total), CAE + vencimiento y **QR AFIP**.
- **QR de la NC**: se genera con nombre propio (`nc-<pv>-<nro>.png`) para no pisar el QR de la factura original (la NC comparte el `tipfac/codfac` de la factura).

### Backend
- Nuevo endpoint `GET /api/credit-notes/{nc_id}/comprobante`: devuelve los datos fiscales de la NC y genera su QR AFIP.
- `arca_service.generate_afip_qr` acepta un `filename` opcional para guardar el QR con un nombre distinto.

---

## v1.7.4 (2026-05-21)

### Nueva funcionalidad - Boton "Grabar datos en Factusol"
- **Problema**: en algunos casos la factura obtenia el CAE correctamente en ARCA (quedaba registrado en el log de CAE Emitidos) pero los datos NO se grababan en Factusol (campos `BNOFAC`/`PEDFAC`/`BNUFAC`/`IMGFAC`/`AATFAC` de F_FAC vacios). Hasta ahora no habia forma de re-sincronizar sin volver a pedir el CAE.
- **Boton "Grabar datos en Factusol"**: re-graba en F_FAC el Nro de comprobante, el vencimiento del CAE, el QR y el codigo de barras AFIP a partir del CAE ya emitido (lo toma del log, NO vuelve a pedir CAE a AFIP). Sirve tambien para re-sincronizar si hay alguna diferencia entre lo emitido y lo que figura en Factusol.
  - Aparece en la lista de Facturas (boton "Grabar", solo cuando hay CAE en el log pero falta en Factusol) y en el modal de detalle de la factura.
  - El modal muestra un aviso cuando detecta la discrepancia (CAE en ARCA pero no en Factusol).
- **Mejor diagnostico al validar**: si al obtener el CAE falla la escritura a Factusol, la respuesta ahora lo informa (`factusol_grabado: false`) y el mensaje sugiere usar el boton de re-grabar, en vez de quedar en silencio.

### Backend
- Nuevo endpoint `POST /api/arca/write-factusol/{tipfac}/{codfac}`: re-graba en Factusol los datos del CAE ya emitido.
- Refactor: la logica de armado de QR + Nro comprobante + codigo de barras + write-back a F_FAC se unifico en un helper reutilizado tanto al validar como al re-grabar.

---

## v1.7.3 (2026-05-13)

### Hotfix - ARCA.exe no arrancaba en v1.7.2
- **Problema**: el build de v1.7.2 no incluyo la libreria `greenlet` (dependencia de SQLAlchemy 2.x). Al iniciar ARCA.exe se generaba `ImportError: cannot import name 'getcurrent' from 'greenlet' (unknown location)` y la app no levantaba el servidor.
- **Causa raiz**: el `arca.spec` confiaba en `collect_submodules('sqlalchemy')` que NO arrastra deps externas (greenlet es paquete separado). En entornos donde greenlet no esta en `site-packages` del venv al momento del build, PyInstaller silenciosamente omite la libreria.
- **Fix**: `greenlet` agregado explicitamente a `hiddenimports` en `arca.spec`.
- **v1.7.2 fue retirada del manifest** (rollback a v1.7.1) mientras se preparo este hotfix. Clientes que descargaron v1.7.2 deben actualizar a v1.7.3.
- Contenido funcional identico a v1.7.2: mapeo de Tipos de IVA + fix operaciones exentas.

---

## v1.7.2 (2026-05-13)

### Nuevas funcionalidades - Mapeo de Tipos de IVA configurable
- **Card "Tipos de IVA (Factusol)"** en Configuracion: permite mapear los 4 tipos de IVA de Factusol (campo IVALFA en lineas, slot N en header) a las alicuotas AFIP correspondientes (21%, 10.5%, 0%, 27%, 5%, 2.5%, Exento).
- **Defaults estandar AR**: tipo 1 = 21%, tipo 2 = 10.5%, tipo 3 = 27%, tipo 4 = Exento. Cada empresa puede ajustar segun como tenga configurado su Factusol.
- **Boton "Detectar desde Factusol"**: analiza las facturas reales de F_FAC (filtrando series fiscales — las que tienen IVA cobrado) y sugiere automaticamente el mapping. El usuario revisa y guarda.
  - Detecta series fiscales por `(IIVA1+IIVA2+IIVA3) > 0` para descartar operaciones internas/presupuestos.
  - Snapea valores cercanos al AFIP valido mas proximo (tolerancia 1.5%).
  - Si un slot no tiene uso historico, deja el valor actual sin tocar.

### Fix - Operaciones Exentas a AFIP
- **Problema**: el campo `imp_op_ex` se mandaba SIEMPRE en 0 a AFIP, aunque la factura tuviera articulos exentos en BAS4FAC. Resultado: facturas con exentos pasaban con el total correcto pero el neto gravado inflado y operaciones exentas en 0.
- **Fix**: `build_voucher_data` ahora usa el `iva_mapping` para decidir que slots son exentos. La base de esos slots va a `imp_op_ex` (operaciones exentas) en lugar de `imp_neto` (neto gravado), y no genera entrada en el array de alicuotas.
- **Mismo fix en RG 1361** (Libro IVA): `imp_exento` se calcula desde el header de Factusol segun el mapping configurado, en vez del `0.0` hardcodeado.
- **Fallback de lineas corregido**: el campo `IVALFA` de F_LFA era tratado como importe monetario cuando en realidad es un codigo categorico (1-4) que indica el tipo de IVA de cada linea. Ahora se agrupa correctamente.

### Backend
- Nuevo endpoint `PUT /api/config/iva-mapping` para guardar el mapeo manual.
- Nuevo endpoint `POST /api/config/iva-mapping/infer` para inferencia automatica desde F_FAC.
- Nueva funcion `factusol_service.infer_iva_mapping()`.

---

## v1.7.1 (2026-05-12)

### Fix - Wizard solo aparece si faltan datos
- **Problema en v1.7.0**: el wizard de primer uso podia abrirse incluso cuando el cliente ya tenia licencia activa (cargada en versiones anteriores con CUIT/email/razon social en config).
- **Fix**: el endpoint `/api/license/needs-registration` ahora solo dispara el wizard cuando faltan los 3 datos basicos (CUIT, email, razon social) en config local. Si ya estan cargados, asumimos que el cliente paso por el wizard antes o cargo los datos manualmente — no molestamos con el modal.
- **Nuevo boton "Activar / Actualizar licencia"** en Configuracion (al lado de "Verificar plan"): abre el wizard de forma manual. Util para:
  - Re-registrar el CUIT en el server si nunca paso por el wizard automatico (clientes que actualizaron desde v1.6.x con datos cargados a mano).
  - Actualizar datos (cambio de email / WhatsApp / razon social) y refrescar el Lead en el CRM.
- El wizard al abrirse manualmente **precarga los datos existentes** desde config (no pide rellenar lo que ya esta).

---

## v1.7.0 (2026-05-12)

### Nuevas funcionalidades - Registro automatico de licencia gratuita
- **Wizard de primer uso**: cuando la app arranca y la empresa no esta registrada todavia (faltan CUIT, email o razon social en config), se muestra un modal bloqueante con un formulario simple.
  - Campos: Razon social, CUIT, Condicion frente al IVA, Nombre del responsable, Email, WhatsApp.
  - **Validacion de CUIT con digito verificador** (mod 11) tanto en frontend como backend.
  - Al submit: POST a `https://goxtech.com.ar/arca_factusol/api/licenses/free` con todos los datos, incluyendo `phone` y `contact_name` para alimentar el CRM.
  - El cliente queda con plan basico activado y un Lead "Nuevo" automaticamente creado en el CRM de GoxTech.
- **Nuevo router `/api/license/`**:
  - `GET  /api/license/needs-registration` - True/False si falta completar el wizard.
  - `POST /api/license/register` - registra al cliente en el backend remoto + guarda config local.
  - `GET  /api/license/status` - estado del plan actual.
  - `POST /api/license/refresh` - fuerza re-verificacion online.

### Backend remoto (deployado en /opt/goxtech_licenses/)
- `POST /licenses/free` ahora acepta campos opcionales `phone`, `contact_name`, `source`.
- Cuando llega un registro nuevo, **crea automaticamente un Lead** en la tabla `leads` con stage="Nuevo", source="app_registration", linkeado por CUIT.
- Si el Lead ya existe (re-registro), actualiza campos vacios + agrega un `LeadEvent` "re_registration".
- Nueva columna `cuit` en tabla `leads` (con indice) para correlacionar Lead <-> License.

---

## v1.6.9 (2026-05-12)

### Fix - Condicion fiscal del cliente mostrada en el modal de factura
- **Problema**: en el modal de detalle de la factura (Facturas -> click en una factura), el campo "Cond. IVA" SIEMPRE mostraba "Resp. Inscripto" independientemente de como estaba cargado el cliente en Factusol.
- **Causa**: el frontend estaba mapeando el campo `IVACLI` (codigo interno de calculos de Factusol que por default queda en 0) en vez de `CFECLI` (condicion fiscal real del cliente).
- **Fix**: el header del modal ahora usa `CFECLI` con el mapeo correcto: 0=Sin configurar, 1=Consumidor Final, 2=Resp. Inscripto, 3=Monotributista, 4=Exento, 5=No Responsable.
- Esto es solo visual — la decision del tipo de comprobante (A/B/C) ya usaba `CFECLI` correctamente desde v1.6.8.

---

## v1.6.8 (2026-05-12)

### Fix - Tipo de comprobante para clientes Exentos
- **Problema**: con el flag "Facturar Monotributistas como Factura A" activado, algunos clientes Exentos podian recibir Factura A. La regla queda explicita ahora.
- **Reglas explicitas por CFECLI (emisor RI + cliente con CUIT)**:
  - CFECLI=2 (Responsable Inscripto) → SIEMPRE Factura A
  - CFECLI=3 (Monotributo) → A si `mono_como_a=True` (RG 5022/21), B si no
  - **CFECLI=4 (Exento) → SIEMPRE Factura B** (el flag mono_como_a no aplica a exentos)
  - CFECLI=5 (No Responsable / No Alcanzado) → SIEMPRE Factura B
  - CFECLI=0/1 con CUIT → Factura B (default seguro)
- **`determine_tipo_comprobante` ahora acepta `explain=True`** y devuelve la razon de la decision junto con el tipo. Se usa en el log de validacion para que quede registrado por que se eligio cada tipo.
- **Log detallado** en cada validacion: `[TIPO CBTE] 1-100: cfecli=4 (Exento) nif='20123456789' mono_como_a=True → tipo=6. Razon: CFECLI=4 (Exento) → Factura B (SIEMPRE...)`.

---

## v1.6.7 (2026-05-12)

### Lineas-leyenda de Factusol
- Muchos usuarios usan lineas con cantidad=0 y precio=0 como **texto descriptivo / leyenda** dentro de la factura (observaciones, condiciones de venta, datos de envio, etc). Esas lineas no son items reales y antes podian bloquear la validacion en ARCA o ensuciar el archivo DETALLE de RG 1361.
- **Nuevo helper `arca_service.is_legend_line`**: detecta lineas con `CANLFA=0 AND PRELFA=0 AND TOTLFA=0`. Estrictamente las tres condiciones — si la cantidad es 1 y el precio 0 (regalo/promo), se mantiene como item real.
- **Filtro automatico aplicado en**:
  - Validacion manual (`arca_router.validate_invoice`).
  - Validacion en lote / auto-validador (`auto_validate._validate_single_sync`).
  - Emision de Notas de Credito (`arca_router.create_credit_note`).
  - Exportacion RG 1361 DETALLE (`rg1361_service.generate_files`).
- **Log visible** cuando se filtran lineas: en consola/log de ARCA aparece `📝 1-100: omitidas 3 linea(s) leyenda (cant=0 precio=0)`.

---

## v1.6.6 (2026-05-12)

### Fix critico - cache del WebView embebido
- **El navegador embebido (Chrome/Edge --app mode) cacheaba HTML/JS** entre updates: despues de actualizar, el server tenia la version nueva pero la UI seguia mostrando la version vieja (los botones nuevos y los filtros no aparecian).
- **Backend**: middleware `NoCacheStaticMiddleware` agrega headers `Cache-Control: no-store, no-cache, must-revalidate` a `/`, `/static/*` y `/favicon.ico`. El browser nunca mas va a cachear los assets de UI.
- **Updater (bat)**: al final del proceso de update, borra automaticamente las subcarpetas de cache del navegador embebido (`Cache/`, `Code Cache/`, `GPUCache/`, `Service Worker/`) preservando las cookies de login. Esto fuerza un reload completo en el primer abrir.

---

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
