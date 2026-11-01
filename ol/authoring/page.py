"""A page's Markdown, read as blocks the page standard can measure.

The checks in ``standard.py`` and ``glossary.py`` count words, sentences,
headings and table columns. They read the page through MyST's own Markdown
parser, so a line inside a fence is never mistaken for a heading or a table.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.colon_fence import colon_fence_plugin
from mdit_py_plugins.deflist import deflist_plugin

from ol.authoring.specs_data import SPECS

_PARSER = MarkdownIt("commonmark").enable("table")
_PARSER.use(colon_fence_plugin).use(deflist_plugin)

_DIRECTIVE = re.compile(r"\{([a-z-]+)\}\s*(.*)")
_OPTION = re.compile(r"^:[a-z-]+:")
_NOT_PROSE = {"audio-examples", "toctree", "glossary", "code-block"}

ROLE = re.compile(r"\{([a-z-]+)\}`([^`]*)`")
EXPLICIT_TARGET = re.compile(r"^(.*?)\s*<([^<>]+)>$", re.S)
_LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_LINK_TARGET = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_MARKUP = re.compile(r"(?<!\\)[*`]+|(?<![\w\\])_+|_+(?![\w])")
_ESCAPE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!|])")
_SENTENCE_END = re.compile(r"(?<=[.!?…])[\"'”’)\]]*\s+(?=[\"'“„(\[]*[A-ZÄÖÜ0-9])")
_WORD = re.compile(r"\w")


@dataclass
class Block:
    """One top-level piece of a page."""

    kind: str
    line: int
    text: str = ""
    level: int = 0
    name: str = ""
    arg: str = ""
    items: list[str] = field(default_factory=list)
    header: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    children: list[Block] = field(default_factory=list)

    def is_directive(self, name: str, arg: str | None = None) -> bool:
        """Whether this is the directive ``name``, with ``arg`` when it is given."""
        return (
            self.kind == "directive"
            and self.name == name
            and (arg is None or self.arg == arg)
        )

    @property
    def examples(self) -> bool:
        """Whether this is a ``:::{div} ol-examples`` block."""
        return self.is_directive("div") and "ol-examples" in self.arg


@dataclass
class Section:
    """An H2 and everything up to the next H2."""

    title: str
    line: int
    blocks: list[Block]

    def walk(self):
        """Every block of the section, with those inside directives."""
        return walk(self.blocks)


def walk(blocks: list[Block]):
    """Yield ``blocks`` and every block nested inside them."""
    for block in blocks:
        yield block
        yield from walk(block.children)


def _consume(tokens: list[Token], start: int) -> int:
    """The index just past the token closing the one at ``start``."""
    level = tokens[start].level
    i = start + 1
    while tokens[i].level != level or tokens[i].nesting != -1:
        i += 1
    return i + 1


def _inline(token: Token) -> str:
    return " ".join(token.content.split())


def _table(tokens: list[Token], line: int) -> Block:
    block = Block("table", line)
    row: list[str] = []
    in_header = False
    for i, token in enumerate(tokens):
        if token.type == "thead_open":
            in_header = True
        elif token.type == "tbody_open":
            in_header = False
        elif token.type == "tr_open":
            row = []
        elif token.type in ("th_open", "td_open"):
            row.append(_inline(tokens[i + 1]))
        elif token.type == "tr_close":
            if in_header:
                block.header = row
            else:
                block.rows.append(row)
    return block


def _list(tokens: list[Token], line: int) -> Block:
    block = Block("list", line)
    item_level = tokens[0].level + 1
    for token in tokens:
        if token.type == "list_item_open" and token.level == item_level:
            block.items.append("")
        elif token.type == "inline":
            block.items[-1] = f"{block.items[-1]} {_inline(token)}".strip()
    return block


def _directive(token: Token, line: int) -> Block:
    m = _DIRECTIVE.fullmatch(token.info.strip())
    if not m:
        return Block("code", line, token.content)
    block = Block("directive", line, token.content, name=m[1], arg=m[2].strip())
    if m[1] not in _NOT_PROSE and not block.examples:
        lines = token.content.splitlines()
        while lines and _OPTION.match(lines[0]):
            lines.pop(0)
        block.children = parse("\n".join(lines) + "\n", line)
    return block


def parse(body: str, offset: int = 0) -> list[Block]:
    """Read a page's Markdown into its top-level blocks.

    Args:
        body: The Markdown, without its front matter.
        offset: Lines above ``body`` in the file.

    Returns:
        The blocks, in page order.
    """
    tokens = _PARSER.parse(body)
    blocks: list[Block] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        line = offset + (token.map[0] if token.map else 0) + 1
        end = i + 1
        if token.type == "heading_open":
            level = int(token.tag[1])
            blocks.append(Block("heading", line, _inline(tokens[i + 1]), level=level))
            end = _consume(tokens, i)
        elif token.type == "paragraph_open":
            blocks.append(Block("paragraph", line, _inline(tokens[i + 1])))
            end = _consume(tokens, i)
        elif token.type == "table_open":
            end = _consume(tokens, i)
            blocks.append(_table(tokens[i:end], line))
        elif token.type in ("bullet_list_open", "ordered_list_open"):
            end = _consume(tokens, i)
            blocks.append(_list(tokens[i:end], line))
        elif token.type == "blockquote_open":
            end = _consume(tokens, i)
            quoted = [_inline(t) for t in tokens[i:end] if t.type == "inline"]
            blocks.append(Block("quote", line, " ".join(quoted)))
        elif token.type == "dl_open":
            end = _consume(tokens, i)
        elif token.type in ("colon_fence", "fence"):
            blocks.append(_directive(token, line))
        i = end
    return blocks


def sections(blocks: list[Block]) -> tuple[list[Block], list[Section]]:
    """Split a page at its H2s.

    Args:
        blocks: The page's blocks.

    Returns:
        What stands between the H1 and the first H2, then the H2 sections.
    """
    opening: list[Block] = []
    found: list[Section] = []
    for block in blocks:
        if block.kind == "heading" and block.level == 1:
            continue
        if block.kind == "heading" and block.level == 2:
            found.append(Section(plain(block.text), block.line, []))
        elif found:
            found[-1].blocks.append(block)
        else:
            opening.append(block)
    return opening, found


def _role_text(m: re.Match) -> str:
    text = m[2]
    if m[1] == "stack":
        return text.partition(" | ")[0]
    target = EXPLICIT_TARGET.match(text)
    return target[1] if target else text


def plain(text: str) -> str:
    """The words of inline Markdown, without its markup.

    Args:
        text: Inline Markdown.

    Returns:
        The text as a reader sees it.
    """
    text = ROLE.sub(_role_text, text)
    text = _LINK.sub(r"\1", text)
    return " ".join(_ESCAPE.sub(r"\1", _MARKUP.sub("", text)).split())


def link_targets(text: str) -> list[str]:
    """Where each Markdown link in ``text`` goes."""
    return _LINK_TARGET.findall(text)


def word_count(text: str) -> int:
    """The words in plain text. A lone symbol such as an arrow is not a word."""
    return sum(1 for word in text.split() if _WORD.search(word))


def sentences(text: str) -> list[str]:
    """Split plain text into sentences.

    A full stop ends a sentence unless it closes an abbreviation in
    ``sentence_abbreviations`` in ``specs.yml``.

    Args:
        text: Plain text.

    Returns:
        The sentences, each with at least one word.
    """
    guarded = text
    for abbreviation in SPECS["common"]["sentence_abbreviations"]:
        guarded = re.sub(
            rf"(?<!\w){re.escape(abbreviation)}\s",
            lambda m: m[0].replace(".", "\0").replace(" ", "\1"),
            guarded,
            flags=re.I,
        )
    parts = _SENTENCE_END.split(guarded)
    restored = [p.replace("\0", ".").replace("\1", " ") for p in parts]
    return [p for p in restored if word_count(p)]
