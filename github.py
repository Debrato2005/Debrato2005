from __future__ import annotations

from typing import Any

import requests


PROFILE_QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        nameWithOwner
        stargazerCount
        defaultBranchRef {
          target {
            ... on Commit {
              history { totalCount }
            }
          }
        }
      }
    }
  }
}
"""


def parse_profile_query(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    user = payload["data"]["user"]
    followers = int(user["followers"]["totalCount"])
    repos: list[dict[str, Any]] = []

    for node in user["repositories"]["nodes"]:
        default_branch = node.get("defaultBranchRef")
        commits = 0
        if default_branch and default_branch.get("target"):
            commits = int(default_branch["target"]["history"]["totalCount"])
        repos.append(
            {
                "nameWithOwner": node["nameWithOwner"],
                "stars": int(node["stargazerCount"]),
                "commits": commits,
            }
        )
    return repos, followers


def parse_account_created_at(payload: dict[str, Any]) -> str:
    return str(payload["data"]["user"]["createdAt"])


def fetch_profile_data(username: str, token: str, timeout: float = 20.0) -> tuple[list[dict[str, Any]], int, str]:
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": PROFILE_QUERY, "variables": {"login": username}},
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "dynamic-profile-readme",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(f"GitHub GraphQL error: {payload['errors']}")
    repos, followers = parse_profile_query(payload)
    return repos, followers, parse_account_created_at(payload)
