"""Situation articles and the how-to articles they name (ADR 2).

Each case breaks one rule of a finished situation, or of a how-to article a
situation names, and asserts the error it should raise.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from test_standard import FIXTURES, PATHS, errors, fixture, report, repository

from ol.authoring.validate import validate_file

SITUATION = "a1/situations/at-a-party.md"
HOW_TO = "a1/how-to/introduce-yourself.md"
WHEN = "## When to use it\n\n- Walking into a shop or an office.\n- Meeting a friend on the street.\n- Leaving a party.\n\n"
BOX = ":::{situations}\n:::\n\n"


BROKEN = {
    "no how-to list": (
        lambda s: s.replace("how-to:\n  - /a1/how-to/introduce-yourself.md\n", ""),
        "front matter has no 'how-to:' list",
    ),
    "four how-to links": (
        lambda s: s.replace(
            "  - /a1/how-to/introduce-yourself.md\n",
            "  - /a1/how-to/introduce-yourself.md\n" * 4,
        ),
        "names 4 articles (a situation names 1 to 3)",
    ),
    "a grammar page as a how-to link": (
        lambda s: s.replace(
            "/a1/how-to/introduce-yourself.md", "/a1/grammar/cases/nominativ.md", 1
        ),
        "is not a how-to article",
    ),
    "a how-to link that does not exist": (
        lambda s: s.replace(
            "/a1/how-to/introduce-yourself.md", "/a1/how-to/missing.md", 1
        ),
        "'a1/how-to/missing' does not exist",
    ),
    "a how-to link above the level": (
        lambda s: s.replace(
            "/a1/how-to/introduce-yourself.md", "/b1/how-to/introduce-yourself.md", 1
        ),
        "is above the situation's level",
    ),
    "an explanation paragraph": (
        lambda s: s.replace(
            ":::{how-to-links}", "Roman says hello first.\n\n:::{how-to-links}", 1
        ),
        "a situation sets its scene in the lead alone",
    ),
    "a how-to box with a body": (
        lambda s: s.replace(
            ":::{how-to-links}\n:::",
            ":::{how-to-links}\n- [](/a1/how-to/introduce-yourself.md)\n:::",
        ),
        "the how-to-links box takes no options and no body",
    ),
    "a phrase table": (
        lambda s: s.replace(
            "## What to listen for",
            "| Phrase | Notes |\n|---|---|\n| {stack}`Hallo \\| Hi` | Casual. |\n\n"
            "## What to listen for",
        ),
        "a situation teaches nothing itself",
    ),
    "an examples box": (
        lambda s: s.replace(
            "## What to listen for",
            ":::{ol-examples}\n:presenters: lina\nHallo!\n: Hi!\n:::\n\n"
            "## What to listen for",
        ),
        "an examples box on a situation",
    ),
    "key points": (
        lambda s: s.replace(
            "## Related articles",
            ":::{admonition} Key points\n:class: note\n\n- Names.\n:::\n\n"
            "## Related articles",
        ),
        "a situation has no summary",
    ),
    "no listening points": (
        lambda s: s.replace(
            "## What to listen for\n\n- *Und du?* turns the question back, so the "
            "conversation keeps going.\n",
            "",
        ),
        "a situations article needs the section '## What to listen for'",
    ),
    "one listening point": (
        lambda s: s.replace(
            "- *Und du?* turns the question back, so the conversation keeps going.\n",
            "",
        ),
        "'What to listen for' has 1 bullets (it has 2 to 4)",
    ),
    "a listening point that teaches": (
        lambda s: s.replace(
            "- *Und du?* turns the question back",
            "- *Und du?* turns the question back " + "and " * 30,
        ),
        "words (maximum 30)",
    ),
    "a summary section": (
        lambda s: s.replace(
            "## Related articles", "## Summary\n\nNames.\n\n## Related articles"
        ),
        "'Summary' is not a section of a situations article",
    ),
    "an examples track": (
        lambda s: s.replace(
            ":mode: dialogue\n:presenters: lina, roman", ":presenters: lina"
        ),
        "a situation's track is a dialogue, correspondence, passage block, not examples",
    ),
    "a dialogue too short": (
        lambda s: s.replace(
            "roman: Ich komme aus Kiew. Ich wohne jetzt hier in Freiburg.\n"
            ": I'm from Kyiv. I live here in Freiburg now.\n"
            "lina: Ich auch, seit einer Woche.\n: Me too, for a week.\n",
            "",
        ),
        "the dialogue has 4 lines (a scene has 6 to 20)",
    ),
}


@pytest.mark.parametrize("case", BROKEN)
def test_a_broken_situation_is_red(tmp_path, case):
    breaker, expected = BROKEN[case]
    found = errors(tmp_path, "situations", breaker(fixture("situations")))
    assert any(expected in message for message in found), found


def test_a_situation_may_have_two_versions_under_h3s(tmp_path):
    text = fixture("situations")
    start = text.index(":::{audio-examples}")
    end = text.index(":::\n\n## What to listen for") + 4
    block = text[start:end]
    formal = block.replace("at-a-party", "at-a-party-formal").replace(
        ":title: Auf einer Party", ":title: Auf einer Party (Sie)"
    )
    two = text.replace(block, f"### With *du*\n\n{block}\n### With *Sie*\n\n{formal}")
    assert errors(tmp_path, "situations", two) == []


def test_a_situation_has_two_tracks_at_most(tmp_path):
    text = fixture("situations")
    start = text.index(":::{audio-examples}")
    end = text.index(":::\n\n## What to listen for") + 4
    block = text[start:end]
    heads = "".join(
        f"### Version {name}\n\n{block.replace('at-a-party', f'at-a-party-{name}')}\n"
        for name in ("one", "two", "three")
    )
    found = errors(tmp_path, "situations", text.replace(block, heads))
    assert any("3 audio blocks (maximum 2)" in message for message in found), found


# The how-to side.


def how_to_repository(root: Path, *, named: bool, how_to: str) -> Path:
    repository(root)
    if named:
        page = root / SITUATION
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(fixture("situations"), encoding="utf-8")
    page = root / HOW_TO
    page.write_text(how_to, encoding="utf-8")
    return page


def how_to_errors(root: Path, *, named: bool, how_to: str) -> list[str]:
    page = how_to_repository(root, named=named, how_to=how_to)
    return [m for lvl, m in validate_file(page, root).items if lvl == "ERROR"]


def with_box() -> str:
    return (
        fixture("how-to")
        .replace(WHEN, "")
        .replace("## Key phrases", BOX + "## Key phrases", 1)
    )


def test_a_how_to_article_no_situation_names_keeps_when_to_use_it(tmp_path):
    assert how_to_errors(tmp_path, named=False, how_to=fixture("how-to")) == []


def test_a_named_how_to_article_with_the_box_passes(tmp_path):
    assert how_to_errors(tmp_path, named=True, how_to=with_box()) == []


def test_a_named_how_to_article_keeping_when_to_use_it_is_red(tmp_path):
    found = how_to_errors(tmp_path, named=True, how_to=fixture("how-to"))
    assert any(
        "a1/situations/at-a-party names this article" in message for message in found
    ), found


def test_a_named_how_to_article_without_the_box_or_the_section_passes(tmp_path):
    bare = fixture("how-to").replace(WHEN, "")
    assert how_to_errors(tmp_path, named=True, how_to=bare) == []


def test_a_situation_without_the_box_passes(tmp_path):
    bare = fixture("situations").replace(":::{how-to-links}\n:::\n\n", "")
    assert errors(tmp_path, "situations", bare) == []


def retired(tmp_path, text: str, category: str = "how-to") -> list[tuple[str, str]]:
    return report(tmp_path, category, text).items


def test_a_box_on_a_page_without_related_warns(tmp_path):
    items = retired(tmp_path, with_box())
    assert any(lvl == "WARN" and "situations box is retired" in m for lvl, m in items)


@pytest.mark.parametrize(
    ("category", "text"),
    [
        ("how-to", lambda: with_box()),
        (
            "situations",
            lambda: fixture("situations").replace("how-to:", "related: []\nhow-to:", 1),
        ),
    ],
)
def test_a_box_on_a_page_with_related_is_red(tmp_path, category, text):
    page = text()
    if category == "how-to":
        page = page.replace("---\n", "---\nrelated: []\n", 1)
    items = retired(tmp_path, page, category)
    assert any(lvl == "ERROR" and "box is retired" in m for lvl, m in items), items


def test_the_box_on_an_article_no_situation_names_is_red(tmp_path):
    found = how_to_errors(tmp_path, named=False, how_to=with_box())
    assert any("on an article no situation names" in m for m in found), found


def test_the_box_and_when_to_use_it_together_are_red(tmp_path):
    both = fixture("how-to").replace("## When to use it", BOX + "## When to use it", 1)
    found = how_to_errors(tmp_path, named=True, how_to=both)
    assert any("the box takes the section's place" in m for m in found), found


def test_a_how_to_article_with_neither_is_red(tmp_path):
    neither = fixture("how-to").replace(WHEN, "")
    found = how_to_errors(tmp_path, named=False, how_to=neither)
    assert "a how-to article needs the section '## When to use it'" in found


def test_the_box_out_of_the_opening_is_red(tmp_path):
    late = (
        fixture("how-to").replace(WHEN, "").replace("## Summary", BOX + "## Summary", 1)
    )
    found = how_to_errors(tmp_path, named=True, how_to=late)
    assert any("the situations box stands in the opening" in m for m in found), found


@pytest.mark.parametrize(
    ("category", "box"), [("grammar", "situations"), ("how-to", "how-to-links")]
)
def test_each_box_belongs_to_its_category(tmp_path, category, box):
    text = fixture(category).replace(
        "## Hear it in practice", f":::{{{box}}}\n:::\n\n## Hear it in practice", 1
    )
    found = errors(tmp_path, category, text)
    assert any(f"{box} on this page" in m for m in found), found


def test_the_fixture_is_where_the_tests_expect_it():
    assert PATHS["situations"] == SITUATION
    assert (FIXTURES / "situations-article.md").is_file()
