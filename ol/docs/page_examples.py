"""Read a page's ``ol-examples`` blocks from its doctree.

An ``ol-examples`` block is a ``div`` holding a definition list, each term a
sentence and each definition its translation. A build reads the page, so a
sentence here is the sentence as the reader sees it: roles and emphasis are
gone, and typographic quotation marks are in.
"""

from __future__ import annotations

from docutils import nodes

from ol.blocks import BlockReader, Example


class PageExamples:
    """The examples a page shows in its ``ol-examples`` blocks."""

    CLASS = "ol-examples"

    @classmethod
    def read(cls, doctree: nodes.document) -> list[Example]:
        """Read every ``ol-examples`` block of a page.

        Args:
            doctree: The page's doctree.

        Returns:
            The examples, in page order. A block holding anything but sentences
            and their translations gives none.
        """
        found: list[Example] = []
        for block in doctree.findall(nodes.container):
            if cls.CLASS in block["classes"]:
                found += cls.pairs(block)
        return found

    @staticmethod
    def pairs(block: nodes.container) -> list[Example]:
        """Read one block's sentences and translations.

        Args:
            block: The block.

        Returns:
            The examples, or none when the block is anything else than one
            definition list of one term and one definition each.
        """
        children = list(block.children)
        if len(children) != 1 or not isinstance(children[0], nodes.definition_list):
            return []
        examples = []
        for item in children[0].children:
            parts = list(item.children)
            if (
                len(parts) != 2
                or not isinstance(parts[0], nodes.term)
                or not isinstance(parts[1], nodes.definition)
            ):
                return []
            sentence = BlockReader.sentence_key(parts[0].astext())
            translation = "\n".join(p.astext() for p in parts[1].children)
            examples.append(Example(sentence, translation))
        return examples
