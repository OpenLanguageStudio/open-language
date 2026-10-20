"""Helpers shared by the tests."""

from __future__ import annotations

from pathlib import Path

import pytest

MENU_PAGES = {
    "index.md": "# Introduction\n\n```{toctree}\na1/index\n```\n",
    "a1/index.md": "# A1\n\n```{toctree}\ngrammar/index\n```\n",
    "a1/grammar/index.md": "# Grammar\n\nGrammar articles.\n\n```{toctree}\nfirst\n```\n",
    "a1/grammar/first.md": "# First\n",
}


@pytest.fixture
def write_menu():
    """Give a language repository the smallest menu the menu check passes.

    The menu lists A1, whose grammar index lists one placeholder page.
    """

    def write(root: Path) -> Path:
        for rel, text in MENU_PAGES.items():
            page = root / rel
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(text, encoding="utf-8")
        return root

    return write
