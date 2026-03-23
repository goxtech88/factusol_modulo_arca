"""
Base de datos SQLite para datos de la app (usuarios, logs de CAE).
La DB se crea en DATA_DIR para soportar multi-instancia.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATA_DIR

DATABASE_PATH = DATA_DIR / "app_data.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency para FastAPI: provee una sesión de DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Crea todas las tablas si no existen."""
    from app.models.user import User, UserPuntoVenta  # noqa: F401
    from app.models.cae_log import CAELog  # noqa: F401
    Base.metadata.create_all(bind=engine)
