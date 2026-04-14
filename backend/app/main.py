from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api import auth, leads, stats
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.middleware.security import SecurityHeadersMiddleware
from app.utils.rate_limit import limiter

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("NexaroAI API arrancando | env=%s", settings.ENVIRONMENT)
    yield
    logger.info("NexaroAI API apagando")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# ── Rate limiting ──────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Security headers ───────────────────────────────────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": settings.APP_NAME, "environment": settings.ENVIRONMENT}


@app.get("/", include_in_schema=False)
def root():
    return {"status": "ok"}


# ── Global error handler — no filtrar detalles internos en producción ──────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Error no controlado | path=%s | %s", request.url.path, str(exc))
    if settings.ENVIRONMENT == "production":
        return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})
    return JSONResponse(status_code=500, content={"detail": str(exc)})