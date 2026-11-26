"""The content review a pull request needs, and the verdict a reviewer posts."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from ol import github
from ol.cli import app, tier_comment
from ol.review import (
    FULL,
    SMALL,
    SMALL_MAX_LINES,
    TRIVIAL,
    TRUSTED_AUTHORS,
    ChangedFile,
    changed_lines,
    covers,
    decide,
    line_kinds,
)

OWNER = 47405990
BOT = 335511516
STRANGER = 1
PAGE = """---
myst:
  html_meta:
    keywords: "greetings"
---
# Greet someone

Saying hello depends on the time of day. See [the dative](/a1/grammar/dativ.md).

## Key phrases

:::{ol-examples}
:presenters: emilia
Hallo, Anna.
: Hello, Anna.
:::

::::{tab-set}
:::{tab-item} Formal (Sie)
Use it with strangers.
:::
::::

```{toctree}
:hidden:
a
```

:::{audio-examples}
:track: a1/how-to/greet
:title: Begrüßen

Guten Tag.
: Good day.
:::
"""


def kinds() -> dict[int, str]:
    return dict(enumerate(line_kinds(PAGE), 1))


def test_each_line_of_a_page_has_its_kind():
    found = kinds()
    assert found[2] == "front"
    assert found[5] == "front"
    assert found[6] == "heading"
    assert found[8] == "prose"
    assert found[12] == found[15] == "examples"
    assert found[20] == "prose"  # inside a tab: ordinary text
    assert found[19] == "markup"
    assert found[24] == found[26] == "markup"  # a toctree fence
    assert found[29] == found[33] == found[35] == "track"


def diff(old: int, new: int, *lines: str) -> str:
    return f"@@ -{old},3 +{new},3 @@\n" + "\n".join(lines)


def test_changed_lines_carry_their_line_numbers():
    patch = diff(7, 7, " ", "-Saying hello", "+Saying hi", " ")
    assert changed_lines(patch) == [("-", 8, "Saying hello"), ("+", 8, "Saying hi")]


def page(patch: str, status: str = "modified", head: str = PAGE) -> ChangedFile:
    return ChangedFile(
        path="a1/how-to/greet.md",
        status=status,
        additions=patch.count("\n+"),
        deletions=patch.count("\n-"),
        patch=patch,
        base_text=PAGE,
        head_text=head,
    )


TYPO = diff(
    7,
    7,
    " ",
    "-Saying hello depends on the time of day. See [the dative](/a1/grammar/dativ.md).",
    "+Saying hello depends on the time of the day. See [the dative](/a1/grammar/dativ.md).",
    " ",
)


@pytest.mark.parametrize("author", [OWNER, BOT])
def test_a_typo_fix_by_a_trusted_author_is_trivial(author):
    assert decide(author, [page(TYPO)]).tier == TRIVIAL


def test_the_trusted_authors_are_named_by_user_id():
    assert set(TRUSTED_AUTHORS) == {OWNER, BOT}


def test_an_outside_contributor_is_never_trivial():
    decision = decide(STRANGER, [page(TYPO)])
    assert decision.tier == SMALL
    assert "the author is not a trusted author" in decision.reasons


@pytest.mark.parametrize(
    ("patch", "reason"),
    [
        (diff(3, 3, '-    keywords: "greetings"', '+    keywords: "hello"'), "(front)"),
        (diff(6, 6, "-# Greet someone", "+# Say hello"), "(heading)"),
        (diff(13, 13, "-Hallo, Anna.", "+Hallo, Ana."), "(examples)"),
        (
            diff(
                8,
                8,
                "-Saying hello. See [the dative](/a1/grammar/dativ.md).",
                "+Saying hello. See [the dative](/a1/grammar/akkusativ.md).",
            ),
            "changes a link target",
        ),
    ],
)
def test_more_than_a_prose_edit_is_small(patch, reason):
    decision = decide(OWNER, [page(patch)])
    assert decision.tier == SMALL
    assert any(reason in why for why in decision.reasons)


def test_a_file_that_is_not_a_page_is_small():
    lock = ChangedFile("uv.lock", "modified", 1, 1, "@@ -1 +1 @@\n-a\n+b")
    assert decide(OWNER, [lock]).tier == SMALL


def test_more_than_the_trivial_limit_is_small():
    lines = [f"-Line {n}." for n in range(6)] + [f"+Line {n}!" for n in range(6)]
    patch = diff(7, 7, *lines)
    changed = page(patch)
    changed.base_text = changed.head_text = "\n" * 6 + "prose\n" * 20
    assert decide(OWNER, [changed]).tier == SMALL


def test_a_changed_track_is_full():
    decision = decide(OWNER, [page(diff(33, 33, "-Guten Tag.", "+Guten Morgen."))])
    assert decision.tier == FULL
    assert decision.reasons == ["a1/how-to/greet.md changes a track"]


def test_a_new_page_is_full():
    new = ChangedFile("a1/how-to/new.md", "added", 3, 0, "@@ -0,0 +1,3 @@\n+# New")
    assert decide(OWNER, [new]).tier == FULL


def test_more_than_the_small_limit_is_full():
    big = ChangedFile("README.md", "modified", SMALL_MAX_LINES, 1, "@@ -1 +1 @@\n-a")
    assert decide(STRANGER, [big]).tier == FULL


def test_a_higher_review_covers_a_lower_tier():
    assert covers(FULL, SMALL)
    assert covers(SMALL, TRIVIAL)
    assert not covers(SMALL, FULL)


def test_the_tier_comment_says_what_is_needed_in_words():
    text = tier_comment(decide(STRANGER, [page(TYPO)]))
    assert text.startswith("**Content review: small.** A review by a fast model")
    assert "- the author is not a trusted author" in text


class FakeGitHub:
    def __init__(self, monkeypatch, author=STRANGER, files=None):
        self.statuses: list[tuple] = []
        self.comments: list[str] = []
        pr = {"number": 7, "user": {"id": author}, "head": {"sha": "abc123def456"}}
        monkeypatch.setattr(github, "pull", lambda repo, number: pr)
        monkeypatch.setattr(
            github, "changed_files", lambda repo, pull: files or [page(TYPO)]
        )
        monkeypatch.setattr(
            github, "post_status", lambda *args: self.statuses.append(args)
        )
        monkeypatch.setattr(
            github, "comment", lambda repo, n, body: self.comments.append(body)
        )
        monkeypatch.setattr(
            github,
            "upsert_tier_comment",
            lambda repo, n, body: self.comments.append(body),
        )


def run(*args: str):
    return CliRunner().invoke(app, [*args, "--repo", "o/r"])


@pytest.fixture
def review_report(tmp_path):
    path = tmp_path / "report.md"
    path.write_text("Every claim checked.\n", encoding="utf-8")
    return path


def test_a_trivial_pull_request_gets_success_at_once(monkeypatch):
    fake = FakeGitHub(monkeypatch, author=OWNER)
    result = run("review-tier", "--pr", "7", "--post")
    assert result.exit_code == 0
    assert fake.statuses[0][1:3] == ("abc123def456", "success")


def test_a_small_pull_request_is_left_pending(monkeypatch):
    fake = FakeGitHub(monkeypatch)
    run("review-tier", "--pr", "7", "--post")
    assert fake.statuses[0][2] == "pending"
    assert fake.statuses[0][3].startswith("Small:")


def test_a_passing_review_posts_success_and_the_report(monkeypatch, review_report):
    fake = FakeGitHub(monkeypatch)
    result = run(
        "review-status", "--pr", "7", "--verdict", "pass", "--tier", "small",
        "--report", str(review_report), "--model", "claude-sonnet-5-5",
    )  # fmt: skip
    assert result.exit_code == 0, result.output
    assert fake.statuses == [
        ("o/r", "abc123def456", "success", "Small review passed (claude-sonnet-5-5)")
    ]
    assert fake.comments[0].startswith("**Content review (small): pass.**")
    assert "Every claim checked." in fake.comments[0]


def test_a_failing_review_posts_failure(monkeypatch, review_report):
    fake = FakeGitHub(monkeypatch)
    run(
        "review-status", "--pr", "7", "--verdict", "fail", "--tier", "small",
        "--report", str(review_report), "--model", "m",
    )  # fmt: skip
    assert fake.statuses[0][2] == "failure"


def test_a_review_below_the_tier_needed_is_refused(monkeypatch, review_report):
    track = page(diff(33, 33, "-Guten Tag.", "+Guten Morgen."))
    fake = FakeGitHub(monkeypatch, files=[track])
    result = run(
        "review-status", "--pr", "7", "--verdict", "pass", "--tier", "small",
        "--report", str(review_report), "--model", "m",
    )  # fmt: skip
    assert result.exit_code == 1
    assert "needs a full review, not small" in result.output
    assert fake.statuses == []


def test_a_review_of_an_older_commit_is_refused(monkeypatch, review_report):
    fake = FakeGitHub(monkeypatch)
    result = run(
        "review-status", "--pr", "7", "--verdict", "pass", "--tier", "small",
        "--report", str(review_report), "--model", "m", "--sha", "0000000",
    )  # fmt: skip
    assert result.exit_code == 1
    assert fake.statuses == []


def test_a_full_review_by_the_writers_model_is_refused(monkeypatch, review_report):
    fake = FakeGitHub(monkeypatch)
    result = run(
        "review-status", "--pr", "7", "--verdict", "pass", "--tier", "full",
        "--report", str(review_report), "--model", "m", "--writer-model", "m",
    )  # fmt: skip
    assert result.exit_code == 1
    assert fake.statuses == []


def test_an_empty_report_is_refused(monkeypatch, tmp_path):
    fake = FakeGitHub(monkeypatch)
    empty = tmp_path / "empty.md"
    empty.write_text("", encoding="utf-8")
    result = run(
        "review-status", "--pr", "7", "--verdict", "pass", "--tier", "small",
        "--report", str(empty), "--model", "m",
    )  # fmt: skip
    assert result.exit_code != 0
    assert fake.statuses == []


def test_a_page_that_cannot_be_read_is_full():
    changed = page(TYPO)
    changed.head_text = None
    decision = decide(OWNER, [changed])
    assert decision.tier == FULL
    from ol.review import _kind_at

    assert _kind_at(line_kinds("one"), 9) == "unknown"


@pytest.mark.parametrize(
    "added",
    ["Saying hello <!-- bend: x --> today.", "[dativ]: /a1/grammar/dativ.md"],
)
def test_a_changed_line_with_markup_or_a_reference_definition_is_not_trivial(added):
    patch = diff(7, 7, " ", "-Saying hello depends.", f"+{added}", " ")
    assert decide(OWNER, [page(patch)]).tier == SMALL


@pytest.mark.parametrize("author", [OWNER, BOT])
def test_a_pin_bump_with_its_lock_file_is_trivial(author):
    pin = '@@ -8,1 +8,1 @@\n-    "open-language @ git+https://x/open-language@v0.18.0",\n+    "open-language @ git+https://x/open-language@v0.19.0",'
    files = [
        ChangedFile("pyproject.toml", "modified", 1, 1, pin),
        ChangedFile("uv.lock", "modified", 2, 2, "@@ -1 +1 @@\n-a\n+b"),
    ]
    assert decide(author, files).tier == TRIVIAL
    assert decide(STRANGER, files).tier == SMALL
