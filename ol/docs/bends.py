"""Remove the bend comments from a page before it is built.

A writer marks a bent writing rule with ``<!-- OL-W8 bent: reason -->``. The
comment is for reviewers and for ``ol validate``, which lists every bend, so
the build drops it and no reader or platform sees it.
"""

from __future__ import annotations

from ol.authoring.rules import strip_bends


def drop_bends(app, docname, source):
    """Strip the page's bend comments."""
    source[0] = strip_bends(source[0])


def setup(app):
    """Register the hook.

    Returns:
        The extension's metadata.
    """
    app.connect("source-read", drop_bends)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
