"""Compose 256x256 rounded icon tiles that match the skill-icons style."""

from __future__ import annotations

import re
from html import escape

TILE_SIZE = 256
TILE_RADIUS = 60
TILE_BACKGROUND = "#242938"
GLYPH_SIZE = 144
MIN_CONTRAST = 4.5

_OPEN_TAG = re.compile(r"<svg\b[^>]*>", re.IGNORECASE)
_VIEWBOX = re.compile(r'viewBox="([^"]+)"')
_TITLE = re.compile(r"<title>.*?</title>", re.IGNORECASE | re.DOTALL)
_HEX = re.compile(r"^#?([0-9a-fA-F]{6})$")


def parse_svg(svg: str) -> tuple[str, str]:
    """Split an SVG document into its viewBox and inner markup (minus <title>)."""
    open_tag = _OPEN_TAG.search(svg)
    close = svg.lower().rfind("</svg>")
    if open_tag is None or close < open_tag.end():
        raise ValueError("not an SVG document")
    viewbox = _VIEWBOX.search(open_tag.group(0))
    if viewbox is None:
        raise ValueError("SVG has no viewBox")
    inner = _TITLE.sub("", svg[open_tag.end() : close]).strip()
    return viewbox.group(1), inner


def _rgb(color: str) -> tuple[int, int, int]:
    match = _HEX.match(color)
    if match is None:
        raise ValueError(f"expected a #RRGGBB colour, got {color!r}")
    value = match.group(1)
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _luminance(color: str) -> float:
    def linear(channel: int) -> float:
        c = channel / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (linear(c) for c in _rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: str, b: str) -> float:
    """WCAG contrast ratio between two colours."""
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def ensure_contrast(
    color: str, background: str = TILE_BACKGROUND, minimum: float = MIN_CONTRAST
) -> str:
    """Return ``color`` blended toward white just enough to stand out on ``background``."""
    r, g, b = _rgb(color)
    for step in range(0, 101, 5):
        t = step / 100
        blended = "#{:02X}{:02X}{:02X}".format(*(round(c + (255 - c) * t) for c in (r, g, b)))
        if contrast_ratio(blended, background) >= minimum:
            return blended
    return "#FFFFFF"


def _tile(body: str, defs: str = "") -> str:
    return (
        f'<svg width="{TILE_SIZE}" height="{TILE_SIZE}" viewBox="0 0 {TILE_SIZE} {TILE_SIZE}" '
        f'fill="none" xmlns="http://www.w3.org/2000/svg">\n'
        f"{defs}"
        f'<rect width="{TILE_SIZE}" height="{TILE_SIZE}" rx="{TILE_RADIUS}" '
        f'fill="{TILE_BACKGROUND}"/>\n'
        f"{body}\n"
        f"</svg>\n"
    )


def glyph_tile(svg: str, color: str) -> str:
    """Centre a single-colour glyph (e.g. Simple Icons) on a dark tile."""
    viewbox, inner = parse_svg(svg)
    offset = (TILE_SIZE - GLYPH_SIZE) // 2
    fill = ensure_contrast(color)
    return _tile(
        f'<svg x="{offset}" y="{offset}" width="{GLYPH_SIZE}" height="{GLYPH_SIZE}" '
        f'viewBox="{viewbox}"><g fill="{fill}">{inner}</g></svg>'
    )


def full_bleed_tile(svg: str) -> str:
    """Scale an icon with its own square background to the tile and round its corners."""
    viewbox, inner = parse_svg(svg)
    defs = (
        f'<defs><clipPath id="tile"><rect width="{TILE_SIZE}" height="{TILE_SIZE}" '
        f'rx="{TILE_RADIUS}"/></clipPath></defs>\n'
    )
    return _tile(
        f'<g clip-path="url(#tile)"><svg width="{TILE_SIZE}" height="{TILE_SIZE}" '
        f'viewBox="{viewbox}">{inner}</svg></g>',
        defs,
    )


def monogram_font_size(text: str) -> int:
    """Largest font size that keeps ``text`` inside the glyph area."""
    return min(120, 300 // max(len(text), 1))


def monogram_tile(text: str, color: str) -> str:
    """Draw short text on a dark tile for tools that have no logo."""
    if not text:
        raise ValueError("monogram text must not be empty")
    size = monogram_font_size(text)
    return _tile(
        f'<text x="{TILE_SIZE // 2}" y="{TILE_SIZE // 2}" text-anchor="middle" '
        f'dominant-baseline="central" font-family="-apple-system, BlinkMacSystemFont, '
        f'Segoe UI, Helvetica, Arial, sans-serif" font-size="{size}" font-weight="700" '
        f'fill="{ensure_contrast(color)}">{escape(text)}</text>'
    )
