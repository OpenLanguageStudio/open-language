"""Helpers shared by the tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from ol.authoring.menu import CATEGORY_NAMES

CATEGORIES = ("how-to", "grammar", "writing", "vocabulary")
SIDEBAR = "---\nhtml_theme.sidebar_secondary.remove:\n---\n"


def grid(*cards: tuple[str, str, str]) -> str:
    """A card grid of (title, link, sentence) cards."""
    body = "".join(
        f":::{{grid-item-card}} {title}\n:link: {link}\n:link-type: doc\n\n"
        f"{sentence}\n:::\n\n"
        for title, link, sentence in cards
    )
    return f"::::{{grid}} 1 1 2 2\n:gutter: 3\n\n{body}::::\n"


INTRODUCTION = (
    f"{SIDEBAR}# Introduction\n\nA free, open coursebook.\n\n"
    "## How the course works\n\nAny page can be read first.\n\n"
    "## Levels\n\n" + grid(("A1", "a1/index", "The first days.")) + "\n"
    "## Categories\n\n"
    + grid(
        ("How to", "a1/how-to/index", "What to say."),
        ("Grammar", "a1/grammar/index", "How it is built."),
        ("Writing", "a1/writing/index", "Model texts."),
        ("Vocabulary", "a1/vocabulary/index", "Word packs."),
    )
    + "\n## Where to start\n\n"
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
    "```{toctree}\n:maxdepth: 2\n:hidden:\n\nhow-to/index\ngrammar/index\n"
    "writing/index\nvocabulary/index\n```\n\n"
    "## Categories\n\n"
    + grid(
        ("How to", "how-to/index", "What to say."),
        ("Grammar", "grammar/index", "How it is built."),
        ("Writing", "writing/index", "Model texts."),
        ("Vocabulary", "vocabulary/index", "Word packs."),
    )
    + "\n## Additional reading\n\n- [A list](https://example.org/list): the words.\n"
)
MENU_PAGES = {
    "index.md": INTRODUCTION,
    "how_to_use.md": "# How to use\n\nHow to read it.\n",
    "terminology.md": "# Terminology\n\nThe terms.\n",
    "contributing.md": "# Contributing\n\nHow to help.\n",
    "a1/index.md": LEVEL,
    **{
        f"a1/{category}/index.md": (
            f"{SIDEBAR}# {CATEGORY_NAMES[category]}\n\nThe {category} articles.\n\n"
            "```{toctree}\nfirst\n```\n"
        )
        for category in CATEGORIES
    },
    **{f"a1/{category}/first.md": "# First\n" for category in CATEGORIES},
}


@pytest.fixture(autouse=True)
def no_shared_terms(tmp_path, monkeypatch):
    """Hide the term list this package ships.

    A test's pages then need not link the list's words, and its Terminology page
    need not hold an entry for each. A test about term lists sets its own, and
    ``test_glossary.py`` reads the shipped one.
    """
    monkeypatch.setattr("ol.authoring.glossary.SHARED_TERMS", tmp_path / "none.yml")


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
