"""
Router para configuración del sistema (admin only).
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.auth import require_admin
from app.models.user import User
from app.config import get_config, save_config

router = APIRouter(prefix="/api/config", tags=["config"])


class EmpresaConfig(BaseModel):
    razon_social: Optional[str] = None
    cuit: Optional[str] = None
    domicilio: Optional[str] = None
    inicio_actividades: Optional[str] = None
    condicion_iva: Optional[str] = None

class FactusolConfig(BaseModel):
    db_path: Optional[str] = None

class ArcaConfig(BaseModel):
    access_token: Optional[str] = None
    environment: Optional[str] = None
    cert_path: Optional[str] = None
    key_path: Optional[str] = None


@router.get("")
def get_configuration(_admin: User = Depends(require_admin)):
    """Obtiene la configuración actual."""
    config = get_config()
    # No exponer secret_key
    safe = {
        "empresa": config.get("empresa", {}),
        "factusol": config.get("factusol", {}),
        "arca": {
            **config.get("arca", {}),
            "access_token": "***" if config.get("arca", {}).get("access_token") else "",
        },
        "app": {
            "host": config.get("app", {}).get("host", "0.0.0.0"),
            "port": config.get("app", {}).get("port", 8000),
        },
    }
    return safe


@router.put("/empresa")
def update_empresa(data: EmpresaConfig, _admin: User = Depends(require_admin)):
    config = get_config()
    for key, val in data.model_dump(exclude_none=True).items():
        config["empresa"][key] = val
    save_config(config)
    return {"message": "Configuración de empresa actualizada"}


@router.put("/factusol")
def update_factusol(data: FactusolConfig, _admin: User = Depends(require_admin)):
    config = get_config()
    for key, val in data.model_dump(exclude_none=True).items():
        config["factusol"][key] = val
    save_config(config)
    return {"message": "Configuración de Factusol actualizada"}


@router.put("/arca")
def update_arca(data: ArcaConfig, _admin: User = Depends(require_admin)):
    config = get_config()
    for key, val in data.model_dump(exclude_none=True).items():
        config["arca"][key] = val
    save_config(config)
    return {"message": "Configuración de ARCA actualizada"}


@router.get("/browse-dialog")
def browse_dialog(
    extensions: str = "",
    title: str = "Seleccionar archivo",
    _admin: User = Depends(require_admin),
):
    """
    Abre el diálogo de selección de archivos nativo del SO (Windows Explorer).
    Funciona porque el servidor corre localmente en la misma máquina.
    Retorna el path del archivo seleccionado.
    """
    import tkinter as tk
    from tkinter import filedialog

    result = {"path": ""}

    def _open():
        root = tk.Tk()
        root.withdraw()                       # ocultar la ventana principal
        root.wm_attributes("-topmost", 1)     # traer al frente

        filetypes = [("Todos los archivos", "*.*")]
        if extensions:
            exts = [e.strip().lstrip(".") for e in extensions.split(",") if e.strip()]
            if exts:
                pattern = " ".join(f"*.{e}" for e in exts)
                filetypes = [(f"Archivos compatibles ({pattern})", pattern),
                             ("Todos los archivos", "*.*")]

        path = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes,
            parent=root,
        )
        result["path"] = path or ""
        root.destroy()

    _open()
    return {"path": result["path"]}


def browse_files(
    path: str = "",
    extensions: str = "",
    _admin: User = Depends(require_admin),
):
    """Browse server filesystem for file selection."""
    import os
    from pathlib import Path

    # Default to common starting points
    if not path:
        # List drives on Windows, or root on Linux
        if os.name == "nt":
            import string
            drives = []
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append({"name": f"{letter}:", "path": drive, "is_dir": True})
            return {"current": "", "parent": "", "items": drives}
        else:
            path = "/"

    target = Path(path)
    if not target.exists() or not target.is_dir():
        return {"current": str(path), "parent": str(Path(path).parent), "items": [], "error": "Directorio no encontrado"}

    ext_filter = [e.strip().lower() for e in extensions.split(",") if e.strip()] if extensions else []

    items = []
    try:
        for entry in sorted(target.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
            try:
                if entry.name.startswith("."):
                    continue
                if entry.is_dir():
                    items.append({"name": entry.name, "path": str(entry), "is_dir": True})
                else:
                    if ext_filter:
                        if entry.suffix.lower().lstrip(".") in ext_filter:
                            items.append({"name": entry.name, "path": str(entry), "is_dir": False})
                    else:
                        items.append({"name": entry.name, "path": str(entry), "is_dir": False})
            except PermissionError:
                continue
    except PermissionError:
        return {"current": str(target), "parent": str(target.parent), "items": [], "error": "Acceso denegado"}

    return {
        "current": str(target),
        "parent": str(target.parent) if target.parent != target else "",
        "items": items[:200],  # Limit results
    }
