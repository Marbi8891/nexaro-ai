"""
Configuración central de NEXARO AI.

Todas las variables sensibles se cargan EXCLUSIVAMENTE desde variables de entorno
o desde el archivo .env. Ningún valor sensible está hardcodeado en el código.

En producción (ENVIRONMENT=production), la aplicación NO arranca si:
  - SECRET_KEY está vacía, es demasiado corta o usa un valor de la lista negra
  - ADMIN_PASSWORD tiene menos de 12 caracteres
  - DATABASE_URL apunta a localhost

Uso:
    from app.core.config import settings
"""

from functools import lru_cache
from typing import List

from pydantic import model_validator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Valores que se consideran inseguros en producción.
# Ninguno de estos es un secreto real — son las claves de ejemplo más comunes.
_INSECURE_DEFAULTS: frozenset[str] = frozenset({
    "changeme",
    "secret",
    "mysecret",
    "password",
    "admin",
    "admin123",
    "your-secret-key",
    "your_secret_key",
    "supersecret",
    "default",
    "test",
    "dev",
    "insecure",
    "replace_me",
    "placeholder",
    "example",
    "nexaro",
})


class Settings(BaseSettings):
    """
    Configuración de la aplicación cargada desde variables de entorno.

    Variables sin valor por defecto son OBLIGATORIAS — Pydantic lanza
    ValidationError si no están definidas al arrancar la app.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ──────────────────────────────────────────────
    # Seguridad — OBLIGATORIAS (sin default)
    # ──────────────────────────────────────────────
    SECRET_KEY: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    # ──────────────────────────────────────────────
    # Base de datos — OBLIGATORIA (sin default)
    # ──────────────────────────────────────────────
    DATABASE_URL: str

    # ──────────────────────────────────────────────
    # Entorno
    # ──────────────────────────────────────────────
    ENVIRONMENT: str = "development"

    # ──────────────────────────────────────────────
    # JWT
    # ──────────────────────────────────────────────
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas

    # ──────────────────────────────────────────────
    # CORS — array JSON como string
    # Ejemplo: '["https://mrabehfathi.com"]'
    # ──────────────────────────────────────────────
    CORS_ORIGINS: str = '["http://localhost:8080", "http://localhost:3000"]'

    # ──────────────────────────────────────────────
    # Email
    # ──────────────────────────────────────────────
    EMAIL_MOCK: bool = True   # true = solo logs, sin envío real
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # ──────────────────────────────────────────────
    # App
    # ──────────────────────────────────────────────
    APP_NAME: str = "NEXARO AI"
    APP_VERSION: str = "1.0.0"

    # ──────────────────────────────────────────────
    # Testing — se activa con TESTING=true en la CLI
    # Nunca establecer en .env de producción
    # ──────────────────────────────────────────────
    TESTING: bool = False

    # ──────────────────────────────────────────────
    # Validadores
    # ──────────────────────────────────────────────

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "production", "staging"}
        if v not in allowed:
            raise ValueError(
                f"ENVIRONMENT '{v}' no válido. "
                f"Valores permitidos: {', '.join(sorted(allowed))}"
            )
        return v

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """
        Validación fail-fast en producción.
        Si algún secreto es inseguro → la app no arranca.
        El error aparece en los logs del servidor, nunca en la respuesta HTTP.
        """
        if self.ENVIRONMENT != "production" or self.TESTING:
            return self

        errors: list[str] = []

        # SECRET_KEY
        if not self.SECRET_KEY:
            errors.append(
                "SECRET_KEY no puede estar vacía. "
                "Genera una con: openssl rand -hex 32"
            )
        elif self.SECRET_KEY.lower() in _INSECURE_DEFAULTS:
            errors.append(
                f"SECRET_KEY usa el valor '{self.SECRET_KEY}', que está en la lista negra de valores inseguros. "
                "Genera una nueva con: openssl rand -hex 32"
            )
        elif len(self.SECRET_KEY) < 32:
            errors.append(
                f"SECRET_KEY tiene {len(self.SECRET_KEY)} caracteres. "
                "Mínimo requerido en producción: 32."
            )

        # ADMIN_USERNAME
        if not self.ADMIN_USERNAME:
            errors.append("ADMIN_USERNAME no puede estar vacío en producción.")
        elif self.ADMIN_USERNAME.lower() in {"admin", "administrator", "root", "user", "test"}:
            errors.append(
                f"ADMIN_USERNAME '{self.ADMIN_USERNAME}' es demasiado predecible. "
                "Usa un nombre de usuario único."
            )

        # ADMIN_PASSWORD
        if not self.ADMIN_PASSWORD:
            errors.append("ADMIN_PASSWORD no puede estar vacía en producción.")
        elif self.ADMIN_PASSWORD.lower() in _INSECURE_DEFAULTS:
            errors.append(
                "ADMIN_PASSWORD usa un valor de la lista negra. "
                "Elige una contraseña segura de mínimo 12 caracteres."
            )
        elif len(self.ADMIN_PASSWORD) < 12:
            errors.append(
                f"ADMIN_PASSWORD tiene {len(self.ADMIN_PASSWORD)} caracteres. "
                "Mínimo requerido en producción: 12."
            )

        # DATABASE_URL — no debería apuntar a localhost en producción
        if "localhost" in self.DATABASE_URL or "127.0.0.1" in self.DATABASE_URL:
            errors.append(
                "DATABASE_URL apunta a localhost en producción. "
                "Usa la URL de tu base de datos gestionada (Render, RDS, etc.)."
            )

        if errors:
            separator = "\n  ✗ "
            raise ValueError(
                f"\n\n⛔  NEXARO AI no puede arrancar en producción:\n"
                f"{separator}{separator.join(errors)}\n\n"
                f"Corrige las variables de entorno y reinicia el servicio.\n"
            )

        return self

    # ──────────────────────────────────────────────
    # Propiedades de conveniencia
    # ──────────────────────────────────────────────

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Parsea CORS_ORIGINS (string JSON) a lista de strings.

        Acepta tanto formato JSON array:  '["https://example.com"]'
        como formato CSV:                 'https://example.com, http://localhost'
        """
        import json
        try:
            origins = json.loads(self.CORS_ORIGINS)
            if isinstance(origins, list):
                return [o.strip() for o in origins if o.strip()]
        except (json.JSONDecodeError, TypeError):
            pass
        # Fallback: tratar como CSV
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def swagger_enabled(self) -> bool:
        """Swagger UI solo disponible fuera de producción."""
        return not self.is_production


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Retorna la instancia singleton de Settings.

    Cacheada con lru_cache para evitar re-leer variables de entorno
    en cada petición. En tests, invalida con get_settings.cache_clear().
    """
    return Settings()


# Instancia global para importación directa:
#   from app.core.config import settings
settings = get_settings()
