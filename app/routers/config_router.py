"""
Router para configuración del sistema (admin only).
Incluye gestión de Punto de Venta del usuario actual (sin requerir plan completa).
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.auth import require_admin, get_current_user
from app.database import get_db
from app.models.user import User, UserPuntoVenta
from app.config import get_config, save_config

router = APIRouter(prefix="/api/config", tags=["config"])


class EmpresaConfig(BaseModel):
    razon_social: Optional[str] = None
    cuit: Optional[str] = None
    domicilio: Optional[str] = None
    inicio_actividades: Optional[str] = None
    condicion_iva: Optional[str] = None
    concepto_facturacion: Optional[int] = None

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
    from app.services import license_service
    lic_status = license_service.get_license_status()
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
        "license": lic_status,
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


@router.post("/license/refresh")
def refresh_license(_admin: User = Depends(require_admin)):
    """Fuerza una re-verificación online de la licencia, ignorando el caché."""
    from app.services import license_service
    status = license_service.refresh_license()
    return status


@router.post("/generate-cert")
def generate_cert(_admin: User = Depends(require_admin)):
    """Genera clave privada (.key) y CSR (.req) para ARCA/AFIP."""
    config = get_config()
    cuit = config.get("empresa", {}).get("cuit", "").replace("-", "").replace(" ", "").strip()
    razon_social = config.get("empresa", {}).get("razon_social", "").strip()

    if not cuit or len(cuit) < 10:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Configure el CUIT de la empresa primero")
    if not razon_social:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Configure la Razón Social de la empresa primero")

    import os
    from cert_gen import generate_key_and_csr

    output_dir = os.path.join(os.getcwd(), "certs")
    try:
        key_path, csr_path = generate_key_and_csr(cuit, razon_social, output_dir)
    except ImportError:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Falta la librería 'cryptography'. Instalar con: pip install cryptography")
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error al generar certificado: {str(e)}")

    # Auto-configurar key_path
    config["arca"]["key_path"] = key_path
    save_config(config)

    # Leer contenido del CSR para copiar
    with open(csr_path, "r") as f:
        csr_content = f.read()

    return {
        "key_path": key_path,
        "csr_path": csr_path,
        "csr_content": csr_content,
    }


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


# ── Punto de Venta del usuario actual ────────────────────────────────────────
# Permite gestionar PVs sin requerir Plan Completa (para plan básico con 1 PV).


class PVConfig(BaseModel):
    nombre: str
    punto_venta: int
    serie_factusol: int
    tipo_comprobante: int = 0  # 0=auto


@router.get("/my-puntos-venta")
def get_my_puntos_venta(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene los puntos de venta del usuario actual."""
    pvs = db.query(UserPuntoVenta).filter(
        UserPuntoVenta.user_id == current_user.id
    ).all()
    return [
        {
            "id": pv.id,
            "nombre": pv.nombre,
            "punto_venta": pv.punto_venta,
            "serie_factusol": pv.serie_factusol,
            "tipo_comprobante": pv.tipo_comprobante,
        }
        for pv in pvs
    ]


@router.post("/my-puntos-venta")
def add_my_punto_venta(
    data: PVConfig,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Agrega un PV al usuario actual. Plan básico: máximo 1 PV."""
    from app.services import license_service

    existing = db.query(UserPuntoVenta).filter(
        UserPuntoVenta.user_id == current_user.id
    ).count()

    if not license_service.has_completa() and existing >= 1:
        raise HTTPException(
            status_code=403,
            detail="El Plan Básico permite 1 punto de venta. Para más, active el Plan Completo en goxtech.com.ar",
        )

    pv = UserPuntoVenta(
        user_id=current_user.id,
        nombre=data.nombre,
        punto_venta=data.punto_venta,
        serie_factusol=data.serie_factusol,
        tipo_comprobante=data.tipo_comprobante,
    )
    db.add(pv)
    db.commit()
    db.refresh(pv)
    return {"id": pv.id, "message": "Punto de venta configurado"}


@router.put("/my-puntos-venta/{pv_id}")
def update_my_punto_venta(
    pv_id: int,
    data: PVConfig,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza un PV del usuario actual."""
    pv = db.query(UserPuntoVenta).filter(
        UserPuntoVenta.id == pv_id,
        UserPuntoVenta.user_id == current_user.id,
    ).first()
    if not pv:
        raise HTTPException(status_code=404, detail="Punto de venta no encontrado")

    pv.nombre = data.nombre
    pv.punto_venta = data.punto_venta
    pv.serie_factusol = data.serie_factusol
    pv.tipo_comprobante = data.tipo_comprobante
    db.commit()
    return {"message": "Punto de venta actualizado"}


@router.delete("/my-puntos-venta/{pv_id}")
def delete_my_punto_venta(
    pv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina un PV del usuario actual."""
    pv = db.query(UserPuntoVenta).filter(
        UserPuntoVenta.id == pv_id,
        UserPuntoVenta.user_id == current_user.id,
    ).first()
    if not pv:
        raise HTTPException(status_code=404, detail="Punto de venta no encontrado")
    db.delete(pv)
    db.commit()
    return {"message": "Punto de venta eliminado"}
