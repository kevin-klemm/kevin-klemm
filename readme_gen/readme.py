"""Render the skills table and splice it into README.md."""

from __future__ import annotations

from html import escape

from .catalog import Catalog, Skill

START_MARKER = "<!-- skills:start -->"
END_MARKER = "<!-- skills:end -->"
GENERATED_NOTE = (
    "<!-- Generated from skills.toml by `uv run python -m readme_gen`. Do not edit. -->"
)
ICON_DIR = "icons"
ICON_SIZE = 48


def icon_path(skill: Skill) -> str:
    return f"{ICON_DIR}/{skill.slug}.svg"


def _cell(skill: Skill) -> str:
    name = escape(skill.name)
    return (
        f'    <td align="center">\n'
        f'      <img src="{icon_path(skill)}" width="{ICON_SIZE}" height="{ICON_SIZE}" '
        f'alt="{name}" title="{name}" /><br />{name}\n'
        f"    </td>"
    )


def render_table(catalog: Catalog) -> str:
    """HTML table with one row per group, wrapped at ``catalog.columns`` cells."""
    rows: list[str] = []
    for group in catalog.groups:
        skills = group.skills
        for start in range(0, len(skills), catalog.columns):
            cells = "\n".join(_cell(s) for s in skills[start : start + catalog.columns])
            rows.append(f"  <tr>\n{cells}\n  </tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def splice(readme: str, table: str) -> str:
    """Replace everything between the skills markers with ``table``."""
    start = readme.find(START_MARKER)
    end = readme.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"README must contain {START_MARKER} followed by {END_MARKER}")
    head = readme[: start + len(START_MARKER)]
    return f"{head}\n{GENERATED_NOTE}\n{table}\n{readme[end:]}"
