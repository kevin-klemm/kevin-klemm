import pytest

from readme_gen.catalog import CatalogError, Skill, parse_catalog
from readme_gen.sources import build_sources, render_icon

from .conftest import CATALOG_TOML, TILE_SVG


@pytest.fixture
def sources(fake_fetch):
    return build_sources(parse_catalog(CATALOG_TOML), fake_fetch)


def test_skill_icons_are_used_verbatim_from_pinned_commit(sources, fake_fetch):
    svg = render_icon(Skill(name="C", kind="skill-icons", ref="C"), sources)
    assert svg == TILE_SVG
    assert fake_fetch.urls == [
        "https://cdn.jsdelivr.net/gh/tandpfun/skill-icons@abc123/icons/C.svg"
    ]


def test_simple_icons_are_placed_on_a_tile(sources, fake_fetch):
    svg = render_icon(Skill(name="YAML", kind="simple-icons", ref="yaml", color="#FCC624"), sources)
    assert '<g fill="#FCC624">' in svg
    assert fake_fetch.urls == ["https://cdn.jsdelivr.net/npm/simple-icons@1.0.0/icons/yaml.svg"]


def test_aws_icons_are_clipped(sources, fake_fetch):
    svg = render_icon(Skill(name="S3", kind="aws-icons", ref="architecture-service/S3"), sources)
    assert 'clip-path="url(#tile)"' in svg
    assert fake_fetch.urls == [
        "https://cdn.jsdelivr.net/npm/aws-icons@2.0.0/icons/architecture-service/S3.svg"
    ]


def test_monogram_needs_no_network(sources, fake_fetch):
    svg = render_icon(Skill(name="gtest", kind="monogram", text="gtest", color="#34A853"), sources)
    assert ">gtest</text>" in svg
    assert fake_fetch.urls == []


@pytest.mark.parametrize(
    "skill",
    [
        Skill(name="NoRef", kind="skill-icons"),
        Skill(name="NoColor", kind="simple-icons", ref="yaml"),
        Skill(name="NoText", kind="monogram", color="#FFFFFF"),
    ],
)
def test_missing_required_fields_are_reported(sources, skill):
    with pytest.raises(CatalogError, match=skill.name):
        render_icon(skill, sources)


def test_unknown_kind_is_reported(sources):
    with pytest.raises(CatalogError, match="unknown or unpinned"):
        render_icon(Skill(name="X", kind="devicon", ref="x"), sources)


def test_unpinned_remote_source_is_unavailable(fake_fetch):
    catalog = parse_catalog(CATALOG_TOML.replace('aws-icons = "2.0.0"', ""))
    assert "aws-icons" not in build_sources(catalog, fake_fetch)
