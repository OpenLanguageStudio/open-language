"""The page standard's measurable rules, as read from ``docs/reference/page-standard.md``.

Each function checks one part of the standard and reports to a page's report.
The limits are in ``specs.yml``. The rules that belong to the menu are in
``menu.py`` and the glossary's are in ``glossary.py``.
"""

from __future__ import annotations

import re
from itertools import pairwise
from pathlib import Path

from ol.authoring.glossary import check_terms, load_terms, prose
from ol.authoring.menu import LEVELS, MENU_CATEGORIES
from ol.authoring.page import (
    Block,
    Section,
    link_targets,
    parse,
    plain,
    sections,
    sentences,
    walk,
    word_count,
)
from ol.authoring.specs_data import SPECS

COMMON = SPECS["common"]
SIDEBAR_KEY = "html_theme.sidebar_secondary.remove"

_SECOND_PERSON = re.compile(r"\byou(?:r|rs|rself)?\b", re.I)
_DIGIT = re.compile(r"\d")
_CLOSING_PUNCTUATION = re.compile(r"[.,:;!?…]$")
_WORD = re.compile(r"[^\W\d_]+")
_EMPHASIS = re.compile(
    r"(?<![\\*])\*{1,3}(?:[^*\\]|\\.)+\*{1,3}|\{[a-z-]+\}`[^`]*`|`[^`]*`"
)
_QUOTED = re.compile(r"[\"“„][^\"”“]*[\"”“]")
_OPTION = re.compile(r"^:[a-z-]+:")
_NOT_BASE_FORM = re.compile(r"[^su]s$|\w{3}ing$", re.I)


def heading_blocks(blocks: list[Block]) -> list[Block]:
    """Every heading of a page, in order."""
    return [block for block in blocks if block.kind == "heading"]


def _section(found: list[Section], title: str) -> Section | None:
    return next((section for section in found if section.title == title), None)


def _keywords(fm: dict | None) -> list[str]:
    meta = ((fm or {}).get("myst") or {}).get("html_meta") or {}
    keywords = meta.get("keywords") or ""
    if isinstance(keywords, list):
        return [str(keyword).strip() for keyword in keywords]
    return [keyword.strip() for keyword in str(keywords).split(",")]


def _learner_phrasings(fm, language, level, category) -> list[str]:
    """The keywords that say what the page is about, not where it sits."""
    name = (language or "").lower()
    generic = {
        name,
        f"{name} learning",
        f"{name} language",
        f"{name} grammar",
        (level or "").lower(),
        (category or "").lower(),
    }
    return [k.lower() for k in _keywords(fm) if k and k.lower() not in generic]


def check_opening(rep, opening, fm, language, level, category):
    """The lead, the explanation and the optional Prerequisites.

    Args:
        rep: The page's report.
        opening: The blocks between the H1 and the first H2.
        fm: The front matter.
        language: The language taught.
        level: The page's level.
        category: The page's category.
    """
    if not opening or opening[0].kind != "paragraph":
        rep.error(
            "the first thing under the title is the lead paragraph: one or two "
            "sentences on what the page covers"
        )
        return
    lead = opening[0]
    lead_text = plain(lead.text)
    lead_words = word_count(lead_text)
    if not COMMON["lead_min_words"] <= lead_words <= COMMON["lead_max_words"]:
        rep.error(
            f"line {lead.line}: lead paragraph is {lead_words} words (it has "
            f"{COMMON['lead_min_words']} to {COMMON['lead_max_words']})"
        )
    count = len(sentences(lead_text))
    if count > COMMON["lead_max_sentences"]:
        rep.error(
            f"line {lead.line}: lead paragraph is {count} sentences (maximum "
            f"{COMMON['lead_max_sentences']})"
        )
    phrasings = _learner_phrasings(fm, language, level, category)
    if phrasings and not any(p in lead_text.lower() for p in phrasings):
        rep.error(
            f"line {lead.line}: the lead paragraph uses none of the phrasings in "
            "html_meta.keywords: use the main one a learner would search with"
        )

    if len(opening) < 2 or opening[1].kind != "paragraph":
        rep.error(
            "the second paragraph under the title is the explanation: the one "
            "idea of the page in plain language"
        )
    else:
        explanation = opening[1]
        words = word_count(plain(explanation.text))
        low, high = COMMON["explanation_min_words"], COMMON["explanation_max_words"]
        if not low <= words <= high:
            rep.error(
                f"line {explanation.line}: explanation paragraph is {words} words "
                f"(it has {low} to {high})"
            )
        if lead_words + words > COMMON["opening_max_words"]:
            rep.error(
                f"the lead and explanation are {lead_words + words} words together "
                f"(maximum {COMMON['opening_max_words']})"
            )
    for block in opening[2:]:
        if not block.is_directive("admonition", "Prerequisites"):
            rep.error(
                f"line {block.line}: only a Prerequisites admonition stands "
                "between the explanation paragraph and the first H2"
            )


def check_prerequisites_place(rep, opening, found):
    """Prerequisites stand after the two opening paragraphs, before the first H2."""
    misplaced = [
        block
        for block in opening[:2]
        if block.is_directive("admonition", "Prerequisites")
    ]
    for section in found:
        misplaced += [
            block
            for block in section.walk()
            if block.is_directive("admonition", "Prerequisites")
        ]
    for block in misplaced:
        rep.error(
            f"line {block.line}: Prerequisites go after the two opening "
            "paragraphs, before the first H2"
        )


def check_title(rep, title):
    """The H1 is short and has no number. ``validate`` checks level and category."""
    limit = COMMON["h1_max_words"]
    if word_count(title) > limit:
        rep.error(f"title '{title}' is {word_count(title)} words (maximum {limit})")
    if _DIGIT.search(title):
        rep.error(f"title '{title}' has a number: a title carries none")


_ING_VERBS = {"bring", "cling", "fling", "ring", "sing", "sling", "spring", "sting"}
_ING_VERBS |= {"string", "swing", "wring"}
_NOT_A_VERB = {"a", "an", "the", "my", "your", "our", "some", "this", "these"}
_NOT_A_VERB |= {"that", "those", "what", "when", "where", "which", "who", "how"}


def check_how_to_title(rep, title):
    """A how-to title finishes the phrase "How to ...", so it opens on a verb.

    A first word ending in -ing ("Ordering food") or a word that cannot be a
    verb ("The weather") is reported. Any other word is taken to be a verb.
    """
    words = _WORD.findall(title)
    first = words[0].lower() if words else ""
    if first.endswith("ing") and first not in _ING_VERBS:
        rep.error(
            f"title '{title}' opens on '{words[0]}': a how-to title finishes "
            '"How to ...", so write the verb in its base form, as in '
            "'Introduce yourself'"
        )
    elif first in _NOT_A_VERB:
        rep.error(
            f"title '{title}' opens on '{words[0]}': a how-to title finishes "
            "\"How to ...\", so it opens on a verb, as in 'Order food and drink'"
        )


def taught_words(blocks: list[Block]) -> tuple[set[str], set[str]]:
    """The words in the language taught on a page, and the page's English words.

    An example gives its sentence in the language taught and its translation in
    English. Prose outside emphasis and roles is English too.

    Args:
        blocks: The page's blocks.

    Returns:
        The lower-case words of each.
    """
    taught: set[str] = set()
    english: set[str] = set()
    for block in walk(blocks):
        if block.examples or block.is_directive("audio-examples"):
            for line in block.text.splitlines():
                if _OPTION.match(line) or not line.strip():
                    continue
                words = _WORD.findall(plain(line.lstrip(": ")).lower())
                (english if line.startswith(":") else taught).update(words)
    for _, text in prose(blocks):
        english.update(_WORD.findall(plain(_EMPHASIS.sub(" ", text)).lower()))
    return taught, english


def check_headings(rep, blocks, parent_title):
    """Heading levels, caps, length, wording and what a heading may repeat."""
    taught, english = taught_words(blocks)
    parents = {1: parent_title}
    counts = {2: 0, 3: 0}
    for block in heading_blocks(blocks):
        where = f"line {block.line}"
        text = plain(block.text)
        if block.level == 1:
            continue
        if block.level > 3:
            rep.error(f"{where}: H{block.level} '{text}': only H1, H2 and H3 exist")
            continue
        counts[block.level] += 1
        if word_count(text) > COMMON["heading_max_words"]:
            rep.error(
                f"{where}: heading '{text}' is {word_count(text)} words (maximum "
                f"{COMMON['heading_max_words']})"
            )
        if _DIGIT.search(text):
            rep.error(f"{where}: heading '{text}' has a number")
        if _CLOSING_PUNCTUATION.search(text):
            rep.error(f"{where}: heading '{text}' ends in punctuation")
        if _SECOND_PERSON.search(_QUOTED.sub(" ", _EMPHASIS.sub(" ", block.text))):
            rep.error(f"{where}: heading '{text}' addresses the reader")
        parent = parents.get(block.level - 1, "")
        if text.lower() == parent.lower():
            rep.error(f"{where}: heading '{text}' repeats the heading above it")
        parents[block.level] = text
        unmarked = _EMPHASIS.sub(" ", block.text)
        for word in _WORD.findall(plain(unmarked)):
            if word.lower() in taught and word.lower() not in english:
                rep.error(
                    f"{where}: the word '{word}' in heading '{text}' is in the "
                    "language taught: put it in italics"
                )
    if counts[2] > COMMON["max_h2"]:
        rep.error(
            f"{counts[2]} H2 (maximum {COMMON['max_h2']}): a page that needs more "
            "is two pages"
        )
    if counts[3] > COMMON["max_h3"]:
        rep.error(f"{counts[3]} H3 (maximum {COMMON['max_h3']})")


def _h3_allowed(section: Section, ctype: str) -> bool:
    if ctype == "grammar":
        return section.title not in SPECS["types"]["grammar"]["no_h3_sections"]
    if ctype == "how-to":
        return section.title in ("Key phrases", "Hear it in practice")
    if ctype == "writing":
        return section.title.startswith("Example: ")
    return False


def check_h3_places(rep, found, ctype):
    """An H3 stands only where the category's template names one."""
    for section in found:
        if _h3_allowed(section, ctype):
            continue
        for block in section.blocks:
            if block.kind == "heading" and block.level == 3:
                rep.error(
                    f"line {block.line}: H3 '{plain(block.text)}' under "
                    f"'{section.title}': a {ctype} article has no H3 there"
                )


def check_table(rep, block, ctype, translation_headers):
    """One table's columns and header row."""
    where = f"table (line {block.line})"
    limit = COMMON["table_max_columns"]
    if ctype == "grammar":
        limit = COMMON["forms_table_max_columns"]
    columns = len(block.header)
    if columns > limit:
        rep.error(f"{where}: {columns} columns (maximum {limit})")
    if not any(cell.strip() for cell in block.header):
        rep.error(f"{where}: the header row is empty")
    elif not block.header[0].strip() and ctype != "grammar":
        rep.error(
            f"{where}: the first header cell is empty: only a table of forms "
            "in a grammar article leaves it empty"
        )
    elif not all(cell.strip() for cell in block.header[1:]):
        rep.error(
            f"{where}: a column has an empty header cell: name every column, and "
            "put a translation under its phrase with the stack role"
        )
    for cell in block.header:
        if translation_headers.search(plain(cell)):
            rep.error(
                f"{where}: '{plain(cell)}' is a column for the translation: put "
                "the translation under its phrase with the stack role, and "
                "anything else in a Notes column"
            )


def check_tables(rep, blocks, ctype, extra_headers):
    """Every table on the page.

    Args:
        rep: The page's report.
        blocks: The page's blocks.
        ctype: The article's category.
        extra_headers: The language repository's own translation headers.
    """
    words = [*COMMON["translation_headers"], *extra_headers]
    alternatives = "|".join(re.escape(word) for word in words)
    translation_headers = re.compile(rf"\b(?:{alternatives})\b", re.I)
    for block in walk(blocks):
        if block.kind == "table":
            check_table(rep, block, ctype, translation_headers)


def check_prose(rep, blocks):
    """Sentence and paragraph limits."""
    limit = COMMON["sentence_max_words"]
    total_words = total_sentences = 0
    for line, text in prose(blocks):
        for sentence in sentences(plain(text)):
            words = word_count(sentence)
            total_words += words
            total_sentences += 1
            if words > limit:
                start = " ".join(sentence.split()[:6])
                rep.error(
                    f"line {line}: sentence of {words} words (maximum {limit}): "
                    f"'{start} ...'"
                )
    limit = COMMON["paragraph_max_sentences"]
    for block in walk(blocks):
        if block.kind == "paragraph":
            count = len(sentences(plain(block.text)))
            if count > limit:
                rep.error(
                    f"line {block.line}: paragraph of {count} sentences (maximum "
                    f"{limit})"
                )
    average = total_words / total_sentences if total_sentences else 0
    if average > COMMON["sentence_average_words"]:
        rep.warn(
            f"prose averages {average:.1f} words a sentence (aim for "
            f"{COMMON['sentence_average_words']} or fewer)"
        )


def _slot(title: str, parts: list[dict]) -> int | None:
    other = None
    for i, part in enumerate(parts):
        if part.get("other"):
            other = i
        elif title == part.get("heading") or (
            "match" in part and re.search(part["match"], title)
        ):
            return i
    return other


def _label(part: dict) -> str:
    return part.get("heading") or part.get("label") or "other sections"


def check_section_order(rep, found, ctype, parts):
    """The H2s are the category's sections, in its order and number."""
    slots = []
    for section in found:
        slot = _slot(section.title, parts)
        if slot is None:
            rep.error(
                f"line {section.line}: '{section.title}' is not a section of a "
                f"{ctype} article: its sections are "
                f"{', '.join(_label(part) for part in parts)}"
            )
            continue
        slots.append((slot, section))
    for i, part in enumerate(parts):
        low, high = part.get("count", [1, 1])
        count = sum(1 for slot, _ in slots if slot == i)
        if count < low:
            what = (
                f"at least {low} sections of its own"
                if part.get("other")
                else f"the section '## {_label(part)}'"
            )
            rep.error(f"a {ctype} article needs {what}")
        elif count > high:
            rep.error(f"{count} '{_label(part)}' sections (maximum {high})")
    for (earlier, _), (later, section) in pairwise(slots):
        if later < earlier:
            rep.error(
                f"line {section.line}: '{section.title}' is out of order: a "
                f"{ctype} article runs {', '.join(_label(part) for part in parts)}"
            )
            break


def check_hear_it(rep, found):
    """The Hear it in practice section holds the audio block."""
    section = _section(found, "Hear it in practice")
    if section and not any(
        block.is_directive("audio-examples") for block in section.walk()
    ):
        rep.error(f"line {section.line}: 'Hear it in practice' has no audio block")


def check_track_headings(rep, found):
    """Under Hear it in practice, an H3 gives one of several tracks its own heading."""
    section = _section(found, "Hear it in practice")
    if section is None:
        return
    heads: list[Block] = []
    parts: list[list[Block]] = [[]]
    for block in section.blocks:
        if block.kind == "heading" and block.level == 3:
            heads.append(block)
            parts.append([])
        else:
            parts[-1].append(block)
    if not heads:
        return
    tracks = [
        [block for block in walk(part) if block.is_directive("audio-examples")]
        for part in parts
    ]
    if sum(map(len, tracks)) < 2:
        rep.error(
            f"line {heads[0].line}: H3 '{plain(heads[0].text)}' under 'Hear it in "
            "practice': an H3 there names one of several audio blocks"
        )
        return
    for block in tracks[0]:
        rep.error(
            f"audio block (line {block.line}) under 'Hear it in practice' has no H3: "
            "when one block has its own H3, every block does"
        )
    for head, held in zip(heads, tracks[1:], strict=True):
        if len(held) != 1:
            rep.error(
                f"line {head.line}: H3 '{plain(head.text)}' under 'Hear it in "
                f"practice' holds {len(held)} audio blocks: each H3 holds one"
            )


def check_related(rep, found):
    """Related articles is links only, and comes only when there are some."""
    section = _section(found, "Related articles")
    if section is None:
        return
    lists = [block for block in section.blocks if block.kind == "list"]
    if not lists:
        rep.error(
            f"line {section.line}: 'Related articles' has no links: leave the "
            "section out"
        )
    for block in section.blocks:
        if block.kind != "list":
            rep.error(f"line {block.line}: 'Related articles' holds only links")
    for block in lists:
        for item in block.items:
            if not link_targets(item):
                rep.error(
                    f"line {block.line}: 'Related articles' item without a link: "
                    f"'{plain(item)[:40]}'"
                )


def _admonition_titled(section: Section, title: str) -> bool:
    return any(block.is_directive("admonition", title) for block in section.walk())


def check_grammar(rep, found):
    """Common mistakes close the body, and each section keeps few examples."""
    check_track_headings(rep, found)
    body = [
        section
        for section in found
        if section.title not in ("Hear it in practice", "Summary", "Related articles")
    ]
    if body and not _admonition_titled(body[-1], "Common mistakes"):
        rep.error(
            f"line {body[-1].line}: the last body section, '{body[-1].title}', "
            "holds the Common mistakes admonition"
        )
    limit = SPECS["types"]["grammar"]["max_examples_per_section"]
    for section in body:
        pairs = sum(
            1
            for block in section.walk()
            if block.examples
            for line in block.text.splitlines()
            if line.startswith(": ")
        )
        if pairs > limit:
            rep.error(
                f"line {section.line}: '{section.title}' has {pairs} inline "
                f"examples (maximum {limit})"
            )


def check_how_to(rep, found):
    """Key phrases are grouped under H3s, and the Culture note stays short."""
    check_track_headings(rep, found)
    limits = SPECS["types"]["how-to"]
    phrases = _section(found, "Key phrases")
    if phrases:
        if not any(
            block.kind == "heading" and block.level == 3 for block in phrases.blocks
        ):
            rep.error(
                f"line {phrases.line}: 'Key phrases' groups its phrases by "
                "situation, under H3 group names"
            )
        for block in phrases.walk():
            if block.kind == "table" and len(block.header) > 2:
                rep.error(
                    f"table (line {block.line}): {len(block.header)} columns "
                    "under 'Key phrases' (maximum 2)"
                )
    culture = _section(found, "Culture note")
    if culture:
        words = sum(word_count(plain(text)) for _, text in prose(culture.blocks))
        if words > limits["culture_note_max_words"]:
            rep.error(
                f"line {culture.line}: 'Culture note' is {words} words (maximum "
                f"{limits['culture_note_max_words']})"
            )


def check_writing(rep, found):
    """Each example has its model text, a short note and its own audio section."""
    limit = SPECS["types"]["writing"]["example_note_max_words"]
    for section in found:
        if not section.title.startswith("Example: "):
            continue
        before: list[Block] = []
        heard = False
        for block in section.blocks:
            if block.kind == "heading" and block.level == 3:
                heard = heard or plain(block.text) == "Hear it in practice"
                if heard:
                    break
            before.append(block)
        if not heard:
            rep.error(f"line {section.line}: '{section.title}' has no H3 audio section")
            continue
        quotes = [i for i, block in enumerate(before) if block.kind == "quote"]
        note = before[quotes[-1] + 1 :] if quotes else before
        words = sum(
            word_count(plain(block.text)) for block in note if block.kind == "paragraph"
        )
        if words > limit:
            rep.error(
                f"line {section.line}: the note in '{section.title}' is {words} "
                f"words (maximum {limit})"
            )


def check_vocabulary(rep, found):
    """The words stand in one two-column table with stacked translations."""
    section = _section(found, "The words")
    if section is None:
        return
    tables = [block for block in section.blocks if block.kind == "table"]
    if len(tables) != 1:
        rep.error(
            f"line {section.line}: 'The words' holds one table, found {len(tables)}"
        )
    for table in tables:
        if len(table.header) != 2 or plain(table.header[-1]) != "Notes":
            rep.error(
                f"table (line {table.line}): the word table has two columns, the "
                "word and Notes"
            )
        for row in table.rows:
            if "{stack}`" not in row[0]:
                rep.error(
                    f"table (line {table.line}): '{plain(row[0])[:30]}' is not "
                    "written with the stack role"
                )
                break


def word_table_rows(found) -> int | None:
    """The rows of the word table, or None when the page has none."""
    section = _section(found, "The words")
    tables = [b for b in section.blocks if b.kind == "table"] if section else []
    return len(tables[0].rows) if tables else None


CATEGORY_CHECKS = {
    "grammar": check_grammar,
    "how-to": check_how_to,
    "writing": check_writing,
    "vocabulary": check_vocabulary,
}


def check_article(rep, body, fm, ctype, spec, context):
    """Hold an article to the frame and to its category.

    Args:
        rep: The page's report.
        body: The article's Markdown.
        fm: The front matter.
        ctype: The article's category.
        spec: The category's entry in ``specs.yml``.
        context: The article's ``language``, ``level``, ``workspace``,
            ``translation_headers`` and ``offset``, the lines above ``body``.

    Returns:
        The article's H2 sections.
    """
    blocks = parse(body, context["offset"])
    titles = [b for b in heading_blocks(blocks) if b.level == 1]
    title = plain(titles[0].text) if titles else ""
    opening, found = sections(blocks)
    if title:
        check_title(rep, title)
    if title and ctype == "how-to":
        check_how_to_title(rep, title)
    check_opening(rep, opening, fm, context["language"], context["level"], ctype)
    check_prerequisites_place(rep, opening, found)
    check_headings(rep, blocks, title)
    check_h3_places(rep, found, ctype)
    check_tables(rep, blocks, ctype, context["translation_headers"])
    check_prose(rep, blocks)
    check_section_order(rep, found, ctype, spec["sections"])
    check_hear_it(rep, found)
    check_related(rep, found)
    CATEGORY_CHECKS[ctype](rep, found)
    check_terms(rep, blocks, title, load_terms(context["workspace"]))
    if fm is not None and SIDEBAR_KEY in fm:
        rep.error(
            f"front matter has {SIDEBAR_KEY}: on-this-page navigation shows on "
            "every article"
        )
    return found


def check_index_sidebar(rep, fm):
    """On-this-page navigation is removed from every index page."""
    if fm is None or SIDEBAR_KEY not in fm:
        rep.error(
            f"front matter needs {SIDEBAR_KEY}: an index page has no on-this-page "
            "navigation"
        )


def check_category_index(rep, body, offset=0):
    """A category index opens with one to three plain sentences."""
    blocks = parse(body, offset)
    count = 0
    for block in blocks:
        if block.is_directive("toctree"):
            break
        if block.kind == "paragraph":
            count += len(sentences(plain(block.text)))
    limit = COMMON["index_max_sentences"]
    if not 1 <= count <= limit:
        rep.error(
            f"the page opens with {count} sentences before its toctree (it has 1 "
            f"to {limit}): say what its articles have in common"
        )


def _bullets(rep, section, low, high, max_words):
    """The items of a section's list, checked for number and length."""
    items = [
        item for block in section.blocks if block.kind == "list" for item in block.items
    ]
    if not low <= len(items) <= high:
        expected = f"{low}" if low == high else f"{low} to {high}"
        rep.error(
            f"line {section.line}: '{section.title}' has {len(items)} bullets "
            f"(it has {expected})"
        )
    for item in items:
        if word_count(plain(item)) > max_words:
            rep.error(
                f"line {section.line}: a bullet of '{section.title}' is "
                f"{word_count(plain(item))} words (maximum {max_words}): "
                f"'{plain(item)[:40]}'"
            )
    return items


def _section_words(section: Section) -> int:
    return sum(word_count(plain(text)) for _, text in prose(section.blocks))


def _expect_titles(rep, found, expected):
    titles = [section.title for section in found]
    if titles != expected:
        rep.error(
            "the sections are "
            f"{', '.join(repr(t) for t in expected)}, in that order, and no "
            f"others (found {', '.join(repr(t) for t in titles) or 'none'})"
        )


def _check_toctree_place(rep, blocks, h2s_before):
    """The toctree comes after the first ``h2s_before`` H2s of the page."""
    seen = 0
    for block in blocks:
        if block.is_directive("toctree"):
            if seen != h2s_before:
                rep.error(
                    f"the toctree comes after {h2s_before} H2 sections, found "
                    f"{seen} before it"
                )
            return
        if block.kind == "heading" and block.level == 2:
            seen += 1


def check_level_index(rep, body, level, offset=0):
    """The level overview page, part by part."""
    limits = SPECS["level_page"]
    blocks = parse(body, offset)
    titles = [b for b in heading_blocks(blocks) if b.level == 1]
    if titles and plain(titles[0].text) != level.upper():
        rep.error(f"the title of a level page is the bare level name, {level.upper()}")
    opening, found = sections(blocks)
    lead = opening[0] if opening and opening[0].kind == "paragraph" else None
    words = word_count(plain(lead.text)) if lead else 0
    if not lead:
        rep.error("the first thing under the title is the lead paragraph")
    elif words > limits["lead_max_words"]:
        rep.error(
            f"line {lead.line}: lead paragraph is {words} words (maximum "
            f"{limits['lead_max_words']})"
        )
    _expect_titles(
        rep, found, ["What learners know", "What learners can do", "Additional reading"]
    )
    know = _section(found, "What learners know")
    can_do = _section(found, "What learners can do")
    total = words
    if know:
        low, high = limits["know_bullets"]
        _bullets(rep, know, low, high, limits["bullet_max_words"])
        total += _section_words(know)
    if can_do:
        low, high = limits["can_do_bullets"]
        for item in _bullets(rep, can_do, low, high, limits["bullet_max_words"]):
            first = plain(item).split()[0] if plain(item) else ""
            if _NOT_BASE_FORM.search(first):
                rep.error(
                    f"line {can_do.line}: the bullet '{plain(item)[:40]}' does not "
                    "start with a verb in its base form"
                )
        total += _section_words(can_do)
    if total > limits["overview_max_words"]:
        rep.error(
            f"the lead and the two lists are {total} words together (maximum "
            f"{limits['overview_max_words']})"
        )
    _check_toctree_place(rep, blocks, 2)
    reading = _section(found, "Additional reading")
    if reading:
        links = [
            target
            for block in reading.blocks
            if block.kind == "list"
            for item in block.items
            for target in link_targets(item)
        ]
        if not links:
            rep.error(f"line {reading.line}: 'Additional reading' has no links")
        for target in links:
            if not target.startswith(("http://", "https://")):
                rep.error(
                    f"line {reading.line}: 'Additional reading' holds external "
                    f"links only, found {target}"
                )


def _page(target: str) -> str:
    return target.lstrip("./").removesuffix(".md")


def check_introduction(rep, body, workspace: Path, offset=0):
    """The Introduction page, part by part."""
    limits = SPECS["introduction_page"]
    blocks = parse(body, offset)
    opening, found = sections(blocks)
    lead = opening[0] if opening and opening[0].kind == "paragraph" else None
    if not lead:
        rep.error("the first thing under the title is the lead paragraph")
    elif word_count(plain(lead.text)) > limits["lead_max_words"]:
        rep.error(
            f"line {lead.line}: lead is {word_count(plain(lead.text))} words "
            f"(maximum {limits['lead_max_words']})"
        )
    _expect_titles(
        rep, found, ["How the course works", "Levels", "Categories", "Where to start"]
    )
    _check_toctree_place(rep, blocks, 4)

    how = _section(found, "How the course works")
    if how and _section_words(how) > limits["how_max_words"]:
        rep.error(
            f"line {how.line}: 'How the course works' is {_section_words(how)} "
            f"words (maximum {limits['how_max_words']})"
        )

    levels = [lvl for lvl in LEVELS if (workspace / lvl / "index.md").is_file()]
    if section := _section(found, "Levels"):
        items = _bullets(
            rep, section, len(levels), len(levels), limits["level_bullet_max_words"]
        )
        linked = [_page(target) for item in items for target in link_targets(item)[:1]]
        if linked != [f"{level}/index" for level in levels]:
            rep.error(
                f"line {section.line}: 'Levels' has one bullet per level that "
                "exists, each linking to its level page"
            )
    if section := _section(found, "Categories"):
        items = _bullets(
            rep,
            section,
            len(MENU_CATEGORIES),
            len(MENU_CATEGORIES),
            limits["category_bullet_max_words"],
        )
        expected = [
            f"{level}/{category}/index"
            for category in MENU_CATEGORIES
            for level in levels[:1]
        ]
        linked = [_page(target) for item in items for target in link_targets(item)[:1]]
        if linked != expected:
            rep.error(
                f"line {section.line}: 'Categories' links, in order, to "
                f"{', '.join(expected)}"
            )
    if section := _section(found, "Where to start"):
        low, high = limits["start_bullets"]
        items = _bullets(rep, section, low, high, limits["page_max_words"])
        if any(not link_targets(item) for item in items):
            rep.error(f"line {section.line}: every 'Where to start' bullet has a link")
        if items and "terminology" not in [_page(t) for t in link_targets(items[-1])]:
            rep.error(
                f"line {section.line}: the last 'Where to start' bullet links to "
                "the glossary, terminology.md"
            )
    total = sum(word_count(plain(text)) for _, text in prose(blocks))
    if total > limits["page_max_words"]:
        rep.error(f"the page is {total} words (maximum {limits['page_max_words']})")
