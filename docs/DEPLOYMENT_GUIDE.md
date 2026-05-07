# Deployment Guide — NEXARO AI

---

## Arquitectura de Despliegue

```
Internet
    │
    ├── mrabehfathi.com (Hostinger)
    │   ├── index.html   → Landing pública con formulario
    │   └── admin.html   → Panel CRM
    │           │
    │           │ fetch() a la API
    │           ▼
    └── <servicio>.onrender.com (Render)
            │
        FastAPI (uvicorn)
            │
        PostgreSQL (Render Managed DB)
```

El frontend es HTML estático servido desde Hostinger. El backend es un Web Service en Render conectado a una base de datos PostgreSQL gestionada por Render.

---

## Opción 1 — Docker Compose (local)

La forma más rápida de levantar el entorno completo:

```bash
git clone https://github.com/Marbi8891/nexaro-ai.git
cd nexaro-ai

# Configurar variables de entorno
cp backend/.env.example backend/.env
# Edita backend/.env con tus valores reales

# Levantar app + PostgreSQL
docker-compose up -d

# Ejecutar migraciones
docker-compose exec app alembic upgrade head

# Ver logs
docker-compose logs -f app
```

Accesos:
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

---

## Opción 2 — Sin Docker (local)

```bash
git clone https://github.com/Marbi8891/nexaro-ai.git
cd nexaro-ai/backend

# Entorno virtual
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

pip install -r requirements.txt

# Variables de entorno
cp .env.example .env
# Edita .env

# Solo la DB en Docker
docker-compose up -d db

# Migraciones
alembic upgrade head

# Servidor
uvicorn app.main:app --reload --port 8000
```

### Frontend local

```bash
cd frontend
python -m http.server 8080
```

- Landing: `http://localhost:8080/index.html`
- Admin: `http://localhost:8080/admin.html`

---

## Despliegue en Render — Backend

### Paso 1: Crear la base de datos

1. Render Dashboard → **New** → **PostgreSQL**
2. Name: `nexaro-db`, Region: Frankfurt (EU)
3. Crea la DB y copia la **Internal Database URL**

### Paso 2: Crear el Web Service

1. Render Dashboard → **New** → **Web Service**
2. Conectar repositorio `Marbi8891/nexaro-ai`
3. Configurar:

| Campo | Valor |
|---|---|
| **Name** | `nexaro-ai-backend` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### Paso 3: Variables de entorno en Render

Panel del servicio → **Environment** → Add environment variable:

| Variable | Valor |
|---|---|
| `ENVIRONMENT` | `production` |
| `DATABASE_URL` | Internal URL de la DB de Render (reemplaza `postgres://` por `postgresql+asyncpg://`) |
| `SECRET_KEY` | `openssl rand -hex 32` → pegar el resultado |
| `ADMIN_USERNAME` | Tu usuario admin |
| `ADMIN_PASSWORD` | Contraseña segura (mín. 12 chars) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` |
| `CORS_ORIGINS` | `["https://mrabehfathi.com", "https://www.mrabehfathi.com"]` |
| `EMAIL_MOCK` | `true` (hasta configurar SMTP) |

> ⚠️ **Importante:** Render provee URLs con prefijo `postgres://`. Debes reemplazarlo por `postgresql+asyncpg://` para que funcione con SQLAlchemy async.

### Paso 4: Deploy

Render despliega automáticamente en cada push a `main`. Para forzar un deploy manual: panel del servicio → **Manual Deploy** → **Deploy latest commit**.

---

## Despliegue en Hostinger — Frontend

### Paso 1: Actualizar URLs en el frontend

Antes de subir los archivos, reemplaza `http://localhost:8000` por la URL de Render en ambos archivos:

```bash
# En frontend/index.html y frontend/admin.html
# Reemplazar: http://localhost:8000
# Por:        https://nexaro-ai-backend.onrender.com
```

### Paso 2: Subir archivos

1. Panel de Hostinger → **File Manager**
2. Navegar a `public_html/`
3. Subir `frontend/index.html` → renombrar a `index.html` (o mantener nombre)
4. Subir `frontend/admin.html`

### Paso 3: (Opcional) Dominio personalizado para la API

Si quieres `api.mrabehfathi.com` → Render:

1. Hostinger → DNS Zone → Añadir registro CNAME:
   ```
   Tipo:   CNAME
   Nombre: api
   Valor:  nexaro-ai-backend.onrender.com
   TTL:    3600
   ```
2. Render → tu servicio → **Settings** → **Custom Domains** → añadir `api.mrabehfathi.com`
3. Render gestiona el certificado TLS automáticamente (Let's Encrypt)

---

## Tests antes de desplegar

```bash
cd backend
TESTING=true python -m pytest tests/ -v --tb=short
```

**Resultado esperado:** 41 tests passing, 0 failed.

Si hay fallos, **no desplegar** hasta resolverlos.

---

## Comandos Alembic útiles

```bash
# Ver estado de migraciones
alembic current

# Aplicar todas las migraciones pendientes
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Crear nueva migración (tras cambios en models/)
alembic revision --autogenerate -m "descripcion_del_cambio"

# Historial completo
alembic history --verbose
```

---

## Troubleshooting

### `sqlalchemy.exc.OperationalError: could not connect to server`
- Verifica que `DATABASE_URL` usa `postgresql+asyncpg://` (no `postgres://`)
- En local: ¿está corriendo el contenedor de PostgreSQL? → `docker-compose up -d db`

### `ValueError: SECRET_KEY insegura en producción`
La app no arranca porque `SECRET_KEY` está vacía o usa un valor por defecto. Genera una nueva:
```bash
openssl rand -hex 32
```

### `ModuleNotFoundError` al ejecutar tests
Ejecuta desde el directorio correcto con el entorno virtual activado:
```bash
cd backend
source venv/bin/activate
TESTING=true python -m pytest tests/ -v
```

### `alembic.util.exc.CommandError: Can't locate revision`
```bash
alembic stamp head    # Sincronizar estado sin aplicar migraciones
alembic upgrade head  # Aplicar desde el estado actual
```

### Render: `Build failed`
- Revisa que `Root Directory` está configurado como `backend`
- Comprueba que `requirements.txt` existe en `backend/requirements.txt`

### Frontend: `CORS error` en producción
- Verifica que `CORS_ORIGINS` incluye la URL de Hostinger exacta (con y sin `www`)
- Formato correcto: `["https://mrabehfathi.com", "https://www.mrabehfathi.com"]`

---

## Variables de Entorno — Referencia Completa

```env
# ─── Entorno ──────────────────────────────────────
ENVIRONMENT=development        # development | production

# ─── Seguridad ────────────────────────────────────
SECRET_KEY=                    # openssl rand -hex 32 → mín 32 chars
ADMIN_USERNAME=                # Usuario del panel CRM
ADMIN_PASSWORD=                # Mín 12 chars en producción

# ─── Base de datos ────────────────────────────────
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# ─── JWT ──────────────────────────────────────────
ACCESS_TOKEN_EXPIRE_MINUTES=480   # 8h por defecto

# ─── CORS ─────────────────────────────────────────
CORS_ORIGINS=["http://localhost:8080"]

# ─── Email ────────────────────────────────────────
EMAIL_MOCK=true                # true = solo logs | false = SMTP real
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu@email.com
SMTP_PASSWORD=

# ─── Tests ────────────────────────────────────────
# TESTING=true se pasa como variable de entorno en CLI, no en .env
```
