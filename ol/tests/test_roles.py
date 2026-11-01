"""A standalone Sphinx build stacks a phrase over its translation."""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import pytest
from sphinx.application import Sphinx

STACKED = (
    '<span class="ol-stack"><span class="ol-stack-target" lang="de">'
    'Guten Morgen</span><span class="ol-stack-translation">Good morning'
    "</span></span>"
)
PHRASE = "{stack}`Guten Morgen | Good morning`"


class Build:
    def __init__(self, root: Path, page: str, builder: str = "html"):
        self.src = root / "src"
        self.src.mkdir(parents=True)
        (self.src / "conf.py").write_text(
            'extensions = ["myst_parser", "ol.docs.roles"]\n'
        )
        (self.src / "index.md").write_text(page, encoding="utf-8")
        self.out = root / "out"
        self.warnings = StringIO()
        Sphinx(
            str(self.src),
            str(self.src),
            str(self.out),
            str(root / "doctrees"),
            builder,
            status=None,
            warning=self.warnings,
            freshenv=True,
        ).build()

    def output(self, filename: str = "index.html") -> str:
        return (self.out / filename).read_text(encoding="utf-8")


@pytest.fixture
def language_repository(tmp_path, monkeypatch):
    """Point the build at a language repository's configuration."""
    config = tmp_path / "open-language.yml"
    config.write_text("language: German\nlanguage_code: de\n", encoding="utf-8")
    monkeypatch.setenv("OPEN_LANGUAGE_CONFIG", str(config))
    return config


@pytest.fixture
def build(tmp_path, language_repository):
    return lambda page, builder="html": Build(tmp_path / "site", page, builder)


class TestStackRole:
    def test_a_paragraph_shows_the_translation_beneath_the_phrase(self, build):
        done = build(f"# Index\n\nSay {PHRASE} to a friend.\n")
        assert STACKED in done.output()

    def test_a_table_cell_shows_the_translation_beneath_the_phrase(self, build):
        # A pipe table splits a cell at every pipe, so the separator is escaped.
        phrase = PHRASE.replace(" | ", r" \| ")
        table = f"| Phrase | Notes |\n|---|---|\n| {phrase} | Until noon. |\n"
        done = build(f"# Index\n\n{table}")
        assert STACKED in done.output()
        assert done.output().count("<td>") == 2

    def test_a_list_item_shows_the_translation_beneath_the_phrase(self, build):
        done = build(f"# Index\n\n- {PHRASE}\n- Something else\n")
        assert STACKED in done.output()

    def test_the_dirhtml_builder_renders_the_same_markup(self, build):
        done = build(f"# Index\n\n{PHRASE}\n", "dirhtml")
        assert STACKED in done.output("index.html")

    def test_the_json_builder_renders_the_same_markup(self, build):
        done = build(f"# Index\n\n{PHRASE}\n", "json")
        assert STACKED in json.loads(done.output("index.fjson"))["body"]

    def test_the_phrase_and_translation_are_escaped(self, build):
        done = build('# Index\n\n{stack}`<b>Hallo</b> | Hi & "bye"`\n')
        assert "&lt;b&gt;Hallo&lt;/b&gt;" in done.output()
        assert "Hi &amp; &quot;bye&quot;" in done.output()

    def test_only_the_first_separator_splits_the_text(self, build):
        done = build("# Index\n\n{stack}`Ja | Yes | of course`\n")
        assert '<span class="ol-stack-translation">Yes | of course</span>' in (
            done.output()
        )

    def test_no_lang_is_written_when_the_repository_sets_no_language_code(
        self, build, language_repository
    ):
        language_repository.write_text("language: German\n", encoding="utf-8")
        done = build(f"# Index\n\n{PHRASE}\n")
        assert '<span class="ol-stack-target">Guten Morgen</span>' in done.output()

    def test_a_missing_separator_warns_with_the_page_and_line(self, build):
        done = build("# Index\n\nFirst line.\n\nSay {stack}`Guten Morgen` here.\n")
        assert "index.md:5" in done.warnings.getvalue()

    def test_a_missing_separator_shows_the_text_unstacked(self, build):
        done = build("# Index\n\nSay {stack}`Guten Morgen` here.\n")
        assert "ol-stack" not in done.output()
        assert "Say Guten Morgen here." in done.output()
