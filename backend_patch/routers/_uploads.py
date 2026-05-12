"""Helper para manejo de uploads — compartido entre routers admin.

Hardening (Fase 4 - Plan 02):
- Whitelist de extensiones por tipo (imágenes / documentos).
- Tamaño máximo configurable via ``MAX_UPLOAD_MB`` (env var, default 10 MB).
- Validación de MIME para imágenes.
- ``validate_upload(file, allowed_exts, max_size_mb=None)`` lanza HTTPException.

Procesamiento de imágenes (agregado):
- ``save_image_upload`` usa Pillow para abrir, optimizar y convertir imágenes.
- Soporta HEIC/HEIF si está instalado ``pillow-heif``.
- Redimensiona automáticamente si la imagen es muy grande.
- Convierte a un formato estándar (PNG con transparencia, JPEG opaco).
- SVG e ICO se guardan como-tal (vectoriales / favicon nativo).
"""
import io
import os
import time
from pathlib import Path
from typing import Iterable, Optional, Set, Tuple

from fastapi import HTTPException, UploadFile

# Pillow (procesamiento de imagenes)
try:
    from PIL import Image, ImageOps, UnidentifiedImageError
    _PIL_OK = True
except ImportError:
    _PIL_OK = False

# Soporte HEIC/HEIF (opcional)
try:
    import pillow_heif  # noqa: F401
    pillow_heif.register_heif_opener()
    _HEIC_OK = True
except ImportError:
    _HEIC_OK = False


# ── Config ────────────────────────────────────────────────────────────────────

MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
MAX_UPLOAD_BYTES: int = MAX_UPLOAD_MB * 1024 * 1024

# Whitelists de extensiones (lowercase, con punto)
ALLOWED_IMAGE_EXTS: Set[str] = {
    ".png", ".jpg", ".jpeg", ".webp", ".svg", ".ico",
    ".gif", ".bmp", ".tif", ".tiff", ".heic", ".heif", ".avif",
}
ALLOWED_DOCUMENT_EXTS: Set[str] = {".pdf", ".zip", ".exe"}
ALLOWED_ANY_EXTS: Set[str] = ALLOWED_IMAGE_EXTS | ALLOWED_DOCUMENT_EXTS

# Extensiones que NO se procesan con Pillow (se guardan tal cual)
_PASSTHROUGH_EXTS: Set[str] = {".svg", ".ico"}

# MIME types aceptados para imágenes
ALLOWED_IMAGE_MIME: Set[str] = {
    "image/png", "image/jpeg", "image/webp", "image/svg+xml",
    "image/x-icon", "image/vnd.microsoft.icon", "image/gif",
    "image/bmp", "image/tiff", "image/heic", "image/heif", "image/avif",
}


# ── Validación ────────────────────────────────────────────────────────────────

def _ext_of(filename: Optional[str]) -> str:
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def validate_upload(
    file: UploadFile,
    allowed_exts: Iterable[str],
    max_size_mb: Optional[int] = None,
) -> bytes:
    """Valida un upload (extensión + tamaño) y devuelve el contenido leído."""
    allowed = {e.lower() for e in allowed_exts}
    ext = _ext_of(file.filename)
    if ext not in allowed:
        pretty = ", ".join(sorted(allowed))
        raise HTTPException(
            status_code=400,
            detail=f"Extension no permitida: '{ext or '(sin extension)'}'. Aceptadas: {pretty}",
        )

    limit_mb = max_size_mb if max_size_mb is not None else MAX_UPLOAD_MB
    limit_bytes = limit_mb * 1024 * 1024

    contents = file.file.read()
    if len(contents) > limit_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Archivo demasiado grande (maximo {limit_mb} MB)",
        )
    return contents


# ── Procesamiento de imagenes ─────────────────────────────────────────────────

def _process_image_with_pillow(
    contents: bytes,
    max_size: Tuple[int, int] = (1920, 1080),
    *,
    target_format: str = "auto",  # 'auto' | 'PNG' | 'JPEG' | 'WEBP'
    jpeg_quality: int = 88,
    background_for_jpeg: Tuple[int, int, int] = (255, 255, 255),
) -> Tuple[bytes, str]:
    """
    Procesa la imagen con Pillow:
      1. Abre el archivo (soporta HEIC si pillow-heif esta presente).
      2. Aplica EXIF rotation (fotos celulares vienen rotadas en metadata).
      3. Redimensiona si excede max_size (manteniendo aspecto, calidad alta).
      4. Convierte al formato target.

    Si target_format='auto':
      - Imagen con alpha (transparencia) -> PNG
      - Sin alpha -> JPEG (mas chico)

    Devuelve (bytes_optimizados, extension_destino).
    """
    if not _PIL_OK:
        # Sin Pillow: devolver tal cual, sin extension forzada.
        return contents, ""

    try:
        img = Image.open(io.BytesIO(contents))
    except (UnidentifiedImageError, Exception) as e:
        raise HTTPException(status_code=400, detail=f"No se pudo leer la imagen: {e}")

    # 1) Corregir rotacion EXIF (iPhone / Android suelen guardar la foto
    # acostada con metadata indicando "rotar al mostrar")
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    # 2) Detectar si tiene alpha (transparencia)
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)

    # 3) Resize si excede max_size (mantiene aspecto)
    if img.width > max_size[0] or img.height > max_size[1]:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

    # 4) Elegir formato target
    if target_format == "auto":
        target_format = "PNG" if has_alpha else "JPEG"

    out = io.BytesIO()
    if target_format == "PNG":
        # Para PNG mantener alpha si la tiene
        if img.mode not in ("RGBA", "P", "L"):
            img = img.convert("RGBA" if has_alpha else "RGB")
        img.save(out, format="PNG", optimize=True)
        ext = ".png"
    elif target_format == "WEBP":
        img.save(out, format="WEBP", quality=jpeg_quality, method=6)
        ext = ".webp"
    else:  # JPEG
        # JPEG no soporta alpha — si la imagen lo tiene, fondear con blanco
        if img.mode in ("RGBA", "LA"):
            bg = Image.new("RGB", img.size, background_for_jpeg)
            bg.paste(img, mask=img.split()[-1])
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
        img.save(out, format="JPEG", quality=jpeg_quality, optimize=True, progressive=True)
        ext = ".jpg"

    return out.getvalue(), ext


def save_image_upload(
    file: UploadFile,
    dest_dir: Path,
    name_prefix: str,
    *,
    max_size: Tuple[int, int] = (1920, 1080),
    target_format: str = "auto",
    max_size_mb: Optional[int] = None,
) -> Path:
    """
    Procesa y guarda una imagen subida. Acepta JPG/PNG/WEBP/GIF/BMP/TIFF/HEIC/AVIF.

    - SVG y ICO se guardan SIN procesar (son vectoriales / favicon nativo).
    - Otros formatos pasan por Pillow: resize + optimize + convert.
    """
    contents = validate_upload(file, ALLOWED_IMAGE_EXTS, max_size_mb=max_size_mb)
    ext_orig = _ext_of(file.filename)

    dest_dir.mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())

    # Passthrough: SVG e ICO se guardan tal cual
    if ext_orig in _PASSTHROUGH_EXTS:
        dest = dest_dir / f"{name_prefix}-{timestamp}{ext_orig}"
        dest.write_bytes(contents)
        return dest

    # Procesar con Pillow
    if not _PIL_OK:
        # Sin Pillow: fallback al comportamiento legacy (guardar tal cual)
        dest = dest_dir / f"{name_prefix}-{timestamp}{ext_orig}"
        dest.write_bytes(contents)
        return dest

    optimized_bytes, ext_final = _process_image_with_pillow(
        contents, max_size=max_size, target_format=target_format,
    )
    dest = dest_dir / f"{name_prefix}-{timestamp}{ext_final}"
    dest.write_bytes(optimized_bytes)
    return dest


# ── Guardado (legacy compat) ──────────────────────────────────────────────────

def save_upload(
    file: UploadFile,
    dest_dir: Path,
    name_prefix: str,
    *,
    only_images: bool = False,
    allowed_exts: Optional[Iterable[str]] = None,
    max_size_mb: Optional[int] = None,
) -> Path:
    """Guarda un archivo subido. Mantiene la firma legacy.

    Si ``only_images=True`` Y Pillow esta disponible, delega a
    ``save_image_upload`` para optimizar/convertir. Para documentos (PDF, ZIP, EXE)
    guarda tal cual.
    """
    if allowed_exts is None:
        allowed_exts = ALLOWED_IMAGE_EXTS if only_images else ALLOWED_ANY_EXTS

    if only_images and _PIL_OK:
        return save_image_upload(file, dest_dir, name_prefix, max_size_mb=max_size_mb)

    # Path legacy para documentos no-imagen (o sin Pillow)
    contents = validate_upload(file, allowed_exts, max_size_mb=max_size_mb)

    if only_images and file.content_type and file.content_type not in ALLOWED_IMAGE_MIME:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo MIME no permitido: {file.content_type}.",
        )

    dest_dir.mkdir(parents=True, exist_ok=True)
    ext = _ext_of(file.filename)
    dest = dest_dir / f"{name_prefix}-{int(time.time())}{ext}"
    dest.write_bytes(contents)
    return dest
