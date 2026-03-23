"""
Router de administración de usuarios (solo admin).
Requiere licencia válida para funcionar.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.auth import hash_password, require_admin
from app.models.user import User, UserPuntoVenta
from app.services import license_service


def _require_license():
    """Verifica que la licencia sea válida antes de operar."""
    if not license_service.is_licensed():
        raise HTTPException(
            status_code=403,
            detail="Licencia no válida. Ingrese una clave de licencia válida en Configuración.",
        )


router = APIRouter(prefix="/api/users", tags=["users"], dependencies=[Depends(_require_license)])


# --- Schemas ---

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "user"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class PuntoVentaCreate(BaseModel):
    nombre: str
    punto_venta: int
    serie_factusol: int
    tipo_comprobante: int = 0  # 0=auto

class PuntoVentaUpdate(BaseModel):
    nombre: Optional[str] = None
    punto_venta: Optional[int] = None
    serie_factusol: Optional[int] = None
    tipo_comprobante: Optional[int] = None


# --- Endpoints ---

@router.get("")
def list_users(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "puntos_venta": [
                {
                    "id": pv.id,
                    "nombre": pv.nombre,
                    "punto_venta": pv.punto_venta,
                    "serie_factusol": pv.serie_factusol,
                    "tipo_comprobante": pv.tipo_comprobante,
                }
                for pv in u.puntos_venta
            ],
        }
        for u in users
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "message": "Usuario creado"}


@router.put("/{user_id}")
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password:
        user.password_hash = hash_password(data.password)

    db.commit()
    return {"message": "Usuario actualizado"}


@router.delete("/{user_id}")
def deactivate_user(user_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.is_active = False
    db.commit()
    return {"message": "Usuario desactivado"}


# --- Puntos de Venta ---

@router.post("/{user_id}/puntos-venta", status_code=status.HTTP_201_CREATED)
def add_punto_venta(
    user_id: int,
    data: PuntoVentaCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    pv = UserPuntoVenta(
        user_id=user_id,
        nombre=data.nombre,
        punto_venta=data.punto_venta,
        serie_factusol=data.serie_factusol,
        tipo_comprobante=data.tipo_comprobante,
    )
    db.add(pv)
    db.commit()
    db.refresh(pv)
    return {"id": pv.id, "message": "Punto de venta asignado"}


@router.put("/{user_id}/puntos-venta/{pv_id}")
def update_punto_venta(
    user_id: int,
    pv_id: int,
    data: PuntoVentaUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    pv = db.query(UserPuntoVenta).filter(
        UserPuntoVenta.id == pv_id, UserPuntoVenta.user_id == user_id
    ).first()
    if not pv:
        raise HTTPException(status_code=404, detail="Punto de venta no encontrado")

    if data.nombre is not None:
        pv.nombre = data.nombre
    if data.punto_venta is not None:
        pv.punto_venta = data.punto_venta
    if data.serie_factusol is not None:
        pv.serie_factusol = data.serie_factusol
    if data.tipo_comprobante is not None:
        pv.tipo_comprobante = data.tipo_comprobante

    db.commit()
    return {"message": "Punto de venta actualizado"}


@router.delete("/{user_id}/puntos-venta/{pv_id}")
def remove_punto_venta(
    user_id: int,
    pv_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    pv = db.query(UserPuntoVenta).filter(
        UserPuntoVenta.id == pv_id, UserPuntoVenta.user_id == user_id
    ).first()
    if not pv:
        raise HTTPException(status_code=404, detail="Punto de venta no encontrado")
    db.delete(pv)
    db.commit()
    return {"message": "Punto de venta eliminado"}
