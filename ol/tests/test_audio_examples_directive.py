"""A standalone Sphinx build renders blocks in the app's form."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest
from sphinx.application import Sphinx

from ol.blocks import Example
from ol.docs.page_examples import PageExamples

WRITER = """# Weil

:::{audio-examples}
:track: a2/grammar/weil
:title: Nebensatz mit weil

Ich bleibe zu Hause, weil ich <krank> bin.
: I am staying at home because I am ill.
:::
"""

DUPLICATE = """# Denn

:::{audio-examples}
:track: a2/grammar/weil
:duplicate:
:::
"""


class Build:
    def __init__(self, root: Path, pages: dict[str, str]):
        self.root = root
        self.src = root / "src"
        self.src.mkdir()
        (self.src / "conf.py").write_text(
            'extensions = ["myst_parser", "ol.docs.audio_examples"]\n'
            'myst_enable_extensions = ["colon_fence"]\n'
        )
        toctree = "\n".join(pages)
        (self.src / "index.md").write_text(
            f"# Index\n\n```{{toctree}}\n{toctree}\n```\n"
        )
        self.out = root / "out"
        self.run(pages, fresh=True)

    def run(self, pages: dict[str, str], fresh: bool = False) -> None:
        for name, text in pages.items():
            page = self.src / f"{name}.md"
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(text, encoding="utf-8")
        self.warnings = StringIO()
        Sphinx(
            str(self.src),
            str(self.src),
            str(self.out),
            str(self.root / "doctrees"),
            "html",
            status=None,
            warning=self.warnings,
            freshenv=fresh,
        ).build()

    def html(self, name: str) -> str:
        return (self.out / f"{name}.html").read_text(encoding="utf-8")


@pytest.fixture
def build(tmp_path):
    return lambda pages: Build(tmp_path, pages)


PLAIN = """# Hafen

:::{div} ol-examples
{mark}`Der` Hafen ist **groß**.
: The harbour is big.

Die Brücke heißt "Alsterbrücke".
: The bridge is called "Alsterbrücke".

    A second paragraph of the translation.
:::

:::{div} other
Nicht hier.
: Not here.
:::

:::{div} ol-examples
Der Satz.
: The sentence.
: Another translation.
:::

:::{div} ol-examples
Ein Absatz, kein Beispiel.
:::

:::{div} ol-examples
Noch ein Satz.
: One more sentence.
:::
"""


class TestPageExamples:
    def read(self, tmp_path: Path) -> list[Example]:
        src = tmp_path / "src"
        src.mkdir()
        (src / "conf.py").write_text(
            'extensions = ["myst_parser", "sphinx_design", "ol.docs.roles"]\n'
            'myst_enable_extensions = ["colon_fence", "deflist"]\n'
            'custom_roles = ["mark"]\n'
            "suppress_warnings = ['toc.not_readable']\n"
        )
        (src / "index.md").write_text(PLAIN, encoding="utf-8")
        app = Sphinx(
            str(src),
            str(src),
            str(tmp_path / "out"),
            str(tmp_path / "doctrees"),
            "html",
            status=None,
            warning=StringIO(),
        )
        app.build()
        return PageExamples.read(app.env.get_doctree("index"))

    def test_a_page_gives_what_its_blocks_show_with_no_markup(self, tmp_path):
        examples = self.read(tmp_path)
        assert examples[0] == Example("Der Hafen ist groß.", "The harbour is big.")
        assert examples[1].sentence == "Die Brücke heißt “Alsterbrücke”."
        assert examples[1].translation.endswith(
            "\nA second paragraph of the translation."
        )

    def test_a_block_of_anything_but_pairs_gives_nothing(self, tmp_path):
        sentences = [example.sentence for example in self.read(tmp_path)]
        assert sentences[2:] == ["Noch ein Satz."]


class TestAudioExamplesDirective:
    def test_a_block_that_writes_shows_its_examples_escaped(self, build):
        html = build({"a2/grammar/weil": WRITER}).html("a2/grammar/weil")
        assert "weil ich &lt;krank&gt; bin." in html
        assert "I am staying at home because I am ill." in html

    def test_a_duplicate_shows_the_examples_of_the_block_that_writes(self, build):
        done = build({"a2/grammar/weil": WRITER, "a2/grammar/denn": DUPLICATE})
        assert "weil ich &lt;krank&gt; bin." in done.html("a2/grammar/denn")
        assert "audio-examples:" not in done.warnings.getvalue()

    def test_a_duplicate_follows_its_track_when_only_the_writer_changes(self, build):
        done = build({"a2/grammar/weil": WRITER, "a2/grammar/denn": DUPLICATE})
        done.run({"a2/grammar/weil": WRITER.replace("krank", "müde")})
        assert "weil ich &lt;müde&gt; bin." in done.html("a2/grammar/denn")

    def test_a_duplicate_of_a_track_nobody_writes_warns(self, build):
        done = build({"a2/grammar/denn": DUPLICATE})
        assert "orphan_duplicate" in done.warnings.getvalue()

    def test_a_track_written_on_two_pages_warns(self, build):
        done = build({"a2/grammar/weil": WRITER, "a2/grammar/denn": WRITER})
        assert done.warnings.getvalue().count("written_twice") == 2

    def test_a_refused_block_warns_with_its_code(self, build):
        page = WRITER.replace(":title: Nebensatz mit weil\n", ":duplicate:\n")
        done = build({"a2/grammar/weil": page})
        assert "duplicate_writes" in done.warnings.getvalue()

    def test_a_block_that_cannot_be_read_warns(self, build):
        page = WRITER.replace("Ich bleibe", ": Ich bleibe")
        done = build({"a2/grammar/weil": page})
        assert "a2/grammar/weil" in done.warnings.getvalue()
