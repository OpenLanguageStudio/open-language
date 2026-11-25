"""An article's ``related:`` front matter is held to the rules of Related articles."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from test_validate import ARTICLE, FIXTURE, errors, write_index, write_page

from ol.authoring.validate import validate_file

FLAT_ARTICLE = "a1/grammar/bestimmter-artikel.md"


@pytest.fixture
def source() -> str:
    """The fixture article without its hand-written Related articles section."""
    text = FIXTURE.read_text(encoding="utf-8")
    return re.sub(r"\n## Related articles\n.*\Z", "\n", text, flags=re.S)


def with_related(source: str, value: str) -> str:
    return source.replace("---\n", f"---\nrelated: {value}\n", 1)


def items(tmp_path: Path, text: str, name: str = ARTICLE):
    errors(tmp_path, text, name)
    return validate_file(tmp_path / name, tmp_path).items


class TestRelatedFrontMatter:
    def test_entries_naming_pages_pass(self, tmp_path, source):
        write_page(tmp_path, "a1/grammar/other/sein.md")
        text = with_related(source, "[/a1/grammar/other/sein, ../other/sein]")
        assert errors(tmp_path, text) == []

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("sein", "is a list of page paths"),
            ("[1, 2]", "is a list of page paths"),
            ("[/a1/grammar/other/sein.md]", "ends in .md"),
            ("[/a1/grammar/other/missing]", "names no page"),
            ("[bestimmter-artikel]", "is the page itself"),
        ],
    )
    def test_a_bad_entry_is_red(self, tmp_path, source, value, expected):
        write_page(tmp_path, "a1/grammar/other/sein.md")
        found = errors(tmp_path, with_related(source, value))
        assert any(expected in m for m in found), found

    def test_an_entry_is_held_to_the_subcategory_rule(self, tmp_path, source):
        write_page(tmp_path, "a1/grammar/articles/negativartikel.md")
        found = errors(
            tmp_path, with_related(source, "[/a1/grammar/articles/negativartikel]")
        )
        assert any("same subcategory" in m for m in found), found

    def test_an_entry_is_held_to_the_toctree_neighbour_rule(self, tmp_path, source):
        write_index(tmp_path, "a1/grammar", "bestimmter-artikel", "sein")
        write_page(tmp_path, "a1/grammar/sein.md")
        found = errors(tmp_path, with_related(source, "[sein]"), FLAT_ARTICLE)
        assert any("next to this article in the toctree" in m for m in found), found

    def test_front_matter_and_a_written_section_together_are_red(self, tmp_path):
        text = with_related(FIXTURE.read_text(encoding="utf-8"), "[]")
        found = errors(tmp_path, text)
        assert any("both 'related:'" in m for m in found), found

    def test_a_written_section_alone_warns(self, tmp_path, source):
        text = FIXTURE.read_text(encoding="utf-8")
        found = items(tmp_path, text)
        assert any(lvl == "WARN" and "written by hand" in m for lvl, m in found)
