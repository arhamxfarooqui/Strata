"""
Codeforces API fetcher — async version of the Go fetcher.go.
"""

import logging
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)


@dataclass
class DetailedStats:
    total_solved: int = 0
    max_rating: int = 0
    top_tags: dict[str, int] = field(default_factory=dict)
    easy_count: int = 0
    medium_count: int = 0
    hard_count: int = 0


async def fetch_codeforces_rating(handle: str) -> int:
    """Fetch the current rating for a Codeforces handle."""
    if not handle:
        return 0
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"https://codeforces.com/api/user.info?handles={handle}")
        data = resp.json()
        if data.get("status") == "FAILED":
            raise ValueError(f"Codeforces error: {data.get('comment', 'Unknown')}")
        results = data.get("result", [])
        if not results:
            raise ValueError("No user data found")
        return results[0].get("rating", 0)


async def fetch_codeforces_details(handle: str) -> DetailedStats:
    """Fetch detailed submission stats including tags and difficulties."""
    stats = DetailedStats()
    if not handle:
        return stats

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"https://codeforces.com/api/user.status?handle={handle}")
        data = resp.json()
        if data.get("status") == "FAILED":
            raise ValueError(f"Codeforces status error: {data.get('comment', 'Unknown')}")

        solved = set()
        for sub in data.get("result", []):
            if sub.get("verdict") == "OK":
                problem = sub.get("problem", {})
                pid = f"{problem.get('contestId', 0)}{problem.get('index', '')}"
                if pid in solved:
                    continue
                solved.add(pid)

                stats.total_solved += 1
                rating = problem.get("rating", 0)
                if rating > stats.max_rating:
                    stats.max_rating = rating

                if rating > 0:
                    if rating < 1200:
                        stats.easy_count += 1
                    elif rating <= 1600:
                        stats.medium_count += 1
                    else:
                        stats.hard_count += 1

                for tag in problem.get("tags", []):
                    stats.top_tags[tag] = stats.top_tags.get(tag, 0) + 1

    return stats


async def fetch_codeforces_solved(handle: str) -> int:
    """Shortcut to get just the solved count."""
    stats = await fetch_codeforces_details(handle)
    return stats.total_solved


async def fetch_recent_submissions(handle: str, count: int = 20) -> list[dict]:
    """Fetch the last N submissions for upsolve sync."""
    if not handle:
        return []
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"https://codeforces.com/api/user.status?handle={handle}&from=1&count={count}"
        )
        data = resp.json()
        if data.get("status") != "OK":
            raise ValueError(f"CF API error: {data.get('comment', 'Unknown')}")
        return data.get("result", [])
