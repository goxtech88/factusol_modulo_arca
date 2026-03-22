"""
WSAA - Web Service de Autenticación y Autorización de AFIP
Gestiona el token y sign necesarios para el resto de los WS.
"""
import json
import base64
import datetime
import logging
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.x509.oid import NameOID
import requests

log = logging.getLogger(__name__)

# Vigencia del TRA en horas (máximo 24)
TRA_VIGENCIA_HS = 12


class WSAAError(Exception):
    pass


class WSAA:
    """
    Cliente del Web Service de Autenticación y Autorización (WSAA).
    Maneja la obtención y caché del token/sign.
    """

    def __init__(self, cert_path: str, key_path: str, wsaa_url: str, cache_file: str, service: str = "wsfe"):
        self.cert_path = Path(cert_path)
        self.key_path  = Path(key_path)
        self.wsaa_url  = wsaa_url
        self.cache_file = Path(cache_file)
        self.service   = service

        self._token = None
        self._sign  = None
        self._expiry = None

        # Intentar cargar desde caché
        self._load_cache()

    # ──────────────────────────────────────────────────────────────────────────
    # Propiedades públicas
    # ──────────────────────────────────────────────────────────────────────────
    @property
    def token(self) -> str:
        self._ensure_valid()
        return self._token

    @property
    def sign(self) -> str:
        self._ensure_valid()
        return self._sign

    # ──────────────────────────────────────────────────────────────────────────
    # Lógica interna
    # ──────────────────────────────────────────────────────────────────────────
    def _ensure_valid(self):
        """Renueva el token si está por vencer o no existe."""
        if self._token and self._sign and self._expiry:
            # Margen de 5 minutos
            if datetime.datetime.now(datetime.timezone.utc) < self._expiry - datetime.timedelta(minutes=5):
                return
        log.info("Obteniendo nuevo token WSAA para '%s'...", self.service)
        self._login()

    def _build_tra(self) -> str:
        """Construye el Ticket de Requerimiento de Acceso (TRA) en XML."""
        now = datetime.datetime.now(datetime.timezone.utc)
        expiry = now + datetime.timedelta(hours=TRA_VIGENCIA_HS)

        unique_id = str(int(now.timestamp()))
        gen_time  = now.strftime("%Y-%m-%dT%H:%M:%S%z")
        # Formato AFIP: +00:00
        gen_time  = gen_time[:-2] + ":" + gen_time[-2:]
        exp_time  = expiry.strftime("%Y-%m-%dT%H:%M:%S%z")
        exp_time  = exp_time[:-2] + ":" + exp_time[-2:]

        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<loginTicketRequest version="1.0">'
            f"<header><uniqueId>{unique_id}</uniqueId>"
            f"<generationTime>{gen_time}</generationTime>"
            f"<expirationTime>{exp_time}</expirationTime></header>"
            f"<service>{self.service}</service>"
            "</loginTicketRequest>"
        )

    def _sign_tra(self, tra_xml: str) -> str:
        """Firma el TRA con el certificado y clave privada. Devuelve CMS en Base64."""
        tra_bytes = tra_xml.encode("utf-8")

        # Cargar clave privada
        with open(self.key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)

        # Cargar certificado
        with open(self.cert_path, "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read())

        # Construir CMS / PKCS7 firmado
        builder = pkcs7.PKCS7SignatureBuilder()
        builder = builder.set_data(tra_bytes)
        builder = builder.add_signer(cert, private_key, hashes.SHA256())

        cms_der = builder.sign(serialization.Encoding.DER, [pkcs7.PKCS7Options.DetachedSignature])
        return base64.b64encode(cms_der).decode()

    def _call_wsaa(self, cms_b64: str) -> dict:
        """Llama al WS WSAA con el CMS firmado y retorna token/sign."""
        body = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
            "<soap:Body>"
            '<loginCms xmlns="http://wsaa.view.sua.dvadac.desein.afip.gov/">'
            f"<in0>{cms_b64}</in0>"
            "</loginCms>"
            "</soap:Body>"
            "</soap:Envelope>"
        )

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "",
        }

        try:
            resp = requests.post(self.wsaa_url, data=body.encode("utf-8"), headers=headers, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise WSAAError(f"Error al conectar con WSAA: {e}") from e

        # Parsear respuesta XML
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.text)
        ns = "http://wsaa.view.sua.dvadac.desein.afip.gov/"

        # Buscar loginCmsReturn (puede estar en distintos namespaces)
        return_node = root.find(".//{%s}loginCmsReturn" % ns)
        if return_node is None:
            # Intento sin namespace
            return_node = root.find(".//loginCmsReturn")
        if return_node is None:
            raise WSAAError(f"Respuesta WSAA inesperada: {resp.text[:500]}")

        ta_xml = return_node.text
        ta_root = ET.fromstring(ta_xml)

        token = ta_root.findtext(".//token")
        sign  = ta_root.findtext(".//sign")
        exp_str = ta_root.findtext(".//expirationTime")

        if not token or not sign:
            raise WSAAError("WSAA no retornó token/sign válidos")

        # Parsear expiración
        expiry = datetime.datetime.fromisoformat(exp_str)
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=datetime.timezone.utc)

        return {"token": token, "sign": sign, "expiry": expiry.isoformat()}

    def _login(self):
        """Ejecuta el flujo completo de autenticación."""
        if not self.cert_path.exists():
            raise WSAAError(f"Certificado no encontrado: {self.cert_path}")
        if not self.key_path.exists():
            raise WSAAError(f"Clave privada no encontrada: {self.key_path}")

        tra = self._build_tra()
        cms = self._sign_tra(tra)
        result = self._call_wsaa(cms)

        self._token  = result["token"]
        self._sign   = result["sign"]
        self._expiry = datetime.datetime.fromisoformat(result["expiry"])

        self._save_cache(result)
        log.info("Token WSAA obtenido. Vence: %s", result["expiry"])

    # ──────────────────────────────────────────────────────────────────────────
    # Caché en disco
    # ──────────────────────────────────────────────────────────────────────────
    def _save_cache(self, data: dict):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load_cache(self):
        if not self.cache_file.exists():
            return
        try:
            with open(self.cache_file) as f:
                data = json.load(f)
            expiry = datetime.datetime.fromisoformat(data["expiry"])
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=datetime.timezone.utc)
            # Solo usar caché si aún es válido
            if datetime.datetime.now(datetime.timezone.utc) < expiry - datetime.timedelta(minutes=5):
                self._token  = data["token"]
                self._sign   = data["sign"]
                self._expiry = expiry
                log.info("Token WSAA cargado desde caché. Vence: %s", data["expiry"])
        except Exception as e:
            log.warning("No se pudo cargar caché WSAA: %s", e)
