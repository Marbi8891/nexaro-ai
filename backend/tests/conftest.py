"""
Fixtures de test para NexaroAI API.
Usa SQLite en memoria para aislar completamente los tests de producción.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Sobreescribir variables de entorno ANTES de importar la app
# para evitar que session.py intente conectar a PostgreSQL
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "testsecretkey32charslong1234567890")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "CambiaMeEnProduccion2024!")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("CORS_ORIGINS", '["http://localhost:8080"]')
os.environ.setdefault("EMAIL_MOCK", "true")

from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402

# Motor SQLite propio — sin pool_size ni max_overflow (no soportados por SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Crea todas las tablas antes de los tests, las borra al finalizar."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """Sesión de DB que hace rollback tras cada test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """TestClient con DB sobreescrita por la sesión de test."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    """Cabeceras con token JWT válido para endpoints privados."""
    res = client.post("/api/auth/login", json={"username": "admin", "password": "CambiaMeEnProduccion2024!"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_lead(client):
    """Crea un lead de prueba y devuelve sus datos."""
    payload = {
        "name": "Test Usuario",
        "email": "test@ejemplo.com",
        "phone": "600123456",
        "company": "Empresa Test",
        "message": "Mensaje de prueba para test",
        "source": "web",
    }
    res = client.post("/api/leads", json=payload)
    assert res.status_code == 201
    return res.json()
