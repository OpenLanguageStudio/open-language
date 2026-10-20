from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(params=["docs", "root"])
def src(request, tmp_path: Path) -> Path:
    """The folder of a workspace's pages, in each layout a workspace may have.

    In the ``docs`` layout the pages and ``conf.py`` sit under
    ``<workspace>/docs``. In the ``root`` layout they sit at the top of the
    workspace, which is ``tmp_path``.
    """
    pages = tmp_path / "docs" if request.param == "docs" else tmp_path
    pages.mkdir(exist_ok=True)
    (pages / "conf.py").write_text("", encoding="utf-8")
    return pages
