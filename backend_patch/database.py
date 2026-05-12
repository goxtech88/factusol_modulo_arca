import sqlite3

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./licenses.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def auto_migrate():
    """Garantiza tablas nuevas y agrega columnas faltantes a tablas existentes (SQLite, idempotente)."""
    # Importar modelos para que Base conozca las tablas nuevas antes de create_all
    import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Migraciones de columnas sobre tablas que pudieron existir antes (ARCA en prod):
    migrations = [
        # Tablas ARCA preexistentes
        ("licenses", "app_version", "VARCHAR(20)"),
        ("licenses", "last_seen",   "DATETIME"),
        # Lead.cuit: vincula con License cuando el lead viene del registro de la app
        ("leads",    "cuit",        "VARCHAR(20)"),
    ]

    # Indices a crear despues de las columnas (idempotente).
    index_migrations = [
        ("ix_leads_cuit", "leads", "cuit"),
    ]

    with engine.connect() as conn:
        existing_tables = {row[0] for row in conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )).fetchall()}

        for table, column, col_type in migrations:
            if table not in existing_tables:
                # La tabla la creará create_all; saltamos.
                continue
            result = conn.execute(text(f"PRAGMA table_info({table})"))
            cols = {row[1] for row in result.fetchall()}
            if column not in cols:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                print(f"  [migrate] {table}.{column} ({col_type})")

        # Indices: CREATE INDEX IF NOT EXISTS es idempotente
        for idx_name, table, column in index_migrations:
            if table in existing_tables:
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})"))

        conn.commit()

    print("[migrate] auto_migrate OK — tablas creadas/verificadas")
