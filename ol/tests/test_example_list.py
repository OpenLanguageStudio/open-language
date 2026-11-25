"""The list of sentences and translations both example blocks draw."""

from docutils import nodes

from ol.blocks import Example
from ol.docs.example_list import ExampleList


def pair(sentence: str, translation: str) -> nodes.definition_list_item:
    return nodes.definition_list_item(
        "",
        nodes.term("", sentence),
        nodes.definition("", nodes.paragraph("", translation)),
    )


class TestRead:
    def test_a_definition_list_of_pairs_gives_each_term_and_definition(self):
        dl = nodes.definition_list("", pair("Ja.", "Yes."), pair("Nein.", "No."))

        pairs = ExampleList.read(dl)

        assert [ExampleList.example(*p) for p in pairs] == [
            Example("Ja.", "Yes."),
            Example("Nein.", "No."),
        ]

    def test_anything_but_a_definition_list_gives_none(self):
        assert ExampleList.read(nodes.paragraph("", "Ja.")) is None

    def test_an_item_with_two_definitions_gives_none(self):
        item = pair("Ja.", "Yes.")
        item += nodes.definition("", nodes.paragraph("", "Indeed."))

        assert ExampleList.read(nodes.definition_list("", item)) is None


class TestSentence:
    def test_it_is_the_terms_text_normalised_as_a_track_sentence_is(self):
        term = nodes.term("", "", nodes.Text("Der  Hafen\nist "), nodes.Text("groß."))

        assert ExampleList.sentence(term) == "Der Hafen ist groß."


class TestDraw:
    def test_each_pair_is_an_item_of_one_list_with_its_classes(self):
        dl = ExampleList.draw(ExampleList.plain([Example("Ja.", "Yes.")]), ["x"])

        assert dl["classes"] == ["ol-example-list", "x"]
        assert ExampleList.read(dl) is not None
        assert [ExampleList.example(*p) for p in ExampleList.read(dl)] == [
            Example("Ja.", "Yes.")
        ]

    def test_plain_text_keeps_its_line_breaks(self):
        drawn = ExampleList.lines("Liebe Anna,\n\nbis bald.")

        assert [type(node).__name__ for node in drawn] == [
            "Text",
            "raw",
            "raw",
            "Text",
        ]
