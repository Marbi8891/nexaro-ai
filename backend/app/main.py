from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.db.base import Base
from app.db.session import engine
from app.middleware.security import SecurityHeadersMiddleware
from app.utils.rate_limit import limiter
from app.api import leads, stats, auth

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("NexaroAI API arrancando — env=%s", settings.ENVIRONMENT)
    Base.metadata.create_all(bind=engine)
    logger.info("Base de datos lista")
    yield
    logger.info("NexaroAI API apagándose")


app = FastAPI(
    title="NexaroAI API",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

# Rate limiting global
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers en todas las respuestas
app.add_middleware(SecurityHeadersMiddleware)

# CORS restringido
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)

app.include_router(leads.router, prefix="/api", tags=["leads"])
app.include_router(stats.router, prefix="/api", tags=["stats"])
app.include_router(auth.router, prefix="/api", tags=["auth"])


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log completo internamente, nunca exponer al cliente
    logger.error("Error no controlado: %s | path=%s", str(exc), request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno. Inténtalo de nuevo más tarde."},
    )


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": "NexaroAI API", "version": "1.0.0"}
