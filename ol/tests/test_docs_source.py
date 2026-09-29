"""Tests for ol.docs_source — the ADR-0006 docs-as-source extractor."""

from pathlib import Path

import pytest

from ol.docs_source import (
    DocsFormatError,
    block_to_track_data,
    iter_file_blocks,
    parse_example_pairs,
    parse_option_lines,
    rewrite_block_examples,
    scan_docs,
)

GOOD_BLOCK = """\
# The Dative Case

Some prose.

## Hear it in practice

:::{audio-examples}
:album: a1/grammar/part-1
:title: Der Dativ
:title-en: The dative case

Ich fahre mit dem Bus.
: I go by bus.

Sie kommt aus der Türkei.
: She comes from Turkey.
:::

## Summary
"""


# ---------------------------------------------------------------------------
# Body grammar
# ---------------------------------------------------------------------------


def test_parse_example_pairs_happy_path():
    pairs = parse_example_pairs(
        [
            "Ich fahre mit dem Bus.",
            ": I go by bus.",
            "",
            "Er sagt: Hallo.",
            ": He says hello.",
        ],
        "test",
    )
    assert pairs == [
        ("Ich fahre mit dem Bus.", "I go by bus."),
        ("Er sagt: Hallo.", "He says hello."),
    ]


def test_parse_example_pairs_without_blank_separators():
    pairs = parse_example_pairs(["Eins.", ": One.", "Zwei.", ": Two."], "test")
    assert len(pairs) == 2


@pytest.mark.parametrize(
    "lines,fragment",
    [
        (["Ich fahre.", "Ich gehe.", ": I go."], "two consecutive native lines"),
        (["Ich fahre."], "no ': translation' line"),
        ([": I go by bus."], "no native line above"),
        (["Ich fahre.", ":"], "empty translation"),
        (["Der {dativ}`Hund`.", ": The dog."], "not allowed"),
        (["Der `Hund`.", ": The dog."], "not allowed"),
    ],
)
def test_parse_example_pairs_rejects_bad_grammar(lines, fragment):
    with pytest.raises(DocsFormatError, match=fragment):
        parse_example_pairs(lines, "test")


def test_parse_option_lines_splits_options_from_body():
    options, start = parse_option_lines(
        [":album: a1/grammar/part-1", ":title: Der Dativ", "", "Ich fahre."],
        "test",
    )
    assert options == {"album": "a1/grammar/part-1", "title": "Der Dativ"}
    assert start == 2


def test_parse_option_lines_rejects_unknown_key():
    with pytest.raises(DocsFormatError, match="unknown option"):
        parse_option_lines([":armadillo: yes"], "test")


def test_parse_option_lines_strips_angle_brackets():
    options, _ = parse_option_lines([":spotify: <https://x.example>"], "test")
    assert options["spotify"] == "https://x.example"


# ---------------------------------------------------------------------------
# Block location
# ---------------------------------------------------------------------------


def test_iter_file_blocks_finds_block_with_line_spans(tmp_path: Path):
    doc = tmp_path / "dativ.md"
    doc.write_text(GOOD_BLOCK, encoding="utf-8")
    blocks = iter_file_blocks(doc, GOOD_BLOCK)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.album == "a1/grammar/part-1"
    assert block.name("dativ") == "dativ"
    assert block.pairs[1] == ("Sie kommt aus der Türkei.", "She comes from Turkey.")
    lines = GOOD_BLOCK.splitlines()
    assert lines[block.open_line] == ":::{audio-examples}"
    assert lines[block.close_line] == ":::"


def test_iter_file_blocks_skips_legacy_pointer(tmp_path: Path):
    text = ":::{audio-examples}\n:album: a1/grammar/part-1\n:track: dativ.yml\n:::\n"
    doc = tmp_path / "dativ.md"
    doc.write_text(text, encoding="utf-8")
    (block,) = iter_file_blocks(doc, text)
    assert block.is_legacy_pointer
    assert block.pairs == []


def test_iter_file_blocks_ignores_fences_inside_code_blocks(tmp_path: Path):
    text = (
        "Example of the syntax:\n\n```\n:::{audio-examples}\n:album: fake\n:::\n```\n"
    )
    doc = tmp_path / "guide.md"
    doc.write_text(text, encoding="utf-8")
    assert iter_file_blocks(doc, text) == []


def test_iter_file_blocks_requires_album_and_title(tmp_path: Path):
    text = ":::{audio-examples}\n:title: X\n\nEins.\n: One.\n:::\n"
    doc = tmp_path / "x.md"
    doc.write_text(text, encoding="utf-8")
    with pytest.raises(DocsFormatError, match="':album:'"):
        iter_file_blocks(doc, text)


# ---------------------------------------------------------------------------
# Scanning + shaping
# ---------------------------------------------------------------------------


def _write_docs_tree(root: Path) -> Path:
    docs = root / "docs"
    (docs / "a1").mkdir(parents=True)
    (docs / "a1" / "dativ.md").write_text(GOOD_BLOCK, encoding="utf-8")
    (docs / "a1" / "verben.md").write_text(
        ":::{audio-examples}\n"
        ":album: a1/grammar/part-2\n"
        ":name: verben-extra\n"
        ":title: Verben\n"
        ":title-en: Verbs\n"
        ":voice: sophie\n"
        ":spotify: https://open.spotify.com/album/x\n"
        "\n"
        "Ich lerne.\n"
        ": I learn.\n"
        ":::\n",
        encoding="utf-8",
    )
    (docs / "_build").mkdir()
    (docs / "_build" / "stale.md").write_text(GOOD_BLOCK, encoding="utf-8")
    return docs


def test_scan_docs_indexes_by_album_and_name(tmp_path: Path):
    docs = _write_docs_tree(tmp_path)
    index = scan_docs(docs)
    assert set(index) == {
        ("a1/grammar/part-1", "dativ"),
        ("a1/grammar/part-2", "verben-extra"),
    }


def test_scan_docs_rejects_duplicates(tmp_path: Path):
    docs = _write_docs_tree(tmp_path)
    (docs / "a1" / "copy.md").write_text(
        GOOD_BLOCK.replace(
            ":::{audio-examples}", ":::{audio-examples}\n:name: dativ", 1
        ),
        encoding="utf-8",
    )
    with pytest.raises(DocsFormatError, match="duplicate track"):
        scan_docs(docs)


def test_block_to_track_data_matches_track_yml_shape(tmp_path: Path):
    docs = _write_docs_tree(tmp_path)
    index = scan_docs(docs)
    data = block_to_track_data(index[("a1/grammar/part-2", "verben-extra")], "de")
    assert data["title"] == {"de": "Verben", "en": "Verbs"}
    assert data["voice"] == "sophie"
    assert data["streaming"] == {"spotify": "https://open.spotify.com/album/x"}
    assert data["examples"] == [{"de": "Ich lerne.", "en": "I learn."}]
    assert data["_docs_source"]["path"].endswith("verben.md")


def test_block_to_track_data_title_en_falls_back_to_native(tmp_path: Path):
    text = (
        ":::{audio-examples}\n:album: a1/g/x\n:title: Der Dativ\n\nEins.\n: One.\n:::\n"
    )
    doc = tmp_path / "x.md"
    doc.write_text(text, encoding="utf-8")
    (block,) = iter_file_blocks(doc, text)
    data = block_to_track_data(block, "de")
    assert data["title"] == {"de": "Der Dativ", "en": "Der Dativ"}


# ---------------------------------------------------------------------------
# Trim rewrite
# ---------------------------------------------------------------------------


def test_rewrite_block_examples_trims_body_and_nothing_else(tmp_path: Path):
    doc = tmp_path / "dativ.md"
    doc.write_text(GOOD_BLOCK, encoding="utf-8")
    rewrite_block_examples(
        doc,
        album="a1/grammar/part-1",
        name="dativ",
        kept_pairs=[("Ich fahre mit dem Bus.", "I go by bus.")],
    )
    text = doc.read_text(encoding="utf-8")
    assert "Sie kommt aus der Türkei." not in text
    assert "Ich fahre mit dem Bus.\n: I go by bus.\n:::" in text
    # Everything outside the block is untouched.
    assert text.startswith("# The Dative Case")
    assert text.rstrip().endswith("## Summary")
    assert ":title-en: The dative case" in text
    # The rewritten block still parses.
    (block,) = iter_file_blocks(doc, text)
    assert block.pairs == [("Ich fahre mit dem Bus.", "I go by bus.")]


def test_rewrite_block_examples_unknown_name_raises(tmp_path: Path):
    doc = tmp_path / "dativ.md"
    doc.write_text(GOOD_BLOCK, encoding="utf-8")
    with pytest.raises(DocsFormatError, match="no audio-examples block"):
        rewrite_block_examples(
            doc, album="a1/grammar/part-1", name="nope", kept_pairs=[]
        )


# ---------------------------------------------------------------------------
# Multiline mode (writing model texts)
# ---------------------------------------------------------------------------

MULTILINE_BLOCK = """\
# Writing: A Formal Email

:::{audio-examples}
:album: a1/writing/part-1
:title: E-Mail an die Chefin
:title-en: An email to your boss
:multiline:

Betreff: Urlaub im August.
Sehr geehrte Frau Weber,
ich möchte gern Urlaub nehmen.
Mit freundlichen Grüßen,
Anna Kowalska
: Subject: holiday in August.
: Dear Ms Weber,
: I would like to take holiday.
: With kind regards,
: Anna Kowalska
:::
"""


def test_parse_multiline_pairs_groups_by_blank_line():
    from ol.docs_source import parse_example_pairs_multiline

    pairs = parse_example_pairs_multiline(
        [
            "Zeile eins.",
            "Zeile zwei.",
            ": Line one.",
            ": Line two.",
            "",
            "Kurz.",
            ": Short.",
        ],
        "test",
    )
    assert pairs == [
        ("Zeile eins.\nZeile zwei.", "Line one.\nLine two."),
        ("Kurz.", "Short."),
    ]


def test_parse_multiline_rejects_native_after_translation():
    from ol.docs_source import parse_example_pairs_multiline

    with pytest.raises(DocsFormatError, match="after translation"):
        parse_example_pairs_multiline(["Eins.", ": One.", "Zwei."], "test")


def test_parse_multiline_rejects_group_without_translation():
    from ol.docs_source import parse_example_pairs_multiline

    with pytest.raises(DocsFormatError, match="no ': translation' lines"):
        parse_example_pairs_multiline(["Eins.", "", "Zwei.", ": Two."], "test")


def test_multiline_block_roundtrip_and_trim(tmp_path: Path):
    doc = tmp_path / "email-formal-1.md"
    doc.write_text(MULTILINE_BLOCK, encoding="utf-8")
    (block,) = iter_file_blocks(doc, MULTILINE_BLOCK)
    assert len(block.pairs) == 1
    native, translation = block.pairs[0]
    assert native.startswith("Betreff: Urlaub im August.\nSehr geehrte Frau Weber,")
    assert translation.endswith("Anna Kowalska")

    data = block_to_track_data(block, "de")
    assert data["examples"][0]["de"].count("\n") == 4

    # Trim keeps the pair and reproduces the exact multi-line body.
    rewrite_block_examples(
        doc, album="a1/writing/part-1", name="email-formal-1", kept_pairs=block.pairs
    )
    text = doc.read_text(encoding="utf-8")
    (reparsed,) = iter_file_blocks(doc, text)
    assert reparsed.pairs == block.pairs
    assert ":multiline:" in text
