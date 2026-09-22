"""
Sync logic — fetches recent CF submissions and populates the UpsolveTask table.
Used by both the Celery worker and manual sync endpoint.
"""

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.upsolve_task import UpsolveTask
from app.services.codeforces import fetch_recent_submissions

logger = logging.getLogger(__name__)


async def sync_user_upsolves(db: AsyncSession, user_id: int, cf_handle: str) -> int:
    """
    Fetch recent submissions for a user, filter non-OK verdicts, deduplicate,
    and insert pending UpsolveTask rows.

    Returns the number of new tasks created.
    """
    if not cf_handle:
        return 0

    logger.info("[SYNC] Syncing upsolves for user_id=%d handle=%s", user_id, cf_handle)

    submissions = await fetch_recent_submissions(cf_handle, count=20)
    created = 0

    for sub in submissions:
        verdict = sub.get("verdict", "")
        if verdict in ("OK", "TESTING"):
            continue

        problem = sub.get("problem", {})
        contest_id = problem.get("contestId", 0)
        index = problem.get("index", "")
        problem_url = f"https://codeforces.com/contest/{contest_id}/problem/{index}"

        # Deduplication check
        stmt = select(UpsolveTask).where(
            UpsolveTask.user_id == user_id,
            UpsolveTask.problem_url == problem_url,
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none() is not None:
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

    await db.flush()
    logger.info("[SYNC] Created %d new upsolve tasks for user_id=%d", created, user_id)
    return created
