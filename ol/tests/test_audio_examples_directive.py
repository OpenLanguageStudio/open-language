"""A standalone Sphinx build renders blocks in the app's form."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest
from sphinx.application import Sphinx

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
