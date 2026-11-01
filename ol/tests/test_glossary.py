"""The term lists, the glossary entries and the first use of a term."""

from __future__ import annotations

from pathlib import Path

import pytest

from ol.authoring.glossary import load_terms, term_uses
from ol.authoring.validate import validate_file

CONFIG = "language: German\nlanguage_code: de\n"
TERMINOLOGY = """# Terminology

Grammar has its own words, and each one is explained here in one plain sentence with one example.

## Parts of speech

```{glossary}
Noun : Nomen
  A word that names a person, place or thing. *Example: der Hund, the dog.*

Dative case : Dativ
  The case of the indirect object. *Example: mit dem Hund, with the dog.*
```
"""


@pytest.fixture
def repository(tmp_path, monkeypatch):
    (tmp_path / "open-language.yml").write_text(CONFIG, encoding="utf-8")
    (tmp_path / "glossary-terms.yml").write_text(
        "terms:\n  - noun\n  - term: dative case\n    forms: [dative]\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("ol.authoring.glossary.SHARED_TERMS", tmp_path / "none.yml")
    return tmp_path


def terminology_errors(root: Path, text: str) -> list[str]:
    page = root / "terminology.md"
    page.write_text(text, encoding="utf-8")
    return [m for lvl, m in validate_file(page, root).items if lvl == "ERROR"]


def test_the_shared_list_is_read(tmp_path):
    (tmp_path / "list.yml").write_text("terms: []\n", encoding="utf-8")
    assert load_terms(None) == {}


def test_both_lists_are_read(repository, monkeypatch):
    (repository / "shared.yml").write_text("terms: [verb]\n", encoding="utf-8")
    monkeypatch.setattr("ol.authoring.glossary.SHARED_TERMS", repository / "shared.yml")
    forms = load_terms(repository)
    assert forms["verb"] == "verb"
    assert forms["verbs"] == "verb"
    assert forms["dative"] == "dative case"


def test_every_listed_term_with_its_entry_passes(repository):
    assert terminology_errors(repository, TERMINOLOGY) == []


def test_a_listed_term_with_no_entry_is_red(repository):
    text = TERMINOLOGY.replace("Noun : Nomen", "Pronoun : Pronomen", 1)
    assert any(
        "'noun' has no glossary entry" in m
        for m in terminology_errors(repository, text)
    )


def test_a_term_with_two_entries_is_red(repository):
    text = TERMINOLOGY.replace(
        "```\n",
        "\nNoun\n  Another word for a thing. *Example: der Tisch, the table.*\n```\n",
    )
    assert any(
        "'noun' has 2 entries" in m for m in terminology_errors(repository, text)
    )


@pytest.mark.parametrize(
    ("change", "expected"),
    [
        ((" *Example: der Hund, the dog.*", ""), "has no example"),
        (
            (" names a person, place or thing.", " names things. It is common."),
            "2 sentences",
        ),
        (
            ("A word that names", "A " + "word " * 30 + "that names"),
            "words (maximum 30)",
        ),
    ],
)
def test_a_badly_shaped_entry_is_red(repository, change, expected):
    found = terminology_errors(repository, TERMINOLOGY.replace(*change, 1))
    assert any(expected in msg for msg in found), found


def test_a_page_with_no_glossary_directive_is_red(repository):
    text = "# Terminology\n\n" + "A long page of text with no entries. " * 10 + "\n\n"
    found = terminology_errors(repository, text)
    assert any("no {glossary} directive" in msg for msg in found), found


def test_an_entry_may_give_the_term_in_several_forms(repository):
    text = TERMINOLOGY.replace("Noun : Nomen\n", "Noun\nNomen\n", 1)
    assert terminology_errors(repository, text) == []


class TestUses:
    forms = {
        "noun": "noun",
        "nouns": "noun",
        "dative case": "dative case",
        "case": "case",
    }

    def test_a_bare_word_is_a_use(self):
        assert term_uses("A noun here.", self.forms) == [("noun", False)]

    def test_a_form_is_the_term(self):
        assert term_uses("Two Nouns here.", self.forms) == [("noun", False)]

    def test_the_role_is_a_linked_use(self):
        assert term_uses("A {term}`noun`.", self.forms) == [("noun", True)]

    def test_the_role_may_name_its_target(self):
        assert term_uses("Two {term}`names <noun>`.", self.forms) == [("noun", True)]

    def test_the_longest_term_wins(self):
        assert term_uses("The dative case.", self.forms) == [("dative case", False)]

    def test_part_of_a_word_is_not_a_use(self):
        assert term_uses("A pronoun.", self.forms) == []

    def test_another_role_is_not_a_use(self):
        assert term_uses("{stack}`noun | noun`", self.forms) == []

    def test_the_text_of_a_link_is_not_a_use(self):
        assert term_uses("[A1 > Grammar > The noun](/a1/noun.md)", self.forms) == []

    def test_a_link_address_is_not_a_use(self):
        assert term_uses("[here](/a1/noun.md)", self.forms) == []


FIXTURE = Path(__file__).parent / "fixtures" / "concepts-article.md"
ARTICLE = "a1/concepts/greetings.md"
SENTENCE = "Strangers and customers get the formal greeting."
LEAD = "Saying hello in German depends"
EXPLANATION = "A German greeting is a small choice"


def article_errors(root: Path, text: str) -> list[str]:
    page = root / ARTICLE
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(text, encoding="utf-8")
    return [m for lvl, m in validate_file(page, root).items if lvl == "ERROR"]


def test_a_first_use_that_is_linked_passes(repository):
    text = FIXTURE.read_text(encoding="utf-8").replace(
        SENTENCE, f"{SENTENCE} A {{term}}`noun` comes next, then a noun.", 1
    )
    assert article_errors(repository, text) == []


def test_an_unlinked_first_use_is_red(repository):
    text = FIXTURE.read_text(encoding="utf-8").replace(
        SENTENCE, f"{SENTENCE} A noun comes next, then a {{term}}`noun`.", 1
    )
    found = article_errors(repository, text)
    assert any("first use of the term 'noun'" in msg for msg in found), found


def test_a_term_in_an_example_or_a_heading_is_exempt(repository):
    text = (
        FIXTURE.read_text(encoding="utf-8")
        .replace("## Formal or casual", "## Formal nouns", 1)
        .replace("Guten Tag, Frau Weber.", "Noun.", 1)
    )
    assert article_errors(repository, text) == []


def test_the_term_a_page_is_about_is_exempt_on_that_page(repository):
    text = (
        FIXTURE.read_text(encoding="utf-8")
        .replace("# Greetings", "# The noun", 1)
        .replace(SENTENCE, f"{SENTENCE} A noun comes next.", 1)
    )
    assert article_errors(repository, text) == []


def test_a_term_first_used_in_the_explanation_is_linked_there(repository):
    text = FIXTURE.read_text(encoding="utf-8").replace(
        EXPLANATION, f"Each noun matters. {EXPLANATION}", 1
    )
    found = article_errors(repository, text)
    assert any("first use of the term 'noun'" in m for m in found), found


def test_a_term_linked_in_the_lead_needs_no_link_in_the_explanation(repository):
    text = FIXTURE.read_text(encoding="utf-8").replace(
        LEAD, "Saying hello in German uses a {term}`noun` and depends", 1
    )
    text = text.replace(EXPLANATION, f"Each noun matters. {EXPLANATION}", 1)
    assert article_errors(repository, text) == []


def test_a_term_used_but_not_linked_in_the_lead_is_red(repository):
    text = FIXTURE.read_text(encoding="utf-8").replace(
        LEAD, "Saying hello in German uses a noun and depends", 1
    )
    text = text.replace(EXPLANATION, f"Each {{term}}`noun` matters. {EXPLANATION}", 1)
    found = article_errors(repository, text)
    assert any("first use of the term 'noun'" in m for m in found), found
