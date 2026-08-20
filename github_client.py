from __future__ import annotations

from typing import Any

import requests


GRAPHQL_URL = "https://api.github.com/graphql"


PROFILE_QUERY = """
query($login: String!) {
  user(login: $login) {
    id
    createdAt

    followers {
      totalCount
    }

    repositories(
      first: 100
      ownerAffiliations: OWNER
      orderBy: {
        field: UPDATED_AT
        direction: DESC
      }
    ) {
      nodes {
        nameWithOwner
        stargazerCount

        defaultBranchRef {
          target {
            ... on Commit {
              history {
                totalCount
              }
            }
          }
        }
      }
    }
  }
}
"""


COMMIT_HISTORY_QUERY = """
query(
  $owner: String!
  $repo: String!
  $cursor: String
) {
  repository(
    owner: $owner
    name: $repo
  ) {
    defaultBranchRef {
      target {
        ... on Commit {
          history(
            first: 100
            after: $cursor
          ) {
            nodes {
              additions
              deletions

              author {
                user {
                  login
                }
              }
            }

            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
      }
    }
  }
}
"""


def _request(
    token: str,
    query: str,
    variables: dict[str, Any],
    timeout: float = 30.0,
) -> dict[str, Any]:

    response = requests.post(
        GRAPHQL_URL,
        json={
            "query": query,
            "variables": variables,
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "debrato-dynamic-profile",
        },
        timeout=timeout,
    )

    response.raise_for_status()

    payload = response.json()

    if payload.get("errors"):
        raise RuntimeError(
            f"GitHub GraphQL error: {payload['errors']}"
        )

    return payload


def _fetch_authored_repo_stats(
    owner: str,
    repo: str,
    username: str,
    token: str,
) -> dict[str, int]:

    cursor: str | None = None

    authored_commits = 0
    additions = 0
    deletions = 0

    username_lower = username.lower()

    while True:

        payload = _request(
            token,
            COMMIT_HISTORY_QUERY,
            {
                "owner": owner,
                "repo": repo,
                "cursor": cursor,
            },
        )

        repository = payload["data"]["repository"]

        if repository is None:
            break

        default_branch = repository.get(
            "defaultBranchRef"
        )

        if not default_branch:
            break

        target = default_branch.get("target")

        if not target:
            break

        history = target["history"]

        for commit in history.get("nodes", []):

            author = commit.get("author") or {}
            user = author.get("user")

            if not user:
                continue

            login = user.get("login")

            if not login:
                continue

            if login.lower() != username_lower:
                continue

            authored_commits += 1
            additions += int(
                commit.get("additions", 0)
            )
            deletions += int(
                commit.get("deletions", 0)
            )

        page_info = history["pageInfo"]

        if not page_info["hasNextPage"]:
            break

        cursor = page_info["endCursor"]

    return {
        "commits": authored_commits,
        "additions": additions,
        "deletions": deletions,
        "loc": additions - deletions,
    }


def fetch_profile_data(
    username: str,
    token: str,
) -> tuple[
    list[dict[str, Any]],
    int,
    str,
    dict[str, int],
]:

    payload = _request(
        token,
        PROFILE_QUERY,
        {
            "login": username,
        },
    )

    user = payload["data"]["user"]

    if user is None:
        raise RuntimeError(
            f"GitHub user not found: {username}"
        )

    followers = int(
        user["followers"]["totalCount"]
    )

    created_at = str(
        user["createdAt"]
    )

    repos: list[dict[str, Any]] = []

    total_authored_commits = 0
    total_additions = 0
    total_deletions = 0

    for node in user["repositories"]["nodes"]:

        name_with_owner = node[
            "nameWithOwner"
        ]

        owner, repo_name = (
            name_with_owner.split("/", 1)
        )

        repo_stats = (
            _fetch_authored_repo_stats(
                owner=owner,
                repo=repo_name,
                username=username,
                token=token,
            )
        )

        repo_data = {
            "nameWithOwner": name_with_owner,
            "stars": int(
                node["stargazerCount"]
            ),
            "commits": repo_stats[
                "commits"
            ],
            "additions": repo_stats[
                "additions"
            ],
            "deletions": repo_stats[
                "deletions"
            ],
            "loc": repo_stats["loc"],
        }

        repos.append(repo_data)

        total_authored_commits += (
            repo_stats["commits"]
        )

        total_additions += (
            repo_stats["additions"]
        )

        total_deletions += (
            repo_stats["deletions"]
        )

    authored_stats = {
        "commits": total_authored_commits,
        "additions": total_additions,
        "deletions": total_deletions,
        "loc": (
            total_additions
            - total_deletions
        ),
    }

    return (
        repos,
        followers,
        created_at,
        authored_stats,
    )