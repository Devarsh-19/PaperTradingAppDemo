"""
Application configuration loaded from environment variables.
Uses pydantic-settings for type-safe config with .env file support.
"""

from functools import lru_cache
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the Paper Trading backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──
    app_name: str = "PaperTradingApp"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # ── Server ──
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated string or JSON array from env var."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ── Database ──
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/trading"

    # ── Redis ──
    redis_url: str = "redis://localhost:6379/0"

    # ── Authentication ──
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ── Trading ──
    default_virtual_balance: float = 100_000.00
    price_cache_ttl_seconds: int = 15
    order_match_interval_seconds: int = 15
    price_sync_interval_seconds: int = 10

    # ── Market Data ──
    market_data_provider: str = "yfinance"


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton — call this everywhere instead of constructing Settings()."""
    return Settings()
