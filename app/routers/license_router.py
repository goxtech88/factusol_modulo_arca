"""
Router de gestion de licencias en el cliente local.

Wizard de primer uso:
  - GET  /api/license/needs-registration  → indica si la empresa no esta registrada todavia
  - POST /api/license/register            → registra al cliente en el backend remoto
                                            (crea License + Lead en CRM) y guarda config local
  - GET  /api/license/status              → estado actual (proxy de license_service)
  - POST /api/license/refresh             → fuerza re-verificacion online (ignora cache)
"""
import logging
import re

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import get_current_user
from app.config import get_config, save_config
from app.models.user import User
from app.services import license_service

router = APIRouter(prefix="/api/license", tags=["license"])
log = logging.getLogger("license")

# URL del endpoint publico de registro en el backend de GoxTech.
_REGISTER_URL = "https://goxtech.com.ar/arca_factusol/api/licenses/free"


# ─── Schemas ────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """Payload del wizard de primer uso."""
    cuit: str
    company_name: str       # Razon social
    email: str              # Email del responsable
    phone: str              # WhatsApp del responsable (sin formato especifico)
    contact_name: str = ""  # Nombre del responsable (opcional, default = company_name)
    condicion_iva: str = "Responsable Inscripto"  # Para guardar en config local


# ─── Helpers ────────────────────────────────────────────────────────────────

def _clean_cuit(cuit: str) -> str:
    """Elimina guiones, espacios y puntos del CUIT. Devuelve solo digitos."""
    if not cuit:
        return ""
    return re.sub(r"\D", "", cuit)


def _is_valid_cuit(cuit: str) -> bool:
    """Valida formato CUIT (11 digitos exactos) + digito verificador."""
    c = _clean_cuit(cuit)
    if len(c) != 11 or not c.isdigit():
        return False
    # Validacion de digito verificador (modulo 11)
    multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    total = sum(int(c[i]) * multipliers[i] for i in range(10))
    expected = 11 - (total % 11)
    if expected == 11:
        expected = 0
    elif expected == 10:
        # CUIT con digito 10 es invalido — no se asignan
        return False
    return int(c[10]) == expected


def _is_valid_email(email: str) -> bool:
    if not email or "@" not in email:
        return False
    parts = email.split("@")
    if len(parts) != 2 or not parts[0] or "." not in parts[1]:
        return False
    return True


# ─── Endpoints ─────────────────────────────────────────────────────────────

@router.get("/needs-registration")
def needs_registration(current_user: User = Depends(get_current_user)):
    """
    Devuelve True SI Y SOLO SI faltan datos basicos en config local (CUIT, email,
    razon social). Si los 3 datos estan completos, asumimos que el cliente ya
    paso por el wizard alguna vez (o cargo los datos manualmente).

    NOTA: el endpoint /licenses/check del backend SIEMPRE devuelve plan='basica'
    aunque el CUIT no este registrado (es retrocompatible). Por eso no podemos
    distinguir confiablemente "no registrado" de "registrado con plan basica"
    desde el cliente. Si el usuario quiere re-registrarse, lo hace manualmente
    desde el boton "Activar licencia" en Configuracion.
    """
    config = get_config()
    empresa = config.get("empresa", {}) or {}
    cuit = _clean_cuit(empresa.get("cuit", ""))
    email = (empresa.get("email", "") or "").strip()
    company = (empresa.get("razon_social", "") or "").strip()

    needs = (
        len(cuit) != 11
        or not email
        or not _is_valid_email(email)
        or not company
    )

    return {
        "needs_registration": needs,
        "has_cuit": bool(cuit),
        "has_email": bool(email),
        "has_company_name": bool(company),
        "current_cuit": cuit,
        "current_email": email,
        "current_company": company,
    }


@router.post("/register")
def register(data: RegisterRequest, current_user: User = Depends(get_current_user)):
    """
    Registra a la empresa en el backend remoto (crea License + Lead en CRM)
    y guarda los datos en config.json local.

    Pasos:
      1. Validar CUIT (11 digitos + digito verificador) y email.
      2. POST al endpoint /licenses/free del backend remoto con todos los datos
         (incluyendo phone y contact_name para que se cree un Lead en CRM).
      3. Si el backend responde 201, guardar datos en config local.
      4. Forzar refresh del cache de licencias para tomar el plan nuevo.
    """
    # ── Validaciones ──
    cuit_clean = _clean_cuit(data.cuit)
    if not _is_valid_cuit(cuit_clean):
        raise HTTPException(status_code=400, detail="CUIT invalido (debe tener 11 digitos y digito verificador correcto)")
    if not _is_valid_email(data.email):
        raise HTTPException(status_code=400, detail="Email invalido")
    if not data.company_name or not data.company_name.strip():
        raise HTTPException(status_code=400, detail="Razon social es obligatoria")
    if not data.phone or len(_clean_cuit(data.phone)) < 8:
        raise HTTPException(status_code=400, detail="Telefono / WhatsApp es obligatorio (minimo 8 digitos)")

    contact = (data.contact_name or "").strip() or data.company_name.strip()

    # ── POST al backend remoto ──
    payload = {
        "cuit": cuit_clean,
        "email": data.email.strip(),
        "company_name": data.company_name.strip(),
        "phone": data.phone.strip(),
        "contact_name": contact,
        "source": "app_registration",
    }
    try:
        resp = httpx.post(_REGISTER_URL, json=payload, timeout=15.0)
    except Exception as e:
        log.error(f"Error de red al registrar CUIT {cuit_clean}: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"No se pudo conectar al servidor de licencias: {e}. Verifique conexion a internet.",
        )

    if resp.status_code not in (200, 201):
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        log.error(f"Backend rechazo registro CUIT {cuit_clean}: HTTP {resp.status_code} - {detail}")
        raise HTTPException(status_code=resp.status_code, detail=f"Backend rechazo el registro: {detail}")

    backend_response = resp.json()
    log.info(f"Registro exitoso CUIT {cuit_clean}: {backend_response}")

    # ── Guardar en config local ──
    config = get_config()
    if "empresa" not in config:
        config["empresa"] = {}
    config["empresa"]["cuit"] = cuit_clean
    config["empresa"]["razon_social"] = data.company_name.strip()
    config["empresa"]["email"] = data.email.strip()
    config["empresa"]["whatsapp"] = data.phone.strip()
    config["empresa"]["contact_name"] = contact
    config["empresa"]["condicion_iva"] = data.condicion_iva or "Responsable Inscripto"

    # Limpiar cache de licencias para que el proximo check pegue al backend
    if "_license_cache" in config:
        del config["_license_cache"]
    save_config(config)

    # Refrescar status (verificacion online ahora)
    status = license_service.get_license_status()

    return {
        "status": "ok",
        "message": backend_response.get("message", "Licencia gratuita activada"),
        "plan": status.get("plan", "basica"),
        "license_status": status,
    }


@router.get("/status")
def status(current_user: User = Depends(get_current_user)):
    """Estado de la licencia actual (proxy a license_service)."""
    return license_service.get_license_status()


@router.post("/refresh")
def refresh(current_user: User = Depends(get_current_user)):
    """Fuerza re-verificacion online ignorando el cache."""
    return license_service.refresh_license()
