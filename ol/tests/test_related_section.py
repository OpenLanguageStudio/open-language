"""The build draws Related articles from the front matter, grouped by kind."""

from __future__ import annotations

import re

import pytest
from sphinx.errors import SphinxError
from test_link_boxes import COURSE, Build, index, situation

PAGES = {
    "index": index("Course", "a1/index", "b1/index"),
    "a1/index": index("A1", "how-to/index"),
    "a1/how-to/index": index("How to", "greet", "thank"),
    "a1/how-to/greet": "# Greet\n\nText.\n",
    "a1/how-to/thank": "# Thank\n\nText.\n",
    "a1/grammar/verbs": "# Verbs\n\nText.\n",
    "a1/grammar/cases": "# Cases\n\nText.\n",
    "a1/vocabulary/food-1": "# Food\n\nText.\n",
    "a1/writing/letter-1": "# Letter\n\nText.\n",
    "a1/situations/at-a-party": situation("At a party", "a1/how-to/greet"),
    "a1/extra": "# Extra\n\nText.\n",
    "b1/index": index("B1", "grammar/past"),
    "b1/grammar/past": "# Past\n\nText.\n",
}


def page(related: str, title: str = "Page") -> str:
    return f"---\nrelated: {related}\n---\n# {title}\n\nText.\n"


def named(pages: dict[str, str]) -> dict[str, str]:
    return {k.replace("__", "/").replace("_", "-"): v for k, v in pages.items()}


def course(tmp_path, **pages: str):
    done = Build(tmp_path, extension="ol.docs.related")
    return done.run({**PAGES, **named(pages)})


def stopped(tmp_path, **pages: str) -> str:
    """The warnings of a build that stops, which must name the page at fault."""
    done = Build(tmp_path, extension="ol.docs.related")
    with pytest.raises(SphinxError):
        done.run({**PAGES, **named(pages)})
    return done.warnings.getvalue()


def section(done: Build, name: str) -> str:
    html = done.html(name)
    found = re.search(r'<section id="related-articles">.*?</section>', html, re.S)
    return found.group(0) if found else ""


def kinds(done: Build, name: str) -> list[str]:
    return re.findall(
        r'<p class="ol-related-kind"><strong>(.*?)</strong></p>', section(done, name)
    )


def links(done: Build, name: str) -> list[list[str]]:
    items = re.findall(r"<li>(.*?)</li>", section(done, name), re.S)
    return [re.sub(r"<[^>]+>", "", item).split() for item in items]


class TestRelatedSection:
    def test_it_is_the_last_section_titled_related_articles(self, tmp_path):
        done = course(tmp_path, a1__extra=page("[/a1/grammar/verbs]"))
        html = done.html("a1/extra")
        assert '<section id="related-articles">' in section(done, "a1/extra")
        assert "<h2>Related articles" in section(done, "a1/extra")
        assert html.index("<h1>Page") < html.index('id="related-articles"')

    def test_pages_are_grouped_by_kind_in_category_order(self, tmp_path):
        done = course(
            tmp_path,
            a1__extra=page(
                "[/a1/vocabulary/food-1, /a1/extra2, /a1/grammar/verbs, "
                "/a1/situations/at-a-party, /a1/how-to/thank]"
            ),
            a1__extra2="# Extra two\n\nText.\n",
        )
        assert kinds(done, "a1/extra") == [
            "How to",
            "Situations",
            "Grammar",
            "Vocabulary",
            "More",
        ]

    def test_links_keep_the_authors_order_within_a_kind(self, tmp_path):
        done = course(
            tmp_path, a1__extra=page("[/a1/grammar/verbs, /a1/grammar/cases]")
        )
        assert links(done, "a1/extra") == [["Verbs"], ["Cases"]]

    def test_a_page_of_another_level_carries_its_badge_and_one_of_the_same_does_not(
        self, tmp_path
    ):
        done = course(tmp_path, a1__extra=page("[/b1/grammar/past, /a1/grammar/verbs]"))
        assert links(done, "a1/extra") == [["Past", "B1"], ["Verbs"]]

    def test_a_link_written_twice_is_drawn_once(self, tmp_path):
        done = course(
            tmp_path, a1__extra=page("[/a1/grammar/verbs, /a1/grammar/verbs]")
        )
        assert links(done, "a1/extra") == [["Verbs"]]

    def test_the_section_holds_no_nested_section_and_no_link_box_class(self, tmp_path):
        done = course(tmp_path, a1__extra=page("[/a1/grammar/verbs]"))
        drawn = section(done, "a1/extra")
        assert "ol-links" not in drawn
        assert drawn.count("<section") == 1

    def test_a_how_to_article_folds_in_the_situations_naming_it(self, tmp_path):
        done = course(tmp_path)
        assert kinds(done, "a1/how-to/greet") == ["Situations"]
        assert links(done, "a1/how-to/greet") == [["At", "a", "party"]]

    def test_a_situation_folds_in_the_how_to_articles_it_names(self, tmp_path):
        done = course(tmp_path)
        assert kinds(done, "a1/situations/at-a-party") == ["How to"]
        assert links(done, "a1/situations/at-a-party") == [["Greet"]]

    def test_folded_links_follow_the_pages_own_entries_in_their_kind(self, tmp_path):
        done = course(
            tmp_path,
            a1__how_to__greet=page("[thank, /a1/grammar/verbs]"),
        )
        assert kinds(done, "a1/how-to/greet") == ["How to", "Situations", "Grammar"]

    def test_a_page_with_no_links_has_no_section(self, tmp_path):
        done = course(tmp_path)
        assert section(done, "a1/how-to/thank") == ""

    def test_the_boxes_draw_nothing_where_the_section_is_drawn(self, tmp_path):
        done = Build(tmp_path, extension="ol.docs.related").run(COURSE)
        assert "ol-links" not in done.html("a1/how-to/say-hello")
        assert "ol-links" not in done.html("a1/situations/at-a-party")
        assert links(done, "a1/how-to/say-hello")

    def test_a_box_on_a_page_whose_section_is_drawn_does_not_warn(self, tmp_path):
        done = Build(tmp_path, extension="ol.docs.related").run(COURSE)
        assert "box" not in done.warnings.getvalue()

    def test_a_page_with_a_written_section_and_no_related_is_drawn_as_before(
        self, tmp_path
    ):
        legacy = (
            "# Say hello\n\nText.\n\n:::{situations}\n:::\n\n"
            "## Related articles\n\n- [](/a1/grammar/verbs.md)\n"
        )
        done = Build(tmp_path, extension="ol.docs.related").run(
            {**COURSE, "a1/grammar/verbs": "# Verbs\n", "a1/how-to/say-hello": legacy}
        )
        html = done.html("a1/how-to/say-hello")
        assert "ol-links--situations" in html
        assert "ol-related-list" not in html
        assert "box" not in done.warnings.getvalue()

    def test_a_written_section_beside_related_warns_and_is_not_replaced(self, tmp_path):
        both = page("[/a1/grammar/verbs]") + "\n## Related articles\n\n- Text.\n"
        done = course(tmp_path, a1__extra=both)
        assert "hand-written" in done.warnings.getvalue()
        assert "ol-related-list" not in done.html("a1/extra")

    def test_a_missing_page_stops_the_build_and_names_the_page(self, tmp_path):
        found = stopped(tmp_path, a1__extra=page("[/a1/grammar/gone]"))
        assert "a1/extra" in found
        assert "a1/grammar/gone" in found

    def test_an_entry_ending_in_md_stops_the_build(self, tmp_path):
        found = stopped(tmp_path, a1__extra=page("[/a1/grammar/verbs.md]"))
        assert "a1/grammar/verbs.md" in found

    def test_an_entry_that_is_not_a_list_of_strings_stops_the_build(self, tmp_path):
        found = stopped(tmp_path, a1__extra=page("verbs"))
        assert "a1/extra" in found

    def test_adding_a_situation_redraws_the_how_to_article_it_names(self, tmp_path):
        done = course(tmp_path)
        done.run(
            {
                "a1/situations/in-a-cafe": situation("In a cafe", "a1/how-to/thank"),
                "a1/situations/index": index("Situations", "in-a-cafe"),
            }
        )
        assert links(done, "a1/how-to/thank") == [["In", "a", "cafe"]]
