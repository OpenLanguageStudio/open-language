"""Where a language workspace keeps its pages.

A language repository keeps its pages at its top level, with ``conf.py`` next to
``open-language.yml``. The workspace root is the source Sphinx builds, and every
path to a page (its name, its level and category, a site-root link) is read
from there.
"""

from __future__ import annotations

from pathlib import Path

CONFIG_FILE = "open-language.yml"

ROOT_EXCLUDES = frozenset({"_build", ".venv", ".github", "README.md", "AGENTS.md"})
"""Files and folders at the top of a workspace that are never pages."""


def find_workspace(path: Path) -> Path | None:
    """Return the workspace a page belongs to.

    Args:
        path: A file in the workspace.

    Returns:
        The nearest folder above ``path`` that holds ``open-language.yml``, or
        None.
    """
    for parent in path.resolve().parents:
        if (parent / CONFIG_FILE).is_file():
            return parent
    return None


def page_path(path: Path, workspace: Path) -> tuple[str, ...] | None:
    """Return a page's path below the workspace, without ``.md``.

    Args:
        path: The page's file.
        workspace: The language repository's root.

    Returns:
        The parts of the path, or None when the file is outside the workspace.
    """
    try:
        relative = path.resolve().relative_to(workspace.resolve())
    except ValueError:
        return None
    return relative.with_suffix("").parts
