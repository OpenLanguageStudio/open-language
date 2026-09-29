from pathlib import Path
from types import SimpleNamespace

from ol.docs.branding import Branding, apply_branding


def test_favicon_points_at_the_ico_in_brand_dir(tmp_path: Path):
    branding = Branding(brand_dir=tmp_path)
    assert branding.favicon() == str(tmp_path / "open-language.ico")


def test_logo_theme_option_pairs_light_and_dark(tmp_path: Path):
    branding = Branding(brand_dir=tmp_path)
    logo = branding.logo_theme_option()
    assert logo["image_light"] == str(tmp_path / "open-language-logo.svg")
    assert logo["image_dark"] == str(tmp_path / "open-language-logo-dark.svg")


def test_apply_branding_sets_favicon_and_logo_on_config():
    config = SimpleNamespace(html_favicon=None, html_theme_options={})
    apply_branding(app=None, config=config)
    assert config.html_favicon.endswith("open-language.ico")
    assert config.html_theme_options["logo"]["image_light"].endswith(
        "open-language-logo.svg"
    )
    assert config.html_theme_options["logo"]["image_dark"].endswith(
        "open-language-logo-dark.svg"
    )


def test_apply_branding_preserves_a_workspaces_own_theme_options():
    config = SimpleNamespace(
        html_favicon=None,
        html_theme_options={"header_links_before_dropdown": 2},
    )
    apply_branding(app=None, config=config)
    assert config.html_theme_options["header_links_before_dropdown"] == 2
    assert "logo" in config.html_theme_options


def test_apply_branding_lets_a_workspace_override_the_logo():
    config = SimpleNamespace(
        html_favicon=None,
        html_theme_options={"logo": {"image_light": "custom.svg"}},
    )
    apply_branding(app=None, config=config)
    assert config.html_theme_options["logo"]["image_light"] == "custom.svg"
    assert config.html_theme_options["logo"]["image_dark"].endswith(
        "open-language-logo-dark.svg"
    )
