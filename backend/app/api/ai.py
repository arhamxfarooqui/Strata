"""AI routes — /api/ai/codesensei, /api/ai/roadmap, /api/ai/analysis, /api/ai/analyze."""

import logging
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.models.user import User
from app.models.query_log import QueryLog
from app.models.routing_log import RoutingLog
from app.schemas.ai import CodeSenseiInput, AnalyzeInput, SubTaskResult
from app.services.multi_provider import multi_call
from app.services.orchestrator import decompose_task
from app.services.shadow_memory import get_weak_concepts, get_all_weak_concepts, format_context_string
from app.services.prompt_guard import check_prompt, check_response_for_solution_leak, FLAGGED_SYSTEM_SUFFIX
from app.services.roadmap import generate_roadmap
from app.services.codeforces import fetch_codeforces_details
from app.services.domain_handlers import get_handler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/codesensei")
async def code_sensei(
    input: CodeSenseiInput,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Anti-cheat: check prompt
    is_flagged, flag_reason = check_prompt(input.message)

    # Build context
    context = (
        f"User: {user.name}. CF Rating: {user.codeforces_rating}. "
        f"Solved: {user.total_solved}. Wings: {user.wings}."
    )

    # Get domain-specific handler
    wing = input.wing.lower() if input.wing else "general"
    handler = get_handler(wing.upper())
    system_prompt = handler.system_prompt

    # Inject anti-cheat suffix if flagged
    if is_flagged:
        system_prompt += FLAGGED_SYSTEM_SUFFIX

    response, persona = await multi_call(wing, input.message, system_prompt + "\nContext: " + context)

    # Log query for metrics
    leaked = check_response_for_solution_leak(response)
    query_log = QueryLog(
        user_id=user_id,
        prompt=input.message,
        flagged=is_flagged,
        flag_reason=flag_reason if is_flagged else None,
        domain_predicted=wing,
        response_leaked_solution=leaked,
    )
    db.add(query_log)
    await db.flush()

    return {"response": response, "persona": persona}


@router.post("/roadmap")
async def generate_roadmap_endpoint(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    roadmap = await generate_roadmap(
        cf_rating=user.codeforces_rating,
        total_solved=user.total_solved,
        wings=user.wings or [],
        top_languages=["C++", "Python"],
    )

    from fastapi.responses import Response
    return Response(content=roadmap, media_type="application/json")


@router.get("/analysis")
async def get_profile_analysis(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    detailed_stats = await fetch_codeforces_details(user.codeforces_handle or "")
    tags = [f"{t} ({c})" for t, c in list(detailed_stats.top_tags.items())[:10]]
    top_tags_str = ", ".join(tags)

    context_prompt = (
        f"Analyze this user's profile and provide motivation. "
        f"User: {user.name}, Codeforces: {user.codeforces_handle} "
        f"(Rating: {user.codeforces_rating}), Total Solved: {detailed_stats.total_solved}. "
        f"Top Tags: {top_tags_str}. Keep the analysis encouraging. Use Markdown."
    )

    response, _ = await multi_call(
        "general", context_prompt, "You are CodeSensei. Analyze the profile."
    )

    return {"analysis": response}


@router.post("/analyze")
async def analyze_with_orchestrator(
    input: AnalyzeInput,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Anti-cheat check
    is_flagged, flag_reason = check_prompt(input.prompt)

    # Fetch Shadow Memory
    weaknesses = await get_all_weak_concepts(db, user_id, limit=5)
    memory_context = format_context_string(weaknesses)

    # Task decomposition
    try:
        plan = await decompose_task(input.prompt, memory_context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestrator failure: {e}")

    # Log the query
    query_log = QueryLog(
        user_id=user_id,
        prompt=input.prompt,
        flagged=is_flagged,
        flag_reason=flag_reason if is_flagged else None,
        domain_predicted=plan.sub_tasks[0].target_wing if plan.sub_tasks else None,
        domain_actual=input.domain,
        response_leaked_solution=False,
    )
    db.add(query_log)
    await db.flush()

    # Execute sub-tasks
    results = []
    for task in plan.sub_tasks:
        handler = get_handler(task.target_wing)
        system_prompt = (
            f"You are a specialized {task.target_wing} sub-agent. "
            f"Provide CONCEPTUAL NUDGES ONLY. No full solutions. Focus on {task.action_type}."
        )
        if is_flagged:
            system_prompt += FLAGGED_SYSTEM_SUFFIX

        try:
            res, _ = await multi_call(task.target_wing, task.description, system_prompt)
            status = "completed"
        except Exception as e:
            res = str(e)
            status = "failed"

        leaked = check_response_for_solution_leak(res)

        results.append(SubTaskResult(
            description=task.description,
            target_wing=task.target_wing,
            action_type=task.action_type,
            status=status,
            result=res,
        ))

        # Log routing accuracy
        routing_log = RoutingLog(
            query_id=query_log.id,
            sub_task=task.description,
            predicted_domain=task.target_wing,
            validated_domain=input.domain,
            correct=(task.target_wing.lower() == input.domain.lower()) if input.domain else None,
        )
        db.add(routing_log)

    await db.flush()

    return {"summary": plan.summary, "tasks": [r.model_dump() for r in results]}
