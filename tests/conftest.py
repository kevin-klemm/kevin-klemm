import pytest

GLYPH_SVG = (
    '<svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
    '<title>Example</title><path d="M0 0h24v24H0z"/></svg>'
)
FULL_BLEED_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><title>Icon</title>'
    '<g fill="none"><path fill="#8c4fff" d="M0 0h64v64H0z"/></g></svg>'
)
TILE_SVG = '<svg width="256" height="256" viewBox="0 0 256 256"><rect/></svg>\n'

CATALOG_TOML = """
[sources]
skill-icons = "abc123"
simple-icons = "1.0.0"
aws-icons = "2.0.0"

[layout]
columns = 2

[[groups]]
name = "Languages"
skills = [
  { name = "C", kind = "skill-icons", ref = "C" },
  { name = "C++", kind = "skill-icons", ref = "CPP" },
  { name = "YAML", kind = "simple-icons", ref = "yaml", color = "#CB171E" },
]

[[groups]]
name = "Services"
skills = [
  { name = "AWS S3", kind = "aws-icons", ref = "architecture-service/S3" },
  { name = "gtest", kind = "monogram", text = "gtest", color = "#34A853" },
]
"""

README = "# Hi\n\n<!-- skills:start -->\nold table\n<!-- skills:end -->\n\nFooter\n"


class FakeFetch:
    """Serves canned SVGs by URL fragment and records every request."""

    def __init__(self) -> None:
        self.urls: list[str] = []

    def __call__(self, url: str) -> str:
        self.urls.append(url)
        if "skill-icons" in url:
            return TILE_SVG
        if "simple-icons" in url:
            return GLYPH_SVG
        if "aws-icons" in url:
            return FULL_BLEED_SVG
        raise AssertionError(f"unexpected URL {url}")


@pytest.fixture
def fake_fetch() -> FakeFetch:
    return FakeFetch()


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "skills.toml").write_text(CATALOG_TOML)
    (tmp_path / "README.md").write_text(README)
    return tmp_path
