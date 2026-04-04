# NexaroAI Agency

> Sistema completo de captación y conversión de leads con IA para agencias de automatización.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## ¿Qué es esto?

Sistema full-stack listo para producción que incluye:

- **Landing page** de alta conversión (HTML/CSS/JS, sin dependencias)
- **API REST** con FastAPI — gestión completa de leads
- **Panel CRM** admin con login JWT y gestión de estados
- **Automatización** de email/WhatsApp al recibir un lead
- **Seguridad real**: rate limiting, honeypot, sanitización, security headers

---

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | HTML · CSS · JavaScript vanilla |
| Backend | Python 3.11 · FastAPI · SQLAlchemy · Pydantic |
| Base de datos | PostgreSQL 16 |
| Seguridad | JWT · slowapi · honeypot · hmac timing-safe |
| Despliegue | Hostinger (frontend) · Render (backend) · Neon (DB) |

---

## Estructura

```
nexaro-ai/
├── frontend/
│   ├── index.html          ← Landing page conectada a la API
│   └── admin.html          ← Panel CRM con login JWT
├── backend/
│   ├── app/
│   │   ├── main.py         ← FastAPI app + middlewares + CORS
│   │   ├── api/            ← leads.py · stats.py · auth.py
│   │   ├── core/           ← config · security · logging
│   │   ├── db/             ← session · base
│   │   ├── middleware/     ← security headers
│   │   ├── models/         ← Lead (SQLAlchemy)
│   │   ├── schemas/        ← Pydantic con validación estricta
│   │   ├── services/       ← email · whatsapp · calendar
│   │   └── utils/          ← rate_limit · sanitize
│   ├── alembic/            ← Migraciones de BD
│   ├── Dockerfile
│   ├── Procfile
│   ├── requirements.txt
│   └── .env.example
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Instalación local

### Con Docker (recomendado)

```bash
git clone https://github.com/TU_USUARIO/nexaro-ai.git
cd nexaro-ai

cp backend/.env.example backend/.env

docker-compose up --build
```

- API → `http://localhost:8000`
- Docs → `http://localhost:8000/docs`
- Frontend → abre `frontend/index.html` en el navegador

### Sin Docker

```bash
# Requiere PostgreSQL corriendo localmente
createdb nexaroai

cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # edita con tus valores

alembic upgrade head            # crea las tablas
uvicorn app.main:app --reload --port 8000
```

---

## Endpoints

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/health` | ❌ | Estado del servicio |
| POST | `/api/leads` | ❌ | Crear lead (formulario web) |
| GET | `/api/leads` | ✅ JWT | Listar leads con filtros |
| GET | `/api/leads/{id}` | ✅ JWT | Detalle de lead |
| PATCH | `/api/leads/{id}` | ✅ JWT | Actualizar estado/notas |
| GET | `/api/stats` | ✅ JWT | KPIs del dashboard |
| POST | `/api/auth/login` | ❌ | Login admin → JWT |

---

## Seguridad

- Rate limiting por IP (slowapi): 5/min en leads, 10/min en login
- Honeypot anti-bot en formulario (frontend + backend)
- Sanitización de inputs y detección de patrones de inyección
- Login con `hmac.compare_digest` (timing-safe)
- Security headers en todas las respuestas
- Docs API desactivadas en producción
- Proceso Docker corre como usuario no-root

---

## Despliegue

### 1. Base de datos — Neon (gratis)
1. Crea cuenta en [neon.tech](https://neon.tech)
2. New Project → copia la `DATABASE_URL`

### 2. Backend — Render
1. New Web Service → conecta este repo
2. Root Directory: `backend`
3. Build: `pip install -r requirements.txt && alembic upgrade head`
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Añade las variables de entorno del `.env.example`

### 3. Frontend — Hostinger
1. Edita `frontend/admin.html` → cambia `const API = "https://TU-BACKEND.onrender.com"`
2. Sube `index.html` y `admin.html` a `public_html/`

---

## Variables de entorno necesarias en Render

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://...neon.tech/nexaroai?sslmode=require
SECRET_KEY=<openssl rand -hex 32>
CORS_ORIGINS=["https://nexaroai.agency"]
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<password seguro>
EMAIL_MOCK=false
SMTP_USER=tu@gmail.com
SMTP_PASSWORD=<app password Gmail>
```

---

## Licencia

MIT — NexaroAI Agency © 2025
