"""The rules that tie situation articles to how-to articles (ADR 2).

A situation article names the how-to articles it puts to use in its front
matter, under ``how-to:``. That list is the only place the link is written:
the build draws it as the ``how-to-links`` box on the situation and as the
``situations`` box on each how-to article it names. These checks hold both
sides to the list.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from ol.authoring.page import Block, Section, plain, walk, word_count
from ol.authoring.specs_data import SPECS
from ol.levels import LEVELS
from ol.workspace import page_path

SPEC = SPECS["types"]["situations"]
FRONT_MATTER_KEY = "how-to"
SITUATIONS_BOX = "situations"
HOW_TO_BOX = "how-to-links"


def front_matter(text: str) -> dict:
    """A page's front matter, or nothing when it has none or it does not parse.

    Args:
        text: The page's Markdown.

    Returns:
        The front matter as a dict.
    """
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}
    head, sep, _ = text[3:].partition("\n---")
    if not sep:
        return {}
    try:
        found = yaml.safe_load(head)
    except yaml.YAMLError:
        return {}
    return found if isinstance(found, dict) else {}


def _front_matter(path: Path) -> dict:
    """The front matter of the page at ``path``."""
    return front_matter(path.read_text(encoding="utf-8"))


def _name(link: str) -> str:
    """A front-matter link as a page name, such as ``a1/how-to/introduce-yourself``."""
    return link.strip().lstrip("/").removesuffix(".md")


def how_to_names(fm: dict | None) -> list[str] | None:
    """The how-to articles a situation's front matter names, or None without the key."""
    if not fm or FRONT_MATTER_KEY not in fm:
        return None
    value = fm[FRONT_MATTER_KEY]
    if not isinstance(value, list):
        return []
    return [_name(item) for item in value if isinstance(item, str)]


def situations_naming(workspace: Path | None, name: str) -> list[str]:
    """Every situation article in the workspace whose front matter names ``name``.

    Args:
        workspace: The language repository's root.
        name: A how-to article's page name, such as ``a1/how-to/introduce-yourself``.

    Returns:
        The situations' page names, sorted.
    """
    if workspace is None:
        return []
    found = []
    for level in LEVELS:
        for path in sorted((workspace / level / "situations").glob("*.md")):
            if path.name == "index.md":
                continue
            if name in (how_to_names(_front_matter(path)) or []):
                found.append(f"{level}/situations/{path.stem}")
    return found


def check_how_to_front_matter(rep, fm: dict | None, path: Path, workspace: Path | None):
    """A situation names one to three how-to articles, at its level or below."""
    names = how_to_names(fm)
    low, high = SPEC["how_to_links"]
    example = "/a1/how-to/introduce-yourself.md"
    if names is None:
        rep.error(
            f"front matter has no '{FRONT_MATTER_KEY}:' list: name the how-to "
            f"articles the scene puts to use, such as '- {example}'"
        )
        return
    if not low <= len(names) <= high:
        rep.error(
            f"front matter '{FRONT_MATTER_KEY}:' names {len(names)} articles (a "
            f"situation names {low} to {high})"
        )
    parts = page_path(path, workspace) if workspace else None
    own = LEVELS.index(parts[0]) if parts and parts[0] in LEVELS else None
    for name in names:
        bits = name.split("/")
        if len(bits) < 3 or bits[1] != "how-to" or bits[0] not in LEVELS:
            rep.error(
                f"front matter '{FRONT_MATTER_KEY}:' entry '{name}' is not a how-to "
                f"article: write it as {example}"
            )
            continue
        if workspace and not (workspace / f"{name}.md").is_file():
            rep.error(
                f"front matter '{FRONT_MATTER_KEY}:' entry '{name}' does not exist"
            )
        if own is not None and LEVELS.index(bits[0]) > own:
            rep.error(
                f"front matter '{FRONT_MATTER_KEY}:' entry '{name}' is above the "
                "situation's level: a scene puts to use what its level has taught"
            )


def _boxes(blocks: list[Block], name: str) -> list[Block]:
    return [block for block in walk(blocks) if block.is_directive(name)]


def _check_empty_box(rep, block: Block):
    if block.arg or block.children or block.text.strip():
        rep.error(
            f"line {block.line}: the {block.name} box takes no options and no "
            "body: the build writes its links from the situations' front matter"
        )


def check_situation_opening(rep, opening: list[Block], blocks: list[Block]):
    """After the lead comes the how-to-links box, if there is one, and nothing else.

    The lead itself is checked with every article's lead.
    """
    boxes = _boxes(blocks, HOW_TO_BOX)
    for block in opening[1:]:
        if not block.is_directive(HOW_TO_BOX):
            rep.error(
                f"line {block.line}: a situation sets its scene in the lead alone: "
                f"only the {HOW_TO_BOX} box may stand between the lead and the "
                "first H2"
            )
    if len(boxes) > 1:
        rep.error(f"line {boxes[1].line}: {len(boxes)} {HOW_TO_BOX} boxes (one only)")
    for block in boxes:
        _check_empty_box(rep, block)


def check_retired_boxes(rep, blocks: list[Block], fm: dict | None):
    """The two boxes are retired: their links are drawn under Related articles.

    Args:
        rep: The page's report.
        blocks: The page's blocks.
        fm: The page's front matter.
    """
    has_related = bool(fm) and "related" in fm
    for name in (SITUATIONS_BOX, HOW_TO_BOX):
        for block in _boxes(blocks, name):
            message = (
                f"line {block.line}: the {name} box is retired: its links are "
                "drawn under Related articles, so remove the box"
            )
            if has_related:
                rep.error(message)
            else:
                rep.warn(message)


def check_situation(rep, found: list[Section]):
    """A situation shows a scene and teaches nothing itself."""
    for section in found:
        for block in section.walk():
            if block.kind == "table":
                rep.error(
                    f"table (line {block.line}): a situation teaches nothing "
                    "itself: phrases go in the how-to article it links"
                )
            elif block.is_directive("ol-examples"):
                rep.error(
                    f"line {block.line}: an examples box on a situation: the "
                    "scene's lines are its examples, under Hear it in practice"
                )
            elif block.is_directive("admonition"):
                rep.error(
                    f"line {block.line}: the {block.arg} notice on a situation: a "
                    "situation has no summary and no list of mistakes"
                )
    listen = next((s for s in found if s.title == "What to listen for"), None)
    if listen is None:
        return
    low, high = SPEC["listen_bullets"]
    lists = [block for block in listen.blocks if block.kind == "list"]
    items = [item for block in lists for item in block.items]
    if len(lists) != 1 or any(block.kind != "list" for block in listen.blocks):
        rep.error(
            f"line {listen.line}: 'What to listen for' is one list of bullets, "
            "and nothing else"
        )
    if not low <= len(items) <= high:
        rep.error(
            f"line {listen.line}: 'What to listen for' has {len(items)} bullets "
            f"(it has {low} to {high})"
        )
    limit = SPEC["listen_bullet_max_words"]
    for item in items:
        if word_count(plain(item)) > limit:
            rep.error(
                f"line {listen.line}: the bullet '{plain(item)[:40]}' is "
                f"{word_count(plain(item))} words (maximum {limit})"
            )


def check_situation_track(rep, block, where: str):
    """A situation's track is a scene: a dialogue, correspondence or passage."""
    if block.mode not in SPEC["modes"]:
        rep.error(
            f"{where}: a situation's track is a {', '.join(SPEC['modes'])} block, "
            f"not {block.mode}"
        )
    if block.mode == "dialogue":
        low, high = SPEC["dialogue_lines"]
        if not low <= len(block.examples) <= high:
            rep.error(
                f"{where}: the dialogue has {len(block.examples)} lines (a scene "
                f"has {low} to {high})"
            )


def check_situation_tracks(rep, count: int):
    """A situation has one track, or two for two versions of one scene."""
    if count > SPEC["max_tracks"]:
        rep.error(
            f"{count} audio blocks (maximum {SPEC['max_tracks']}): a second block "
            "is a second version of the same scene, and a different scene is its "
            "own page"
        )


def check_situations_box(
    rep,
    opening: list[Block],
    blocks: list[Block],
    found: list[Section],
    path: Path,
    workspace: Path | None,
):
    """A how-to article keeps ``## When to use it`` until a situation names it.

    Once a situation names the article, the situations are drawn under Related
    articles and take the section's place. The retired box is allowed where it
    stood, in the opening, after the explanation and any Prerequisites.
    """
    boxes = _boxes(blocks, SITUATIONS_BOX)
    parts = page_path(path, workspace) if workspace else None
    name = "/".join(parts) if parts else None
    naming = situations_naming(workspace, name) if name else []
    when = next((s for s in found if s.title == "When to use it"), None)
    if naming and when and not boxes:
        rep.error(
            f"line {when.line}: {', '.join(naming)} names this article, so the "
            "situations are drawn under Related articles: remove 'When to use it'"
        )
    if boxes and workspace and not naming:
        rep.error(
            f"line {boxes[0].line}: the {SITUATIONS_BOX} box on an article no "
            "situation names: keep '## When to use it' until one does"
        )
    if boxes and when:
        rep.error(
            f"line {when.line}: 'When to use it' and the {SITUATIONS_BOX} box: the "
            "box takes the section's place, remove the section"
        )
    if not naming and not when and not boxes:
        rep.error("a how-to article needs the section '## When to use it'")
    if len(boxes) > 1:
        rep.error(
            f"line {boxes[1].line}: {len(boxes)} {SITUATIONS_BOX} boxes (one only)"
        )
    for block in boxes:
        _check_empty_box(rep, block)
        if not any(held is block for held in opening):
            rep.error(
                f"line {block.line}: the {SITUATIONS_BOX} box stands in the "
                "opening, after the explanation and any Prerequisites"
            )
