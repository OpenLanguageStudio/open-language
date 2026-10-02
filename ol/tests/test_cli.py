"""The baseline contract of ``ol validate``: known failures pass, new ones fail."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

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


def test_check_skips_the_audit_without_an_albums_directory(tmp_path):
    workspace = _workspace(tmp_path)
    result = runner.invoke(
        app, ["check", "--workspace", str(workspace), "--skip-build"]
    )
    assert "== ol audit" not in result.output
