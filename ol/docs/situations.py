"""The ``situations`` and ``how-to-links`` boxes (ADR 2).

A situation article names the how-to articles it puts to use in its front
matter, and that list is the only place the link is written::

    ---
    how-to:
      - /a1/how-to/introduce-yourself.md
    ---

Two boxes draw it, each written with no options and no body. ``how-to-links``
on a situation article links the how-to articles its own front matter names.
``situations`` on a how-to article links every situation article whose front
matter names it, at any level. A link to a page of another level is followed
by that level's badge, as the ``level`` role draws it after a Related articles
link.

A box is drawn once every page is read, because the situations naming a page
may be read after it. A page whose list of situations has changed is written
again, so adding a situation redraws the how-to articles it names.
"""

from __future__ import annotations

import re

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx import addnodes
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging

from ol.authoring.situations import (
    HOW_TO_BOX,
    SITUATIONS_BOX,
    front_matter,
    how_to_names,
)
from ol.docs.roles import level_badge_html
from ol.levels import LEVELS

logger = logging.getLogger(__name__)

SITUATION_PAGE = re.compile(
    rf"(?P<level>{'|'.join(LEVELS)})/situations/(?P<name>(?!index$)[^/]+)"
)
"""The page name of a situation article, such as ``a1/situations/at-a-party``."""

TITLES = {SITUATIONS_BOX: "Situations", HOW_TO_BOX: "How to"}
"""The title each box is drawn with."""


class LinkBox(nodes.General, nodes.Element):
    """Where a box goes, until every page is read and its links are known.

    It keeps the box's directive name as ``box``.
    """


class LinkBoxDirective(Directive):
    """Mark where a box goes and record that the page carries it.

    A box takes no options and no body. ``ol validate`` reports one that has
    either, and the build draws it from the front matter all the same.
    """

    has_content = True

    def run(self) -> list[nodes.Node]:
        """Record the box on the build environment.

        Returns:
            The box's placeholder.
        """
        env = self.state.document.settings.env
        boxes_on(env, self.name)[env.docname] = self.lineno
        return [LinkBox(box=self.name)]


def _kept(env, key: str) -> dict:
    if not hasattr(env, key):
        setattr(env, key, {})
    return getattr(env, key)


def how_to_links_on(env) -> dict[str, list[str]]:
    """The how-to articles each situation article names, by its page name."""
    return _kept(env, "ol_how_to_links")


def boxes_on(env, box: str) -> dict[str, int]:
    """The pages that carry a box, each with the box's line."""
    return _kept(env, f"ol_boxes_{box.replace('-', '_')}")


def drawn_on(env) -> dict[str, tuple[str, ...]]:
    """The situations each ``situations`` box was last drawn with."""
    return _kept(env, "ol_situations_drawn")


def level_of(docname: str) -> str:
    """The level a page belongs to, or nothing for a page outside the levels."""
    level = docname.partition("/")[0]
    return level if level in LEVELS else ""


def read_how_to_links(app, docname, source):
    """Keep the how-to articles a situation article's front matter names."""
    if SITUATION_PAGE.fullmatch(docname):
        how_to_links_on(app.env)[docname] = how_to_names(front_matter(source[0])) or []


def situations_naming(env, docname: str) -> tuple[str, ...]:
    """Every situation article whose front matter names a page, in course order.

    Situations are ordered by level, then as the level's ``situations/index``
    lists them. One the index does not list comes after, by name.

    Args:
        env: The Sphinx build environment.
        docname: The how-to article's page name.

    Returns:
        The situations' page names.
    """

    def order(situation: str) -> tuple[int, int, str]:
        level = level_of(situation)
        listed = env.toctree_includes.get(f"{level}/situations/index", [])
        place = listed.index(situation) if situation in listed else len(listed)
        return LEVELS.index(level), place, situation

    naming = [
        situation
        for situation, names in how_to_links_on(env).items()
        if docname in names and situation in env.found_docs
    ]
    return tuple(sorted(naming, key=order))


def purge(app, env, docname):
    """Forget what a page recorded before it is read again or after it is removed."""
    how_to_links_on(env).pop(docname, None)
    for box in TITLES:
        boxes_on(env, box).pop(docname, None)
    drawn_on(env).pop(docname, None)


def merge(app, env, docnames, other):
    """Take what the pages a parallel reader read recorded."""
    stores = [how_to_links_on, drawn_on] + [
        lambda e, box=box: boxes_on(e, box) for box in TITLES
    ]
    for store in stores:
        theirs = store(other)
        for docname in docnames:
            if docname in theirs:
                store(env)[docname] = theirs[docname]


def pages_to_redraw(app, env):
    """Name the pages whose ``situations`` box would now list other situations.

    Returns:
        The page names, to be written again.
    """
    changed = []
    for docname in boxes_on(env, SITUATIONS_BOX):
        naming = situations_naming(env, docname)
        if drawn_on(env).get(docname) != naming:
            drawn_on(env)[docname] = naming
            changed.append(docname)
    return changed


def warn_empty_boxes(app, env):
    """Warn about a box that would link nothing, once every page is read."""
    for docname, line in sorted(boxes_on(env, SITUATIONS_BOX).items()):
        if not situations_naming(env, docname):
            logger.warning(
                "%s: no situation names this page in its 'how-to:' front matter, "
                "so the box is empty: keep '## When to use it' until one does",
                SITUATIONS_BOX,
                location=(docname, line),
            )
    for docname, line in sorted(boxes_on(env, HOW_TO_BOX).items()):
        if not how_to_links_on(env).get(docname):
            logger.warning(
                "%s: the page's front matter names no how-to article under "
                "'how-to:', so the box is empty",
                HOW_TO_BOX,
                location=(docname, line),
            )


class DrawLinkBoxes(SphinxPostTransform):
    """Draw each box as a titled list of links, before references are resolved.

    Each link is a ``doc`` cross-reference with no text of its own, so Sphinx
    writes the target page's title as it does for a link with empty brackets.
    """

    default_priority = 5

    def run(self, **kwargs) -> None:
        """Replace each placeholder with its box, or remove an empty one."""
        docname = self.env.docname
        for node in list(self.document.findall(LinkBox)):
            box = node["box"]
            if box == SITUATIONS_BOX:
                targets = situations_naming(self.env, docname)
            else:
                targets = tuple(how_to_links_on(self.env).get(docname, []))
            if targets:
                node.replace_self(self.box(box, targets, docname))
            else:
                node.parent.remove(node)

    def box(self, box: str, targets: tuple[str, ...], docname: str) -> nodes.container:
        """Draw one box.

        Args:
            box: The directive name, which names the box's look.
            targets: The pages it links, in order.
            docname: The page it is on.

        Returns:
            A ``div`` of class ``ol-links`` holding a title and a list.
        """
        title = nodes.paragraph(classes=["ol-links-title"])
        title += nodes.strong(TITLES[box], TITLES[box])
        items = nodes.bullet_list(classes=["ol-links-list"])
        for target in targets:
            paragraph = nodes.paragraph()
            paragraph += addnodes.pending_xref(
                "",
                nodes.inline("", ""),
                refdomain="std",
                reftype="doc",
                reftarget=f"/{target}",
                refexplicit=False,
                refwarn=True,
                refdoc=docname,
            )
            level = level_of(target)
            if level and level != level_of(docname):
                paragraph += nodes.Text(" ")
                paragraph += self.badge(level)
            items += nodes.list_item("", paragraph)
        return nodes.container(
            "",
            title,
            items,
            classes=["ol-links", f"ol-links--{box}"],
            is_div=True,
        )

    def badge(self, level: str) -> nodes.Node:
        """A level's badge, or the level in brackets where HTML is not drawn."""
        # Sphinx 9 keeps the builder's class on the environment, as its own
        # post-transforms read it. Sphinx 8 has only the application's builder.
        builder = getattr(self.env, "_builder_cls", None) or self.app.builder
        if builder.format == "html":
            return nodes.raw("", level_badge_html(level), format="html")
        return nodes.Text(f"({level.upper()})")


def setup(app):
    """Register the two boxes and the hooks that draw them.

    Returns:
        The extension's metadata.
    """
    app.add_node(LinkBox)
    app.add_directive(SITUATIONS_BOX, LinkBoxDirective)
    app.add_directive(HOW_TO_BOX, LinkBoxDirective)
    app.add_post_transform(DrawLinkBoxes)
    app.connect("source-read", read_how_to_links)
    app.connect("env-purge-doc", purge)
    app.connect("env-merge-info", merge)
    app.connect("env-get-updated", pages_to_redraw)
    app.connect("env-check-consistency", warn_empty_boxes)
    return {
        "version": "1.0",
        "env_version": 1,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
