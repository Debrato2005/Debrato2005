from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

from github_client import fetch_profile_data
from svg import render_svg
from profile_config import load_profile
from stats import aggregate_stats, format_uptime



def project_commit_map(projects: list[dict[str, Any]], repos: list[dict[str, Any]]) -> dict[str, int]:
    by_repo = {repo["nameWithOwner"].lower(): int(repo.get("commits", 0)) for repo in repos}
    result: dict[str, int] = {}
    for project in projects:
        repository = project.get("repository")
        result[project["id"]] = by_repo.get(str(repository).lower(), 0) if repository else 0
    return result


def generate(
    profile_path: Path,
    output_dir: Path,
    token: str | None = None,
) -> None:
    profile = load_profile(profile_path)

    username = (
        profile.get("identity", {}).get("github_username")
        or profile["identity"]["username"]
    )

    if token:
        (
            repos,
            followers,
            created_at,
            authored_stats,
        ) = fetch_profile_data(
            username,
            token,
        )

        uptime = format_uptime(created_at)

    else:
        repos = []
        followers = 0
        uptime = "offline"

        authored_stats = {
            "commits": 0,
            "additions": 0,
            "deletions": 0,
            "loc": 0,
        }

    stats = aggregate_stats(
        repos,
        followers,
    )

    stats.update(authored_stats)

    projects = profile.get(
        "projects",
        [],
    )

    commits = project_commit_map(
        projects,
        repos,
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    (output_dir / "dark_mode.svg").write_text(
        render_svg(
            profile,
            stats,
            commits,
            theme="dark",
            uptime=uptime,
        ),
        encoding="utf-8",
    )

    (output_dir / "light_mode.svg").write_text(
        render_svg(
            profile,
            stats,
            commits,
            theme="light",
            uptime=uptime,
        ),
        encoding="utf-8",
    )