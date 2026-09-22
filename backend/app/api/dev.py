"""Dev Wing routes — /api/wings/dev/*."""

import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.models.user import User
from app.schemas.dev import PRReviewInput, ResumeBulletsInput
from app.services.github_service import (
    fetch_good_first_issues, fetch_user_repos, calculate_project_health,
    fetch_pr_diff, fetch_recent_commits,
)
from app.services.multi_provider import multi_call

router = APIRouter(prefix="/api/wings/dev", tags=["dev"])


@router.get("/first-issues")
async def get_good_first_issues(language: str = ""):
    langs = [l.strip() for l in language.split(",") if l.strip()] if language else []
    try:
        issues = await fetch_good_first_issues(langs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub API error: {e}")
    return [{"title": i.title, "url": i.url, "repo_name": i.repo_name} for i in issues]


@router.get("/health")
async def get_dev_health(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.github_handle:
        raise HTTPException(status_code=404, detail="GitHub handle not linked. Please update your profile in Settings.")

    repos = await fetch_user_repos(user.github_handle)
    limit = min(3, len(repos))
    results = []
    for i in range(limit):
        repo = repos[i]
        owner = repo.get("owner", {}).get("login", "")
        name = repo.get("name", "")
        try:
            health = await calculate_project_health(owner, name)
            results.append({
                "name": repo.get("full_name", ""),
                "health": {
                    "score": health.score,
                    "has_readme": health.has_readme,
                    "active_last_30": health.active_last_30,
                    "issue_ratio": health.issue_ratio,
                },
            })
        except Exception:
            pass
    return results


@router.post("/review")
async def review_pull_request(
    input: PRReviewInput,
    user_id: int = Depends(get_current_user_id),
):
    try:
        diff_content = await fetch_pr_diff(input.pr_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if len(diff_content) > 8000:
        diff_content = diff_content[:8000] + "\n... (Diff truncated for review) ..."

    system_prompt = (
        "You are The Architect, a Senior Backend Engineer and System Design expert. "
        "You STRICTLY ONLY answer questions regarding software development."
    )
    ai_prompt = (
        f"Review this GitHub PR diff. Focus on security vulnerabilities, "
        f"anti-patterns, and performance bottlenecks. Be concise. Markdown.\n\n"
        f"Diff:\n```diff\n{diff_content}\n```"
    )

    response, persona = await multi_call("dev", ai_prompt, system_prompt)
    return {"review": response, "persona": persona}


@router.post("/resume")
async def generate_resume_bullets(
    input: ResumeBulletsInput,
    user_id: int = Depends(get_current_user_id),
):
    trimmed = input.repo_url.rstrip("/")
    parts = trimmed.split("/")
    if len(parts) < 5:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")
    owner, repo = parts[3], parts[4]

    try:
        commits = await fetch_recent_commits(owner, repo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch commits: {e}")

    commit_summary = "\n- ".join(commits)
    if len(commit_summary) > 5000:
        commit_summary = commit_summary[:5000]

    system_prompt = "You are an Expert Tech Recruiter specializing in Software Engineering."
    ai_prompt = (
        f"Turn these raw git commit messages into 3 powerful, professional resume "
        f"bullet points using the STAR method. Focus on impact and technical keywords.\n\n"
        f"Commits:\n- {commit_summary}"
    )

    response, _ = await multi_call("dev", ai_prompt, system_prompt)
    return {"bullets": response}
