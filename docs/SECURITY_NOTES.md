# Security Notes — NEXARO AI

> Análisis técnico de seguridad para revisores de código y evaluadores.

---

## Filosofía

NEXARO AI aplica **security-by-design**: la seguridad es una decisión de arquitectura en cada componente, no una capa añadida al final. Las medidas implementadas cubren las categorías relevantes del **OWASP Top 10** para un MVP SaaS con API REST pública.

---

## 1. Autenticación — JWT

### Implementación

```python
# core/security.py
import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
```

### `require_admin` — dependencia reutilizable

```python
async def require_admin(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Esquema de autenticación inválido")
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    return payload
```

Esta dependencia se inyecta en todos los endpoints privados: `Depends(require_admin)`.

### Hashing de Contraseñas — bcrypt directo

```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

**Por qué bcrypt directo y no passlib:** passlib + bcrypt 4.x genera warnings que rompen los tests. El uso directo elimina la capa de abstracción problemática.

**Work factor 12:** equilibrio entre seguridad (resistencia a brute force) y latencia aceptable (~250ms en hardware estándar).

---

## 2. Rate Limiting — slowapi

```python
# utils/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

if settings.TESTING:
    limiter = Limiter(key_func=get_remote_address, enabled=False)
else:
    limiter = Limiter(key_func=get_remote_address)
```

Aplicación por endpoint:

```python
# api/leads.py
@router.post("/leads")
@limiter.limit("5/minute")
async def create_lead(request: Request, ...):
    ...

# api/auth.py
@router.post("/auth/login")
@limiter.limit("10/minute")
async def login(request: Request, ...):
    ...
```

**Respuesta ante rate limit:**
```
HTTP 429 Too Many Requests
Content-Type: application/json
{"detail": "Rate limit exceeded: 5 per 1 minute"}
```

**Decisión clave:** `enabled=False` cuando `TESTING=true`. Sin esto, los tests que crean múltiples leads fallarían con 429 en lugar de los códigos esperados, haciendo la suite de tests frágil.

---

## 3. Security Headers — Middleware Personalizado

```python
# middleware/security.py
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
```

| Cabecera | Protección |
|---|---|
| `X-Content-Type-Options: nosniff` | Previene MIME-sniffing |
| `X-Frame-Options: DENY` | Previene clickjacking (iframes) |
| `X-XSS-Protection: 1; mode=block` | XSS en navegadores legacy |
| `Referrer-Policy` | Controla información de referrer en peticiones cross-origin |
| `Content-Security-Policy` | Restringe recursos cargables desde el documento |

---

## 4. Honeypot Anti-Bot

Campo oculto en el formulario HTML (`_gotcha`). Los bots que rellenan todos los campos visibles lo envían con valor.

```python
# schemas/lead.py
class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    ...
    gotcha: str = Field(default="", alias="_gotcha")

# services/lead_service.py (lógica de negocio)
async def create_lead(data: LeadCreate, db: Session) -> LeadOut:
    if data.gotcha:
        # Bot detectado — respuesta silenciosa sin procesar
        return _fake_lead_response()
    ...
```

**Por qué HTTP 200 silencioso:** devolver un error (400, 403) revelaría al bot que el campo es una trampa. Con HTTP 200, el bot cree que ha tenido éxito y no adapta su estrategia.

---

## 5. Deduplicación 24h

```python
# services/lead_service.py
from datetime import datetime, timedelta

async def _is_duplicate(email: str, db: Session) -> bool:
    cutoff = datetime.utcnow() - timedelta(hours=24)
    existing = db.query(Lead).filter(
        Lead.email == email,
        Lead.created_at >= cutoff
    ).first()
    return existing is not None

async def create_lead(data: LeadCreate, db: Session) -> LeadOut:
    if await _is_duplicate(data.email, db):
        return _fake_lead_response()  # Silencioso
    ...
```

**Justificación del comportamiento silencioso:** devolver un error revelaría que el email ya existe en la base de datos, lo que filtra información sobre usuarios registrados.

**Por qué 24h y no unicidad absoluta:** un mismo email puede volver a ser un lead válido después de tiempo (cliente que vuelve a interesarse). La unicidad absoluta eliminaría esa posibilidad.

---

## 6. Sanitización de Entradas

```python
# utils/sanitize.py
import re
import html

SQL_INJECTION_PATTERNS = [
    r"(\bSELECT\b|\bDROP\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bUNION\b)",
    r"(--|;|\/\*|\*\/)",
    r"(\bOR\b\s+\d+\s*=\s*\d+|\bAND\b\s+\d+\s*=\s*\d+)",
]

def strip_html(value: str) -> str:
    """Elimina tags HTML y decodifica entidades."""
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()

def detect_injection(value: str) -> bool:
    """True si se detectan patrones de inyección SQL."""
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False
```

**Nota importante:** SQLAlchemy ORM con queries parametrizadas previene la inyección SQL por defecto. Esta detección es una capa defensiva adicional que rechaza entradas maliciosas antes de llegar al ORM.

---

## 7. Configuración Segura — Variables de Entorno

### Validación en startup (config.py)

```python
from pydantic_settings import BaseSettings
from pydantic import model_validator

class Settings(BaseSettings):
    SECRET_KEY: str           # Sin default — falla si no está definida
    ADMIN_USERNAME: str       # Sin default — falla si no está definida
    ADMIN_PASSWORD: str       # Sin default — falla si no está definida
    DATABASE_URL: str         # Sin default — falla si no está definida
    ENVIRONMENT: str = "development"

    @model_validator(mode="after")
    def validate_production_config(self) -> "Settings":
        if self.ENVIRONMENT != "production":
            return self

        insecure = {"changeme", "secret", "password", "admin123", "default", "test"}

        if self.SECRET_KEY.lower() in insecure or len(self.SECRET_KEY) < 32:
            raise ValueError(
                "SECRET_KEY insegura en producción. "
                "Genera una con: openssl rand -hex 32"
            )
        if len(self.ADMIN_PASSWORD) < 12:
            raise ValueError("ADMIN_PASSWORD debe tener mínimo 12 caracteres en producción.")

        return self
```

Si la validación falla → `uvicorn` no arranca. El error se muestra en los logs del servidor, nunca en la respuesta HTTP al cliente.

---

## 8. Ocultación de Errores en Producción

```python
# main.py
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {exc}", exc_info=True)

    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno. Por favor, inténtalo más tarde."}
        )
    raise exc  # En development: propaga el error completo
```

**Qué se oculta en producción:**
- Stack traces con rutas del sistema de archivos
- Nombres de tablas o columnas de la base de datos
- Versiones de librerías (potencialmente vulnerables)
- Mensajes de error internos de SQLAlchemy

---

## Cobertura OWASP Top 10

| ID | Categoría | Estado | Medida |
|---|---|---|---|
| A01 | Broken Access Control | ✅ | `require_admin` en todos los endpoints privados |
| A02 | Cryptographic Failures | ✅ | bcrypt rounds=12, JWT HS256, HTTPS en Render |
| A03 | Injection | ✅ | ORM parametrizado + detección de patrones |
| A04 | Insecure Design | ✅ | Deduplicación silenciosa, honeypot silencioso |
| A05 | Security Misconfiguration | ✅ | Validación en startup, headers, Swagger solo en dev |
| A07 | Identification & Auth Failures | ✅ | Rate limit en login, JWT con expiración |
| A09 | Security Logging | ✅ | Logging estructurado, errores logueados internamente |

---

## Generación de Secretos

```bash
# SECRET_KEY (recomendado)
openssl rand -hex 32

# Alternativa Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Verificar longitud
echo -n "tu_secret_key" | wc -c   # debe ser >= 32
```
