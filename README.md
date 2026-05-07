# NEXARO AI — Sistema de Captación y Gestión Automática de Clientes

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Tests](https://img.shields.io/badge/Tests-41%20passing-4CAF50?logo=pytest)](./backend/tests/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](./docker-compose.yml)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](./LICENSE)

> **Proyecto de portfolio académico y profesional** · MVP SaaS funcional que automatiza la captación de leads con landing pública, backend FastAPI y panel CRM administrable, con seguridad de nivel producción y 41 tests automatizados.

---

## Tabla de Contenidos

- [Problema que resuelve](#problema-que-resuelve)
- [Objetivo académico](#objetivo-académico)
- [Objetivo profesional](#objetivo-profesional)
- [Funcionalidades](#funcionalidades-principales)
- [Arquitectura](#arquitectura)
- [Stack tecnológico](#stack-tecnológico)
- [Seguridad implementada](#seguridad-implementada)
- [Endpoints API](#endpoints-api)
- [Testing](#testing)
- [Instalación local](#instalación-local)
- [Variables de entorno](#variables-de-entorno)
- [Despliegue](#despliegue)
- [Screenshots](#screenshots)
- [Estado del MVP](#estado-del-mvp)
- [Próximos pasos](#próximos-pasos)
- [Valor para recruiters](#valor-para-recruiters)

---

## Problema que resuelve

Las agencias digitales y consultoras pequeñas **pierden leads potenciales** por falta de automatización en la captación y seguimiento. El flujo habitual — formulario de contacto → email → Excel → olvido — no escala.

NEXARO AI elimina ese problema con:

- Una **landing embebible** con formulario de captación listo para producción
- Un **backend API REST** con validación, deduplicación y protección anti-bots
- Un **panel CRM** con login seguro, tabla filtrable y estadísticas en tiempo real

---

## Objetivo Académico

Proyecto desarrollado en el ciclo formativo **DAW/DAM** para demostrar competencias en:

- Desarrollo backend con **FastAPI** y arquitectura REST
- Persistencia con **PostgreSQL + SQLAlchemy + Alembic**
- Autenticación segura con **JWT**
- Frontend HTML/CSS/JS vanilla integrado con API REST
- Testing automatizado con **pytest** (41 tests)
- Despliegue real en cloud (**Render + Hostinger**)
- Containerización con **Docker Compose**

---

## Objetivo Profesional

Demostrar capacidad para diseñar, construir y desplegar un **SaaS MVP funcional** con criterios de seguridad y mantenibilidad de entorno profesional:

- Clean Architecture: separación Router → Service → Model
- Seguridad desde el diseño (security-by-design)
- Código preparado para escalar: servicios de email, WhatsApp y Calendar ya estructurados
- Documentación técnica completa orientada a equipo

---

## Funcionalidades Principales

| Módulo | Descripción | Estado |
|---|---|---|
| **Landing pública** | Formulario HTML con honeypot, validación y fuente de lead | ✅ |
| **Backend API** | FastAPI con todos los endpoints documentados en Swagger | ✅ |
| **Login JWT** | Autenticación con token firmado, expira en 8h | ✅ |
| **Panel CRM** | Dashboard admin: tabla de leads, filtros, estadísticas | ✅ |
| **Honeypot anti-bot** | Campo oculto — bots rechazados silenciosamente | ✅ |
| **Deduplicación 24h** | Mismo email no genera lead duplicado en 24h | ✅ |
| **Sanitización** | Strip HTML + detección de patrones de inyección SQL | ✅ |
| **Rate limiting** | slowapi por IP — desactivado automáticamente en tests | ✅ |
| **Security headers** | Middleware personalizado con cabeceras OWASP | ✅ |
| **Email service** | SMTP real o mock configurable vía `EMAIL_MOCK=true` | ✅ |
| **WhatsApp** | Placeholder Twilio listo para activar | 🔲 |
| **Google Calendar** | Placeholder listo para activar | 🔲 |
| **41 tests** | SQLite en memoria, rollback por test, sin PostgreSQL | ✅ |
| **Migraciones Alembic** | 2 versiones: tabla leads + trigger `updated_at` | ✅ |
| **Docker Compose** | Entorno local completo (app + PostgreSQL) en un comando | ✅ |

---

## Arquitectura

```
nexaro-ai/
├── frontend/
│   ├── index.html          # Landing pública con formulario de captación
│   └── admin.html          # Panel CRM (login, dashboard, tabla de leads)
│
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI: routers, CORS, middlewares, lifespan
│   │   ├── api/
│   │   │   ├── auth.py     # POST /api/auth/login
│   │   │   ├── leads.py    # CRUD leads (público + privado)
│   │   │   └── stats.py    # GET /api/stats (privado)
│   │   ├── core/
│   │   │   ├── config.py   # pydantic-settings — variables de entorno
│   │   │   ├── security.py # JWT encode/decode + require_admin dependency
│   │   │   └── logging.py  # Logging estructurado
│   │   ├── db/
│   │   │   ├── base.py     # DeclarativeBase SQLAlchemy
│   │   │   └── session.py  # Engine + get_db (compatible PostgreSQL y SQLite)
│   │   ├── middleware/
│   │   │   └── security.py # Middleware security headers
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
│   └── Procfile
│
├── docker-compose.yml       # App + PostgreSQL en un comando
├── .gitignore
└── LICENSE
```

**Patrón arquitectónico:** Layered — Router → Service → ORM Model → DB

**Decisión de diseño clave:** `db/session.py` detecta `TESTING=true` y usa SQLite en memoria en lugar de PostgreSQL, eliminando dependencias externas en el entorno de tests.

---

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| **Backend** | Python 3.11 + FastAPI |
| **Base de datos** | PostgreSQL 15 (prod) · SQLite en memoria (tests) |
| **ORM** | SQLAlchemy · Migraciones con Alembic |
| **Autenticación** | JWT con python-jose · bcrypt para contraseñas |
| **Rate Limiting** | slowapi |
| **Email** | SMTP directo (modo mock o real vía `.env`) |
| **Containerización** | Docker + Docker Compose |
| **Despliegue** | Render (backend + PostgreSQL) · Hostinger (frontend) |
| **Testing** | pytest + httpx AsyncClient |
| **Validación** | Pydantic v2 |

---

## Seguridad Implementada

> Análisis completo con código en [`docs/SECURITY_NOTES.md`](./docs/SECURITY_NOTES.md)

### JWT con expiración y firmas verificadas
- Token firmado con `SECRET_KEY` obligatoria desde variable de entorno
- Expiración configurable (`ACCESS_TOKEN_EXPIRE_MINUTES`, default 8h)
- `require_admin` como dependencia FastAPI reutilizable en todos los endpoints privados

### Rate Limiting — `slowapi`
- `POST /api/leads` → máx. 5 req/minuto por IP
- `POST /api/auth/login` → máx. 10 req/minuto por IP
- **Desactivado automáticamente** cuando `TESTING=true` (sin interferir en tests)

### Security Headers (middleware personalizado)
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'
```

### Honeypot Anti-Bot
Campo oculto en el formulario HTML. Si viene relleno → petición descartada silenciosamente con HTTP 200 (sin revelar la detección al bot).

### Deduplicación 24h
El mismo email no puede generar un nuevo lead en un periodo de 24 horas. Protege contra spam y datos duplicados.

### Sanitización de Entradas
- Strip de HTML en campos de texto libre
- Detección de patrones de inyección SQL antes de persistir
- Validación de tipos y longitudes con Pydantic v2

### Configuración Segura
- `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD` cargadas **exclusivamente** desde variables de entorno
- Validación en startup: la app no arranca en producción con valores por defecto
- `ENVIRONMENT=production` → errores internos nunca expuestos al cliente

---

## Endpoints API

> Documentación interactiva en `/docs` (solo disponible con `ENVIRONMENT=development`)

### Públicos

| Método | Ruta | Rate limit | Descripción |
|---|---|---|---|
| `GET` | `/health` | — | Estado del servicio |
| `POST` | `/api/leads` | 5/min por IP | Crear lead desde landing |
| `POST` | `/api/auth/login` | 10/min por IP | Login admin → JWT |

### Privados (`Authorization: Bearer <token>`)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/leads` | Listar leads (filtro `status`, búsqueda, paginación) |
| `GET` | `/api/leads/{id}` | Detalle de un lead |
| `PATCH` | `/api/leads/{id}` | Actualizar status y notas |
| `GET` | `/api/stats` | Total, by_status, by_source, daily_7d, conversion_rate |

### Payload `POST /api/leads`

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

`source` acepta: `web` · `instagram` · `google` · `referral` · `whatsapp` · `other`

---

## Testing

```bash
cd backend
TESTING=true python -m pytest tests/ -v
```

**41 tests — 100% passing · Sin PostgreSQL — SQLite en memoria con rollback por test**

| Suite | Descripción |
|---|---|
| `test_health.py` | Health check y respuesta básica |
| `test_auth.py` | Login correcto, credenciales inválidas, token expirado, acceso sin token |
| `test_leads.py` | CRUD completo, honeypot, deduplicación 24h, validación de campos, rate limit |
| `test_stats.py` | Estadísticas by_status, by_source, daily_7d, conversión, acceso no autorizado |

---

## Instalación Local

### Con Docker Compose (recomendado)

```bash
git clone https://github.com/Marbi8891/nexaro-ai.git
cd nexaro-ai

# Configurar variables de entorno
cp backend/.env.example backend/.env
# Edita backend/.env con tus valores

# Levantar todo (app + PostgreSQL)
docker-compose up -d

# Ejecutar migraciones
docker-compose exec app alembic upgrade head
```

### Sin Docker

```bash
git clone https://github.com/Marbi8891/nexaro-ai.git
cd nexaro-ai/backend

python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

pip install -r requirements.txt

cp .env.example .env
# Edita .env con tus valores

# Levantar PostgreSQL por separado:
docker-compose up -d db

# Migraciones
alembic upgrade head

# Servidor
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
python -m http.server 8080
# Landing:      http://localhost:8080/index.html
# Panel admin:  http://localhost:8080/admin.html
```

Accesos backend:
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs` (solo en `ENVIRONMENT=development`)

---

## Variables de Entorno

```env
# .env.example — copia a .env y rellena

# Entorno
ENVIRONMENT=development        # development | production
SECRET_KEY=                    # Obligatorio — openssl rand -hex 32

# Base de datos
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/nexaro_dev

# Admin
ADMIN_USERNAME=                # Obligatorio
ADMIN_PASSWORD=                # Obligatorio

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=480   # 8 horas por defecto

# CORS — array JSON
CORS_ORIGINS=["http://localhost:8080", "http://localhost:3000"]

# Email
EMAIL_MOCK=true                # true = solo logs, sin envío real
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

---

## Despliegue

> Guía completa en [`docs/DEPLOYMENT_GUIDE.md`](./docs/DEPLOYMENT_GUIDE.md)

### Backend → Render.com

1. New Web Service → repositorio `Marbi8891/nexaro-ai` → Root directory: `backend`
2. Build: `pip install -r requirements.txt`
3. Start: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Añadir PostgreSQL de Render → copiar `DATABASE_URL` interno a env vars
5. Configurar el resto de variables del `.env.example`

### Frontend → Hostinger

1. En `frontend/index.html` y `frontend/admin.html`, reemplazar `http://localhost:8000` por la URL de Render
2. Subir ambos HTML a `public_html` vía File Manager de Hostinger

---

## Screenshots

Añadir capturas en `screenshots/` antes de la evaluación:

| Archivo | Vista |
|---|---|
| `screenshots/landing.png` | Landing pública con formulario |
| `screenshots/admin-login.png` | Pantalla de login del CRM |
| `screenshots/admin-dashboard.png` | Dashboard con leads y stats |
| `screenshots/swagger-api.png` | Swagger UI con endpoints expandidos |
| `screenshots/tests-passing.png` | Terminal con 41 tests en verde |

Ver instrucciones en [`screenshots/README.md`](./screenshots/README.md).

---

## Estado del MVP

| Funcionalidad | Estado |
|---|---|
| Landing + formulario captación | ✅ |
| Backend FastAPI con todos los endpoints | ✅ |
| Login JWT + panel CRM | ✅ |
| Honeypot, sanitización, deduplicación 24h | ✅ |
| Rate limiting, security headers | ✅ |
| Email service (mock activado, SMTP listo) | ✅ |
| Migraciones Alembic + trigger `updated_at` | ✅ |
| 41 tests pasando | ✅ |
| Docker Compose (app + PostgreSQL) | ✅ |
| SMTP real activado | 🔲 configurable en `.env` |
| WhatsApp Twilio | 🔲 placeholder listo |
| Google Calendar | 🔲 placeholder listo |

---

## Próximos Pasos

- [ ] Activar SMTP real con Resend o SendGrid
- [ ] Integrar Twilio para notificaciones WhatsApp al recibir un lead
- [ ] CI/CD con GitHub Actions: lint + tests en cada PR
- [ ] Exportación de leads a CSV/Excel desde el dashboard
- [ ] Autenticación con Google OAuth2
- [ ] Multi-tenancy: múltiples agencias con datos aislados

---

## Valor para Recruiters

| Competencia | Evidencia concreta |
|---|---|
| **Backend FastAPI** | API REST completa, middleware personalizado, lifespan |
| **Diseño de APIs REST** | 7 endpoints, Swagger docs, respuestas consistentes |
| **Autenticación JWT** | Token firmado, dependencia reutilizable `require_admin` |
| **Seguridad desde el diseño** | Rate limiting, headers, honeypot, deduplicación, sanitización |
| **Testing con pytest** | 41 tests, SQLite en memoria, sin dependencias externas |
| **Arquitectura limpia** | Router / Service / Model / Schema separados |
| **Full-stack** | Frontend HTML/JS vanilla + backend FastAPI integrado |
| **DevOps básico** | Docker Compose, Dockerfile, Procfile, Alembic migrations |
| **Despliegue real** | Producción en Render + Hostinger con dominio propio |
| **Mentalidad de producto** | Servicios de email/WhatsApp/Calendar ya estructurados para escalar |

---

## Autor

**Mrabeh Fathi Boussayff**
- 🌐 [mrabehfathi.com](https://mrabehfathi.com)
- 📧 hola@mrabehfathi.com
- 🐙 [github.com/Marbi8891](https://github.com/Marbi8891)
- 📍 Leganés, Madrid

*Estudiante DAW/DAM · Fundador de NEXARO TECH, S.L. · Red Team 200h + Blue Team 250h (INCIBE)*

---

## Licencia

MIT — ver [LICENSE](./LICENSE)
