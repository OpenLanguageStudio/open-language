"""Docs-as-source: extract track content from ``:::{audio-examples}`` blocks.

ADR-0006 inverts ADR-0002: the ``audio-examples`` block in a docs article is
the source of truth for track content. Its ``:album:`` option is the backlink
that assigns the track to an album; ``album.yml`` keeps only an ordered list
of track *names* (slugs). This module is the single parser for those blocks —
the Sphinx directive (``ol.docs.audio_examples``) and the album loader
(``ol.language``) both call :func:`parse_example_pairs`, so the coursebook
page and the generated audio cannot drift.

Block grammar (strict — violations raise :class:`DocsFormatError`)::

    :::{audio-examples}
    :album: a1/grammar/part-1
    :name: dativ                      # optional; defaults to the .md file stem
    :title: Der Dativ                 # native title, spoken in the audio intro
    :title-en: The dative case       # instruction-language title
    :voice: sophie                    # optional track-level voice override
    :spotify: https://...            # optional, set after release
    :youtube-music: https://...      # optional, set after release

    Ich fahre mit dem Bus.
    : I go by bus.

    Sie kommt aus der Türkei.
    : She comes from Turkey.
    :::

Body rules: pairs of one native line and one ``:``-prefixed translation line,
optionally separated by blank lines. Lines must be plain text — no Sphinx role
markup, backticks or braces — because the native line is fed verbatim to TTS.

Blocks that carry a ``:track:`` option are legacy ADR-0002 pointers; the
scanner skips them (their data still lives in a track ``.yml``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from markdown_it import MarkdownIt
from mdit_py_plugins.colon_fence import colon_fence_plugin

DIRECTIVE_NAME = "audio-examples"

#: Options the block grammar accepts. ``track`` marks a legacy pointer block.
KNOWN_OPTIONS = {
    "album",
    "name",
    "title",
    "title-en",
    "voice",
    "multiline",
    "spotify",
    "youtube-music",
    "track",
}

#: Characters banned inside example lines: role markup and code would reach
#: the TTS text verbatim.
_BANNED_CHARS = ("`", "{", "}")

_md_parser = MarkdownIt("commonmark").use(colon_fence_plugin)


class DocsFormatError(ValueError):
    """An audio-examples block violates the authoring grammar."""


@dataclass
class AudioExamplesBlock:
    """One parsed ``audio-examples`` block located in a docs article."""

    doc_path: Path
    open_line: int  # 0-based line index of the opening fence
    close_line: int  # 0-based line index of the closing fence
    option_lines: list[str]  # raw option lines, exactly as authored
    options: dict[str, str] = field(default_factory=dict)
    pairs: list[tuple[str, str]] = field(default_factory=list)

    @property
    def is_legacy_pointer(self) -> bool:
        return "track" in self.options

    @property
    def album(self) -> str:
        return self.options.get("album", "")

    def name(self, default_stem: str) -> str:
        return self.options.get("name") or default_stem


# ---------------------------------------------------------------------------
# Body grammar
# ---------------------------------------------------------------------------


def parse_option_lines(lines: list[str], where: str) -> tuple[dict[str, str], int]:
    """Parse leading ``:key: value`` lines; return (options, body start index)."""
    options: dict[str, str] = {}
    body_start = len(lines)
    for idx, line in enumerate(lines):
        stripped = line.strip()
        is_option = (
            stripped.startswith(":")
            and not stripped.startswith(": ")
            and ":" in stripped[1:]
        )
        if not is_option:
            body_start = idx
            break
        key, _, value = stripped[1:].partition(":")
        key = key.strip()
        if key not in KNOWN_OPTIONS:
            raise DocsFormatError(f"{where}: unknown option ':{key}:'")
        if key in options:
            raise DocsFormatError(f"{where}: duplicate option ':{key}:'")
        options[key] = value.strip().strip("<>")
    return options, body_start


def parse_example_pairs(lines: list[str], where: str) -> list[tuple[str, str]]:
    """Parse the example body: (native, translation) line pairs.

    This is the shared grammar: the Sphinx directive renders exactly what
    this function returns, and the audio pipeline speaks exactly the native
    halves of it.
    """
    pairs: list[tuple[str, str]] = []
    pending_native: str | None = None

    for offset, raw in enumerate(lines):
        line = raw.strip()
        loc = f"{where} (body line {offset + 1})"
        if not line:
            if pending_native is not None:
                raise DocsFormatError(
                    f"{loc}: native line {pending_native!r} has no ': translation' line"
                )
            continue
        for ch in _BANNED_CHARS:
            if ch in line:
                raise DocsFormatError(
                    f"{loc}: {ch!r} is not allowed in example lines "
                    "(plain text only — this text is fed to TTS verbatim)"
                )
        if line.startswith(":"):
            if pending_native is None:
                raise DocsFormatError(
                    f"{loc}: translation line {line!r} has no native line above it"
                )
            translation = line[1:].strip()
            if not translation:
                raise DocsFormatError(f"{loc}: empty translation line")
            pairs.append((pending_native, translation))
            pending_native = None
        else:
            if pending_native is not None:
                raise DocsFormatError(
                    f"{loc}: two consecutive native lines — expected "
                    f"': translation' after {pending_native!r}"
                )
            pending_native = line

    if pending_native is not None:
        raise DocsFormatError(
            f"{where}: native line {pending_native!r} has no ': translation' line"
        )
    return pairs


def parse_example_pairs_multiline(
    lines: list[str], where: str
) -> list[tuple[str, str]]:
    """Parse a ``:multiline:`` body: blank-line-separated multi-line pairs.

    Used for writing-category model texts (emails, postcards, SMS threads).
    Each group is one example: native lines first, then the ``:``-prefixed
    translation lines. Line breaks are preserved — the joined native text is
    fed to TTS verbatim.
    """
    pairs: list[tuple[str, str]] = []
    native_lines: list[str] = []
    translation_lines: list[str] = []

    def flush(loc: str) -> None:
        if not native_lines and not translation_lines:
            return
        if not native_lines:
            raise DocsFormatError(f"{loc}: example has no native lines")
        if not translation_lines:
            raise DocsFormatError(
                f"{loc}: example {native_lines[0]!r}… has no ': translation' lines"
            )
        pairs.append(("\n".join(native_lines), "\n".join(translation_lines)))
        native_lines.clear()
        translation_lines.clear()

    for offset, raw in enumerate(lines):
        line = raw.strip()
        loc = f"{where} (body line {offset + 1})"
        if not line:
            flush(loc)
            continue
        for ch in _BANNED_CHARS:
            if ch in line:
                raise DocsFormatError(
                    f"{loc}: {ch!r} is not allowed in example lines "
                    "(plain text only — this text is fed to TTS verbatim)"
                )
        if line.startswith(":"):
            translation = line[1:].strip()
            if not translation:
                raise DocsFormatError(f"{loc}: empty translation line")
            translation_lines.append(translation)
        else:
            if translation_lines:
                raise DocsFormatError(
                    f"{loc}: native line {line!r} after translation lines — "
                    "separate examples with a blank line"
                )
            native_lines.append(line)

    flush(where)
    return pairs


# ---------------------------------------------------------------------------
# Block location
# ---------------------------------------------------------------------------


def iter_file_blocks(doc_path: Path, text: str) -> list[AudioExamplesBlock]:
    """Locate and parse every audio-examples block in one markdown file."""
    lines = text.splitlines()
    blocks: list[AudioExamplesBlock] = []
    for token in _md_parser.parse(text):
        if token.type not in ("colon_fence", "fence"):
            continue
        if token.info.strip() != f"{{{DIRECTIVE_NAME}}}":
            continue
        if token.map is None:
            continue
        start, end = token.map  # [opening fence, line after closing fence)
        where = f"{doc_path}:{start + 1}"
        body = lines[start + 1 : end - 1]
        options, body_start = parse_option_lines(body, where)
        block = AudioExamplesBlock(
            doc_path=doc_path,
            open_line=start,
            close_line=end - 1,
            option_lines=body[:body_start],
            options=options,
        )
        if not block.is_legacy_pointer:
            parse_body = (
                parse_example_pairs_multiline
                if "multiline" in options
                else parse_example_pairs
            )
            block.pairs = parse_body(body[body_start:], where)
            _validate_content_block(block, where)
        blocks.append(block)
    return blocks


def _validate_content_block(block: AudioExamplesBlock, where: str) -> None:
    if not block.options.get("album"):
        raise DocsFormatError(f"{where}: missing required option ':album:'")
    if not block.options.get("title"):
        raise DocsFormatError(f"{where}: missing required option ':title:'")
    if not block.pairs:
        raise DocsFormatError(f"{where}: block has no example pairs")


def scan_docs(docs_root: Path) -> dict[tuple[str, str], AudioExamplesBlock]:
    """Scan a docs tree and index every content block by (album, name).

    Legacy pointer blocks are skipped. Hidden and underscore-prefixed
    directories (``_build``, ``.git``, …) are ignored.
    """
    index: dict[tuple[str, str], AudioExamplesBlock] = {}
    docs_root = Path(docs_root)
    for md_path in sorted(docs_root.rglob("*.md")):
        rel_parts = md_path.relative_to(docs_root).parts
        if any(p.startswith(("_", ".")) for p in rel_parts):
            continue
        text = md_path.read_text(encoding="utf-8")
        if f"{{{DIRECTIVE_NAME}}}" not in text:
            continue
        for block in iter_file_blocks(md_path, text):
            if block.is_legacy_pointer:
                continue
            key = (block.album, block.name(md_path.stem))
            if key in index:
                raise DocsFormatError(
                    f"duplicate track {key[1]!r} for album {key[0]!r}: "
                    f"defined in both {index[key].doc_path} and {md_path} "
                    "(use :name: to disambiguate)"
                )
            index[key] = block
    return index


# ---------------------------------------------------------------------------
# Track-data shaping
# ---------------------------------------------------------------------------


def block_to_track_data(block: AudioExamplesBlock, native_code: str) -> dict:
    """Shape a parsed block into the track-yml-equivalent dict Track consumes."""
    title: dict[str, str] = {native_code: block.options["title"]}
    title["en"] = block.options.get("title-en") or block.options["title"]

    data: dict = {"title": title}
    if block.options.get("voice"):
        data["voice"] = block.options["voice"]
    streaming = {
        key: block.options[opt]
        for opt, key in (("spotify", "spotify"), ("youtube-music", "youtube_music"))
        if block.options.get(opt)
    }
    if streaming:
        data["streaming"] = streaming
    data["examples"] = [
        {native_code: native, "en": translation} for native, translation in block.pairs
    ]
    data["_docs_source"] = {"path": str(block.doc_path)}
    return data


# ---------------------------------------------------------------------------
# Trim rewrite
# ---------------------------------------------------------------------------


def rewrite_block_examples(
    doc_path: Path, album: str, name: str, kept_pairs: list[tuple[str, str]]
) -> None:
    """Rewrite one block's example body in place, keeping fences and options.

    Used by ``Track.trim()`` after stitching: the docs block is trimmed down
    to exactly the examples that made it into the audio, preserving the
    page == audio invariant from ADR-0002 in the docs-as-source world.
    """
    text = doc_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    target = None
    for block in iter_file_blocks(doc_path, text):
        if block.is_legacy_pointer:
            continue
        if block.album == album and block.name(doc_path.stem) == name:
            target = block
            break
    if target is None:
        raise DocsFormatError(
            f"{doc_path}: no audio-examples block for album {album!r} name {name!r}"
        )

    body: list[str] = list(target.option_lines)
    for native, translation in kept_pairs:
        body.append("")
        body.extend(native.split("\n"))
        body.extend(f": {line}" for line in translation.split("\n"))

    new_lines = lines[: target.open_line + 1] + body + lines[target.close_line :]
    ending = "\n" if text.endswith("\n") else ""
    doc_path.write_text("\n".join(new_lines) + ending, encoding="utf-8")
