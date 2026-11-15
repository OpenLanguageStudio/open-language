"""The course's levels, and the colour each one is drawn in.

A level has one colour wherever it appears: the level badge on a Coursebook page,
an album cover and the app all read it from here. The colours are categorical,
not a ramp, and they never follow the reader's light or dark mode, because a
cover is a picture and cannot.
"""

from __future__ import annotations

from dataclasses import dataclass

INK = "#1e1a15"
"""The dark text colour drawn on a light level colour."""
PAPER = "#fbf7f0"
"""The light text colour drawn on a dark level colour."""


@dataclass(frozen=True)
class LevelColour:
    """A level's colour, and the colour of anything drawn on it."""

    background: str
    text: str


LEVEL_COLOURS = {
    "a1": LevelColour("#eeb849", INK),
    "a2": LevelColour("#a4563a", PAPER),
    "b1": LevelColour("#79b3a8", INK),
    "b2": LevelColour("#496695", PAPER),
}
"""Each level, by its lower-case code, from A1 to B2."""

LEVELS = tuple(LEVEL_COLOURS)
"""Every level, by its lower-case code, in the order of the course."""
