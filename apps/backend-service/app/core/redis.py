"""
Redis connection manager for price caching and pub/sub.

Provides an async Redis connection pool that is initialized on startup
and cleaned up on shutdown.
"""

from typing import Optional

from loguru import logger
from redis.asyncio import Redis, from_url

from app.core.config import get_settings

settings = get_settings()

# ── Module-level Redis instance ──
_redis: Optional[Redis] = None


async def init_redis() -> Redis:
    """Initialize the Redis connection pool. Call during app startup."""
    global _redis
    try:
        _redis = from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )
        # Test connection
        await _redis.ping()
        logger.info(f"✅ Redis connected: {settings.redis_url}")
        return _redis
    except Exception as e:
        logger.warning(f"⚠️ Redis unavailable ({e}) — running without cache")
        _redis = None
        return None


async def close_redis() -> None:
    """Close the Redis connection pool. Call during app shutdown."""
    global _redis
    if _redis:
        await _redis.close()
        logger.info("Redis connection closed")
        _redis = None


def get_redis() -> Optional[Redis]:
    """Get the current Redis instance (may be None if unavailable)."""
    return _redis
