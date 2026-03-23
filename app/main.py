"""
Factusol Módulo ARCA - Web Application
Punto de entrada de la aplicación FastAPI.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.database import init_db, SessionLocal
from app.auth import hash_password
from app.models.user import User

from app.routers import auth_router, users_router, factusol_router, arca_router, config_router


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

    print("🚀 Factusol Arca by Goxtech iniciado")
    yield
    # Shutdown
    auto_validate.stop_background_task()
    print("👋 Factusol Arca by Goxtech detenido")


app = FastAPI(
    title="Factusol Arca by Goxtech",
    description="Módulo de facturación electrónica ARCA para Factusol",
    version="1.0.0",
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

# API Routers
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(factusol_router.router)
app.include_router(arca_router.router)
app.include_router(config_router.router)

# Static files (frontend)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(str(STATIC_DIR / "favicon.ico"), media_type="image/x-icon")
