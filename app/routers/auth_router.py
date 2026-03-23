"""
Router de autenticación.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.auth import verify_password, create_access_token, get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado",
        )

    token = create_access_token(data={"sub": user.id})
    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "puntos_venta": [
                {
                    "id": pv.id,
                    "nombre": pv.nombre,
                    "punto_venta": pv.punto_venta,
                    "serie_factusol": pv.serie_factusol,
                    "tipo_comprobante": pv.tipo_comprobante,
                }
                for pv in user.puntos_venta
            ],
        },
    )


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "puntos_venta": [
            {
                "id": pv.id,
                "nombre": pv.nombre,
                "punto_venta": pv.punto_venta,
                "serie_factusol": pv.serie_factusol,
                "tipo_comprobante": pv.tipo_comprobante,
            }
            for pv in current_user.puntos_venta
        ],
    }
