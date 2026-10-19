"""Every validator rule must go red on a deliberately broken article.

The fixture is a finished A1 grammar article that passes cleanly. Each case
breaks exactly one thing and asserts the specific error it should raise, so a
rule that silently stops firing fails here rather than in a content review.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ol.authoring.validate import validate_file

FIXTURE = Path(__file__).parent / "fixtures" / "grammar-article.md"
ARTICLE = "docs/a1/grammar/articles/bestimmter-artikel.md"
LINK_TARGETS = [
    "a1/grammar/articles/unbestimmter-artikel.md",
    "a1/grammar/articles/negativartikel.md",
    "a1/grammar/cases/nominativ.md",
    "a1/grammar/cases/akkusativ.md",
    "a1/grammar/other/nomen-genus-plural.md",
]
H1 = "# Definite Articles\n"
TRACK = ":track: a1/grammar/bestimmter-artikel\n"


def errors(tmp_path: Path, text: str) -> list[str]:
    for target in LINK_TARGETS:
        page = tmp_path / "docs" / target
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("# Page\n", encoding="utf-8")
    article = tmp_path / ARTICLE
    article.write_text(text, encoding="utf-8")
    (tmp_path / "open-language.yml").write_text(
        "language: German\nlanguage_code: de\n", encoding="utf-8"
    )
    return [
        msg for lvl, msg in validate_file(article, tmp_path).items if lvl == "ERROR"
    ]


@pytest.fixture
def source() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def test_fixture_passes(tmp_path, source):
    assert errors(tmp_path, source) == []


def _break_first_audio_line(text: str) -> str:
    pattern = r"(:track: a1/grammar/bestimmter-artikel\n(?:.*\n)*?\n)(\S[^\n]*)"
    return re.sub(pattern, lambda m: m.group(1) + "`" + m.group(2), text, count=1)


def _keep_audio_pairs(text: str, keep: int) -> str:
    head, rest = text.split(":title-en: The definite article\n\n", 1)
    block, tail = rest.split("\n:::\n", 1)
    pairs = block.split("\n\n")[:keep]
    return (
        head
        + ":title-en: The definite article\n\n"
        + "\n\n".join(pairs)
        + "\n:::\n"
        + tail
    )


BROKEN_ARTICLES = {
    "too many inline examples": (
        lambda s: s.replace(
            "Sie liest {akk}`das` Buch.",
            "Ich lese {akk}`das` Heft.\n: I am reading the notebook.\n\n"
            "Sie liest {akk}`das` Buch.",
            1,
        ),
        "5 examples",
    ),
    "too many marks in a sentence": (
        lambda s: s.replace(
            "Ich sehe {akk}`den` Turm.", "{nom}`Ich` {verb}`sehe` {akk}`den` Turm.", 1
        ),
        "different marks in one sentence",
    ),
    "too many marks in a block": (
        lambda s: (
            s.replace(
                "Er kauft {akk}`den` Käse.", "{nom}`Er` kauft {dat}`dem` Käse.", 1
            )
            .replace("Wir nehmen {akk}`die`", "{verb}`Wir` nehmen {gen}`die`", 1)
            .replace("Sie liest {akk}`das`", "Sie liest {prep}`das`", 1)
        ),
        "different marks in one block",
    ),
    "too few audio examples": (
        lambda s: _keep_audio_pairs(s, 5),
        "5 examples (a track carries",
    ),
    "dash in a new store title": (
        lambda s: s.replace(
            ":title-en: The definite article", ":title-en: Articles - Definite", 1
        ),
        "contains a dash",
    ),
    "stock phrase": (
        lambda s: s.replace(
            "## The forms", "Additionally, gender matters.\n\n## The forms", 1
        ),
        "stock phrase 'Additionally'",
    ),
    "em dash": (
        lambda s: s.replace(
            "## The forms", "Articles — the basics.\n\n## The forms", 1
        ),
        "em dash",
    ),
    "missing audio section": (
        lambda s: s.replace("## Hear it in practice", "## Listen", 1),
        "^Hear it in practice$",
    ),
    "missing summary": (
        lambda s: s.replace("## Summary", "## Recap", 1),
        "^Summary$",
    ),
    "blockquote subtitle": (
        lambda s: s.replace(H1, H1 + "\n> The words for 'the'\n", 1),
        "blockquote subtitle",
    ),
    "seealso block": (
        lambda s: s.replace("## Summary", ":::{seealso}\nx\n:::\n\n## Summary", 1),
        "seealso",
    ),
    "no frontmatter": (lambda s: s[s.index(H1) :], "frontmatter"),
    "html comment": (
        lambda s: s.replace("## Summary", "<!-- note -->\n\n## Summary", 1),
        "HTML comment",
    ),
    "unfilled placeholder": (
        lambda s: s.replace("## Summary", "{{TITLE}}\n\n## Summary", 1),
        "PLACEHOLDER",
    ),
    "broken doc link": (
        lambda s: s.replace("negativartikel.md", "missing-page.md", 1),
        "broken doc link",
    ),
    "stock opener": (
        lambda s: s.replace(
            H1, H1 + "\nAfter this page you can use der, die and das.\n", 1
        ),
        "stock opener",
    ),
    "hand-written prev/next": (
        lambda s: s.replace(
            "## Related articles",
            "## Related articles\n\n- Previous: [x](/a1/grammar/cases/nominativ.md)",
            1,
        ),
        "manual navigation link",
    ),
    "note for the author": (
        lambda s: s.replace("## Summary", "TODO: more examples.\n\n## Summary", 1),
        "TODO or FIXME note",
    ),
    "level in the title": (
        lambda s: s.replace(H1, "# A1 Definite Articles\n", 1),
        "contains the CEFR level",
    ),
    "category in the title": (
        lambda s: s.replace(H1, "# Grammar: Definite Articles\n", 1),
        "category prefix",
    ),
    "further reading in an article": (
        lambda s: s.replace(
            "## Related articles", "## Further reading\n\n- x\n\n## Related articles", 1
        ),
        "'Further reading' section",
    ),
    "see also heading": (
        lambda s: s.replace("## Related articles", "## See also", 1),
        "'See also' section",
    ),
    "hand-numbered heading": (
        lambda s: s.replace("## The forms", "## 1. The forms", 1),
        "numbered heading",
    ),
    "too many prerequisites": (
        lambda s: s.replace(
            H1,
            H1
            + "\n:::{admonition} Prerequisites\n:class: note\n"
            + "".join(f"- [Page](/{target})\n" for target in LINK_TARGETS[1:])
            + ":::\n",
            1,
        ),
        "4 prerequisites",
    ),
    "collapsed audio section": (
        lambda s: s.replace(
            "## Hear it in practice\n",
            "## Hear it in practice\n\n:::{dropdown} Listen\nx\n:::\n",
            1,
        ),
        "collapsed",
    ),
    "markup in audio example": (_break_first_audio_line, "plain text"),
    "retired album option": (
        lambda s: s.replace(TRACK, TRACK + ":album: a1/grammar/part-1\n", 1),
        "unknown_option",
    ),
    "no track": (lambda s: s.replace(TRACK, "", 1), "bad_address"),
    "examples on a duplicate": (
        lambda s: s.replace(TRACK, TRACK + ":duplicate:\n", 1),
        "duplicate_writes",
    ),
    "no examples": (lambda s: _keep_audio_pairs(s, 0), "missing_examples"),
    "sentence twice": (
        lambda s: s.replace(
            "Die Brücke ist alt.\n: The bridge is old.\n",
            "Die Brücke ist alt.\n: The bridge is old.\n\n"
            "Die Brücke ist *alt*.\n: The bridge is old indeed.\n",
            1,
        ),
        "sentence_twice",
    ),
}


@pytest.mark.parametrize("case", BROKEN_ARTICLES, ids=list(BROKEN_ARTICLES))
def test_broken_article_is_red(tmp_path, source, case):
    breaker, expected = BROKEN_ARTICLES[case]
    broken = breaker(source)
    assert broken != source, "the mutation did not change the fixture"
    found = errors(tmp_path, broken)
    assert any(expected in msg for msg in found), found


def test_stock_phrase_in_an_example_is_not_prose(tmp_path, source):
    glossed = source.replace(": The harbour is big.", ": The harbour is robust.", 1)
    assert errors(tmp_path, glossed) == []


def write_articles_index(tmp_path: Path, *entries: str) -> None:
    index = tmp_path / "docs/a1/grammar/articles/index.md"
    index.parent.mkdir(parents=True, exist_ok=True)
    toctree = "\n".join(entries)
    index.write_text(
        f"# Articles\n\n```{{toctree}}\n{toctree}\n```\n", encoding="utf-8"
    )


def test_related_link_to_a_toctree_neighbour_warns(tmp_path, source):
    write_articles_index(tmp_path, "bestimmter-artikel", "unbestimmter-artikel")
    assert errors(tmp_path, source) == []
    warnings = [
        msg
        for lvl, msg in validate_file(tmp_path / ARTICLE, tmp_path).items
        if lvl == "WARN"
    ]
    assert any("unbestimmter-artikel" in msg for msg in warnings), warnings


def test_related_link_past_a_toctree_neighbour_passes(tmp_path, source):
    write_articles_index(
        tmp_path, "bestimmter-artikel", "possessivartikel", "unbestimmter-artikel"
    )
    assert errors(tmp_path, source) == []


def vocabulary_errors(
    tmp_path: Path, words: int = 12, name: str = "at-the-beach-1"
) -> list[str]:
    article = tmp_path / f"docs/a1/vocabulary/{name}.md"
    article.parent.mkdir(parents=True)
    rows = "".join(f"| Wort {n} | word {n} |\n" for n in range(words))
    article.write_text(
        "# At the Beach 1\n\nA day at the sea, from the sand to the ice cream.\n\n"
        f"## The words\n\n| German | English |\n|---|---|\n{rows}\n"
        "## Summary\n\nSand, sea and sun.\n",
        encoding="utf-8",
    )
    return [
        msg for lvl, msg in validate_file(article, tmp_path).items if lvl == "ERROR"
    ]


@pytest.mark.parametrize("words", [5, 25])
def test_vocabulary_pack_outside_its_size_is_red(tmp_path, words):
    found = vocabulary_errors(tmp_path, words)
    assert any(f"{words} words" in msg for msg in found), found


def test_vocabulary_pack_within_its_size_passes(tmp_path):
    found = vocabulary_errors(tmp_path, 12)
    assert not any("words" in msg for msg in found), found


def test_pack_without_a_running_number_is_red(tmp_path):
    found = vocabulary_errors(tmp_path, name="at-the-beach")
    assert any("running number" in msg for msg in found), found


def test_short_model_text_is_red(tmp_path):
    article = tmp_path / "docs/a1/writing/postcard.md"
    article.parent.mkdir(parents=True)
    filler = "Writing a postcard is a small, friendly task. " * 6
    article.write_text(
        f"# A Postcard\n\n{filler}\n\n"
        ":::{audio-examples}\n:track: a1/writing/postcard\n:title: Eine Postkarte\n"
        ":multiline:\n\nLiebe Anna,\nviele Grüße aus Hamburg.\n"
        ": Dear Anna,\n: greetings from Hamburg.\n:::\n",
        encoding="utf-8",
    )
    found = [
        msg for lvl, msg in validate_file(article, tmp_path).items if lvl == "ERROR"
    ]
    assert any("model text is 6 words" in msg for msg in found), found


def test_review_rubric_is_well_formed():
    import yaml

    from ol.authoring.validate import SPECS_PATH

    rubric = yaml.safe_load(
        (SPECS_PATH.parent / "review-rubric.yml").read_text(encoding="utf-8")
    )
    assert rubric["answers"] == ["pass", "concern", "fail"]
    ids = [item["id"] for item in rubric["items"]]
    assert len(ids) == len(set(ids))
    for item in rubric["items"]:
        assert item["question"].strip() and item["fail_when"].strip() and item["area"]
