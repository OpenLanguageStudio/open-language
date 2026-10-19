"""The ``audio-examples`` directive for a standalone build of a Coursebook."""

from html import escape
from typing import ClassVar

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util import logging

from ol.blocks import Block, BlockCollection, BlockFormatError, BlockReader, Example

logger = logging.getLogger(__name__)


class DuplicateTrack(nodes.General, nodes.Element):
    """Where a duplicate block shows the examples of the block that writes its track.

    It is replaced once every page has been read, because that block may be on
    a page read later.
    """


def build_audio_examples_html(examples: list[Example]) -> str:
    """Build the HTML of a track's examples, each above its hidden translation.

    Args:
        examples: The track's examples, in order.

    Returns:
        The HTML, with every sentence and translation escaped.
    """
    items = ""
    for sentence, translation in examples:
        # Multiline examples (writing model texts) keep their line breaks.
        sentence_html = escape(sentence).replace("\n", "<br>")
        translation_html = escape(translation).replace("\n", "<br>")
        items += (
            f'<li class="ae-item"><p class="ae-de">{sentence_html}</p>'
            f'<p class="ae-en ae-hidden">{translation_html}</p></li>'
        )
    return (
        '<div class="ae-container">'
        '<div class="ae-header">'
        '<p class="ae-subtitle">Become familiar with the sounds of the language'
        " and listen to how this topic sounds in practice.</p>"
        '<button class="btn btn-sm btn-outline-secondary ae-toggle-btn"'
        ' type="button">Show Translations</button>'
        "</div>"
        f'<ul class="ae-list" role="list">{items}</ul>'
        "</div>"
    )


class AudioExamplesDirective(Directive):
    """Show a block's track and warn about each refusal it earns.

    A block that writes its track shows its own examples. A ``:duplicate:``
    block shows the examples of the block that writes its track, on whichever
    page that is. An option the block does not take is reported by MyST as an
    unknown option.
    """

    has_content = True
    option_spec: ClassVar[dict] = {
        "track": directives.unchanged,
        "title": directives.unchanged,
        "title-en": directives.unchanged,
        "tags": directives.unchanged,
        "multiline": directives.flag,
        "duplicate": directives.flag,
    }
    reader: ClassVar[BlockReader] = BlockReader()

    def run(self):
        """Read the block, record it for the build and return what it shows.

        Returns:
            A warning for each refusal, then the examples' HTML for a block
            that writes, or a ``DuplicateTrack`` for a duplicate.
        """
        env = self.state.document.settings.env
        reporter = self.state_machine.reporter
        try:
            block = self.reader.read(
                env.docname, self.options, list(self.content), self.lineno
            )
        except BlockFormatError as exc:
            return [reporter.error(f"audio-examples: {exc}", line=self.lineno)]
        blocks_on(env).setdefault(env.docname, []).append(block)

        shown: list[nodes.Node] = [
            reporter.warning(f"audio-examples: {code}", line=self.lineno)
            for code in block.refusals
        ]
        if block.writes:
            html = build_audio_examples_html(list(block.examples))
            shown.append(nodes.raw("", html, format="html"))
        elif block.duplicate and not block.refusals:
            shown.append(DuplicateTrack(address=block.address))
        return shown


def blocks_on(env) -> dict[str, list[Block]]:
    """Return the blocks read so far, kept on the build environment.

    Args:
        env: The Sphinx build environment.

    Returns:
        Each page's blocks, by page name.
    """
    if not hasattr(env, "ol_blocks"):
        env.ol_blocks = {}
    blocks: dict[str, list[Block]] = env.ol_blocks
    return blocks


def collection(env) -> BlockCollection:
    """Collect every block of the build.

    Args:
        env: The Sphinx build environment.

    Returns:
        The blocks, page by page.
    """
    return BlockCollection(
        block for page in sorted(blocks_on(env)) for block in blocks_on(env)[page]
    )


def purge_blocks(app, env, docname):
    """Forget a page's blocks before it is read again or after it is removed."""
    blocks_on(env).pop(docname, None)


def merge_blocks(app, env, docnames, other):
    """Take the blocks of the pages a parallel reader read."""
    for docname in docnames:
        blocks_on(env)[docname] = blocks_on(other).get(docname, [])


def warn_across_pages(app, env):
    """Warn about the refusals that need every page, once every page is read."""
    for refusal in collection(env).refusals():
        if refusal.code in refusal.CROSS_PAGE:
            logger.warning(
                "audio-examples: %s: %s",
                refusal.code,
                refusal.detail,
                location=(refusal.block.page, refusal.block.line),
            )


def pages_with_duplicates(app, env):
    """Name every page with a duplicate, to write again as its track may have changed.

    Returns:
        The page names.
    """
    return [
        page
        for page, blocks in blocks_on(env).items()
        if any(block.duplicate for block in blocks)
    ]


def show_duplicates(app, doctree, docname):
    """Give each duplicate the examples of the one block that writes its track.

    A duplicate whose track is written by no block, or by more than one, shows
    nothing: the build has warned about it already.
    """
    writers: dict[str, list[Block]] = {}
    for block in collection(app.env).blocks:
        if block.writes:
            writers.setdefault(block.address, []).append(block)
    for node in list(doctree.findall(DuplicateTrack)):
        found = writers.get(node["address"], [])
        if len(found) == 1:
            html = build_audio_examples_html(list(found[0].examples))
            node.replace_self(nodes.raw("", html, format="html"))
        else:
            node.parent.remove(node)


def setup(app):
    """Register the directive and the hooks that match duplicates with their tracks.

    Returns:
        The extension's metadata. ``env_version`` makes Sphinx discard a build
        environment saved by a version that did not record blocks.
    """
    app.add_node(DuplicateTrack)
    app.add_directive("audio-examples", AudioExamplesDirective)
    app.add_js_file("audio-examples.js")
    app.connect("env-purge-doc", purge_blocks)
    app.connect("env-merge-info", merge_blocks)
    app.connect("env-check-consistency", warn_across_pages)
    app.connect("env-get-updated", pages_with_duplicates)
    app.connect("doctree-resolved", show_duplicates)
    return {
        "version": "2.0",
        "env_version": 2,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
