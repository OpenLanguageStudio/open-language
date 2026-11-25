"""The tags a language repository allows, read from its ``track-tags.yml``.

The file holds two lists of strings::

    grammar:
      - nebensatz
    themes:
      - greetings

The allowed tags are the two lists together. A repository without the file has
no list to hold tags to, and nothing is checked.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

TAGS_FILE = "track-tags.yml"
LISTS = ("grammar", "themes")


@dataclass(frozen=True)
class TrackTags:
    """What a repository's ``track-tags.yml`` allows.

    Attributes:
        allowed: Every tag in the file's two lists.
        problem: Why the file is not two lists of strings, or None.
    """

    allowed: frozenset[str]
    problem: str | None = None


@lru_cache(maxsize=32)
def _read(path: Path, stamp: int) -> TrackTags:
    """The tags in a file, read again when its modification time changes."""
    try:
        found = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return TrackTags(frozenset(), f"{TAGS_FILE} does not parse: {exc}")
    allowed: set[str] = set()
    ok = isinstance(found, dict) and set(found) == set(LISTS)
    for name in LISTS:
        values = found.get(name) if isinstance(found, dict) else None
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            ok = False
        else:
            allowed.update(v.strip() for v in values)
    if not ok:
        return TrackTags(
            frozenset(),
            f"{TAGS_FILE} is two lists of strings, 'grammar:' and 'themes:'",
        )
    return TrackTags(frozenset(allowed))


def load_tags(workspace: Path | None) -> TrackTags | None:
    """The tags a language repository allows, or None when it has no list.

    Args:
        workspace: The language repository's root.

    Returns:
        The tags, or None without a ``track-tags.yml``.
    """
    if workspace is None:
        return None
    path = workspace / TAGS_FILE
    if not path.is_file():
        return None
    return _read(path, path.stat().st_mtime_ns)


def check_file(rep, tags: TrackTags | None):
    """Report a ``track-tags.yml`` that is not two lists of strings."""
    if tags and tags.problem:
        rep.error(tags.problem)


def check_block_tags(rep, block, tags: TrackTags | None):
    """A block that writes a track carries tags, each from the list.

    Args:
        rep: The page's report.
        block: The audio block.
        tags: The repository's tags, or None without a list.
    """
    if tags is None or tags.problem:
        return
    where = f"audio-examples (line {block.line})"
    if block.writes and not block.tags:
        rep.error(
            f"{where}: a block that writes a track has no :tags:: add tags "
            f"from {TAGS_FILE}"
        )
    for tag in block.tags:
        if tag not in tags.allowed:
            rep.error(f"{where}: the tag '{tag}' is not in {TAGS_FILE}")


def check_article_tags(rep, fm: dict | None, tags: TrackTags | None):
    """An article's front matter ``tags:`` is a list of tags from the list.

    Args:
        rep: The page's report.
        fm: The article's front matter.
        tags: The repository's tags, or None without a list.
    """
    if tags is None or tags.problem:
        return
    if not fm or "tags" not in fm:
        rep.warn(f"front matter has no 'tags:': list tags from {TAGS_FILE}")
        return
    value = fm["tags"]
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        rep.error("front matter 'tags:' is a list of strings")
        return
    for tag in value:
        if tag.strip() not in tags.allowed:
            rep.error(f"front matter tag '{tag}' is not in {TAGS_FILE}")
