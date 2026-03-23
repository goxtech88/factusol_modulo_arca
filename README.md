# Factusol Módulo ARCA

Módulo web de facturación electrónica ARCA (ex-AFIP) para Factusol.

## Características

- 🔗 **Conexión directa** a la base de datos Factusol (MS Access)
- 📄 **Factura electrónica** via ARCA/AFIP usando [AFIP SDK](https://afipsdk.com)
- 👥 **Multi-usuario** con puntos de venta y series independientes
- 🔒 **Autenticación JWT** con roles (admin/usuario)
- 🌐 **Interfaz web** moderna y responsive
- ⚙️ **Configuración** desde la UI (sin editar archivos)

## Requisitos

- Python 3.11+
- Microsoft Access Database Engine (ODBC driver)
- Access Token de [AFIP SDK](https://app.afipsdk.com)

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/goxtech88/factusol_modulo_arca.git
cd factusol_modulo_arca

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar el servidor
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Primer Uso

1. Abrir `http://localhost:8000` en el navegador
2. Login con **admin** / **admin**
3. Ir a **Configuración** y completar:
   - Datos de empresa (CUIT, razón social)
   - Ruta a la base de datos Factusol
   - Access Token de AFIP SDK
4. Ir a **Usuarios** y crear usuarios con sus puntos de venta y series

## Estructura

```
app/
├── main.py              # Entry point FastAPI
├── config.py            # Configuración JSON
├── database.py          # SQLAlchemy / SQLite
├── auth.py              # JWT Authentication
├── models/              # User, UserPuntoVenta, CAELog
├── routers/             # API endpoints
├── services/            # Factusol (pyodbc) + ARCA (afip.py)
└── static/              # Frontend SPA
```
