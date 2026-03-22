"""
Configuración del módulo ARCA - Facturación Electrónica AFIP
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

# ─── AFIP / ARCA ───────────────────────────────────────────────────────────────
AFIP_CUIT = os.getenv("AFIP_CUIT", "")          # CUIT del emisor (sin guiones)
AFIP_CERT = os.getenv("AFIP_CERT", str(BASE_DIR / "certs" / "cert.pem"))
AFIP_KEY  = os.getenv("AFIP_KEY",  str(BASE_DIR / "certs" / "key.pem"))

# Entorno: "homo" = homologación/testing | "prod" = producción
AFIP_ENV  = os.getenv("AFIP_ENV", "homo")

WSAA_URLS = {
    "homo": "https://wsaahomo.afip.gov.ar/ws/services/LoginCms",
    "prod": "https://wsaa.afip.gov.ar/ws/services/LoginCms",
}

WSFE_URLS = {
    "homo": "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL",
    "prod": "https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL",
}

PADRON_A4_URLS = {
    "homo": "https://awshomo.afip.gov.ar/sr-padron/ws/personaServiceA4?WSDL",
    "prod": "https://aws.afip.gov.ar/sr-padron/ws/personaServiceA4?WSDL",
}

PADRON_A13_URLS = {
    "homo": "https://awshomo.afip.gov.ar/sr-padron/ws/personaServiceA13?WSDL",
    "prod": "https://aws.afip.gov.ar/sr-padron/ws/personaServiceA13?WSDL",
}

# Servicio de padrón según tipo de persona
PADRON_SERVICE = os.getenv("PADRON_SERVICE", "A13")  # A4 (contrib.) o A13 (completo)

# ─── TOKEN CACHE ───────────────────────────────────────────────────────────────
TOKEN_CACHE_FILE = BASE_DIR / "certs" / "token_wsfe.json"
TOKEN_CACHE_PADRON_FILE = BASE_DIR / "certs" / "token_padron.json"

# ─── FACTUSOL ──────────────────────────────────────────────────────────────────
# Ruta al archivo .mdb de Factusol
FACTUSOL_MDB = os.getenv(
    "FACTUSOL_MDB",
    r"C:\Factusol\Datos\FACTUSOL.MDB"
)

# Driver ODBC para Access
ODBC_DRIVER = os.getenv("ODBC_DRIVER", "Microsoft Access Driver (*.mdb, *.accdb)")

# Intervalo de polling en segundos (modo automático)
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))

# ─── COMPROBANTES ──────────────────────────────────────────────────────────────
# Mapa tipo comprobante Factusol → código AFIP
TIPO_COMPROBANTE_MAP = {
    "FA": 1,    # Factura A
    "FB": 6,    # Factura B
    "FC": 11,   # Factura C
    "FM": 51,   # Factura M
    "NCA": 3,   # Nota de Crédito A
    "NCB": 8,   # Nota de Crédito B
    "NCC": 13,  # Nota de Crédito C
    "NDA": 2,   # Nota de Débito A
    "NDB": 7,   # Nota de Débito B
    "NDC": 12,  # Nota de Débito C
}

# Condiciones de IVA AFIP
CONDICION_IVA = {
    1:  "IVA Responsable Inscripto",
    2:  "IVA Responsable no Inscripto",
    3:  "IVA no Responsable",
    4:  "IVA Sujeto Exento",
    5:  "Consumidor Final",
    6:  "Responsable Monotributo",
    7:  "Sujeto no Categorizado",
    8:  "Importador del Exterior",
    9:  "Cliente del Exterior",
    10: "IVA Liberado – Ley Nº 19.640",
    11: "IVA Responsable Inscripto – Agente de Percepción",
    12: "Pequeño Contribuyente Eventual",
    13: "Monotributista Social",
    14: "Pequeño Contribuyente Eventual Social",
}

# Tipos de documento AFIP
TIPO_DOC = {
    80: "CUIT",
    86: "CUIL",
    96: "DNI",
    99: "Sin identificar/Consumidor Final",
}
