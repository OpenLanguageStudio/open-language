"""The target-language title, drawn under the H1 from ``target-title:``.

The H1 of an article is English. ``target-title:`` in its front matter names the
goal in the language taught, and the build draws it straight under the H1::

    <p class="ol-target-title" lang="de">Sich vorstellen</p>

It is a subtitle, not a heading, so the sidebar and the page contents never
list it.
"""

from __future__ import annotations

from html import escape

from docutils import nodes

from ol.authoring.situations import front_matter
from ol.docs.roles import language_code

KEY = "target-title"
CLASS = "ol-target-title"


class target_title(nodes.paragraph):
    """The subtitle. Drawn as a paragraph by every builder but HTML and LaTeX."""


def titles_on(env) -> dict[str, str]:
    """The target-language title of each page that has one."""
    if not hasattr(env, "ol_target_titles"):
        env.ol_target_titles = {}
    return env.ol_target_titles


def read_title(app, docname, source):
    """Keep the page's ``target-title:`` when it is one line of text."""
    value = front_matter(source[0]).get(KEY)
    if isinstance(value, str) and value.strip():
        titles_on(app.env)[docname] = " ".join(value.split())
    else:
        titles_on(app.env).pop(docname, None)


def draw(app, doctree):
    """Put the subtitle straight under the page's H1."""
    text = titles_on(app.env).get(app.env.docname)
    section = next(iter(doctree.findall(nodes.section)), None)
    if not text or section is None or not isinstance(section[0], nodes.title):
        return
    section.insert(1, target_title(text, text, classes=[CLASS]))


def purge(app, env, docname):
    """Forget a page's title before it is read again or after it is removed."""
    titles_on(env).pop(docname, None)


def merge(app, env, docnames, other):
    """Take the titles a parallel reader read."""
    for docname in docnames:
        if docname in titles_on(other):
            titles_on(env)[docname] = titles_on(other)[docname]


def visit_html(self, node: target_title) -> None:
    """Open the paragraph with the language of its text."""
    code = language_code()
    lang = f' lang="{escape(code)}"' if code else ""
    self.body.append(f'<p class="{CLASS}"{lang}>')


def depart_html(self, node: target_title) -> None:
    """Close the paragraph."""
    self.body.append("</p>\n")


def visit_latex(self, node: target_title) -> None:
    """Set the subtitle large and in italics, under the chapter or section title."""
    self.body.append("\n\\begingroup\\large\\itshape ")


def depart_latex(self, node: target_title) -> None:
    """End the subtitle's paragraph and its style."""
    self.body.append("\\par\\endgroup\n\n")


def setup(app):
    """Register the subtitle and the hooks that draw it.

    Returns:
        The extension's metadata.
    """
    app.add_node(
        target_title,
        html=(visit_html, depart_html),
        latex=(visit_latex, depart_latex),
    )
    app.connect("source-read", read_title)
    app.connect("doctree-read", draw)
    app.connect("env-purge-doc", purge)
    app.connect("env-merge-info", merge)
    return {
        "version": "1.0",
        "env_version": 1,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
