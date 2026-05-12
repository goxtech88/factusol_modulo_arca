"""Admin CRUD para SiteAsset y HeroSlide con upload de imagenes optimizadas."""
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from database import get_db
from auth_utils import require_admin_jwt
from models import SiteAsset, HeroSlide
from schemas import SiteAssetOut, SiteAssetIn, HeroSlideOut, HeroSlideIn
from routers._uploads import save_image_upload

UPLOADS_SITE = Path("uploads/site")
UPLOADS_HERO = Path("uploads/hero")

# Tamanos maximos por tipo de asset (mantiene aspecto, no expande)
ASSET_MAX_SIZES = {
    "logo_main": (800, 800),    # logo principal — usado en cabecera
    "logo_dark": (800, 800),    # variante para fondos oscuros
    "favicon":   (256, 256),    # favicon — el browser lo va a re-escalar a 16/32/48
}

# Prefijo de URL publico que el frontend usa para servir los uploads.
# Nginx routea /arca_factusol/api/ -> backend FastAPI :8001, y el backend monta
# /uploads como static (ver main.py). Resultado:
#   GET /arca_factusol/api/uploads/site/logo_main-XXX.png -> archivo en disco.
PUBLIC_UPLOAD_PREFIX = "/arca_factusol/api/uploads"


def _to_public_url(dest: Path) -> str:
    """Convierte path local 'uploads/site/foo.png' a URL publica."""
    rel = dest.as_posix()
    if rel.startswith("uploads/"):
        rel = rel[len("uploads/"):]
    return f"{PUBLIC_UPLOAD_PREFIX}/{rel}"


router = APIRouter(prefix="/admin/site", tags=["admin"], dependencies=[Depends(require_admin_jwt)])


# ── SiteAsset ──

@router.get("/assets", response_model=list[SiteAssetOut])
def list_assets(db: Session = Depends(get_db)):
    return db.query(SiteAsset).order_by(SiteAsset.key.asc()).all()


@router.post("/assets", response_model=SiteAssetOut, status_code=201)
def create_asset(data: SiteAssetIn, db: Session = Depends(get_db)):
    existing = db.query(SiteAsset).filter(SiteAsset.key == data.key).first()
    if existing:
        existing.path = data.path
        existing.alt_text = data.alt_text
        existing.is_active = data.is_active
        db.commit()
        db.refresh(existing)
        return existing
    asset = SiteAsset(key=data.key, path=data.path, alt_text=data.alt_text, is_active=data.is_active)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.put("/assets/{asset_id}", response_model=SiteAssetOut)
def update_asset(asset_id: int, data: SiteAssetIn, db: Session = Depends(get_db)):
    asset = db.query(SiteAsset).filter(SiteAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset no encontrado")
    asset.key = data.key
    asset.path = data.path
    asset.alt_text = data.alt_text
    asset.is_active = data.is_active
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/assets/{asset_id}", status_code=204)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(SiteAsset).filter(SiteAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset no encontrado")
    db.delete(asset)
    db.commit()


@router.post("/assets/upload", response_model=SiteAssetOut)
def upload_asset(
    key: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Sube logo principal / oscuro / favicon. El archivo se procesa con Pillow:
    se aplica EXIF rotation, se redimensiona al maximo del tipo, se optimiza,
    y se convierte a PNG (con alpha si la imagen lo tiene) o JPEG (sin alpha).
    Acepta JPG, PNG, WEBP, GIF, BMP, TIFF, HEIC, AVIF, SVG, ICO.
    """
    if key not in ("logo_main", "logo_dark", "favicon"):
        raise HTTPException(status_code=400, detail="Key invalida. Opciones: logo_main, logo_dark, favicon")

    max_size = ASSET_MAX_SIZES.get(key, (1024, 1024))
    # Para favicon priorizamos PNG con alpha (no convertir a JPEG aunque sea opaco)
    target = "PNG" if key == "favicon" else "auto"

    dest = save_image_upload(file, UPLOADS_SITE, key, max_size=max_size, target_format=target)
    public_url = _to_public_url(dest)

    existing = db.query(SiteAsset).filter(SiteAsset.key == key).first()
    if existing:
        existing.path = public_url
        existing.content_type = file.content_type
        existing.file_size = dest.stat().st_size
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing

    asset = SiteAsset(
        key=key, path=public_url, alt_text="Goxtech",
        content_type=file.content_type, file_size=dest.stat().st_size, is_active=True,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


# ── HeroSlide ──

@router.get("/hero", response_model=list[HeroSlideOut])
def list_hero_slides(db: Session = Depends(get_db)):
    return db.query(HeroSlide).order_by(HeroSlide.sort_order.asc(), HeroSlide.id.asc()).all()


@router.post("/hero", response_model=HeroSlideOut, status_code=201)
def create_hero_slide(data: HeroSlideIn, db: Session = Depends(get_db)):
    slide = HeroSlide(**data.model_dump())
    db.add(slide)
    db.commit()
    db.refresh(slide)
    return slide


@router.put("/hero/{slide_id}", response_model=HeroSlideOut)
def update_hero_slide(slide_id: int, data: HeroSlideIn, db: Session = Depends(get_db)):
    slide = db.query(HeroSlide).filter(HeroSlide.id == slide_id).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide no encontrado")
    for k, v in data.model_dump().items():
        setattr(slide, k, v)
    db.commit()
    db.refresh(slide)
    return slide


@router.delete("/hero/{slide_id}", status_code=204)
def delete_hero_slide(slide_id: int, db: Session = Depends(get_db)):
    slide = db.query(HeroSlide).filter(HeroSlide.id == slide_id).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide no encontrado")
    db.delete(slide)
    db.commit()


@router.post("/hero/upload-image")
def upload_hero_image(
    slide_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    slide = db.query(HeroSlide).filter(HeroSlide.id == slide_id).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide no encontrado")
    # Hero banners: hasta 1920x1080, JPEG para tamano chico
    dest = save_image_upload(file, UPLOADS_HERO, f"slide-{slide_id}", max_size=(1920, 1080))
    slide.image_path = _to_public_url(dest)
    db.commit()
    return {"image_path": slide.image_path}
