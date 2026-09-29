"""
context — resolve the working context from the active git branch.

Branch naming convention (enforced by ol.create):
  content/{level}-{section}                e.g. content/a1-grammar
  content/{level}-{section}-{sub-section}  e.g. content/a2-grammar-cases
"""

from __future__ import annotations

import subprocess

CONTENT_PREFIX = "content/"

VALID_LEVELS = {"a1", "a2", "b1", "b2", "c1", "c2"}


def get_current_branch() -> str | None:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        branch = result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    else:
        return branch if branch else None


def parse_branch(branch: str) -> dict:
    """Parse a content branch name into level, section, and sub_section."""
    empty = {"branch": branch, "level": None, "section": None, "sub_section": None}

    if not branch or not branch.startswith(CONTENT_PREFIX):
        return empty

    slug = branch[len(CONTENT_PREFIX) :]
    parts = slug.split("-", maxsplit=2)

    if len(parts) < 2:
        return empty

    level = parts[0].lower()
    if level not in VALID_LEVELS:
        return empty

    return {
        "branch": branch,
        "level": level,
        "section": parts[1].lower(),
        "sub_section": parts[2].lower() if len(parts) == 3 else None,
    }
