from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def aggregate_stats(
    repos: list[dict[str, Any]],
    followers: int,
) -> dict[str, int]:
    return {
        "repositories": len(repos),
        "commits": sum(int(repo.get("commits", 0)) for repo in repos),
        "stars": sum(int(repo.get("stars", 0)) for repo in repos),
        "followers": followers,
    }


def format_uptime(created_at: str) -> str:
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)

    total_days = (now - created).days

    years, remaining_days = divmod(total_days, 365)
    months, days = divmod(remaining_days, 30)

    parts = []

    if years:
        parts.append(f"{years}y")

    if months:
        parts.append(f"{months}m")

    if days or not parts:
        parts.append(f"{days}d")

    return " ".join(parts)