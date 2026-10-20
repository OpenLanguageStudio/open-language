"""Every menu rule must go red on a deliberately broken language repository.

The good menu is the Introduction page listing the other top-level pages, then
every level from A1 to B2, each listing its categories in order. Each case
breaks exactly one thing and asserts the error it should raise.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ol.authoring.menu import check_menu, toctrees
from ol.authoring.validate import validate_file
from ol.cli import app

runner = CliRunner()

TOP_LEVEL = ("how_to_use", "terminology", "contributing")


def toctree(*entries: str) -> str:
    return (
        "```{toctree}\n:maxdepth: 2\n:hidden:\n\n"
        + "".join(f"{e}\n" for e in entries)
        + "```\n"
    )


def root_index(*entries: str, h1: str = "Introduction") -> str:
    return f"---\ntitle: Home\n---\n# {h1}\n\n" + toctree(*entries)


def level_index(level: str, *entries: str, orphan: bool = False) -> str:
    frontmatter = "---\norphan: true\n---\n" if orphan else ""
    return f"{frontmatter}# {level.upper()}\n\n" + toctree(*entries)


GOOD_ROOT_ENTRIES = (*TOP_LEVEL, "a1/index", "a2/index", "b1/index", "b2/index")
GOOD_ROOT = root_index(*GOOD_ROOT_ENTRIES)
GOOD_LEVEL = ("concepts/index", "grammar/index", "writing/index", "vocabulary/index")


def menu_repository(tmp_path: Path) -> Path:
    (tmp_path / "open-language.yml").write_text("language: German\nlanguage_code: de\n")
    (tmp_path / "index.md").write_text(GOOD_ROOT)
    for page in TOP_LEVEL:
        (tmp_path / f"{page}.md").write_text(f"# {page}\n")
    for level in ("a1", "a2", "b1", "b2"):
        for category in ("concepts", "grammar", "writing", "vocabulary"):
            (tmp_path / level / category).mkdir(parents=True)
            (tmp_path / level / category / "index.md").write_text("# Category\n")
        (tmp_path / level / "index.md").write_text(level_index(level, *GOOD_LEVEL))
    return tmp_path


def menu_errors(repository: Path) -> dict[str, list[str]]:
    return check_menu(repository)


def test_good_menu_passes(tmp_path):
    assert menu_errors(menu_repository(tmp_path)) == {}


def test_a_level_may_leave_a_category_out(tmp_path):
    repo = menu_repository(tmp_path)
    (repo / "a2/index.md").write_text(
        level_index("a2", "concepts/index", "grammar/index")
    )
    assert menu_errors(repo) == {}


def test_top_level_pages_take_any_order_and_explicit_titles(tmp_path):
    repo = menu_repository(tmp_path)
    (repo / "index.md").write_text(
        root_index(
            "contributing",
            "How to use <how_to_use>",
            "/terminology",
            "a1/index",
            "a2/index",
            "b1/index",
            "b2/index",
        )
    )
    assert menu_errors(repo) == {}


def test_a_commented_out_toctree_is_not_read():
    body = (
        "# Introduction\n\n"
        + toctree("a1/index")
        + "<!--\n"
        + toctree("b1/x")
        + "-->\n"
    )
    assert toctrees(body) == [["a1/index"]]


def write(repo: Path, rel: str, text: str) -> None:
    (repo / rel).write_text(text)


CASES = {
    # 1. The root page is the Introduction, then top-level pages, then levels.
    "root page is not the Introduction": (
        lambda r: write(r, "index.md", GOOD_ROOT.replace("# Introduction", "# Home")),
        "index.md",
        "its H1 is 'Introduction' (found 'Home')",
    ),
    "top-level page after a level": (
        lambda r: write(
            r,
            "index.md",
            root_index(
                "how_to_use",
                "a1/index",
                "a2/index",
                "b1/index",
                "b2/index",
                "contributing",
                "terminology",
            ),
        ),
        "index.md",
        "top-level page 'contributing' comes after 'a1/index': move it above the first level",
    ),
    "top-level page that does not exist": (
        lambda r: write(r, "index.md", root_index("missing", *GOOD_ROOT_ENTRIES)),
        "index.md",
        "'missing' has no page missing.md: remove it",
    ),
    "root has no toctree": (
        lambda r: write(r, "index.md", "# Introduction\n\nWelcome.\n"),
        "index.md",
        "no toctree: this page holds the menu, add one",
    ),
    "root has no index.md": (
        lambda r: (r / "index.md").unlink(),
        "index.md",
        "no index.md at the top level",
    ),
    # 2. Levels A1 to B2, in order, all listed, none orphaned.
    "levels out of order": (
        lambda r: write(
            r,
            "index.md",
            root_index(*TOP_LEVEL, "a2/index", "a1/index", "b1/index", "b2/index"),
        ),
        "index.md",
        "'a1/index' comes after 'a2/index': list the levels in order from A1 to B2",
    ),
    "level directory above B2": (
        lambda r: (r / "c1").mkdir(),
        "c1/",
        "c1/ is not a level from A1 to B2",
    ),
    "level above B2 in the menu": (
        lambda r: write(
            r, "index.md", GOOD_ROOT.replace("b2/index\n", "b2/index\nc1/index\n")
        ),
        "index.md",
        "'c1/index' is not a level from A1 to B2",
    ),
    "level not in the menu": (
        lambda r: write(
            r, "index.md", root_index(*TOP_LEVEL, "a1/index", "a2/index", "b1/index")
        ),
        "b2/index.md",
        "b2/index is not in the top-level index.md toctree",
    ),
    "level index marked orphan": (
        lambda r: write(r, "b1/index.md", level_index("b1", *GOOD_LEVEL, orphan=True)),
        "b1/index.md",
        "marked 'orphan: true': remove it",
    ),
    "level directory without an index": (
        lambda r: (r / "b2/index.md").unlink(),
        "b2/index.md",
        "b2/ has no index.md",
    ),
    "level in the menu without a directory": (
        lambda r: shutil.rmtree(r / "b2"),
        "index.md",
        "'b2/index' has no page b2/index.md: remove it",
    ),
    "page listed twice": (
        lambda r: write(r, "index.md", root_index("how_to_use", *GOOD_ROOT_ENTRIES)),
        "index.md",
        "'how_to_use' is listed twice: remove the second one",
    ),
    # 3. Each level lists only its four categories, in order.
    "categories out of order": (
        lambda r: write(
            r, "a1/index.md", level_index("a1", "grammar/index", "concepts/index")
        ),
        "a1/index.md",
        "'concepts/index' comes after 'grammar/index': list the categories in the order concepts, grammar, writing, vocabulary",
    ),
    "another category in a level": (
        lambda r: write(
            r, "b2/index.md", level_index("b2", *GOOD_LEVEL, "topics/index")
        ),
        "b2/index.md",
        "'topics/index' is not a category index",
    ),
    "an overview page in a level": (
        lambda r: write(r, "b1/index.md", level_index("b1", "overview", *GOOD_LEVEL)),
        "b1/index.md",
        "'overview' is not a category index",
    ),
    "another category directory": (
        lambda r: (r / "b2/situations").mkdir(),
        "b2/index.md",
        "category directory b2/situations/ is not one of concepts, grammar, writing, vocabulary",
    ),
    # 4. Nothing else in the menu.
    "external link in the root": (
        lambda r: write(
            r,
            "index.md",
            GOOD_ROOT.replace("b2/index\n", "b2/index\nhttps://example.com\n"),
        ),
        "index.md",
        "external link 'https://example.com' in the menu: remove it",
    ),
    "page below a level in the root": (
        lambda r: write(
            r,
            "index.md",
            GOOD_ROOT.replace("b2/index\n", "b2/index\nb2/grammar/index\n"),
        ),
        "index.md",
        "'b2/grammar/index' is not a top-level page or a level index",
    ),
    "second toctree in the root": (
        lambda r: write(r, "index.md", GOOD_ROOT + "\n" + toctree("b2/grammar/index")),
        "index.md",
        "2 toctrees: keep the menu in the first toctree and remove the others",
    ),
    "second toctree in a level": (
        lambda r: write(
            r, "a1/index.md", level_index("a1", *GOOD_LEVEL) + toctree("concepts/index")
        ),
        "a1/index.md",
        "2 toctrees",
    ),
    "external link in a level": (
        lambda r: write(
            r, "a1/index.md", level_index("a1", *GOOD_LEVEL, "https://example.com")
        ),
        "a1/index.md",
        "'https://example.com' is not a category index",
    ),
}


@pytest.mark.parametrize("case", CASES, ids=list(CASES))
def test_broken_menu_is_red(tmp_path, case):
    breaks, where, expected = CASES[case]
    repo = menu_repository(tmp_path)
    breaks(repo)
    found = menu_errors(repo)
    assert any(expected in msg for msg in found.get(where, [])), found


def test_validate_fails_on_a_menu_error(tmp_path):
    repo = menu_repository(tmp_path)
    write(repo, "b1/index.md", level_index("b1", *GOOD_LEVEL, orphan=True))
    result = runner.invoke(app, ["validate", "--workspace", str(repo)])
    assert result.exit_code == 1, result.output
    assert "[FAIL] b1/index.md" in result.output
    assert "marked 'orphan: true'" in result.output


def test_validate_reports_a_menu_error_on_the_root_index(tmp_path):
    repo = menu_repository(tmp_path)
    write(
        repo,
        "index.md",
        root_index("a1/index", "a2/index", "b1/index", "b2/index", *TOP_LEVEL),
    )
    result = runner.invoke(app, ["validate", "--workspace", str(repo)])
    assert result.exit_code == 1, result.output
    assert "[FAIL] index.md" in result.output


def test_the_baseline_does_not_cover_a_menu_error(tmp_path):
    repo = menu_repository(tmp_path)
    write(repo, "b2/index.md", level_index("b2", *GOOD_LEVEL, "topics/index"))
    (repo / ".ol-validate-baseline").write_text("b2/index.md\n")
    result = runner.invoke(app, ["validate", "--workspace", str(repo)])
    assert result.exit_code == 1, result.output
    assert "'topics/index' is not a category index" in result.output


def test_check_fails_on_a_menu_error(tmp_path):
    repo = menu_repository(tmp_path)
    (repo / "c2").mkdir()
    result = runner.invoke(app, ["check", "--workspace", str(repo), "--skip-build"])
    assert result.exit_code == 1, result.output
    assert "[FAIL] c2/" in result.output


def test_validate_of_named_files_skips_the_menu(tmp_path):
    repo = menu_repository(tmp_path)
    (repo / "c2").mkdir()
    result = runner.invoke(
        app, ["validate", "--workspace", str(repo), str(repo / "a1/index.md")]
    )
    assert "c2/" not in result.output


def test_an_article_outside_the_four_categories_is_told_where_to_go(tmp_path):
    repo = menu_repository(tmp_path)
    (repo / "b2/topics").mkdir()
    article = repo / "b2/topics/smalltalk.md"
    article.write_text("# Smalltalk\n")
    errors = [msg for lvl, msg in validate_file(article, repo).items if lvl == "ERROR"]
    assert errors == [
        "b2/topics/ is not a category: move the article into one of "
        "concepts/, grammar/, writing/, vocabulary/"
    ]
