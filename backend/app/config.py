"""
Strata configuration — loads all settings from environment variables via Pydantic Settings.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    # --- Database ---
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "strata"

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- RabbitMQ ---
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672//"

    # --- AI Providers ---
    GROQ_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    HF_TOKEN: str = ""

    # --- GitHub ---
    GITHUB_TOKEN: str = ""

    # --- Auth ---
    JWT_SECRET: str = "insecure-default-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    # --- Server ---
    PORT: int = 8081
    DEBUG: bool = False

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync URL for Alembic migrations and Celery tasks."""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
