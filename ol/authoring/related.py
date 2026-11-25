"""The related articles an article lists in its front matter.

An article names the pages a reader may want next under ``related:``::

    related: [/a1/grammar/verbs/sein-und-haben, choose-between-du-and-sie]

Each entry is a page path without ``.md``, relative to the page's folder or,
with a leading ``/``, from the root of the language repository. The build draws
the list as the last section of the page, grouped by kind of page.
"""

from __future__ import annotations

import posixpath
from pathlib import Path

KEY = "related"


def resolve(docname: str, entry: str) -> str:
    """The page name an entry points at.

    Args:
        docname: The page that holds the entry, such as ``a1/how-to/greet``.
        entry: The entry as written.

    Returns:
        The target's page name, such as ``a1/grammar/verbs/sein-und-haben``.
    """
    if entry.startswith("/"):
        return posixpath.normpath(entry[1:])
    return posixpath.normpath(posixpath.join(posixpath.dirname(docname), entry))


def problem(value) -> str | None:
    """Why a ``related:`` value is not a list of page paths, or None when it is."""
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        return (
            "front matter 'related:' is a list of page paths, such as /a1/how-to/greet"
        )
    return None


def entries(fm: dict | None) -> list[str]:
    """The entries of a page's ``related:`` list, or nothing when it is not sound."""
    if not fm or KEY not in fm or problem(fm[KEY]):
        return []
    return [item.strip() for item in fm[KEY]]


def check_entries(rep, fm: dict | None, docname: str, workspace: Path | None):
    """Each entry is a page path, without ``.md``, naming another page that exists.

    Args:
        rep: The page's report.
        fm: The page's front matter.
        docname: The page's name.
        workspace: The language repository's root.
    """
    if not fm or KEY not in fm:
        return
    if why := problem(fm[KEY]):
        rep.error(why)
        return
    for entry in entries(fm):
        if entry.endswith(".md"):
            rep.error(
                f"front matter 'related:' entry '{entry}' ends in .md: write the "
                "page path without it"
            )
            continue
        target = resolve(docname, entry)
        if target == docname:
            rep.error(f"front matter 'related:' entry '{entry}' is the page itself")
        elif workspace and not (workspace / f"{target}.md").is_file():
            rep.error(
                f"front matter 'related:' entry '{entry}' names no page "
                f"({target}.md does not exist)"
            )
