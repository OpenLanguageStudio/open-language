"""The build draws the Situations and How to boxes from situations' front matter."""

from __future__ import annotations

import re
from io import StringIO
from pathlib import Path

import pytest
from sphinx.application import Sphinx


def how_to(title: str) -> str:
    return f"# {title}\n\nThe explanation.\n\n:::{{situations}}\n:::\n"


def situation(title: str, *names: str) -> str:
    links = "".join(f"  - /{name}.md\n" for name in names)
    return (
        f"---\nhow-to:\n{links}---\n# {title}\n\nThe scene.\n\n"
        ":::{how-to-links}\n:::\n"
    )


def index(title: str, *pages: str) -> str:
    listed = "\n".join(pages)
    return f"# {title}\n\n```{{toctree}}\n{listed}\n```\n"


class Build:
    def __init__(self, root: Path, extension: str = "ol.docs.situations"):
        self.root = root
        self.src = root / "src"
        self.src.mkdir()
        (self.src / "conf.py").write_text(
            f'extensions = ["myst_parser", "{extension}"]\n'
            'myst_enable_extensions = ["colon_fence"]\n'
            "suppress_warnings = ['toc.not_included']\n"
        )
        self.out = root / "out"
        self.fresh = True

    def run(self, pages: dict[str, str], builder: str = "html") -> Build:
        for name, text in pages.items():
            page = self.src / f"{name}.md"
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(text, encoding="utf-8")
        self.warnings = StringIO()
        Sphinx(
            str(self.src),
            str(self.src),
            str(self.out / builder),
            str(self.root / "doctrees"),
            builder,
            status=None,
            warning=self.warnings,
            freshenv=self.fresh,
        ).build()
        self.fresh = False
        return self

    def remove(self, name: str) -> None:
        (self.src / f"{name}.md").unlink()

    def html(self, name: str) -> str:
        return (self.out / "html" / f"{name}.html").read_text(encoding="utf-8")

    def box(self, name: str) -> str:
        html = self.html(name)
        found = re.search(r'<div class="ol-links.*?</ul>\s*</div>', html, re.S)
        return found.group(0) if found else ""

    def links(self, name: str) -> list[str]:
        """The box's links as text, each followed by its badge's level."""
        items = re.findall(r"<li>(.*?)</li>", self.box(name), re.S)
        return [re.sub(r"<[^>]+>", "", item).split() for item in items]


COURSE = {
    "index": index("Course", "a1/index", "b1/index"),
    "a1/index": index("A1", "how-to/index", "situations/index"),
    "a1/how-to/index": index("How to", "introduce-yourself", "say-hello"),
    "a1/how-to/introduce-yourself": how_to("Introduce yourself"),
    "a1/how-to/say-hello": how_to("Say hello and goodbye"),
    "a1/situations/index": index("Situations", "on-the-phone", "at-a-party"),
    "a1/situations/at-a-party": situation(
        "At a party", "a1/how-to/introduce-yourself", "a1/how-to/say-hello"
    ),
    "a1/situations/on-the-phone": situation(
        "On the phone", "a1/how-to/introduce-yourself"
    ),
    "b1/index": index("B1", "situations/index"),
    "b1/situations/index": index("Situations", "a-new-colleague"),
    "b1/situations/a-new-colleague": situation(
        "A new colleague", "a1/how-to/introduce-yourself"
    ),
}


@pytest.fixture
def course(tmp_path):
    return Build(tmp_path).run(COURSE)


class TestSituationsBox:
    def test_it_links_every_situation_naming_the_page_in_course_order(self, course):
        assert course.links("a1/how-to/introduce-yourself") == [
            ["On", "the", "phone"],
            ["At", "a", "party"],
            ["A", "new", "colleague", "B1"],
        ]

    def test_it_is_titled_situations_and_drawn_as_its_own_box(self, course):
        box = course.box("a1/how-to/say-hello")
        assert 'class="ol-links ol-links--situations' in box
        assert "<strong>Situations</strong>" in box

    def test_each_link_points_at_the_situation(self, course):
        box = course.box("a1/how-to/say-hello")
        assert 'href="../situations/at-a-party.html"' in box

    def test_a_situation_of_the_same_level_has_no_badge(self, course):
        assert "ol-level" not in course.box("a1/how-to/say-hello")

    def test_a_situation_of_another_level_carries_its_badge(self, course):
        assert 'class="ol-level ol-level--b1"' in course.box(
            "a1/how-to/introduce-yourself"
        )

    def test_a_box_no_situation_fills_warns_and_draws_nothing(self, tmp_path):
        done = Build(tmp_path).run(
            {"index": index("Course", "a1/how-to/x"), "a1/how-to/x": how_to("X")}
        )
        assert "no situation names this page" in done.warnings.getvalue()
        assert "ol-links" not in done.html("a1/how-to/x")

    def test_adding_a_situation_redraws_the_pages_it_names(self, course):
        course.run(
            {
                "a1/situations/index": index(
                    "Situations", "on-the-phone", "at-a-party", "in-a-cafe"
                ),
                "a1/situations/in-a-cafe": situation(
                    "In a cafe", "a1/how-to/say-hello"
                ),
            }
        )
        assert course.links("a1/how-to/say-hello") == [
            ["At", "a", "party"],
            ["In", "a", "cafe"],
        ]

    def test_removing_a_situation_redraws_the_pages_it_named(self, course):
        course.remove("b1/situations/a-new-colleague")
        course.run({"b1/situations/index": index("Situations")})
        assert ["A", "new", "colleague", "B1"] not in course.links(
            "a1/how-to/introduce-yourself"
        )

    def test_changing_a_situations_list_redraws_both_pages(self, course):
        course.run(
            {
                "a1/situations/on-the-phone": situation(
                    "On the phone", "a1/how-to/say-hello"
                )
            }
        )
        assert ["On", "the", "phone"] not in course.links(
            "a1/how-to/introduce-yourself"
        )
        assert course.links("a1/how-to/say-hello")[0] == ["On", "the", "phone"]

    def test_reordering_a_level_index_reorders_the_box(self, course):
        course.run(
            {"a1/situations/index": index("Situations", "at-a-party", "on-the-phone")}
        )
        assert course.links("a1/how-to/introduce-yourself")[:2] == [
            ["At", "a", "party"],
            ["On", "the", "phone"],
        ]


class TestHowToBox:
    def test_it_links_the_pages_the_front_matter_names_in_order(self, course):
        assert course.links("a1/situations/at-a-party") == [
            ["Introduce", "yourself"],
            ["Say", "hello", "and", "goodbye"],
        ]

    def test_it_is_titled_how_to(self, course):
        box = course.box("a1/situations/at-a-party")
        assert "ol-links--how-to-links" in box
        assert "<strong>How to</strong>" in box

    def test_a_page_of_a_lower_level_carries_its_badge(self, course):
        assert course.links("b1/situations/a-new-colleague") == [
            ["Introduce", "yourself", "A1"]
        ]

    def test_a_situation_with_no_how_to_list_warns(self, tmp_path):
        page = "# At a party\n\nThe scene.\n\n:::{how-to-links}\n:::\n"
        done = Build(tmp_path).run(
            {"index": index("Course", "a1/situations/p"), "a1/situations/p": page}
        )
        assert "names no how-to article" in done.warnings.getvalue()

    def test_a_box_on_a_page_that_is_no_situation_warns(self, tmp_path):
        page = situation("Elsewhere", "a1/how-to/x")
        done = Build(tmp_path).run(
            {
                "index": index("Course", "a1/how-to/x", "a1/grammar/p"),
                "a1/how-to/x": "# X\n",
                "a1/grammar/p": page,
            }
        )
        assert "the box goes on a situation article" in done.warnings.getvalue()
        assert "ol-links" not in done.html("a1/grammar/p")

    def test_a_name_that_is_no_page_warns(self, tmp_path):
        done = Build(tmp_path).run(
            {
                "index": index("Course", "a1/situations/p"),
                "a1/situations/p": situation("P", "a1/how-to/gone"),
            }
        )
        assert "a1/how-to/gone" in done.warnings.getvalue()


def test_a_build_that_draws_no_html_writes_the_level_in_brackets(tmp_path):
    Build(tmp_path).run(COURSE, builder="text")
    text = (tmp_path / "out" / "text" / "a1/how-to/introduce-yourself.txt").read_text()
    assert "A new colleague (B1)" in text


def test_a_build_into_one_document_draws_every_box_from_its_own_page(tmp_path):
    Build(tmp_path).run(COURSE, builder="singlehtml")
    html = (tmp_path / "out" / "singlehtml" / "index.html").read_text()
    assert html.count('class="ol-links ') == 5
    assert "A new colleague</span></a> <span" in html


def test_the_audio_examples_extension_brings_the_boxes(tmp_path):
    done = Build(tmp_path, extension="ol.docs.audio_examples").run(COURSE)
    assert done.links("a1/situations/at-a-party")
