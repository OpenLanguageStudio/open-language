"""The limits in ``specs.yml``, read once for every check."""

from __future__ import annotations

from pathlib import Path

import yaml

SPECS_PATH = Path(__file__).resolve().parent / "specs.yml"
SPECS = yaml.safe_load(SPECS_PATH.read_text(encoding="utf-8"))
