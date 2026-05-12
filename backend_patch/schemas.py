"""Modelos Pydantic Request/Response para los endpoints nuevos de la plataforma unificada.

Hardening (Fase 4 - Plan 02):
- ``Field(max_length=N)`` en strings para evitar payloads abusivos.
- ``EmailStr`` (vía email-validator) en campos de email.
- Regex de CUIT (``^\\d{11}$``) en leads admin.
- ``Field(ge=1, le=5)`` en rating de reviews.
- ``HttpUrl`` en URLs (CTA de hero slides).
"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


# ── /site/config ──

class ContactInfo(BaseModel):
    whatsapp: str = Field(..., max_length=32)
    email: str = Field(..., max_length=200)


class SiteConfigResponse(BaseModel):
    logo_url: Optional[str] = None
    logo_dark_url: Optional[str] = None
    favicon_url: Optional[str] = None
    contact: ContactInfo


# ── HeroSlide ──

class HeroSlideOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    subtitle: Optional[str] = None
    image_path: Optional[str] = None
    cta_text: Optional[str] = None
    cta_url: Optional[str] = None
    sort_order: int
    is_active: bool


class HeroSlideIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    subtitle: Optional[str] = Field(default=None, max_length=500)
    image_path: Optional[str] = Field(default=None, max_length=500)
    cta_text: Optional[str] = Field(default=None, max_length=80)
    # Permitimos URLs absolutas o paths relativos del propio sitio (ej: "/contacto").
    cta_url: Optional[str] = Field(default=None, max_length=500)
    sort_order: int = 0
    is_active: bool = True


# ── SiteAsset ──

class SiteAssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    key: str
    path: str
    alt_text: Optional[str] = None
    content_type: Optional[str] = None
    file_size: int
    is_active: bool


class SiteAssetIn(BaseModel):
    key: Literal["logo_main", "logo_dark", "favicon"]
    path: str = Field(..., max_length=500)
    alt_text: Optional[str] = Field(default=None, max_length=200)
    is_active: bool = True


# ── Download ──

class DownloadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    title: str
    category: str
    version: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    file_size: int
    downloads_count: int
    is_active: bool
    requires_login: bool
    # Evidencia tecnica (Goxtech v2)
    video_url: Optional[str] = None
    screenshots_json: Optional[str] = None  # JSON array as string
    requirements: Optional[str] = None
    whatsapp_message: Optional[str] = None
    tagline: Optional[str] = None


class DownloadIn(BaseModel):
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9][a-z0-9\-]*$")
    title: str = Field(..., min_length=1, max_length=200)
    category: str = Field(default="otros", max_length=50)
    version: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=2000)
    icon: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = True
    requires_login: bool = False
    # Evidencia tecnica (Goxtech v2) - todos opcionales para no romper integraciones existentes
    video_url: Optional[str] = Field(default=None, max_length=500)
    screenshots_json: Optional[str] = Field(default=None, max_length=5000)
    requirements: Optional[str] = Field(default=None, max_length=3000)
    whatsapp_message: Optional[str] = Field(default=None, max_length=500)
    tagline: Optional[str] = Field(default=None, max_length=200)


# ── Review ──

class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    company: Optional[str] = None
    industry: Optional[str] = None
    role: Optional[str] = None
    rating: int
    text: str
    photo_path: Optional[str] = None
    is_published: bool
    is_featured: bool
    created_at: datetime


class ReviewIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    company: Optional[str] = Field(default=None, max_length=200)
    industry: Optional[str] = Field(default=None, max_length=80)
    role: Optional[str] = Field(default=None, max_length=100)
    rating: int = Field(default=5, ge=1, le=5)
    text: str = Field(..., min_length=1, max_length=5000)
    photo_path: Optional[str] = Field(default=None, max_length=500)
    is_published: bool = False
    is_featured: bool = False


# ── Lead + LeadEvent ──

LeadStage = Literal["Nuevo", "Contactado", "Calificado", "Propuesta", "Ganado", "Perdido"]

# CUIT argentino: 11 dígitos exactos (sin guiones — el cliente puede mandar con
# guiones pero recomendamos limpiar antes; ver `_clean_cuit` en main.py).
CUIT_REGEX = r"^\d{11}$"


class LeadIn(BaseModel):
    """Payload del formulario público de contacto.

    Para evitar fricción en el form web, ``email`` usa ``EmailStr`` solo si se
    completa (es opcional) y los textos tienen ``max_length`` razonables.
    """
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=40)
    email: Optional[EmailStr] = None
    company: Optional[str] = Field(default=None, max_length=200)
    industry: Optional[str] = Field(default=None, max_length=80)
    # CUIT opcional — se completa cuando el lead viene de un registro de licencia.
    cuit: Optional[str] = Field(default=None, max_length=20)
    source: Optional[str] = Field(default="web_contact", max_length=50)
    notes: Optional[str] = Field(default=None, max_length=5000)


class LeadAdminIn(LeadIn):
    """Payload del CRM admin: extiende LeadIn con stage / next_action / owner."""
    stage: LeadStage = "Nuevo"
    next_action_at: Optional[datetime] = None
    owner: Optional[str] = Field(default=None, max_length=80)


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    cuit: Optional[str] = None
    source: Optional[str] = None
    stage: str
    notes: Optional[str] = None
    next_action_at: Optional[datetime] = None
    owner: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class LeadEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    lead_id: int
    type: str
    payload_json: Optional[str] = None
    created_at: datetime


class LeadCreatedResponse(BaseModel):
    id: int
    stage: str
