"""Sphinx extension: wires the Open Language visual identity into every
workspace's docs build. Assets live under ``_static/brand`` in this package
so a language workspace enables branding by adding this extension to its
``conf.py``, the same way it already does for ``ol.docs.roles`` and
``ol.docs.audio_examples`` — it never copies or re-tracks the files itself.
"""

from pathlib import Path

_BRAND_DIR = Path(__file__).parent / "_static" / "brand"


class Branding:
    """Resolves the Open Language identity assets pydata-sphinx-theme needs.

    A class rather than functions because both members answer the same
    question — "what represents the site chrome?" — and share the one
    directory they resolve paths from.
    """

    def __init__(self, brand_dir: Path = _BRAND_DIR):
        self.brand_dir = brand_dir

    def favicon(self) -> str:
        return str(self.brand_dir / "open-language.ico")

    def logo_theme_option(self) -> dict:
        # image_light / image_dark is pydata-sphinx-theme's own swap
        # mechanism (data-theme attribute, no layout shift) — the pairing
        # the brand handoff was designed for.
        return {
            "image_light": str(self.brand_dir / "open-language-logo.svg"),
            "image_dark": str(self.brand_dir / "open-language-logo-dark.svg"),
        }


def apply_branding(app, config):
    branding = Branding()
    config.html_favicon = branding.favicon()
    theme_options = dict(config.html_theme_options or {})
    theme_options["logo"] = {
        **branding.logo_theme_option(),
        **theme_options.get("logo", {}),
    }
    config.html_theme_options = theme_options


def setup(app):
    app.connect("config-inited", apply_branding)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
