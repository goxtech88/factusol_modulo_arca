"""
Validación de licencias para Factusol ARCA Sync.
"""
import hmac
import hashlib
from app.config import get_config

# Misma clave secreta que el generador
_LICENSE_SECRET = "GoxTech-ARCA-Sync-2026-SecretKey"


def _generate_expected(cuit: str) -> str:
    """Genera la clave esperada para un CUIT."""
    cuit_clean = cuit.replace("-", "").replace(" ", "").strip()
    sig = hmac.new(
        _LICENSE_SECRET.encode(),
        cuit_clean.encode(),
        hashlib.sha256,
    ).hexdigest().upper()
    return f"{sig[:4]}-{sig[4:8]}-{sig[8:12]}-{sig[12:16]}"


def is_licensed() -> bool:
    """Verifica si la instancia tiene una licencia válida."""
    config = get_config()
    cuit = config.get("empresa", {}).get("cuit", "")
    license_key = config.get("license", {}).get("key", "")

    if not cuit or not license_key:
        return False

    cuit_clean = cuit.replace("-", "").replace(" ", "").strip()
    if len(cuit_clean) < 10:
        return False

    try:
        expected = _generate_expected(cuit_clean)
        return license_key.strip().upper() == expected.upper()
    except Exception:
        return False


def get_license_status() -> dict:
    """Retorna el estado de la licencia."""
    config = get_config()
    cuit = config.get("empresa", {}).get("cuit", "")
    license_key = config.get("license", {}).get("key", "")
    valid = is_licensed()

    return {
        "valid": valid,
        "cuit": cuit,
        "has_key": bool(license_key),
        "message": "Licencia válida" if valid else "Licencia no válida — Panel de Usuarios bloqueado",
    }
