# NexaroAI Agency

Sistema de captación y conversión de leads para agencia de IA.  
Landing pública + backend FastAPI + panel CRM admin.

---

## Arquitectura real

```
nexaro-ai/
├── frontend/
│   ├── index.html          # Landing pública con formulario de captación
│   └── admin.html          # Panel CRM (login, dashboard, tabla, modal)
│
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI: routers, CORS, middlewares, lifespan
│   │   ├── api/
│   │   │   ├── auth.py     # POST /api/auth/login
│   │   │   ├── leads.py    # CRUD leads (público + privado)
│   │   │   └── stats.py    # GET /api/stats (privado)
│   │   ├── core/
│   │   │   ├── config.py   # pydantic-settings, variables de entorno
│   │   │   ├── security.py # JWT + require_admin dependency
│   │   │   └── logging.py  # Logging estructurado
│   │   ├── db/
│   │   │   ├── base.py     # DeclarativeBase
│   │   │   └── session.py  # Engine + get_db (compatible PG y SQLite)
│   │   ├── middleware/
│   │   │   └── security.py # Security headers
│   │   ├── models/
│   │   │   └── lead.py     # ORM Lead con enums LeadStatus / LeadSource
│   │   ├── schemas/
│   │   │   └── lead.py     # LeadCreate, LeadUpdate, LeadOut, LeadListOut
│   │   ├── services/
│   │   │   ├── email_service.py     # SMTP real o mock (EMAIL_MOCK=true)
│   │   │   ├── whatsapp_service.py  # Placeholder Twilio
│   │   │   └── calendar_service.py  # Placeholder Google Calendar
│   │   └── utils/
│   │       ├── rate_limit.py  # slowapi (desactivado en TESTING=true)
│   │       └── sanitize.py    # Sanitización HTML + detección inyección SQL
│   ├── alembic/versions/
│   │   ├── 0001_create_leads_table.py
│   │   └── 0002_updated_at_trigger.py
│   ├── tests/
│   │   ├── conftest.py     # SQLite en memoria, rollback por test
│   │   ├── test_health.py
│   │   ├── test_auth.py
│   │   ├── test_leads.py
│   │   └── test_stats.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── Procfile
│   └── .env.example
│
└── docker-compose.yml
```

---

## Endpoints

### Públicos

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Estado de la API |
| `POST` | `/api/leads` | Crear lead desde landing |
| `POST` | `/api/auth/login` | Login admin — devuelve JWT |

### Privados (`Authorization: Bearer <token>`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/leads` | Listar leads (filtro status, búsqueda, paginación) |
| `GET` | `/api/leads/{id}` | Detalle de un lead |
| `PATCH` | `/api/leads/{id}` | Actualizar status y notas |
| `GET` | `/api/stats` | Total, by_status, by_source, daily_7d, conversion_rate |

### POST /api/leads — payload

```json
{
  "name": "María García",
  "email": "maria@empresa.com",
  "phone": "612345678",
  "company": "Clínica Dental",
  "message": "Quiero automatizar la captación de pacientes",
  "source": "web"
}
```

`source` acepta: `web` `instagram` `google` `referral` `whatsapp` `other`

---

## Instalación local

```bash
git clone https://github.com/Marbi8891/nexaro-ai.git
cd nexaro-ai/backend

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # editar SECRET_KEY, ADMIN_PASSWORD, DATABASE_URL
```

Levantar PostgreSQL:

```bash
cd ..   # raíz del proyecto
docker-compose up -d db
```

Migraciones y arranque:

```bash
cd backend
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Swagger disponible en `http://localhost:8000/docs` (solo `ENVIRONMENT=development`).

Frontend — abrir directamente o servir:

```bash
cd ../frontend
python -m http.server 8080
# Panel admin: http://localhost:8080/admin.html
```

---

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `ENVIRONMENT` | `development` o `production` |
| `SECRET_KEY` | Clave JWT — generar con `openssl rand -hex 32` |
| `DATABASE_URL` | URL PostgreSQL |
| `ADMIN_USERNAME` | Usuario del panel admin |
| `ADMIN_PASSWORD` | Contraseña del panel admin |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración JWT (default 480 = 8h) |
| `CORS_ORIGINS` | Array JSON de orígenes permitidos |
| `EMAIL_MOCK` | `true` = solo logs, no envía email real |
| `SMTP_HOST/PORT/USER/PASSWORD` | Configuración SMTP para email real |

---

## Tests

```bash
cd backend
TESTING=true python -m pytest tests/ -v
```

41 tests. Sin PostgreSQL — usa SQLite en memoria con rollback por test.

---

## Despliegue: Render (backend) + Hostinger (frontend)

**Backend en Render:**
1. Web Service → directorio `backend`
2. Build: `pip install -r requirements.txt && alembic upgrade head`
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Añadir PostgreSQL de Render → copiar `DATABASE_URL` a env vars
5. Añadir el resto de variables de `.env.example`

**Frontend en Hostinger:**
1. En `frontend/index.html` y `frontend/admin.html`, cambiar `http://localhost:8000` por la URL de Render
2. Subir ambos HTML a `public_html`

---

## Estado del MVP

| Funcionalidad | Estado |
|---------------|--------|
| Landing + formulario captación | ✅ |
| Backend FastAPI con todos los endpoints | ✅ |
| Login JWT + panel CRM | ✅ |
| Honeypot, sanitización, deduplicación 24h | ✅ |
| Rate limiting, security headers | ✅ |
| Emails (mock activado, SMTP listo) | ✅ |
| Migraciones Alembic + trigger updated_at | ✅ |
| 41 tests pasando | ✅ |
| SMTP real configurado | 🔲 configurable en .env |
| WhatsApp Twilio activado | 🔲 placeholder listo |
| Google Calendar activado | 🔲 placeholder listo |

---

## Licencia

MIT
