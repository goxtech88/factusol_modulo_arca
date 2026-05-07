# Changelog - Factusol ARCA Sync

## v1.5.0 (2026-05-06)

### Nuevas funcionalidades
- **Exportador RG 1361 (Duplicado Electronico)**: Genera CABECERA_AAAAMM.txt y DETALLE_AAAAMM.txt en el formato exacto del Anexo II de la RG (AFIP) 1361/2002, listos para subir a sistemas de validacion tributaria.
  - Boton "Exportar RG 1361" en seccion CAE Emitidos. Toma el periodo del filtro de mes activo (o el mes en curso).
  - Registros tipo 1 + tipo 2 (resumen) en CABECERA, ASCII, padding numerico con ceros, alfanumerico con blancos a derecha, fin de registro CRLF (0D0A).
  - Mapeo automatico de codigos: tipo de responsable (Tabla E.4), alicuota IVA (Tabla E.6), documento (Tabla E.7).
  - Endpoint: `GET /api/arca/rg1361/export?year=YYYY&month=MM[&pv=NNNN]` -> ZIP con ambos archivos.

---

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
