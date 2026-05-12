"""Endpoints públicos /site/* — config, hero slides, reseñas."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import SiteAsset, HeroSlide, Review
from schemas import SiteConfigResponse, ContactInfo, HeroSlideOut, ReviewOut

router = APIRouter(prefix="/site", tags=["site"])

CONTACT_WHATSAPP = "+5493541651038"
CONTACT_EMAIL = "gonzalo@goxtech.com.ar"

# Prefijo que el admin guarda en la DB para que la imagen sea servible desde
# el panel React directamente. El frontend publico (Astro) concatena este
# endpoint con `${API_URL}${path}`, asi que hay que devolver el path SIN ese
# prefijo para que no quede doble-prefijado.
_API_PREFIX = "/arca_factusol/api"


def _strip_api_prefix(path):
    """Quita el prefijo /arca_factusol/api si esta al inicio del path."""
    if not path:
        return None
    if path.startswith(_API_PREFIX):
        return path[len(_API_PREFIX):] or "/"
    return path


@router.get("/config", response_model=SiteConfigResponse)
def get_site_config(db: Session = Depends(get_db)):
    """Devuelve URLs de logos+favicon y datos de contacto. Sin auth."""
    assets = {a.key: a for a in db.query(SiteAsset).filter(SiteAsset.is_active == True).all()}
    return SiteConfigResponse(
        logo_url=_strip_api_prefix(assets["logo_main"].path) if "logo_main" in assets else None,
        logo_dark_url=_strip_api_prefix(assets["logo_dark"].path) if "logo_dark" in assets else None,
        favicon_url=_strip_api_prefix(assets["favicon"].path) if "favicon" in assets else None,
        contact=ContactInfo(whatsapp=CONTACT_WHATSAPP, email=CONTACT_EMAIL),
    )


@router.get("/hero", response_model=list[HeroSlideOut])
def get_hero_slides(db: Session = Depends(get_db)):
    """Lista slides activos ordenados por sort_order."""
    return (
        db.query(HeroSlide)
        .filter(HeroSlide.is_active == True)
        .order_by(HeroSlide.sort_order.asc(), HeroSlide.id.asc())
        .all()
    )


@router.get("/reviews", response_model=list[ReviewOut])
def get_reviews(
    featured: Optional[bool] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista reseñas publicadas. featured=true filtra solo destacadas."""
    q = db.query(Review).filter(Review.is_published == True)
    if featured is True:
        q = q.filter(Review.is_featured == True)
    return q.order_by(Review.created_at.desc()).limit(limit).all()
