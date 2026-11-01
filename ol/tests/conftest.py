"""Helpers shared by the tests."""

from __future__ import annotations

from pathlib import Path

import pytest

CATEGORIES = ("concepts", "grammar", "writing", "vocabulary")
SIDEBAR = "---\nhtml_theme.sidebar_secondary.remove:\n---\n"
INTRODUCTION = (
    f"{SIDEBAR}# Introduction\n\nA free, open coursebook.\n\n"
    "## How the course works\n\nAny page can be read first.\n\n"
    "## Levels\n\n- [A1](a1/index.md): the first days.\n\n"
    "## Categories\n\n"
    "- [Concepts](a1/concepts/index.md): what to say.\n"
    "- [Grammar](a1/grammar/index.md): how it is built.\n"
    "- [Writing](a1/writing/index.md): model texts.\n"
    "- [Vocabulary](a1/vocabulary/index.md): word packs.\n\n"
    "## Where to start\n\n"
    "- New to the language: [A1](a1/index.md).\n"
    "- An unfamiliar term: [the glossary](terminology.md).\n\n"
    "```{toctree}\n:hidden:\n\nhow_to_use\nterminology\ncontributing\na1/index\n```\n"
)
LEVEL = (
    f"{SIDEBAR}# A1\n\nThe first level of the course.\n\n"
    "## What learners know\n\n- The articles.\n- The present tense.\n"
    "- Word order.\n\n"
    "## What learners can do\n\n- Greet someone.\n- Order food.\n"
    "- Ask the way.\n- Spell a name.\n\n"
    "```{toctree}\n:maxdepth: 2\n\nconcepts/index\ngrammar/index\n"
    "writing/index\nvocabulary/index\n```\n\n"
    "## Additional reading\n\n- [A list](https://example.org/list): the words.\n"
)
MENU_PAGES = {
    "index.md": INTRODUCTION,
    "how_to_use.md": "# How to use\n\nHow to read it.\n",
    "terminology.md": "# Terminology\n\nThe terms.\n",
    "contributing.md": "# Contributing\n\nHow to help.\n",
    "a1/index.md": LEVEL,
    **{
        f"a1/{category}/index.md": (
            f"{SIDEBAR}# {category.capitalize()}\n\nThe {category} articles.\n\n"
            "```{toctree}\nfirst\n```\n"
        )
        for category in CATEGORIES
    },
    **{f"a1/{category}/first.md": "# First\n" for category in CATEGORIES},
}


@pytest.fixture
def write_menu():
    """Give a language repository the smallest pages the checks pass.

    The standard top-level pages, and A1, whose category indexes each list one
    placeholder page.
    """

    def write(root: Path) -> Path:
        for rel, text in MENU_PAGES.items():
            page = root / rel
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(text, encoding="utf-8")
        return root

    return write
