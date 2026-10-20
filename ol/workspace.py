"""Where a language workspace keeps its pages.

A language repository keeps its pages either in ``docs/``, with ``docs/conf.py``,
or at its top level, with ``conf.py`` next to ``open-language.yml``. The folder
that holds ``conf.py`` is the source Sphinx builds, and every path to a page
(its name, its level and category, a site-root link) is read from there.
"""

from __future__ import annotations

from pathlib import Path

CONFIG_FILE = "open-language.yml"

ROOT_EXCLUDES = frozenset({"_build", ".venv", ".github", "README.md", "AGENTS.md"})
"""Files and folders at the top of a workspace that are never pages."""


def source_dir(workspace: Path) -> Path:
    """Return the folder Sphinx builds for a workspace.

    Args:
        workspace: The language repository's root.

    Returns:
        ``<workspace>/docs`` when it holds ``conf.py``, else ``workspace``.
    """
    docs = workspace / "docs"
    return docs if (docs / "conf.py").is_file() else workspace


def root_excludes(workspace: Path) -> frozenset[str]:
    """Return the top-level names of the source that are never pages.

    Args:
        workspace: The language repository's root.

    Returns:
        ``ROOT_EXCLUDES`` when the source is the workspace root, else nothing.
    """
    return ROOT_EXCLUDES if source_dir(workspace) == workspace else frozenset()


def find_workspace(path: Path) -> Path | None:
    """Return the workspace a page belongs to.

    Args:
        path: A file in the workspace.

    Returns:
        The nearest folder above ``path`` that holds ``open-language.yml``, else
        the folder above a ``docs`` folder on the path, else None.
    """
    resolved = path.resolve()
    for parent in resolved.parents:
        if (parent / CONFIG_FILE).is_file():
            return parent
    parts = resolved.parts
    if "docs" in parts:
        return Path(*parts[: parts.index("docs")])
    return None


def page_path(path: Path, workspace: Path) -> tuple[str, ...] | None:
    """Return a page's path below the workspace's source, without ``.md``.

    Args:
        path: The page's file.
        workspace: The language repository's root.

    Returns:
        The parts of the path, or None when the file is outside the source.
    """
    try:
        relative = path.resolve().relative_to(source_dir(workspace).resolve())
    except ValueError:
        return None
    return relative.with_suffix("").parts
