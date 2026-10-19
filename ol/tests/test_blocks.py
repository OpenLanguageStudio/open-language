"""The block form the app reads, and the refusals it reports."""

from __future__ import annotations

from pathlib import Path

import pytest

from ol.blocks import (
    Block,
    BlockCollection,
    BlockFormatError,
    BlockReader,
    Example,
    Refusal,
    Sample,
    load_samples,
)

PAGE = "a2/grammar/nebensatz-mit-weil"
BODY = [
    "Ich bleibe zu Hause, weil ich krank bin.",
    ": I am staying at home because I am ill.",
]


def read(options: dict, body: list[str] = BODY, page: str = PAGE) -> Block:
    return BlockReader().read(page, options, body, line=3)


def codes(blocks: list[Block]) -> set[str]:
    return {refusal.code for refusal in BlockCollection(blocks).refusals()}


class TestBlockReader:
    def test_a_block_gives_everything_it_reads(self):
        block = read(
            {
                "track": "a2/grammar/nebensatz-mit-weil",
                "title": "Nebensatz mit weil",
                "title-en": "Subordinate clauses with weil",
                "tags": "nebensatz, konjunktionen",
            }
        )
        assert block == Block(
            page=PAGE,
            line=3,
            address="a2/grammar/nebensatz-mit-weil",
            title="Nebensatz mit weil",
            title_en="Subordinate clauses with weil",
            tags=("nebensatz", "konjunktionen"),
            examples=(
                Example(
                    "Ich bleibe zu Hause, weil ich krank bin.",
                    "I am staying at home because I am ill.",
                ),
            ),
            multiline=False,
            duplicate=False,
            refusals=(),
        )

    def test_the_address_splits_into_level_category_and_name(self):
        block = read({"track": "a2/grammar/weil"})
        assert (block.level, block.category, block.name) == ("a2", "grammar", "weil")

    def test_a_level_and_a_category_take_the_pages_name(self):
        block = read({"track": "a2/grammar"}, page="a2/grammar/dass")
        assert block.address == "a2/grammar/dass"

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "a2",
            "a2/grammar/weil/extra",
            "a2/grammar/we.il",
            "a2/grammar/Weil",
            "A2/grammar/weil",
            "a2/Grammar/weil",
        ],
    )
    def test_an_address_in_another_shape_is_bad(self, value):
        block = read({"track": value})
        assert (block.address, block.refusals) == (None, ("bad_address",))

    def test_a_block_with_no_track_is_a_bad_address(self):
        assert read({"title": "Weil"}).refusals == ("bad_address",)

    def test_a_blank_title_reads_as_no_title(self):
        block = read({"track": "a2/grammar/weil", "title": " ", "title-en": ""})
        assert (block.title, block.title_en) == (None, None)

    @pytest.mark.parametrize(
        "option", ["album", "name", "voice", "spotify", "youtube-music"]
    )
    def test_a_retired_option_is_refused(self, option):
        block = read({"track": "a2/grammar/weil", option: "x"})
        assert block.refusals == ("unknown_option",)

    def test_a_block_with_an_unknown_option_still_gives_its_track(self):
        block = read({"track": "a2/grammar/weil", "album": "a2/grammar/part-1"})
        assert block.address == "a2/grammar/weil"

    def test_a_block_with_no_examples_is_missing_them(self):
        block = read({"track": "a2/grammar/weil", "title": "Weil"}, body=[])
        assert block.refusals == ("missing_examples",)

    def test_a_duplicate_block_writes_nothing(self):
        block = read({"track": "a2/grammar/weil", "duplicate": None}, body=[])
        assert (block.duplicate, block.writes, block.refusals) == (True, False, ())

    @pytest.mark.parametrize(
        ("options", "body"),
        [
            ({}, BODY),
            ({"title": "Weil"}, []),
            ({"title-en": "Because"}, []),
        ],
    )
    def test_a_duplicate_block_that_gives_anything_writes(self, options, body):
        block = read(
            {"track": "a2/grammar/weil", "duplicate": None, **options}, body=body
        )
        assert block.refusals == ("duplicate_writes",)

    def test_a_sentence_given_twice_is_refused(self):
        body = [*BODY, "", "Ich  bleibe zu Hause, weil ich *krank* bin.", ": Again."]
        block = read({"track": "a2/grammar/weil"}, body=body)
        assert block.refusals == ("sentence_twice",)

    def test_sentences_in_another_case_or_punctuation_are_two(self):
        body = ["Du kommst.", ": You come.", "Du kommst?", ": Do you come?"]
        assert read({"track": "a2/grammar/weil"}, body=body).refusals == ()

    def test_a_multiline_block_keeps_each_examples_lines(self):
        body = ["Liebe Anna,", "bis bald.", ": Dear Anna,", ": see you soon."]
        block = read({"track": "a1/writing/brief", "multiline": None}, body=body)
        assert block.examples == (
            Example("Liebe Anna,\nbis bald.", "Dear Anna,\nsee you soon."),
        )

    def test_a_translation_with_no_sentence_cannot_be_read(self):
        with pytest.raises(BlockFormatError):
            read({"track": "a2/grammar/weil"}, body=[": Only a translation."])

    def test_markup_in_an_example_cannot_be_read(self):
        with pytest.raises(BlockFormatError):
            read({"track": "a2/grammar/weil"}, body=["{akk}`Den` Bus.", ": The bus."])


class TestBlockReaderFind:
    def test_finds_each_block_on_a_page_with_its_line(self):
        text = (
            "# Weil\n\n"
            ":::{audio-examples}\n:track: a2/grammar/weil\n:album: a2/grammar/x\n"
            "\nEins.\n: One.\n:::\n\n"
            ":::{audio-examples}\n:track: a2/grammar/weil\n:duplicate:\n:::\n"
        )
        first, second = BlockReader().find("a2/grammar/weil", text)
        assert (first.line, first.refusals, first.examples) == (
            3,
            ("unknown_option",),
            (Example("Eins.", "One."),),
        )
        assert (second.line, second.duplicate) == (11, True)

    def test_a_block_quoted_in_a_code_fence_is_not_a_block(self):
        text = "```\n:::{audio-examples}\n:track: a2/grammar/weil\n:::\n```\n"
        assert BlockReader().find("a2/grammar/weil", text) == []


class TestSentenceKey:
    def test_spacing_and_emphasis_are_tidied_and_case_kept(self):
        key = BlockReader.sentence_key("Ich  fahre\nmit *dem* _Bus_.")
        assert key == "Ich fahre mit dem Bus."

    def test_unicode_forms_compare_equal(self):
        decomposed = "Grüße."
        assert BlockReader.sentence_key(decomposed) == BlockReader.sentence_key(
            "Grüße."
        )


class TestBlockCollection:
    def writer(self, page: str, address: str = "a2/grammar/weil") -> Block:
        return read({"track": address}, page=page)

    def duplicate(self, page: str, address: str = "a2/grammar/weil") -> Block:
        return read({"track": address, "duplicate": None}, body=[], page=page)

    def test_two_blocks_writing_one_track_are_each_refused(self):
        blocks = [self.writer("a2/grammar/weil"), self.writer("a2/grammar/denn")]
        refusals = BlockCollection(blocks).refusals()
        assert [(r.block.page, r.code) for r in refusals] == [
            ("a2/grammar/weil", "written_twice"),
            ("a2/grammar/denn", "written_twice"),
        ]

    def test_a_duplicate_whose_track_no_block_writes_is_an_orphan(self):
        assert codes([self.duplicate("a2/grammar/denn")]) == {"orphan_duplicate"}

    def test_a_duplicate_of_a_written_track_is_accepted(self):
        blocks = [self.writer("a2/grammar/weil"), self.duplicate("a2/grammar/denn")]
        assert codes(blocks) == set()

    def test_a_writer_counts_however_it_fared(self):
        body = [*BODY, *BODY]
        writer = read({"track": "a2/grammar/weil"}, body=body)
        blocks = [writer, self.duplicate("a2/grammar/denn")]
        assert codes(blocks) == {"sentence_twice"}

    def test_a_duplicate_that_writes_is_not_also_an_orphan(self):
        duplicate = read({"track": "a2/grammar/weil", "duplicate": None})
        assert codes([duplicate]) == {"duplicate_writes"}

    def test_a_bad_address_is_never_grouped(self):
        blocks = [read({"track": "a2"}), read({"track": "a2"})]
        assert codes(blocks) == {"bad_address"}

    def test_reads_every_page_of_a_docs_tree(self, tmp_path: Path):
        page = tmp_path / "a2/grammar/weil.md"
        page.parent.mkdir(parents=True)
        page.write_text(
            ":::{audio-examples}\n:track: a2/grammar\n:duplicate:\n:::\n",
            encoding="utf-8",
        )
        hidden = tmp_path / "_build/a2/grammar/weil.md"
        hidden.parent.mkdir(parents=True)
        hidden.write_text(page.read_text(encoding="utf-8"), encoding="utf-8")

        (refusal,) = BlockCollection.from_docs(tmp_path).refusals()
        assert (refusal.block.page, refusal.code) == (
            "a2/grammar/weil",
            "orphan_duplicate",
        )


class TestSamples:
    def test_the_package_ships_samples_of_every_outcome(self):
        expected = {sample.expect for sample in load_samples()}
        assert expected == {"accepted", *Refusal.CODES}

    @pytest.mark.parametrize("sample", load_samples(), ids=lambda s: s.name)
    def test_each_sample_gets_its_outcome(self, sample: Sample):
        found = codes(sample.blocks())
        assert found == (set() if sample.expect == "accepted" else {sample.expect})
