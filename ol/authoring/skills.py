"""The skills a level page lists in its front matter, and the articles that teach them.

A level page names what learners know and can do under ``skills:``::

    skills:
      - id: a1-meet-people
        kind: can
        text: "Greet people and give personal details."

The ``skills`` directive draws the texts of one kind under the level page's two
sections. An article's own front matter names one or two of the level's skill
ids under ``skills:``. These checks hold both sides to that list.
"""

from __future__ import annotations

from pathlib import Path

from ol.authoring.situations import front_matter
from ol.authoring.specs_data import SPECS

DIRECTIVE = "skills"
KINDS = ("know", "can")
SECTION_KIND = {"What learners know": "know", "What learners can do": "can"}
"""The level page's two sections, each with the kind of skill it draws."""


def list_problem(value) -> str | None:
    """Why a level page's ``skills:`` value is not a list of skills.

    Args:
        value: What the front matter holds under ``skills:``.

    Returns:
        A sentence naming the problem, or None when the value is sound.
    """
    if not isinstance(value, list):
        return "'skills:' is a list of skills, each with an id, a kind and a text"
    seen: set[str] = set()
    for number, item in enumerate(value, 1):
        if not isinstance(item, dict):
            return f"skill {number} is not a mapping with an id, a kind and a text"
        ident = item.get("id")
        if not isinstance(ident, str) or not ident.strip():
            return f"skill {number} has no 'id': a non-empty string"
        if item.get("kind") not in KINDS:
            return f"skill '{ident}' has kind {item.get('kind')!r}: use know or can"
        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            return f"skill '{ident}' has no 'text': a non-empty string"
        if ident in seen:
            return f"the skill id '{ident}' is used twice on this page"
        seen.add(ident)
    return None


def skills_of(fm: dict | None) -> list[dict] | None:
    """A page's skills, or None when it has none or the list is not sound."""
    if not fm or "skills" not in fm or list_problem(fm["skills"]):
        return None
    return fm["skills"]


def level_skill_ids(workspace: Path | None, level: str) -> set[str] | None:
    """The skill ids on a level's page, or None when there is no page to read."""
    if workspace is None:
        return None
    page = workspace / level / "index.md"
    if not page.is_file():
        return None
    return {s["id"] for s in skills_of(front_matter(page.read_text("utf-8"))) or []}


def check_article_skills(rep, fm: dict | None, workspace: Path | None, level):
    """An article names one or two of its level's skills.

    Args:
        rep: The article's report.
        fm: The article's front matter.
        workspace: The language repository's root.
        level: The article's level, or None when the page is outside the levels.
    """
    low, high = SPECS["common"]["article_skills"]
    if not fm or "skills" not in fm:
        rep.warn(
            "front matter has no 'skills:': name the skills of the level page "
            f"that this article teaches ({low} or {high}), by id"
        )
        return
    value = fm["skills"]
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        rep.error(
            "front matter 'skills:' is a list of skill ids, such as a1-meet-people"
        )
        return
    if not low <= len(value) <= high:
        rep.error(
            f"front matter 'skills:' names {len(value)} skills (an article "
            f"names {low} to {high})"
        )
    known = level_skill_ids(workspace, level) if level else None
    if known is None:
        return
    for ident in value:
        if ident not in known:
            rep.error(
                f"front matter 'skills:' names '{ident}', which is not a skill on "
                f"the level page {level}/index.md"
            )
