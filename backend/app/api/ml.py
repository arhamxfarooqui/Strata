"""ML Wing routes — /api/wings/ml/curate."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.models.resource import Resource
from app.services.shadow_memory import get_weak_concepts

router = APIRouter(prefix="/api/wings/ml", tags=["ml"])


@router.get("/curate")
async def get_ml_curation(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    weaknesses = await get_weak_concepts(db, user_id, "ML")

    if not weaknesses:
        stmt = (
            select(Resource)
            .where(Resource.wing_id == "ML", Resource.difficulty_level == "beginner")
            .limit(5)
        )
        result = await db.execute(stmt)
        resources = result.scalars().all()
        return {
            "status": "exploring",
            "message": "No specific weaknesses identified yet. Here are some introductory materials.",
            "resources": [r.to_dict() for r in resources],
        }

    # Find resources matching weak concepts
    results = []
    for w in weaknesses:
        stmt = (
            select(Resource)
            .where(
                Resource.wing_id == "ML",
                (Resource.subject.ilike(f"%{w.concept}%"))
                | (Resource.title.ilike(f"%{w.concept}%")),
            )
            .limit(2)
        )
        result = await db.execute(stmt)
        results.extend(result.scalars().all())

    return {
        "status": "targeting_weaknesses",
        "weaknesses": [w.to_dict() for w in weaknesses],
        "resources": [r.to_dict() for r in results],
    }
