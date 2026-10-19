"""The baseline contract of ``ol validate``: known failures pass, new ones fail."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ol.blocks import Refusal, load_samples
from ol.cli import app

runner = CliRunner()

GOOD_INDEX = """---
myst:
  html_meta:
    description: Grammar at A1.
---
# Grammar

Grammar articles.

```{toctree}
```
"""


def _workspace(tmp_path: Path) -> Path:
    (tmp_path / "open-language.yml").write_text("language: German\nlanguage_code: de\n")
    grammar = tmp_path / "docs/a1/grammar"
    grammar.mkdir(parents=True)
    (grammar / "broken.md").write_text("# Broken\n\n" + "No frontmatter here. " * 20)
    return tmp_path


def test_new_failure_fails_the_run(tmp_path):
    ws = _workspace(tmp_path)
    result = runner.invoke(app, ["validate", "--workspace", str(ws)])
    assert result.exit_code == 1, result.output
    assert "docs/a1/grammar/broken.md" in result.output


def test_baselined_failure_passes_the_run(tmp_path):
    ws = _workspace(tmp_path)
    written = runner.invoke(
        app, ["validate", "--workspace", str(ws), "--write-baseline"]
    )
    assert written.exit_code == 0, written.output
    assert "docs/a1/grammar/broken.md" in (ws / ".ol-validate-baseline").read_text()

    result = runner.invoke(app, ["validate", "--workspace", str(ws)])
    assert result.exit_code == 0, result.output


def test_fixed_baseline_entry_is_reported(tmp_path):
    ws = _workspace(tmp_path)
    (ws / ".ol-validate-baseline").write_text("docs/a1/grammar/broken.md\n")
    # A short placeholder page is reported as a stub, not a failure.
    (ws / "docs/a1/grammar/broken.md").write_text("# Broken\n")
    result = runner.invoke(app, ["validate", "--workspace", str(ws)])
    assert result.exit_code == 0, result.output
    assert "remove from baseline: docs/a1/grammar/broken.md" in result.output


def test_templates_lists_the_article_templates():
    result = runner.invoke(app, ["templates"])
    assert result.exit_code == 0
    assert "grammar-article.md" in result.output


def duplicate_page(workspace: Path, name: str) -> None:
    page = workspace / f"docs/a1/grammar/{name}.md"
    page.write_text(
        "# Page\n\n:::{audio-examples}\n:track: a1/grammar/dativ\n:duplicate:\n:::\n"
    )


def test_a_refusal_across_pages_fails_the_run(tmp_path):
    workspace = _workspace(tmp_path)
    (workspace / ".ol-validate-baseline").write_text("docs/a1/grammar/broken.md\n")
    duplicate_page(workspace, "praepositionen")

    result = runner.invoke(app, ["validate", "--workspace", str(workspace), "-v"])

    assert result.exit_code == 1, result.output
    assert "orphan_duplicate" in result.output


def test_a_refusal_across_pages_is_found_when_checking_one_file(tmp_path):
    workspace = _workspace(tmp_path)
    duplicate_page(workspace, "praepositionen")
    page = workspace / "docs/a1/grammar/praepositionen.md"

    result = runner.invoke(
        app, ["validate", str(page), "--workspace", str(workspace), "-v"]
    )

    assert "orphan_duplicate" in result.output


def test_a_track_written_on_another_page_is_found(tmp_path):
    workspace = _workspace(tmp_path)
    (workspace / ".ol-validate-baseline").write_text(
        "docs/a1/grammar/broken.md\ndocs/a1/grammar/praepositionen.md\n"
        "docs/a1/grammar/dativ.md\n"
    )
    duplicate_page(workspace, "praepositionen")
    (workspace / "docs/a1/grammar/dativ.md").write_text(
        "# Dativ\n\n:::{audio-examples}\n:track: a1/grammar/dativ\n:title: Dativ\n\n"
        "Ich fahre mit dem Bus.\n: I go by bus.\n:::\n"
    )

    result = runner.invoke(app, ["validate", "--workspace", str(workspace), "-v"])

    assert "orphan_duplicate" not in result.output


def test_a_block_that_cannot_be_read_fails_the_run_and_nothing_else(tmp_path):
    workspace = _workspace(tmp_path)
    (workspace / ".ol-validate-baseline").write_text("docs/a1/grammar/broken.md\n")
    (workspace / "docs/a1/grammar/dativ.md").write_text(
        "# Dativ\n\n:::{audio-examples}\n:track: a1/grammar/dativ\n\n: No sentence.\n:::\n"
        + "Filler prose for the page. " * 10
    )

    result = runner.invoke(app, ["validate", "--workspace", str(workspace)])

    assert result.exit_code == 1, result.output
    assert "docs/a1/grammar/dativ.md" in result.output


@pytest.mark.parametrize("sample", load_samples(), ids=lambda s: s.name)
def test_validate_gives_each_sample_its_outcome(tmp_path, sample):
    (tmp_path / "open-language.yml").write_text("language: German\nlanguage_code: de\n")
    for page, text in sample.pages.items():
        path = tmp_path / "docs" / f"{page}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    result = runner.invoke(app, ["validate", "--workspace", str(tmp_path)])

    found = {code for code in Refusal.CODES if code in result.output}
    assert found == (set() if sample.expect == "accepted" else {sample.expect})
