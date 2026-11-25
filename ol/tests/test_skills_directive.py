"""The build draws a level page's skills from its front matter."""

from __future__ import annotations

import re

from test_link_boxes import Build, index

PAGE = (
    "---\nskills:\n"
    "  - id: a\n    kind: can\n    text: Greet people.\n"
    "  - id: b\n    kind: know\n    text: The articles.\n"
    "  - id: c\n    kind: can\n    text: Order food.\n"
    "---\n# A1\n\n## What learners know\n\n:::{skills} know\n:::\n\n"
    "## What learners can do\n\n:::{skills} can\n:::\n"
)


def build(tmp_path, page=PAGE):
    return Build(tmp_path, extension="ol.docs.skills").run(
        {"index": index("Course", "a1/index"), "a1/index": page}
    )


def items(done, heading: str) -> list[str]:
    html = done.html("a1/index")
    part = html.split(f"<h2>{heading}")[1].split("</section>")[0]
    return re.findall(r"<li>.*?<p>(.*?)</p>.*?</li>", part, re.S)


class TestSkillsDirective:
    def test_it_draws_the_texts_of_its_kind_in_front_matter_order(self, tmp_path):
        done = build(tmp_path)
        assert items(done, "What learners can do") == ["Greet people.", "Order food."]
        assert items(done, "What learners know") == ["The articles."]

    def test_an_argument_that_is_not_a_kind_warns(self, tmp_path):
        done = build(tmp_path, PAGE.replace("{skills} know", "{skills} maybe"))
        assert "is not a kind of skill" in done.warnings.getvalue()

    def test_a_skill_list_that_is_not_valid_warns(self, tmp_path):
        done = build(tmp_path, PAGE.replace("kind: can", "kind: maybe", 1))
        assert "use know or can" in done.warnings.getvalue()

    def test_a_page_with_no_skills_warns(self, tmp_path):
        done = build(tmp_path, "# A1\n\n:::{skills} know\n:::\n")
        assert "no 'skills:'" in done.warnings.getvalue()
