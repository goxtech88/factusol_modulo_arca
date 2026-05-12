from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Integer, BigInteger, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class License(Base):
    __tablename__ = "licenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cuit: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(20), default="completa")  # basica | monthly | completa
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    valid_until: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payment_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    app_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Version(Base):
    __tablename__ = "versions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    version_number: Mapped[str] = mapped_column(String(20), nullable=False)   # "1.2.3"
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)    # "ARCA Sync v1.2.3"
    plan: Mapped[str] = mapped_column(String(20), default="basica")           # "basica" | "completa" | "all"
    filename: Mapped[str] = mapped_column(String(200), nullable=False)        # "arca_sync_v1.2.3.zip"
    file_size: Mapped[int] = mapped_column(BigInteger, default=0)             # bytes
    changelog: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[str] = mapped_column(String(500), nullable=False)


# ═══════════════════════════════════════════════════════════════════════
# Modelos nuevos — Plataforma Unificada Goxtech
# ═══════════════════════════════════════════════════════════════════════


class SiteAsset(Base):
    """Assets del sitio público: logo principal, logo dark, favicon."""
    __tablename__ = "site_assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)  # 'logo_main' | 'logo_dark' | 'favicon'
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_size: Mapped[int] = mapped_column(BigInteger, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HeroSlide(Base):
    """Slides del hero banner del sitio público."""
    __tablename__ = "hero_slides"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cta_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cta_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Download(Base):
    """Archivos disponibles para descarga + metadatos tecnicos del producto.

    Se usa para landings de productos (Modulo ARCA, Tableros Power BI, etc):
    cada landing levanta del backend las screenshots, el video demo, los
    requisitos del sistema y el mensaje custom de WhatsApp asociado al
    producto, sin necesidad de hardcodear nada en el HTML estatico.
    """
    __tablename__ = "downloads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), index=True, default="otros")  # instaladores | addons | plantillas | otros
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)  # nombre Lucide icon
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_size: Mapped[int] = mapped_column(BigInteger, default=0)
    downloads_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_login: Mapped[bool] = mapped_column(Boolean, default=False)
    # ── Evidencia tecnica (Goxtech v2) ──
    # URL del video demo (YouTube embed o MP4 self-hosted). Si null, no muestra.
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # JSON array de URLs de screenshots. Ej: ["/arca_factusol/api/uploads/screenshots/cae.png", ...]
    screenshots_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Texto libre con requisitos del sistema (markdown / multilinea).
    # Ej: "- Factusol Evolution 2020+\n- Certificado .p12\n- .NET Framework 4.7.2"
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Mensaje pre-cargado para el boton WhatsApp del producto.
    # Ej: "Hola! Quiero informacion sobre el Modulo ARCA para Factusol."
    whatsapp_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Tagline corto para landing (1 linea). Ej: "Inyeccion de CAE en Factusol en 10 segundos"
    tagline: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Review(Base):
    """Reseñas de clientes mostradas en el sitio público."""
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[str | None] = mapped_column(String(150), nullable=True)
    rating: Mapped[int] = mapped_column(Integer, default=5)  # 1..5
    text: Mapped[str] = mapped_column(Text, nullable=False)
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Lead(Base):
    """Leads del mini CRM — formulario de contacto, WhatsApp, registro de app, etc."""
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # CUIT del lead - correlaciona con tabla `licenses` cuando el lead se origino
    # desde el registro de la app (source='app_registration').
    cuit: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)  # web_contact | whatsapp | manual | app_registration
    stage: Mapped[str] = mapped_column(String(30), default="Nuevo", index=True)  # Nuevo|Contactado|Calificado|Propuesta|Ganado|Perdido
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_action_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    owner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    events = relationship("LeadEvent", back_populates="lead", cascade="all, delete-orphan")


class LeadEvent(Base):
    """Historial de eventos de un lead — audit trail del CRM."""
    __tablename__ = "lead_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'created' | 'stage_changed' | 'note_added' | 'whatsapp_in'
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON serializado
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    lead = relationship("Lead", back_populates="events")

