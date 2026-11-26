"""The ``culture-note`` directive: a short note on how people live with the language.

A culture note is a notice with a fixed title, "Culture note", and a colour of
its own, so a reader knows it from the four free notices before reading it::

    :::{culture-note}
    Germans often give only their surname in formal settings.
    :::

It may stand anywhere in the body of a how-to, grammar or writing article.
``ol validate`` holds it to its length and to three on a page.
"""

from __future__ import annotations

from docutils import nodes
from sphinx.util.docutils import SphinxDirective

TITLE = "Culture note"
CLASS = "ol-culture-note"
LATEX_COLOURS = {
    "border": "6B3D99",
    "background": "E7DCF5",
    "title-background": "E7DCF5",
    "title-foreground": "6B3D99",
}
"""The violet of the site's own culture note, which no other notice uses."""


class culture_note(nodes.admonition):
    """A culture note. Drawn as an admonition by every builder but LaTeX."""


class CultureNoteDirective(SphinxDirective):
    """Draw a culture note: the fixed title, then the note's own Markdown."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    option_spec: dict = {}

    def run(self) -> list[nodes.Node]:
        """Draw the note.

        Returns:
            The note, holding its title and its content.
        """
        node = culture_note("\n".join(self.content), classes=[CLASS])
        self.set_source_info(node)
        node += nodes.title(TITLE, TITLE)
        node.extend(self.parse_content_to_nodes(allow_section_headings=False))
        return [node]


def visit_latex(self, node: culture_note) -> None:
    """Open a note box in the culture note's own colours.

    The colours are set inside a group, so the other notes keep theirs.
    """
    colours = ",".join(
        f"div.note_{key}-TeXcolor={{HTML}}{{{value}}}"
        for key, value in LATEX_COLOURS.items()
    )
    self.body.append(
        f"\n{{\\sphinxsetup{{{colours}}}%\n\\begin{{sphinxadmonition}}{{note}}"
    )
    self.no_latex_floats += 1


def depart_latex(self, node: culture_note) -> None:
    """Close the box and the group."""
    self.body.append("\\end{sphinxadmonition}}\n")
    self.no_latex_floats -= 1


def setup(app):
    """Register the directive and its LaTeX drawing.

    Returns:
        The extension's metadata.
    """
    app.add_node(culture_note, latex=(visit_latex, depart_latex))
    app.add_directive("culture-note", CultureNoteDirective)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
