"""Regenerate icons/ and the README skills table, or check they are up to date."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from .catalog import load_catalog
from .readme import ICON_DIR, render_table, splice
from .sources import Fetch, build_sources, http_fetch, render_icon


@dataclass(frozen=True)
class Plan:
    """Files the generator wants on disk, and stale icons to delete."""

    writes: dict[Path, str]
    deletes: tuple[Path, ...]


def plan(root: Path, fetch: Fetch = http_fetch) -> Plan:
    catalog = load_catalog(root / "skills.toml")
    sources = build_sources(catalog, fetch)
    icon_dir = root / ICON_DIR

    writes = {
        icon_dir / f"{skill.slug}.svg": render_icon(skill, sources) for skill in catalog.skills
    }
    readme = root / "README.md"
    writes[readme] = splice(readme.read_text(encoding="utf-8"), render_table(catalog))

    existing = icon_dir.glob("*.svg") if icon_dir.is_dir() else ()
    deletes = tuple(sorted(p for p in existing if p not in writes))
    return Plan(writes=writes, deletes=deletes)


def drift(p: Plan) -> list[Path]:
    """Paths whose on-disk content differs from the plan."""
    changed = [
        path
        for path, content in p.writes.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]
    return sorted(changed + list(p.deletes))


def apply(p: Plan) -> None:
    for path, content in p.writes.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    for path in p.deletes:
        path.unlink()


def main(argv: list[str] | None = None, fetch: Fetch = http_fetch) -> int:
    parser = argparse.ArgumentParser(prog="readme_gen", description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument(
        "--check", action="store_true", help="exit 1 if icons/ or README.md are out of date"
    )
    args = parser.parse_args(argv)

    p = plan(args.root, fetch)
    if args.check:
        stale = drift(p)
        for path in stale:
            print(f"out of date: {path.relative_to(args.root)}", file=sys.stderr)
        if stale:
            print("run `uv run python -m readme_gen` and commit the result", file=sys.stderr)
        return 1 if stale else 0

    apply(p)
    print(f"wrote {len(p.writes)} files, removed {len(p.deletes)} stale icons")
    return 0


if __name__ == "__main__":
    sys.exit(main())
