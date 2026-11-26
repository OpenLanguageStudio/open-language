"""Links in the text to pages that do not exist yet, drawn as plain text.

A writer links to the article a sentence needs even before it is written (see
``ol.authoring.wanted``). The build draws such a link's text as plain text,
``<span class="ol-wanted">``, instead of failing on it, and logs it. ``ol
wanted`` lists every wanted page with the pages that link to it.
"""

from __future__ import annotations

from docutils import nodes
from sphinx import addnodes
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging

from ol.authoring.wanted import page_link, words_of

logger = logging.getLogger(__name__)

CLASS = "ol-wanted"


class DrawWanted(SphinxPostTransform):
    """Replace each link to a missing page before MyST resolves the links."""

    default_priority = 8
    """MyST resolves its links at 9 and would warn about these."""

    def run(self, **kwargs) -> None:
        """Draw every link to a page that is not in the build as its text."""
        for ref in list(self.document.findall(addnodes.pending_xref)):
            if ref.get("reftype") != "myst" or ref.get("refdomain"):
                # MyST has already matched the link to a page that exists.
                continue
            page = page_link(ref.get("refdoc", self.env.docname), ref["reftarget"])
            if page is None or page in self.env.found_docs:
                continue
            logger.info("wanted page %s", page, location=ref)
            drawn = nodes.inline(classes=[CLASS])
            held = ref.children
            if len(held) == 1 and "xref" in held[0].get("classes", []):
                held = held[0].children
            if ref.astext().strip():
                drawn.extend(child.deepcopy() for child in held)
            else:
                drawn += nodes.Text(words_of(page))
            ref.replace_self(drawn)


def setup(app):
    """Register the transform.

    Returns:
        The extension's metadata.
    """
    app.add_post_transform(DrawWanted)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
