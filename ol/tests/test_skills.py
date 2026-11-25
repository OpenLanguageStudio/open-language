"""The skills a level page lists, and the articles that name them."""

from __future__ import annotations

from pathlib import Path

import pytest

from ol.authoring.validate import validate_file

SKILLS = (
    "skills:\n"
    "  - id: a1-meet-people\n    kind: can\n    text: Greet people and say who you are.\n"
    "  - id: a1-order-food\n    kind: can\n    text: Order food and drink.\n"
    "  - id: a1-ask-the-way\n    kind: can\n    text: Ask the way.\n"
    "  - id: a1-spell-a-name\n    kind: can\n    text: Spell a name.\n"
    "  - id: a1-articles\n    kind: know\n    text: The articles.\n"
    "  - id: a1-present\n    kind: know\n    text: The present tense.\n"
    "  - id: a1-word-order\n    kind: know\n    text: Word order.\n"
)
KNOW = "## What learners know\n\n- The articles.\n- The present tense.\n- Word order.\n"
CAN = (
    "## What learners can do\n\n- Greet someone.\n- Order food.\n"
    "- Ask the way.\n- Spell a name.\n"
)


@pytest.fixture
def level(tmp_path, write_menu):
    """A repository whose A1 page lists its skills in front matter."""
    root = write_menu(tmp_path)
    page = root / "a1/index.md"
    text = page.read_text(encoding="utf-8")
    text = text.replace(
        "html_theme.sidebar_secondary.remove:\n",
        "html_theme.sidebar_secondary.remove:\n" + SKILLS,
        1,
    )
    text = text.replace(KNOW, "## What learners know\n\n:::{skills} know\n:::\n")
    text = text.replace(CAN, "## What learners can do\n\n:::{skills} can\n:::\n")
    page.write_text(text, encoding="utf-8")
    return root


def check(root: Path, change=lambda s: s) -> list[tuple[str, str]]:
    page = root / "a1/index.md"
    page.write_text(change(page.read_text(encoding="utf-8")), encoding="utf-8")
    return validate_file(page, root).items


def errors(root: Path, change=lambda s: s) -> list[str]:
    return [m for lvl, m in check(root, change) if lvl == "ERROR"]


class TestLevelPageSkills:
    def test_a_page_with_skills_and_both_directives_passes(self, level):
        assert errors(level) == []

    @pytest.mark.parametrize(
        ("change", "expected"),
        [
            (lambda s: s.replace(SKILLS, "skills: x\n"), "'skills:' is a list"),
            (
                lambda s: s.replace("    kind: can\n", "    kind: maybe\n", 1),
                "use know or can",
            ),
            (
                lambda s: s.replace("id: a1-order-food", "id: a1-meet-people"),
                "used twice",
            ),
            (lambda s: s.replace("id: a1-order-food", "id: ''"), "no 'id'"),
            (
                lambda s: s.replace("    text: Ask the way.\n", "    text: ''\n"),
                "no 'text'",
            ),
        ],
        ids=["not a list", "bad kind", "duplicate id", "empty id", "empty text"],
    )
    def test_a_bad_skills_list_is_red(self, level, change, expected):
        assert any(expected in m for m in errors(level, change))

    def test_the_directive_argument_must_match_its_section(self, level):
        found = errors(level, lambda s: s.replace("{skills} know", "{skills} can"))
        assert any("this section draws 'know'" in m for m in found)

    def test_a_section_with_the_directive_holds_no_hand_written_list(self, level):
        found = errors(
            level,
            lambda s: s.replace(
                ":::{skills} know\n:::\n", ":::{skills} know\n:::\n\n- Extra.\n"
            ),
        )
        assert any("hand-written list" in m for m in found)

    def test_a_page_with_skills_needs_the_directive_in_both_sections(self, level):
        found = errors(
            level, lambda s: s.replace(":::{skills} can\n:::\n", "- Greet.\n")
        )
        assert any("needs ':::{skills} can'" in m for m in found)

    def test_the_directive_without_skills_is_red(self, level):
        found = errors(level, lambda s: s.replace(SKILLS, ""))
        assert any("has none" in m for m in found)

    def test_the_bullet_limits_apply_to_the_front_matter_texts(self, level):
        found = errors(
            level,
            lambda s: s.replace(
                "  - id: a1-word-order\n    kind: know\n    text: Word order.\n", ""
            ),
        )
        assert any("'What learners know' has 2 bullets" in m for m in found)

    def test_a_long_text_is_red(self, level):
        long = " ".join(["word"] * 20)
        found = errors(
            level, lambda s: s.replace("Spell a name.\n", f"Spell {long}.\n")
        )
        assert any("a bullet of 'What learners can do' is" in m for m in found)

    def test_a_can_text_starts_with_a_verb_in_its_base_form(self, level):
        found = errors(level, lambda s: s.replace("Spell a name.", "Spells a name."))
        assert any("base form" in m for m in found)

    def test_the_total_words_count_the_front_matter_texts(self, level):
        long = " ".join(["word"] * 25)
        change = lambda s: (
            s.replace("text: Order food and drink.", f"text: Order {long}.")
            .replace("text: Ask the way.", f"text: Ask {long}.")
            .replace("text: Spell a name.", f"text: Spell {long}.")
            .replace("text: The articles.", f"text: Know {long}.")
            .replace("text: Word order.", f"text: Know {long}.")
            .replace("text: The present tense.", f"text: Know {long}.")
        )
        assert any("words together" in m for m in errors(level, change))

    def test_hand_written_bullets_pass_with_a_warning(self, tmp_path, write_menu):
        root = write_menu(tmp_path)
        items = check(root)
        assert not [m for lvl, m in items if lvl == "ERROR"]
        assert any(
            lvl == "WARN" and "move them into 'skills:'" in m for lvl, m in items
        )


ARTICLE = "a1/how-to/first.md"


def article_items(root: Path, front: str) -> list[tuple[str, str]]:
    text = (Path(__file__).parent / "fixtures" / "how-to-article.md").read_text("utf-8")
    page = root / "a1/how-to/introduce-yourself.md"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(text.replace("---\n", "---\n" + front, 1), encoding="utf-8")
    (root / "open-language.yml").write_text("language: German\nlanguage_code: de\n")
    return validate_file(page, root).items


class TestArticleSkills:
    def test_one_or_two_skills_of_the_level_pass(self, level):
        items = article_items(level, "skills: [a1-meet-people, a1-order-food]\n")
        assert not [m for lvl, m in items if "skills" in m and lvl == "ERROR"]

    @pytest.mark.parametrize(
        ("front", "expected"),
        [
            ("skills: a1-meet-people\n", "is a list of skill ids"),
            ("skills: [1, 2]\n", "is a list of skill ids"),
            ("skills: []\n", "names 0 skills"),
            (
                "skills: [a1-meet-people, a1-order-food, a1-articles]\n",
                "names 3 skills",
            ),
            ("skills: [a1-nonsense]\n", "not a skill on the level page a1/index.md"),
        ],
    )
    def test_a_bad_skills_entry_is_red(self, level, front, expected):
        items = article_items(level, front)
        assert any(lvl == "ERROR" and expected in m for lvl, m in items), items

    def test_an_article_with_no_skills_warns(self, level):
        items = article_items(level, "")
        assert any(lvl == "WARN" and "no 'skills:'" in m for lvl, m in items)
