"""The list of sentences and their translations that both example blocks draw.

A page shows examples in two blocks. An ``ol-examples`` box sits beside an
explanation, and an ``audio-examples`` block holds the page's track. Both are
written as a definition list, each term a sentence and each definition its
translation::

    Ich bin müde.
    : I am tired.

This module is what the two blocks share. ``ExampleList.read`` reads a parsed
definition list as its pairs, ``ExampleList.draw`` draws pairs as the list a
page shows, and ``ExampleList.sentence`` is the sentence a pair gives, as
``BlockReader.sentence_key`` normalises it. ``ol.docs.page_examples`` draws a
box with them, and ``ol.docs.audio_examples`` adds a track's header and its
translations button around the same list.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from docutils import nodes

from ol.blocks import BlockReader, Example

#: A sentence and its translation, each as the nodes that draw it.
Pair = tuple[Sequence[nodes.Node], Sequence[nodes.Node]]


class ExampleList:
    """Read and draw a list of sentences and their translations."""

    @staticmethod
    def read(dl: nodes.Node) -> list[tuple[nodes.term, nodes.definition]] | None:
        """Read a parsed definition list as its sentences and translations.

        Args:
            dl: The node a block's content was parsed into.

        Returns:
            Each item's term and definition, or ``None`` when the node is not
            a definition list whose every item is one term and one definition.
        """
        if not isinstance(dl, nodes.definition_list):
            return None
        pairs = []
        for item in dl.children:
            parts = list(item.children)
            if (
                len(parts) != 2
                or not isinstance(parts[0], nodes.term)
                or not isinstance(parts[1], nodes.definition)
            ):
                return None
            pairs.append((parts[0], parts[1]))
        return pairs

    @staticmethod
    def sentence(term: nodes.term) -> str:
        """Return the sentence a term gives, as it identifies an example.

        Args:
            term: The term, as the page draws it.

        Returns:
            The term's text, normalised by ``BlockReader.sentence_key``.
        """
        return BlockReader.sentence_key(term.astext())

    @staticmethod
    def translation(definition: nodes.definition) -> str:
        """Return a definition's text, one line for each of its paragraphs."""
        return "\n".join(part.astext() for part in definition.children)

    @classmethod
    def example(cls, term: nodes.term, definition: nodes.definition) -> Example:
        """Return the example a pair gives, with no presenter."""
        return Example(cls.sentence(term), cls.translation(definition))

    @staticmethod
    def lines(text: str) -> list[nodes.Node]:
        """Draw plain text, keeping its line breaks.

        Args:
            text: A sentence or translation as a block gives it. A passage keeps
                its lines and an empty line between its paragraphs.

        Returns:
            The text's nodes, with a line break between its lines.
        """
        drawn: list[nodes.Node] = []
        for number, line in enumerate(text.split("\n")):
            if number:
                drawn.append(nodes.raw("", "<br>", format="html"))
            if line:
                drawn.append(nodes.Text(line))
        return drawn

    @classmethod
    def plain(cls, examples: Iterable[Example]) -> list[Pair]:
        """Return examples as pairs of plain text, for ``draw``.

        Args:
            examples: The examples, whose text is drawn as it is, never parsed.

        Returns:
            Each sentence's lines, and its translation's lines in one paragraph.
        """
        pairs: list[Pair] = []
        for example in examples:
            translation = nodes.paragraph("", "", *cls.lines(example.translation))
            pairs.append((cls.lines(example.sentence), [translation]))
        return pairs

    @staticmethod
    def draw(
        pairs: Iterable[Pair], classes: Sequence[str] = ()
    ) -> nodes.definition_list:
        """Draw pairs as the list a page shows.

        Args:
            pairs: Each sentence and its translation, as the nodes that draw
                them. A translation's nodes go into its definition as they are.
            classes: Classes the list carries besides its own.

        Returns:
            One definition list, an item for each pair.
        """
        dl = nodes.definition_list(classes=["ol-example-list", *classes])
        for sentence, translation in pairs:
            dl += nodes.definition_list_item(
                "",
                nodes.term("", "", *sentence),
                nodes.definition("", *translation),
            )
        return dl
