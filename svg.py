from html import escape
from typing import Any


def _text(x: int, y: int, value: object, css_class: str = "value") -> str:
    return f'<text x="{x}" y="{y}" class="{css_class}">{escape(str(value))}</text>'


def render_svg(
    profile: dict[str, Any],
    stats: dict[str, int],
    project_commits: dict[str, int],
    theme: str = "dark",
    uptime: str = "offline",
) -> str:
    if theme not in {"dark", "light"}:
        raise ValueError("theme must be 'dark' or 'light'")

    identity = profile["identity"]
    system = profile.get("system", {})
    projects = profile.get("projects", [])

    if theme == "dark":
        background, foreground, muted, accent = "#0d1117", "#e6edf3", "#8b949e", "#58a6ff"
    else:
        background, foreground, muted, accent = "#ffffff", "#1f2328", "#656d76", "#0969da"

    rows: list[str] = []
    y = 42
    rows.append(_text(28, y, f'{identity["username"]}@github', "heading"))
    y += 34
    rows.append(_text(28, y, "name", "label"))
    rows.append(_text(180, y, identity["name"]))
    y += 26
    rows.append(_text(28, y, "role", "label"))
    rows.append(_text(180, y, identity["role"]))
    y += 26
    rows.append(_text(28, y, "host", "label"))
    rows.append(_text(180, y, identity["institution"]))
    y += 26
    rows.append(_text(28, y, "os", "label"))
    rows.append(_text(180, y, " / ".join(system.get("os", []))))
    y += 26
    rows.append(_text(28, y, "uptime", "label"))
    rows.append(_text(180, y, uptime))

    y += 42
    rows.append(_text(28, y, "~/projects", "section"))
    for project in projects:
        y += 30
        rows.append(_text(44, y, project["name"], "project"))
        rows.append(_text(180, y, project.get("tagline", ""), "muted"))
        commits = project_commits.get(project["id"], 0)
        rows.append(_text(650, y, f"{commits} commits", "value-right"))

    y += 48
    rows.append(_text(28, y, "github --stats", "section"))
    for label in ("repositories", "commits", "stars", "followers"):
        y += 28
        rows.append(_text(44, y, label, "label"))
        rows.append(_text(300, y, stats.get(label, 0)))

    height = y + 34
    body = "\n  ".join(rows)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="{height}" viewBox="0 0 860 {height}" role="img" aria-label="Debrato Ghosh GitHub profile">
<style>
  .bg {{ fill: {background}; }}
  text {{ fill: {foreground}; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; font-size: 15px; }}
  .heading {{ fill: {accent}; font-size: 20px; font-weight: 700; }}
  .section {{ fill: {accent}; font-size: 16px; font-weight: 700; }}
  .label, .muted {{ fill: {muted}; }}
  .project {{ font-weight: 700; }}
  .value-right {{ text-anchor: end; }}
</style>
<rect class="bg" width="100%" height="100%" rx="12" />
  {body}
</svg>'''
