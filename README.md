# Factusol ARCA Sync

Módulo de facturación electrónica ARCA (ex AFIP) para **Factusol** — desarrollado por **GoxTech S.R.L.**

Permite validar facturas electrónicas directamente desde la base de datos de Factusol contra los servicios de ARCA, obteniendo CAE, QR y código de barras de forma automática o manual.

---

## 🚀 Características

### Facturación Electrónica
- **Validación manual** — Seleccionar factura y validar con un click
- **Validación automática** — Loop en background que detecta facturas nuevas (solo del día) y las valida cada 60s
- **Multi punto de venta** — Soporte para múltiples PV ARCA con tipos de comprobante configurables (A, B, C)
- **QR Code AFIP** — Generación automática del QR reglamentario
- **Código de barras AFIP** — Cadena CUIT+TipoCbte+PV+CAE+VtoCae

### Escritura en Factusol (F_FAC)
| Campo | Contenido |
|-------|-----------|
| `BNOFAC` | Número de CAE |
| `PEDFAC` | Nro comprobante ARCA (ej: `B-0002-00000023`) |
| `BIBFAC` | Nro comprobante ARCA (duplicado para impresión) |
| `BNUFAC` | Fecha de vencimiento del CAE |
| `IMGFAC` | Ruta absoluta de la imagen QR |
| `AATFAC` | Código de barras AFIP |
| `REAFAC` | Código de barras AFIP (duplicado) |

### Gestión de Clientes
- Listado completo de clientes con datos fiscales (CUIT, condición IVA, domicilio)
- **Actualización desde Padrón ARCA** — Consulta ARCA y actualiza razón social, domicilio, condición fiscal en Factusol

### CAE Emitidos
- Historial completo de comprobantes validados
- **Filtro por mes** para control mensual
- **Totales por punto de venta** — Cantidad, total facturado, neto gravado, IVA
- **Posición IVA (Débito Fiscal)** — Control mensual del IVA generado

### Panel de Control (Dashboard)
- Estadísticas en tiempo real (facturas del día, CAE emitidos)
- Monitor de estado de servidores ARCA
- Panel de auto-validación con logs en vivo
- Estado por punto de venta

### Usuarios y Seguridad
- Sistema de login con autenticación JWT
- Roles: **admin** (acceso total) y **usuario** (solo sus PV)
- Cada usuario tiene asignados sus puntos de venta

---

## 📦 Multi-Instancia

El sistema soporta **múltiples empresas** en un mismo servidor. Cada instancia usa su propia carpeta con:

```
C:\Empresa_A\
    ARCA.exe          ← Ejecutable (compartido o copiado)
    config.json       ← Configuración de esta empresa
    app_data.db       ← Base de datos local (usuarios, logs CAE)
    certs/            ← Certificados ARCA de esta empresa

C:\Empresa_B\
    ARCA.exe
    config.json       ← Otro CUIT, otro puerto
    app_data.db
    certs/
```

Cada instancia se configura con un **puerto diferente** y un **CUIT diferente**.

---

## ⚙️ Configuración

El archivo `config.json` se crea automáticamente en el directorio de trabajo:

```json
{
  "empresa": {
    "razon_social": "MI EMPRESA S.R.L.",
    "cuit": "20-12345678-9",
    "domicilio": "Av. Siempre Viva 742",
    "inicio_actividades": "2020-01-01",
    "condicion_iva": "Responsable Inscripto"
  },
  "factusol": {
    "db_path": "C:\\Factusol\\Datos\\EMPRESA.mdb"
  },
  "arca": {
    "environment": "production",
    "cert_path": "C:\\certs\\cert.pem",
    "key_path": "C:\\certs\\key.pem"
  },
  "app": {
    "secret_key": "clave-secreta-unica",
    "host": "127.0.0.1",
    "port": 8765
  },
  "auto_validate": {
    "enabled": true,
    "interval_seconds": 60
  }
}
```

### Secciones del config

| Sección | Campo | Descripción |
|---------|-------|-------------|
| `empresa` | `razon_social` | Razón social del emisor |
| `empresa` | `cuit` | CUIT del emisor (con o sin guiones) |
| `empresa` | `condicion_iva` | `Responsable Inscripto`, `Monotributo`, etc. |
| `factusol` | `db_path` | Ruta absoluta al archivo `.mdb` de Factusol |
| `arca` | `environment` | `production` o `development` (homologación) |
| `arca` | `cert_path` | Ruta al certificado `.pem` de ARCA |
| `arca` | `key_path` | Ruta a la clave privada `.pem` |
| `app` | `port` | Puerto HTTP (cambiar para multi-instancia) |
| `app` | `secret_key` | Clave para tokens JWT (cambiar en producción) |
| `auto_validate` | `enabled` | `true`/`false` — auto-validación activa |
| `auto_validate` | `interval_seconds` | Intervalo de chequeo (30-600 segundos) |

---

## 🖥️ Instalación

### Opción 1: Ejecutable (Recomendado)

1. Copiar la carpeta `ARCA/` al servidor donde corre Factusol
2. Ejecutar `ARCA.exe`
3. Se abre la ventana de la aplicación
4. Configurar desde la sección **Configuración** en la app

### Opción 2: Desde código fuente

```bash
# Clonar repositorio
git clone https://github.com/goxtech88/factusol_modulo_arca.git
cd factusol_modulo_arca

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

### Compilar ejecutable

```bash
pip install pyinstaller pywebview
python -m PyInstaller arca.spec --clean --noconfirm
# El resultado queda en dist/ARCA/
```

---

## 🔑 Primer Uso

1. Abrir la app en `http://127.0.0.1:8765`
2. Login: usuario `admin`, contraseña `admin`
3. Ir a **Configuración**:
   - Cargar datos de la empresa (razón social, CUIT)
   - Seleccionar la base de datos de Factusol (`.mdb`)
   - Configurar certificados ARCA
4. Ir a **Usuarios** → crear usuarios y asignar puntos de venta
5. Ir a **Facturas** → validar la primera factura

---

## 📋 Requisitos del Servidor

- **Windows** 10/11 o Server 2016+
- **Factusol** instalado con base de datos Access (`.mdb`)
- **Certificado digital ARCA** válido (`.pem`)
- **Acceso a internet** para comunicación con ARCA
- Puerto HTTP libre (por defecto 8765)

---

## 🏗️ Arquitectura

```
┌──────────────────────────────────────┐
│         Factusol ARCA Sync           │
│   ┌─────────────┐  ┌─────────────┐  │
│   │  PyWebView   │  │   FastAPI    │  │
│   │  (Ventana)   │──│  (Backend)   │  │
│   └─────────────┘  └──────┬──────┘  │
│                            │         │
│   ┌────────────┐  ┌───────┴───────┐ │
│   │  Factusol   │  │  ARCA/AFIP    │ │
│   │  MS Access   │  │  (pyafipws)   │ │
│   └────────────┘  └───────────────┘ │
│                                      │
│   ┌────────────────────────────────┐ │
│   │  SQLite (usuarios, logs CAE)   │ │
│   └────────────────────────────────┘ │
└──────────────────────────────────────┘
```

---

## 📄 Licencia

Propiedad de **GoxTech S.R.L.** — Todos los derechos reservados.

---

*Powered by GoxTech S.R.L.*
