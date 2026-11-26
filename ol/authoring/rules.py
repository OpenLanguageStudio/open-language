"""The writing rules, read from their files, and the bends a page declares.

The global rules are ``docs/reference/writing-rules.md`` in this repository,
shipped inside the package so every language repository checks against the
rules of the release it pins. A language's own rules are
``standards/writing-<language code>.md`` in its repository. Each rule opens
with its ID in bold, as in ``**OL-W26.**`` or ``**DE-W1. Sie and du in tabs.**``.

A check that enforces a rule names it, and the ID must be one the rules file
defines: :func:`require` raises otherwise, so a check never cites a rule that
does not exist.

A page bends a rule with a comment beside the bend::

    <!-- OL-W8 bent: this page compares the two registers line by line -->

The bend suppresses that rule's findings on the page and is listed in the
output, so every bend stays visible. The build removes the comment.
"""

from __future__ import annotations

import re
from functools import cache
from pathlib import Path

import yaml

RULES_FILE = "writing-rules.md"
PACKAGED = Path(__file__).resolve().parent / RULES_FILE
SOURCE = Path(__file__).resolve().parents[2] / "docs" / "reference" / RULES_FILE

RULE_ID = r"[A-Z]{2,}-W\d+"
# A rule opens a paragraph with its ID in bold: **OL-W26.** or **DE-W1. Title.**
DEFINITION = re.compile(rf"^\*\*({RULE_ID})\.(.*?)\*\*(.*)$", re.M)
NARROWS = re.compile(rf"\bNarrows ({RULE_ID})\b")
BEND = re.compile(rf"<!--\s*({RULE_ID}) bent:\s*(.*?)\s*-->", re.S)
# A finding that enforces a rule starts with its ID.
CITED = re.compile(rf"^({RULE_ID}): ")


class UnknownRule(KeyError):
    """A check cites a rule ID that no rules file defines."""


def global_rules_file() -> Path:
    """The global rules shipped with the package, or the repository's copy."""
    return PACKAGED if PACKAGED.is_file() else SOURCE


def parse(text: str) -> dict[str, str]:
    """Every rule a rules file defines, by ID, with the paragraph that opens it.

    Args:
        text: The rules file's Markdown.

    Returns:
        The rule's opening paragraph by ID, in the order the file gives them.
    """
    rules: dict[str, str] = {}
    for match in DEFINITION.finditer(text):
        start = match.start()
        end = text.find("\n\n", start)
        rules[match.group(1)] = text[start : end if end != -1 else len(text)]
    return rules


@cache
def global_rules() -> dict[str, str]:
    """The global rules, OL-W1 onwards."""
    return parse(global_rules_file().read_text(encoding="utf-8"))


def language_rules_file(workspace: Path | None) -> Path | None:
    """The language repository's own rules file, when it has one."""
    if workspace is None:
        return None
    config = workspace / "open-language.yml"
    code = None
    if config.is_file():
        code = (yaml.safe_load(config.read_text(encoding="utf-8")) or {}).get(
            "language_code"
        )
    path = workspace / "standards" / f"writing-{code}.md"
    return path if code and path.is_file() else None


@cache
def _language_rules(path: Path | None) -> dict[str, str]:
    return parse(path.read_text(encoding="utf-8")) if path else {}


def language_rules(workspace: Path | None) -> dict[str, str]:
    """The rules of the language taught in ``workspace``, by ID."""
    return _language_rules(language_rules_file(workspace))


def known(workspace: Path | None = None) -> dict[str, str]:
    """Every rule a page in ``workspace`` is held to: the global ones and its own."""
    return {**global_rules(), **language_rules(workspace)}


def require(rule: str, workspace: Path | None = None) -> str:
    """Return ``rule`` when a rules file defines it, else raise UnknownRule."""
    if rule not in known(workspace):
        raise UnknownRule(f"{rule} is not defined in any writing rules file")
    return rule


def narrowing(rule: str, workspace: Path | None) -> str | None:
    """The language rule that narrows a global rule, if the language has one."""
    for rule_id, text in language_rules(workspace).items():
        if rule in NARROWS.findall(text):
            return rule_id
    return None


def cite(rule: str | None, message: str, workspace: Path | None = None) -> str:
    """``message`` with the rule it enforces in front, as in ``OL-W26: ...``.

    Raises:
        UnknownRule: When no rules file defines ``rule``.
    """
    if rule is None:
        return message
    return f"{require(rule, workspace)}: {message}"


def covers(bent: str, rule: str, workspace: Path | None) -> bool:
    """Whether bending ``bent`` bends ``rule``: itself, or a language rule narrowing it."""
    return rule == bent or bent in NARROWS.findall(
        language_rules(workspace).get(rule, "")
    )


def cited(message: str) -> str | None:
    """The rule a finding cites, or None."""
    match = CITED.match(message)
    return match.group(1) if match else None


def bends(text: str) -> list[tuple[int, str, str]]:
    """Every bend a page declares, as (line, rule, reason)."""
    return [
        (text.count("\n", 0, match.start()) + 1, match.group(1), match.group(2))
        for match in BEND.finditer(text)
    ]


def strip_bends(text: str) -> str:
    """The page without its bend comments, keeping every line where it was."""
    return BEND.sub(lambda match: "\n" * match.group(0).count("\n"), text)
