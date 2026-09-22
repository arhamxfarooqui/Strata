"""
Cache-aside pattern implementation with instrumentation.

Usage:
    data = await cache_aside_get("leaderboard:global:1:50", ttl=300)
    if data is not None:
        return json.loads(data)  # cache hit

    # cache miss — fetch from DB
    result = await fetch_from_db()
    await cache_aside_set("leaderboard:global:1:50", json.dumps(result), ttl=300)
    return result
"""

import json
import logging
import time
from dataclasses import dataclass, field

from app.cache.redis_client import get_redis

logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """In-memory cache instrumentation counters."""
    hits: int = 0
    misses: int = 0
    cache_latency_sum_ms: float = 0.0
    cache_latency_count: int = 0
    db_latency_sum_ms: float = 0.0
    db_latency_count: int = 0
    db_queries_saved: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def avg_cache_latency_ms(self) -> float:
        return (
            self.cache_latency_sum_ms / self.cache_latency_count
            if self.cache_latency_count > 0
            else 0.0
        )

    @property
    def avg_db_latency_ms(self) -> float:
        return (
            self.db_latency_sum_ms / self.db_latency_count
            if self.db_latency_count > 0
            else 0.0
        )

    def to_dict(self) -> dict:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hit_rate, 4),
            "avg_cache_latency_ms": round(self.avg_cache_latency_ms, 2),
            "avg_db_latency_ms": round(self.avg_db_latency_ms, 2),
            "db_queries_saved": self.db_queries_saved,
        }


# Global metrics instance
metrics = CacheMetrics()


async def cache_aside_get(key: str) -> str | None:
    """
    Try to read from cache. Returns the cached string or None on miss.
    Records hit/miss and latency metrics.
    """
    redis = await get_redis()
    if redis is None:
        metrics.misses += 1
        return None

    try:
        start = time.monotonic()
        data = await redis.get(key)
        elapsed_ms = (time.monotonic() - start) * 1000

        if data is not None:
            metrics.hits += 1
            metrics.db_queries_saved += 1
            metrics.cache_latency_sum_ms += elapsed_ms
            metrics.cache_latency_count += 1
            logger.debug("Cache HIT: %s (%.2fms)", key, elapsed_ms)
        else:
            metrics.misses += 1
            logger.debug("Cache MISS: %s", key)

        return data
    except Exception as e:
        logger.warning("Redis GET error for %s: %s", key, e)
        metrics.misses += 1
        return None


async def cache_aside_set(key: str, value: str, ttl: int = 300) -> None:
    """
    Write data to cache with a TTL (default 5 minutes).
    """
    redis = await get_redis()
    if redis is None:
        return

    try:
        await redis.set(key, value, ex=ttl)
        logger.debug("Cache SET: %s (TTL=%ds)", key, ttl)
    except Exception as e:
        logger.warning("Redis SET error for %s: %s", key, e)


def record_db_latency(latency_ms: float) -> None:
    """Record a DB query latency for instrumentation comparison."""
    metrics.db_latency_sum_ms += latency_ms
    metrics.db_latency_count += 1
