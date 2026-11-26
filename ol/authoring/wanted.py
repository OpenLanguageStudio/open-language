"""Wanted pages: links in a page's text to articles that do not exist yet.

A writer links to the article a sentence needs, at the point where the reader
needs it, whether or not that article has been written. A link to a page that
does not exist fails nothing. The build draws its text as plain text, and
``ol wanted`` lists every missing page with the pages that link to it, so a
reviewer can decide which to write. ``related:`` in the front matter is not
text, and an entry there that names no page still stops the build.

A link names a page when its path, before any ``#``, ends in ``.md``, or has no
file suffix and holds a ``/``: ``[](/a1/grammar/cases/dativ.md)``,
``[](choose-between-du-and-sie.md)`` or ``[](/a1/grammar/cases/dativ)``.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from pathlib import Path

from ol.authoring.components import unfenced_lines
from ol.authoring.related import resolve
from ol.workspace import page_path

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
    found = []
    for line_no, line in unfenced_lines(body, offset):
        for m in LINK.finditer(line):
            page = page_link(docname, m[2])
            if page is not None and page != docname and not exists(page):
                found.append((line_no, page))
    return found


def wanted_pages(workspace: Path, files: Iterable[Path]) -> dict[str, list[str]]:
    """Every wanted page, with the pages that link to it.

    Args:
        workspace: The language repository's root.
        files: The pages to read.

    Returns:
        Each missing page's name, in order, mapped to the names of the pages
        that link to it, in order.
    """
    from ol.authoring.validate import split_frontmatter

    def exists(page: str) -> bool:
        return (workspace / f"{page}.md").is_file()

    wanted: dict[str, set[str]] = {}
    for path in files:
        parts = page_path(path, workspace)
        if parts is None:
            continue
        docname = "/".join(parts)
        _fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
        for _line, page in missing_links(body, docname, exists):
            wanted.setdefault(page, set()).add(docname)
    return {page: sorted(wanted[page]) for page in sorted(wanted)}
