"""The content review a pull request into a language repository needs.

Every pull request gets a tier, worked out from its diff and its author's
numeric GitHub user id (never a login name, which can be changed or reused):

- **trivial**: no review. The author is a trusted author (the repository
  owner or the Open Language bot), every changed line is a prose edit inside
  pages that already exist, and the pull request changes at most
  ``trivial_max_lines`` lines.
- **small**: a review by a fast, low-cost model. The pull request adds no
  page, changes no track and changes at most ``small_max_lines`` lines.
- **full**: a review by a strong model other than the one that wrote the
  change. Everything else: a new, removed or renamed page that holds a track,
  a renamed or new page, a changed track, or a larger change.

A prose edit is a changed line outside the front matter, outside every
``audio-examples`` block and ``ol-examples`` box, outside code fences and
directive lines, and not a heading. Across a page the link targets of the
removed lines and the added lines are the same, so no link moves.

The limits and the trusted authors are in ``specs.yml``, under
``content_review``.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from ol.authoring.specs_data import SPECS

POLICY = SPECS["content_review"]
TRUSTED_AUTHORS: dict[int, str] = {
    int(user_id): name for user_id, name in POLICY["trusted_authors"].items()
}
TRIVIAL_MAX_LINES: int = POLICY["trivial_max_lines"]
SMALL_MAX_LINES: int = POLICY["small_max_lines"]

TRIVIAL, SMALL, FULL = "trivial", "small", "full"
TIERS = (TRIVIAL, SMALL, FULL)
CONTEXT = "content-review"

NOT_PAGES = ("README.md", "AGENTS.md", "LICENSE", "CHANGELOG.md")
NOT_PAGE_DIRS = (".github/", "standards/", "_build/", "media/")

_HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
_FENCE_OPEN = re.compile(r"^(:{3,}|`{3,})\{([a-z-]+)\}")
_FENCE = re.compile(r"^(:{3,}|`{3,})")
_LINK_TARGET = re.compile(r"\]\(([^)\s]*)")
_NOT_PLAIN = re.compile(r"<|^\s{0,3}\[[^\]]+\]:\s*\S")
_PIN_LINE = re.compile(r"open-language", re.IGNORECASE)


@dataclass
class ChangedFile:
    """One file of a pull request, as the GitHub API lists it.

    Attributes:
        path: The file's path in the head commit.
        status: ``added``, ``removed``, ``modified``, ``renamed`` and so on.
        additions: Lines added.
        deletions: Lines removed.
        patch: The unified diff, or None when GitHub gives none (a large or
            binary file).
        base_text: The file in the base commit, when it was fetched.
        head_text: The file in the head commit, when it was fetched.
    """

    path: str
    status: str
    additions: int = 0
    deletions: int = 0
    patch: str | None = None
    base_text: str | None = None
    head_text: str | None = None


@dataclass
class Decision:
    """The tier a pull request needs, and why."""

    tier: str
    reasons: list[str] = field(default_factory=list)

    @property
    def description(self) -> str:
        """The commit status description: the tier and what it needs."""
        return {
            TRIVIAL: "Trivial: a small prose edit by a trusted author, no review needed",
            SMALL: "Small: needs a review by a fast model before merge",
            FULL: "Full: needs a review by a strong model other than the writer's",
        }[self.tier]


def is_page(path: str) -> bool:
    """Whether a file of a language repository is a coursebook page."""
    return (
        path.endswith(".md")
        and path not in NOT_PAGES
        and not path.startswith(NOT_PAGE_DIRS)
    )


def line_kinds(text: str) -> list[str]:
    """The kind of each line of a page: what an edit to it would change.

    Args:
        text: The page's Markdown.

    Returns:
        One of ``front``, ``heading``, ``track``, ``examples``, ``markup`` or
        ``prose`` per line, in order.
    """
    lines = text.splitlines()
    kinds = ["prose"] * len(lines)
    start = 0
    if lines and lines[0].strip() == "---":
        start = next(
            (n + 1 for n in range(1, len(lines)) if lines[n].strip() == "---"),
            len(lines),
        )
        kinds[:start] = ["front"] * start
    # Each open fence: its character, its length and the kind of every line in
    # it, or None for a directive that holds ordinary text (a notice, a tab).
    stack: list[tuple[str, int, str | None]] = []
    for n in range(start, len(lines)):
        line = lines[n].strip()
        held = next((kind for _, _, kind in reversed(stack) if kind), None)
        fence = _FENCE.fullmatch(line)
        if stack and fence and _closes(fence.group(1), stack[-1]):
            kind = stack.pop()[2]
            kinds[n] = kind or held or "markup"
        elif held == "code":
            kinds[n] = "code"
        elif m := _FENCE_OPEN.match(line):
            marks, name = m.groups()
            kind = held or {"audio-examples": "track", "ol-examples": "examples"}.get(
                name, "code" if marks[0] == "`" else None
            )
            stack.append((marks[0], len(marks), kind))
            kinds[n] = kind or "markup"
        elif (m := _FENCE.match(line)) and line.startswith("`"):
            stack.append((m.group(1)[0], len(m.group(1)), held or "code"))
            kinds[n] = held or "code"
        elif held:
            kinds[n] = held
        elif line.startswith(":"):
            kinds[n] = "markup"
        elif line.startswith("#"):
            kinds[n] = "heading"
    return ["markup" if kind == "code" else kind for kind in kinds]


def _closes(marks: str, fence: tuple[str, int, str | None]) -> bool:
    return marks[0] == fence[0] and len(marks) >= fence[1]


def changed_lines(patch: str) -> list[tuple[str, int, str]]:
    """Every changed line of a unified diff.

    Args:
        patch: The diff of one file.

    Returns:
        ``("-", line in the base, text)`` for a removed line and
        ``("+", line in the head, text)`` for an added one.
    """
    found = []
    old = new = 0
    for line in patch.splitlines():
        if m := _HUNK.match(line):
            old, new = int(m.group(1)), int(m.group(2))
        elif line.startswith("-"):
            found.append(("-", old, line[1:]))
            old += 1
        elif line.startswith("+"):
            found.append(("+", new, line[1:]))
            new += 1
        elif not line.startswith("\\"):
            old += 1
            new += 1
    return found


def _kind_at(kinds: list[str], line: int) -> str:
    return kinds[line - 1] if 0 < line <= len(kinds) else "unknown"


def touches_track(changed: ChangedFile) -> bool:
    """Whether a page's change touches a track: an audio-examples block."""
    if changed.status != "modified":
        texts = [changed.base_text, changed.head_text]
        return any("{audio-examples}" in (text or "") for text in texts)
    if changed.patch is None:
        return True
    base = line_kinds(changed.base_text or "")
    head = line_kinds(changed.head_text or "")
    return any(
        _kind_at(base if sign == "-" else head, line) == "track"
        or "{audio-examples}" in text
        for sign, line, text in changed_lines(changed.patch)
    )


def prose_only(changed: ChangedFile) -> str | None:
    """Why a page's change is more than a prose edit, or None when it is not."""
    if changed.status != "modified":
        return f"{changed.path} is {changed.status}"
    if changed.patch is None:
        return f"{changed.path} has no diff to read"
    base = line_kinds(changed.base_text or "")
    head = line_kinds(changed.head_text or "")
    targets: dict[str, Counter] = {"-": Counter(), "+": Counter()}
    for sign, line, text in changed_lines(changed.patch):
        kind = _kind_at(base if sign == "-" else head, line)
        if kind != "prose":
            return f"{changed.path} line {line} is not prose ({kind})"
        if _NOT_PLAIN.search(text):
            return f"{changed.path} line {line} holds markup or a reference definition"
        targets[sign].update(_LINK_TARGET.findall(text))
    if targets["-"] != targets["+"]:
        return f"{changed.path} changes a link target"
    return None


def is_pin_bump(files: list[ChangedFile]) -> bool:
    """Whether the change is only the ``open-language`` pin and the lock file."""
    paths = {f.path for f in files}
    if paths != {"pyproject.toml", "uv.lock"}:
        return False
    for changed in files:
        if changed.path == "pyproject.toml":
            if changed.patch is None:
                return False
            lines = changed_lines(changed.patch)
            if not lines or not all(_PIN_LINE.search(text) for _, _, text in lines):
                return False
    return True


def decide(author_id: int, files: list[ChangedFile]) -> Decision:
    """The tier a pull request needs.

    Args:
        author_id: The pull request author's numeric GitHub user id.
        files: Every changed file, with its texts for each modified page.

    Returns:
        The tier, with the reasons it is not a lower one.
    """
    total = sum(f.additions + f.deletions for f in files)
    if author_id in TRUSTED_AUTHORS and is_pin_bump(files):
        return Decision(TRIVIAL, [f"pin bump by {TRUSTED_AUTHORS[author_id]}"])
    full: list[str] = []
    for changed in files:
        if not is_page(changed.path):
            continue
        if changed.status in ("added", "renamed", "copied"):
            full.append(f"{changed.path} is a new page ({changed.status})")
        elif changed.status == "modified" and (
            changed.base_text is None or changed.head_text is None
        ):
            full.append(f"{changed.path} could not be read to check the change")
        elif touches_track(changed):
            full.append(f"{changed.path} changes a track")
    if total > SMALL_MAX_LINES:
        full.append(f"{total} changed lines (a small review covers {SMALL_MAX_LINES})")
    if full:
        return Decision(FULL, full)

    small: list[str] = []
    if author_id not in TRUSTED_AUTHORS:
        small.append("the author is not a trusted author")
    if total > TRIVIAL_MAX_LINES:
        small.append(f"{total} changed lines (trivial is {TRIVIAL_MAX_LINES} or fewer)")
    for changed in files:
        if not is_page(changed.path):
            small.append(f"{changed.path} is not a coursebook page")
        elif why := prose_only(changed):
            small.append(why)
    if small:
        return Decision(SMALL, small)
    return Decision(TRIVIAL, [f"prose edit by {TRUSTED_AUTHORS[author_id]}"])


def needs_texts(changed: ChangedFile) -> bool:
    """Whether deciding the tier reads the file's base and head texts."""
    return is_page(changed.path)


def covers(given: str, required: str) -> bool:
    """Whether a review of tier ``given`` satisfies a pull request needing ``required``."""
    return TIERS.index(given) >= TIERS.index(required)
