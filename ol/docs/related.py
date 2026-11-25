"""The Related articles section, drawn from front matter.

A page lists the pages a reader may want next under ``related:`` in its front
matter. Once every page is read, the build appends them as the last section of
the page, one group for each kind of page, in category order. The links the two
retired boxes drew are folded in: on a how-to article every situation naming it,
and on a situation article the how-to articles it names.

A page that keeps a hand-written ``## Related articles`` section and has no
``related:`` is drawn as before, boxes included. A page holding both is
warned about and keeps its section.
"""

from __future__ import annotations

import re

from docutils import nodes
from sphinx.errors import ExtensionError
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging

from ol.authoring.menu import CATEGORY_NAMES
from ol.authoring.related import KEY, resolve
from ol.authoring.situations import front_matter
from ol.docs.situations import (
    SITUATION_PAGE,
    generated_on,
    how_to_links_on,
    link_item,
    related_on,
    situations_naming,
)
from ol.levels import LEVELS

logger = logging.getLogger(__name__)

TITLE = "Related articles"
OTHER = "More"
"""The label of the group of pages that belong to no category."""
HOW_TO_PAGE = re.compile(
    rf"(?P<level>{'|'.join(LEVELS)})/how-to/(?P<name>(?!index$)[^/]+)"
)
"""The page name of a how-to article, such as ``a1/how-to/introduce-yourself``."""


class RelatedMarker(nodes.General, nodes.Element):
    """Where the section goes, until every page is read and its links are known.

    It keeps its page as ``docname``, because a builder that joins every page
    into one document draws them all as the root page.
    """


def written_on(env) -> dict[str, bool]:
    """The pages that hold a hand-written Related articles section."""
    if not hasattr(env, "ol_related_written"):
        env.ol_related_written = {}
    return env.ol_related_written


def read_related(app, docname, source):
    """Keep the ``related:`` of a page that has any."""
    fm = front_matter(source[0])
    if KEY in fm:
        related_on(app.env)[docname] = fm[KEY]


def mark(app, doctree):
    """Note a hand-written section, and mark where the generated one goes."""
    env = app.env
    for section in doctree.findall(nodes.section):
        depth = 0
        parent = section.parent
        while parent is not None and not isinstance(parent, nodes.document):
            depth += 1
            parent = parent.parent
        title = section.next_node(nodes.title)
        if depth <= 1 and title is not None and title.astext() == TITLE:
            written_on(env)[env.docname] = True
    holder = next(
        (child for child in doctree.children if isinstance(child, nodes.section)),
        doctree,
    )
    holder += RelatedMarker(docname=env.docname)


def purge(app, env, docname):
    """Forget what a page recorded before it is read again or after it is removed."""
    for store in (related_on, written_on, generated_on):
        store(env).pop(docname, None)


def merge(app, env, docnames, other):
    """Take what the pages a parallel reader read recorded."""
    for store in (related_on, written_on):
        for docname in docnames:
            if docname in store(other):
                store(env)[docname] = store(other)[docname]


def entries(env, docname: str) -> list[str]:
    """The page names a page's ``related:`` list resolves to, as far as it is sound."""
    value = related_on(env).get(docname)
    if not isinstance(value, list):
        return []
    return [
        resolve(docname, item.strip())
        for item in value
        if isinstance(item, str) and not item.strip().endswith(".md")
    ]


def links_of(env, docname: str) -> tuple[str, ...]:
    """Every page a page links under Related articles, without repeats.

    Args:
        env: The Sphinx build environment.
        docname: The page's name.

    Returns:
        Its own entries in the author's order, then the links its retired box
        drew.
    """
    if HOW_TO_PAGE.fullmatch(docname):
        folded = situations_naming(env, docname)
    elif SITUATION_PAGE.fullmatch(docname):
        folded = tuple(how_to_links_on(env).get(docname, []))
    else:
        folded = ()
    found = dict.fromkeys([*entries(env, docname), *folded])
    found.pop(docname, None)
    return tuple(found)


def pages_to_redraw(app, env):
    """Decide which pages get the generated section, and name those that changed.

    Returns:
        The page names whose section is now drawn with other links, to be
        written again.
    """
    changed = []
    for docname in sorted(env.found_docs):
        links = links_of(env, docname)
        drawn = links if links and docname not in written_on(env) else None
        if generated_on(env).get(docname) != drawn:
            if drawn is None:
                generated_on(env).pop(docname)
            else:
                generated_on(env)[docname] = drawn
            changed.append(docname)
    return changed


def check_entries(app, env):
    """Stop the build on an entry that names no page, and warn about both sources."""
    failed = 0
    for docname, value in sorted(related_on(env).items()):
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            logger.error(
                "'related:' is a list of page paths, such as /a1/how-to/greet",
                location=docname,
            )
            failed += 1
            continue
        for item in value:
            entry = item.strip()
            if entry.endswith(".md"):
                logger.error(
                    "'related:' entry '%s' ends in .md: write the page path without it",
                    entry,
                    location=docname,
                )
                failed += 1
            elif resolve(docname, entry) not in env.found_docs:
                logger.error(
                    "'related:' entry '%s' names no page (%s)",
                    entry,
                    resolve(docname, entry),
                    location=docname,
                )
                failed += 1
        if docname in written_on(env):
            logger.warning(
                "the page has 'related:' and a hand-written '## Related "
                "articles' section: keep the front matter and remove the "
                "section",
                location=docname,
            )
    if failed:
        raise ExtensionError(
            f"{failed} 'related:' entries are not pages: see the errors above"
        )


class DrawRelated(SphinxPostTransform):
    """Draw each page's Related articles, before references are resolved."""

    default_priority = 5

    def run(self, **kwargs) -> None:
        """Replace each marker with its section, or remove it where there is none."""
        for marker in list(self.document.findall(RelatedMarker)):
            links = generated_on(self.env).get(marker["docname"])
            if links:
                marker.replace_self(self.section(links, marker["docname"]))
            else:
                marker.parent.remove(marker)

    def section(self, links: tuple[str, ...], docname: str) -> nodes.section:
        """Draw the section.

        Args:
            links: The pages to link.
            docname: The page it goes on.

        Returns:
            A section with a group of links for each kind of page.
        """
        groups: dict[str, list[str]] = {}
        for link in links:
            groups.setdefault(kind_of(link), []).append(link)
        section = nodes.section(ids=["related-articles"], names=["related articles"])
        section += nodes.title(TITLE, TITLE)
        for kind in sorted(groups, key=order):
            label = CATEGORY_NAMES.get(kind, OTHER)
            heading = nodes.paragraph(classes=["ol-related-kind"])
            heading += nodes.strong(label, label)
            items = nodes.bullet_list(classes=["ol-related-list"])
            for link in groups[kind]:
                items += link_item(self, link, docname)
            section += [heading, items]
        return section


def kind_of(docname: str) -> str:
    """The category a page belongs to, or an empty string for a page of none."""
    parts = docname.split("/")
    if len(parts) >= 3 and parts[0] in LEVELS and parts[1] in CATEGORY_NAMES:
        return parts[1]
    return ""


def order(kind: str) -> int:
    """Where a kind's group stands: the categories in menu order, the rest last."""
    names = list(CATEGORY_NAMES)
    return names.index(kind) if kind in names else len(names)


def setup(app):
    """Register the section and the hooks that draw it.

    Returns:
        The extension's metadata.
    """
    app.setup_extension("ol.docs.situations")
    app.add_node(RelatedMarker)
    app.add_post_transform(DrawRelated)
    app.connect("source-read", read_related)
    app.connect("doctree-read", mark)
    app.connect("env-purge-doc", purge)
    app.connect("env-merge-info", merge)
    app.connect("env-get-updated", pages_to_redraw)
    app.connect("env-check-consistency", check_entries)
    return {
        "version": "1.0",
        "env_version": 1,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
