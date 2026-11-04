"""Every page of a coursebook's HTML build carries the licence of its text."""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import pytest
from sphinx.application import Sphinx

import ol.docs

TEMPLATES = Path(ol.docs.__file__).parent / "_templates"
LICENCE_LINK = 'href="https://creativecommons.org/licenses/by-sa/4.0/"'


@pytest.fixture
def build(tmp_path):
    src = tmp_path / "src"
    (src / "a1").mkdir(parents=True)

    def configure(theme: str) -> None:
        (src / "conf.py").write_text(
            'extensions = ["myst_parser"]\n'
            f"html_theme = {theme!r}\n"
            f"templates_path = [{str(TEMPLATES)!r}]\n"
        )

    (src / "index.md").write_text("# Index\n\n```{toctree}\na1/page\n```\n")
    (src / "a1" / "page.md").write_text("# Page\n\nText.\n")

    def run(builder: str, theme: str = "pydata_sphinx_theme") -> Path:
        configure(theme)
        out = tmp_path / builder
        Sphinx(
            str(src),
            str(src),
            str(out),
            str(tmp_path / "doctrees" / builder),
            builder,
            status=None,
            warning=StringIO(),
            freshenv=True,
        ).build()
        return out

    return run


def test_every_html_page_names_the_licence_once_in_its_footer(build):
    out = build("html")

    for name in ("index", "a1/page"):
        page = (out / f"{name}.html").read_text(encoding="utf-8")
        footer = page[page.index('<footer class="bd-footer">') :]
        assert page.count(LICENCE_LINK) == 1
        assert LICENCE_LINK in footer


def test_the_json_build_leaves_the_licence_to_the_site_that_serves_it(build):
    # The theme the app's JSON build uses: the app draws every page itself.
    out = build("json", theme="basic")

    page = json.loads((out / "a1" / "page.fjson").read_text(encoding="utf-8"))
    assert LICENCE_LINK not in page["body"]
