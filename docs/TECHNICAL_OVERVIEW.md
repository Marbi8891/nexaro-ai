# Technical Overview — NEXARO AI

---

## Stack y Versiones

| Componente | Tecnología |
|---|---|
| Runtime | Python 3.11 |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Migraciones | Alembic |
| Validación | Pydantic v2 |
| DB producción | PostgreSQL 15 |
| DB tests | SQLite en memoria |
| Auth | JWT (python-jose) + bcrypt |
| Rate limiting | slowapi |
| Email | SMTP directo (modo mock o real) |
| Contenedor | Docker + Docker Compose |
| Despliegue | Render (backend) + Hostinger (frontend) |

---

## Arquitectura en Capas

```
HTTP Request
     │
     ▼
┌────────────────────┐
│   FastAPI Router   │  Validación Pydantic, autenticación, rate limit
│  (api/*.py)        │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│    Service Layer   │  Lógica de negocio: deduplicación, notificaciones
│  (services/*.py)   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│   SQLAlchemy ORM   │  Queries, transacciones
│  (models/*.py)     │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  PostgreSQL / SQLite│ Persistencia (prod / tests)
└────────────────────┘
```

**Principio de acoplamiento**: siempre hacia abajo. Los routers no acceden a la DB directamente. Los modelos no contienen lógica de negocio.

---

## Estructura de Módulos

```
backend/app/
├── main.py                 # Punto de entrada
│                           # Registra routers, CORS, middleware, lifespan
├── api/
│   ├── auth.py             # POST /api/auth/login
│   ├── leads.py            # GET|POST /api/leads, GET|PATCH /api/leads/{id}
│   └── stats.py            # GET /api/stats
├── core/
│   ├── config.py           # Settings con pydantic-settings
│   ├── security.py         # JWT + require_admin dependency
│   └── logging.py          # Logging estructurado
├── db/
│   ├── base.py             # DeclarativeBase
│   └── session.py          # Engine + get_db (detecta TESTING=true)
├── middleware/
│   └── security.py         # BaseHTTPMiddleware — security headers
├── models/
│   └── lead.py             # ORM Lead + enums LeadStatus, LeadSource
├── schemas/
│   └── lead.py             # LeadCreate, LeadUpdate, LeadOut, LeadListOut
├── services/
│   ├── email_service.py    # send_lead_notification() — mock o SMTP real
│   ├── whatsapp_service.py # Placeholder Twilio (no activo)
│   └── calendar_service.py # Placeholder Google Calendar (no activo)
└── utils/
    ├── rate_limit.py       # Limiter slowapi (vacío si TESTING=true)
    └── sanitize.py         # strip_html() + detect_injection()
```

---

## Esquema de Base de Datos

```sql
CREATE TABLE leads (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(254) NOT NULL,
    phone       VARCHAR(20),
    company     VARCHAR(100),
    message     TEXT,
    status      VARCHAR(20) DEFAULT 'new',
    -- Enum: new | contacted | qualified | converted | discarded
    source      VARCHAR(20) DEFAULT 'web',
    -- Enum: web | instagram | google | referral | whatsapp | other
    notes       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Trigger para updated_at automático (migración 0002)
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER leads_updated_at
BEFORE UPDATE ON leads
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

---

## Flujo de Autenticación

```
POST /api/auth/login  { username, password }
    │
    ├─ Verificar ADMIN_USERNAME (env var) — constante tiempo
    ├─ bcrypt.checkpw(password, stored_hash)
    ├─ Generar JWT con { sub: username, exp: now + ACCESS_TOKEN_EXPIRE_MINUTES }
    └─ Devolver { access_token, token_type: "bearer" }

Endpoints privados:
    Header: Authorization: Bearer <token>
    │
    └─ require_admin dependency:
        ├─ Extraer token del header
        ├─ jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        ├─ Verificar expiración
        └─ Devolver usuario o raise 401
```

**Decisión de scope:** Sin refresh tokens en este MVP. El token de acceso dura 8h (configurable), suficiente para el uso diario del panel admin. Un sistema con múltiples usuarios necesitaría refresh tokens — está en el roadmap.

---

## Flujo de Captación de Lead

```
POST /api/leads  { name, email, phone, company, message, source }
    │
    ├─ 1. Rate limit: ≤5 req/min por IP (slowapi)
    ├─ 2. Pydantic: validar tipos, longitudes, formato email
    ├─ 3. Honeypot: si _gotcha != "" → HTTP 200 silencioso (bot detectado)
    ├─ 4. Sanitización: sanitize.strip_html() + sanitize.detect_injection()
    ├─ 5. Deduplicación 24h: ¿existe lead con mismo email en últimas 24h?
    │       └─ Si existe → HTTP 200 silencioso (sin revelar al usuario)
    ├─ 6. Persistir en DB → Lead con status="new"
    ├─ 7. email_service.send_lead_notification() (mock o SMTP)
    └─ 8. Response: { id, created_at }
```

**Por qué HTTP 200 en honeypot y deduplicación:** devolver 400 o 429 revelaría al bot o al usuario que fue detectado. Devolver 200 sin procesar es la respuesta más segura.

---

## Gestión de Entornos

### `db/session.py` — compatibilidad PostgreSQL/SQLite

```python
if settings.TESTING:
    # SQLite en memoria — sin PostgreSQL, sin migraciones
    engine = create_engine("sqlite:///:memory:", ...)
else:
    # PostgreSQL en producción
    engine = create_engine(settings.DATABASE_URL, ...)
```

### `utils/rate_limit.py` — slowapi en tests

```python
if settings.TESTING:
    # Limiter vacío — no bloquea peticiones en tests
    limiter = Limiter(key_func=get_remote_address, enabled=False)
else:
    limiter = Limiter(key_func=get_remote_address)
```

Estas dos decisiones permiten ejecutar los 41 tests sin ninguna dependencia externa.

---

## Docker Compose

```yaml
# docker-compose.yml (raíz del proyecto)
services:
  app:
    build: ./backend
    ports: ["8000:8000"]
    env_file: ./backend/.env
    depends_on: [db]

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: nexaro_dev
      POSTGRES_USER: nexaro
      POSTGRES_PASSWORD: nexaro_local
    ports: ["5432:5432"]
    volumes: [postgres_data:/var/lib/postgresql/data]
```

```bash
# Levantar todo
docker-compose up -d

# Migraciones
docker-compose exec app alembic upgrade head

# Ver logs
docker-compose logs -f app
```

---

## Tests — Arquitectura

```
backend/tests/
├── conftest.py         # Fixtures globales
│   ├── engine          # SQLite :memory:
│   ├── tables          # create_all / drop_all por sesión
│   ├── db_session      # Rollback por test (aislamiento)
│   └── client          # httpx.TestClient con override de get_db
├── test_health.py      # GET /health → 200
├── test_auth.py        # Login correcto/incorrecto, token inválido, acceso denegado
├── test_leads.py       # Crear lead, honeypot, deduplicación, validación, CRUD
└── test_stats.py       # Stats autenticadas, sin auth → 401, valores correctos
```

### Patrón de fixture

```python
@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()   # ← Cada test empieza con DB limpia
    connection.close()
```

---

## Decisiones de Performance

| Decisión | Justificación |
|---|---|
| Índice en `leads.email` | Deduplicación 24h hace lookup por email en cada POST |
| Índice en `leads.created_at` | Stats `daily_7d` filtra por fecha frecuentemente |
| `EMAIL_MOCK=true` por defecto | SMTP síncrono — en desarrollo bloquearía el event loop |
| Pydantic v2 | ~5-10x más rápido en validación respecto a v1 |
| bcrypt rounds=12 | Equilibrio seguridad/latencia — ~250ms por hash en hardware estándar |
