"""
GitHub API service — async version of the Go github.go.
Handles repo listing, health audit, PR diff fetching, and commit history.
"""

import logging
from dataclasses import dataclass

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _github_headers(accept: str = "application/vnd.github.v3+json") -> dict:
    headers = {"Accept": accept}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
    return headers


@dataclass
class GoodFirstIssue:
    title: str
    url: str
    repo_name: str


@dataclass
class ProjectHealth:
    score: int = 50
    has_readme: bool = False
    active_last_30: bool = False
    issue_ratio: float = 0.0


async def fetch_github_repos_count(handle: str) -> int:
    if not handle:
        return 0
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"https://api.github.com/users/{handle}", headers=_github_headers()
        )
        if resp.status_code != 200:
            raise ValueError(f"GitHub API returned status: {resp.status_code}")
        return resp.json().get("public_repos", 0)


async def fetch_github_languages(handle: str) -> tuple[list[str], str]:
    """Returns (top_languages, top_repo_description)."""
    if not handle:
        return [], ""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"https://api.github.com/users/{handle}/repos?sort=updated&per_page=10",
            headers=_github_headers(),
        )
        if resp.status_code != 200:
            return [], ""
        repos = resp.json()

    lang_map: dict[str, int] = {}
    top_repo = ""
    max_stars = -1

    for repo in repos:
        lang = repo.get("language", "")
        if lang:
            lang_map[lang] = lang_map.get(lang, 0) + 1
        stars = repo.get("stargazers_count", 0)
        if stars > max_stars:
            max_stars = stars
            desc = repo.get("description") or "No description"
            top_repo = f"{repo.get('name', '')}: {desc}"

    top_langs = list(lang_map.keys())[:5]
    return top_langs, top_repo


async def fetch_user_repos(handle: str) -> list[dict]:
    if not handle:
        return []
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"https://api.github.com/users/{handle}/repos?sort=updated&per_page=30",
            headers=_github_headers(),
        )
        if resp.status_code == 403:
            raise ValueError("GitHub API Rate Limit Exceeded or Invalid Token (403)")
        if resp.status_code != 200:
            raise ValueError(f"GitHub API returned status: {resp.status_code}")
        return resp.json()


async def calculate_project_health(owner: str, repo: str) -> ProjectHealth:
    health = ProjectHealth()
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Check README
        resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/readme",
            headers=_github_headers(),
        )
        if resp.status_code == 200:
            health.has_readme = True
            health.score += 20

        # Check recent activity
        from datetime import datetime, timedelta
        since = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/commits?since={since}",
            headers=_github_headers(),
        )
        if resp.status_code == 200:
            commits = resp.json()
            if commits:
                health.active_last_30 = True
                health.score += 20

        # Check issues
        resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=_github_headers(),
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("open_issues_count", 0) < 5:
                health.score += 10

    health.score = min(100, health.score)
    return health


async def fetch_good_first_issues(languages: list[str]) -> list[GoodFirstIssue]:
    query = 'label:"good first issue" is:open no:assignee'
    if languages:
        query += " " + " ".join(f"language:{lang}" for lang in languages)

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"https://api.github.com/search/issues?q={query}",
            headers=_github_headers(),
        )
        if resp.status_code != 200:
            raise ValueError(f"GitHub API returned status: {resp.status_code}")

        items = resp.json().get("items", [])
        return [
            GoodFirstIssue(
                title=item["title"],
                url=item["html_url"],
                repo_name=item.get("repository", {}).get("full_name", ""),
            )
            for item in items
        ]


async def fetch_pr_diff(pr_url: str) -> str:
    if "/pull/" not in pr_url:
        raise ValueError("Invalid GitHub PR URL format")

    parts = pr_url.rstrip("/").split("/")
    if len(parts) < 7:
        raise ValueError("Invalid GitHub PR URL format")
    owner, repo, pr_number = parts[3], parts[4], parts[6]

    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            api_url, headers=_github_headers("application/vnd.github.v3.diff")
        )
        if resp.status_code != 200:
            raise ValueError(f"GitHub API returned status: {resp.status_code}")
        return resp.text


async def fetch_recent_commits(owner: str, repo: str) -> list[str]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=10",
            headers=_github_headers(),
        )
        if resp.status_code != 200:
            raise ValueError(f"GitHub API returned status: {resp.status_code}")
        return [c["commit"]["message"] for c in resp.json()]
