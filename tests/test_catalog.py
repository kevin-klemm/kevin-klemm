from pathlib import Path

import pytest

from readme_gen.catalog import CatalogError, Skill, load_catalog, parse_catalog
from readme_gen.sources import build_sources

from .conftest import CATALOG_TOML

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("name", "slug"),
    [
        ("C++", "cpp"),
        ("GitHub Actions", "github-actions"),
        ("AWS S3", "aws-s3"),
        ("gtest", "gtest"),
    ],
)
def test_slug(name, slug):
    assert Skill(name=name, kind="monogram").slug == slug


def test_parse_catalog_preserves_group_order():
    catalog = parse_catalog(CATALOG_TOML)
    assert catalog.columns == 2
    assert [g.name for g in catalog.groups] == ["Languages", "Services"]
    assert [s.name for s in catalog.skills] == ["C", "C++", "YAML", "AWS S3", "gtest"]
    assert catalog.sources["simple-icons"] == "1.0.0"


def test_parse_catalog_rejects_duplicate_slugs():
    text = CATALOG_TOML.replace('name = "C++"', 'name = "c"')
    with pytest.raises(CatalogError, match="share icon slug"):
        parse_catalog(text)


def test_parse_catalog_rejects_unknown_fields():
    text = CATALOG_TOML.replace('ref = "C" }', 'ref = "C", colour = "#fff" }')
    with pytest.raises(CatalogError, match="malformed"):
        parse_catalog(text)


def test_parse_catalog_rejects_non_positive_columns():
    with pytest.raises(CatalogError, match="columns"):
        parse_catalog(CATALOG_TOML.replace("columns = 2", "columns = 0"))


def test_repository_catalog_only_uses_pinned_sources():
    catalog = load_catalog(REPO_ROOT / "skills.toml")
    sources = build_sources(catalog, fetch=lambda url: "")
    assert {s.kind for s in catalog.skills} <= set(sources)
