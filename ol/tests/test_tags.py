"""Tags are held to the list in the repository's ``track-tags.yml``."""

from __future__ import annotations

from pathlib import Path

import pytest
from test_validate import ARTICLE, FIXTURE, errors

from ol.authoring.validate import validate_file

TAG_FILE = "grammar:\n  - articles\nthemes:\n  - greetings\n"
TAGGED = FIXTURE.read_text(encoding="utf-8").replace(
    ":track: a1/grammar/bestimmter-artikel\n",
    ":track: a1/grammar/bestimmter-artikel\n:tags: articles, greetings\n",
    1,
)


def tagged(text: str = TAGGED, front: str = "tags: [articles]\n") -> str:
    return text.replace("---\n", "---\n" + front, 1)


def check(tmp_path: Path, text: str, listed: str | None = TAG_FILE):
    if listed is not None:
        (tmp_path / "track-tags.yml").write_text(listed, encoding="utf-8")
    found = errors(tmp_path, text)
    return found, validate_file(tmp_path / ARTICLE, tmp_path).items


class TestTrackTags:
    def test_listed_tags_pass(self, tmp_path):
        assert check(tmp_path, tagged())[0] == []

    def test_a_repository_without_the_file_is_not_held_to_tags(self, tmp_path):
        found, items = check(tmp_path, FIXTURE.read_text("utf-8"), listed=None)
        assert found == []
        assert not any("tags" in m for _, m in items)

    def test_a_block_that_writes_without_tags_is_red(self, tmp_path):
        untagged = tagged(TAGGED.replace(":tags: articles, greetings\n", ""))
        found, _ = check(tmp_path, untagged)
        assert any("no :tags:" in m for m in found), found

    def test_a_tag_not_in_the_list_is_red(self, tmp_path):
        found, _ = check(tmp_path, tagged(TAGGED.replace("greetings", "weather")))
        assert any("'weather' is not in track-tags.yml" in m for m in found), found

    def test_tags_compare_exactly_as_written(self, tmp_path):
        found, _ = check(tmp_path, tagged(TAGGED.replace("articles,", "Articles,")))
        assert any("'Articles' is not in track-tags.yml" in m for m in found), found

    def test_a_duplicate_block_needs_no_tags(self, tmp_path):
        duplicate = (
            ":::{audio-examples}\n:track: a1/grammar/other-page\n:duplicate:\n:::\n"
        )
        text = tagged().replace("## Summary", duplicate + "\n## Summary", 1)
        found, _ = check(tmp_path, text)
        assert not any("no :tags:" in m for m in found), found

    @pytest.mark.parametrize(
        ("front", "expected"),
        [
            ("tags: articles\n", "is a list of strings"),
            ("tags: [1]\n", "is a list of strings"),
            ("tags: [weather]\n", "front matter tag 'weather' is not in"),
        ],
    )
    def test_front_matter_tags_not_in_the_list_are_red(self, tmp_path, front, expected):
        found, _ = check(tmp_path, tagged(front=front))
        assert any(expected in m for m in found), found

    def test_an_article_without_tags_warns(self, tmp_path):
        _, items = check(tmp_path, tagged(front=""))
        assert any(lvl == "WARN" and "no 'tags:'" in m for lvl, m in items)

    @pytest.mark.parametrize(
        "listed",
        ["grammar: [a]\n", "grammar: a\nthemes: [b]\n", "grammar: [1]\nthemes: []\n"],
    )
    def test_a_file_that_is_not_two_lists_of_strings_is_red(self, tmp_path, listed):
        found, _ = check(tmp_path, tagged(), listed)
        assert any("is two lists of strings" in m for m in found), found
