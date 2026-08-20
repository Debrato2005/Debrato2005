from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any
from zoneinfo import ZoneInfo


# ============================================================
# FIXED TERMINAL GEOMETRY
# ============================================================

WIDTH = 985

PADDING_X = 30
PADDING_TOP = 30
PADDING_BOTTOM = 26

ROW_HEIGHT = 24
SECTION_GAP_ROWS = 1

FONT_SIZE = 14

# Number of monospace character columns available per line.
TOTAL_COLUMNS = 108


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


def _plain_text(
    y: int,
    value: object,
    css_class: str = "normal",
) -> str:
    return (
        f'<text x="{PADDING_X}" y="{y}" '
        f'class="{css_class}">{_esc(value)}</text>'
    )


def _row(
    y: int,
    label: str,
    value: object,
) -> str:
    """
    Deterministic terminal row.

    Example:
        OS ................................ Windows / Ubuntu

    Dot count is calculated strictly from TOTAL_COLUMNS.
    """

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
    """
    Example:

    - Projects -----------------------------------------------------
    """

    prefix = f"- {title} "

    filler_length = max(
        3,
        TOTAL_COLUMNS - len(prefix),
    )

    return (
        f'<text x="{PADDING_X}" y="{y}" class="section">'
        f'{_esc(prefix + ("-" * filler_length))}'
        f"</text>"
    )


def _stats_row(
    y: int,
    left_label: str,
    left_value: object,
    right_label: str,
    right_value: object,
) -> str:
    """
    Fixed two-column stats line.

    Repos ........ 21    |    Commits ........ 247
    """

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
        border_color = "#30363d"

        green = "#3fb950"
        red = "#f85149"

    else:
        background = "#ffffff"
        foreground = "#24292f"

        key_color = "#bc4c00"
        value_color = "#0969da"

        muted_color = "#8c959f"
        border_color = "#d0d7de"

        green = "#1a7f37"
        red = "#cf222e"

    # ========================================================
    # BUILD LOGICAL ROWS FIRST
    #
    # Height is determined exclusively from this structure.
    # ========================================================

    logical_rows: list[tuple[str, Any]] = []

    username = identity.get(
        "username",
        identity.get("github_username", "github"),
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    logical_rows.append(
        (
            "header",
            f"{username}@github",
        )
    )

    # --------------------------------------------------------
    # SYSTEM
    # --------------------------------------------------------

    logical_rows.append(
        (
            "row",
            (
                "Name",
                identity.get("name", ""),
            ),
        )
    )

    logical_rows.append(
        (
            "row",
            (
                "Role",
                identity.get("role", ""),
            ),
        )
    )

    logical_rows.append(
        (
            "row",
            (
                "Location",
                identity.get("location", ""),
            ),
        )
    )

    logical_rows.append(
        (
            "row",
            (
                "OS",
                " / ".join(
                    system.get("os", [])
                ),
            ),
        )
    )

    logical_rows.append(
        (
            "row",
            (
                "Uptime",
                uptime,
            ),
        )
    )

    logical_rows.append(
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
        )
    )

    logical_rows.append(
        (
            "row",
            (
                "Focus",
                identity.get("tagline", ""),
            ),
        )
    )

    # --------------------------------------------------------
    # DEVELOPMENT
    # --------------------------------------------------------

    logical_rows.append(("gap", None))

    tools = " · ".join(
        development.get("tools", [])
    )

    ide = " · ".join(
        development.get("ide", [])
    )

    logical_rows.append(
        (
            "row",
            (
                "Tools",
                tools,
            ),
        )
    )

    logical_rows.append(
        (
            "row",
            (
                "IDE",
                ide,
            ),
        )
    )

    logical_rows.append(
        (
            "row",
            (
                "Status",
                development.get(
                    "status",
                    "",
                ),
            ),
        )
    )

    # --------------------------------------------------------
    # LANGUAGES
    # --------------------------------------------------------

    logical_rows.append(("gap", None))

    logical_rows.append(
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
        )
    )

    logical_rows.append(
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
        )
    )

    # --------------------------------------------------------
    # HOBBIES
    # --------------------------------------------------------

    logical_rows.append(("gap", None))

    logical_rows.append(
        (
            "row",
            (
                "Hobbies",
                " · ".join(hobbies),
            ),
        )
    )

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    logical_rows.append(("gap", None))

    logical_rows.append(
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

        logical_rows.append(
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

    # --------------------------------------------------------
    # CONTACT
    # --------------------------------------------------------

    logical_rows.append(("gap", None))

    logical_rows.append(
        (
            "section",
            "Contact",
        )
    )

    email = contact.get(
        "email",
        {},
    )

    personal_email = email.get(
        "personal",
        "",
    )

    college_email = email.get(
        "college",
        "",
    )

    if personal_email:
        logical_rows.append(
            (
                "row",
                (
                    "Email.Personal",
                    personal_email,
                ),
            )
        )

    if college_email:
        logical_rows.append(
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
        logical_rows.append(
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
        logical_rows.append(
            (
                "row",
                (
                    "X",
                    x_handle,
                ),
            )
        )

    # --------------------------------------------------------
    # GITHUB STATS
    # --------------------------------------------------------

    logical_rows.append(("gap", None))

    logical_rows.append(
        (
            "section",
            "GitHub Stats",
        )
    )

    logical_rows.append(
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
                "Commits",
                _number(
                    stats.get(
                        "commits",
                        0,
                    )
                ),
            ),
        )
    )

    logical_rows.append(
        (
            "stats",
            (
                "Stars",
                _number(
                    stats.get(
                        "stars",
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

    # LOC is displayed only if the backend actually provides it.
    if "loc" in stats:

        loc = _number(
            stats.get("loc", 0)
        )

        additions = stats.get(
            "additions"
        )

        deletions = stats.get(
            "deletions"
        )

        if (
            additions is not None
            and deletions is not None
        ):
            loc_value = (
                f"{loc} "
                f"(+{_number(additions)} / "
                f"-{_number(deletions)})"
            )
        else:
            loc_value = loc

        logical_rows.append(
            (
                "row",
                (
                    "LOC",
                    loc_value,
                ),
            )
        )

    else:
        logical_rows.append(
            (
                "row",
                (
                    "LOC",
                    "—",
                ),
            )
        )

    # --------------------------------------------------------
    # LAST UPDATED
    # --------------------------------------------------------

    logical_rows.append(("gap", None))

    logical_rows.append(
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

    rendered_row_units = 0

    for row_type, _ in logical_rows:

        if row_type == "gap":
            rendered_row_units += SECTION_GAP_ROWS
        else:
            rendered_row_units += 1

    HEIGHT = (
        PADDING_TOP
        + rendered_row_units * ROW_HEIGHT
        + PADDING_BOTTOM
    )

    # ========================================================
    # RENDER ROWS
    # ========================================================

    elements: list[str] = []

    y = PADDING_TOP + FONT_SIZE

    for row_type, payload in logical_rows:

        if row_type == "gap":
            y += (
                ROW_HEIGHT
                * SECTION_GAP_ROWS
            )
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
                _plain_text(
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
                _row(
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

        y += ROW_HEIGHT

    body = "\n".join(elements)

    # ========================================================
    # FINAL SVG
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
        font-size: 16px;
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
    rx="15"
    fill="{background}"
    stroke="{border_color}"
    stroke-width="1"
/>

{body}

</svg>
"""