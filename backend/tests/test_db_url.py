from app.db.session import _normalize_db_url


def test_url_render_postgres():
    assert _normalize_db_url("postgres://u:p@h:5432/db") == "postgresql://u:p@h:5432/db"


def test_url_asyncpg_legacy():
    assert _normalize_db_url("postgresql+asyncpg://u:p@h/db") == "postgresql://u:p@h/db"


def test_url_sqlite_sin_cambios():
    assert _normalize_db_url("sqlite:///:memory:") == "sqlite:///:memory:"
