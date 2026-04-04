from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.core.config import settings
from app.core.security import create_access_token
from app.core.logging import get_logger
from app.utils.rate_limit import limiter

router = APIRouter()
logger = get_logger(__name__)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/auth/login", response_model=LoginResponse)
@limiter.limit("10/minute")
def login(request: Request, payload: LoginRequest):
    """Login admin con rate limiting estricto."""
    # Comparación de tiempo constante para evitar timing attacks
    import hmac
    user_ok = hmac.compare_digest(payload.username, settings.ADMIN_USERNAME)
    pass_ok = hmac.compare_digest(payload.password, settings.ADMIN_PASSWORD)

    if not (user_ok and pass_ok):
        logger.warning("Intento de login fallido | IP=%s | user=%s", request.client.host, payload.username)
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = create_access_token({"sub": payload.username, "role": "admin"})
    logger.info("Login admin exitoso | IP=%s", request.client.host)
    return {"access_token": token, "token_type": "bearer"}
