"""Every page standard rule must go red on a deliberately broken page.

Each category has a finished fixture article that passes. Each case breaks one
thing and asserts the error it should raise, so a rule that stops firing fails
here rather than in a content review.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ol.authoring.page import parse, plain, sections, sentences, word_count
from ol.authoring.specs_data import SPECS
from ol.authoring.validate import TEMPLATES_DIR, validate_file

FIXTURES = Path(__file__).parent / "fixtures"
PATHS = {
    "grammar": "a1/grammar/articles/bestimmter-artikel.md",
    "how-to": "a1/how-to/greetings.md",
    "writing": "a1/writing/email-formal-1.md",
    "vocabulary": "a1/vocabulary/at-the-beach-1.md",
}
LINK_TARGETS = [
    "a1/grammar/articles/unbestimmter-artikel.md",
    "a1/grammar/cases/nominativ.md",
    "a1/grammar/cases/akkusativ.md",
    "a1/grammar/other/nomen-genus-plural.md",
]
WORDS_30 = " ".join(["word"] * 30) + "."


def fixture(category: str) -> str:
    return (FIXTURES / f"{category}-article.md").read_text(encoding="utf-8")


def repository(root: Path) -> Path:
    (root / "open-language.yml").write_text(
        "language: German\nlanguage_code: de\n", encoding="utf-8"
    )
    for target in LINK_TARGETS:
        page = root / target
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("# Page\n", encoding="utf-8")
    return root


def report(root: Path, category: str, text: str):
    repository(root)
    page = root / PATHS[category]
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(text, encoding="utf-8")
    return validate_file(page, root)


def errors(root: Path, category: str, text: str) -> list[str]:
    return [m for lvl, m in report(root, category, text).items if lvl == "ERROR"]


@pytest.mark.parametrize("category", PATHS)
def test_fixture_passes(tmp_path, category):
    assert errors(tmp_path, category, fixture(category)) == []


LEAD = "The definite article is the German word for *the*, and it changes with the gender of the noun: **der**, **die** or **das**."
EXPLANATION = "Every German noun has one of three genders"
H1 = "# Definite Articles\n"
SECTION = "## When to use *der*, *die*, *das*"


def add_h2s(text: str, count: int) -> str:
    extra = "".join(f"## Topic number{chr(97 + i)}\n\nText.\n\n" for i in range(count))
    return text.replace(SECTION, extra + SECTION, 1)


GRAMMAR = {
    "short lead": (lambda s: s.replace(LEAD, "Short lead.", 1), "lead paragraph is 2"),
    "long lead": (
        lambda s: s.replace(LEAD, "der " + "word " * 55, 1),
        "lead paragraph is 56",
    ),
    "lead of three sentences": (
        lambda s: s.replace(LEAD, f"{LEAD} A second one here. A third one here.", 1),
        "lead paragraph is 3 sentences",
    ),
    "lead without a learner phrasing": (
        lambda s: s.replace(
            LEAD, "The small word before a noun shows which one is meant. " * 2, 1
        ),
        "none of the phrasings",
    ),
    "no explanation": (
        lambda s: s.replace(EXPLANATION, "**Examples:**\n\n" + EXPLANATION, 1),
        "explanation paragraph is 1",
    ),
    "long explanation": (
        lambda s: s.replace(EXPLANATION, "word " * 125 + EXPLANATION, 1),
        "(it has 40 to 120)",
    ),
    "long opening": (
        lambda s: s.replace(LEAD, "der " + "word " * 45 + ".", 1).replace(
            EXPLANATION, "word " * 90 + EXPLANATION, 1
        ),
        "words together",
    ),
    "something else before the first H2": (
        lambda s: s.replace("## The forms", "A third paragraph.\n\n## The forms", 1),
        "only a Prerequisites admonition",
    ),
    "Prerequisites before the lead": (
        lambda s: s.replace(
            H1, H1 + "\n:::{admonition} Prerequisites\n- [A](/a.md)\n:::\n", 1
        ),
        "first thing under the title",
    ),
    "Prerequisites in a section": (
        lambda s: s.replace(
            "## Summary",
            ":::{admonition} Prerequisites\n- [A](/a.md)\n:::\n\n## Summary",
            1,
        ),
        "Prerequisites go after",
    ),
    "two titles": (lambda s: s + "\n# Another\n", "exactly one H1"),
    "long title": (
        lambda s: s.replace(H1, "# The Definite Articles Of German Nouns\n", 1),
        "is 6 words",
    ),
    "number in the title": (
        lambda s: s.replace(H1, "# Definite Articles 2\n", 1),
        "has a number",
    ),
    "an H4": (
        lambda s: s.replace("## Summary", "#### Deep\n\n## Summary", 1),
        "only H1, H2 and H3",
    ),
    "eight H2": (lambda s: add_h2s(s, 2), "8 H2"),
    "seven H3": (
        lambda s: s.replace(
            SECTION,
            SECTION + "\n\n" + "".join("### Part\n\nText.\n\n" for _ in range(7)),
            1,
        ),
        "7 H3",
    ),
    "H3 in a closing section": (
        lambda s: s.replace("## Summary\n", "## Summary\n\n### Points\n", 1),
        "has no H3 there",
    ),
    "long heading": (
        lambda s: s.replace(
            SECTION, "## One two three four five six seven eight nine", 1
        ),
        "is 9 words",
    ),
    "number in a heading": (
        lambda s: s.replace(SECTION, "## The 3 articles", 1),
        "has a number",
    ),
    "closing punctuation": (
        lambda s: s.replace(SECTION, "## When to use them?", 1),
        "ends in punctuation",
    ),
    "heading addresses the reader": (
        lambda s: s.replace(SECTION, "## What your article does", 1),
        "addresses the reader",
    ),
    "heading repeats its parent": (
        lambda s: s.replace(SECTION, "## Definite articles", 1),
        "repeats the heading above it",
    ),
    "German word not in italics": (
        lambda s: s.replace(SECTION, "## When to use der", 1),
        "'der'",
    ),
    "six columns": (
        lambda s: s.replace(
            "## Summary", "| a | b | c | d | e | f |\n|-|-|-|-|-|-|\n\n## Summary", 1
        ),
        "6 columns",
    ),
    "German and English columns": (
        lambda s: s.replace(
            "## Summary", "| German | English |\n|-|-|\n| a | b |\n\n## Summary", 1
        ),
        "'English' is a column for the translation",
    ),
    "long sentence": (
        lambda s: s.replace(
            "## Summary", " ".join(["word"] * 26) + ".\n\n## Summary", 1
        ),
        "sentence of 26 words",
    ),
    "long paragraph": (
        lambda s: s.replace("## Summary", "One here. " * 6 + "\n\n## Summary", 1),
        "paragraph of 6 sentences",
    ),
    "long description": (
        lambda s: s.replace(
            'description: "A1 grammar: der, die, das.',
            f'description: "{"word " * 40}',
            1,
        ),
        "html_meta.description is",
    ),
    "one body section": (
        lambda s: (
            s[: s.index("## When to use")]
            + "\n"
            + s[s.index("## Accusative") :]
            .replace("## Accusative", "", 0)
            .split("## Accusative", 1)[0]
            + s[s.index("## Hear it") :]
        ),
        "at least 2 sections",
    ),
    "sections past the limit": (lambda s: add_h2s(s, 3), "6 'other sections'"),
    "summary before audio": (
        lambda s: (
            s.replace("## Summary", "## Temp", 1)
            .replace("## Hear it in practice", "## Summary", 1)
            .replace("## Temp", "## Hear it in practice", 1)
        ),
        "out of order",
    ),
    "section after related articles": (
        lambda s: s + "\n## More\n\nText.\n",
        "out of order",
    ),
    "audio section without a block": (
        lambda s: s.replace("## Summary", "## Temp", 1).replace(
            ":::{audio-examples}", ":::{note}", 1
        ),
        "needs >= 1 audio-examples",
    ),
    "empty related articles": (
        lambda s: s[: s.index("## Related articles")] + "## Related articles\n",
        "has no links",
    ),
    "prose in related articles": (
        lambda s: s.replace(
            "## Related articles\n\n", "## Related articles\n\nSome words.\n\n", 1
        ),
        "holds only links",
    ),
    "common mistakes elsewhere": (
        lambda s: s.replace(":::{admonition} Common mistakes", ":::{note}", 1),
        "Common mistakes",
    ),
    "four examples in a section": (
        lambda s: s.replace(
            "Sie liest {akk}`das` Buch.",
            "Wir nehmen {akk}`die` Tram.\n: We take the tram.\n\n"
            "Sie liest {akk}`das` Buch.",
            1,
        ),
        "4 inline examples",
    ),
    "on-this-page navigation removed": (
        lambda s: s.replace("---\n", "---\nhtml_theme.sidebar_secondary.remove:\n", 1),
        "shows on every article",
    ),
}


@pytest.mark.parametrize("case", GRAMMAR, ids=list(GRAMMAR))
def test_broken_grammar_article_is_red(tmp_path, case):
    breaker, expected = GRAMMAR[case]
    source = fixture("grammar")
    broken = breaker(source)
    assert broken != source, "the mutation did not change the fixture"
    found = errors(tmp_path, "grammar", broken)
    assert any(expected in msg for msg in found), found


HOW_TO = {
    "title opens on an -ing word": (
        lambda s: s.replace("# Greet someone", "# Greeting someone", 1),
        "write the verb in its base form",
    ),
    "title opens on no verb": (
        lambda s: s.replace("# Greet someone", "# The greetings", 1),
        "so it opens on a verb",
    ),
    "no When to use it": (
        lambda s: s.replace("## When to use it", "## Situations", 1),
        "the section '## When to use it'",
    ),
    "no Key phrases": (
        lambda s: s.replace("## Key phrases", "## Phrases", 1),
        "the section '## Key phrases'",
    ),
    "phrases not grouped": (
        lambda s: s.replace("### Saying hello\n", "", 1).replace(
            "### Saying goodbye\n", "", 1
        ),
        "under H3 group names",
    ),
    "H3 outside Key phrases": (
        lambda s: s.replace("## Formal or casual\n", "## Formal or casual\n\n### A\n"),
        "has no H3 there",
    ),
    "three columns under Key phrases": (
        lambda s: s.replace(
            "| Phrase | Notes |\n|---|---|\n",
            "| Phrase | Notes | Use |\n|---|---|---|\n",
            1,
        ),
        "3 columns under 'Key phrases'",
    ),
    "long culture note": (
        lambda s: s.replace(
            "Regional greetings such", f"{WORDS_30} {WORDS_30} {WORDS_30} Regional", 1
        ),
        "'Culture note' is",
    ),
    "culture note after the audio": (
        lambda s: s.replace(
            "## Summary", "## Culture note\n\nMore.\n\n## Summary", 1
        ).replace("## Culture note\n\nRegional", "Regional", 1),
        "out of order",
    ),
    "four other sections": (
        lambda s: s.replace(
            "## Formal or casual",
            "## One\n\nText.\n\n## Two\n\nText.\n\n## Three\n\nText.\n\n"
            "## Formal or casual",
            1,
        ),
        "4 'other sections'",
    ),
}
WRITING = {
    "no example": (
        lambda s: s.replace("## Example: Asking", "## Asking", 1),
        "not a section of a writing article",
    ),
    "lower case after the colon": (
        lambda s: s.replace("## Example: Asking", "## Example: asking", 1),
        "not a section of a writing article",
    ),
    "three examples": (
        lambda s: s.replace(
            "## Building blocks",
            "## Example: Two\n\nText.\n\n### Hear it in practice\n\n"
            "## Example: Three\n\nText.\n\n### Hear it in practice\n\n"
            "## Building blocks",
            1,
        ),
        "3 'Example: <Situation>' sections",
    ),
    "no building blocks": (
        lambda s: s.replace("## Building blocks", "## Phrases", 1),
        "the section '## Building blocks'",
    ),
    "no H3 audio section": (
        lambda s: s.replace("### Hear it in practice", "### Listen", 1),
        "has no H3 audio section",
    ),
    "long note": (
        lambda s: s.replace(
            "The request comes first, politely",
            f"{WORDS_30} {WORDS_30} {WORDS_30} The request",
            1,
        ),
        "the note in",
    ),
    "H3 outside an example": (
        lambda s: s.replace("## Summary\n", "## Summary\n\n### Points\n", 1),
        "has no H3 there",
    ),
    "H2 audio section": (
        lambda s: s.replace(
            "## Summary", "## Hear it in practice\n\nText.\n\n## Summary", 1
        ),
        "not a section of a writing article",
    ),
}
VOCABULARY = {
    "no word section": (
        lambda s: s.replace("## The words", "## Words", 1),
        "the section '## The words'",
    ),
    "English column": (
        lambda s: s.replace("| Word | Notes |", "| German | English |", 1),
        "'English' is a column for the translation",
    ),
    "three columns": (
        lambda s: s.replace(
            "| Word | Notes |\n|---|---|", "| Word | Notes | Use |\n|---|---|---|", 1
        ),
        "the word table has two columns",
    ),
    "second table": (
        lambda s: s.replace(
            "## Words that look alike",
            "| Word | Notes |\n|---|---|\n\n## Words that look alike",
            1,
        ).replace(
            "| {stack}`schwimmen \\| to swim` | A verb. |\n",
            "| {stack}`schwimmen \\| to swim` | A verb. |\n\nText.\n",
            1,
        ),
        "holds one table",
    ),
    "word without the stack role": (
        lambda s: s.replace("{stack}`der Strand \\| beach`", "der Strand, beach", 1),
        "is not written with the stack role",
    ),
    "too few words": (
        lambda s: s.replace("| {stack}`schwimmen \\| to swim` | A verb. |\n", "", 1),
        "9 words",
    ),
    "three other sections": (
        lambda s: s.replace(
            "## Words that look alike",
            "## One\n\nText.\n\n## Two\n\nText.\n\n## Words that look alike",
            1,
        ),
        "3 'other sections'",
    ),
    "H3 anywhere": (
        lambda s: s.replace("## Summary\n", "## Summary\n\n### Points\n", 1),
        "has no H3 there",
    ),
    "empty first header cell": (
        lambda s: s.replace("| Word | Notes |", "|  | Notes |", 1),
        "first header cell is empty",
    ),
}


@pytest.mark.parametrize(
    ("category", "case"),
    [
        *(("how-to", case) for case in HOW_TO),
        *(("writing", case) for case in WRITING),
        *(("vocabulary", case) for case in VOCABULARY),
    ],
    ids=[*HOW_TO, *WRITING, *VOCABULARY],
)
def test_broken_article_is_red(tmp_path, category, case):
    breaker, expected = {
        "how-to": HOW_TO,
        "writing": WRITING,
        "vocabulary": VOCABULARY,
    }[category][case]
    source = fixture(category)
    broken = breaker(source)
    assert broken != source, "the mutation did not change the fixture"
    found = errors(tmp_path, category, broken)
    assert any(expected in msg for msg in found), found


@pytest.mark.parametrize("title", ["Bring a friend", "Introduce yourself"])
def test_a_how_to_title_may_open_on_any_verb(tmp_path, title):
    text = fixture("how-to").replace("# Greet someone", f"# {title}", 1)
    assert errors(tmp_path, "how-to", text) == []


def test_a_grammar_title_need_not_open_on_a_verb(tmp_path):
    text = fixture("grammar")
    assert not text.startswith("# Greet")
    assert not any("opens on" in msg for msg in errors(tmp_path, "grammar", text))


TRACK_BLOCK = """:::{{audio-examples}}
:track: a1/{category}/{track}
:duplicate:
:::
"""


def tracks_section(category: str, *parts: str) -> str:
    """The fixture with ``parts`` added after its audio block.

    A part beginning with ``#`` is a heading and any other names a track, except
    ``first``, which puts ``### First`` above the fixture's own block.
    """
    text = fixture(category)
    added = [
        part
        if part.startswith("#")
        else TRACK_BLOCK.format(category=category, track=part)
        for part in parts
        if part != "first"
    ]
    if "first" in parts:
        text = text.replace(
            "## Hear it in practice\n", "## Hear it in practice\n\n### First\n", 1
        )
    return text.replace("\n## Summary", "\n" + "\n".join(added) + "\n## Summary", 1)


@pytest.mark.parametrize("category", ["grammar", "how-to"])
def test_each_of_several_tracks_may_have_its_own_h3(tmp_path, category):
    text = tracks_section(category, "first", "### Second", "other")
    assert errors(tmp_path, category, text) == []


@pytest.mark.parametrize("category", ["grammar", "how-to"])
def test_several_tracks_may_stand_without_h3s(tmp_path, category):
    assert errors(tmp_path, category, tracks_section(category, "other")) == []


@pytest.mark.parametrize("category", ["grammar", "how-to"])
@pytest.mark.parametrize(
    ("parts", "expected"),
    [
        (("first",), "an H3 there names one of several audio blocks"),
        (("### Second", "other"), "has no H3: when one block has its own H3"),
        (("first", "other", "### Third", "more"), "holds 2 audio blocks"),
        (("first", "### Second"), "an H3 there names one of several audio blocks"),
        (("first", "other", "### Third"), "holds 0 audio blocks"),
    ],
    ids=["one block", "a block with no H3", "two blocks", "only one", "an empty H3"],
)
def test_a_track_h3_out_of_place_is_red(tmp_path, category, parts, expected):
    found = errors(tmp_path, category, tracks_section(category, *parts))
    assert any(expected in msg for msg in found), found


def test_track_h3s_count_towards_the_limit(tmp_path):
    parts = ["first"]
    for number in range(4):
        parts += [f"### Track {'abcd'[number]}", f"track-{number}"]
    found = errors(tmp_path, "how-to", tracks_section("how-to", *parts))
    assert any("7 H3" in msg for msg in found), found


def test_a_vocabulary_article_has_no_h3_under_hear_it_in_practice(tmp_path):
    found = errors(
        tmp_path, "vocabulary", tracks_section("vocabulary", "first", "### B", "other")
    )
    assert any("has no H3 there" in msg for msg in found), found


def test_a_table_of_forms_stays_within_its_limit_only_in_grammar(tmp_path):
    forms = "| | A | B | C | D |\n|-|-|-|-|-|\n| x | 1 | 2 | 3 | 4 |\n\n## Summary"
    assert not any(
        "columns" in msg
        for msg in errors(
            tmp_path, "grammar", fixture("grammar").replace("## Summary", forms, 1)
        )
    )
    found = errors(
        tmp_path, "how-to", fixture("how-to").replace("## Summary", forms, 1)
    )
    assert any("5 columns (maximum 3)" in msg for msg in found), found


def test_a_heading_may_quote_the_word_you(tmp_path):
    quoted = fixture("grammar").replace(SECTION, '## Two ways to say "you"', 1)
    assert not any(
        "addresses the reader" in msg for msg in errors(tmp_path, "grammar", quoted)
    )


def test_a_long_average_warns_and_does_not_fail(tmp_path):
    sentence = " ".join(["word"] * 24) + ". "
    long_prose = fixture("how-to").replace(
        "Strangers and customers get the formal greeting.", sentence * 5, 1
    )
    items = report(tmp_path, "how-to", long_prose).items
    assert any(lvl == "WARN" and "words a sentence" in m for lvl, m in items)
    assert not any(lvl == "ERROR" and "words a sentence" in m for lvl, m in items)


def with_table(category: str, header: str) -> str:
    """The category's fixture with a table of that header before its last section."""
    cells = header.count("|") - 1
    rows = f"{header}\n|{'-|' * cells}\n|{' a |' * cells}\n\n"
    last = re.findall(r"^## .+$", fixture(category), re.M)[-1]
    return fixture(category).replace(last, rows + last, 1)


@pytest.mark.parametrize("category", PATHS)
@pytest.mark.parametrize(
    ("header", "cell"),
    [
        ("| Formal | Informal | English |", "English"),
        ("| Word | Meaning | Example |", "Meaning"),
        ("| Nominative | Accusative | English |", "English"),
        ("| Preposition | Core meaning | Example |", "Core meaning"),
        ("| English meaning | Example |", "English meaning"),
        ("| Translation | Notes |", "Translation"),
        ("| Verb | **MEANING** |", "MEANING"),
    ],
)
def test_a_translation_column_is_red_in_any_category(tmp_path, category, header, cell):
    found = errors(tmp_path, category, with_table(category, header))
    assert any(
        f"'{cell}' is a column for the translation" in msg
        and "stack role" in msg
        and "Notes" in msg
        for msg in found
    ), found


def test_an_unnamed_column_is_red(tmp_path):
    table = with_table("grammar", "| Singular | | Plural | |")
    found = errors(tmp_path, "grammar", table)
    assert any("empty header cell" in msg and "stack role" in msg for msg in found)


@pytest.mark.parametrize(
    "header",
    [
        "| | Masculine | Feminine | Neuter | Plural |",
        "| Person | Ending | Example |",
        "| Englishman | Meaningful |",
    ],
)
def test_a_table_with_no_translation_column_passes(tmp_path, header):
    found = errors(tmp_path, "grammar", with_table("grammar", header))
    assert not any(
        "column for the translation" in msg or "empty header cell" in msg
        for msg in found
    ), found


def test_a_language_adds_its_own_translation_headers(tmp_path):
    table = with_table("grammar", "| Verb | Bedeutung | Beispiel |")
    assert not any(
        "column for the translation" in msg
        for msg in errors(tmp_path, "grammar", table)
    )
    (tmp_path / "open-language.yml").write_text(
        "language: German\ntranslation_headers:\n  - Bedeutung\n", encoding="utf-8"
    )
    page = tmp_path / PATHS["grammar"]
    assert any(
        "'Bedeutung' is a column for the translation" in msg
        for _, msg in validate_file(page, tmp_path).items
    )


def test_a_table_in_a_fence_is_not_read(tmp_path):
    fenced = fixture("grammar").replace(
        "## Summary",
        "```text\n| German | English |\n|-|-|\n```\n\n## Summary",
        1,
    )
    assert errors(tmp_path, "grammar", fenced) == []


@pytest.mark.parametrize("category", PATHS)
def test_a_template_has_the_sections_of_its_category(category):
    text = (TEMPLATES_DIR / f"{category}-article.md").read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    named = [
        part["heading"]
        for part in SPECS["types"][category]["sections"]
        if "heading" in part
    ]
    in_template = re.findall(r"^## (.+)$", text, re.M)
    assert [title for title in in_template if title in named] == named


class TestReading:
    def test_an_abbreviation_does_not_end_a_sentence(self):
        assert len(sentences("Use a word, e.g. Hund, here. Then stop.")) == 2

    def test_a_quotation_closes_its_sentence(self):
        assert len(sentences('He said "Hallo." Then he left.')) == 2

    def test_a_translation_is_not_counted_as_words(self):
        assert plain("{stack}`Guten Tag | Good day`") == "Guten Tag"

    def test_a_term_counts_as_what_the_reader_sees(self):
        assert plain("{term}`nouns <noun>` and [a link](/a.md)") == "nouns and a link"

    def test_an_arrow_is_not_a_word(self):
        assert word_count("Wrong → right") == 2

    def test_a_page_splits_at_its_h2s(self):
        opening, found = sections(parse("# T\n\nA.\n\n## B\n\nC.\n\n### D\n"))
        assert [b.text for b in opening] == ["A."]
        assert [s.title for s in found] == ["B"]


SIDEBAR = "---\nhtml_theme.sidebar_secondary.remove:\n---\n"


@pytest.fixture
def pages(tmp_path, write_menu):
    root = repository(write_menu(tmp_path))
    return root


def level_errors(root: Path, breaker) -> list[str]:
    page = root / "a1/index.md"
    page.write_text(breaker(page.read_text(encoding="utf-8")), encoding="utf-8")
    return [m for lvl, m in validate_file(page, root).items if lvl == "ERROR"]


def introduction_errors(root: Path, breaker) -> list[str]:
    page = root / "index.md"
    page.write_text(breaker(page.read_text(encoding="utf-8")), encoding="utf-8")
    return [m for lvl, m in validate_file(page, root).items if lvl == "ERROR"]


def test_the_level_page_passes(pages):
    assert level_errors(pages, lambda s: s) == []


def test_the_introduction_passes(pages):
    assert introduction_errors(pages, lambda s: s) == []


LEVEL_PAGE = {
    "title with more than the level": (
        lambda s: s.replace("# A1", "# A1 German", 1),
        "bare level name",
    ),
    "no lead": (
        lambda s: s.replace("The first level of the course.\n\n", "", 1),
        "lead paragraph",
    ),
    "long lead": (
        lambda s: s.replace("The first level", WORDS_30 + " " + WORDS_30, 1),
        "lead paragraph is",
    ),
    "sections swapped": (
        lambda s: (
            s.replace("What learners know", "TEMP")
            .replace("What learners can do", "What learners know")
            .replace("TEMP", "What learners can do")
        ),
        "in that order",
    ),
    "two things known": (
        lambda s: s.replace("- Word order.\n", "", 1),
        "'What learners know' has 2 bullets",
    ),
    "seven things to do": (
        lambda s: s.replace("- Spell a name.\n", "- Spell.\n" * 4, 1),
        "'What learners can do' has 7 bullets",
    ),
    "long bullet": (
        lambda s: s.replace("- Word order.", "- " + " ".join(["word"] * 16), 1),
        "is 16 words",
    ),
    "bullet not a base-form verb": (
        lambda s: s.replace("- Order food.", "- Ordering food.", 1),
        "does not start with a verb",
    ),
    "a verb that merely ends like one": (
        lambda s: s.replace("- Order food.", "- Bring food.", 1),
        None,
    ),
    "third person verb": (
        lambda s: s.replace("- Order food.", "- Orders food.", 1),
        "does not start with a verb",
    ),
    "overview too long": (
        lambda s: (
            s.replace(
                "The first level of the course.", " ".join(["word"] * 39) + ".", 1
            )
            .replace(
                "- The articles.\n- The present tense.\n- Word order.",
                "\n".join("- " + " ".join(["word"] * 15) for _ in range(5)),
                1,
            )
            .replace(
                "- Greet someone.\n- Order food.\n- Ask the way.\n- Spell a name.",
                "\n".join("- Say " + " ".join(["word"] * 14) for _ in range(6)),
                1,
            )
        ),
        "words together",
    ),
    "toctree after the reading": (
        lambda s: (
            s[: s.index("```{toctree}")]
            + s[s.index("## Additional reading") :]
            + "\n"
            + s[s.index("```{toctree}") : s.index("## Additional reading")]
        ),
        "the toctree comes after 2",
    ),
    "no additional reading": (
        lambda s: s[: s.index("## Additional reading")],
        "in that order",
    ),
    "internal link in the reading": (
        lambda s: s.replace("https://example.org/list", "a1/grammar/index.md", 1),
        "external links only",
    ),
}
INTRODUCTION_PAGE = {
    "long lead": (
        lambda s: s.replace("A free, open coursebook.", " ".join(["word"] * 61), 1),
        "lead is 61 words",
    ),
    "section in the wrong place": (
        lambda s: (
            s.replace("## Levels", "## TEMP")
            .replace("## Categories", "## Levels")
            .replace("## TEMP", "## Categories")
        ),
        "in that order",
    ),
    "extra section": (
        lambda s: s.replace("## Levels", "## News\n\nText.\n\n## Levels", 1),
        "and no others",
    ),
    "long how it works": (
        lambda s: s.replace("Any page can be read first.", WORDS_30 * 3, 1),
        "'How the course works' is",
    ),
    "a level that does not exist": (
        lambda s: s.replace(
            "- [A1](a1/index.md): the first days.\n",
            "- [A1](a1/index.md): the first days.\n- [A2](a2/index.md): next.\n",
            1,
        ),
        "'Levels' has 2 bullets",
    ),
    "a level link somewhere else": (
        lambda s: s.replace(
            "[A1](a1/index.md): the first", "[A1](a2/index.md): the", 1
        ),
        "each linking to its level page",
    ),
    "long level bullet": (
        lambda s: s.replace("the first days.", " ".join(["word"] * 20), 1),
        "'Levels' is 21 words",
    ),
    "categories out of order": (
        lambda s: s.replace(
            "[How to](a1/how-to/index.md)", "[X](a1/grammar/index.md)", 1
        ),
        "'Categories' links, in order",
    ),
    "three categories": (
        lambda s: s.replace("- [Writing](a1/writing/index.md): model texts.\n", "", 1),
        "'Categories' has 3 bullets",
    ),
    "one place to start": (
        lambda s: s.replace("- New to the language: [A1](a1/index.md).\n", "", 1),
        "'Where to start' has 1 bullets",
    ),
    "a place to start without a link": (
        lambda s: s.replace("- New to the language: [A1](a1/index.md).", "- New.", 1),
        "has a link",
    ),
    "glossary is not last": (
        lambda s: s.replace("[the glossary](terminology.md)", "[A1](a1/index.md)", 1),
        "links to the glossary",
    ),
    "page too long": (
        lambda s: s.replace("## Levels", (WORDS_30 + "\n\n") * 13 + "## Levels", 1),
        "the page is",
    ),
    "toctree before the sections": (
        lambda s: (
            s[: s.index("## How the course works")]
            + s[s.index("```{toctree}") :]
            + "\n"
            + s[s.index("## How the course works") : s.index("```{toctree}")]
        ),
        "the toctree comes",
    ),
}


@pytest.mark.parametrize("case", LEVEL_PAGE, ids=list(LEVEL_PAGE))
def test_broken_level_page_is_red(pages, case):
    breaker, expected = LEVEL_PAGE[case]
    found = level_errors(pages, breaker)
    if expected is None:
        assert found == []
    else:
        assert any(expected in msg for msg in found), found


@pytest.mark.parametrize("case", INTRODUCTION_PAGE, ids=list(INTRODUCTION_PAGE))
def test_broken_introduction_is_red(pages, case):
    breaker, expected = INTRODUCTION_PAGE[case]
    found = introduction_errors(pages, breaker)
    assert any(expected in msg for msg in found), found


def category_index_errors(root: Path, text: str) -> list[str]:
    page = root / "a1/grammar/index.md"
    page.write_text(text, encoding="utf-8")
    return [m for lvl, m in validate_file(page, root).items if lvl == "ERROR"]


def test_a_category_index_opens_with_one_to_three_sentences(pages):
    index = (pages / "a1/grammar/index.md").read_text(encoding="utf-8")
    assert category_index_errors(pages, index) == []
    found = category_index_errors(
        pages, index.replace("The grammar articles.\n\n", "", 1)
    )
    assert any("opens with 0 sentences" in msg for msg in found), found
    found = category_index_errors(
        pages, index.replace("The grammar articles.", "One. Two. Three. Four.", 1)
    )
    assert any("opens with 4 sentences" in msg for msg in found), found


def test_an_index_page_has_no_on_this_page_navigation(pages):
    index = (pages / "a1/grammar/index.md").read_text(encoding="utf-8")
    found = category_index_errors(pages, index.replace(SIDEBAR, "", 1))
    assert any("no on-this-page navigation" in msg for msg in found), found
