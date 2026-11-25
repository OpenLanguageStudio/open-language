"""The ``ol-examples`` box, and reading a page's boxes from its doctree.

An examples box shows sentences beside the explanation they illustrate. It
holds a definition list, each term a sentence and each definition its
translation, and names the one presenter who says them::

    :::{ol-examples}
    :presenters: emilia
    Ich bin müde.
    : I am tired.
    :::

A build reads the page, so a sentence here is the sentence as the reader sees
it: roles and emphasis are gone, and typographic quotation marks are in.

The box's list is read and drawn by ``ol.docs.example_list``, as a track's is.
"""

from __future__ import annotations

from typing import ClassVar

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from ol.blocks import BlockReader, Example
from ol.docs.example_list import ExampleList


class ExamplesBox(Directive):
    """An examples box: sentences and their translations, said by one presenter.

    It is drawn as a ``div`` of class ``ol-examples``, as sphinx-design's
    ``div`` draws one, and keeps its presenter's slug as ``presenter``. A box
    that does not name exactly one presenter by slug is reported and keeps
    none.
    """

    has_content = True
    option_spec: ClassVar[dict] = {"presenters": directives.unchanged}

    def run(self) -> list[nodes.Node]:
        """Draw the box and keep its presenter.

        Returns:
            The box, after an error when its ``:presenters:`` is not one slug.
        """
        presenter = (self.options.get("presenters") or "").strip()
        box = nodes.container(classes=[PageExamples.CLASS], is_div=True)
        found: list[nodes.Node] = []
        if BlockReader.SLUG.fullmatch(presenter):
            box["presenter"] = presenter
        else:
            found.append(
                self.state_machine.reporter.error(
                    "ol-examples: name the one presenter who says the box, as "
                    "':presenters: <slug>'",
                    line=self.lineno,
                )
            )
        parsed = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, parsed)
        pairs = ExampleList.read(parsed[0]) if len(parsed) == 1 else None
        if pairs is None:
            # Anything else than sentences and translations is shown as written.
            box += parsed.children
        else:
            box += ExampleList.draw(
                ((term.children, definition.children) for term, definition in pairs),
                parsed[0]["classes"],
            )
        return [*found, box]


class PageExamples:
    """The examples a page shows in its ``ol-examples`` boxes."""

    CLASS = "ol-examples"

    @classmethod
    def read(cls, doctree: nodes.document) -> list[Example]:
        """Read every ``ol-examples`` box of a page.

        Args:
            doctree: The page's doctree.

        Returns:
            The examples, in page order, each with the presenter its box
            names, or none for a box that names none. A box holding anything
            but sentences and their translations gives none.
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
        """Read one box's sentences and translations.

        Args:
            block: The box.

        Returns:
            The examples, or none when the box is anything else than one
            definition list of one term and one definition each.
        """
        children = list(block.children)
        pairs = ExampleList.read(children[0]) if len(children) == 1 else None
        return [ExampleList.example(*pair) for pair in pairs or []]


def setup(app):
    """Register the ``ol-examples`` directive.

    Args:
        app: The Sphinx application.

    Returns:
        The extension's metadata.
    """
    app.add_directive("ol-examples", ExamplesBox)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
