# Referencia Base de Datos Factusol (MS Access)

> Exportado desde el proyecto **Facturador Consolidado**.
> Base de datos: archivos `.accdb` (Microsoft Access).
> Conexion ODBC: **SIEMPRE** usar `Mode=Share Deny None` (Factusol puede estar abierto).

---

## Resumen de Tablas

| Tabla | Descripcion | Clave Primaria |
|---|---|---|
| **F_FAC** | Cabecera factura de venta | TIPFAC + CODFAC |
| **F_LFA** | Lineas de factura de venta | TIPLFA + CODLFA + POSLFA |
| **F_SLF** | Series/lotes de factura venta | TIPSLF + CODSLF + POSSLF + NSESLF |
| **F_FRE** | Cabecera factura recibida (compra) | TIPFRE + CODFRE |
| **F_LFR** | Lineas de factura recibida | TIPLFR + CODLFR + POSLFR |
| **F_SLR** | Series/lotes de factura recibida | TIPSLR + CODSLR + POSSLR + NSESLR |
| **F_ART** | Articulos | CODART |
| **F_STO** | Stock por articulo+almacen | ARTSTO + ALMSTO |
| **F_CNS** | Stock por serie/lote (tiempo real) | ARTCNS + ALMCNS + NSECNS |
| **F_CLI** | Clientes | CODCLI |
| **F_PRO** | Proveedores | CODPRO |
| **F_TAR** | Tarifas | CODTAR |
| **F_LTA** | Precios por tarifa x articulo | TARLTA + ARTLTA |
| **F_FAM** | Familias de articulos | CODFAM |
| **F_EMP** | Datos de la empresa | CODEMP |

> **NO existe tabla F_CSL / F_CSN** — no buscarla.

---

## Diagrama de Relaciones

```
F_FAC ──┬── F_LFA ──── F_SLF
        │       │
        │       └── F_ART ──── F_STO
        │                  │
        │                  └── F_CNS
        └── F_CLI

F_FRE ──┬── F_LFR ──── F_SLR
        │       │
        │       └── F_ART
        └── F_PRO

F_ART ──── F_FAM
      ├── F_LTA ──── F_TAR
      └── F_STO
```

---

## IVA — Tipos (patron Factusol)

Patron: `[L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]`

| Valor | Tipo Factusol | Alicuota |
|:---:|---|:---:|
| `0` | IVA Tipo 1 (IVA1AUT) | **21%** |
| `1` | IVA Tipo 2 (IVA2AUT) | **10,5%** |
| `2` | IVA Tipo 3 (IVA3AUT) | **4%** |
| `3` | Exento | **0%** |

> **El valor 0 NO es exento** — es IVA 21%. Exento es valor `3`.
> Se usa en: `F_LFA.IVALFA`, `F_LFR.IVALFR`, `F_ART.TIVART`.

---

## Estados de Documentos

### F_FAC — Facturas de Venta (ESTFAC)
| Valor | Estado |
|:---:|---|
| `0` | Pendiente |
| `1` | Pendiente Parcial |
| `2` | Cobrada |
| `3` | Devuelta |
| `4` | Anulada |

### F_FRE — Facturas de Compra (ESTFRE)
| Valor | Estado |
|:---:|---|
| `0` | Pendiente |
| `1` | Pagada Parcial |
| `2` | Pagada |

---

## Calculo de Stock

### Stock General
Tabla `F_STO`: campos `ACTSTO` (actual) y `DISSTO` (disponible).

### Stock por NSE (Serie/Lote) — Metodo Calculado
```sql
stock_nse = SUM(F_SLR.CANSLR WHERE ARTSLR=codart AND NSESLR=nse)
          - SUM(F_SLF.CANSLF WHERE ARTSLF=codart AND NSESLF=nse)
```

### Stock por NSE — Via F_CNS (Tiempo Real)
Tabla `F_CNS` es la **fuente de verdad en tiempo real** para stock por serie/lote:
```sql
SELECT NSECNS, CANCNS FROM F_CNS
WHERE ARTCNS = ? AND ALMCNS = ? AND CANCNS > 0
```

---

## Numeracion de Documentos

- **TIPFAC / TIPFRE**: Serie numerica (1-9), categoriza tipos de documento
- **CODFAC / CODFRE**: Numero secuencial dentro de la serie
- **Nuevo documento**: `MAX(CODFAC) + 1` dentro de su `TIPFAC`
- **ID Virtual (NROFAC)**: `Concat(TIPFAC, "-", CODFAC)` — ej: `1-000042`
- **Fecha nula**: Access usa `1900-01-01` como null-equivalente, mostrar como vacio

---

## Tablas Detalladas

### F_FAC (Cabecera Factura Venta)

| Campo | Descripcion |
|---|---|
| `TIPFAC` | Serie (codigo numerico) |
| `CODFAC` | Numero secuencial |
| `REFFAC` | Su referencia |
| `FECFAC` | Fecha |
| `ESTFAC` | Estado (0-4, ver tabla estados) |
| `ALMFAC` | Almacen (default: "GEN") |
| `AGEFAC` | Agente comercial |
| `CLIFAC` | Codigo cliente |
| `CNOFAC` | Nombre cliente |
| `CDOFAC` | Domicilio |
| `CPOFAC` | Poblacion |
| `CCPFAC` | Codigo postal |
| `CPRFAC` | Provincia |
| `CNIFAC` | NIF |
| `TIVFAC` | Tipo de IVA (0=Con IVA, 1=Sin IVA, 2=Intracomunitario, 3=Exportacion) |
| `REQFAC` | Recargo equivalencia (0=No, 1=Si) |
| `TELFAC` | Telefono |
| `NET1FAC`..`NET3FAC` | Netos por tipo IVA (1, 2, 3) |
| `PDTO1FAC`..`PDTO3FAC` | % descuento por neto |
| `IDTO1FAC`..`IDTO3FAC` | Importe descuento por neto |
| `PPPA1FAC`..`PPPA3FAC` | % pronto pago por neto |
| `IPPA1FAC`..`IPPA3FAC` | Importe pronto pago |
| `PPOR1FAC`..`PPOR3FAC` | % portes |
| `IPOR1FAC`..`IPOR3FAC` | Importe portes |
| `PFIN1FAC`..`PFIN3FAC` | % financiacion |
| `IFIN1FAC`..`IFIN3FAC` | Importe financiacion |
| `BAS1FAC`..`BAS3FAC` | Base imponible por tipo IVA |
| `PIVA1FAC`..`PIVA3FAC` | % impuestos |
| `IIVA1FAC`..`IIVA3FAC` | Importe impuestos |
| `PREC1FAC`..`PREC3FAC` | % recargo equivalencia |
| `IREC1FAC`..`IREC3FAC` | Importe recargo equivalencia |
| `PRET1FAC` | % retencion |
| `IRET1FAC` | Importe retencion |
| `TOTFAC` | Total |
| `FOPFAC` | Forma de pago |
| `OB1FAC`, `OB2FAC` | Observaciones (2 lineas) |
| `PEDFAC` | Nro de pedido (usado para refs AFIP) |
| `FPEFAC` | Fecha de pedido |
| `COBFAC` | Recibo (0=Pendiente, 1=Girado) |
| `COPFAC` | Clave de operacion |
| `TRAFAC` | Traspasado a contabilidad (0=No, 1=Si) |
| `HORFAC` | Hora (HH:mm) |
| `USUFAC` | Codigo usuario creador |
| `USMFAC` | Ultimo usuario modificador |
| `NET4FAC` | Neto exento de impuestos |
| `BAS4FAC` | Base exenta |
| `TIVA1FAC`..`TIVA3FAC` | Tipo IVA al que pertenece cada neto |
| `RCCFAC` | Regimen criterio de caja |
| `FROFAC` | Fecha de operacion |
| `FUMFAC` | Fecha ultima modificacion |
| `TDRFAC` | Serie doc. rectificado |
| `CDRFAC` | Codigo doc. rectificado |

### F_LFA (Lineas Factura Venta)

| Campo | Descripcion |
|---|---|
| `TIPLFA` | Serie (FK → F_FAC.TIPFAC) |
| `CODLFA` | Numero (FK → F_FAC.CODFAC) |
| `POSLFA` | Posicion/linea (secuencial) |
| `ARTLFA` | Articulo (FK → F_ART.CODART) |
| `DESLFA` | Descripcion |
| `CANLFA` | Cantidad |
| `DT1LFA` | Descuento 1 |
| `DT2LFA` | Descuento 2 |
| `DT3LFA` | Descuento 3 |
| `PRELFA` | Precio unitario |
| `TOTLFA` | Total linea (neto) |
| `IVALFA` | Tipo IVA (0=21%, 1=10.5%, 2=4%, 3=Exento) |
| `COSLFA` | Precio costo al crear la linea |
| `BULLFA` | Bultos |
| `COMLFA` | Comision agente |
| `MEMLFA` | Comentarios |
| `IINLFA` | [E] IVA incluido en la linea |
| `PIVLFA` | [E] Precio IVA incluido |
| `TIVLFA` | [E] Total IVA incluido |
| `CE1LFA` | Talla |
| `CE2LFA` | Color |

### F_SLF (Series/Lotes Factura Venta)

| Campo | Descripcion |
|---|---|
| `TIPSLF` | Serie factura (FK → F_FAC.TIPFAC) |
| `CODSLF` | Codigo factura (FK → F_FAC.CODFAC) |
| `POSSLF` | Posicion linea (FK → F_LFA.POSLFA) |
| `NSESLF` | Numero de serie/lote |
| `CANSLF` | Cantidad |
| `FFASLF` | Fecha fabricacion |
| `FCOSLF` | Fecha consumo preferente |
| `ARTSLF` | [E] Articulo |

---

### F_FRE (Cabecera Factura Recibida / Compra)

| Campo | Descripcion |
|---|---|
| `TIPFRE` | Serie |
| `CODFRE` | Codigo secuencial |
| `FACFRE` | Codigo de factura (ref. proveedor) |
| `REFFRE` | Su referencia |
| `FECFRE` | Fecha |
| `PROFRE` | Proveedor (FK → F_PRO.CODPRO) |
| `ESTFRE` | Estado (0=Pte, 1=Pag.Parcial, 2=Pagada) |
| `PNOFRE` | Nombre proveedor |
| `PDOFRE` | Domicilio |
| `PPOFRE` | Poblacion |
| `PNIFRE` | NIF |
| `TIVFRE` | Tipo IVA (0=Con, 1=Sin, 2=Intracom., 3=Importacion) |
| `NET1FRE`..`NET4FRE` | Netos (1-3 por tipo IVA + 4 exento) |
| `BAS1FRE`..`BAS4FRE` | Bases imponibles |
| `PIVA1FRE`..`PIVA3FRE` | % impuestos |
| `IIVA1FRE`..`IIVA3FRE` | Importe impuestos |
| `TOTFRE` | Total |
| `FOPFRE` | Forma de pago |
| `ALMFRE` | Almacen |
| `USUFRE` | Usuario creador |
| `FUMFRE` | Fecha ultima modificacion |
| `DEDFRE` | Tipo (0=Deducible, 1=No deducible, 2=Prorrata) |

### F_LFR (Lineas Factura Recibida)

| Campo | Descripcion |
|---|---|
| `TIPLFR` | Serie (FK → F_FRE.TIPFRE) |
| `CODLFR` | Codigo (FK → F_FRE.CODFRE) |
| `POSLFR` | Posicion |
| `ARTLFR` | Articulo (FK → F_ART.CODART) |
| `DESLFR` | Descripcion |
| `CANLFR` | Cantidad |
| `DT1LFR`..`DT3LFR` | Descuentos 1-3 |
| `PRELFR` | Precio |
| `TOTLFR` | Total |
| `IVALFR` | Tipo IVA |
| `BULLFR` | Bultos |
| `MEMLFR` | Comentarios |

### F_SLR (Series/Lotes Factura Recibida)

| Campo | Descripcion |
|---|---|
| `TIPSLR` | Serie (FK → F_FRE.TIPFRE) |
| `CODSLR` | Codigo (FK → F_FRE.CODFRE) |
| `POSSLR` | Posicion linea |
| `NSESLR` | Numero de serie/lote |
| `CANSLR` | Cantidad |
| `FFASLR` | Fecha fabricacion |
| `FCOSLR` | Fecha consumo preferente |
| `ARTSLR` | [E] Articulo |

---

### F_ART (Articulos)

| Campo | Descripcion |
|---|---|
| `CODART` | Codigo articulo (PK) |
| `EANART` | Codigo EAN |
| `EQUART` | Equivalente |
| `CCOART` | Codigo corto |
| `FAMART` | Familia (FK → F_FAM.CODFAM) |
| `DESART` | Descripcion general |
| `PHAART` | Proveedor habitual |
| `TIVART` | Tipo IVA (0-3, mismo patron) |
| `PCOART` | Precio de costo |
| `DT0ART`..`DT2ART` | Descuentos 1-3 |
| `FALART` | Fecha de alta |
| `REFART` | Referencia del proveedor |
| `DLAART` | Descripcion larga |
| `CANART` | Cantidad por defecto en salidas |
| `STOART` | [E] Control de stock |
| `FUMART` | Fecha ultima modificacion |
| `PESART` | Peso |
| `UMEART` | Unidad de medida |
| `DFIART` | % Descuento fijo en ventas |
| `DSCART` | Articulo descatalogado |
| `CP1ART`..`CP5ART` | Campos programables 1-5 |

### F_STO (Stock General)

| Campo | Descripcion |
|---|---|
| `ARTSTO` | Articulo (FK → F_ART.CODART) |
| `ALMSTO` | Almacen |
| `MINSTO` | Stock minimo |
| `MAXSTO` | Stock maximo |
| `ACTSTO` | Stock actual |
| `DISSTO` | Stock disponible |
| `UBISTO` | Ubicacion en almacen |

### F_CNS (Stock por Serie/Lote)

| Campo | Descripcion |
|---|---|
| `ALMCNS` | Almacen |
| `ARTCNS` | Articulo (FK → F_ART.CODART) |
| `NSECNS` | Numero de serie/lote |
| `CANCNS` | Unidades disponibles |
| `FFACNS` | Fecha fabricacion |
| `FCOCNS` | Fecha consumo preferente |
| `FECCNS` | Fecha |

---

### F_CLI (Clientes)

| Campo | Descripcion |
|---|---|
| `CODCLI` | Codigo cliente (PK) |
| `CCOCLI` | Codigo contable |
| `NIFCLI` | NIF |
| `NOFCLI` | Nombre fiscal |
| `NOCCLI` | Nombre comercial |
| `DOMCLI` | Domicilio |
| `POBCLI` | Poblacion |
| `CPOCLI` | Codigo postal |
| `PROCLI` | Provincia |
| `TELCLI` | Telefono |
| `FAXCLI` | Fax |
| `EMACLI` | E-mail |
| `FPACLI` | Forma de pago |
| `TARCLI` | [E] Tarifa |
| `DT1CLI`..`DT3CLI` | Descuentos 1-3 |
| `IVACLI` | Tipo IVA (0=Con, 1=Sin, 2=Intra, 3=Export) |
| `TIVCLI` | Porcentaje IVA (0=Sin asignar, 1=IVA1, 2=IVA2, 3=IVA3, 4=Exento) |
| `REQCLI` | Recargo equivalencia (0=No, 1=Si) |
| `PAICLI` | Pais |
| `DOCCLI` | Serie predeterminada |
| `CPRCLI` | Codigo de proveedor |
| `AGECLI` | Agente comercial |
| `FALCLI` | Fecha alta |
| `ESTCLI` | Estado (0=Sin sel, 1=Habitual, 2=Esporadico, 3=Baja, 4=En...) |
| `RETCLI` | Retencion (0=No, 1=Si) |
| `PRECLI` | % retencion |
| `DTCCLI` | % dto. comercial |
| `FUMCLI` | Fecha ultima modificacion |
| `MOVCLI` | Movil |
| `RCCCLI` | Regimen criterio de caja |

### F_PRO (Proveedores)

| Campo | Descripcion |
|---|---|
| `CODPRO` | Codigo proveedor (PK) |
| `CCOPRO` | Codigo contabilidad |
| `TIPPRO` | Tipo (0=Proveedor, 1=Acreedor) |
| `NIFPRO` | NIF |
| `NOFPRO` | Nombre fiscal |
| `NOCPRO` | Nombre comercial |
| `DOMPRO` | Domicilio |
| `POBPRO` | Poblacion |
| `CPOPRO` | Codigo postal |
| `PROPRO` | Provincia |
| `TELPRO` | Telefono |
| `EMAPRO` | E-mail |
| `FPAPRO` | Forma de pago |
| `DT1PRO`..`DT3PRO` | Descuentos 1-3 |
| `IVAPRO` | Tipo IVA (0=Con, 1=Sin, 2=Intra, 3=Import) |
| `PAIPRO` | Pais |
| `RETPRO` | % retencion |
| `DOCPRO` | Serie predeterminada |
| `CCLPRO` | Codigo de cliente |
| `FALPRO` | Fecha alta |
| `FUMPRO` | Fecha ultima modificacion |

### F_TAR (Tarifas)

| Campo | Descripcion |
|---|---|
| `CODTAR` | Codigo tarifa (PK) |
| `DESTAR` | Descripcion |
| `MARTAR` | Margen |
| `IVATAR` | Incluir impuesto |

### F_LTA (Precios por Tarifa)

| Campo | Descripcion |
|---|---|
| `TARLTA` | Tarifa (FK → F_TAR.CODTAR) |
| `ARTLTA` | Articulo (FK → F_ART.CODART) |
| `PRELTA` | Precio |
| `MARLTA` | Margen |

### F_FAM (Familias)

| Campo | Descripcion |
|---|---|
| `CODFAM` | Codigo familia (PK) |
| `DESFAM` | Descripcion |
| `SECFAM` | Seccion |
| `CUEFAM` | Cuenta contable ventas |
| `CUCFAM` | Cuenta contable compras |

### F_EMP (Empresa)

| Campo | Descripcion |
|---|---|
| `CODEMP` | Codigo empresa (PK) |
| `NIFEMP` | NIF |
| `DENEMP` | Denominacion social |
| `NOMEMP` | Nombre comercial |
| `SIGEMP` | Sigla |
| `DOMEMP` | Domicilio |
| `POBEMP` | Poblacion |
| `CPOEMP` | Codigo postal |
| `PROEMP` | Provincia |
| `TELEMP` | Telefono |
| `EMAEMP` | E-mail |
| `WEBEMP` | Web |
| `MOVEMP` | Movil |
| `EJEEMP` | [E] Ejercicio |

---

## Compatibilidad SQL (MS Access / ODBC)

### Reglas Generales
- Parametros: SIEMPRE `?` placeholders, NUNCA concatenar strings SQL
- `UCASE()`: solo en queries simples sin JOIN. Con JOIN usar `LIKE`
- Paginacion: **NO** usar `TOP N` ni `OFFSET` — cargar todo, paginar en memoria
- Filtro multi-token: usar funcion `token_search_clause()` para busquedas flexibles

### Patron EXISTS (evitar JOINs encadenados)

Access ODBC falla con cadenas de 3+ INNER JOINs. Usar `EXISTS`:

```sql
-- MAL: falla con "Operator missing" o "Query too complex"
SELECT DISTINCT f.CODFAC, f.CNOFAC
FROM F_FAC f
INNER JOIN F_LFA lf ON lf.TIPLFA = f.TIPFAC AND lf.CODLFA = f.CODFAC
INNER JOIN F_ART ar ON ar.CODART = lf.ARTLFA
WHERE ar.FAMART IN ('FAMILY_A', 'FAMILY_B')

-- BIEN: compatible con Access ODBC
SELECT f.CODFAC, f.CNOFAC
FROM F_FAC f
WHERE EXISTS (
    SELECT 1
    FROM F_LFA lf, F_ART ar
    WHERE lf.ARTLFA = ar.CODART
      AND lf.TIPLFA = f.TIPFAC
      AND lf.CODLFA = f.CODFAC
      AND ar.FAMART IN ('FAMILY_A', 'FAMILY_B')
)
```

### Conexion
- Driver: Microsoft Access Database Engine 2016 o 2019
- `Mode=Share Deny None` — siempre, sin excepcion
- Context manager: `get_connection(empresa)` donde empresa = 1 o 2
- Funciones: `fetch_all()`, `fetch_one()`, `execute()`, `execute_many()`

---

## Campos Marcados con [E]

Los campos marcados `[E]` en la documentacion Factusol son campos **internos/extendidos** que no se muestran normalmente en la UI pero que pueden contener datos auxiliares importantes (imagenes, trazabilidad, permisos, etc.).

## Campos con [F=...]

Los campos marcados `[F=...]` indican un **formato de visualizacion**. Por ejemplo:
- `[F=000000]` → formato numerico con ceros a la izquierda (6 digitos)
- `[F=00000]` → 5 digitos
- `[F=HH:mm]` → formato hora

## Campos con [L=...]

Los campos marcados `[L=...]` definen una **lista de valores posibles**. Por ejemplo:
- `[L=#0;Pte.#1;Pte. Parcial#2;Cobrada#3;Devuelta#4;Anulada]` → ESTFAC
- `[L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]` → Tipos de IVA
