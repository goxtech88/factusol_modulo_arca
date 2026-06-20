"""
Base de datos SQLite para datos de la app (usuarios, logs de CAE).
La DB se crea en DATA_DIR para soportar multi-instancia.
"""
import greenlet  # noqa: F401 — dep de SQLAlchemy 2.x; import explicito para que PyInstaller lo detecte
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
    """Crea todas las tablas si no existen y aplica migraciones automaticas."""
    from app.models.user import User, UserPuntoVenta  # noqa: F401
    from app.models.cae_log import CAELog  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _auto_migrate()


def _auto_migrate():
    """Agrega columnas faltantes a tablas existentes (SQLite, sin Alembic).

    Este mecanismo simple mira PRAGMA table_info y hace ALTER TABLE ADD COLUMN
    para cada columna que falta. Solo soporta agregar columnas nullable.
    """
    # Columnas esperadas en cae_logs (nombre -> definicion SQL)
    expected_cae_logs = {
        "motivo": "VARCHAR(50)",
        "cmp_asoc_tipo": "INTEGER",
        "cmp_asoc_pv": "INTEGER",
        "cmp_asoc_nro": "INTEGER",
        "fecha_cbte": "VARCHAR(10)",
    }
    try:
        with engine.begin() as conn:
            from sqlalchemy import text
            existing = {
                row[1] for row in conn.exec_driver_sql("PRAGMA table_info(cae_logs)").fetchall()
            }
            for col, ddl in expected_cae_logs.items():
                if col not in existing:
                    conn.exec_driver_sql(f"ALTER TABLE cae_logs ADD COLUMN {col} {ddl}")
                    print(f"[migrate] cae_logs: columna {col} agregada")
    except Exception as e:
        print(f"[migrate] Error en auto-migracion: {e}")
