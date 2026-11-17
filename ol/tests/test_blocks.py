"""The block form the app reads, and the refusals it reports."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

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


WEIL = {"track": "a2/grammar/weil", "presenters": "lina"}
BRIEF = {"track": "a1/writing/brief", "mode": "passage", "presenters": "lina"}


def read(options: dict, body: list[str] = BODY, page: str = PAGE) -> Block:
    return BlockReader().read(page, options, body, line=3)


def texts(block: Block) -> list[tuple[str, str]]:
    return [(example.sentence, example.translation) for example in block.examples]


def said(block: Block) -> list[tuple[str, int]]:
    return [(example.presenter, example.group) for example in block.examples]


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
                "presenters": "lina",
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
                    "lina",
                    1,
                ),
            ),
            mode="examples",
            presenters=("lina",),
            duplicate=False,
            refusals=(),
        )

    def test_the_address_splits_into_level_category_and_name(self):
        block = read({"track": "a2/grammar/weil"})
        assert (block.level, block.category, block.name) == ("a2", "grammar", "weil")

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "a2",
            "a2/grammar",
            "a2/grammar/",
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
        "option", ["album", "name", "voice", "spotify", "youtube-music", "multiline"]
    )
    def test_a_retired_option_is_refused(self, option):
        block = read({**WEIL, option: "x"})
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
            ({"mode": "pairs"}, []),
            ({"presenters": "lina"}, []),
        ],
    )
    def test_a_duplicate_block_that_gives_anything_writes(self, options, body):
        block = read(
            {"track": "a2/grammar/weil", "duplicate": None, **options}, body=body
        )
        assert block.refusals == ("duplicate_writes",)

    @pytest.mark.parametrize(
        ("written", "said"),
        [
            ("{article}`Der` Hafen ist **groß**.", "Der Hafen ist groß."),
            ("Ich sehe {akk}`den` {noun}`Turm`.", "Ich sehe den Turm."),
            ("Ein  *ganz*\neinfacher Satz.", "Ein ganz einfacher Satz."),
            ("Du kommst?", "Du kommst?"),
        ],
    )
    def test_what_is_spoken_has_no_markup(self, written, said):
        assert BlockReader.spoken(written) == said

    def test_a_sentence_given_twice_is_refused(self):
        body = [*BODY, "", "Ich  bleibe zu Hause, weil ich *krank* bin.", ": Again."]
        block = read(WEIL, body=body)
        assert block.refusals == ("sentence_twice",)

    def test_sentences_in_another_case_or_punctuation_are_two(self):
        body = ["Du kommst.", ": You come.", "Du kommst?", ": Do you come?"]
        assert read(WEIL, body=body).refusals == ()

    def test_a_passage_keeps_each_examples_lines(self):
        body = ["Liebe Anna,", "bis bald.", ": Dear Anna,", ": see you soon."]
        block = read(BRIEF, body=body)
        assert texts(block) == [("Liebe Anna,\nbis bald.", "Dear Anna,\nsee you soon.")]

    def test_a_blank_line_inside_a_passage_is_a_paragraph_break(self):
        body = ["Liebe Anna,", "", "bis bald.", ": Dear Anna,", "", ": see you soon."]
        block = read(BRIEF, body=body)
        assert texts(block) == [
            ("Liebe Anna,\n\nbis bald.", "Dear Anna,\n\nsee you soon.")
        ]

    def test_blank_lines_in_a_row_are_one_paragraph_break(self):
        body = ["Eins.", "", "", "Zwei.", ": One.", ": Two."]
        block = read(BRIEF, body=body)
        assert texts(block) == [("Eins.\n\nZwei.", "One.\nTwo.")]

    def test_a_blank_line_after_a_translation_still_starts_the_next_example(self):
        body = ["Eins.", ": One.", "", "Zwei.", "", "Drei.", ": Two and three."]
        block = read(BRIEF, body=body)
        assert texts(block) == [("Eins.", "One."), ("Zwei.\n\nDrei.", "Two and three.")]

    def test_a_blank_line_before_the_translation_is_no_paragraph_break(self):
        body = ["Eins.", "", ": One."]
        block = read(BRIEF, body=body)
        assert texts(block) == [("Eins.", "One.")]

    @pytest.mark.parametrize(
        "body",
        [
            ["Eins.", "", "Zwei."],
            ["Eins.", ": One.", "", "Zwei.", "", "Drei."],
            ["", ": Only a translation.", "", ": And another."],
            ["Eins.", ": One.", "Zwei.", "", ": Two."],
        ],
    )
    def test_a_passage_with_a_gap_still_needs_its_translation(self, body):
        with pytest.raises(BlockFormatError):
            read(BRIEF, body=body)

    def test_a_single_line_block_takes_no_paragraph_break(self):
        with pytest.raises(BlockFormatError):
            read(WEIL, body=["Eins.", "", ": One."])

    def test_examples_need_no_blank_line_between_them(self):
        body = ["Eins.", ": One.", "Zwei.", ": Two."]
        block = read(WEIL, body=body)
        assert texts(block) == [("Eins.", "One."), ("Zwei.", "Two.")]

    @pytest.mark.parametrize(
        "body",
        [
            [": Only a translation."],
            ["Eins.", "Zwei.", ": Two."],
            ["Eins.", "", ": One."],
            ["Eins."],
            ["Eins.", ":"],
        ],
    )
    def test_a_body_that_is_not_sentence_then_translation_cannot_be_read(self, body):
        with pytest.raises(BlockFormatError):
            read(WEIL, body=body)

    @pytest.mark.parametrize(
        "body",
        [
            ["Liebe Anna,", "bis bald."],
            [": Dear Anna,"],
            ["Liebe Anna,", ": Dear Anna,", "bis bald.", ": see you soon."],
        ],
    )
    def test_a_passage_example_needs_sentences_then_translations(self, body):
        with pytest.raises(BlockFormatError):
            read(BRIEF, body=body)

    def test_markup_in_an_example_cannot_be_read(self):
        with pytest.raises(BlockFormatError):
            read(WEIL, body=["{akk}`Den` Bus.", ": The bus."])


class TestPresenters:
    def test_the_presenters_are_kept_in_the_order_listed(self):
        block = read({**WEIL, "mode": "pairs", "presenters": " deniz ,lina "}, [])
        assert block.presenters == ("deniz", "lina")

    def test_a_block_that_writes_names_its_presenters(self):
        block = read({"track": "a2/grammar/weil"})
        assert block.refusals == ("missing_presenters",)

    def test_a_block_with_no_mode_reads_as_examples(self):
        assert read(WEIL).mode == "examples"

    @pytest.mark.parametrize(
        ("mode", "presenters"),
        [
            ("examples", "lina, roman"),
            ("examples", "Lina"),
            ("examples", "lina berger"),
            ("pairs", "lina, lina"),
            ("pairs", "deniz, lina, roman"),
            ("passage", "lina, roman"),
        ],
    )
    def test_presenters_wrong_for_the_mode_are_refused(self, mode, presenters):
        body = ["Eins.", ": One.", "Zwei.", ": Two."]
        if mode == "passage":
            body.insert(2, "")
        block = read({**WEIL, "mode": mode, "presenters": presenters}, body)
        assert block.refusals == ("bad_presenters",)

    @pytest.mark.parametrize("mode", ["dialogue", "correspondence"])
    def test_a_conversation_needs_two_presenters(self, mode):
        body = ["lina:", "Hallo.", ": Hello."]
        if mode == "dialogue":
            body = ["lina: Hallo.", ": Hello."]
        block = read({**WEIL, "mode": mode}, body)
        assert block.refusals == ("bad_presenters",)

    def test_an_unknown_mode_is_refused_and_its_body_left_unread(self):
        block = read({**WEIL, "mode": "chat"}, ["lina:", "Hallo."])
        assert (block.refusals, block.examples) == (("unknown_mode",), ())

    def test_every_example_of_a_one_presenter_block_is_theirs_and_its_own_group(
        self,
    ):
        body = ["Eins.", ": One.", "", "Zwei.", ": Two."]
        assert said(read(WEIL, body)) == [("lina", 1), ("lina", 2)]

    def test_every_example_of_a_passage_is_its_own_group(self):
        body = ["Eins.", ": One.", "", "Zwei.", ": Two."]
        assert said(read(BRIEF, body)) == [("lina", 1), ("lina", 2)]


class TestPairs:
    OPTIONS: ClassVar[dict] = {**WEIL, "mode": "pairs", "presenters": "deniz, lina"}
    BODY: ClassVar[list] = [
        "Hast du keine Zeit?",
        ": Don't you have time?",
        "Doch, ich habe Zeit.",
        ": Yes, I do have time.",
        "",
        "Kommst du nicht mit?",
        ": Aren't you coming?",
        "Doch, ich komme mit.",
        ": Yes, I'm coming.",
    ]

    def test_the_first_presenter_asks_and_the_second_answers(self):
        block = read(self.OPTIONS, self.BODY)
        assert (block.refusals, said(block)) == (
            (),
            [("deniz", 1), ("lina", 1), ("deniz", 2), ("lina", 2)],
        )

    def test_one_presenter_says_both_halves(self):
        block = read({**self.OPTIONS, "presenters": "lina"}, self.BODY)
        assert said(block) == [("lina", 1), ("lina", 1), ("lina", 2), ("lina", 2)]

    @pytest.mark.parametrize(
        "extra",
        [
            ["", "Und du?", ": And you?"],
            ["Und du?", ": And you?"],
        ],
    )
    def test_a_group_that_is_not_two_examples_is_a_bad_pair(self, extra):
        block = read(self.OPTIONS, [*self.BODY, *extra])
        assert block.refusals == ("bad_pair",)

    def test_a_sentence_may_come_twice(self):
        body = [*self.BODY[:4], "", *self.BODY[:4]]
        assert read(self.OPTIONS, body).refusals == ()


class TestDialogue:
    OPTIONS: ClassVar[dict] = {**WEIL, "mode": "dialogue", "presenters": "lina, roman"}
    BODY: ClassVar[list] = [
        "lina: Guten Morgen! Ist hier noch frei?",
        ": Good morning! Is this seat free?",
        "roman: Ja, natürlich.",
        ": Yes, of course.",
        "",
        "lina: Danke.",
        ": Thanks.",
        "roman: Ja.",
        ": Yes.",
        "lina: Danke.",
        ": Thank you.",
    ]

    def test_each_sentence_is_said_by_the_presenter_it_names(self):
        block = read(self.OPTIONS, self.BODY)
        assert block.refusals == ()
        assert said(block) == [
            ("lina", 1),
            ("roman", 1),
            ("lina", 2),
            ("roman", 2),
            ("lina", 2),
        ]
        assert block.examples[0].sentence == "Guten Morgen! Ist hier noch frei?"

    def test_a_presenter_the_block_does_not_list_is_refused(self):
        body = [*self.BODY, "max: Tschüss.", ": Bye."]
        assert read(self.OPTIONS, body).refusals == ("presenter_not_listed",)

    def test_a_listed_presenter_who_says_nothing_is_refused(self):
        options = {**self.OPTIONS, "presenters": "lina, roman, max"}
        assert read(options, self.BODY).refusals == ("presenter_silent",)

    @pytest.mark.parametrize(
        "line", ["Guten Morgen!", "Lina: Guten Morgen!", "lina:Guten Morgen!"]
    )
    def test_a_sentence_that_names_no_presenter_cannot_be_read(self, line):
        with pytest.raises(BlockFormatError):
            read(self.OPTIONS, [line, ": Good morning!"])


class TestCorrespondence:
    OPTIONS: ClassVar[dict] = {
        **WEIL,
        "mode": "correspondence",
        "presenters": "lina, roman",
    }
    BODY: ClassVar[list] = [
        "lina:",
        "Lieber Roman,",
        "hast du am Samstag Zeit?",
        ": Dear Roman,",
        ": are you free on Saturday?",
        "",
        "roman:",
        "Liebe Lina,",
        "",
        "ja.",
        ": Dear Lina,",
        "",
        ": yes.",
    ]

    def test_each_message_is_one_example_said_by_its_writer(self):
        block = read(self.OPTIONS, self.BODY)
        assert block.refusals == ()
        assert texts(block) == [
            (
                "Lieber Roman,\nhast du am Samstag Zeit?",
                "Dear Roman,\nare you free on Saturday?",
            ),
            ("Liebe Lina,\n\nja.", "Dear Lina,\n\nyes."),
        ]
        assert said(block) == [("lina", 1), ("roman", 1)]

    def test_a_writer_the_block_does_not_list_is_refused(self):
        body = [*self.BODY, "max:", "Hallo.", ": Hello."]
        assert read(self.OPTIONS, body).refusals == ("presenter_not_listed",)

    def test_a_listed_presenter_who_writes_nothing_is_refused(self):
        options = {**self.OPTIONS, "presenters": "lina, roman, max"}
        assert read(options, self.BODY).refusals == ("presenter_silent",)

    @pytest.mark.parametrize(
        "body",
        [
            ["Lieber Roman,", ": Dear Roman,"],
            ["lina:", "Lieber Roman,"],
            ["lina:", "Eins.", ": One.", "", "Zwei.", ": Two."],
        ],
    )
    def test_a_message_that_is_not_a_writer_then_text_then_translation_cannot_be_read(
        self, body
    ):
        with pytest.raises(BlockFormatError):
            read(self.OPTIONS, body)


class TestBlockReaderFind:
    def test_finds_each_block_on_a_page_with_its_line(self):
        text = (
            "# Weil\n\n"
            ":::{audio-examples}\n:track: a2/grammar/weil\n:album: a2/grammar/x\n"
            ":presenters: lina\n"
            "\nEins.\n: One.\n:::\n\n"
            ":::{audio-examples}\n:track: a2/grammar/weil\n:duplicate:\n:::\n"
        )
        first, second = BlockReader().find("a2/grammar/weil", text)
        assert (first.line, first.refusals, first.examples) == (
            3,
            ("unknown_option",),
            (Example("Eins.", "One.", "lina", 1),),
        )
        assert (second.line, second.duplicate) == (12, True)

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
        return read({"track": address, "presenters": "lina"}, page=page)

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
        writer = read(WEIL, body=body)
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
            ":::{audio-examples}\n:track: a2/grammar/weil\n:duplicate:\n:::\n",
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

    def test_skips_the_excluded_names_at_the_top_only(self, tmp_path: Path):
        block = ":::{audio-examples}\n:track: a2/grammar/weil\n:duplicate:\n:::\n"
        (tmp_path / "README.md").write_text(block, encoding="utf-8")
        nested = tmp_path / "a2/README.md"
        nested.parent.mkdir()
        nested.write_text(block, encoding="utf-8")

        refusals = BlockCollection.from_docs(tmp_path, exclude={"README.md"}).refusals()

        assert [refusal.block.page for refusal in refusals] == ["a2/README"]


class TestSamples:
    def test_the_package_ships_samples_of_every_outcome(self):
        expected = {sample.expect for sample in load_samples()}
        assert expected == {"accepted", *(Refusal.CODES - Refusal.APP_ONLY)}

    @pytest.mark.parametrize("sample", load_samples(), ids=lambda s: s.name)
    def test_each_sample_gets_its_outcome(self, sample: Sample):
        found = codes(sample.blocks())
        assert found == (set() if sample.expect == "accepted" else {sample.expect})
