"""A workspace keeps its pages at its top level, next to conf.py."""

from __future__ import annotations

from typer.testing import CliRunner

from ol.authoring.validate import validate_file
from ol.cli import app
from ol.language import Language

runner = CliRunner()

CONFIG = "language: German\nlanguage_code: de\n"

DUPLICATE = (
    "# Page\n\n:::{audio-examples}\n:track: a1/grammar/dativ\n:duplicate:\n:::\n"
)

LEVEL_INDEX = """---
myst:
  html_meta:
    description: German at A1.
---
# A1 German

The A1 level.

```{toctree}
grammar/index
```
"""


def test_check_builds_the_top_level_into_build_html(tmp_path, monkeypatch):
    (tmp_path / "open-language.yml").write_text(CONFIG)
    (tmp_path / "a1").mkdir()
    calls = []

    class Done:
        returncode = 0

    def run(cmd, cwd):
        calls.append((cmd, cwd))
        return Done()

    monkeypatch.setattr("ol.cli.subprocess.run", run)
    result = runner.invoke(app, ["check", "--workspace", str(tmp_path)])

    assert result.exit_code == 0, result.output
    ((cmd, cwd),) = calls
    assert (cmd[-2:], cwd) == ([".", "_build/html"], tmp_path)


def test_files_at_the_top_that_are_not_pages_are_not_read(tmp_path):
    (tmp_path / "open-language.yml").write_text(CONFIG)
    (tmp_path / "a1").mkdir()
    for name in ("README.md", "AGENTS.md", ".venv/x.md", ".github/x.md", "_build/x.md"):
        (tmp_path / name).parent.mkdir(exist_ok=True)
        (tmp_path / name).write_text(DUPLICATE)

    result = runner.invoke(app, ["validate", "--workspace", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert "orphan_duplicate" not in result.output


def test_a_page_at_the_top_is_found_on_every_page(tmp_path):
    (tmp_path / "open-language.yml").write_text(CONFIG)
    (tmp_path / "a1/grammar").mkdir(parents=True)
    (tmp_path / "a1/grammar/dativ.md").write_text(DUPLICATE)

    result = runner.invoke(app, ["validate", "--workspace", str(tmp_path), "-v"])

    assert "orphan_duplicate" in result.output
    assert "[FAIL] a1/grammar/dativ.md" in result.output


def test_a_page_is_validated_without_a_workspace(tmp_path):
    (tmp_path / "open-language.yml").write_text(CONFIG)
    page = tmp_path / "a1/grammar/dativ.md"
    page.parent.mkdir(parents=True)
    page.write_text("# Dativ\n\n" + "No frontmatter here. " * 20)

    messages = [msg for _lvl, msg in validate_file(page).items]

    assert "missing YAML frontmatter (--- block)" in messages
    assert not any("cannot infer content type" in msg for msg in messages)


def test_only_the_level_index_may_name_its_level(tmp_path):
    (tmp_path / "a1/grammar").mkdir(parents=True)
    level = tmp_path / "a1/index.md"
    level.write_text(LEVEL_INDEX)
    category = tmp_path / "a1/grammar/index.md"
    category.write_text(LEVEL_INDEX.replace("grammar/index\n", ""))

    def errors(path):
        return [m for lvl, m in validate_file(path, tmp_path).items if lvl == "ERROR"]

    assert not any("contains the CEFR level" in m for m in errors(level))
    assert any("contains the CEFR level" in m for m in errors(category))


def test_the_language_reads_its_pages_from_the_top(tmp_path, monkeypatch):
    (tmp_path / "open-language.yml").write_text(CONFIG)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPEN_LANGUAGE_DOCS", raising=False)
    monkeypatch.delenv("OPEN_LANGUAGE_CONFIG", raising=False)

    assert Language().docs_root.resolve() == tmp_path.resolve()
