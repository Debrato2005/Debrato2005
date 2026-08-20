from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any
from zoneinfo import ZoneInfo


# ============================================================
# FIXED GEOMETRY
# ============================================================

WIDTH = 1100

PADDING_X = 34
PADDING_TOP = 28
PADDING_BOTTOM = 24

ROW_HEIGHT = 22
SECTION_GAP = 12

FONT_SIZE = 16
HEADER_FONT_SIZE = 18

TOTAL_COLUMNS = 105


# ============================================================
# HELPERS
# ============================================================


def _esc(value: object) -> str:
    return escape(str(value))


def _number(value: object) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def _last_updated() -> str:
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return now.strftime("%d %b %Y · %H:%M IST")


def _text(
    y: int,
    value: object,
    css_class: str = "normal",
) -> str:
    return (
        f'<text x="{PADDING_X}" y="{y}" '
        f'class="{css_class}">{_esc(value)}</text>'
    )


def _leader_row(
    y: int,
    label: str,
    value: object,
) -> str:
    value_text = str(value)

    occupied = len(label) + len(value_text) + 2

    dot_count = max(
        3,
        TOTAL_COLUMNS - occupied,
    )

    dots = "." * dot_count

    return (
        f'<text x="{PADDING_X}" y="{y}">'
        f'<tspan class="key">{_esc(label)}</tspan>'
        f'<tspan class="dots"> {dots} </tspan>'
        f'<tspan class="value">{_esc(value_text)}</tspan>'
        f"</text>"
    )


def _section(
    y: int,
    title: str,
) -> str:
    prefix = f"- {title} "

    filler = max(
        3,
        TOTAL_COLUMNS - len(prefix),
    )

    return (
        f'<text x="{PADDING_X}" y="{y}" class="section">'
        f'{_esc(prefix + ("-" * filler))}'
        f"</text>"
    )


def _stats_row(
    y: int,
    left_label: str,
    left_value: object,
    right_label: str,
    right_value: object,
) -> str:
    return (
        f'<text x="{PADDING_X}" y="{y}">'
        f'<tspan class="key">{_esc(left_label)}</tspan>'
        f'<tspan class="dots"> ........ </tspan>'
        f'<tspan class="value">{_esc(left_value)}</tspan>'
        f'<tspan class="divider">    |    </tspan>'
        f'<tspan class="key">{_esc(right_label)}</tspan>'
        f'<tspan class="dots"> ........ </tspan>'
        f'<tspan class="value">{_esc(right_value)}</tspan>'
        f"</text>"
    )


def _loc_row(
    y: int,
    loc: object,
    additions: object | None,
    deletions: object | None,
) -> str:
    if additions is None or deletions is None:
        return _leader_row(
            y,
            "LOC",
            _number(loc),
        )

    loc_text = _number(loc)
    add_text = _number(additions)
    del_text = _number(deletions)

    label = "LOC"

    occupied = (
        len(label)
        + len(loc_text)
        + len(add_text)
        + len(del_text)
        + 12
    )

    dot_count = max(
        3,
        TOTAL_COLUMNS - occupied,
    )

    dots = "." * dot_count

    return (
        f'<text x="{PADDING_X}" y="{y}">'
        f'<tspan class="key">{label}</tspan>'
        f'<tspan class="dots"> {dots} </tspan>'
        f'<tspan class="value">{loc_text}</tspan>'
        f'<tspan class="normal"> (</tspan>'
        f'<tspan class="green">+{add_text}</tspan>'
        f'<tspan class="normal">, </tspan>'
        f'<tspan class="red">-{del_text}</tspan>'
        f'<tspan class="normal">)</tspan>'
        f"</text>"
    )


# ============================================================
# RENDERER
# ============================================================


def render_svg(
    profile: dict[str, Any],
    stats: dict[str, int],
    project_commits: dict[str, int],
    theme: str = "dark",
    uptime: str = "offline",
) -> str:

    if theme not in {"dark", "light"}:
        raise ValueError(
            "theme must be either 'dark' or 'light'"
        )

    identity = profile["identity"]
    system = profile.get("system", {})
    development = profile.get("development", {})
    languages = profile.get("languages", {})
    hobbies = profile.get("hobbies", [])
    projects = profile.get("projects", [])
    contact = profile.get("contact", {})

    # ========================================================
    # THEME
    # ========================================================

    if theme == "dark":
        background = "#161b22"
        foreground = "#c9d1d9"

        key_color = "#ffa657"
        value_color = "#a5d6ff"
        muted_color = "#616e7f"

        green = "#3fb950"
        red = "#f85149"

        border_color = "#30363d"

    else:
        background = "#ffffff"
        foreground = "#24292f"

        key_color = "#bc4c00"
        value_color = "#0969da"
        muted_color = "#8c959f"

        green = "#1a7f37"
        red = "#cf222e"

        border_color = "#d0d7de"

    # ========================================================
    # LOGICAL ROWS
    # ========================================================

    rows: list[tuple[str, Any]] = []

    username = identity.get(
        "username",
        identity.get("github_username", "github"),
    )

    rows.append(
        (
            "header",
            f"{username}@github",
        )
    )

    # --------------------------------------------------------
    # IDENTITY / SYSTEM
    # --------------------------------------------------------

    rows.extend(
        [
            (
                "row",
                (
                    "Name",
                    identity.get("name", ""),
                ),
            ),
            (
                "row",
                (
                    "Role",
                    identity.get("role", ""),
                ),
            ),
            (
                "row",
                (
                    "Location",
                    identity.get("location", ""),
                ),
            ),
            (
                "row",
                (
                    "OS",
                    " / ".join(
                        system.get("os", [])
                    ),
                ),
            ),
            (
                "row",
                (
                    "Uptime",
                    uptime,
                ),
            ),
            (
                "row",
                (
                    "Host",
                    system.get(
                        "host",
                        identity.get(
                            "institution",
                            "",
                        ),
                    ),
                ),
            ),
            (
                "row",
                (
                    "Focus",
                    identity.get(
                        "tagline",
                        "",
                    ),
                ),
            ),
        ]
    )

    rows.append(("gap", None))

    # --------------------------------------------------------
    # DEVELOPMENT
    # --------------------------------------------------------

    rows.extend(
        [
            (
                "row",
                (
                    "Tools",
                    " · ".join(
                        development.get(
                            "tools",
                            [],
                        )
                    ),
                ),
            ),
            (
                "row",
                (
                    "IDE",
                    " · ".join(
                        development.get(
                            "ide",
                            [],
                        )
                    ),
                ),
            ),
            (
                "row",
                (
                    "Status",
                    development.get(
                        "status",
                        "",
                    ),
                ),
            ),
        ]
    )

    rows.append(("gap", None))

    # --------------------------------------------------------
    # LANGUAGES
    # --------------------------------------------------------

    rows.extend(
        [
            (
                "row",
                (
                    "Languages.Programming",
                    " · ".join(
                        languages.get(
                            "programming",
                            [],
                        )
                    ),
                ),
            ),
            (
                "row",
                (
                    "Languages.Real",
                    " · ".join(
                        languages.get(
                            "real",
                            [],
                        )
                    ),
                ),
            ),
        ]
    )

    rows.append(("gap", None))

    # --------------------------------------------------------
    # HOBBIES
    # --------------------------------------------------------

    rows.append(
        (
            "row",
            (
                "Hobbies",
                " · ".join(hobbies),
            ),
        )
    )

    rows.append(("gap", None))

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    rows.append(
        (
            "section",
            "Projects",
        )
    )

    for project in projects:
        project_id = project.get("id", "")

        commits = project_commits.get(
            project_id,
            0,
        )

        rows.append(
            (
                "row",
                (
                    project.get(
                        "name",
                        project_id,
                    ),
                    f"{_number(commits)} commits",
                ),
            )
        )

    rows.append(("gap", None))

    # --------------------------------------------------------
    # CONTACT
    # --------------------------------------------------------

    rows.append(
        (
            "section",
            "Contact",
        )
    )

    emails = contact.get("email", {})

    personal_email = emails.get(
        "personal",
        "",
    )

    college_email = emails.get(
        "college",
        "",
    )

    if personal_email:
        rows.append(
            (
                "row",
                (
                    "Email.Personal",
                    personal_email,
                ),
            )
        )

    if college_email:
        rows.append(
            (
                "row",
                (
                    "Email.College",
                    college_email,
                ),
            )
        )

    linkedin = contact.get(
        "linkedin",
        {},
    ).get(
        "handle",
        "",
    )

    if linkedin:
        rows.append(
            (
                "row",
                (
                    "LinkedIn",
                    linkedin,
                ),
            )
        )

    x_handle = contact.get(
        "x",
        {},
    ).get(
        "handle",
        "",
    )

    if x_handle:
        rows.append(
            (
                "row",
                (
                    "X",
                    x_handle,
                ),
            )
        )

    rows.append(("gap", None))

    # --------------------------------------------------------
    # GITHUB STATS
    # --------------------------------------------------------

    rows.append(
        (
            "section",
            "GitHub Stats",
        )
    )

    rows.append(
        (
            "stats",
            (
                "Repos",
                _number(
                    stats.get(
                        "repositories",
                        0,
                    )
                ),
                "Stars",
                _number(
                    stats.get(
                        "stars",
                        0,
                    )
                ),
            ),
        )
    )

    rows.append(
        (
            "stats",
            (
                "Commits",
                _number(
                    stats.get(
                        "commits",
                        0,
                    )
                ),
                "Followers",
                _number(
                    stats.get(
                        "followers",
                        0,
                    )
                ),
            ),
        )
    )

    if "loc" in stats:
        rows.append(
            (
                "loc",
                (
                    stats.get(
                        "loc",
                        0,
                    ),
                    stats.get(
                        "additions"
                    ),
                    stats.get(
                        "deletions"
                    ),
                ),
            )
        )

    else:
        rows.append(
            (
                "row",
                (
                    "LOC",
                    "—",
                ),
            )
        )

    rows.append(("gap", None))

    # --------------------------------------------------------
    # LAST UPDATED
    # --------------------------------------------------------

    rows.append(
        (
            "row",
            (
                "Last Updated",
                _last_updated(),
            ),
        )
    )

    # ========================================================
    # DETERMINISTIC HEIGHT
    # ========================================================

    content_height = 0

    for row_type, _ in rows:
        if row_type == "gap":
            content_height += SECTION_GAP
        else:
            content_height += ROW_HEIGHT

    HEIGHT = (
        PADDING_TOP
        + content_height
        + PADDING_BOTTOM
    )

    # ========================================================
    # RENDER
    # ========================================================

    elements: list[str] = []

    y = PADDING_TOP + FONT_SIZE

    for row_type, payload in rows:

        if row_type == "gap":
            y += SECTION_GAP
            continue

        if row_type == "header":

            header = str(payload)

            filler = max(
                3,
                TOTAL_COLUMNS
                - len(header)
                - 1,
            )

            elements.append(
                _text(
                    y,
                    f"{header} "
                    + ("-" * filler),
                    "header",
                )
            )

        elif row_type == "section":

            elements.append(
                _section(
                    y,
                    str(payload),
                )
            )

        elif row_type == "row":

            label, value = payload

            elements.append(
                _leader_row(
                    y,
                    str(label),
                    value,
                )
            )

        elif row_type == "stats":

            (
                left_label,
                left_value,
                right_label,
                right_value,
            ) = payload

            elements.append(
                _stats_row(
                    y,
                    str(left_label),
                    left_value,
                    str(right_label),
                    right_value,
                )
            )

        elif row_type == "loc":

            loc, additions, deletions = payload

            elements.append(
                _loc_row(
                    y,
                    loc,
                    additions,
                    deletions,
                )
            )

        y += ROW_HEIGHT

    body = "\n".join(elements)

    # ========================================================
    # SVG
    # ========================================================

    return f"""<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
    role="img"
    aria-label="Debrato Ghosh GitHub profile"
>

<style>

    text {{
        font-family:
            "JetBrains Mono",
            "Cascadia Code",
            "SFMono-Regular",
            Consolas,
            "Liberation Mono",
            monospace;

        font-size: {FONT_SIZE}px;
        font-weight: 400;

        fill: {foreground};
    }}

    .header {{
        fill: {foreground};
        font-size: {HEADER_FONT_SIZE}px;
        font-weight: 600;
    }}

    .section {{
        fill: {foreground};
        font-weight: 600;
    }}

    .key {{
        fill: {key_color};
    }}

    .value {{
        fill: {value_color};
    }}

    .dots {{
        fill: {muted_color};
    }}

    .divider {{
        fill: {muted_color};
    }}

    .normal {{
        fill: {foreground};
    }}

    .green {{
        fill: {green};
    }}

    .red {{
        fill: {red};
    }}

</style>

<rect
    x="0"
    y="0"
    width="{WIDTH}"
    height="{HEIGHT}"
    rx="12"
    fill="{background}"
    stroke="{border_color}"
    stroke-width="1"
/>

{body}

</svg>
"""