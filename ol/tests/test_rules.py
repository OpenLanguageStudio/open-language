"""Findings cite the writing rule they enforce, and a page may bend a rule.

The rule IDs come from the rules files: the global rules in
docs/reference/writing-rules.md and a language's own in
standards/writing-<code>.md. Code that cites an ID neither file defines fails
here.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ol.authoring import rules
from ol.authoring.validate import Report
from ol.docs.bends import drop_bends
from ol.tests.test_standard import errors, fixture, report

PACKAGE = Path(__file__).resolve().parents[1]
CITATION = re.compile(r"""rule=["']([A-Z]{2,}-W\d+)["']""")
LANGUAGE_RULES = (
    "# Writing rules: German\n\n"
    "**DE-W1. Sie and du in tabs, labelled `Formal (Sie)` and `Informal (du)`.** "
    "Narrows OL-W8.\nWherever the same phrases come in both registers.\n\n"
    "**DE-W2. Run the lexicon check on every page.**\n"
)
TABS = (
    ":::::{{tab-set}}\n\n::::{{tab-item}} {first}\n:::{{ol-examples}}\n"
    ":presenters: emilia\nWie heißen Sie?\n: What's your name?\n:::\n::::\n\n"
    "::::{{tab-item}} {second}\n:::{{ol-examples}}\n:presenters: emilia\n"
    "Wie heißt du?\n: What's your name?\n:::\n::::\n\n:::::\n\n"
)


def cited_in_code() -> set[str]:
    found = set()
    for path in PACKAGE.rglob("*.py"):
        if "tests" not in path.parts:
            found |= set(CITATION.findall(path.read_text(encoding="utf-8")))
    return found


def test_every_rule_the_code_cites_is_defined():
    assert cited_in_code() - set(rules.global_rules()) == set()


def test_the_code_cites_no_language_rule_by_id():
    """A language rule is found by the global rule it narrows, never named in code."""
    assert {rule for rule in cited_in_code() if not rule.startswith("OL-")} == set()


def test_the_global_rules_run_from_one_with_no_gaps():
    numbers = [int(rule.split("W")[1]) for rule in rules.global_rules()]
    assert numbers == list(range(1, len(numbers) + 1))


def test_a_finding_citing_an_undefined_rule_raises(tmp_path):
    with pytest.raises(rules.UnknownRule):
        Report(tmp_path / "page.md").error("nothing", rule="OL-W999")


def test_a_finding_starts_with_its_rule(tmp_path):
    text = fixture("grammar").replace(
        "Always learn a noun", "Always — always — learn a noun", 1
    )
    assert any(
        e.startswith("OL-W26: em dash on line")
        for e in errors(tmp_path, "grammar", text)
    )


def test_a_bend_hides_the_rule_and_is_listed(tmp_path):
    text = fixture("grammar").replace(
        "Always learn a noun",
        "<!-- OL-W26 bent: the quoted title keeps its dash -->\n"
        "Always — always — learn a noun",
        1,
    )
    found = report(tmp_path, "grammar", text).items
    assert [m for lvl, m in found if lvl == "ERROR"] == []
    assert (
        "INFO",
        "line 19: OL-W26 bent: the quoted title keeps its dash",
    ) in found


def test_a_bend_hides_only_its_own_rule(tmp_path):
    text = fixture("grammar").replace(
        "Always learn a noun",
        "<!-- OL-W8 bent: a page about mixing registers -->\nAlways — learn a noun",
        1,
    )
    assert any(e.startswith("OL-W26:") for e in errors(tmp_path, "grammar", text))


def test_a_bend_of_an_undefined_rule_is_an_error(tmp_path):
    text = fixture("grammar").replace(
        "Always learn a noun",
        "<!-- OL-W99 bent: no such rule -->\nAlways learn a noun",
        1,
    )
    assert "line 19: bends OL-W99, which no writing rules file defines" in errors(
        tmp_path, "grammar", text
    )


def test_a_bend_with_no_reason_is_an_error(tmp_path):
    text = fixture("grammar").replace(
        "Always learn a noun", "<!-- OL-W26 bent: -->\nAlways learn a noun", 1
    )
    assert "line 19: the bend of OL-W26 gives no reason" in errors(
        tmp_path, "grammar", text
    )


def test_any_other_html_comment_still_fails(tmp_path):
    text = fixture("grammar").replace(
        "Always learn a noun", "<!-- a note -->\nAlways learn a noun", 1
    )
    assert any("HTML comment" in e for e in errors(tmp_path, "grammar", text))


def test_the_build_drops_bend_comments():
    source = ["Text.\n<!-- OL-W8 bent: why -->\nMore.\n"]
    drop_bends(None, "page", source)
    assert source == ["Text.\n\nMore.\n"]


def language(root: Path, labels: str = "[Formal (Sie), Informal (du)]") -> None:
    (root / "standards").mkdir(exist_ok=True)
    (root / "standards" / "writing-de.md").write_text(LANGUAGE_RULES, encoding="utf-8")
    rules._language_rules.cache_clear()


def how_to_with_tabs(first: str, second: str) -> str:
    return fixture("how-to").replace(
        ":::{ol-examples}\n:presenters: emilia\nGuten Tag",
        TABS.format(first=first, second=second)
        + ":::{ol-examples}\n:presenters: emilia\nGuten Tag",
        1,
    )


def register_errors(root: Path, text: str, labels: str | None) -> list[str]:
    found = report(root, "how-to", text)  # writes open-language.yml
    if labels is None:
        return [m for lvl, m in found.items if lvl == "ERROR"]
    (root / "open-language.yml").write_text(
        f"language: German\nlanguage_code: de\nregister_tabs: {labels}\n",
        encoding="utf-8",
    )
    from ol.authoring.validate import validate_file

    page = root / "a1/how-to/greetings.md"
    return [m for lvl, m in validate_file(page, root).items if lvl == "ERROR"]


LABELS = "[Formal (Sie), Informal (du)]"


def test_register_tabs_in_the_language_order_pass(tmp_path):
    language(tmp_path)
    text = how_to_with_tabs("Formal (Sie)", "Informal (du)")
    assert not [
        e for e in register_errors(tmp_path, text, LABELS) if "register tabs" in e
    ]


def test_register_tabs_out_of_order_cite_the_language_rule(tmp_path):
    language(tmp_path)
    text = how_to_with_tabs("Informal (du)", "Formal (Sie)")
    assert [
        e for e in register_errors(tmp_path, text, LABELS) if "register tabs" in e
    ] == [
        "DE-W1: line 40: the register tabs are labelled 'Informal (du)', "
        "'Formal (Sie)': label them 'Formal (Sie)', 'Informal (du)', in that order"
    ]


def test_register_tabs_with_other_labels_cite_the_global_rule_without_a_language_rule(
    tmp_path,
):
    rules._language_rules.cache_clear()
    text = how_to_with_tabs("Sie", "du")
    found = [e for e in register_errors(tmp_path, text, LABELS) if "register tabs" in e]
    assert len(found) == 1
    assert found[0].startswith("OL-W8: ")


def test_bending_the_global_rule_bends_the_language_rule_that_narrows_it(tmp_path):
    language(tmp_path)
    text = how_to_with_tabs("Informal (du)", "Formal (Sie)").replace(
        "# Greet someone\n",
        "# Greet someone\n<!-- OL-W8 bent: informal comes first here -->\n",
        1,
    )
    assert not [
        e for e in register_errors(tmp_path, text, LABELS) if "register tabs" in e
    ]


def test_tabs_that_are_not_registers_are_not_held_to_the_labels(tmp_path):
    language(tmp_path)
    text = how_to_with_tabs("Morning", "Evening")
    assert not [
        e for e in register_errors(tmp_path, text, LABELS) if "register tabs" in e
    ]


def test_a_keyword_only_in_a_table_cell_fails(tmp_path):
    text = fixture("how-to").replace(
        'keywords: "german, a1, how to, greetings, saying hello in german"',
        'keywords: "german, a1, how to, greetings, saying hello in german, until about noon"',
        1,
    )
    assert (
        "OL-W29: the keyword 'until about noon' appears only in a table cell: say it in "
        "a sentence of the page"
    ) in errors(tmp_path, "how-to", text)


def test_a_keyword_said_in_a_sentence_passes(tmp_path):
    text = (
        fixture("how-to")
        .replace(
            'keywords: "german, a1, how to, greetings, saying hello in german"',
            'keywords: "german, a1, how to, greetings, saying hello in german, until about noon"',
            1,
        )
        .replace(
            "Shops, offices and strangers",
            "Greetings change until about noon. Shops, offices and strangers",
            1,
        )
    )
    assert not [e for e in errors(tmp_path, "how-to", text) if e.startswith("OL-W29")]


def test_a_disclosure_line_fails(tmp_path):
    text = fixture("how-to").replace(
        "Strangers and customers get the formal greeting.",
        "Strangers and customers get the formal greeting. The recordings use AI voices.",
        1,
    )
    assert any(e.startswith("OL-W31: line") for e in errors(tmp_path, "how-to", text))


def test_the_rules_ship_with_the_package():
    """The wheel carries the rules file beside this module; a checkout reads docs/."""
    assert rules.global_rules_file().name == rules.RULES_FILE
    assert "OL-W26" in rules.global_rules()
