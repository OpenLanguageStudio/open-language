"""The site menu every language repository builds the same way.

The menu is the toctree of the root ``index.md`` and of each level index. The
top level holds exactly the standard pages in ``TOP_LEVEL_PAGES``. The root page
is the Introduction: its toctree lists the other standard pages in their order,
then the levels from A1 to B2. Each level lists its categories in the
order concepts, grammar, writing, vocabulary. Nothing else goes in the menu.

The menu belongs to the whole repository, not to one page, so its errors are
never covered by the baseline.
"""

from __future__ import annotations

import re
from pathlib import Path

from ol.workspace import ROOT_EXCLUDES

LEVELS = ("a1", "a2", "b1", "b2")
MENU_CATEGORIES = ("concepts", "grammar", "writing", "vocabulary")
TOP_LEVEL_PAGES = {
    "index": "Introduction",
    "how_to_use": "How to use",
    "terminology": "Terminology",
    "contributing": "Contributing",
}
"""Every top-level page, by name, with its H1, in menu order."""
MENU_PAGES = tuple(name for name in TOP_LEVEL_PAGES if name != "index")

_LEVEL_DIR = re.compile(r"[abc]\d")
_TOCTREE = re.compile(r"```\{toctree\}[^\n]*\n(.*?)```", re.S)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_EXPLICIT_TITLE = re.compile(r".*<([^<>]+)>$")
_EXTERNAL = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)


def toctrees(body: str) -> list[list[str]]:
    """The entries of every toctree in ``body`` that the build reads.

    A toctree inside an HTML comment is not built, so it is not read. An entry
    with an explicit title (``Title <target>``) is read as its target.

    Args:
        body: The page's Markdown.

    Returns:
        One list of entries per toctree, in page order.
    """
    found = []
    for m in _TOCTREE.finditer(_COMMENT.sub("", body)):
        entries = []
        for line in m.group(1).splitlines():
            entry = line.strip()
            if not entry or entry.startswith(":"):
                continue
            if title := _EXPLICIT_TITLE.match(entry):
                entry = title.group(1).strip()
            entries.append(entry)
        found.append(entries)
    return found


def _target(entry: str) -> str:
    """An entry as a page name: no leading slash, no ``.md``."""
    return entry.lstrip("/").removesuffix(".md")


def _orphan(text: str) -> bool:
    m = re.match(r"^﻿?---\s*\n(.*?)\n---\s*\n", text, re.S)
    return bool(m and re.search(r"^orphan:\s*true\s*$", m.group(1), re.M | re.I))


_FENCE = re.compile(r"^(`{3,}|:{3,}).*?^\1\s*$", re.S | re.M)


def _has_prose(body: str) -> bool:
    """Whether a paragraph of prose follows the page's H1."""
    h1 = re.search(r"^# .*$", body, re.M)
    rest = _FENCE.sub("", _COMMENT.sub("", body[h1.end() if h1 else 0 :]))
    return any(
        line.strip() and not line.lstrip().startswith(("#", ":", "|", "<", "`"))
        for line in rest.splitlines()
    )


def _check_top_level_pages(problems: dict[str, list[str]], workspace: Path):
    """Each standard page exists, has its H1 and prose, and nothing else is there."""
    for name, title in TOP_LEVEL_PAGES.items():
        rel = f"{name}.md"
        page = workspace / rel
        errors = problems.setdefault(rel, [])
        if not page.is_file():
            errors.append(
                f"menu: no {rel} at the top level: every Coursebook has the page "
                f"'{title}', start it from `ol templates "
                f"{'introduction' if name == 'index' else name.replace('_', '-')}.md`"
            )
            continue
        body = page.read_text(encoding="utf-8")
        h1 = re.search(r"^# (.+?)\s*$", body, re.M)
        if not h1 or h1.group(1) != title:
            found = f"'{h1.group(1)}'" if h1 else "no H1"
            errors.append(f"menu: the H1 of {rel} is '{title}' (found {found})")
        if not _has_prose(body):
            errors.append(
                f"menu: {rel} has no prose below its H1: write at least one paragraph"
            )
    for page in sorted(workspace.glob("*.md")):
        if page.name in ROOT_EXCLUDES or page.stem in TOP_LEVEL_PAGES:
            continue
        problems.setdefault(page.name, []).append(
            f"menu: {page.name} is not a standard top-level page: the top level "
            f"holds only {', '.join(f'{n}.md' for n in TOP_LEVEL_PAGES)}, move "
            "its content into one of them and remove it"
        )


def _single_toctree(problems: dict[str, list[str]], rel: str, body: str):
    """The entries of a menu page's one toctree, or None without one."""
    trees = toctrees(body)
    if not trees:
        problems.setdefault(rel, []).append(
            "menu: no toctree: this page holds the menu, add one"
        )
        return None
    if len(trees) > 1:
        problems.setdefault(rel, []).append(
            f"menu: {len(trees)} toctrees: keep the menu in the first toctree and "
            "remove the others"
        )
    return trees[0]


def _check_root(problems: dict[str, list[str]], workspace: Path) -> set[str]:
    """Check the root toctree and return the levels it lists."""
    rel = "index.md"
    index = workspace / rel
    errors = problems.setdefault(rel, [])
    if not index.is_file():
        errors.append(
            "menu: no index.md at the top level: the Introduction page holds the menu"
        )
        return set()
    body = index.read_text(encoding="utf-8")
    entries = _single_toctree(problems, rel, body)
    if entries is None:
        return set()

    listed: list[str] = []
    pages: list[str] = []
    seen: set[str] = set()
    first_level: str | None = None
    for entry in entries:
        if _EXTERNAL.match(entry):
            errors.append(f"menu: external link '{entry}' in the menu: remove it")
            continue
        target = _target(entry)
        if target in seen:
            errors.append(f"menu: '{entry}' is listed twice: remove the second one")
            continue
        seen.add(target)
        parts = target.split("/")
        if len(parts) == 2 and parts[1] == "index" and _LEVEL_DIR.fullmatch(parts[0]):
            level = parts[0]
            if level not in LEVELS:
                errors.append(
                    f"menu: '{entry}' is not a level from A1 to B2: the Coursebook "
                    "has no levels above B2, remove it"
                )
                continue
            if not (workspace / level / "index.md").is_file():
                errors.append(f"menu: '{entry}' has no page {target}.md: remove it")
                continue
            if listed and LEVELS.index(level) < LEVELS.index(listed[-1]):
                errors.append(
                    f"menu: '{entry}' comes after '{listed[-1]}/index': list the "
                    "levels in order from A1 to B2"
                )
            listed.append(level)
            first_level = first_level or entry
        elif len(parts) == 1 and target in MENU_PAGES:
            pages.append(target)
            if first_level:
                errors.append(
                    f"menu: top-level page '{entry}' comes after '{first_level}': "
                    "move it above the first level"
                )
        elif len(parts) == 1:
            errors.append(
                f"menu: '{entry}' is not a standard top-level page: the menu "
                f"lists only {', '.join(MENU_PAGES)} and the levels, remove it"
            )
        else:
            errors.append(
                f"menu: '{entry}' is not a top-level page or a level index: the "
                "menu lists only those, remove it"
            )
    for name in MENU_PAGES:
        if name not in pages:
            errors.append(
                f"menu: '{name}' is missing from the toctree: list it above the levels"
            )
    present = [name for name in MENU_PAGES if name in pages]
    if pages != present:
        errors.append(
            f"menu: list the top-level pages in the order {', '.join(MENU_PAGES)}"
        )
    return set(listed)


def _check_level(problems: dict[str, list[str]], workspace: Path, level: str):
    """Check one level index's toctree and its category directories."""
    directory = workspace / level
    rel = f"{level}/index.md"
    errors = problems.setdefault(rel, [])
    for d in sorted(p for p in directory.iterdir() if p.is_dir()):
        if d.name.startswith((".", "_")) or d.name in MENU_CATEGORIES:
            continue
        errors.append(
            f"menu: category directory {level}/{d.name}/ is not one of "
            f"{', '.join(MENU_CATEGORIES)}: move its articles into one of them "
            "and remove it"
        )
    index = directory / "index.md"
    if not index.is_file():
        return
    entries = _single_toctree(problems, rel, index.read_text(encoding="utf-8"))
    if entries is None:
        return
    allowed = [f"{c}/index" for c in MENU_CATEGORIES]
    previous: str | None = None
    seen: set[str] = set()
    for entry in entries:
        target = _target(entry)
        if target not in allowed:
            errors.append(
                f"menu: '{entry}' is not a category index: a level lists only "
                f"{', '.join(allowed)}, remove it"
            )
            continue
        if target in seen:
            errors.append(f"menu: '{entry}' is listed twice: remove the second one")
            continue
        seen.add(target)
        if previous and allowed.index(target) < allowed.index(previous):
            errors.append(
                f"menu: '{entry}' comes after '{previous}': list the categories "
                f"in the order {', '.join(MENU_CATEGORIES)}"
            )
        previous = target


def check_menu(workspace: Path) -> dict[str, list[str]]:
    """Check the site menu of a language repository.

    Args:
        workspace: The language repository's root.

    Returns:
        The errors, by file or directory relative to the workspace. A file
        without errors is left out.
    """
    problems: dict[str, list[str]] = {}
    _check_top_level_pages(problems, workspace)
    listed = _check_root(problems, workspace)
    for d in sorted(p for p in workspace.iterdir() if p.is_dir()):
        if not _LEVEL_DIR.fullmatch(d.name):
            continue
        if d.name not in LEVELS:
            problems.setdefault(f"{d.name}/", []).append(
                f"menu: {d.name}/ is not a level from A1 to B2: the Coursebook "
                "has no levels above B2, remove the directory"
            )
            continue
        rel = f"{d.name}/index.md"
        index = d / "index.md"
        if not index.is_file():
            problems.setdefault(rel, []).append(
                f"menu: {d.name}/ has no index.md: add the level index"
            )
        else:
            if _orphan(index.read_text(encoding="utf-8")):
                problems.setdefault(rel, []).append(
                    "menu: marked 'orphan: true': remove it and list "
                    f"{d.name}/index in the top-level index.md toctree"
                )
            if d.name not in listed:
                problems.setdefault(rel, []).append(
                    f"menu: {d.name}/index is not in the top-level index.md "
                    "toctree: list it there, in order from A1 to B2"
                )
        _check_level(problems, workspace, d.name)
    return {rel: errors for rel, errors in problems.items() if errors}
