from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "NexaroAI API"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "CHANGE-THIS-IN-PRODUCTION-USE-OPENSSL-RAND-HEX-32"

    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/nexaroai"

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://nexaroai.agency",
        "https://www.nexaroai.agency",
    ]

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "hola@nexaroai.agency"
    EMAIL_FROM_NAME: str = "NexaroAI Agency"
    EMAIL_MOCK: bool = True

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "CambiaMeEnProduccion2024!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
