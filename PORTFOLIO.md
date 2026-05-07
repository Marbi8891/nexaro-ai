# PORTFOLIO.md — NEXARO AI

> Documento de presentación para evaluadores académicos y recruiters técnicos.
> Lectura estimada: 5 minutos.

---

## Contexto

Proyecto construido como parte del ciclo formativo **DAW/DAM** y como pieza central de mi portfolio profesional como desarrollador backend con orientación a productos SaaS.

El objetivo fue construir algo real — un sistema que yo mismo uso en NEXARO TECH para captar leads — con criterios de calidad y seguridad de producción, no de práctica académica.

---

## El Problema

Las agencias digitales pequeñas gestionan sus leads de forma caótica:

> Formulario de contacto → email perdido en la bandeja → Excel manual → cliente sin respuesta → lead perdido.

No hay visibilidad del pipeline, no hay automatización, no hay métricas. Cada lead que llega depende de que alguien lo recuerde a tiempo.

---

## La Solución

NEXARO AI automatiza ese flujo en tres capas:

**1. Captación** — Landing HTML embebible en cualquier web con formulario validado, honeypot anti-bot y deduplicación para evitar duplicados en 24h.

**2. Backend API** — FastAPI que procesa cada lead: valida, sanitiza, persiste y notifica (email en modo mock o real vía SMTP).

**3. Gestión** — Panel CRM con login JWT, tabla filtrable por estado y fuente, estadísticas por periodo y opción de actualizar el estado de cada lead.

---

## Qué He Construido

### Full-stack funcional

**Frontend** (`frontend/`)
- `index.html` — Landing con formulario de captación, field honeypot, validación JS client-side
- `admin.html` — Panel CRM completo: login, dashboard de stats, tabla de leads con filtros y modal de detalle

Ambos archivos son HTML vanilla — sin frameworks, sin build step. Decisión deliberada para el contexto de despliegue (Hostinger shared hosting).

**Backend** (`backend/`)
API REST con FastAPI que incluye:
- 7 endpoints funcionales documentados automáticamente en Swagger
- Autenticación JWT con dependencia `require_admin` reutilizable
- Middleware de security headers en todas las respuestas
- Rate limiting por IP con slowapi (desactivado automáticamente en tests)
- Sanitización de entradas y detección básica de inyección SQL
- Email service con modo mock (`EMAIL_MOCK=true`) y SMTP real configurable
- Placeholders estructurados para WhatsApp (Twilio) y Google Calendar
- Docker Compose para entorno local completo en un comando

**Base de datos**
- PostgreSQL en producción con SQLAlchemy 2.x
- 2 migraciones Alembic: creación de tabla + trigger `updated_at`
- SQLite en memoria para tests — sin dependencias externas

**Testing**
- 41 tests con pytest, rollback por test, cobertura de casos edge
- 4 suites: health, auth, leads (CRUD + honeypot + deduplicación), stats

---

## Competencias Demostradas

### Desarrollo Backend

| Competencia | Evidencia |
|---|---|
| FastAPI | Routers, dependencias, middleware, lifespan, CORS |
| SQLAlchemy 2.x | ORM sync/async compatible, enums, relaciones |
| Alembic | Migraciones versionadas, trigger SQL personalizado |
| Pydantic v2 | Schemas separados por capa (Create / Update / Out / ListOut) |
| Python moderno | Type hints, enums, dataclasses, f-strings |

### Seguridad Web

| Competencia | Evidencia |
|---|---|
| JWT | Firma con SECRET_KEY, expiración configurable, `require_admin` dependency |
| Rate limiting | slowapi por IP, configurable por ruta, desactivado en tests |
| Security headers | Middleware personalizado (DENY, nosniff, XSS, CSP, Referrer) |
| Honeypot | Campo oculto, rechazo silencioso HTTP 200 |
| Deduplicación | Mismo email bloqueado 24h sin error explícito |
| Sanitización | Strip HTML + patrones de inyección SQL detectados pre-persist |
| Config segura | Variables obligatorias desde env, validación en startup |

### Frontend Integrado con API

| Competencia | Evidencia |
|---|---|
| HTML/CSS/JS vanilla | Formulario con validación, fetch a API, manejo de errores |
| Integración REST | Login → JWT en localStorage → cabecera Authorization en cada llamada |
| UX básico | Feedback al usuario, estados de carga, modal de detalle |

### Testing

| Competencia | Evidencia |
|---|---|
| pytest | Fixtures, parametrize, async client |
| Isolation | SQLite en memoria, rollback por test, sin side effects |
| Casos edge | Honeypot activo, deduplicación, campos inválidos, token ausente |

### DevOps Básico

| Competencia | Evidencia |
|---|---|
| Docker | Dockerfile multi-stage, docker-compose.yml con DB |
| Procfile | Deploy directo a Render/Heroku |
| Alembic | Migraciones en pipeline de startup |
| Entornos | `.env.example` documentado, separación development/production |

---

## Qué Aprendí

**Rate limiting en tests es un problema real.** slowapi bloquea peticiones en tests si no se desactiva. La solución fue detectar `TESTING=true` en el módulo de rate_limit y registrar un limiter vacío. Sin esta decisión, varios tests fallarían con 429 en lugar de los códigos esperados.

**La deduplicación de leads requiere una ventana de tiempo, no una unicidad absoluta.** Un mismo email puede volver a ser un lead válido después de 24h (cliente que vuelve a interesarse). Unicidad absoluta haría inútil el sistema para leads recurrentes.

**bcrypt tiene incompatibilidades activas con passlib.** La combinación `passlib` + `bcrypt 4.x` genera warnings que rompen los tests. Solución: usar bcrypt directamente sin la capa de abstracción.

**El frontend HTML vanilla fue una decisión de producto, no de conveniencia.** Hostinger shared hosting no soporta Node.js ni build steps. En lugar de añadir complejidad de despliegue innecesaria, el frontend es un único archivo sin dependencias.

**El modo mock de email es imprescindible en desarrollo.** Poder ejecutar los 41 tests y el servidor local sin configurar SMTP real elimina una fricción enorme. `EMAIL_MOCK=true` hace que el servicio loguee en lugar de enviar.

---

## Decisiones de Arquitectura Relevantes

| Decisión | Alternativa considerada | Por qué esta |
|---|---|---|
| Frontend HTML vanilla | React/Next.js | Sin build step, compatible con Hostinger, suficiente para MVP |
| SQLite en tests | PostgreSQL dockerizado | Sin dependencias externas → CI más simple, tests más rápidos |
| JWT sin refresh tokens | Access + refresh | Scope MVP — 8h es adecuado para panel admin de uso diario |
| Email mock por defecto | SMTP obligatorio | Reduce fricción en setup local y en CI |
| Deduplicación 24h | Unicidad absoluta por email | Lead puede volver a contactar después de tiempo |
| bcrypt directo | passlib | Incompatibilidad conocida con bcrypt 4.x |

---

## Mejoras Futuras

### Corto plazo (junio 2025)
- Activar SMTP real con Resend o SendGrid
- CI/CD con GitHub Actions: tests + lint en cada PR
- Exportación de leads a CSV desde el CRM

### Medio plazo
- Integrar Twilio para notificaciones WhatsApp (placeholder ya estructurado)
- Google Calendar para agendar demos directamente desde el CRM (placeholder listo)
- Métricas avanzadas: tiempo medio de respuesta, tasa de conversión por fuente

### Largo plazo
- Multi-tenancy: múltiples agencias con datos aislados
- Monetización con Stripe (plan SaaS de NEXARO TECH)
- Pipeline de IA: clasificación automática de leads por intención

---

## Por Qué Este Proyecto

Elegí construir una herramienta que yo mismo necesito como fundador de NEXARO TECH, S.L. Eso obligó a tomar decisiones reales de producto — qué campos necesita un lead, qué métricas importan en el dashboard, cómo manejar duplicados — y no solo decisiones técnicas.

El resultado es un proyecto que funciona como:
- **Portfolio académico** → cubre competencias de DAW/DAM con código evaluable
- **Portfolio profesional** → demuestra capacidad para construir productos reales
- **Herramienta propia** → está desplegado y en uso real

---

## Contacto

**Mrabeh Fathi Boussayff**
- 🌐 [mrabehfathi.com](https://mrabehfathi.com)
- 📧 hola@mrabehfathi.com
- 🐙 [github.com/Marbi8891](https://github.com/Marbi8891)
- 📍 Leganés, Madrid
