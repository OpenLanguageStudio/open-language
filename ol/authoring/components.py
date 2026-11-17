"""The components a page is built from, as ``docs/reference/components.md`` lists them.

A page uses only the directives and roles listed here, each on the pages it is
limited to. The rules for notices, badges, tabs, card grids and the button are
in the page standard's Components section. The limits are in ``specs.yml``.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from ol.authoring.page import (
    Block,
    parse,
    plain,
    sections,
    sentences,
    walk,
    word_count,
)
from ol.authoring.specs_data import SPECS
from ol.levels import LEVELS
from ol.workspace import page_path

LIMITS = SPECS["components"]

FREE_NOTICES = ("note", "tip", "important", "warning")
"""The notices a page may hold anywhere, each with its one meaning."""
TITLED_NOTICES = {
    "Prerequisites": "note",
    "Common mistakes": "caution",
    "Key points": "note",
}
"""The only titles an ``admonition`` takes, each with its class."""
DIRECTIVES = {
    "ol-examples",
    "audio-examples",
    *FREE_NOTICES,
    "admonition",
    "tab-set",
    "tab-item",
    "grid",
    "grid-item-card",
    "button-ref",
    "toctree",
    "glossary",
}
"""Every directive a page may use. Some are limited to some pages."""
ROLES = {"stack", "term", "level", "bdg-light"}
"""The roles every page may use, besides the language's marking roles."""
INTERFACE_ROLES = {"kbd", "guilabel", "menuselection", "file", "command", "samp"}
"""Roles that describe software, for the How to use and Contributing pages."""
INTERFACE_PAGES = {"how_to_use", "contributing"}

_NOT_A_NOTICE = {
    "hint": "write it as a tip",
    "caution": "write it as a warning",
    "attention": "write it as a warning or an important",
    "danger": "nothing in a language course cannot be undone: write a warning",
    "error": "nothing in a language course cannot be undone: write a warning",
    "seealso": "links go under Prerequisites or Related articles",
    "div": "an examples box is written ':::{ol-examples}' with ':presenters: <slug>'",
}
_ROLE = re.compile(r"\{([a-z][a-z0-9-]*)\}`([^`]*)`")
_FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
# A role, kept, or a span of inline code, which is blanked out. Read left to
# right, so the backticks of a role never open a code span.
_ROLE_OR_CODE = re.compile(r"(\{[a-z][a-z0-9-]*\}`[^`]*`)|(`+)(?!`).+?(?<!`)\2(?!`)")
_OPTION = re.compile(r"^:([a-z-]+):\s*(.*?)\s*$")
_LINK_BEFORE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)\s*$")
_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
_SEPARATOR = re.compile(r"\^{3,}|\+{3,}")
_BOLD_ONLY = re.compile(r"^(\*\*|__)[^*_]+\1:?$")
_EXTERNAL = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
_INLINE_BANS = (
    (re.compile(r"\[\^[^\]\s]+\]"), "a footnote: an aside goes in brackets or a note"),
    (
        re.compile(r"(?<!~)~~[^~\n]+~~(?!~)"),
        "struck-through text: a screen reader reads it aloud as if it were right",
    ),
    (
        re.compile(r"\]\{[^}]*\.mark\b[^}]*\}"),
        "a highlighted span: highlight is what a marked phrase looks like",
    ),
    (
        re.compile(r"<details\b", re.I),
        "a <details> block is a collapsible: nothing on a page is hidden behind a click",
    ),
)


@dataclass
class Page:
    """Where a page sits, which decides the components it may use.

    Attributes:
        kind: ``article``, ``index``, ``introduction``, ``terminology``,
            ``how_to_use`` or ``contributing``.
        path: The page's file.
        workspace: The language repository's root, or None outside one.
        category: An article's category.
    """

    kind: str
    path: Path
    workspace: Path | None = None
    category: str | None = None

    @property
    def level(self) -> str | None:
        """The level the page belongs to, or None above the levels."""
        parts = page_path(self.path, self.workspace) if self.workspace else None
        return parts[0] if parts and parts[0] in LEVELS else None

    def target(self, link: str) -> Path | None:
        """The file a page link goes to, or None for a link off the site.

        Args:
            link: The link as written, with or without ``.md``.

        Returns:
            The file, which may not exist.
        """
        if _EXTERNAL.match(link) or link.startswith("#"):
            return None
        link = link.partition("#")[0]
        if link.startswith("/"):
            if not self.workspace:
                return None
            target = self.workspace / link.lstrip("/")
        else:
            target = self.path.parent / link
        return (
            target if target.suffix == ".md" else target.with_name(f"{target.name}.md")
        )

    def name(self, link: str) -> str | None:
        """A page link as a page name below the workspace, such as ``a1/index``."""
        target = self.target(link)
        if target is None or not self.workspace:
            return None
        parts = page_path(target.resolve(), self.workspace.resolve())
        return "/".join(parts) if parts else None

    def level_of(self, link: str) -> str | None:
        """The level of the page a link goes to."""
        name = self.name(link)
        first = name.split("/")[0] if name else None
        return first if first in LEVELS else None


@dataclass
class Card:
    """One card of a card grid."""

    line: int
    title: str
    options: dict[str, str]
    body: list[Block]
    separated: bool
    """Whether a ``^^^`` or ``+++`` line gives the card a header or a footer."""

    @property
    def link(self) -> str:
        """Where the card goes, as written."""
        return self.options.get("link", "")


def options(block: Block) -> dict[str, str]:
    """A directive's options, the ``:name: value`` lines that open its content."""
    found = {}
    for line in block.text.splitlines():
        m = _OPTION.match(line.strip())
        if not m:
            break
        found[m[1]] = m[2]
    return found


def marking_roles(workspace: Path | None) -> set[str]:
    """The marking roles a language repository registers in its ``conf.py``.

    They are the ``custom_roles`` list, read without running the file.

    Args:
        workspace: The language repository's root.

    Returns:
        The role names, or none when the file sets no list.
    """
    conf = workspace / "conf.py" if workspace else None
    if conf is None or not conf.is_file():
        return set()
    try:
        tree = ast.parse(conf.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(t, ast.Name) and t.id == "custom_roles" for t in node.targets
            )
            and isinstance(node.value, ast.List | ast.Tuple)
        ):
            return {
                item.value
                for item in node.value.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            }
    return set()


def unfenced_lines(body: str, offset: int = 0):
    """Yield (line number, text) for every line outside a plain code block.

    A backtick fence that opens a directive, such as the toctree, is kept, and
    inline code is blanked out, so markup quoted as code is not read as used.

    Args:
        body: The page's Markdown.
        offset: Lines above ``body`` in the file.
    """
    fence: str | None = None
    for i, line in enumerate(body.splitlines(), offset + 1):
        m = _FENCE.match(line)
        if fence:
            if m and m[2].startswith(fence) and not m[3].strip():
                fence = None
            continue
        if m and not m[3].strip().startswith("{"):
            fence = m[2]
            continue
        yield i, _ROLE_OR_CODE.sub(lambda c: c[1] or " " * len(c[0]), line)


def check_markup(rep, body: str, page: Page, offset: int = 0):
    """Only the listed roles, and none of the inline elements a page never uses.

    Args:
        rep: The page's report.
        body: The page's Markdown.
        page: Where the page sits.
        offset: Lines above ``body`` in the file.
    """
    allowed = ROLES | marking_roles(page.workspace)
    if page.kind in INTERFACE_PAGES:
        allowed |= INTERFACE_ROLES
    registers = set(LIMITS["registers"])
    reported: set[str] = set()
    for line_no, line in unfenced_lines(body, offset):
        for m in _ROLE.finditer(line):
            name, text = m[1], m[2]
            if name == "bdg-light" and text.strip() not in registers:
                rep.error(
                    f"line {line_no}: the register badge holds "
                    f"{', '.join(sorted(registers))}, found {text!r}"
                )
            if name in allowed or name in reported:
                continue
            reported.add(name)
            if name.startswith("bdg"):
                why = "the only badges are {level} and {bdg-light}"
            elif name == "abbr":
                why = "the explanation shows on hover and a phone has no hover"
            elif name in INTERFACE_ROLES:
                why = "it describes software: only How to use and Contributing use it"
            else:
                why = "see docs/reference/components.md for the roles a page uses"
            rep.error(f"line {line_no}: the {{{name}}} role is not a component: {why}")
        for pattern, what in _INLINE_BANS:
            if pattern.search(line):
                rep.error(f"line {line_no}: {what}")


def check_hidden(rep, blocks: list[Block]):
    """No collapsible: nothing on a page is hidden behind a click, except in tabs."""
    for block in walk(blocks):
        if block.kind != "directive":
            continue
        if block.name == "dropdown":
            rep.error(
                f"line {block.line}: the dropdown directive is a collapsible, which "
                "hides its content: anything worth writing is shown, as a notice, a "
                "sentence or a page of its own"
            )
        elif "dropdown" in options(block).get("class", "").split():
            rep.error(
                f"line {block.line}: :class: dropdown makes the {block.name} a "
                "collapsible: a notice is always open"
            )


def _place(block: Block, page: Page) -> str | None:
    """Why a directive may not stand on this page, or None when it may."""
    article = page.kind == "article"
    if block.name in ("grid", "grid-item-card") and page.kind not in (
        "index",
        "introduction",
    ):
        return "card grids are for index pages and the Introduction"
    if block.name == "button-ref" and page.kind != "introduction":
        return "the only button is the Introduction's"
    if block.name == "glossary" and page.kind != "terminology":
        return "the glossary is on the Terminology page"
    if block.name == "tab-set" and not (
        article and page.category in ("grammar", "how-to")
    ):
        return "tabs are for grammar and how-to articles"
    if block.name == "toctree" and article:
        return "the menu is on index pages"
    return None


def check_directives(rep, blocks: list[Block], page: Page):
    """Only the listed directives, each where it belongs."""
    for block in walk(blocks):
        if block.kind == "quote" and not (
            page.kind == "article" and page.category == "writing"
        ):
            rep.error(
                f"line {block.line}: a block quote holds the model text of a "
                "writing article and nothing else"
            )
        if block.kind != "directive" or block.name == "dropdown":
            continue
        where = f"line {block.line}"
        if block.name not in DIRECTIVES:
            why = _NOT_A_NOTICE.get(
                block.name, "see docs/reference/components.md for the directives"
            )
            rep.error(f"{where}: the {block.name} directive is not a component: {why}")
        elif block.name == "admonition":
            wanted = TITLED_NOTICES.get(block.arg)
            if wanted is None:
                rep.error(
                    f"{where}: the notice titled '{block.arg}': a titled notice is "
                    f"{', '.join(TITLED_NOTICES)}, and nothing else is titled"
                )
            elif options(block).get("class", "").split() != [wanted]:
                rep.error(f"{where}: the {block.arg} notice takes ':class: {wanted}'")
        elif why := _place(block, page):
            rep.error(f"{where}: {block.name} on this page: {why}")


def _is_notice(block: Block) -> bool:
    return block.kind == "directive" and (
        block.name in FREE_NOTICES or block.name == "admonition"
    )


def _words(blocks: list[Block]) -> int:
    total = 0
    for block in walk(blocks):
        if block.kind == "paragraph":
            total += word_count(plain(block.text))
        elif block.kind == "list":
            total += sum(word_count(plain(item)) for item in block.items)
    return total


def check_notices(rep, blocks: list[Block], page: Page):
    """Few free notices, each short, and no notice inside another."""
    for block in walk(blocks):
        if not _is_notice(block):
            continue
        if any(_is_notice(inner) for inner in walk(block.children)):
            rep.error(f"line {block.line}: a notice holds another notice")
        if block.name in FREE_NOTICES:
            words = _words(block.children)
            if words > LIMITS["notice_max_words"]:
                rep.error(
                    f"line {block.line}: the {block.name} is {words} words (maximum "
                    f"{LIMITS['notice_max_words']})"
                )
    if page.kind != "article":
        return
    free = [b for b in walk(blocks) if b.kind == "directive" and b.name in FREE_NOTICES]
    if len(free) > LIMITS["max_notices"]:
        rep.error(
            f"{len(free)} notices (maximum {LIMITS['max_notices']}): a notice is "
            "read as a break from the text, and the fewer there are the more each "
            "is read"
        )
    important = [b for b in free if b.name == "important"]
    if len(important) > LIMITS["max_important"]:
        rep.error(
            f"line {important[1].line}: {len(important)} important notices (maximum "
            f"{LIMITS['max_important']}): one rule of the page is the one not to miss"
        )
    _opening, found = sections(blocks)
    for section in found:
        held = [
            b
            for b in section.walk()
            if b.kind == "directive" and b.name in FREE_NOTICES
        ]
        if len(held) > LIMITS["max_notices_per_section"]:
            rep.error(
                f"line {section.line}: '{section.title}' holds {len(held)} notices "
                f"(maximum {LIMITS['max_notices_per_section']})"
            )


def check_bold_labels(rep, blocks: list[Block]):
    """No paragraph is bold text alone, standing in for a heading."""
    for block in walk(blocks):
        if block.kind == "paragraph" and _BOLD_ONLY.match(block.text.strip()):
            rep.error(
                f"line {block.line}: '{plain(block.text)}' is a paragraph of bold "
                "text: a label that is needed is an H3 the template names, otherwise "
                "leave it out"
            )


def _level_problem(page: Page, link: str, badge: str) -> str | None:
    linked = page.level_of(link)
    if badge.strip().lower() not in LEVELS:
        return f"'{badge}' is not a level"
    if linked is None:
        return "a level badge follows a link to a page of another level"
    if linked == page.level:
        return f"{link} is a page of this level, which takes no level badge"
    if linked != badge.strip().lower():
        return f"the badge says {badge}, and {link} is a page of {linked.upper()}"
    return None


def check_level_badges(rep, body: str, page: Page, offset: int = 0):
    """A level badge follows a link to another level's page, and names its level."""
    for line_no, line in unfenced_lines(body, offset):
        for m in _ROLE.finditer(line):
            if m[1] != "level":
                continue
            before = _LINK_BEFORE.search(line[: m.start()])
            problem = (
                _level_problem(page, before[2], m[2])
                if before
                else "a level badge follows a link to a page of another level, "
                "and appears nowhere else"
            )
            if problem:
                rep.error(f"line {line_no}: {problem}")


def _check_links(rep, page: Page, line: int, where: str, items: list[str]):
    for item in items:
        for m in _LINK.finditer(item):
            text, link = m[1], m[2]
            if page.target(link) is None:
                continue
            if text.strip():
                rep.error(
                    f"line {line}: write the {where} link to {link} as [](...), "
                    "with no text: the build writes the page's title"
                )
            linked = page.level_of(link)
            badge = re.match(r"\s*\{level\}`", item[m.end() :])
            if linked and page.level and linked != page.level and not badge:
                rep.error(
                    f"line {line}: the {where} link to {link} is followed by its "
                    f"level, {{level}}`{linked.upper()}`"
                )


def check_article_links(rep, blocks: list[Block], page: Page):
    """Related articles and Prerequisites: empty link text, and another level's badge."""
    opening, found = sections(blocks)
    for block in opening:
        if block.is_directive("admonition", "Prerequisites"):
            for inner in walk(block.children):
                if inner.kind == "list":
                    _check_links(rep, page, inner.line, "Prerequisites", inner.items)
    for section in found:
        if section.title == "Related articles":
            for block in section.blocks:
                if block.kind == "list":
                    _check_links(rep, page, block.line, "Related articles", block.items)


def check_register_badges(rep, body: str, blocks: list[Block], offset: int = 0):
    """A register badge stands in a Notes cell and nowhere else."""
    used = sum(line.count("{bdg-light}`") for _, line in unfenced_lines(body, offset))
    in_notes = 0
    for block in walk(blocks):
        if block.kind != "table":
            continue
        columns = [i for i, cell in enumerate(block.header) if plain(cell) == "Notes"]
        for row in block.rows:
            in_notes += sum(
                row[i].count("{bdg-light}`") for i in columns if i < len(row)
            )
    if used > in_notes:
        rep.error(
            f"{used - in_notes} register badge(s) outside a Notes cell: a register "
            "badge holds the register of a phrase, in its Notes cell"
        )


def check_tabs(rep, blocks: list[Block], page: Page):
    """One tab set at most, of 2 or 3 tabs that each hold the same kind of thing."""
    tab_sets = [b for b in walk(blocks) if b.is_directive("tab-set")]
    if page.kind == "article" and len(tab_sets) > LIMITS["max_tab_sets"]:
        rep.error(
            f"{len(tab_sets)} tab sets (maximum {LIMITS['max_tab_sets']}): show the "
            "rest side by side in one table"
        )
    low, high = LIMITS["tabs"]
    for tab_set in tab_sets:
        tabs = [b for b in tab_set.children if b.is_directive("tab-item")]
        if len(tabs) != len(tab_set.children):
            rep.error(f"line {tab_set.line}: a tab set holds only tab-item blocks")
        if not low <= len(tabs) <= high:
            rep.error(
                f"line {tab_set.line}: {len(tabs)} tabs (a tab set has {low} to {high})"
            )
        kinds = set()
        for tab in tabs:
            if word_count(plain(tab.arg)) > LIMITS["tab_label_max_words"]:
                rep.error(
                    f"line {tab.line}: the tab label '{tab.arg}' is "
                    f"{word_count(plain(tab.arg))} words (maximum "
                    f"{LIMITS['tab_label_max_words']})"
                )
            for inner in tab.children:
                if inner.kind == "table":
                    kinds.add("table")
                elif inner.examples:
                    kinds.add("examples")
                else:
                    what = (
                        "a heading"
                        if inner.kind == "heading"
                        else "a notice"
                        if _is_notice(inner)
                        else "an audio block"
                        if inner.is_directive("audio-examples")
                        else f"a {inner.kind}"
                    )
                    rep.error(
                        f"line {inner.line}: the tab '{tab.arg}' holds {what}: a tab "
                        "holds a phrase table or an example block"
                    )
        if len(kinds) > 1:
            rep.error(
                f"line {tab_set.line}: the tabs hold different kinds of thing: every "
                "tab holds a phrase table, or every tab an example block"
            )


def cards(blocks: list[Block]) -> list[Card]:
    """Every card of the card grids among ``blocks``, in page order."""
    return [
        Card(
            block.line,
            plain(block.arg),
            options(block),
            block.children,
            any(_SEPARATOR.fullmatch(line.strip()) for line in block.text.splitlines()),
        )
        for grid in walk(blocks)
        if grid.is_directive("grid")
        for block in grid.children
        if block.is_directive("grid-item-card")
    ]


def _title(path: Path) -> str | None:
    if not path.is_file():
        return None
    m = re.search(r"^# (.+?)\s*$", path.read_text(encoding="utf-8"), re.M)
    return plain(m[1]) if m else None


def check_grids(rep, blocks: list[Block], page: Page, limits: dict[str, int]):
    """Every card grid is written one way, and each card names the page it opens.

    Args:
        rep: The page's report.
        blocks: The page's blocks.
        page: Where the page sits.
        limits: The words a card's sentence may hold under an H2 that sets its
            own limit, by the H2's title.
    """
    for grid in walk(blocks):
        if not grid.is_directive("grid"):
            continue
        if grid.arg != LIMITS["grid_columns"] or options(grid).get("gutter") != str(
            LIMITS["grid_gutter"]
        ):
            rep.error(
                f"line {grid.line}: a card grid is '::::{{grid}} "
                f"{LIMITS['grid_columns']}' with ':gutter: {LIMITS['grid_gutter']}'"
            )
        for block in grid.children:
            if not block.is_directive("grid-item-card"):
                rep.error(f"line {block.line}: a card grid holds only cards")
    opening, found = sections(blocks)
    groups = [("", opening), *((s.title, s.blocks) for s in found)]
    for title, held in groups:
        limit = limits.get(title, LIMITS["card_max_words"])
        for card in cards(held):
            _check_card(rep, card, page, limit)


def _check_card(rep, card: Card, page: Page, limit: int):
    where = f"line {card.line}"
    if not card.link or card.options.get("link-type") != "doc":
        rep.error(
            f"{where}: the card '{card.title}' takes ':link:' to a page and "
            "':link-type: doc'"
        )
    extras = {"img-top", "img-bottom", "img-background", "header", "footer"}
    if extras & set(card.options) or card.separated:
        rep.error(
            f"{where}: the card '{card.title}' has a header, a footer or a picture: "
            "a card is a title and one sentence"
        )
    if card.link:
        target = page.target(card.link)
        title = _title(target) if target else None
        if title is None:
            rep.error(f"{where}: the card '{card.title}' links {card.link}, no page")
        elif title != card.title:
            rep.error(
                f"{where}: the card '{card.title}' is titled as the page it opens, "
                f"'{title}'"
            )
    text = " ".join(plain(b.text) for b in card.body if b.kind == "paragraph")
    others = [b for b in card.body if b.kind != "paragraph"]
    if others or len(sentences(text)) != 1:
        rep.error(f"{where}: the card '{card.title}' holds one sentence")
    if word_count(text) > limit:
        rep.error(
            f"{where}: the card '{card.title}' is {word_count(text)} words "
            f"(maximum {limit})"
        )


def check_components(rep, body: str, page: Page, offset: int = 0, card_limits=None):
    """Hold a page to the components it may use.

    Args:
        rep: The page's report.
        body: The page's Markdown, without its front matter.
        page: Where the page sits.
        offset: Lines above ``body`` in the file.
        card_limits: The words a card's sentence may hold, by the title of the
            H2 that sets its own limit.

    Returns:
        The page's blocks.
    """
    blocks = parse(body, offset)
    check_markup(rep, body, page, offset)
    check_hidden(rep, blocks)
    check_directives(rep, blocks, page)
    check_notices(rep, blocks, page)
    check_bold_labels(rep, blocks)
    check_level_badges(rep, body, page, offset)
    check_register_badges(rep, body, blocks, offset)
    check_tabs(rep, blocks, page)
    check_grids(rep, blocks, page, card_limits or {})
    if page.kind == "article":
        check_article_links(rep, blocks, page)
    return blocks
