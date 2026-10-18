"""Load and validate the skills catalog (``skills.toml``)."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path


class CatalogError(ValueError):
    """The catalog file is malformed."""


@dataclass(frozen=True)
class Skill:
    """One cell of the skills table."""

    name: str
    kind: str
    ref: str | None = None
    color: str | None = None
    text: str | None = None

    @property
    def slug(self) -> str:
        """File stem for the skill's icon, e.g. ``C++`` -> ``cpp``."""
        name = self.name.lower().replace("+", "p")
        return re.sub(r"[^a-z0-9]+", "-", name).strip("-")


@dataclass(frozen=True)
class Group:
    """Skills that start on a new table row."""

    name: str
    skills: tuple[Skill, ...]


@dataclass(frozen=True)
class Catalog:
    """Everything the generator needs from ``skills.toml``."""

    sources: dict[str, str]
    columns: int
    groups: tuple[Group, ...]

    @property
    def skills(self) -> tuple[Skill, ...]:
        return tuple(skill for group in self.groups for skill in group.skills)


def parse_catalog(text: str) -> Catalog:
    """Parse catalog TOML, rejecting duplicate icon slugs."""
    data = tomllib.loads(text)
    try:
        groups = tuple(
            Group(name=g["name"], skills=tuple(Skill(**s) for s in g["skills"]))
            for g in data["groups"]
        )
        catalog = Catalog(
            sources=dict(data.get("sources", {})),
            columns=int(data["layout"]["columns"]),
            groups=groups,
        )
    except (KeyError, TypeError) as exc:
        raise CatalogError(f"malformed catalog: {exc}") from exc

    if catalog.columns < 1:
        raise CatalogError("layout.columns must be positive")
    seen: dict[str, str] = {}
    for skill in catalog.skills:
        if skill.slug in seen:
            raise CatalogError(
                f"{skill.name!r} and {seen[skill.slug]!r} share icon slug {skill.slug!r}"
            )
        seen[skill.slug] = skill.name
    return catalog


def load_catalog(path: Path) -> Catalog:
    return parse_catalog(path.read_text(encoding="utf-8"))
