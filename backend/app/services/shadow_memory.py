"""
Shadow Memory service — reads/writes proficiency data with decay support.
"""

import math
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shadow_memory import ShadowMemory


async def get_weak_concepts(
    db: AsyncSession, user_id: int, domain: str, limit: int = 3
) -> list[ShadowMemory]:
    """
    Get the weakest concepts for a user in a domain, sorted by effective proficiency.
    Applies time-decay before ranking.
    """
    stmt = (
        select(ShadowMemory)
        .where(ShadowMemory.user_id == user_id, ShadowMemory.domain == domain)
    )
    result = await db.execute(stmt)
    concepts = list(result.scalars().all())

    # Sort by effective (decayed) proficiency ascending — weakest first
    concepts.sort(key=lambda c: c.effective_proficiency)

    return concepts[:limit]


async def get_all_weak_concepts(
    db: AsyncSession, user_id: int, limit: int = 5
) -> list[ShadowMemory]:
    """Get the weakest concepts across ALL domains for a user."""
    stmt = select(ShadowMemory).where(ShadowMemory.user_id == user_id)
    result = await db.execute(stmt)
    concepts = list(result.scalars().all())
    concepts.sort(key=lambda c: c.effective_proficiency)
    return concepts[:limit]


async def update_proficiency(
    db: AsyncSession,
    user_id: int,
    domain: str,
    concept: str,
    score: float,
    is_mistake: bool = False,
) -> None:
    """
    Upsert a concept's proficiency score. Creates if new, updates if exists.
    score is 0.0-1.0. If is_mistake=True, increments the mistake counter.
    """
    score = max(0.0, min(1.0, score))

    stmt = select(ShadowMemory).where(
        ShadowMemory.user_id == user_id,
        ShadowMemory.domain == domain,
        ShadowMemory.concept == concept,
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    if existing is None:
        entry = ShadowMemory(
            user_id=user_id,
            domain=domain,
            concept=concept,
            proficiency=score,
            confidence=0.2,
            mistake_count=1 if is_mistake else 0,
            last_noted_at=now,
        )
        db.add(entry)
    else:
        existing.proficiency = score
        existing.last_noted_at = now
        # Confidence increases with each observation (asymptotic to 1.0)
        existing.confidence = min(1.0, existing.confidence + 0.1 * (1.0 - existing.confidence))
        if is_mistake:
            existing.mistake_count += 1

    await db.flush()


def format_context_string(concepts: list[ShadowMemory]) -> str:
    """
    Convert Shadow Memory entries into a natural language string for LLM injection.
    Output: "User's known weak concepts: Dynamic Programming (Score: 3/10), ..."
    """
    if not concepts:
        return ""
    parts = [f"{c.concept} (Score: {c.display_score}/10)" for c in concepts]
    return f"User's known weak concepts: {', '.join(parts)}."
