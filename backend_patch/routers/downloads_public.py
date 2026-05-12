"""Endpoints públicos /downloads — catálogo y descarga de archivos."""
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Download
from schemas import DownloadOut

router = APIRouter(prefix="/downloads", tags=["downloads"])


@router.get("", response_model=list[DownloadOut])
def list_downloads(
    category: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Lista descargas activas, filtrable por categoría."""
    q = db.query(Download).filter(Download.is_active == True)
    if category:
        q = q.filter(Download.category == category)
    return q.order_by(Download.title.asc()).all()


@router.get("/by-slug/{slug}", response_model=DownloadOut)
def get_download_by_slug(slug: str, db: Session = Depends(get_db)):
    """
    Detalle completo de un producto por slug (sin auth). Lo usan las landings
    de producto para renderizar video demo, screenshots, requisitos tecnicos
    y mensaje custom de WhatsApp. Ej: GET /downloads/by-slug/modulo-arca.
    """
    d = db.query(Download).filter(
        Download.slug == slug,
        Download.is_active == True,
    ).first()
    if not d:
        raise HTTPException(status_code=404, detail=f"Producto '{slug}' no encontrado")
    return d


@router.get("/file/{download_id}")
def download_file(download_id: int, db: Session = Depends(get_db)):
    """Sirve el archivo de descarga y aumenta el contador."""
    d = db.query(Download).filter(Download.id == download_id, Download.is_active == True).first()
    if not d or not d.file_path:
        raise HTTPException(status_code=404, detail="Descarga no encontrada")
    file_path = Path(d.file_path)
    if not file_path.is_absolute():
        file_path = Path.cwd() / d.file_path.lstrip("/")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no disponible")
    d.downloads_count = (d.downloads_count or 0) + 1
    db.commit()
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream",
    )
