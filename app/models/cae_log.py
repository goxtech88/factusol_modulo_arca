"""
Log de CAE (Código de Autorización Electrónica) emitidos.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from app.database import Base


class CAELog(Base):
    """Registro de cada factura electrónica validada en ARCA."""
    __tablename__ = "cae_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Referencia Factusol
    tipfac = Column(Integer, nullable=False)   # Serie Factusol
    codfac = Column(Integer, nullable=False)   # Nro factura Factusol

    # Referencia ARCA
    punto_venta = Column(Integer, nullable=False)
    tipo_comprobante = Column(Integer, nullable=False)
    voucher_number = Column(Integer, nullable=False)  # Nro comprobante ARCA
    cae = Column(String(20), nullable=False)
    cae_vto = Column(String(10), nullable=False)  # YYYY-MM-DD

    # Montos
    imp_total = Column(Float, nullable=True)
    imp_neto = Column(Float, nullable=True)
    imp_iva = Column(Float, nullable=True)

    # Datos del comprobante
    cliente_nombre = Column(String(200), nullable=True)
    cliente_doc = Column(String(20), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
