"""
Celery task for global rating synchronization.
Runs daily at midnight — fetches fresh stats and recalculates all Strata ratings.
"""

import logging
import time

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.tasks.celery_app import celery_app
from app.config import get_settings
from app.models.user import User
from app.services.rating import calculate_axios_rating

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(
    name="app.tasks.rating_sync.sync_global_ratings",
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=True,
    acks_late=True,
)
def sync_global_ratings() -> dict:
    """
    Refresh stats for all users and recalculate Strata ratings.
    Invalidates the leaderboard cache after completion.
    """
    logger.info("[CRON] Starting Global Rating synchronization...")

    engine = create_engine(settings.database_url_sync)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    updated = 0
    try:
        users = db.query(User).all()
        for user in users:
            try:
                # Fetch Codeforces stats
                if user.codeforces_handle:
                    try:
                        resp = httpx.get(
                            f"https://codeforces.com/api/user.info?handles={user.codeforces_handle}",
                            timeout=10.0,
                        )
                        data = resp.json()
                        if data.get("status") == "OK" and data.get("result"):
                            user.codeforces_rating = data["result"][0].get("rating", 0)
                    except Exception as e:
                        logger.warning("CF rating fetch failed for %s: %s", user.email, e)

                    try:
                        resp = httpx.get(
                            f"https://codeforces.com/api/user.status?handle={user.codeforces_handle}",
                            timeout=30.0,
                        )
                        data = resp.json()
                        if data.get("status") == "OK":
                            solved = set()
                            for sub in data.get("result", []):
                                if sub.get("verdict") == "OK":
                                    p = sub.get("problem", {})
                                    pid = f"{p.get('contestId', 0)}{p.get('index', '')}"
                                    solved.add(pid)
                            user.total_solved = len(solved)
                    except Exception as e:
                        logger.warning("CF solved fetch failed for %s: %s", user.email, e)

                # Fetch GitHub stats
                if user.github_handle:
                    try:
                        resp = httpx.get(
                            f"https://api.github.com/users/{user.github_handle}",
                            timeout=10.0,
                        )
                        if resp.status_code == 200:
                            user.github_repos = resp.json().get("public_repos", 0)
                    except Exception as e:
                        logger.warning("GitHub fetch failed for %s: %s", user.email, e)

                # Recalculate rating
                user.axios_rating = calculate_axios_rating(
                    user.codeforces_rating, user.total_solved, user.github_repos, 0
                )
                updated += 1

            except Exception as e:
                logger.error("Rating sync error for user %s: %s", user.email, e)

            time.sleep(0.5)  # Rate limiting

        db.commit()

        # Invalidate leaderboard cache (sync Redis call)
        try:
            import redis
            r = redis.from_url(settings.REDIS_URL)
            keys = list(r.scan_iter(match="leaderboard:*"))
            if keys:
                r.delete(*keys)
                logger.info("Invalidated %d leaderboard cache keys", len(keys))
            r.close()
        except Exception as e:
            logger.warning("Cache invalidation failed: %s", e)

        logger.info("[CRON] Global Rating sync completed. Updated %d users.", updated)
        return {"updated": updated}

    finally:
        db.close()
        engine.dispose()
