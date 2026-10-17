from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


def _normalize_db_url(url: str) -> str:
    """Render entrega 'postgres://' y la guía antigua usaba '+asyncpg'; el motor es síncrono (psycopg2)."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url.replace("postgresql+asyncpg://", "postgresql://", 1)


DATABASE_URL = _normalize_db_url(settings.DATABASE_URL)

# SQLite no soporta pool_size ni max_overflow — solo PostgreSQL/MySQL
_is_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=not _is_sqlite,
    **({} if _is_sqlite else {"pool_size": 5, "max_overflow": 10}),
    **({"connect_args": {"check_same_thread": False}} if _is_sqlite else {}),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
