"""
Celery tasks for Codeforces upsolve synchronization.
Replaces the Go goroutine-based RabbitMQ consumer.
"""

import asyncio
import logging
import time

from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.tasks.celery_app import celery_app
from app.config import get_settings
from app.models.user import User
from app.models.upsolve_task import UpsolveTask
from app.services.codeforces import fetch_recent_submissions

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_sync_session() -> Session:
    """Create a synchronous DB session for Celery workers."""
    engine = create_engine(settings.database_url_sync)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def _sync_user_upsolves_sync(db: Session, user_id: int, cf_handle: str) -> int:
    """Synchronous version of sync_user_upsolves for Celery workers."""
    import json
    import httpx

    if not cf_handle:
        return 0

    # Fetch submissions synchronously
    resp = httpx.get(
        f"https://codeforces.com/api/user.status?handle={cf_handle}&from=1&count=20",
        timeout=15.0,
    )
    data = resp.json()
    if data.get("status") != "OK":
        raise ValueError(f"CF API error: {data.get('comment', 'Unknown')}")

    submissions = data.get("result", [])
    created = 0

    for sub in submissions:
        verdict = sub.get("verdict", "")
        if verdict in ("OK", "TESTING"):
            continue

        problem = sub.get("problem", {})
        contest_id = problem.get("contestId", 0)
        index = problem.get("index", "")
        problem_url = f"https://codeforces.com/contest/{contest_id}/problem/{index}"

        # Dedup check
        existing = db.query(UpsolveTask).filter(
            UpsolveTask.user_id == user_id,
            UpsolveTask.problem_url == problem_url,
        ).first()
        if existing:
            continue

        tags_json = json.dumps(problem.get("tags", []))
        task = UpsolveTask(
            user_id=user_id,
            problem_url=problem_url,
            problem_name=problem.get("name", ""),
            contest_id=contest_id,
            rating=problem.get("rating", 0),
            tags=tags_json,
            status="pending",
        )
        db.add(task)
        created += 1

    db.commit()
    return created


@celery_app.task(
    bind=True,
    name="app.tasks.cf_sync.sync_user_cf",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
    retry_jitter=True,
    acks_late=True,
)
def sync_user_cf(self, user_id: int, cf_handle: str) -> dict:
    """
    Sync Codeforces upsolves for a single user.
    Idempotent: deduplicates by (user_id, problem_url).
    Auto-retries with exponential backoff on failure.
    """
    logger.info("CF sync task for user_id=%d handle=%s (attempt %d)", user_id, cf_handle, self.request.retries)

    db = _get_sync_session()
    try:
        created = _sync_user_upsolves_sync(db, user_id, cf_handle)
        return {"user_id": user_id, "created": created, "status": "success"}
    except Exception as e:
        logger.error("CF sync failed for user_id=%d: %s", user_id, e)
        db.rollback()
        raise  # Celery will auto-retry
    finally:
        db.close()


@celery_app.task(
    name="app.tasks.cf_sync.sync_all_users_upsolves",
    acks_late=True,
)
def sync_all_users_upsolves() -> dict:
    """
    Periodic task: sync upsolves for ALL users with CF handles.
    Dispatches individual sync_user_cf tasks for each user.
    """
    logger.info("[CRON] Starting Codeforces Upsolve sync for all users...")

    db = _get_sync_session()
    try:
        users = db.query(User).filter(User.codeforces_handle != "", User.codeforces_handle.isnot(None)).all()
        dispatched = 0
        for user in users:
            sync_user_cf.delay(user.id, user.codeforces_handle)
            dispatched += 1
            time.sleep(0.5)  # Gentle rate limiting

        logger.info("[CRON] Dispatched %d CF sync tasks", dispatched)
        return {"dispatched": dispatched}
    finally:
        db.close()
