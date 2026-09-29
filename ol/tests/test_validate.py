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


BROKEN_ARTICLES = {
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
