"""The build draws the target-language title, culture notes and wanted pages."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest
from sphinx.application import Sphinx
from typer.testing import CliRunner

from ol.authoring.wanted import page_link, wanted_pages, words_of
from ol.cli import app


class Build:
    def __init__(self, root: Path, pages: dict[str, str], builder: str = "html"):
        self.src = root / "src"
        self.src.mkdir(parents=True)
        (self.src / "conf.py").write_text(
            'extensions = ["myst_parser", "sphinx_design", "ol.docs.audio_examples"]\n'
            'myst_enable_extensions = ["colon_fence"]\n'
            "suppress_warnings = ['toc.not_included']\n"
        )
        for name, text in pages.items():
            page = self.src / f"{name}.md"
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(text, encoding="utf-8")
        self.out = root / "out"
        self.builder = builder
        self.warnings = StringIO()
        self.status = StringIO()
        Sphinx(
            str(self.src),
            str(self.src),
            str(self.out),
            str(root / "doctrees"),
            builder,
            status=self.status,
            warning=self.warnings,
            freshenv=True,
            warningiserror=True,
        ).build()

    def html(self, name: str = "index") -> str:
        return (self.out / f"{name}.html").read_text(encoding="utf-8")

    def latex(self) -> str:
        return next(self.out.glob("*.tex")).read_text(encoding="utf-8")


@pytest.fixture
def language_repository(tmp_path, monkeypatch):
    config = tmp_path / "open-language.yml"
    config.write_text("language: German\nlanguage_code: de\n", encoding="utf-8")
    monkeypatch.setenv("OPEN_LANGUAGE_CONFIG", str(config))
    return config


@pytest.fixture
def build(tmp_path, language_repository):
    def run(pages, builder="html"):
        if isinstance(pages, str):
            pages = {"index": pages}
        return Build(tmp_path / builder, pages, builder)

    return run


TITLED = "---\ntarget-title: Sich vorstellen\n---\n# Introduce yourself\n\nThe lead.\n"
NOTE = ":::{culture-note}\nGermans often give only their surname at work.\n:::\n"


class TestTargetTitle:
    def test_it_is_drawn_straight_under_the_h1_in_the_language_taught(self, build):
        html = build(TITLED).html()
        title = '<p class="ol-target-title" lang="de">Sich vorstellen</p>'
        assert title in html
        assert html.index("<h1>Introduce yourself") < html.index(title)
        assert html.index(title) < html.index("The lead.")

    def test_it_is_not_a_heading(self, build):
        html = build(TITLED).html()
        assert "<h2>Sich vorstellen" not in html
        assert 'id="sich-vorstellen"' not in html

    def test_a_page_without_one_has_none(self, build):
        html = build("# Introduce yourself\n\nThe lead.\n").html()
        assert "ol-target-title" not in html

    def test_the_latex_output_sets_it_under_the_title(self, build):
        tex = build(TITLED, "latex").latex()
        assert "\\begingroup\\large\\itshape Sich vorstellen\\par\\endgroup" in tex


class TestCultureNote:
    def test_it_is_a_notice_with_its_own_title_and_class(self, build):
        html = build(f"# Greet\n\nThe lead.\n\n{NOTE}").html()
        assert 'class="ol-culture-note admonition"' in html
        assert '<p class="admonition-title">Culture note</p>' in html
        assert "only their surname at work" in html

    def test_the_latex_output_draws_it_in_its_own_colours(self, build):
        tex = build(f"# Greet\n\nThe lead.\n\n{NOTE}", "latex").latex()
        assert "div.note_border-TeXcolor={HTML}{6B3D99}" in tex
        assert "\\begin{sphinxadmonition}{note}" in tex
        assert "\\end{sphinxadmonition}}" in tex


class TestWantedPages:
    PAGES = {
        "index": "# Course\n\n```{toctree}\na1/greet\n```\n",
        "a1/greet": (
            "# Greet\n\nUse the formal form ([](/a1/grammar/formal-you.md)).\n\n"
            "Read [the dative](/a1/grammar/dativ.md) first.\n"
        ),
    }

    def test_a_link_to_a_missing_page_is_drawn_as_its_text(self, build):
        html = build(self.PAGES).html("a1/greet")
        assert '<span class="ol-wanted">the dative</span>' in html

    def test_a_link_with_no_text_shows_the_page_name_as_words(self, build):
        html = build(self.PAGES).html("a1/greet")
        assert '<span class="ol-wanted">Formal you</span>' in html

    def test_the_build_passes_and_logs_each_wanted_page(self, build):
        done = build(self.PAGES)
        assert "dativ" not in done.warnings.getvalue()
        assert "wanted page a1/grammar/dativ\n" in done.status.getvalue()

    def test_a_link_to_a_page_that_exists_is_still_a_link(self, build):
        pages = dict(self.PAGES)
        pages["index"] = "# Course\n\n```{toctree}\na1/greet\na1/grammar/dativ\n```\n"
        pages["a1/grammar/dativ"] = "# Dativ\n\nThe case.\n"
        html = build(pages).html("a1/greet")
        assert 'ol-wanted">the dative' not in html
        assert 'href="grammar/dativ.html"' in html
        assert '<span class="ol-wanted">Formal you</span>' in html


class TestExampleTabs:
    def test_example_blocks_in_formal_and_informal_tabs_are_drawn(self, build):
        block = ":::{{ol-examples}}\n:presenters: emilia\n{}\n: Hello.\n:::\n"
        page = (
            "# Greet\n\nThe lead.\n\n::::::{tab-set}\n\n"
            f":::::{{tab-item}} Informal\n{block.format('Hallo')}:::::\n\n"
            f":::::{{tab-item}} Formal\n{block.format('Guten Tag')}:::::\n\n"
            "::::::\n"
        )
        html = build(page).html()
        assert html.count("sd-tab-item") >= 2
        assert html.count('class="ol-examples') == 2
        assert "Hallo" in html
        assert "Guten Tag" in html


class TestPageLink:
    @pytest.mark.parametrize(
        ("target", "page"),
        [
            ("/a1/grammar/cases/dativ.md", "a1/grammar/cases/dativ"),
            ("/a1/grammar/cases/dativ", "a1/grammar/cases/dativ"),
            ("dativ.md#use", "a1/grammar/dativ"),
            ("../how-to/greet.md", "a1/how-to/greet"),
        ],
    )
    def test_a_page_link_names_its_page(self, target, page):
        assert page_link("a1/grammar/akkusativ", target) == page

    @pytest.mark.parametrize(
        "target",
        ["https://example.org/a.md", "#use", "dativ", "/a1/_static/sound.mp3"],
    )
    def test_anything_else_names_no_page(self, target):
        assert page_link("a1/grammar/akkusativ", target) is None

    def test_the_words_of_a_page_name(self):
        assert words_of("a1/grammar/formal-you") == "Formal you"


def write(root: Path, name: str, text: str) -> None:
    page = root / f"{name}.md"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(text, encoding="utf-8")


def test_wanted_pages_maps_each_missing_page_to_its_linking_pages(tmp_path):
    write(tmp_path, "a1/grammar/dativ", "# Dativ\n\nSee [](akkusativ.md).\n")
    write(tmp_path, "a1/how-to/greet", "# Greet\n\nSee [](/a1/grammar/akkusativ.md).\n")
    write(tmp_path, "a1/how-to/thank", "# Thank\n\nSee [](/a1/grammar/dativ.md).\n")
    found = wanted_pages(tmp_path, sorted(tmp_path.rglob("*.md")))
    assert found == {"a1/grammar/akkusativ": ["a1/grammar/dativ", "a1/how-to/greet"]}


def test_a_link_in_code_is_not_wanted(tmp_path):
    write(tmp_path, "a1/how-to/greet", "# Greet\n\n```\n[](/a1/x/missing.md)\n```\n")
    assert wanted_pages(tmp_path, [tmp_path / "a1/how-to/greet.md"]) == {}


def test_ol_wanted_lists_each_page_with_the_pages_that_link_to_it(tmp_path):
    (tmp_path / "open-language.yml").write_text("language: German\nlanguage_code: de\n")
    write(tmp_path, "a1/how-to/greet", "# Greet\n\nSee [](/a1/grammar/dativ.md).\n")
    result = CliRunner().invoke(app, ["wanted", "--workspace", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "a1/grammar/dativ\n    linked from a1/how-to/greet" in result.output


def test_ol_wanted_says_when_nothing_is_wanted(tmp_path):
    (tmp_path / "open-language.yml").write_text("language: German\nlanguage_code: de\n")
    write(tmp_path, "a1/how-to/greet", "# Greet\n\nNo links.\n")
    result = CliRunner().invoke(app, ["wanted", "--workspace", str(tmp_path)])
    assert result.exit_code == 0
    assert "No wanted pages" in result.output


def test_a_related_entry_that_names_no_page_still_stops_the_build(build):
    pages = {
        "index": "# Course\n\n```{toctree}\na1/greet\n```\n",
        "a1/greet": "---\nrelated:\n  - /a1/grammar/missing.md\n---\n# Greet\n\nLead.\n",
    }
    with pytest.raises(Exception, match="not pages"):
        build(pages)
