"""Wanted pages: links in a page's text to articles that do not exist yet.

A writer links to the article a sentence needs, at the point where the reader
needs it, whether or not that article has been written. A link to a page that
does not exist fails nothing. The build draws its text as plain text, and
``ol wanted`` lists every missing page with the pages that link to it, so a
reviewer can decide which to write. ``related:`` in the front matter is not
text, and an entry there that names no page still stops the build.

A link names a page when its path, before any ``#``, ends in ``.md``, or has no
file suffix and holds a ``/``: ``[the dative](/a1/grammar/cases/dativ.md)``,
``[du or Sie](choose-between-du-and-sie.md)`` or
``[the dative](/a1/grammar/cases/dativ)``.

The source never changes: the link is drawn as plain text until its page
exists, and the next build after that draws a live link with no edit to the
linking page. So a link carries its own text, and a link with none to a page
not written yet is an error, as is a missing page that looks like a typo for
one that exists (see ``near_page``).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from pathlib import Path

from ol.authoring.components import unfenced_lines
from ol.authoring.related import resolve
from ol.workspace import ROOT_EXCLUDES, page_path

LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)\)")
_EXTERNAL = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)


def page_link(docname: str, target: str) -> str | None:
    """The page a link names, or None when it names no page.

    Args:
        docname: The page that holds the link, such as ``a1/how-to/greet``.
        target: The link's target as written.

    Returns:
        The target's page name, such as ``a1/grammar/cases/dativ``.
    """
    if _EXTERNAL.match(target) or target.startswith("#"):
        return None
    path = target.partition("#")[0]
    if path.endswith(".md"):
        path = path[: -len(".md")]
    elif "/" not in path or "." in path.rsplit("/", 1)[-1] or path.endswith("/"):
        return None
    return resolve(docname, path) if path else None


def words_of(page: str) -> str:
    """The text a wanted page's link shows when it has none of its own.

    Args:
        page: The page name, such as ``a1/grammar/cases/dativ``.

    Returns:
        The last part of the name as words, such as ``Dativ``.
    """
    words = page.rsplit("/", 1)[-1].replace("-", " ").replace("_", " ").strip()
    return words[:1].upper() + words[1:]


def page_links(body: str, docname: str, offset: int = 0) -> list[tuple[int, str, str]]:
    """The links in a page's text that name a page.

    Code blocks and inline code are not text.

    Args:
        body: The page's Markdown, without its front matter.
        docname: The page's name.
        offset: Lines above ``body`` in the file.

    Returns:
        Each link's line, its text and the page it names, in page order.
    """
    found = []
    for line_no, line in unfenced_lines(body, offset):
        for m in LINK.finditer(line):
            page = page_link(docname, m[2])
            if page is not None and page != docname:
                found.append((line_no, m[1], page))
    return found


def edit_distance(a: str, b: str) -> int:
    """How many letters to add, remove or change to turn one word into the other."""
    previous = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        current = [i]
        for j, y in enumerate(b, 1):
            current.append(
                min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (x != y))
            )
        previous = current
    return previous[-1]


def near_page(page: str, pages: Iterable[str]) -> str | None:
    """The existing page a missing page's name looks like a typo for.

    A page in the same directory whose file name is a small edit away (one
    letter for a name of five letters or fewer, two for a longer one), or a
    page of the same file name in another directory. ``index`` pages share
    their file name and are matched by directory only.

    Args:
        page: The missing page's name, such as ``a1/grammar/akusativ``.
        pages: The names of the pages that exist.

    Returns:
        The closest existing page, or None when none is close.
    """
    folder, _, name = page.rpartition("/")
    allowed = 1 if len(name) <= 5 else 2
    best: tuple[int, str] | None = None
    elsewhere = []
    for other in pages:
        other_folder, _, other_name = other.rpartition("/")
        if other_folder == folder:
            distance = edit_distance(name, other_name)
            if 0 < distance <= allowed and (best is None or (distance, other) < best):
                best = (distance, other)
        elif other_name == name and name != "index":
            elsewhere.append(other)
    if best:
        return best[1]
    return min(elsewhere) if elsewhere else None


def workspace_pages(workspace: Path) -> set[str]:
    """The names of every page in a language repository."""
    names = set()
    for path in workspace.rglob("*.md"):
        parts = page_path(path, workspace)
        if (
            parts
            and parts[0] not in ROOT_EXCLUDES
            and not any(part.startswith((".", "_")) for part in parts)
        ):
            names.add("/".join(parts))
    return names


def missing_links(
    body: str, docname: str, exists: Callable[[str], bool], offset: int = 0
) -> list[tuple[int, str]]:
    """The links in a page's text to pages that do not exist.

    Code blocks and inline code are not text.

    Args:
        body: The page's Markdown, without its front matter.
        docname: The page's name.
        exists: Whether a page name is a page.
        offset: Lines above ``body`` in the file.

    Returns:
        Each link's line and the page it names, in page order.
    """
    return [
        (line, page)
        for line, _text, page in page_links(body, docname, offset)
        if not exists(page)
    ]


def wanted_pages(workspace: Path, files: Iterable[Path]) -> dict[str, list[str]]:
    """Every wanted page, with the pages that link to it.

    A missing page that looks like a typo for one that exists is a broken
    link, not a wanted page, and is left out.

    Args:
        workspace: The language repository's root.
        files: The pages to read.

    Returns:
        Each missing page's name, in order, mapped to the names of the pages
        that link to it, in order.
    """
    from ol.authoring.validate import split_frontmatter

    pages = workspace_pages(workspace)

    def exists(page: str) -> bool:
        return page in pages

    wanted: dict[str, set[str]] = {}
    for path in files:
        parts = page_path(path, workspace)
        if parts is None:
            continue
        docname = "/".join(parts)
        _fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
        for _line, page in missing_links(body, docname, exists):
            if near_page(page, pages) is None:
                wanted.setdefault(page, set()).add(docname)
    return {page: sorted(wanted[page]) for page in sorted(wanted)}
