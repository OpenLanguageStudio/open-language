from pathlib import Path

import yaml

from ol.docs.audio_examples import build_audio_examples_html, load_track_examples
from ol.docs_source import parse_example_pairs


def _make_album(root: Path):
    tracks = root / "albums" / "a1" / "grammar" / "test" / "tracks"
    tracks.mkdir(parents=True, exist_ok=True)
    (tracks / "nominativ.yml").write_text(
        yaml.dump(
            {
                "title": {"de": "Nominativ", "en": "Nominative"},
                "streaming": {"spotify": "https://open.spotify.com/album/x"},
                "examples": [{"de": "Der Hund schläft.", "en": "The dog sleeps."}],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_load_track_examples_reads_new_schema(tmp_path: Path):
    _make_album(tmp_path)
    examples, spotify, youtube = load_track_examples(
        tmp_path, "a1/grammar/test", "nominativ.yml"
    )
    assert examples[0]["de"] == "Der Hund schläft."
    assert spotify == "https://open.spotify.com/album/x"
    assert youtube == ""


def test_build_html_contains_sentence_and_spotify():
    html = build_audio_examples_html(
        [("Der Hund schläft.", "The dog sleeps.")],
        "https://open.spotify.com/album/x",
        "",
    )
    assert "Der Hund schläft." in html
    assert "The dog sleeps." in html
    assert "https://open.spotify.com/album/x" in html
    assert "ae-container" in html


def test_build_html_without_links_shows_coming_soon():
    html = build_audio_examples_html([("Eins.", "One.")], "", "")
    assert "Streaming links coming soon" in html


def test_directive_content_flows_through_shared_parser():
    """The directive body grammar and the extractor grammar are one function."""
    content = ["Der Hund schläft.", ": The dog sleeps."]
    pairs = parse_example_pairs(content, "test")
    html = build_audio_examples_html(pairs, "", "")
    assert "Der Hund schläft." in html
    assert "The dog sleeps." in html
