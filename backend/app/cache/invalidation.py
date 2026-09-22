"""
Cache invalidation utilities — triggered on writes that affect cached data.
"""

import logging

from app.cache.redis_client import get_redis

logger = logging.getLogger(__name__)


async def invalidate_leaderboard_cache() -> None:
    """
    Invalidate all leaderboard cache keys on rating/score writes.
    Uses SCAN to find and delete keys matching 'leaderboard:*'.
    """
    redis = await get_redis()
    if redis is None:
        return

    try:
        cursor = 0
        deleted = 0
        while True:
            cursor, keys = await redis.scan(cursor, match="leaderboard:*", count=100)
            if keys:
                await redis.delete(*keys)
                deleted += len(keys)
            if cursor == 0:
                break
        if deleted > 0:
            logger.info("Invalidated %d leaderboard cache keys", deleted)
    except Exception as e:
        logger.warning("Cache invalidation error: %s", e)


async def invalidate_key(key: str) -> None:
    """Delete a specific cache key."""
    redis = await get_redis()
    if redis is None:
        return
    try:
        await redis.delete(key)
    except Exception as e:
        logger.warning("Cache key deletion error for %s: %s", key, e)
