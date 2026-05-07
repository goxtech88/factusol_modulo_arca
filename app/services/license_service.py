"""
Verificación de licencias para Factusol ARCA Sync.

Planes:
  - basica:    Gratuito. Validación manual de facturas, un solo usuario admin.
  - completa:  Pago. Auto-validación + gestión multi-usuario.

La verificación se realiza contra el backend de GoxTech usando el CUIT configurado.
El resultado se cachea localmente hasta 7 días para funcionar sin internet.
"""
import httpx
from datetime import datetime, timedelta
from app.config import get_config, save_config

# URL del backend de licencias de GoxTech
_LICENSE_API_URL = "https://goxtech.com.ar/arca_factusol/api/licenses/check"
_CACHE_TTL_DAYS = 7


def _get_cached(cuit: str) -> dict | None:
    """Devuelve el caché si es válido (dentro del TTL) y corresponde al CUIT."""
    config = get_config()
    cache = config.get("_license_cache", {})
    if cache.get("cuit") != cuit:
        return None
    cached_at_str = cache.get("cached_at", "")
    if not cached_at_str:
        return None
    try:
        cached_at = datetime.fromisoformat(cached_at_str)
    except (ValueError, TypeError):
        return None
    if datetime.now() - cached_at > timedelta(days=_CACHE_TTL_DAYS):
        return None
    return cache


def _save_cache(cuit: str, plan: str, active: bool, valid_until: str | None) -> None:
    """Guarda el resultado de la verificación en config.json."""
    config = get_config()
    config["_license_cache"] = {
        "cuit": cuit,
        "plan": plan,
        "active": active,
        "valid_until": valid_until,
        "cached_at": datetime.now().isoformat(),
    }
    save_config(config)


def _get_app_version() -> str:
    """Obtiene la version actual de la app para reportar al backend."""
    try:
        from app.main import app
        return app.version
    except Exception:
        return ""


def _check_online(cuit: str) -> dict | None:
    """
    Consulta el backend de licencias.
    Retorna dict con plan/active/valid_until, o None si no hay conexión.
    Envía la version del cliente para tracking.
    """
    try:
        version = _get_app_version()
        params = {"cuit": cuit}
        if version:
            params["v"] = version
        resp = httpx.get(
            _LICENSE_API_URL,
            params=params,
            timeout=8.0,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def get_license_status() -> dict:
    """
    Retorna el estado de la licencia para el CUIT configurado.

    Campos retornados:
      - plan:        "basica" | "completa"
      - active:      bool
      - valid:       bool (siempre True — la app básica es gratuita)
      - from_cache:  bool
      - valid_until: str | None
      - cuit:        str
      - message:     str
    """
    config = get_config()
    cuit = config.get("empresa", {}).get("cuit", "").replace("-", "").replace(" ", "").strip()

    if not cuit or len(cuit) < 10:
        return {
            "plan": "basica",
            "active": True,
            "valid": True,
            "from_cache": False,
            "valid_until": None,
            "cuit": cuit,
            "message": "Configure el CUIT de la empresa para verificar el plan",
        }

    # 1. Intentar verificación online
    online = _check_online(cuit)
    if online is not None:
        plan = online.get("plan", "basica")
        active = bool(online.get("active", False))
        valid_until = online.get("valid_until")
        _save_cache(cuit, plan, active, valid_until)
        return _build_status(cuit, plan, active, valid_until, from_cache=False)

    # 2. Sin internet — usar caché
    cached = _get_cached(cuit)
    if cached:
        plan = cached.get("plan", "basica")
        active = bool(cached.get("active", False))
        valid_until = cached.get("valid_until")
        return _build_status(cuit, plan, active, valid_until, from_cache=True)

    # 3. Sin internet y sin caché — funciona en modo básico
    return {
        "plan": "basica",
        "active": True,
        "valid": True,
        "from_cache": False,
        "valid_until": None,
        "cuit": cuit,
        "message": "Sin conexión al servidor de licencias — modo básico activo",
    }


def _build_status(cuit: str, plan: str, active: bool, valid_until: str | None, from_cache: bool) -> dict:
    if plan == "completa" and active:
        if valid_until:
            msg = f"Plan Completo activo hasta {valid_until}"
        else:
            msg = "Plan Completo activo"
    elif plan == "completa" and not active:
        msg = "Plan Completo vencido — renovar en goxtech.com.ar"
        plan = "basica"  # trata como básico si venció
        active = True
    else:
        msg = "Plan Básico activo"

    if from_cache:
        msg += " (verificado sin conexión)"

    return {
        "plan": plan,
        "active": active,
        "valid": True,  # la app siempre es usable en modo básico
        "from_cache": from_cache,
        "valid_until": valid_until,
        "cuit": cuit,
        "message": msg,
    }


def is_licensed() -> bool:
    """La app básica siempre está disponible."""
    return True


def has_completa() -> bool:
    """True si el CUIT tiene plan Completo activo (verifica online o desde caché)."""
    status = get_license_status()
    return status["plan"] == "completa" and status["active"]


def can_validate() -> bool:
    """Alias: True si tiene plan Completo (para auto-validación)."""
    return has_completa()


def refresh_license() -> dict:
    """Fuerza una verificación online, ignorando el caché."""
    config = get_config()
    # Borrar caché para forzar re-verificación
    if "_license_cache" in config:
        del config["_license_cache"]
        save_config(config)
    return get_license_status()
