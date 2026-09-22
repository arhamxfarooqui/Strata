"""Tests for cache-aside behavior."""

import json
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from app.cache.cache_aside import cache_aside_get, cache_aside_set, metrics, CacheMetrics


class TestCacheMetrics:
    """Tests for the cache instrumentation counters."""

    def test_hit_rate_zero_when_empty(self):
        m = CacheMetrics()
        assert m.hit_rate == 0.0

    def test_hit_rate_calculation(self):
        m = CacheMetrics(hits=85, misses=15)
        assert m.hit_rate == 0.85

    def test_hundred_percent_hit_rate(self):
        m = CacheMetrics(hits=100, misses=0)
        assert m.hit_rate == 1.0

    def test_avg_latency_zero_when_empty(self):
        m = CacheMetrics()
        assert m.avg_cache_latency_ms == 0.0
        assert m.avg_db_latency_ms == 0.0

    def test_avg_cache_latency(self):
        m = CacheMetrics(cache_latency_sum_ms=100.0, cache_latency_count=10)
        assert m.avg_cache_latency_ms == 10.0

    def test_to_dict(self):
        m = CacheMetrics(hits=9, misses=1, db_queries_saved=9)
        d = m.to_dict()
        assert d["hits"] == 9
        assert d["misses"] == 1
        assert d["hit_rate"] == 0.9
        assert d["db_queries_saved"] == 9


@pytest.mark.asyncio
class TestCacheAside:
    """Tests for the cache-aside get/set pattern."""

    async def test_cache_miss_returns_none_when_redis_unavailable(self):
        with patch("app.cache.cache_aside.get_redis", return_value=None):
            result = await cache_aside_get("test_key")
            assert result is None

    async def test_cache_miss_returns_none_on_empty_key(self):
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        with patch("app.cache.cache_aside.get_redis", return_value=mock_redis):
            result = await cache_aside_get("nonexistent_key")
            assert result is None

    async def test_cache_hit_returns_data(self):
        mock_redis = AsyncMock()
        expected = json.dumps([{"name": "user1", "rating": 100}])
        mock_redis.get = AsyncMock(return_value=expected)
        with patch("app.cache.cache_aside.get_redis", return_value=mock_redis):
            result = await cache_aside_get("leaderboard:global:1:50")
            assert result == expected

    async def test_cache_set_calls_redis(self):
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock()
        with patch("app.cache.cache_aside.get_redis", return_value=mock_redis):
            await cache_aside_set("test_key", "test_value", ttl=60)
            mock_redis.set.assert_called_once_with("test_key", "test_value", ex=60)

    async def test_cache_set_noop_when_redis_unavailable(self):
        with patch("app.cache.cache_aside.get_redis", return_value=None):
            # Should not raise
            await cache_aside_set("test_key", "test_value")
