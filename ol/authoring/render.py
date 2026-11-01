"""The render check: a page at phone width does not scroll sideways.

``ol check`` opens the built pages in a real browser, because only a browser
can say what the theme, the tables and the fonts come to together. It needs the
``render`` extra, and either a Chrome on the machine or Playwright's Chromium.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from ol.authoring.menu import LEVELS, MENU_CATEGORIES, TOP_LEVEL_PAGES
from ol.authoring.specs_data import SPECS

# The theme scrolls the article in a box of its own, so the window never moves
# and has to be asked along with every other scrolling box. A table or a code
# block scrolling inside its own box leaves the page where it is.
_SCROLLS_SIDEWAYS = """() => {
  const own = ".pst-scrollable-table-container, pre, .highlight";
  const scrolls = (el) => el.scrollWidth > el.clientWidth + 1;
  const scrollable = (el) =>
    ["auto", "scroll"].includes(getComputedStyle(el).overflowX);
  return scrolls(document.documentElement)
    || [...document.querySelectorAll("body *")].some(
      (el) => scrollable(el) && !el.matches(own) && scrolls(el)
    );
}"""


class RenderUnavailable(RuntimeError):
    """The check cannot open a browser."""


def sample_pages(workspace: Path) -> list[str]:
    """The pages the render check opens, as paths relative to the workspace.

    Every top-level page and index page, and the first articles of each
    category of each level.

    Args:
        workspace: The language repository's root.

    Returns:
        The pages, such as ``a1/grammar/index.md``.
    """
    per_type = SPECS["render"]["articles_per_type"]
    found = [f"{name}.md" for name in TOP_LEVEL_PAGES]
    for level in LEVELS:
        if not (workspace / level).is_dir():
            continue
        found.append(f"{level}/index.md")
        for category in MENU_CATEGORIES:
            pages = sorted((workspace / level / category).rglob("*.md"))
            indexes = [page for page in pages if page.name == "index.md"]
            articles = [page for page in pages if page.name != "index.md"]
            found += [
                page.relative_to(workspace).as_posix()
                for page in (*indexes, *articles[:per_type])
            ]
    return found


def _browser(playwright, error):
    """Open the machine's Chrome, or else Playwright's own Chromium."""
    failure = None
    for options in ({"channel": "chrome"}, {}):
        try:
            return playwright.chromium.launch(**options)
        except error as exc:
            failure = exc
    msg = (
        "no browser for the render check: install Chrome, or run "
        f"`playwright install chromium` ({failure})"
    )
    raise RenderUnavailable(msg) from failure


def overflowing_pages(html_root: Path, pages: Iterable[str]) -> list[str]:
    """The pages that scroll sideways at the width in ``specs.yml``.

    Args:
        html_root: The built site.
        pages: The pages, as paths to their Markdown.

    Returns:
        The pages that scroll sideways.

    Raises:
        RenderUnavailable: Playwright or a browser is not installed.
    """
    try:
        from playwright.sync_api import Error, sync_playwright
    except ImportError as exc:
        msg = "the render check needs the render extra: depend on open-language[render]"
        raise RenderUnavailable(msg) from exc

    viewport = {
        "width": SPECS["render"]["viewport_width"],
        "height": SPECS["render"]["viewport_height"],
    }
    overflowing = []
    with sync_playwright() as playwright:
        browser = _browser(playwright, Error)
        tab = browser.new_page(viewport=viewport)
        for page in pages:
            built = html_root / Path(page).with_suffix(".html")
            if not built.is_file():
                continue
            tab.goto(built.resolve().as_uri())
            if tab.evaluate(_SCROLLS_SIDEWAYS):
                overflowing.append(page)
        browser.close()
    return overflowing
