"""Icon sources: each turns a :class:`Skill` into a finished SVG tile."""

from __future__ import annotations

import urllib.request
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping

from . import tiles
from .catalog import Catalog, CatalogError, Skill

Fetch = Callable[[str], str]


def http_fetch(url: str) -> str:
    """Download ``url`` as UTF-8 text."""
    request = urllib.request.Request(url, headers={"User-Agent": "readme_gen"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def _require(skill: Skill, field: str) -> str:
    value = getattr(skill, field)
    if not value:
        raise CatalogError(f"{skill.name!r} ({skill.kind}) needs {field!r}")
    return value


class IconSource(ABC):
    """Renders the icon tile for skills of one ``kind``."""

    kind: str

    @abstractmethod
    def render(self, skill: Skill) -> str:
        """Return the SVG tile for ``skill``."""


class RemoteSource(IconSource):
    """A source that downloads from a version-pinned CDN path."""

    def __init__(self, fetch: Fetch, version: str) -> None:
        self._fetch = fetch
        self._version = version

    @abstractmethod
    def url(self, ref: str) -> str: ...

    def download(self, skill: Skill) -> str:
        return self._fetch(self.url(_require(skill, "ref")))


class SkillIcons(RemoteSource):
    """Ready-made tiles from tandpfun/skill-icons, used as-is."""

    kind = "skill-icons"

    def url(self, ref: str) -> str:
        return f"https://cdn.jsdelivr.net/gh/tandpfun/skill-icons@{self._version}/icons/{ref}.svg"

    def render(self, skill: Skill) -> str:
        return self.download(skill).rstrip() + "\n"


class SimpleIcons(RemoteSource):
    """Simple Icons glyphs coloured with the brand hex on a dark tile."""

    kind = "simple-icons"

    def url(self, ref: str) -> str:
        return f"https://cdn.jsdelivr.net/npm/simple-icons@{self._version}/icons/{ref}.svg"

    def render(self, skill: Skill) -> str:
        return tiles.glyph_tile(self.download(skill), _require(skill, "color"))


class AwsIcons(RemoteSource):
    """AWS Architecture icons, clipped to a rounded tile."""

    kind = "aws-icons"

    def url(self, ref: str) -> str:
        return f"https://cdn.jsdelivr.net/npm/aws-icons@{self._version}/icons/{ref}.svg"

    def render(self, skill: Skill) -> str:
        return tiles.full_bleed_tile(self.download(skill))


class Monogram(IconSource):
    """Text tiles for tools without a usable logo."""

    kind = "monogram"

    def render(self, skill: Skill) -> str:
        return tiles.monogram_tile(_require(skill, "text"), _require(skill, "color"))


REMOTE_SOURCES: tuple[type[RemoteSource], ...] = (SkillIcons, SimpleIcons, AwsIcons)


def build_sources(catalog: Catalog, fetch: Fetch = http_fetch) -> Mapping[str, IconSource]:
    """Instantiate every source, pinned to the versions in ``catalog.sources``."""
    sources: dict[str, IconSource] = {Monogram.kind: Monogram()}
    for cls in REMOTE_SOURCES:
        version = catalog.sources.get(cls.kind)
        if version:
            sources[cls.kind] = cls(fetch, version)
    return sources


def render_icon(skill: Skill, sources: Mapping[str, IconSource]) -> str:
    source = sources.get(skill.kind)
    if source is None:
        raise CatalogError(
            f"{skill.name!r}: unknown or unpinned icon kind {skill.kind!r} "
            f"(known: {', '.join(sorted(sources))})"
        )
    return source.render(skill)
