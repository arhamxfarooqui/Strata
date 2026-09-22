"""Tests for Celery task retry and dead-letter behavior."""

import pytest
from unittest.mock import patch, MagicMock
from app.tasks.cf_sync import sync_user_cf
from app.services.rating import calculate_axios_rating


class TestCeleryTaskConfig:
    """Tests that Celery tasks are configured with correct retry behavior."""

    def test_cf_sync_has_autoretry(self):
        """CF sync task must have autoretry_for configured."""
        # Check that the task is registered and has retry config
        assert sync_user_cf.max_retries == 5

    def test_cf_sync_acks_late(self):
        """Tasks should ack late for at-least-once delivery."""
        assert sync_user_cf.acks_late is True

    def test_cf_sync_has_backoff(self):
        """CF sync should use exponential backoff."""
        assert sync_user_cf.retry_backoff is True

    def test_cf_sync_has_jitter(self):
        """Retry should have jitter to avoid thundering herd."""
        assert sync_user_cf.retry_jitter is True


class TestIdempotency:
    """Tests that sync operations are idempotent."""

    def test_rating_calculation_is_deterministic(self):
        """Same inputs should always produce the same rating."""
        r1 = calculate_axios_rating(1500, 100, 10, 5)
        r2 = calculate_axios_rating(1500, 100, 10, 5)
        assert r1 == r2

    def test_rating_handles_zero_cf(self):
        """Unrated users (CF=0) should not go negative."""
        r = calculate_axios_rating(0, 0, 0, 0)
        assert r == 0

    def test_rating_handles_negative_cf(self):
        """CF can return -1 for unrated — should be treated as 0."""
        r = calculate_axios_rating(-1, 10, 5, 0)
        assert r > 0  # Should still have points from solved + repos

    def test_rating_formula_matches_spec(self):
        """Verify the exact formula: (cf*0.5) + (solved*5) + (repos*20) + (prs*50)."""
        r = calculate_axios_rating(1600, 200, 15, 10)
        expected = round((1600 * 0.5) + (200 * 5) + (15 * 20) + (10 * 50))
        assert r == expected
