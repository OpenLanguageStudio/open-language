"""A page uses only the components the components page lists, each where it goes.

Each case breaks one finished fixture page, or one page of the smallest menu,
and asserts the error it should raise. The cases that should pass assert that
no error is raised at all.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ol.authoring.validate import validate_file

FIXTURES = Path(__file__).parent / "fixtures"
PATHS = {
    "grammar": "a1/grammar/articles/bestimmter-artikel.md",
    "how-to": "a1/how-to/greetings.md",
    "writing": "a1/writing/email-formal-1.md",
}
LINK_TARGETS = [
    "a1/grammar/articles/unbestimmter-artikel.md",
    "a1/grammar/cases/nominativ.md",
    "a1/grammar/cases/akkusativ.md",
    "a1/grammar/other/nomen-genus-plural.md",
    "a2/grammar/adjektivendungen.md",
]
CONF = 'custom_roles = ["akk", "article"]\n'
WORDS_61 = " ".join(["word"] * 60) + " words."
SECTION_2 = "## When to use *der*, *die*, *das*\n"
SECTION_3 = "## Accusative: *der* becomes *den*\n"
HEAR = "## Hear it in practice\n"
RELATED = "## Related articles\n\n"


def fixture(category: str) -> str:
    return (FIXTURES / f"{category}-article.md").read_text(encoding="utf-8")


def repository(root: Path) -> Path:
    (root / "open-language.yml").write_text(
        "language: German\nlanguage_code: de\n", encoding="utf-8"
    )
    (root / "conf.py").write_text(CONF, encoding="utf-8")
    for target in LINK_TARGETS:
        page = root / target
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("# Page\n", encoding="utf-8")
    return root


def errors(root: Path, category: str, text: str) -> list[str]:
    repository(root)
    page = root / PATHS[category]
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(text, encoding="utf-8")
    return [m for lvl, m in validate_file(page, root).items if lvl == "ERROR"]


def notice(kind: str = "tip", text: str = "A short aside.") -> str:
    return f":::{{{kind}}}\n{text}\n:::\n\n"


def before(anchor: str, text: str):
    """A breaker that puts ``text`` in front of ``anchor``."""
    return lambda s: s.replace(anchor, text + anchor, 1)


def related(line: str):
    """A breaker that adds ``line`` to Related articles."""
    return lambda s: s.replace(RELATED, f"{RELATED}{line}\n", 1)


@pytest.mark.parametrize("category", PATHS)
def test_fixture_passes(tmp_path, category):
    assert errors(tmp_path, category, fixture(category)) == []


GRAMMAR = {
    # Directives.
    "a hint": (
        lambda s: s.replace(":::{note}", ":::{hint}", 1),
        "the hint directive is not a component: write it as a tip",
    ),
    "a danger notice": (
        lambda s: s.replace(":::{note}", ":::{danger}", 1),
        "the danger directive is not a component",
    ),
    "a code block directive": (
        before(SECTION_2, "```{code-block} python\nx = 1\n```\n\n"),
        "the code-block directive is not a component",
    ),
    "an examples box written as a div": (
        lambda s: s.replace(
            ":::{ol-examples}\n:presenters: emilia\n", ":::{div} ol-examples\n", 1
        ),
        "the div directive is not a component",
    ),
    "a notice with another title": (
        lambda s: s.replace(
            "{admonition} Common mistakes", "{admonition} Watch out", 1
        ),
        "the notice titled 'Watch out'",
    ),
    "common mistakes of another class": (
        lambda s: s.replace(":class: caution", ":class: warning", 1),
        "the Common mistakes notice takes ':class: caution'",
    ),
    "a toctree in an article": (
        before(SECTION_2, "```{toctree}\n:hidden:\n\nother\n```\n\n"),
        "the menu is on index pages",
    ),
    "a card grid in an article": (
        before(
            SECTION_2,
            "::::{grid} 1 1 2 2\n:gutter: 3\n\n:::{grid-item-card} Page\n"
            ":link: /a1/grammar/cases/nominativ\n:link-type: doc\n\nA page.\n:::\n"
            "::::\n\n",
        ),
        "card grids are for index pages and the Introduction",
    ),
    "a button in an article": (
        before(
            SECTION_2,
            "```{button-ref} /a1/grammar/cases/nominativ\n:ref-type: doc\n"
            ":color: primary\n\nGo\n```\n\n",
        ),
        "the button-ref directive is not a component",
    ),
    "a glossary in an article": (
        before(SECTION_2, "```{glossary}\nNoun\n  A word.\n```\n\n"),
        "the glossary is on the Terminology page",
    ),
    "a block quote outside writing": (
        before(SECTION_2, "> Der Hafen ist groß.\n\n"),
        "a block quote holds the model text of a writing article",
    ),
    # Hidden content.
    "a collapsible": (
        before(SECTION_2, ":::{dropdown} More\nA detail.\n:::\n\n"),
        "the dropdown directive is a collapsible",
    ),
    "a notice made collapsible": (
        lambda s: s.replace(":::{note}\n", ":::{note}\n:class: dropdown\n", 1),
        ":class: dropdown makes the note a collapsible",
    ),
    "a details block": (
        before(
            SECTION_2, "<details>\n<summary>More</summary>\nA detail.\n</details>\n\n"
        ),
        "a <details> block is a collapsible",
    ),
    # Roles and inline elements.
    "an unlisted role": (
        before(SECTION_2, "Water is H{sub}`2`O.\n\n"),
        "the {sub} role is not a component",
    ),
    "an abbreviation": (
        before(SECTION_2, "An {abbr}`Akk. (Akkusativ)` form.\n\n"),
        "a phone has no hover",
    ),
    "an interface role in an article": (
        before(SECTION_2, "Press {kbd}`Ctrl`.\n\n"),
        "only How to use and Contributing use it",
    ),
    "another badge": (
        before(SECTION_2, "A {bdg-success}`right` form.\n\n"),
        "the only badges are {level} and {bdg-light}",
    ),
    "a footnote": (
        before(SECTION_2, "The article comes first.[^1]\n\n[^1]: Always.\n\n"),
        "a footnote",
    ),
    "struck-through text": (
        before(SECTION_2, "Never ~~der Frau~~ here.\n\n"),
        "struck-through text",
    ),
    "a highlighted span": (
        before(SECTION_2, "The [der]{.mark} form.\n\n"),
        "a highlighted span",
    ),
    "a paragraph of bold text": (
        lambda s: s.replace(":::{ol-examples}", "**Examples:**\n\n:::{ol-examples}", 1),
        "'Examples:' is a paragraph of bold text",
    ),
    # Notices.
    "four notices": (
        lambda s: s.replace(HEAR, HEAR + "\n" + notice("note"), 1).replace(
            SECTION_3, SECTION_3 + "\n" + notice("warning"), 1
        ),
        "4 notices (maximum 3)",
    ),
    "two notices in a section": (
        before(SECTION_2, notice("warning")),
        "holds 2 notices (maximum 1)",
    ),
    "two important notices": (
        lambda s: s.replace(":::{note}", ":::{important}", 1).replace(
            ":::{tip}", ":::{important}", 1
        ),
        "2 important notices (maximum 1)",
    ),
    "a long notice": (
        lambda s: s.replace(":::{note}\n", f":::{{note}}\n{WORDS_61}\n\n", 1),
        "words (maximum 60)",
    ),
    "a notice inside a notice": (
        lambda s: s.replace(
            ":::{admonition} Key points\n",
            "::::{admonition} Key points\n",
            1,
        ).replace(":::\n\n## Related", ":::{tip}\nInside.\n:::\n::::\n\n## Related", 1),
        "a notice holds another notice",
    ),
    # Links and level badges.
    "a related link with text": (
        related("- [Nominative](/a1/grammar/cases/nominativ.md)"),
        "write the Related articles link to /a1/grammar/cases/nominativ.md as [](...)",
    ),
    "a prerequisite with text": (
        before(
            "## The forms",
            ":::{admonition} Prerequisites\n:class: note\n"
            "- [Nominative](/a1/grammar/cases/nominativ.md)\n:::\n\n",
        ),
        "write the Prerequisites link",
    ),
    "another level without its badge": (
        related("- [](/a2/grammar/adjektivendungen.md)"),
        "is followed by its level, {level}`A2`",
    ),
    "a badge naming another level": (
        related("- [](/a2/grammar/adjektivendungen.md) {level}`B1`"),
        "the badge says B1, and /a2/grammar/adjektivendungen.md is a page of A2",
    ),
    "a badge after a link to this level": (
        related("- [](/a1/grammar/cases/nominativ.md) {level}`A1`"),
        "is a page of this level, which takes no level badge",
    ),
    "a badge without a link": (
        before(SECTION_2, "This is an {level}`A1` topic.\n\n"),
        "appears nowhere else",
    ),
    "a badge naming no level": (
        related("- [](/a2/grammar/adjektivendungen.md) {level}`C3`"),
        "'C3' is not a level",
    ),
    "a register badge in prose": (
        before(SECTION_2, "Say it {bdg-light}`informal`.\n\n"),
        "1 register badge(s) outside a Notes cell",
    ),
    # Tabs.
    "tabs in a grammar article": (
        before(
            SECTION_2,
            "::::{tab-set}\n:::{tab-item} One\n| Phrase | Notes |\n|---|---|\n"
            "| a | b |\n:::\n:::{tab-item} Two\n| Phrase | Notes |\n|---|---|\n"
            "| c | d |\n:::\n::::\n\n",
        ),
        None,
    ),
}


@pytest.mark.parametrize("case", GRAMMAR, ids=list(GRAMMAR))
def test_broken_grammar_article_is_red(tmp_path, case):
    breaker, expected = GRAMMAR[case]
    source = fixture("grammar")
    broken = breaker(source)
    assert broken != source, "the mutation did not change the fixture"
    found = errors(tmp_path, "grammar", broken)
    if expected is None:
        assert found == []
    else:
        assert any(expected in msg for msg in found), found


def test_a_role_in_inline_code_or_a_code_block_is_not_read(tmp_path):
    quoted = fixture("grammar").replace(
        SECTION_2,
        "Never write ``{sub}`2` `` on a page.\n\n```text\n{abbr}`x`\n```\n\n"
        + SECTION_2,
        1,
    )
    assert not any(
        "role is not a component" in m for m in errors(tmp_path, "grammar", quoted)
    )


def test_a_badge_after_a_link_to_another_level_passes(tmp_path):
    linked = related("- [](/a2/grammar/adjektivendungen.md) {level}`A2`")
    assert errors(tmp_path, "grammar", linked(fixture("grammar"))) == []


def test_a_role_the_language_does_not_register_is_not_a_component(tmp_path):
    source = fixture("grammar")
    repository(tmp_path)
    (tmp_path / "conf.py").write_text('custom_roles = ["akk"]\n', encoding="utf-8")
    page = tmp_path / PATHS["grammar"]
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(source, encoding="utf-8")
    found = [m for lvl, m in validate_file(page, tmp_path).items if lvl == "ERROR"]
    assert any("the {article} role is not a component" in m for m in found), found


TAB = ":::{{tab-item}} {label}\n{body}:::\n"
TABLE = "| Phrase | Notes |\n|---|---|\n| {stack}`Hallo \\| Hi` | |\n"
EXAMPLES = ":::{ol-examples}\n:presenters: emilia\nHallo.\n: Hi.\n:::\n"


def tab_set(*tabs: tuple[str, str]) -> str:
    inner = "".join(TAB.format(label=label, body=body) for label, body in tabs)
    return f"::::{{tab-set}}\n{inner}::::\n\n"


def how_to(*parts: str) -> str:
    """The how-to fixture with ``parts`` under Key phrases."""
    return fixture("how-to").replace(
        "### Saying goodbye\n", "".join(parts) + "### Saying goodbye\n", 1
    )


TWO_TABS = tab_set(("Informal", TABLE), ("Formal", TABLE))


def test_a_tab_set_of_phrase_tables_passes(tmp_path):
    assert errors(tmp_path, "how-to", how_to(TWO_TABS)) == []


def test_a_tab_set_of_example_blocks_passes(tmp_path):
    # An example block inside a tab takes fewer colons than the tab around it.
    tabs = "".join(
        f"::::{{tab-item}} {label}\n{EXAMPLES}::::\n"
        for label in ("Informal", "Formal")
    )
    tabs = f":::::{{tab-set}}\n{tabs}:::::\n\n"
    assert errors(tmp_path, "how-to", how_to(tabs)) == []


TABS = {
    "one tab": (tab_set(("Informal", TABLE)), "1 tabs (a tab set has 2 to 3)"),
    "four tabs": (
        tab_set(*[(f"Tab {n}", TABLE) for n in "abcd"]),
        "4 tabs (a tab set has 2 to 3)",
    ),
    "a long label": (
        tab_set(("Informal with friends here", TABLE), ("Formal", TABLE)),
        "is 4 words (maximum 3)",
    ),
    "a notice in a tab": (
        tab_set(("Informal", TABLE + notice("tip")), ("Formal", TABLE)),
        "holds a notice",
    ),
    "a heading in a tab": (
        tab_set(("Informal", "#### Greetings\n\n" + TABLE), ("Formal", TABLE)),
        "holds a heading",
    ),
    "prose in a tab": (
        tab_set(("Informal", "Say this.\n\n" + TABLE), ("Formal", TABLE)),
        "holds a paragraph",
    ),
    "mixed kinds": (
        tab_set(("Informal", TABLE), ("Formal", EXAMPLES)),
        "the tabs hold different kinds of thing",
    ),
    "two tab sets": (TWO_TABS + TWO_TABS, "2 tab sets (maximum 1)"),
}


@pytest.mark.parametrize("case", TABS, ids=list(TABS))
def test_broken_tabs_are_red(tmp_path, case):
    tabs, expected = TABS[case]
    found = errors(tmp_path, "how-to", how_to(tabs))
    assert any(expected in msg for msg in found), found


def test_tabs_in_a_writing_article_are_red(tmp_path):
    writing = fixture("writing").replace(
        "## Building blocks\n", "## Building blocks\n\n" + TWO_TABS, 1
    )
    found = errors(tmp_path, "writing", writing)
    assert any("tabs are for grammar and how-to articles" in m for m in found), found


def test_a_register_badge_in_a_notes_cell_passes(tmp_path):
    table = "| Phrase | Notes |\n|---|---|\n| {stack}`Hallo \\| Hi` | {bdg-light}`informal` |\n"
    assert errors(tmp_path, "how-to", how_to(table, "\n")) == []


def test_a_register_badge_holds_a_register(tmp_path):
    table = "| Phrase | Notes |\n|---|---|\n| {stack}`Hallo \\| Hi` | {bdg-light}`friendly` |\n"
    found = errors(tmp_path, "how-to", how_to(table, "\n"))
    assert any("the register badge holds" in m for m in found), found


def test_a_register_badge_outside_the_notes_column_is_red(tmp_path):
    table = "| Phrase | Notes |\n|---|---|\n| {bdg-light}`informal` | Hi. |\n"
    found = errors(tmp_path, "how-to", how_to(table, "\n"))
    assert any("outside a Notes cell" in m for m in found), found


# Index pages and the standard top-level pages.

SUBCATEGORY_INDEX = (
    "---\nhtml_theme.sidebar_secondary.remove:\n---\n# Grammar\n\n"
    "The grammar topics.\n\n```{toctree}\n:hidden:\n\narticles/index\ncases/index\n```\n\n"
    "::::{grid} 1 1 2 2\n:gutter: 3\n\n"
    ":::{grid-item-card} Articles\n:link: articles/index\n:link-type: doc\n\n"
    "The small words before a noun.\n:::\n\n"
    ":::{grid-item-card} Grammatical cases\n:link: cases/index\n:link-type: doc\n\n"
    "The job a noun does.\n:::\n::::\n"
)


@pytest.fixture
def pages(tmp_path, write_menu):
    root = write_menu(tmp_path)
    (root / "conf.py").write_text(CONF, encoding="utf-8")
    for directory, title in (("articles", "Articles"), ("cases", "Grammatical cases")):
        index = root / "a1/grammar" / directory / "index.md"
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(
            f"---\nhtml_theme.sidebar_secondary.remove:\n---\n# {title}\n\n"
            "The articles here.\n\n```{toctree}\nfirst\n```\n",
            encoding="utf-8",
        )
        (index.parent / "first.md").write_text("# First\n", encoding="utf-8")
    return root


def page_errors(root: Path, rel: str, text: str) -> list[str]:
    page = root / rel
    page.write_text(text, encoding="utf-8")
    return [m for lvl, m in validate_file(page, root).items if lvl == "ERROR"]


def test_a_category_index_with_subcategories_shows_cards(pages):
    assert page_errors(pages, "a1/grammar/index.md", SUBCATEGORY_INDEX) == []


INDEXES = {
    "subcategories in a shown toctree": (
        lambda s: s.replace(":hidden:\n", "", 1),
        "the toctree lists subcategories: hide it with :hidden:",
    ),
    "a subcategory without its card": (
        lambda s: s[: s.index(":::{grid-item-card} Grammatical")] + "::::\n",
        "the cards link the pages of the toctree, in its order",
    ),
    "cards in another order": (
        lambda s: s.replace(
            "articles/index\ncases/index", "cases/index\narticles/index"
        ),
        "the cards link the pages of the toctree, in its order",
    ),
    "another grid": (
        lambda s: s.replace("::::{grid} 1 1 2 2", "::::{grid} 1 2 3", 1),
        "a card grid is '::::{grid} 1 1 2 2' with ':gutter: 3'",
    ),
    "no gutter": (
        lambda s: s.replace(":gutter: 3\n", "", 1),
        "with ':gutter: 3'",
    ),
    "a card without link-type": (
        lambda s: s.replace(":link-type: doc\n", "", 1),
        "takes ':link:' to a page and ':link-type: doc'",
    ),
    "a card with a header": (
        lambda s: s.replace(
            ":link-type: doc\n\nThe small",
            ":link-type: doc\n\nHeader\n^^^\nThe small",
            1,
        ),
        "has a header, a footer or a picture",
    ),
    "a card with a picture": (
        lambda s: s.replace(
            ":link-type: doc\n", ":link-type: doc\n:img-top: a.png\n", 1
        ),
        "has a header, a footer or a picture",
    ),
    "a card titled otherwise": (
        lambda s: s.replace("{grid-item-card} Articles", "{grid-item-card} Words", 1),
        "the card 'Words' is titled as the page it opens, 'Articles'",
    ),
    "a card of two sentences": (
        lambda s: s.replace(
            "The small words before a noun.", "Small words. Before a noun.", 1
        ),
        "the card 'Articles' holds one sentence",
    ),
    "a long card": (
        lambda s: s.replace(
            "The small words before a noun.", " ".join(["word"] * 16) + ".", 1
        ),
        "the card 'Articles' is 16 words (maximum 15)",
    ),
    "a card to no page": (
        lambda s: s.replace(":link: articles/index", ":link: missing/index", 1),
        "links missing/index, no page",
    ),
}


@pytest.mark.parametrize("case", INDEXES, ids=list(INDEXES))
def test_broken_category_index_is_red(pages, case):
    breaker, expected = INDEXES[case]
    broken = breaker(SUBCATEGORY_INDEX)
    assert broken != SUBCATEGORY_INDEX, "the mutation did not change the page"
    found = page_errors(pages, "a1/grammar/index.md", broken)
    assert any(expected in msg for msg in found), found


def test_a_flat_category_index_shows_its_toctree(pages):
    flat = (pages / "a1/how-to/index.md").read_text(encoding="utf-8")
    hidden = flat.replace("```{toctree}\n", "```{toctree}\n:hidden:\n", 1)
    found = page_errors(pages, "a1/how-to/index.md", hidden)
    assert any("show it, without :hidden:" in m for m in found), found


def test_a_flat_category_index_has_no_cards(pages):
    flat = (pages / "a1/how-to/index.md").read_text(encoding="utf-8")
    carded = flat + (
        "\n::::{grid} 1 1 2 2\n:gutter: 3\n\n:::{grid-item-card} First\n"
        ":link: first\n:link-type: doc\n\nThe first page.\n:::\n::::\n"
    )
    found = page_errors(pages, "a1/how-to/index.md", carded)
    assert any("cards on an index of articles" in m for m in found), found


def test_how_to_use_may_use_interface_roles(pages):
    text = "# How to use\n\nPress {kbd}`Ctrl` and {guilabel}`Search`.\n"
    assert page_errors(pages, "how_to_use.md", text) == []


def test_contributing_may_use_interface_roles(pages):
    text = "# Contributing\n\nRun {command}`ol check` in {file}`de/`.\n"
    assert page_errors(pages, "contributing.md", text) == []


def test_how_to_use_holds_no_unlisted_directive(pages):
    text = "# How to use\n\nHow to read it.\n\n:::{dropdown} More\nx\n:::\n"
    found = page_errors(pages, "how_to_use.md", text)
    assert any("the dropdown directive is a collapsible" in m for m in found), found


def test_terminology_may_not_use_interface_roles(pages):
    terminology = pages / "terminology.md"
    text = terminology.read_text(encoding="utf-8") + "\nPress {kbd}`Ctrl`.\n"
    found = page_errors(pages, "terminology.md", text)
    assert any("the {kbd} role is not a component" in m for m in found), found
