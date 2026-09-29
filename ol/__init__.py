"""Open Language authoring tools: content validation and the Sphinx coursebook build.

Typical use from a language workspace::

    ol check        # validate articles, audit albums, build the docs strictly
    ol validate     # template conformance only
    ol docs --live  # local preview
"""

from importlib.metadata import PackageNotFoundError, version

from .language import Language

try:
    __version__ = version("open-language")
except PackageNotFoundError:  # running from a source tree without an install
    __version__ = "0.0.0"

__all__ = ["Language", "__version__"]
