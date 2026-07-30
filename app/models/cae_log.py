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

    # Fecha del comprobante efectivamente enviada a ARCA (YYYY-MM-DD). Puede
    # diferir de la FECFAC de Factusol cuando se valida con "usar fecha hoy":
    # AFIP registra esta fecha, mientras que Factusol conserva la fecha original
    # de la operacion. La usa el export RG 1361 / PAMI para que el duplicado
    # coincida con lo que AFIP tiene.
    fecha_cbte = Column(String(10), nullable=True)

    # Montos
    imp_total = Column(Float, nullable=True)
    imp_neto = Column(Float, nullable=True)
    imp_iva = Column(Float, nullable=True)

    # Datos del comprobante
    cliente_nombre = Column(String(200), nullable=True)
    cliente_doc = Column(String(20), nullable=True)

    # Campos especificos para Notas de Credito (nullable para facturas normales)
    motivo = Column(String(50), nullable=True)
    cmp_asoc_tipo = Column(Integer, nullable=True)
    cmp_asoc_pv = Column(Integer, nullable=True)
    cmp_asoc_nro = Column(Integer, nullable=True)

    # Comprobante PROPIO de la NC en Factusol (serie NC + nuevo CODFAC, ver
    # factusol_service.create_credit_note_invoice). tipfac/codfac de arriba
    # siguen apuntando a la FACTURA ORIGINAL -- no confundir. Nullable: solo
    # se completan si el clonado en Factusol se hizo con exito (puede fallar
    # o no aplicar, ej. NC parcial).
    nc_tipfac = Column(Integer, nullable=True)
    nc_codfac = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
