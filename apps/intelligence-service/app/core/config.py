"""Intelligence Service configuration."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "IntelligenceService"
    app_version: str = "1.0.0"
    debug: bool = False

    # Trading service URL (to fetch user performance data)
    trading_service_url: str = "http://localhost:8000"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
