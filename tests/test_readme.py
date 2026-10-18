import pytest

from readme_gen.catalog import parse_catalog
from readme_gen.readme import END_MARKER, GENERATED_NOTE, START_MARKER, render_table, splice

from .conftest import CATALOG_TOML, README


def test_render_table_starts_each_group_on_a_new_row_and_wraps():
    table = render_table(parse_catalog(CATALOG_TOML))
    rows = table.split("<tr>")[1:]
    cells_per_row = [row.count("<td") for row in rows]
    # Languages has 3 skills at 2 columns -> 2 + 1; Services has 2 -> 2.
    assert cells_per_row == [2, 1, 2]


def test_render_table_cell_markup_escapes_names():
    table = render_table(parse_catalog(CATALOG_TOML))
    assert '<img src="icons/cpp.svg" width="48" height="48" alt="C++" title="C++" />' in table
    assert "<br />AWS S3" in table


def test_splice_replaces_only_marked_region():
    out = splice(README, "<table></table>")
    assert out == (
        f"# Hi\n\n{START_MARKER}\n{GENERATED_NOTE}\n<table></table>\n{END_MARKER}\n\nFooter\n"
    )


def test_splice_is_idempotent():
    once = splice(README, "<table></table>")
    assert splice(once, "<table></table>") == once


@pytest.mark.parametrize("readme", ["no markers", f"{END_MARKER}\n{START_MARKER}"])
def test_splice_requires_ordered_markers(readme):
    with pytest.raises(ValueError):
        splice(readme, "<table></table>")
