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
ALBUM = "title: Part 1\nvoice: max\ntracks:\n- bestimmter-artikel\n"
LINK_TARGETS = [
    "a1/grammar/articles/unbestimmter-artikel.md",
    "a1/grammar/articles/negativartikel.md",
    "a1/grammar/cases/nominativ.md",
    "a1/grammar/cases/akkusativ.md",
    "a1/grammar/other/nomen-genus-plural.md",
]
H1 = "# Definite Articles\n"


def errors(tmp_path: Path, text: str, album: str = ALBUM) -> list[str]:
    for target in LINK_TARGETS:
        page = tmp_path / "docs" / target
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("# Page\n", encoding="utf-8")
    article = tmp_path / ARTICLE
    article.write_text(text, encoding="utf-8")
    album_dir = tmp_path / "albums/a1/grammar/part-1"
    album_dir.mkdir(parents=True)
    (album_dir / "album.yml").write_text(album, encoding="utf-8")
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
    pattern = r"(:album: a1/grammar/part-1\n(?:.*\n)*?\n)(\S[^\n]*)"
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
    "markup in audio example": (_break_first_audio_line, "banned char"),
    "no album backlink": (
        lambda s: s.replace(":album: a1/grammar/part-1\n", "", 1),
        ":album: backlink",
    ),
}


@pytest.mark.parametrize("case", BROKEN_ARTICLES, ids=list(BROKEN_ARTICLES))
def test_broken_article_is_red(tmp_path, source, case):
    breaker, expected = BROKEN_ARTICLES[case]
    broken = breaker(source)
    assert broken != source, "the mutation did not change the fixture"
    found = errors(tmp_path, broken)
    assert any(expected in msg for msg in found), found


def test_track_missing_from_album_is_red(tmp_path, source):
    found = errors(
        tmp_path, source, album="title: Part 1\nvoice: max\ntracks:\n- other\n"
    )
    assert any("not listed in" in msg for msg in found), found


def test_album_storing_level_is_red(tmp_path, source):
    album = "title: Part 1\nvoice: max\nlevel: a1\ntracks:\n- bestimmter-artikel\n"
    found = errors(tmp_path, source, album=album)
    assert any("must not store 'level'" in msg for msg in found), found


def test_published_title_keeps_its_dash(tmp_path, source):
    published = source.replace(
        ":title-en: The definite article",
        ":title-en: Articles - Definite\n:spotify: https://open.spotify.com/track/x",
        1,
    )
    assert errors(tmp_path, published) == []


def test_stock_phrase_in_an_example_is_not_prose(tmp_path, source):
    glossed = source.replace(": The harbour is big.", ": The harbour is robust.", 1)
    assert errors(tmp_path, glossed) == []


def test_workspace_without_albums_skips_album_wiring(tmp_path, source):
    for target in LINK_TARGETS:
        page = tmp_path / "docs" / target
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("# Page\n", encoding="utf-8")
    article = tmp_path / ARTICLE
    article.write_text(source, encoding="utf-8")
    report = validate_file(article, tmp_path)
    assert [msg for lvl, msg in report.items if lvl == "ERROR"] == []


def test_short_model_text_is_red(tmp_path):
    article = tmp_path / "docs/a1/writing/postcard.md"
    article.parent.mkdir(parents=True)
    filler = "Writing a postcard is a small, friendly task. " * 6
    article.write_text(
        f"# A Postcard\n\n{filler}\n\n"
        ":::{audio-examples}\n:album: a1/writing/part-1\n:title: Eine Postkarte\n"
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
