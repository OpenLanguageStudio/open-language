"""The render check opens pages in a real browser and measures them."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from ol.authoring import render
from ol.authoring.render import RenderUnavailable, overflowing_pages, sample_pages
from ol.cli import app

runner = CliRunner()

FITS = "<!doctype html><title>Fits</title><p>A short line.</p>"
WIDE = '<!doctype html><title>Wide</title><div style="width:900px">Wide.</div>'
SCROLLING_ARTICLE = (
    '<!doctype html><title>Article</title><div style="overflow-x:auto">'
    '<div style="width:900px">An article in a box of its own.</div></div>'
)
TABLE = (
    '<!doctype html><title>Table</title><div style="overflow-x:auto"'
    ' class="pst-scrollable-table-container"><table style="width:900px"><tr>'
    "<td>A table in a box of its own.</td></tr></table></div>"
)


def site(root, **pages):
    root.mkdir(parents=True, exist_ok=True)
    for name, html in pages.items():
        (root / f"{name}.html").write_text(html, encoding="utf-8")
    return root


def test_only_the_page_that_scrolls_sideways_is_reported(tmp_path):
    root = site(
        tmp_path / "html",
        fits=FITS,
        wide=WIDE,
        table=TABLE,
        article=SCROLLING_ARTICLE,
    )
    found = overflowing_pages(root, ["fits.md", "wide.md", "table.md", "article.md"])
    assert found == ["wide.md", "article.md"]


def test_a_page_within_the_limit_passes_at_the_limit(tmp_path):
    root = site(tmp_path / "html", exact=WIDE.replace("900px", "300px"))
    assert overflowing_pages(root, ["exact.md"]) == []


def test_the_sample_holds_every_index_and_the_first_articles(tmp_path, write_menu):
    root = write_menu(tmp_path)
    for name in ("a", "b", "c"):
        (root / f"a1/writing/{name}.md").write_text("# Page\n", encoding="utf-8")
    sample = sample_pages(root)
    assert "index.md" in sample
    assert "terminology.md" in sample
    assert "a1/index.md" in sample
    assert "a1/grammar/index.md" in sample
    assert "a1/writing/a.md" in sample
    assert "a1/writing/b.md" in sample
    assert "a1/writing/c.md" not in sample


def built(root, write_menu, overflowing):
    write_menu(root)
    (root / "open-language.yml").write_text("language: German\nlanguage_code: de\n")
    (root / "_build/html/a1").mkdir(parents=True)
    return lambda *_: overflowing


@pytest.fixture
def check(tmp_path, write_menu, monkeypatch):
    def run(overflowing, baseline=""):
        monkeypatch.setattr(
            "ol.cli.subprocess.run",
            lambda *a, **k: type("Done", (), {"returncode": 0})(),
        )
        monkeypatch.setattr(
            render, "overflowing_pages", built(tmp_path, write_menu, overflowing)
        )
        (tmp_path / ".ol-validate-baseline").write_text(baseline)
        return runner.invoke(app, ["check", "--workspace", str(tmp_path)])

    return run


def test_check_fails_on_a_page_that_scrolls_sideways(check):
    result = check(["a1/index.md"])
    assert result.exit_code == 1, result.output
    assert "a1/index.md" in result.output
    assert "render check" in result.output


def test_a_baseline_page_may_scroll_sideways(check):
    result = check(["a1/index.md"], "a1/index.md\n")
    assert result.exit_code == 0, result.output


def test_check_fails_when_no_browser_can_be_opened(tmp_path, write_menu, monkeypatch):
    write_menu(tmp_path)
    (tmp_path / "open-language.yml").write_text("language: German\nlanguage_code: de\n")
    monkeypatch.setattr(
        "ol.cli.subprocess.run", lambda *a, **k: type("Done", (), {"returncode": 0})()
    )

    def unavailable(*_):
        raise RenderUnavailable("no browser for the render check")

    monkeypatch.setattr(render, "overflowing_pages", unavailable)
    result = runner.invoke(app, ["check", "--workspace", str(tmp_path)])
    assert result.exit_code == 1, result.output
    assert "no browser" in result.output
