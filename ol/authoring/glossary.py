"""The term lists, the glossary entries, and the use of terms in an article.

A term is on the shared list (``glossary-terms.yml`` in this package) or on the
language repository's own list of the same name. Each has one entry in a
``{glossary}`` directive on the Terminology page. An article writes the first
use of a term with Sphinx's ``term`` role, or links to the article that covers
it, and the build fails on a term the glossary does not hold.

The glossary is for grammar words and words of the language taught that a
general reader would not know. A writer links to an article first, and uses the
glossary only when no article fits.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from ol.authoring.page import (
    EXPLICIT_TARGET,
    Block,
    parse,
    plain,
    sentences,
    walk,
    word_count,
)
from ol.authoring.specs_data import SPECS

TERMS_FILE = "glossary-terms.yml"
SHARED_TERMS = Path(__file__).resolve().parent / TERMS_FILE

_EXAMPLE = re.compile(r"\*Examples?:\s*.+?\*\s*$", re.S)
_LINK = re.compile(r"\[(?P<text>[^\]]*)\]\((?P<target>[^)]*)\)")
_EXTERNAL = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)


def _to_article(target: str) -> bool:
    """Whether a link goes to another page of the Coursebook, written or wanted."""
    target = target.strip()
    return bool(target) and not (_EXTERNAL.match(target) or target.startswith("#"))


def _read_terms(path: Path) -> dict[str, str]:
    """A list's forms, each mapped to its term, all in lower case."""
    if not path.is_file():
        return {}
    forms: dict[str, str] = {}
    for item in (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get(
        "terms"
    ) or []:
        term = item if isinstance(item, str) else item["term"]
        key = term.lower()
        extra = [] if isinstance(item, str) else item.get("forms", [])
        for form in (key, f"{key}s", *extra):
            forms[form.lower()] = key
    return forms


def load_terms(workspace: Path | None) -> dict[str, str]:
    """The term list for a language repository, by every form a term is written in.

    Args:
        workspace: The language repository's root.

    Returns:
        Each lower-case form, such as ``nouns``, mapped to its term, ``noun``.
    """
    forms = _read_terms(SHARED_TERMS)
    if workspace:
        forms |= _read_terms(workspace / TERMS_FILE)
    return forms


def _scanner(forms: dict[str, str]) -> re.Pattern:
    words = "|".join(re.escape(form) for form in sorted(forms, key=len, reverse=True))
    return re.compile(
        rf"\{{term\}}`(?P<linked>[^`]*)`|\{{[a-z-]+\}}`[^`]*`|`[^`]*`"
        rf"|(?<!\w)(?P<bare>{words})(?!\w)",
        re.I,
    )


def term_uses(text: str, forms: dict[str, str]) -> list[tuple[str, bool]]:
    """Each use of a listed term in inline Markdown.

    Args:
        text: Inline Markdown.
        forms: The list from ``load_terms``.

    Returns:
        The term and whether this use is linked, in order. A use is linked when
        it is written with the ``term`` role or is the text of a link to another
        page of the Coursebook, which covers it. A word inside another role or
        inside a link off the site is not a use.
    """
    if not forms:
        return []
    uses = []
    scanner = _scanner(forms)
    at = 0
    for link in [*_LINK.finditer(text), None]:
        end = link.start() if link else len(text)
        for m in scanner.finditer(text[at:end]):
            if m["bare"]:
                uses.append((forms[m["bare"].lower()], False))
            elif m["linked"] is not None:
                target = EXPLICIT_TARGET.match(m["linked"])
                name = (target[2] if target else m["linked"]).strip().lower()
                if name in forms:
                    uses.append((forms[name], True))
        if link is None:
            break
        if _to_article(link["target"]):
            uses += [(term, True) for term, _ in term_uses(link["text"], forms)]
        at = link.end()
    return uses


def links_to_article(text: str) -> bool:
    """Whether inline Markdown holds a link to another page of the Coursebook."""
    return any(_to_article(m["target"]) for m in _LINK.finditer(text))


def prose(blocks: list[Block]) -> list[tuple[int, str]]:
    """The running prose of a page: paragraphs and list items, also in admonitions.

    Args:
        blocks: The page's blocks.

    Returns:
        Each piece's line and its inline Markdown.
    """
    found: list[tuple[int, str]] = []
    for block in walk(blocks):
        if block.kind == "paragraph":
            found.append((block.line, block.text))
        elif block.kind == "list":
            found.extend((block.line, item) for item in block.items)
    return found


def check_terms(
    rep,
    blocks: list[Block],
    title: str,
    forms: dict[str, str],
):
    """The first use of each listed term in an article's prose is linked.

    A first use is linked when it is written with the ``term`` role, or when its
    sentence links to another page of the Coursebook, the article that covers
    it. A term in the title is what the page is about, and is exempt on that
    page. A term linked in the lead needs no second link in the explanation,
    and a term first used in the explanation is linked there.

    Args:
        rep: The page's report.
        blocks: The page's blocks.
        title: The H1.
        forms: The list from ``load_terms``.
    """
    seen = {term for term, _ in term_uses(title, forms)}
    for line, text in prose(blocks):
        for sentence in sentences(text) or [text]:
            to_article = links_to_article(sentence)
            for term, linked in term_uses(sentence, forms):
                if term in seen:
                    continue
                seen.add(term)
                if not (linked or to_article):
                    rep.error(
                        f"line {line}: first use of the term '{term}' is not "
                        "linked: link the sentence to the article that covers "
                        f"it, or write it as {{term}}`{term}`"
                    )


def glossary_entries(blocks: list[Block]) -> list[tuple[int, list[str], str]]:
    """The entries of a page's ``{glossary}`` directives.

    Args:
        blocks: The page's blocks.

    Returns:
        Each entry's line, its terms and its definition.
    """
    entries: list[tuple[int, list[str], list[str]]] = []
    for block in blocks:
        if not block.is_directive("glossary"):
            continue
        starting = True
        for number, line in enumerate(block.text.splitlines(), block.line + 1):
            if not line.strip() or line.startswith(":"):
                continue
            if line[0].isspace():
                entries[-1][2].append(line.strip())
                starting = True
                continue
            if starting:
                entries.append((number, [], []))
                starting = False
            entries[-1][1].append(line.partition(" : ")[0].strip())
    return [(line, terms, " ".join(text)) for line, terms, text in entries]


def check_terminology(rep, body: str, workspace: Path | None, offset: int = 0):
    """Every listed term has one entry, and every entry has the standard's shape.

    Args:
        rep: The page's report.
        body: The Terminology page's Markdown.
        workspace: The language repository's root.
        offset: Lines above ``body`` in the file.
    """
    limit = SPECS["common"]["glossary_entry_max_words"]
    blocks = parse(body, offset)
    entries = glossary_entries(blocks)
    if not entries and len(body.strip()) >= SPECS["common"]["stub_body_bytes"]:
        rep.error(
            "no {glossary} directive: the entries of the Terminology page are "
            "written in one, see `ol templates terminology.md`"
        )
    counts: dict[str, int] = {}
    for line, terms, definition in entries:
        for term in terms:
            counts[term.lower()] = counts.get(term.lower(), 0) + 1
        example = _EXAMPLE.search(definition)
        if not example:
            rep.error(
                f"line {line}: the entry '{terms[0]}' has no example: end it with "
                "*Example: ...*"
            )
        meaning = plain(definition[: example.start()] if example else definition)
        if len(sentences(meaning)) != 1:
            rep.error(
                f"line {line}: the entry '{terms[0]}' is "
                f"{len(sentences(meaning))} sentences: an entry is one sentence "
                "and one example"
            )
        if word_count(meaning) > limit:
            rep.error(
                f"line {line}: the entry '{terms[0]}' is {word_count(meaning)} "
                f"words (maximum {limit})"
            )
    for term, count in sorted(counts.items()):
        if count > 1:
            rep.error(f"the term '{term}' has {count} entries: keep one")
    for term in sorted(set(load_terms(workspace).values())):
        if term not in counts:
            rep.error(f"the listed term '{term}' has no glossary entry: add one")
