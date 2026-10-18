import pytest

from readme_gen import tiles

from .conftest import FULL_BLEED_SVG, GLYPH_SVG


def test_parse_svg_returns_viewbox_and_strips_title():
    viewbox, inner = tiles.parse_svg(GLYPH_SVG)
    assert viewbox == "0 0 24 24"
    assert inner == '<path d="M0 0h24v24H0z"/>'


@pytest.mark.parametrize("svg", ["<div/>", '<svg width="1"></svg>', "<svg viewBox='0 0 1 1'>"])
def test_parse_svg_rejects_invalid_documents(svg):
    with pytest.raises(ValueError):
        tiles.parse_svg(svg)


def test_contrast_ratio_extremes():
    assert tiles.contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0)
    assert tiles.contrast_ratio("#242938", "#242938") == pytest.approx(1.0)


def test_ensure_contrast_keeps_bright_colours():
    assert tiles.ensure_contrast("#FCC624") == "#FCC624"


@pytest.mark.parametrize("color", ["#333333", "#721412", "#262D3A"])
def test_ensure_contrast_lightens_dark_colours(color):
    lightened = tiles.ensure_contrast(color)
    assert lightened != color
    assert tiles.contrast_ratio(lightened, tiles.TILE_BACKGROUND) >= tiles.MIN_CONTRAST


def test_ensure_contrast_rejects_bad_hex():
    with pytest.raises(ValueError):
        tiles.ensure_contrast("red")


def test_glyph_tile_centres_glyph_with_brand_colour():
    svg = tiles.glyph_tile(GLYPH_SVG, "#FCC624")
    assert f'rx="{tiles.TILE_RADIUS}" fill="{tiles.TILE_BACKGROUND}"' in svg
    assert 'x="56" y="56" width="144" height="144" viewBox="0 0 24 24"' in svg
    assert '<g fill="#FCC624"><path d="M0 0h24v24H0z"/></g>' in svg
    assert "<title>" not in svg


def test_full_bleed_tile_clips_icon_to_rounded_tile():
    svg = tiles.full_bleed_tile(FULL_BLEED_SVG)
    assert '<clipPath id="tile">' in svg
    assert 'clip-path="url(#tile)"' in svg
    assert 'viewBox="0 0 64 64"><g fill="none">' in svg


def test_monogram_font_shrinks_with_length():
    sizes = [tiles.monogram_font_size(t) for t in ("Vg", "SQL", "gcov", "gtest")]
    assert sizes == sorted(sizes, reverse=True)
    assert sizes[0] == 120


def test_monogram_tile_escapes_text():
    svg = tiles.monogram_tile("C&", "#4479A1")
    assert ">C&amp;</text>" in svg


def test_monogram_tile_requires_text():
    with pytest.raises(ValueError):
        tiles.monogram_tile("", "#FFFFFF")
