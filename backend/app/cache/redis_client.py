"""
Async Redis client singleton — used for cache-aside and general caching.
"""

import logging

import redis.asyncio as aioredis

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis | None:
    """Get the shared async Redis client. Returns None if Redis is unavailable."""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=3,
            )
            await _redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning("Failed to connect to Redis: %s. Caching disabled.", e)
            _redis_client = None
    return _redis_client


async def close_redis() -> None:
    """Close the Redis connection on app shutdown."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
