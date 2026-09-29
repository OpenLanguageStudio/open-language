"""Language workspace configuration, loaded from ``open-language.yml``.

A language workspace is a directory holding ``open-language.yml``, a ``docs/``
tree of articles and an ``albums/`` tree of album manifests. Paths resolve by
convention from the working directory, or from the ``OPEN_LANGUAGE_CONFIG``,
``OPEN_LANGUAGE_DOCS`` and ``OPEN_LANGUAGE_ALBUMS`` environment variables.

This class carries the configuration the coursebook build and the content
checks need. Audio production extends it elsewhere; keys this package does not
use (voices, for example) are kept on ``config`` untouched.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml


class Language:
    """Language metadata and workspace paths for one language workspace."""

    def __init__(self) -> None:
        config_path = Path(os.getenv("OPEN_LANGUAGE_CONFIG", "open-language.yml"))
        if not config_path.exists():
            msg = (
                f"{config_path} not found. Run from a language workspace or set "
                "OPEN_LANGUAGE_CONFIG."
            )
            raise FileNotFoundError(msg)
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

        self.config: dict = config
        self.config_path = config_path
        self.code: str = config["language_code"]
        self.name: str = config["language"]
        self.title: str = config.get("title", "")
        self.description: str = config.get("description", "")
        self.author: str = config.get("author", "")
        self.docs_root = Path(os.getenv("OPEN_LANGUAGE_DOCS", "docs"))
        self.albums_root = Path(os.getenv("OPEN_LANGUAGE_ALBUMS", "albums"))

    def __repr__(self) -> str:
        return f"Language(code={self.code!r}, name={self.name!r})"
