"""The ``ol-examples`` directive, and reading a page's examples boxes from its doctree.

An examples box holds a definition list, each term a sentence and each
definition its translation, and names the one presenter who says them::

    :::{ol-examples}
    :presenters: emilia

    Ich bin müde.
    : I am tired.
    :::

A build reads the page, so a sentence here is the sentence as the reader sees
it: roles and emphasis are gone, and typographic quotation marks are in.
"""

from __future__ import annotations

from typing import ClassVar

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from ol.blocks import BlockReader, Example


class ExamplesBox(Directive):
    """An examples box: sentences and their translations, said by one presenter.

    It is drawn as a ``div`` of class ``ol-examples``, as the box always was,
    and carries its presenter's slug as ``presenter``. A box that names no
    presenter, or more than one, is reported and drawn with none.
    """

    has_content = True
    option_spec: ClassVar[dict] = {"presenters": directives.unchanged}

    def run(self):
        """Draw the box and note its presenter.

        Returns:
            The box, after an error when its ``:presenters:`` is not one slug.
        """
        slugs = [
            slug.strip()
            for slug in (self.options.get("presenters") or "").split(",")
            if slug.strip()
        ]
        box = nodes.container(classes=[PageExamples.CLASS])
        shown: list[nodes.Node] = []
        if len(slugs) == 1 and BlockReader.SLUG.fullmatch(slugs[0]):
            box["presenter"] = slugs[0]
        else:
            shown.append(
                self.state_machine.reporter.error(
                    "ol-examples: name the one presenter who says the box, as "
                    "':presenters: <slug>'",
                    line=self.lineno,
                )
            )
        self.state.nested_parse(self.content, self.content_offset, box)
        return [*shown, box]


class PageExamples:
    """The examples a page shows in its ``ol-examples`` blocks."""

    CLASS = "ol-examples"

    @classmethod
    def read(cls, doctree: nodes.document) -> list[Example]:
        """Read every ``ol-examples`` block of a page.

        Args:
            doctree: The page's doctree.

        Returns:
            The examples, in page order, each with the presenter its box names,
            or none for a box that names none. A block holding anything but
            sentences and their translations gives none.
        """
        found: list[Example] = []
        for block in doctree.findall(nodes.container):
            if cls.CLASS in block["classes"]:
                presenter = block.get("presenter", "")
                found += [
                    example._replace(presenter=presenter)
                    for example in cls.pairs(block)
                ]
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


def setup(app):
    """Register the ``ol-examples`` directive.

    Returns:
        The extension's metadata.
    """
    app.add_directive("ol-examples", ExamplesBox)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
