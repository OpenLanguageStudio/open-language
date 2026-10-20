"""A workspace's pages sit under docs/ when docs/conf.py exists, else at its top."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from ol.authoring.validate import validate_file
from ol.cli import _build_paths, app
from ol.language import Language
from ol.workspace import source_dir

runner = CliRunner()

DUPLICATE = "# Page\n\n:::{audio-examples}\n:track: a1/grammar/dativ\n:duplicate:\n:::\n"

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


def test_the_source_is_docs_when_it_holds_conf_py(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/conf.py").write_text("")
    assert source_dir(tmp_path) == tmp_path / "docs"


def test_the_source_is_the_workspace_without_docs_conf_py(tmp_path):
    (tmp_path / "conf.py").write_text("")
    (tmp_path / "docs").mkdir()
    assert source_dir(tmp_path) == tmp_path


def test_the_build_reads_the_source_and_writes_below_it(tmp_path, src):
    expected = ("docs", "docs/_build/html") if src.name == "docs" else (".", "_build/html")
    assert tuple(Path(p).as_posix() for p in _build_paths(tmp_path)) == expected


def test_check_builds_the_source(tmp_path, src, monkeypatch):
    (tmp_path / "open-language.yml").write_text("language: German\nlanguage_code: de\n")
    (src / "a1").mkdir()
    calls = []

    class Done:
        returncode = 0

    def run(cmd, cwd):
        calls.append(cmd)
        return Done()

    monkeypatch.setattr("ol.cli.subprocess.run", run)
    result = runner.invoke(app, ["check", "--workspace", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert [Path(p).as_posix() for p in calls[0][-2:]] == list(
        Path(p).as_posix() for p in _build_paths(tmp_path)
    )


def test_pages_outside_the_content_are_not_read_at_the_top(tmp_path):
    (tmp_path / "conf.py").write_text("")
    (tmp_path / "open-language.yml").write_text("language: German\nlanguage_code: de\n")
    (tmp_path / "a1").mkdir()
    for name in ("README.md", "AGENTS.md", ".venv/x.md", ".github/x.md", "_build/x.md"):
        (tmp_path / name).parent.mkdir(exist_ok=True)
        (tmp_path / name).write_text(DUPLICATE)

    result = runner.invoke(app, ["validate", "--workspace", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert "orphan_duplicate" not in result.output


def test_a_page_at_the_top_is_validated_without_a_workspace(tmp_path):
    (tmp_path / "conf.py").write_text("")
    (tmp_path / "open-language.yml").write_text("language: German\nlanguage_code: de\n")
    page = tmp_path / "a1/grammar/dativ.md"
    page.parent.mkdir(parents=True)
    page.write_text("# Dativ\n\n" + "No frontmatter here. " * 20)

    messages = [msg for _lvl, msg in validate_file(page).items]

    assert "missing YAML frontmatter (--- block)" in messages
    assert not any("cannot infer content type" in msg for msg in messages)


def test_the_level_index_may_name_its_level(tmp_path, src):
    (src / "a1/grammar").mkdir(parents=True)
    (src / "a1/grammar/index.md").write_text(LEVEL_INDEX.replace("grammar/index\n", ""))
    level = src / "a1/index.md"
    level.write_text(LEVEL_INDEX)
    category = src / "a1/grammar/index.md"

    level_errors = [m for lvl, m in validate_file(level, tmp_path).items if lvl == "ERROR"]
    category_errors = [
        m for lvl, m in validate_file(category, tmp_path).items if lvl == "ERROR"
    ]

    assert not any("contains the CEFR level" in m for m in level_errors), level_errors
    assert any("contains the CEFR level" in m for m in category_errors), category_errors


def test_the_language_reads_its_pages_from_the_source(tmp_path, src, monkeypatch):
    (tmp_path / "open-language.yml").write_text("language: German\nlanguage_code: de\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPEN_LANGUAGE_DOCS", raising=False)
    monkeypatch.delenv("OPEN_LANGUAGE_CONFIG", raising=False)

    assert Language().docs_root.resolve() == src.resolve()
