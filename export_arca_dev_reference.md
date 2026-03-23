# ARCA (ex AFIP) - Referencia de Desarrollo WSFEv1

> **Documento de referencia** para todos los desarrollos que integren con el servicio de 
> Facturacion Electronica de ARCA (Agencia de Recaudacion y Control Aduanero, ex AFIP).
>
> Basado en: `Manual para el desarrollador - RG 4291 - Proyecto FE v4.0`  
> Revision: 15 de Enero de 2025  
> Fuente: https://www.afip.gob.ar/fe/documentos/manual-desarrollador-ARCA-COMPG-v4-0.pdf

---

## 1. Arquitectura General

### 1.1 Servicios Web (Web Services)

| Servicio | Descripcion | Service Tag WSAA |
|---|---|---|
| **WSAA** | Autenticacion y Autorizacion | - |
| **WSFEv1** | Facturacion Electronica RG 4291 | `wsfe` |
| **ws_sr_constancia_inscripcion** | Padron (Constancia de Inscripcion) | `ws_sr_constancia_inscripcion` |

### 1.2 URLs de los Servicios

| Ambiente | URL WSFEv1 | WSDL |
|---|---|---|
| **Homologacion** | `https://wswhomo.afip.gov.ar/wsfev1/service.asmx` | `...?WSDL` |
| **Produccion** | `https://servicios1.afip.gov.ar/wsfev1/service.asmx` | `...?WSDL` |

| Ambiente | URL WSAA |
|---|---|
| **Homologacion** | `https://wsaahomo.afip.gov.ar/ws/services/LoginCms` |
| **Produccion** | `https://wsaa.afip.gov.ar/ws/services/LoginCms` |

### 1.3 Autenticacion

- Requiere **certificado digital** obtenido desde Clave Fiscal
- El certificado debe estar **asociado al WS de negocio** "Facturacion Electronica"
- El Ticket de Acceso (TA) se solicita via WSAA con `service = "wsfe"`
- **Duracion del TA**: 12 horas
- El TA contiene `Token` y `Sign` que se envian en cada request

### 1.4 Contactos ARCA

| Canal | Email |
|---|---|
| Homologacion (WS) | wsfev1@arca.gov.ar |
| Produccion | sri@arca.gov.ar |
| Normativa | facturaelectronica@arca.gov.ar |

---

## 2. Metodos del WSFEv1

### 2.1 Metodos CAE (los que usamos)

| Metodo | Descripcion | Uso |
|---|---|---|
| **FECAESolicitar** | Solicitar CAE para comprobante/lote | Validar facturas |
| **FECompUltimoAutorizado** | Ultimo nro de comprobante emitido | Obtener proximo nro |
| **FECompConsultar** | Consultar comprobante emitido | Verificar estado |
| **FEDummy** | Verificar estado de servidores | Monitor de salud |

### 2.2 Metodos de Parametros (referencia)

| Metodo | Descripcion |
|---|---|
| FEParamGetTiposCbte | Tipos de comprobante |
| FEParamGetTiposConcepto | Tipos de concepto (1=Prod, 2=Serv, 3=Ambos) |
| FEParamGetTiposDoc | Tipos de documento |
| FEParamGetTiposIva | Alicuotas de IVA |
| FEParamGetTiposMonedas | Monedas |
| FEParamGetTiposOpcional | Datos opcionales |
| FEParamGetTiposTributos | Tributos |
| FEParamGetPtosVenta | Puntos de venta habilitados para FE |
| FEParamGetCotizacion | Cotizacion de moneda (v4.0: acepta fecha opcional) |
| FEParamGetCondicionIvaReceptor | **(v4.0 nuevo)** Condiciones IVA del receptor |
| FEParamGetActividades | Actividades del emisor |
| FEParamGetTiposPaises | Paises |
| FECompTotXRequest | Cantidad maxima de registros por request |

---

## 3. FECAESolicitar - Estructura Completa

### 3.1 Cabecera (FeCabReq)

| Campo | Tipo | Descripcion | Oblig. |
|---|---|---|---|
| CantReg | Int(4) | Cantidad de registros en el lote | S |
| CbteTipo | Int(3) | Tipo de comprobante | S |
| PtoVta | Int(5) | Punto de venta | S |

### 3.2 Detalle (FECAEDetRequest)

| Campo | Tipo | Descripcion | Oblig. |
|---|---|---|---|
| **Concepto** | Int(2) | 1=Productos, 2=Servicios, 3=Ambos | S |
| **DocTipo** | Int(2) | Tipo documento comprador | S |
| **DocNro** | Long(11) | CUIT/DNI del comprador | S |
| **CbteDesde** | Long(8) | Nro comprobante desde. **Rango 1-99999999** | S |
| **CbteHasta** | Long(8) | Nro comprobante hasta. **Rango 1-99999999** | S |
| **CbteFch** | String(8) | Fecha comprobante YYYYMMDD | N |
| **ImpTotal** | Double(13+2) | Total = Neto + IVA + Tributos + Exento + NoGravado | S |
| **ImpTotConc** | Double(13+2) | Neto no gravado (0 para tipo C) | S |
| **ImpNeto** | Double(13+2) | Neto gravado (subtotal para tipo C) | S |
| **ImpOpEx** | Double(13+2) | Importe exento (0 para tipo C) | S |
| **ImpIVA** | Double(13+2) | Suma del array IVA (0 para tipo C) | S |
| **ImpTrib** | Double(13+2) | Suma del array tributos | S |
| FchServDesde | String(8) | Inicio periodo servicio (concepto 2 o 3) | N |
| FchServHasta | String(8) | Fin periodo servicio | N |
| FchVtoPago | String(8) | Vto pago (concepto 2/3 o FCE MiPyME) | N |
| **MonId** | String(3) | Moneda. `PES` = Pesos argentinos | S |
| **MonCotiz** | Double(4+6) | Cotizacion. `1` para PES | S |
| CanMisMonExt | String(1) | **(v4.0)** Cancela en misma moneda extranjera S/N | N |
| CondicionIVAReceptorId | Int(2) | **(v4.0)** Condicion IVA receptor | N |
| CbtesAsoc | Array | Comprobantes asociados (NC, ND) | N |
| Tributos | Array | Tributos asociados | N |
| **Iva** | Array | Alicuotas IVA (NO informar para tipo C) | N |
| Opcionales | Array | Campos opcionales extra | N |
| Compradores | Array | Multiples compradores | N |
| PeriodoAsoc | Struct | Periodo asociado (RG 4540) | N |
| Actividades | Array | Actividades asociadas | N |

### 3.3 Alicuotas de IVA (AlicIva)

| Campo | Tipo | Descripcion | Oblig. |
|---|---|---|---|
| Id | Int(3) | Codigo de alicuota (ver tabla) | S |
| BaseImp | Double(13+2) | Base imponible | S |
| Importe | Double(13+2) | Importe de IVA | S |

**Codigos de alicuotas IVA:**

| Id | Alicuota | Porcentaje |
|---|---|---|
| 3 | 0% | 0.00% |
| 4 | 10.5% | 10.50% |
| 5 | 21% | 21.00% |
| 6 | 27% | 27.00% |
| 8 | 5% | 5.00% |
| 9 | 2.5% | 2.50% |

### 3.4 Regla de Calculo de ImpTotal

```
ImpTotal = ImpNeto + ImpIVA + ImpTrib + ImpTotConc + ImpOpEx
```

Para **comprobantes tipo C** (monotributista):
- `ImpTotConc = 0`
- `ImpOpEx = 0`
- `ImpIVA = 0`
- `ImpNeto = subtotal`
- NO informar array Iva

---

## 4. Tipos de Comprobante (CbteTipo)

| Codigo | Descripcion | Emisor |
|---|---|---|
| 1 | Factura A | RI a RI |
| 2 | Nota de Debito A | RI a RI |
| 3 | Nota de Credito A | RI a RI |
| 6 | Factura B | RI a CF/Mono/Exento |
| 7 | Nota de Debito B | RI a CF/Mono/Exento |
| 8 | Nota de Credito B | RI a CF/Mono/Exento |
| 11 | Factura C | Mono a cualquiera |
| 12 | Nota de Debito C | Mono a cualquiera |
| 13 | Nota de Credito C | Mono a cualquiera |
| 51 | Factura M | RI nuevo |
| 201 | Factura Credito A (MiPyME FCE) | RI a RI |
| 206 | Factura Credito B (MiPyME FCE) | RI a CF |

### 4.1 Determinacion del Tipo de Comprobante

| Emisor / Receptor | RI | CF | Monotributo | Exento |
|---|---|---|---|---|
| **Resp. Inscripto** | Factura A (1) | Factura B (6) | Factura B (6) | Factura B (6) |
| **Monotributista** | Factura C (11) | Factura C (11) | Factura C (11) | Factura C (11) |
| **Exento** | Factura C (11) | Factura C (11) | Factura C (11) | Factura C (11) |

---

## 5. Tipos de Documento (DocTipo)

| Codigo | Descripcion | Uso |
|---|---|---|
| 80 | CUIT | Facturas A, ND A, NC A |
| 86 | CUIL | - |
| 96 | DNI | Facturas B con monto > $10000 |
| 99 | Sin identificar | Facturas B con monto <= $10000, CF |
| 0 | CI Policía Federal | Raro |

**Regla para DocNro:**
- Si DocTipo = 99 → DocNro = 0
- Si DocTipo = 80 → DocNro = CUIT (11 digitos, sin guiones)

---

## 6. FECompUltimoAutorizado

Retorna el ultimo numero de comprobante autorizado para un tipo y punto de venta.

| Parametro | Tipo | Descripcion |
|---|---|---|
| CbteTipo | Int | Tipo de comprobante |
| PtoVta | Int | Punto de venta |

**Retorna:** `CbteNro` (Long) - ultimo numero autorizado

**Uso:** El proximo comprobante es `CbteNro + 1` y se usa como `CbteDesde` y `CbteHasta`.

---

## 7. FEDummy - Monitor de Servidores

Sin parametros. Retorna estado de 3 servidores:

| Campo | Valores |
|---|---|
| AppServer | `OK` / offline |
| DbServer | `OK` / offline |
| AuthServer | `OK` / offline |

---

## 8. Respuesta de FECAESolicitar

### 8.1 Resultado

| Campo | Descripcion |
|---|---|
| Resultado | `A` = Aprobado, `R` = Rechazado, `P` = Parcial |
| CAE | Codigo de Autorizacion Electronica (14 digitos) |
| CAEFchVto | Fecha vencimiento CAE (YYYYMMDD) |

### 8.2 Errores Comunes

| Codigo | Mensaje | Causa comun |
|---|---|---|
| 10008 | Campo CbteDesde entre 1 y 99999999 | `FECompUltimoAutorizado` no retorno valor, o WS no autorizado |
| 10016 | Fecha comprobante fuera de rango | CbteFch muy vieja o futura |
| 10038 | MonCotiz invalida | Cotizacion erronea |
| 10048 | ImpTotal no coincide | Suma de importes no cierra |
| 10015 | DocNro requerido | Falta DNI/CUIT para montos > $10000 |
| 10063 | CUIT emisor no habilitado | Certificado no delegado |

---

## 9. QR Fiscal (ARCA)

El QR de comprobante electronico se genera con la siguiente URL:

```
https://www.afip.gob.ar/fe/qr/?p={BASE64_JSON}
```

Donde el JSON contiene:
```json
{
  "ver": 1,
  "fecha": "2026-03-23",
  "cuit": 30712253610,
  "ptoVta": 2,
  "tipoCmp": 6,
  "nroCmp": 1479,
  "importe": 1.00,
  "moneda": "PES",
  "ctz": 1,
  "tipoDocRec": 80,
  "nroDocRec": 20123456789,
  "tipoCodAut": "E",
  "codAut": 12345678901234
}
```

| Campo | Descripcion |
|---|---|
| ver | Version del QR (siempre 1) |
| fecha | Fecha comprobante YYYY-MM-DD |
| cuit | CUIT emisor (long, sin guiones) |
| ptoVta | Punto de venta |
| tipoCmp | Tipo comprobante |
| nroCmp | Numero de comprobante |
| importe | Importe total |
| moneda | Moneda ("PES") |
| ctz | Cotizacion |
| tipoDocRec | Tipo doc receptor |
| nroDocRec | Nro doc receptor |
| tipoCodAut | "E" = CAE, "A" = CAEA |
| codAut | Numero CAE/CAEA |

---

## 10. Condiciones IVA en Factusol (IVACLI)

Mapeo entre campo `IVACLI` de Factusol y codigos ARCA:

| IVACLI Factusol | Condicion IVA | DocTipo ARCA |
|---|---|---|
| 0 | Responsable Inscripto | 80 (CUIT) |
| 1 | Monotributo | 80 (CUIT) |
| 3 | Exento | 80 (CUIT) |
| 4 | Consumidor Final | 99 (sin identificar) o 96 (DNI) |

---

## 11. Campos Nuevos v4.0 (Enero 2025)

| Campo | Tipo | Descripcion |
|---|---|---|
| **CanMisMonExt** | String(1) | Si = "S", el comprobante se cancela en la misma moneda extranjera. Si se marca, la cotizacion debe coincidir exactamente con la de ARCA del dia habil anterior. |
| **CondicionIVAReceptorId** | Int(2) | Condicion IVA del receptor. Nuevo metodo `FEParamGetCondicionIvaReceptor` para consultar valores. Si invalido: CAE rechaza, CAEA observa. |

### 11.1 Nuevos Codigos de Error v4.0

| Codigo | Descripcion |
|---|---|
| 10239 - 10243 | Validaciones para CAE relacionadas con nuevos campos |
| 820 - 824 | Validaciones para CAEA |
| 12002 | Error en FEParamGetCotizacion con fecha |
| 10244 | Error en FEParamGetCondicionIvaReceptor |

### 11.2 Cambio en MonCotiz (10038)

Si se marca `CanMisMonExt = "S"`, la cotizacion debe ser **exacta** con la registrada en ARCA para el dia habil anterior a la fecha de emision. Si no se marca, se puede omitir el campo.

---

## 12. Flujo de Validacion en Nuestro Sistema

```
1. Usuario click "Validar CAE"
2. Frontend → POST /api/arca/validate/{tipfac}/{codfac}?pv_id={id}
3. Backend lee factura de Factusol (F_FAC + F_LFA)
4. Determina tipo_comprobante segun IVACLI del cliente
5. FECompUltimoAutorizado → obtiene ultimo nro
6. next_cbte = ultimo + 1
7. Construye payload FECAESolicitar
8. Envia a WSFEv1
9. Si OK → guarda CAE en BD local (cae_logs) + escribe en Factusol (BNOFAC, PEDFAC, BNUFAC)
10. Genera QR → guarda imagen en static/qr/
11. Retorna resultado al frontend
```

### 12.1 Campos Factusol para CAE

| Campo F_FAC | Uso | Descripcion |
|---|---|---|
| BNOFAC | CAE | Numero de CAE (14 digitos) |
| PEDFAC | Voucher | Numero de comprobante ARCA |
| BNUFAC | Vto CAE | Fecha vencimiento CAE |
| IMGFAC | QR Path | Ruta imagen QR |

---

## 13. Troubleshooting

### Error 10008: CbteDesde entre 1 y 99999999

**Causa:** `FECompUltimoAutorizado` retorna 0 o error, lo que hace `next_cbte = 1` pero el WS rechaza.  
**Solucion:** Verificar que:
1. El certificado tenga delegado WSFEv1
2. El punto de venta exista y este habilitado para FE
3. El tipo de comprobante sea correcto para ese PV
4. El PV este dado de alta en AFIP para el CUIT del certificado

### Error coe.notAuthorized

**Causa:** El certificado digital no tiene delegado el servicio.  
**Solucion:** Ir a AFIP Portal → Administrar Relaciones → delegar `wsfe` y/o `ws_sr_constancia_inscripcion`

### Error ImpTotal no coincide (10048)

**Causa:** La suma de `ImpNeto + ImpIVA + ImpTrib + ImpTotConc + ImpOpEx != ImpTotal`  
**Solucion:** Verificar el calculo en `build_voucher_data()`

---

## 14. Libreria Python Utilizada

**pyafipws** - Biblioteca oficial/comunidad para AFIP WS  
- `WSFEv1` - Facturacion Electronica
- `WSFEv1.CrearFactura()` - Crea el request
- `WSFEv1.AgregarIva()` - Agrega alicuota
- `WSFEv1.CAESolicitar()` - Envia request
- `WSFEv1.Dummy()` - Test de servidores
- `WSFEv1.CompUltimoAutorizado()` - Ultimo nro
- Propiedades: `.CAE`, `.Vencimiento`, `.Resultado`, `.Obs`, `.ErrMsg`, `.Excepcion`

---

*Documento generado el 2026-03-23. Fuente oficial: ARCA SDG SIT.*
