"""
Factusol Módulo ARCA - Web Application
Punto de entrada de la aplicación FastAPI.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path

from app.database import init_db, SessionLocal
from app.auth import hash_password
from app.models.user import User

from app.routers import auth_router, users_router, factusol_router, arca_router, config_router, credit_notes_router, updates_router


STATIC_DIR = Path(__file__).parent / "static"
QR_DIR = STATIC_DIR / "qr"
QR_DIR.mkdir(exist_ok=True)


def _create_default_admin():
    """Crea el usuario admin por defecto si no existe ningún usuario."""
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                username="admin",
                password_hash=hash_password("admin"),
                full_name="Administrador",
                role="admin",
            )
            db.add(admin)
            db.commit()
            print("✅ Usuario admin creado (usuario: admin, contraseña: admin)")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    _create_default_admin()

    # Iniciar auto-validador si está habilitado
    from app.services import auto_validate
    from app.config import get_config
    if get_config().get("auto_validate", {}).get("enabled", False):
        auto_validate.start_background_task()
        print("🤖 Auto-validación ARCA activada")

    print("🚀 Factusol ARCA Sync iniciado")
    yield
    # Shutdown
    auto_validate.stop_background_task()
    print("👋 Factusol ARCA Sync detenido")


app = FastAPI(
    title="Factusol ARCA Sync",
    description="Módulo de facturación electrónica ARCA para Factusol",
    version="1.6.7",
    lifespan=lifespan,
)

# CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── No-cache para assets de UI ────────────────────────────────────────────
# El WebView embebido (Chrome/Edge --app) cachea HTML/JS por defecto. Tras un
# update remoto, los archivos en disco cambian pero el browser sigue sirviendo
# de cache HTTP la version vieja → el usuario no ve los cambios. Forzamos
# que /static/* y / nunca se cacheen.
class NoCacheStaticMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path == "/" or path.startswith("/static/") or path == "/favicon.ico":
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response


app.add_middleware(NoCacheStaticMiddleware)

# API Routers
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(factusol_router.router)
app.include_router(arca_router.router)
app.include_router(config_router.router)
app.include_router(credit_notes_router.router)
app.include_router(updates_router.router)

# Static files (frontend)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(str(STATIC_DIR / "favicon.ico"), media_type="image/x-icon")
