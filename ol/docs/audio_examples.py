"""audio_examples directive

Renders the body of a "Listen" section: a full (non-collapsible) list of
native/English sentence pairs with optional streaming links (Spotify,
YouTube Music). The section heading itself is authored in the article as a
markdown ``## Listen`` heading right above the directive, so it appears in
the sidebar table of contents.

Directive syntax (MyST colon-fence, ADR-0006 — the block IS the track):

    :::{audio-examples}
    :album: a1/grammar/part-1
    :title: Der Dativ
    :title-en: The dative case

    Ich fahre mit dem Bus.
    : I go by bus.
    :::

The example body is parsed by :func:`ol.docs_source.parse_example_pairs` —
the same function the audio pipeline uses — so the rendered page and the
generated audio cannot drift. A block with a ``:track:`` option is a legacy
ADR-0002 pointer to a track ``.yml``; it still renders, with a deprecation
warning, until the corpus is fully migrated.

When the track has no streaming links yet, a "Streaming links coming soon"
placeholder is shown in place of the buttons.
"""

from html import escape
from pathlib import Path
from typing import ClassVar

import yaml
from docutils import nodes
from docutils.parsers.rst import Directive, directives

from ol.docs_source import (
    DocsFormatError,
    parse_example_pairs,
    parse_example_pairs_multiline,
)

# ---------------------------------------------------------------------------
# Brand SVG icons (inline, no external dependency)
# ---------------------------------------------------------------------------

_SPOTIFY_SVG = (
    '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" '
    'aria-hidden="true" focusable="false">'
    '<path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0z'
    "m5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141"
    "-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 "
    "11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3"
    "-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12"
    "-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm"
    ".12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721"
    "-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719"
    ' 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>'
    "</svg>"
)

_YOUTUBE_MUSIC_SVG = (
    '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" '
    'aria-hidden="true" focusable="false">'
    '<path d="M12 0C5.376 0 0 5.376 0 12s5.376 12 12 12 12-5.376 12-12'
    "S18.624 0 12 0zm0 19.104c-3.924 0-7.104-3.18-7.104-7.104S8.076 4.896 "
    "12 4.896s7.104 3.18 7.104 7.104-3.18 7.104-7.104 7.104zm0-13.332c"
    "-3.432 0-6.228 2.796-6.228 6.228S8.568 18.228 12 18.228s6.228-2.796 "
    "6.228-6.228S15.432 5.772 12 5.772zM9.684 15.216V8.784L15.9 12l-6.216 "
    '3.216z"/>'
    "</svg>"
)


def _strip_angle_brackets(url: str) -> str:
    return url.strip().strip("<>")


def _native_code(workspace_root: Path) -> str:
    """Read language_code from the workspace open-language.yml (fallback: de)."""
    cfg_path = Path(workspace_root) / "open-language.yml"
    try:
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        return cfg.get("language_code") or "de"
    except OSError:
        return "de"


def load_track_examples(
    workspace_root: Path, album: str, track: str
) -> tuple[list[dict], str, str]:
    """Read a track .yml and return (examples, spotify_url, youtube_music_url)."""
    yml_path = Path(workspace_root) / "albums" / album / "tracks" / track
    data = yaml.safe_load(yml_path.read_text(encoding="utf-8")) or {}
    examples = data.get("examples", []) or []
    streaming = data.get("streaming", {}) or {}
    return (
        examples,
        _strip_angle_brackets(streaming.get("spotify", "") or ""),
        _strip_angle_brackets(streaming.get("youtube_music", "") or ""),
    )


def build_audio_examples_html(
    pairs: list[tuple[str, str]], spotify_url: str, youtube_url: str
) -> str:
    """Build the Listen HTML block for a list of (native, translation) pairs."""
    if spotify_url or youtube_url:
        links = ""
        if spotify_url:
            links += (
                f'<a href="{escape(spotify_url)}" target="_blank"'
                f' rel="noopener noreferrer"'
                f' class="btn btn-sm ae-stream-btn ae-spotify-btn">'
                f"{_SPOTIFY_SVG} Open in Spotify</a>"
            )
        if youtube_url:
            links += (
                f'<a href="{escape(youtube_url)}" target="_blank"'
                f' rel="noopener noreferrer"'
                f' class="btn btn-sm ae-stream-btn ae-youtube-btn">'
                f"{_YOUTUBE_MUSIC_SVG} YouTube Music</a>"
            )
        stream_html = f'<div class="ae-stream-links">{links}</div>'
    else:
        stream_html = '<div class="ae-stream-links"><span class="ae-coming-soon">Streaming links coming soon</span></div>'

    items = ""
    for native, en in pairs:
        # Multi-line examples (writing model texts) keep their line breaks.
        native_html = escape(native).replace("\n", "<br>")
        en_html = escape(en).replace("\n", "<br>")
        items += (
            f'<li class="ae-item"><p class="ae-de">{native_html}</p>'
            f'<p class="ae-en ae-hidden">{en_html}</p></li>'
        )

    return (
        '<div class="ae-container">'
        '<div class="ae-header">'
        '<p class="ae-subtitle">Become familiar with the sounds of the language'
        " and listen to how this topic sounds in practice.</p>"
        '<button class="btn btn-sm btn-outline-secondary ae-toggle-btn"'
        ' type="button">Show Translations</button>'
        "</div>"
        f"{stream_html}"
        f'<ul class="ae-list" role="list">{items}</ul>'
        "</div>"
    )


class AudioExamplesDirective(Directive):
    has_content = True
    option_spec: ClassVar[dict] = {
        "album": directives.unchanged_required,
        "name": directives.unchanged,
        "title": directives.unchanged,
        "title-en": directives.unchanged,
        "voice": directives.unchanged,
        "multiline": directives.flag,
        "spotify": directives.unchanged,
        "youtube-music": directives.unchanged,
        "track": directives.unchanged,  # legacy ADR-0002 pointer
    }

    def run(self):
        if "track" in self.options:
            return self._run_legacy_pointer()

        source, lineno = self.state_machine.get_source_and_line(self.lineno)
        where = f"{source}:{lineno}"
        parse_body = (
            parse_example_pairs_multiline
            if "multiline" in self.options
            else parse_example_pairs
        )
        try:
            pairs = parse_body(list(self.content), where)
        except DocsFormatError as exc:
            return [self.state_machine.reporter.error(str(exc), line=self.lineno)]
        if not pairs:
            return [
                self.state_machine.reporter.error(
                    f"audio-examples: block has no example pairs ({where})",
                    line=self.lineno,
                )
            ]

        html = build_audio_examples_html(
            pairs,
            _strip_angle_brackets(self.options.get("spotify", "")),
            _strip_angle_brackets(self.options.get("youtube-music", "")),
        )
        return [nodes.raw("", html, format="html")]

    def _run_legacy_pointer(self):
        """Render an ADR-0002 pointer block from its track .yml (deprecated)."""
        album = self.options["album"].strip()
        track = self.options["track"].strip()
        workspace_root = Path.cwd()
        deprecation = self.state_machine.reporter.warning(
            f"audio-examples: legacy :track: pointer (albums/{album}/tracks/{track})"
            " — move the examples into this block (ADR-0006)",
            line=self.lineno,
        )
        try:
            examples, spotify_url, youtube_url = load_track_examples(
                workspace_root, album, track
            )
        except FileNotFoundError:
            warning = self.state_machine.reporter.warning(
                f"audio-examples: track not found: albums/{album}/tracks/{track}",
                line=self.lineno,
            )
            return [deprecation, warning]

        native_code = _native_code(workspace_root)
        html = build_audio_examples_html(
            [(ex.get(native_code, ""), ex.get("en", "")) for ex in examples],
            spotify_url,
            youtube_url,
        )
        return [deprecation, nodes.raw("", html, format="html")]


def setup(app):
    app.add_directive("audio-examples", AudioExamplesDirective)
    app.add_js_file("audio-examples.js")
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
