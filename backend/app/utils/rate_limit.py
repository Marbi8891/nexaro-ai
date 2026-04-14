import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# En tests se desactiva el rate limiting para no contaminar resultados
# Controlado por variable de entorno TESTING=true
_testing = os.getenv("TESTING", "false").lower() == "true"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
    enabled=not _testing,
)
