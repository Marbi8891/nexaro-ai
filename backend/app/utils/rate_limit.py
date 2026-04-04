from slowapi import Limiter
from slowapi.util import get_remote_address

# Límite por IP — configurado en cada endpoint con el decorador @limiter.limit("N/minute")
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
