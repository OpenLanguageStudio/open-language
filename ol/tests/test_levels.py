"""Every level has one colour, and the course's levels are the ones coloured."""

from __future__ import annotations

from ol.authoring.menu import LEVELS as MENU_LEVELS
from ol.levels import INK, LEVEL_COLOURS, LEVELS, PAPER


def test_the_levels_run_from_a1_to_b2():
    assert LEVELS == ("a1", "a2", "b1", "b2")


def test_the_menu_reads_the_same_levels():
    assert MENU_LEVELS is LEVELS


def test_each_level_is_drawn_in_its_album_cover_colour():
    assert {level: (c.background, c.text) for level, c in LEVEL_COLOURS.items()} == {
        "a1": ("#eeb849", INK),
        "a2": ("#a4563a", PAPER),
        "b1": ("#79b3a8", INK),
        "b2": ("#496695", PAPER),
    }
