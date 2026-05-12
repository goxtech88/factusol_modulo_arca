"""
Backend de licencias — GoxTech ARCA Sync
=========================================
Endpoints públicos:
  GET  /licenses/check                → verifica plan de un CUIT
  GET  /licenses/prices               → precios de todos los planes (ARS + USD)
  POST /licenses/free                 → registro plan Gratis (email + CUIT + empresa)
  POST /licenses/checkout             → crea preferencia MercadoPago (plan Vitalicio)
  POST /licenses/subscribe            → crea suscripción MercadoPago (plan Mensual)
  POST /licenses/mp-webhook           → webhook MercadoPago pagos únicos
  POST /licenses/mp-subscription-webhook → webhook MercadoPago suscripciones
  GET  /versions/latest               → versión más reciente para descarga
  GET  /downloads/{filename}          → descarga archivo

Panel admin (requiere header x-admin-token):
  GET  /admin/stats                   → dashboard
  GET  /admin/licenses                → lista licencias (filtro por plan/search)
  POST /admin/licenses                → crear/actualizar licencia manual
  PUT  /admin/licenses/{cuit}         → editar licencia
  DELETE /admin/licenses/{cuit}       → desactivar licencia
  GET  /admin/settings                → configuración de precios
  PUT  /admin/settings                → actualizar precios
  POST /admin/settings/create-mp-plan → crear plan de suscripción en MercadoPago
  POST /admin/maintenance/cleanup-expired → degradar licencias mensuales vencidas
  GET  /admin/versions                → lista versiones
  POST /admin/versions/upload         → subir nueva versión
  PUT  /admin/versions/{id}           → editar metadatos versión
  DELETE /admin/versions/{id}         → eliminar versión
"""
import asyncio
import os
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

import hashlib
import hmac
import json
import secrets

import httpx
import mercadopago
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request, Header, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from database import engine, get_db, auto_migrate
from models import Base, License, Version, Setting, SiteAsset, HeroSlide, Download, Review, Lead, LeadEvent
from seeds import seed_initial_data

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("licenses")

# ── Config ────────────────────────────────────────────────────────────────────
MP_ACCESS_TOKEN   = os.getenv("MP_ACCESS_TOKEN", "")
MP_PUBLIC_KEY     = os.getenv("MP_PUBLIC_KEY", "")
MP_WEBHOOK_SECRET = os.getenv("MP_WEBHOOK_SECRET", "")
SITE_URL          = os.getenv("SITE_URL", "https://goxtech.com.ar")
ADMIN_USER        = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS        = os.getenv("ADMIN_PASS", "254136b+")
_JWT_SECRET       = os.getenv("JWT_SECRET", "goxtech-arca-admin-jwt-secret-2026")
_JWT_EXPIRY_HOURS = 24
DOWNLOADS_DIR     = Path(os.getenv("DOWNLOADS_DIR", "/home/goxtechcomar/web/goxtech.com.ar/public_html/arca_factusol/downloads"))

# ── Hardening config ──
# CORS env-driven: lista comma-separated de orígenes permitidos.
# Default: localhost para Astro (4321) y Vite admin (5173) en desarrollo.
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:4321,http://localhost:5173").split(",")
    if o.strip()
]

DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)
auto_migrate()  # agrega columnas nuevas si faltan

# Valores default de settings
DEFAULT_SETTINGS = {
    "monthly_price_usd":       "10",
    "lifetime_price_usd":      "200",
    "price_margin_pct":        "0",       # margen % sobre cotización BNA (ej: 5 = +5%)
    "mp_subscription_plan_id": "",
}

# ── Caché cotización BNA ──────────────────────────────────────────────────────
_bna_cache: dict = {"rate": None, "ts": 0}
BNA_CACHE_TTL = 7200  # 2 horas


async def _fetch_bna_rate() -> float | None:
    """Obtiene cotización venta del dólar oficial BNA desde dolarapi.com."""
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get("https://dolarapi.com/v1/dolares/oficial")
            if r.status_code == 200:
                data = r.json()
                return float(data.get("venta") or data.get("compra") or 0)
    except Exception as e:
        logger.warning(f"Error al obtener cotización BNA: {e}")
    return None


async def _get_bna_rate() -> float | None:
    """Devuelve cotización BNA desde caché o fetchea si expiró."""
    now = time.time()
    if _bna_cache["rate"] and (now - _bna_cache["ts"]) < BNA_CACHE_TTL:
        return _bna_cache["rate"]
    rate = await _fetch_bna_rate()
    if rate:
        _bna_cache["rate"] = rate
        _bna_cache["ts"] = now
        logger.info(f"Cotización BNA actualizada: ${rate:.2f}")
    return rate or _bna_cache.get("rate")  # fallback al último valor conocido


def _init_settings(db: Session):
    """Inserta valores default de settings si no existen."""
    for key, value in DEFAULT_SETTINGS.items():
        if not db.query(Setting).filter(Setting.key == key).first():
            db.add(Setting(key=key, value=value))
    db.commit()


def _get_setting(db: Session, key: str, default: str = "") -> str:
    s = db.query(Setting).filter(Setting.key == key).first()
    return s.value if s else default


def _set_setting(db: Session, key: str, value: str):
    s = db.query(Setting).filter(Setting.key == key).first()
    if s:
        s.value = value
    else:
        db.add(Setting(key=key, value=value))
    db.commit()


# Inicializar settings y seeds al arrancar
with next(get_db()) as db:
    _init_settings(db)
    seed_initial_data(db)


app = FastAPI(title="GoxTech Licenses API", docs_url=None, redoc_url=None)

# CORS restrictivo: solo orígenes definidos en CORS_ORIGINS (env var).
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Servir uploads como archivos estaticos ────────────────────────────────
# Nginx routea /arca_factusol/api/* -> este backend en :8001 (sin prefix).
# Resultado: GET /arca_factusol/api/uploads/site/logo_main-XXX.png va a:
#   - nginx: strip /arca_factusol/api/ -> /uploads/site/logo_main-XXX.png
#   - backend: StaticFiles bajo "/uploads" -> sirve "uploads/site/logo_main-XXX.png"
# La carpeta uploads/ esta junto al main.py (WorkingDirectory=/opt/goxtech_licenses).
from fastapi.staticfiles import StaticFiles
import os as _os
_uploads_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "uploads")
_os.makedirs(_uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_uploads_dir), name="uploads")

# Rate limiting con slowapi. Cada endpoint que quiera limitar debe importar
# `limiter` desde aquí o usar `request.app.state.limiter` y aplicar el decorator.
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clean_cuit(cuit: str) -> str:
    return cuit.replace("-", "").replace(" ", "").strip()


def _make_jwt(username: str) -> str:
    """Genera un JWT simple (HMAC-SHA256) sin dependencias externas."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": username,
        "exp": int((datetime.utcnow() + timedelta(hours=_JWT_EXPIRY_HOURS)).timestamp()),
    }
    def _b64(data):
        import base64
        return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()
    head_b64 = _b64(header)
    pay_b64 = _b64(payload)
    sig = hmac.new(_JWT_SECRET.encode(), f"{head_b64}.{pay_b64}".encode(), hashlib.sha256).digest()
    import base64
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
    return f"{head_b64}.{pay_b64}.{sig_b64}"


def _pad_b64(s: str) -> str:
    return s + "=" * (-len(s) % 4)


def _verify_jwt(token: str) -> str | None:
    """Verifica JWT, retorna username o None."""
    import base64
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        head_b64, pay_b64, sig_b64 = parts
        expected_sig = hmac.new(_JWT_SECRET.encode(), f"{head_b64}.{pay_b64}".encode(), hashlib.sha256).digest()
        sig = base64.urlsafe_b64decode(_pad_b64(sig_b64))
        if not hmac.compare_digest(sig, expected_sig):
            return None
        payload = json.loads(base64.urlsafe_b64decode(_pad_b64(pay_b64)))
        if payload.get("exp", 0) < time.time():
            return None
        return payload.get("sub")
    except Exception:
        return None


def _require_admin(
    authorization: str = Header(default=""),
    x_admin_token: str = Header(default=""),
    token: str = Query(default=""),
):
    # 1. Bearer JWT en header Authorization
    if authorization.startswith("Bearer "):
        user = _verify_jwt(authorization[7:])
        if user:
            return user
    # 2. JWT en query param ?token= (fallback si nginx no pasa Authorization)
    if token:
        user = _verify_jwt(token)
        if user:
            return user
    # 3. Token legacy por header x-admin-token
    legacy = os.getenv("ADMIN_TOKEN", "")
    if x_admin_token and legacy and x_admin_token == legacy:
        return "admin"
    raise HTTPException(status_code=401, detail="No autorizado")


def _fmt_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    return f"{size_bytes/1024/1024:.1f} MB"


def _calc_ars(usd: float, rate: float | None, margin_pct: float) -> float | None:
    if not rate:
        return None
    return round(usd * rate * (1 + margin_pct / 100))


def _get_prices_sync(db: Session, bna_rate: float | None = None) -> dict:
    monthly_usd  = float(_get_setting(db, "monthly_price_usd",  "10"))
    lifetime_usd = float(_get_setting(db, "lifetime_price_usd", "200"))
    margin_pct   = float(_get_setting(db, "price_margin_pct",   "0"))
    rate = bna_rate or _bna_cache.get("rate")
    return {
        "monthly": {
            "usd": monthly_usd,
            "ars": _calc_ars(monthly_usd, rate, margin_pct),
        },
        "lifetime": {
            "usd": lifetime_usd,
            "ars": _calc_ars(lifetime_usd, rate, margin_pct),
        },
        "bna_rate":   rate,
        "margin_pct": margin_pct,
    }


async def _get_prices(db: Session) -> dict:
    rate = await _get_bna_rate()
    return _get_prices_sync(db, rate)


# ── Limpieza de licencias vencidas ────────────────────────────────────────────

def _cleanup_expired_monthly(db: Session) -> int:
    """Degrada a 'basica' las licencias mensuales con valid_until vencido."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    expired = db.query(License).filter(
        License.plan == "monthly",
        License.active == True,
        License.valid_until != None,
        License.valid_until < today,
    ).all()
    for lic in expired:
        lic.plan = "basica"
        lic.payment_status = "expired"
        lic.updated_at = datetime.utcnow()
    if expired:
        db.commit()
        logger.info(f"Cleanup: {len(expired)} licencias mensuales vencidas → basica")
    return len(expired)


@app.on_event("startup")
async def startup_cleanup():
    """Limpieza inicial + loop periódico cada 6 horas."""
    try:
        db = next(get_db())
        n = _cleanup_expired_monthly(db)
        if n:
            logger.info(f"Startup cleanup: {n} licencias vencidas degradadas")
    except Exception as e:
        logger.error(f"Startup cleanup error: {e}")

    async def _cleanup_loop():
        while True:
            await asyncio.sleep(6 * 3600)
            try:
                db = next(get_db())
                _cleanup_expired_monthly(db)
                db.close()
            except Exception as e:
                logger.error(f"Periodic cleanup error: {e}")

    asyncio.create_task(_cleanup_loop())


# ── Endpoints públicos ────────────────────────────────────────────────────────

@app.get("/licenses/check")
def check_license(cuit: str = Query(...), v: str = Query(default=""), db: Session = Depends(get_db)):
    """Verifica plan de un CUIT. Opcionalmente recibe ?v=1.6.0 para trackear version."""
    cuit_clean = _clean_cuit(cuit)
    if not cuit_clean or len(cuit_clean) < 10:
        return {"plan": "basica", "active": True, "valid_until": None}
    lic = db.query(License).filter(License.cuit == cuit_clean).first()

    # Registrar version y ultima actividad (incluso si no tiene licencia activa)
    if lic and v:
        lic.app_version = v
        lic.last_seen = datetime.utcnow()
        db.commit()
    elif lic:
        lic.last_seen = datetime.utcnow()
        db.commit()

    if not lic or not lic.active:
        return {"plan": "basica", "active": True, "valid_until": None}
    # Para plan mensual verificar vencimiento
    if lic.plan == "monthly" and lic.valid_until:
        try:
            if datetime.strptime(lic.valid_until, "%Y-%m-%d") < datetime.utcnow():
                return {"plan": "basica", "active": True, "valid_until": None}
        except ValueError:
            pass
    return {"plan": lic.plan, "active": lic.active, "valid_until": lic.valid_until}


@app.get("/licenses/prices")
async def get_prices(db: Session = Depends(get_db)):
    return await _get_prices(db)


# Endpoint legacy para compatibilidad con versiones anteriores del módulo
@app.get("/licenses/price")
async def get_price(db: Session = Depends(get_db)):
    prices = await _get_prices(db)
    return {"price": prices["lifetime"]["ars"], "currency": "ARS"}


class FreeRequest(BaseModel):
    cuit: str
    email: str
    company_name: str = ""
    # Nuevos campos (opcionales para retrocompatibilidad con clientes viejos;
    # la app v1.6.9+ los envia siempre para alimentar el CRM y poder convertir
    # leads gratis a pago).
    phone: str = ""           # WhatsApp del responsable (recomendado)
    contact_name: str = ""    # Nombre del responsable (mostrar en CRM)
    source: str = ""          # 'app_registration' | 'web_form' | etc


def _upsert_lead_for_license(
    db: Session,
    cuit: str,
    email: str,
    company_name: str,
    phone: str = "",
    contact_name: str = "",
    source: str = "app_registration",
) -> None:
    """
    Al registrar una licencia (gratis o pago), creamos/actualizamos un Lead en
    el CRM para hacer follow-up comercial. Si ya existe un lead con ese CUIT,
    actualizamos campos vacios y agregamos un LeadEvent (no duplicamos lead).

    Si el CRM falla por cualquier motivo NO levantamos excepcion — el registro
    de licencia debe completarse aunque el CRM tenga un bug.
    """
    try:
        lead = db.query(Lead).filter(Lead.cuit == cuit).first()
        if lead:
            changes = {}
            if phone and not lead.phone:
                lead.phone = phone
                changes["phone"] = phone
            if email and not lead.email:
                lead.email = email
                changes["email"] = email
            if company_name and not lead.company:
                lead.company = company_name
                changes["company"] = company_name
            if contact_name and lead.name != contact_name and contact_name.strip():
                lead.name = contact_name
                changes["name"] = contact_name
            db.add(LeadEvent(
                lead_id=lead.id,
                type="re_registration",
                payload_json=json.dumps({"source": source, "changes": changes}),
            ))
            return

        display_name = (contact_name or company_name or email or cuit)
        lead = Lead(
            name=display_name,
            phone=phone or None,
            email=email or None,
            company=company_name or None,
            cuit=cuit,
            source=source or "app_registration",
            stage="Nuevo",
            notes="Registrado automaticamente al activar licencia gratuita.",
        )
        db.add(lead)
        db.flush()
        db.add(LeadEvent(
            lead_id=lead.id,
            type="created_from_registration",
            payload_json=json.dumps({"source": source, "plan": "basica"}),
        ))
    except Exception as e:
        logger.warning(f"No pude crear/actualizar Lead para CUIT {cuit}: {e}")


@app.post("/licenses/free", status_code=201)
def register_free(data: FreeRequest, db: Session = Depends(get_db)):
    cuit_clean = _clean_cuit(data.cuit)
    if not cuit_clean or len(cuit_clean) < 10:
        raise HTTPException(status_code=400, detail="CUIT inválido")
    if not data.email or "@" not in data.email:
        raise HTTPException(status_code=400, detail="Email inválido")

    lic = db.query(License).filter(License.cuit == cuit_clean).first()
    if lic:
        # Si ya tiene plan superior, no degradar — pero igual refrescar Lead.
        if lic.plan in ("monthly", "completa") and lic.active:
            _upsert_lead_for_license(
                db, cuit_clean, data.email, data.company_name,
                data.phone, data.contact_name, data.source or "app_registration",
            )
            db.commit()
            return {"message": f"CUIT ya registrado con plan {lic.plan}", "plan": lic.plan}
        lic.email = data.email
        lic.company_name = data.company_name
        lic.updated_at = datetime.utcnow()
    else:
        lic = License(
            cuit=cuit_clean,
            plan="basica",
            active=True,
            email=data.email,
            company_name=data.company_name,
            payment_id="free",
            payment_status="free",
        )
        db.add(lic)

    _upsert_lead_for_license(
        db, cuit_clean, data.email, data.company_name,
        data.phone, data.contact_name, data.source or "app_registration",
    )

    db.commit()
    return {"message": "Licencia gratuita activada", "plan": "basica"}


@app.get("/versions/latest")
def get_latest_version(plan: str = "basica", db: Session = Depends(get_db)):
    q = db.query(Version).filter(Version.is_active == True, Version.is_latest == True)
    if plan != "all":
        q = q.filter(Version.plan.in_([plan, "all"]))
    ver = q.first()
    if not ver:
        return {"available": False}
    return {
        "available": True,
        "id": ver.id,
        "version_number": ver.version_number,
        "display_name": ver.display_name,
        "plan": ver.plan,
        "changelog": ver.changelog,
        "file_size": _fmt_size(ver.file_size),
        "download_url": f"{SITE_URL}/arca_factusol/api/downloads/{ver.filename}",
        "created_at": ver.created_at.isoformat() if ver.created_at else None,
    }


@app.get("/downloads/{filename}")
def download_file(filename: str, db: Session = Depends(get_db)):
    safe_name = Path(filename).name
    file_path = DOWNLOADS_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    ver = db.query(Version).filter(Version.filename == safe_name).first()
    if ver:
        ver.downloads = (ver.downloads or 0) + 1
        db.commit()

    return FileResponse(
        path=str(file_path),
        filename=safe_name,
        media_type="application/octet-stream",
    )


# ── Checkout MercadoPago — Plan Vitalicio ─────────────────────────────────────

class CheckoutRequest(BaseModel):
    cuit: str
    email: str = ""


@app.post("/licenses/checkout")
async def create_checkout(data: CheckoutRequest, db: Session = Depends(get_db)):
    cuit_clean = _clean_cuit(data.cuit)
    if not cuit_clean or len(cuit_clean) < 10:
        raise HTTPException(status_code=400, detail="CUIT inválido")

    existing = db.query(License).filter(License.cuit == cuit_clean).first()
    if existing and existing.active and existing.plan == "completa":
        raise HTTPException(status_code=400, detail="Este CUIT ya tiene licencia Vitalicia activa")

    if not MP_ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail="MercadoPago no configurado")

    prices = await _get_prices(db)
    lifetime_price = prices["lifetime"]["ars"]

    sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
    preference_data = {
        "items": [{
            "id": "arca-sync-vitalicio",
            "title": "ARCA Sync — Licencia Vitalicia",
            "description": f"Licencia de por vida para CUIT {cuit_clean}",
            "quantity": 1,
            "currency_id": "ARS",
            "unit_price": lifetime_price,
        }],
        "external_reference": cuit_clean,
        "payer": {"email": data.email} if data.email else {},
        "back_urls": {
            "success": f"{SITE_URL}/arca_factusol/?pago=ok&cuit={cuit_clean}",
            "failure": f"{SITE_URL}/arca_factusol/?pago=error",
            "pending": f"{SITE_URL}/arca_factusol/?pago=pendiente",
        },
        "auto_return": "approved",
        "notification_url": f"{SITE_URL}/arca_factusol/api/licenses/mp-webhook",
        "statement_descriptor": "GoxTech ARCA Sync",
        "metadata": {"cuit": cuit_clean, "plan": "lifetime"},
    }
    result = sdk.preference().create(preference_data)
    if result["status"] not in (200, 201):
        raise HTTPException(status_code=500, detail="Error al crear preferencia de pago")

    pref = result["response"]
    return {"init_point": pref["init_point"], "sandbox_init_point": pref.get("sandbox_init_point", "")}


@app.post("/licenses/mp-webhook")
async def mp_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.json()
    except Exception:
        return {"status": "ignored"}

    logger.info(f"Webhook pago: {payload}")
    if payload.get("type") not in ("payment",):
        return {"status": "ignored"}

    data_id = payload.get("data", {}).get("id") or payload.get("id")
    if not data_id:
        return {"status": "ignored"}

    sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
    payment_info = sdk.payment().get(data_id)
    if payment_info["status"] != 200:
        return {"status": "error"}

    payment = payment_info["response"]
    status = payment.get("status", "")
    cuit_clean = _clean_cuit(str(payment.get("external_reference", "")))

    if status == "approved" and cuit_clean and len(cuit_clean) >= 10:
        _activate_lifetime_license(cuit_clean, str(data_id), status, db)
        logger.info(f"Licencia vitalicia activada: {cuit_clean}")

    return {"status": "ok"}


def _activate_lifetime_license(cuit: str, payment_id: str, payment_status: str, db: Session):
    lic = db.query(License).filter(License.cuit == cuit).first()
    if lic:
        lic.active = True
        lic.plan = "completa"
        lic.payment_id = payment_id
        lic.payment_status = payment_status
        lic.valid_until = None  # Vitalicio, sin vencimiento
        lic.updated_at = datetime.utcnow()
    else:
        lic = License(cuit=cuit, plan="completa", active=True,
                      payment_id=payment_id, payment_status=payment_status)
        db.add(lic)
    db.commit()


# ── Suscripción MercadoPago — Plan Mensual ────────────────────────────────────

class SubscribeRequest(BaseModel):
    cuit: str
    email: str


@app.post("/licenses/subscribe")
async def create_subscription(data: SubscribeRequest, db: Session = Depends(get_db)):
    cuit_clean = _clean_cuit(data.cuit)
    if not cuit_clean or len(cuit_clean) < 10:
        raise HTTPException(status_code=400, detail="CUIT inválido")
    if not data.email or "@" not in data.email:
        raise HTTPException(status_code=400, detail="Email requerido para suscripción")

    if not MP_ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail="MercadoPago no configurado")

    prices = await _get_prices(db)
    monthly_price = prices["monthly"]["ars"]

    sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

    # Obtener o crear plan de suscripción
    plan_id = _get_setting(db, "mp_subscription_plan_id", "")
    if not plan_id:
        plan_result = sdk.preapproval_plan().create({
            "reason": "ARCA Sync — Plan Mensual",
            "auto_recurring": {
                "frequency": 1,
                "frequency_type": "months",
                "transaction_amount": monthly_price,
                "currency_id": "ARS",
            },
            "back_url": f"{SITE_URL}/arca_factusol/",
            "payment_methods_allowed": {
                "payment_types": [{"id": "credit_card"}, {"id": "debit_card"}],
            },
        })
        if plan_result["status"] not in (200, 201):
            raise HTTPException(status_code=500, detail="Error al crear plan de suscripción")
        plan_id = plan_result["response"]["id"]
        _set_setting(db, "mp_subscription_plan_id", plan_id)

    # Generar URL de checkout del plan SIN crear preapproval del lado backend.
    # Desde mediados de 2024, MercadoPago exige `card_token_id` cuando se crea
    # un preapproval con SDK (POST /preapproval) — requiere tokenizar la tarjeta
    # en el frontend con MercadoPago.js.
    #
    # La forma simple (sin tokenización, que MP usa históricamente) es redirigir
    # al cliente al `init_point` del PLAN. MP captura los datos de tarjeta en su
    # sitio, crea la suscripción y dispara el webhook con el preapproval_id real.
    #
    # Documentación:
    #   https://www.mercadopago.com.ar/developers/es/docs/subscriptions/integration-configuration/plan
    import urllib.parse as _urlparse
    qs = _urlparse.urlencode({
        "preapproval_plan_id": plan_id,
        "external_reference": cuit_clean,
        "payer_email": data.email,
        # back_url se respeta del PLAN; se pueden pasar querys extras y MP los devuelve.
    })
    init_point = f"https://www.mercadopago.com.ar/subscriptions/checkout?{qs}"

    logger.info(
        f"[subscribe] plan={plan_id} cuit={cuit_clean} email={data.email} -> {init_point}"
    )
    return {"init_point": init_point}


@app.post("/licenses/mp-subscription-webhook")
async def mp_subscription_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.json()
    except Exception:
        return {"status": "ignored"}

    logger.info(f"Webhook suscripción: {payload}")

    # MP envía tipo "preapproval" para suscripciones
    event_type = payload.get("type", "")
    if event_type not in ("preapproval", "subscription_authorized_payment"):
        return {"status": "ignored"}

    data_id = payload.get("data", {}).get("id") or payload.get("id")
    if not data_id:
        return {"status": "ignored"}

    sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

    if event_type == "preapproval":
        # Suscripción activada, renovada, cancelada o pausada
        sub_info = sdk.preapproval().get(data_id)
        if sub_info["status"] != 200:
            return {"status": "error"}
        sub = sub_info["response"]
        sub_status = sub.get("status", "")
        cuit_clean = _clean_cuit(str(sub.get("external_reference", "")))
        if not cuit_clean or len(cuit_clean) < 10:
            return {"status": "ignored"}

        if sub_status == "authorized":
            _activate_monthly_license(cuit_clean, str(data_id), sub.get("payer_email", ""), db)
            logger.info(f"Suscripción mensual activada: {cuit_clean}")
        elif sub_status in ("cancelled", "paused"):
            lic = db.query(License).filter(License.cuit == cuit_clean).first()
            if lic and lic.plan == "monthly":
                lic.plan = "basica"
                lic.payment_status = sub_status
                lic.updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Suscripción {sub_status}: {cuit_clean} → basica")
    elif event_type == "subscription_authorized_payment":
        # Pago mensual procesado
        payment_info = sdk.payment().get(data_id)
        if payment_info["status"] == 200:
            payment = payment_info["response"]
            if payment.get("status") == "approved":
                cuit_clean = _clean_cuit(str(payment.get("external_reference", "")))
                if cuit_clean and len(cuit_clean) >= 10:
                    _activate_monthly_license(cuit_clean, str(data_id), "", db)
                    logger.info(f"Pago mensual procesado: {cuit_clean}")

    return {"status": "ok"}


def _activate_monthly_license(cuit: str, payment_id: str, email: str, db: Session):
    valid_until = (datetime.utcnow() + timedelta(days=33)).strftime("%Y-%m-%d")
    lic = db.query(License).filter(License.cuit == cuit).first()
    if lic:
        # No degradar si ya tiene plan vitalicio
        if lic.plan == "completa":
            return
        lic.active = True
        lic.plan = "monthly"
        lic.payment_id = payment_id
        lic.payment_status = "approved"
        lic.valid_until = valid_until
        if email:
            lic.email = email
        lic.updated_at = datetime.utcnow()
    else:
        lic = License(cuit=cuit, plan="monthly", active=True,
                      payment_id=payment_id, payment_status="approved",
                      valid_until=valid_until, email=email or None)
        db.add(lic)
    db.commit()


# ── Admin: Login ──────────────────────────────────────────────────────────────

class AdminLogin(BaseModel):
    username: str
    password: str

@app.post("/admin/login")
def admin_login(data: AdminLogin):
    if data.username == ADMIN_USER and data.password == ADMIN_PASS:
        token = _make_jwt(data.username)
        return {"token": token, "username": data.username}
    raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")


# ── Admin: Stats ──────────────────────────────────────────────────────────────

@app.get("/admin/stats")
async def get_stats(db: Session = Depends(get_db), _=Depends(_require_admin)):
    prices = await _get_prices(db)
    total_licenses  = db.query(License).count()
    active_licenses = db.query(License).filter(License.active == True).count()
    lifetime_active = db.query(License).filter(License.active == True, License.plan == "completa").count()
    monthly_active  = db.query(License).filter(License.active == True, License.plan == "monthly").count()
    free_active     = db.query(License).filter(License.active == True, License.plan == "basica").count()
    dl_sum = db.query(func.sum(Version.downloads)).scalar() or 0
    total_versions = db.query(Version).filter(Version.is_active == True).count()

    revenue_estimate = (lifetime_active * prices["lifetime"]["ars"] +
                        monthly_active * prices["monthly"]["ars"])

    return {
        "licenses": {
            "total": total_licenses,
            "active": active_licenses,
            "lifetime": lifetime_active,
            "monthly": monthly_active,
            "free": free_active,
            "revenue_estimate": revenue_estimate,
        },
        "versions": {
            "total": total_versions,
            "total_downloads": dl_sum,
        },
    }


# ── Admin: Licencias ──────────────────────────────────────────────────────────

@app.get("/admin/licenses")
def list_licenses(
    search: str = "",
    plan: str = "",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _=Depends(_require_admin),
):
    q = db.query(License)
    if search:
        term = search.replace("-", "").replace(" ", "")
        q = q.filter(
            License.cuit.contains(term) |
            License.email.contains(search) |
            License.company_name.contains(search)
        )
    if plan:
        q = q.filter(License.plan == plan)
    total = q.count()
    licenses = q.order_by(License.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [
            {
                "id": l.id,
                "cuit": l.cuit,
                "plan": l.plan,
                "active": l.active,
                "valid_until": l.valid_until,
                "payment_id": l.payment_id,
                "payment_status": l.payment_status,
                "created_at": l.created_at.isoformat() if l.created_at else None,
                "updated_at": l.updated_at.isoformat() if l.updated_at else None,
                "notes": l.notes,
                "email": l.email,
                "company_name": l.company_name,
                "app_version": l.app_version,
                "last_seen": l.last_seen.isoformat() if l.last_seen else None,
            }
            for l in licenses
        ],
    }


class LicenseUpsert(BaseModel):
    cuit: str
    plan: str = "completa"
    active: bool = True
    valid_until: str | None = None
    notes: str | None = None
    email: str | None = None
    company_name: str | None = None


@app.post("/admin/licenses", status_code=201)
def upsert_license(data: LicenseUpsert, db: Session = Depends(get_db), _=Depends(_require_admin)):
    cuit_clean = _clean_cuit(data.cuit)
    if not cuit_clean or len(cuit_clean) < 10:
        raise HTTPException(status_code=400, detail="CUIT inválido (mínimo 10 dígitos)")

    lic = db.query(License).filter(License.cuit == cuit_clean).first()
    if lic:
        lic.plan = data.plan
        lic.active = data.active
        lic.valid_until = data.valid_until
        lic.notes = data.notes
        lic.email = data.email
        lic.company_name = data.company_name
        lic.updated_at = datetime.utcnow()
        action = "actualizada"
    else:
        lic = License(cuit=cuit_clean, plan=data.plan, active=data.active,
                      valid_until=data.valid_until, payment_id="manual",
                      payment_status="manual", notes=data.notes,
                      email=data.email, company_name=data.company_name)
        db.add(lic)
        action = "creada"
    db.commit()
    return {"message": f"Licencia {action} para CUIT {cuit_clean}"}


@app.put("/admin/licenses/{cuit}")
def update_license(cuit: str, data: LicenseUpsert, db: Session = Depends(get_db), _=Depends(_require_admin)):
    cuit_clean = _clean_cuit(cuit)
    lic = db.query(License).filter(License.cuit == cuit_clean).first()
    if not lic:
        raise HTTPException(status_code=404, detail="Licencia no encontrada")
    lic.plan = data.plan
    lic.active = data.active
    lic.valid_until = data.valid_until
    lic.notes = data.notes
    lic.email = data.email
    lic.company_name = data.company_name
    lic.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Licencia actualizada"}


@app.delete("/admin/licenses/{cuit}")
def delete_license(cuit: str, db: Session = Depends(get_db), _=Depends(_require_admin)):
    cuit_clean = _clean_cuit(cuit)
    lic = db.query(License).filter(License.cuit == cuit_clean).first()
    if not lic:
        raise HTTPException(status_code=404, detail="Licencia no encontrada")
    lic.active = False
    lic.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Licencia desactivada"}


# ── Admin: Settings / Precios ─────────────────────────────────────────────────

@app.get("/admin/settings")
def get_settings(db: Session = Depends(get_db), _=Depends(_require_admin)):
    settings = db.query(Setting).all()
    return {s.key: s.value for s in settings}


class SettingsUpdate(BaseModel):
    monthly_price_usd: float | None = None
    lifetime_price_usd: float | None = None
    price_margin_pct: float | None = None
    mp_subscription_plan_id: str | None = None


@app.put("/admin/settings")
def update_settings(data: SettingsUpdate, db: Session = Depends(get_db), _=Depends(_require_admin)):
    if data.monthly_price_usd is not None:
        _set_setting(db, "monthly_price_usd", str(data.monthly_price_usd))
    if data.lifetime_price_usd is not None:
        _set_setting(db, "lifetime_price_usd", str(data.lifetime_price_usd))
    if data.price_margin_pct is not None:
        _set_setting(db, "price_margin_pct", str(max(0, data.price_margin_pct)))
    if data.mp_subscription_plan_id is not None:
        _set_setting(db, "mp_subscription_plan_id", data.mp_subscription_plan_id.strip())
    return {"message": "Configuración actualizada"}


@app.get("/admin/settings/exchange-rate")
async def get_exchange_rate(_=Depends(_require_admin)):
    """Devuelve la cotización BNA actual (forzando refresh si está vencida)."""
    rate = await _fetch_bna_rate()
    if rate:
        _bna_cache["rate"] = rate
        _bna_cache["ts"] = time.time()
    cached_age = int(time.time() - _bna_cache["ts"]) if _bna_cache["ts"] else None
    return {
        "rate": _bna_cache.get("rate"),
        "source": "BNA oficial (dolarapi.com)",
        "cache_age_seconds": cached_age,
        "cache_ttl_seconds": BNA_CACHE_TTL,
    }


@app.post("/admin/settings/create-mp-plan")
async def create_mp_plan(db: Session = Depends(get_db), _=Depends(_require_admin)):
    if not MP_ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail="MercadoPago no configurado")
    prices = await _get_prices(db)
    sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
    result = sdk.preapproval_plan().create({
        "reason": "ARCA Sync — Plan Mensual",
        "auto_recurring": {
            "frequency": 1,
            "frequency_type": "months",
            "transaction_amount": prices["monthly"]["ars"],
            "currency_id": "ARS",
        },
        "back_url": f"{SITE_URL}/arca_factusol/",
        "payment_methods_allowed": {
            "payment_types": [{"id": "credit_card"}, {"id": "debit_card"}],
        },
    })
    if result["status"] not in (200, 201):
        raise HTTPException(status_code=500, detail=f"Error MP: {result}")
    plan_id = result["response"]["id"]
    _set_setting(db, "mp_subscription_plan_id", plan_id)
    return {"message": "Plan MP creado", "plan_id": plan_id}


@app.post("/admin/maintenance/cleanup-expired")
def manual_cleanup(db: Session = Depends(get_db), _=Depends(_require_admin)):
    """Degrada manualmente todas las licencias mensuales con valid_until vencido."""
    n = _cleanup_expired_monthly(db)
    return {"cleaned": n, "message": f"{n} licencia(s) vencida(s) degradada(s) a plan Gratis"}


# ── Admin: Versiones ──────────────────────────────────────────────────────────

@app.get("/admin/versions")
def list_versions(db: Session = Depends(get_db), _=Depends(_require_admin)):
    versions = db.query(Version).order_by(Version.created_at.desc()).all()
    return [
        {
            "id": v.id,
            "version_number": v.version_number,
            "display_name": v.display_name,
            "plan": v.plan,
            "filename": v.filename,
            "file_size": v.file_size,
            "file_size_fmt": _fmt_size(v.file_size),
            "changelog": v.changelog,
            "is_latest": v.is_latest,
            "is_active": v.is_active,
            "downloads": v.downloads,
            "download_url": f"{SITE_URL}/arca_factusol/api/downloads/{v.filename}",
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in versions
    ]


@app.post("/admin/versions/upload", status_code=201)
async def upload_version(
    file: UploadFile = File(...),
    version_number: str = Form(...),
    display_name: str = Form(...),
    plan: str = Form("basica"),
    changelog: str = Form(""),
    set_as_latest: bool = Form(True),
    db: Session = Depends(get_db),
    _=Depends(_require_admin),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Archivo requerido")

    # Validar extensión y tamaño (hardening F4-02). Para versiones del módulo
    # ARCA aceptamos .exe / .zip / .pdf — los binarios de instalador suelen
    # ser pesados, por eso permitimos un tope mayor al global (ver env
    # MAX_VERSION_UPLOAD_MB, default 200).
    max_mb = int(os.getenv("MAX_VERSION_UPLOAD_MB", "200"))
    allowed = {".exe", ".zip", ".pdf"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión no permitida para versiones: '{ext}'. Aceptadas: {', '.join(sorted(allowed))}",
        )

    safe_name = f"arca_sync_v{version_number.replace(' ', '_')}{Path(file.filename).suffix}"
    dest = DOWNLOADS_DIR / safe_name

    content = await file.read()
    if len(content) > max_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Archivo demasiado grande (máximo {max_mb} MB)")
    with open(dest, "wb") as f:
        f.write(content)

    if set_as_latest:
        db.query(Version).filter(Version.plan == plan).update({"is_latest": False})
        db.query(Version).filter(Version.plan == "all").update({"is_latest": False})

    ver = Version(
        version_number=version_number,
        display_name=display_name,
        plan=plan,
        filename=safe_name,
        file_size=len(content),
        changelog=changelog or None,
        is_latest=set_as_latest,
        is_active=True,
        downloads=0,
    )
    db.add(ver)
    db.commit()
    db.refresh(ver)

    return {
        "message": f"Versión {version_number} subida correctamente",
        "id": ver.id,
        "filename": safe_name,
        "file_size": _fmt_size(len(content)),
    }


class VersionUpdate(BaseModel):
    display_name: str | None = None
    plan: str | None = None
    changelog: str | None = None
    is_latest: bool | None = None
    is_active: bool | None = None


@app.put("/admin/versions/{version_id}")
def update_version(version_id: int, data: VersionUpdate, db: Session = Depends(get_db), _=Depends(_require_admin)):
    ver = db.query(Version).filter(Version.id == version_id).first()
    if not ver:
        raise HTTPException(status_code=404, detail="Versión no encontrada")

    if data.display_name is not None:
        ver.display_name = data.display_name
    if data.plan is not None:
        ver.plan = data.plan
    if data.changelog is not None:
        ver.changelog = data.changelog
    if data.is_active is not None:
        ver.is_active = data.is_active
    if data.is_latest is not None:
        if data.is_latest:
            db.query(Version).filter(Version.id != version_id).update({"is_latest": False})
        ver.is_latest = data.is_latest

    db.commit()
    return {"message": "Versión actualizada"}


@app.delete("/admin/versions/{version_id}")
def delete_version(version_id: int, db: Session = Depends(get_db), _=Depends(_require_admin)):
    ver = db.query(Version).filter(Version.id == version_id).first()
    if not ver:
        raise HTTPException(status_code=404, detail="Versión no encontrada")

    file_path = DOWNLOADS_DIR / ver.filename
    if file_path.exists():
        file_path.unlink()

    db.delete(ver)
    db.commit()
    return {"message": "Versión eliminada"}


# ── Routers de la plataforma unificada ────────────────────────────────────────
from routers import site as site_router
from routers import downloads_public as downloads_public_router
from routers import leads as leads_router
from routers import admin_site as admin_site_router
from routers import admin_downloads as admin_downloads_router
from routers import admin_reviews as admin_reviews_router
from routers import admin_leads as admin_leads_router
from routers import admin_stats as admin_stats_router

app.include_router(site_router.router)
app.include_router(downloads_public_router.router)
app.include_router(leads_router.router)
app.include_router(admin_site_router.router)
app.include_router(admin_downloads_router.router)
app.include_router(admin_reviews_router.router)
app.include_router(admin_leads_router.router)
app.include_router(admin_stats_router.router)
