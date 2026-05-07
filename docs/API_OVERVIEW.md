# API Overview — NEXARO AI

**Base URL producción:** `https://<tu-servicio>.onrender.com`
**Base URL local:** `http://localhost:8000`
**Swagger UI:** `GET /docs` (solo en `ENVIRONMENT=development`)
**ReDoc:** `GET /redoc` (solo en `ENVIRONMENT=development`)

---

## Autenticación

La API usa **Bearer Token JWT**. Para endpoints privados:

```
Authorization: Bearer <access_token>
```

El token se obtiene en `POST /api/auth/login` y expira según `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 480 min = 8h).

---

## Endpoints Públicos

### `GET /health`
Estado del servicio.

**Response `200`**
```json
{
  "status": "ok",
  "environment": "development"
}
```

---

### `POST /api/auth/login`
Autenticación de administrador. Devuelve un JWT.

**Rate limit:** 10 req/min por IP

**Request body**
```json
{
  "username": "tu_admin_username",
  "password": "tu_admin_password"
}
```

**Response `200`**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errores**
| Código | Causa |
|---|---|
| `401` | Credenciales incorrectas |
| `429` | Rate limit superado |

---

### `POST /api/leads`
Crear un nuevo lead desde el formulario de captación.

**Rate limit:** 5 req/min por IP

**Request body**
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

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `name` | string | ✅ | Nombre completo |
| `email` | string (EmailStr) | ✅ | Email válido |
| `phone` | string | ❌ | Teléfono |
| `company` | string | ❌ | Nombre de empresa |
| `message` | string | ❌ | Mensaje del formulario |
| `source` | enum | ❌ | Fuente del lead (ver valores) |

**Valores de `source`:** `web` · `instagram` · `google` · `referral` · `whatsapp` · `other`

**Response `201`**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "María García",
  "email": "maria@empresa.com",
  "status": "new",
  "source": "web",
  "created_at": "2025-05-07T10:30:00Z"
}
```

**Comportamientos especiales**

| Situación | Respuesta | Motivo |
|---|---|---|
| Campo `_gotcha` relleno (bot) | `200` sin procesar | No revelar detección al bot |
| Mismo email en últimas 24h | `200` sin duplicar | No revelar deduplicación |
| Validación Pydantic falla | `422` con detalle | Email inválido, campo requerido vacío |
| Rate limit superado | `429` | Protección anti-abuso |

---

## Endpoints Privados

> Requieren `Authorization: Bearer <token>` en todas las peticiones.

---

### `GET /api/leads`
Listar leads con filtros opcionales y paginación.

**Query params**

| Param | Tipo | Descripción |
|---|---|---|
| `status` | string | Filtrar: `new` · `contacted` · `qualified` · `converted` · `discarded` |
| `source` | string | Filtrar: `web` · `instagram` · `google` · `referral` · `whatsapp` · `other` |
| `search` | string | Búsqueda en name, email, company |
| `skip` | int (default 0) | Paginación — offset |
| `limit` | int (default 50) | Paginación — max resultados |

**Response `200`**
```json
{
  "total": 87,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "María García",
      "email": "maria@empresa.com",
      "phone": "612345678",
      "company": "Clínica Dental",
      "message": "Quiero automatizar la captación...",
      "status": "new",
      "source": "web",
      "notes": null,
      "created_at": "2025-05-07T10:30:00Z",
      "updated_at": "2025-05-07T10:30:00Z"
    }
  ]
}
```

---

### `GET /api/leads/{id}`
Detalle completo de un lead.

**Response `200`** → objeto Lead completo (mismo formato que el item de la lista)

**Errores**
| Código | Causa |
|---|---|
| `401` | Token ausente o inválido |
| `404` | Lead no encontrado |

---

### `PATCH /api/leads/{id}`
Actualizar status y/o notas de un lead.

**Request body** (todos los campos son opcionales)
```json
{
  "status": "contacted",
  "notes": "Llamada realizada el 7 de mayo. Interesado en el plan Pro."
}
```

**Valores de `status`:** `new` · `contacted` · `qualified` · `converted` · `discarded`

**Response `200`** → objeto Lead actualizado

---

### `GET /api/stats`
Estadísticas del dashboard.

**Response `200`**
```json
{
  "total": 87,
  "by_status": {
    "new": 34,
    "contacted": 28,
    "qualified": 12,
    "converted": 9,
    "discarded": 4
  },
  "by_source": {
    "web": 45,
    "instagram": 22,
    "google": 11,
    "referral": 6,
    "whatsapp": 2,
    "other": 1
  },
  "daily_7d": [
    { "date": "2025-05-01", "count": 8 },
    { "date": "2025-05-02", "count": 12 },
    { "date": "2025-05-03", "count": 5 },
    { "date": "2025-05-04", "count": 9 },
    { "date": "2025-05-05", "count": 14 },
    { "date": "2025-05-06", "count": 7 },
    { "date": "2025-05-07", "count": 6 }
  ],
  "conversion_rate": 10.34
}
```

---

## Códigos de Error Globales

| Código | Descripción |
|---|---|
| `200` | OK (también usado en honeypot/deduplicación — silencioso) |
| `201` | Creado correctamente |
| `401` | Token ausente, inválido o expirado |
| `403` | Sin permisos para este recurso |
| `404` | Recurso no encontrado |
| `422` | Validación Pydantic fallida — body incluye detalle de los errores |
| `429` | Rate limit superado |
| `500` | Error interno — detalles ocultos en `ENVIRONMENT=production` |

---

## Cabeceras en Todas las Respuestas

```http
Content-Type: application/json
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'
```

---

## Ejemplos con curl

```bash
# Health check
curl http://localhost:8000/health

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"tu_password"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Crear lead
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Lead","email":"test@ejemplo.com","source":"web"}'

# Listar leads (autenticado)
curl http://localhost:8000/api/leads \
  -H "Authorization: Bearer $TOKEN"

# Stats (autenticado)
curl http://localhost:8000/api/stats \
  -H "Authorization: Bearer $TOKEN"

# Actualizar status
curl -X PATCH http://localhost:8000/api/leads/<UUID> \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"contacted","notes":"Llamada realizada."}'
```
