"""
Modelos de usuario y configuración de punto de venta.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="user")  # "admin" o "user"
    is_active = Column(Boolean, default=True)

    # Relación: un usuario puede tener varios puntos de venta asignados
    puntos_venta = relationship("UserPuntoVenta", back_populates="user", cascade="all, delete-orphan")


class UserPuntoVenta(Base):
    """
    Mapeo usuario → serie Factusol + punto de venta ARCA.
    El CUIT y certificados son a nivel empresa (config.json).
    """
    __tablename__ = "user_puntos_venta"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nombre = Column(String(100), nullable=False)  # Ej: "Sucursal Centro", "Casa Matriz"
    punto_venta = Column(Integer, nullable=False)  # Punto de venta ARCA (1, 2, 3...)
    serie_factusol = Column(Integer, nullable=False)  # TIPFAC en Factusol (1-9)
    tipo_comprobante = Column(Integer, nullable=False, default=0)  # 0=auto, 1=Fac A, 6=Fac B, 11=Fac C

    user = relationship("User", back_populates="puntos_venta")
