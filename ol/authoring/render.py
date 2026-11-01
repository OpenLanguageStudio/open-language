"""The render check: a page at phone width does not scroll sideways.

``ol check`` opens the built pages in a real browser, because only a browser
can say what the theme, the tables and the fonts come to together. It needs the
``render`` extra, and either a Chrome on the machine or Playwright's Chromium.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

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


def built_pages(html_root: Path) -> list[str]:
    """Every page of the built site, as paths to their Markdown.

    Args:
        html_root: The built site.

    Returns:
        The pages, such as ``a1/grammar/index.md``. Sphinx's own directories,
        which start with an underscore, hold no pages.
    """
    pages = (page.relative_to(html_root) for page in html_root.rglob("*.html"))
    return sorted(
        page.with_suffix(".md").as_posix()
        for page in pages
        if not any(part.startswith("_") for part in page.parts)
    )


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
            tab.goto(built.resolve().as_uri())
            if tab.evaluate(_SCROLLS_SIDEWAYS):
                overflowing.append(page)
        browser.close()
    return overflowing
