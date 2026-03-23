"""
Configuración del sistema.
Lee/escribe config.json en la raíz del proyecto.
"""
import json
import os
from pathlib import Path

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config.json"

DEFAULT_CONFIG = {
    "empresa": {
        "razon_social": "",
        "cuit": "",
        "domicilio": "",
        "inicio_actividades": "",
        "condicion_iva": "Responsable Inscripto",
    },
    "factusol": {
        "db_path": "",
    },
    "arca": {
        "access_token": "",
        "environment": "development",
        "cert_path": "",
        "key_path": "",
    },
    "app": {
        "secret_key": "cambiar-por-una-clave-segura",
        "host": "0.0.0.0",
        "port": 8000,
    },
}


def load_config() -> dict:
    """Carga la configuración desde config.json. Si no existe, crea uno con valores por defecto."""
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
    # Merge con defaults para campos faltantes
    merged = _deep_merge(DEFAULT_CONFIG.copy(), config)
    return merged


def save_config(config: dict) -> None:
    """Guarda la configuración en config.json."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_config() -> dict:
    """Shortcut para obtener la config actual."""
    return load_config()


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge recursivo: override sobreescribe base."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            base[key] = _deep_merge(base[key], value)
        else:
            base[key] = value
    return base
