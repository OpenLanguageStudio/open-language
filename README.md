# Open Language

[![CI](https://github.com/OpenLanguageStudio/open-language/actions/workflows/ci.yml/badge.svg)](https://github.com/OpenLanguageStudio/open-language/actions/workflows/ci.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Authoring tools for the Open Language coursebooks: the Sphinx extensions that render a language workspace into a coursebook, the article templates, and the checks that keep new content in line with them.

Each language lives in its own workspace repository, which installs this package and runs `ol check` locally and in CI. The package itself holds nothing language-specific.

## What it provides

- **`ol check`** runs every content check in one pass: template conformance, the album audit (in workspaces that keep an `albums/` directory), and a strict docs build with warnings as errors. This is the command CI runs.
- **`ol validate`** checks articles and category indexes against the templates: required sections in order, frontmatter, titles, banned characters, audio-examples block grammar, example and marking limits, Prerequisites and Related articles links, vocabulary pack size, file names, and stock machine-writing vocabulary. The limits and the word list live in `ol/authoring/specs.yml`.
- **`ol audit`** cross-checks every `album.yml` track list against the audio-examples blocks in the docs, in both directions.
- **`ol/authoring/review-rubric.yml`** is the checklist for the part a script cannot judge: level, correctness, teaching value and plain language. Each item is answered pass, concern or fail.
- **[Authoring rules](docs/reference/authoring-rules.md)** holds the rules neither the checks nor the rubric cover. A language repository's `AGENTS.md` links it instead of restating it.
- **`ol templates`** lists the article templates, or prints one to start a new article from.
- **`ol docs`** builds the coursebook, with `--live` for a local preview that rebuilds on save.
- **`ol outline`** prints the heading structure of the CEFR-level docs.
- The Sphinx extensions `ol.docs.audio_examples`, `ol.docs.roles` and `ol.docs.branding`, plus the shared stylesheet, fonts and brand assets.

## Install

The package is installed from this repository and is not published to a package index. Pin a tag, or a commit until the first tag exists:

```bash
uv add "open-language @ git+https://github.com/OpenLanguageStudio/open-language@<tag-or-commit>"
```

## Scope & philosophy

**What it is.** The single definition of what an Open Language Coursebook page must be: the article templates, the checks that hold articles to them, the grammar of an `audio-examples` block, and the Sphinx extensions that build the pages. The Open Language app reads pages through the same code, so a page that passes `ol check` is a page the app can show.

**What it deliberately is not.**

- Not a language. It holds no content and no rule that only one language needs.
- Not an audio tool. Recording and producing tracks happen elsewhere, and this package never depends on audio libraries.
- Not a place for taste. A check measures something a script can measure. What needs a reader goes in the review rubric.

**When two goals pull apart.** The checks follow what the app can read, because a page it cannot read never reaches a learner. A rule is written once, here, rather than restated in a language repository or a second implementation.

## A language workspace

```text
german/
├── open-language.yml      language code, name, title, description
├── docs/                  conf.py, index.md, then docs/<level>/<category>/...
├── albums/                albums/<level>/<category>/<album>/album.yml
└── .ol-validate-baseline  optional list of known failures
```

`docs/conf.py` loads the extensions and reads the workspace configuration:

```python
from ol.language import Language

lang = Language()
html_title = lang.title
extensions = [
    "myst_parser",
    "ol.docs.roles",
    "ol.docs.audio_examples",
    "ol.docs.branding",
]
```

## Adopting the checks on existing content

Content written before the templates will fail `ol validate`. Record the current failures once, commit the file, and the check then fails only on new problems:

```bash
ol validate --write-baseline
```

When a listed article is fixed, `ol validate` says so and the line comes out of the file. The baseline only ever shrinks.

## Development

```bash
uv sync
uv run pytest
uv run ruff check .
```

## License

MIT for the code. The bundled fonts (Bricolage Grotesque, Literata, JetBrains Mono) are distributed under the SIL Open Font License.
