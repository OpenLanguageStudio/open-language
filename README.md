# Open Language

Authoring tools for the Open Language coursebooks: the Sphinx extensions that render a language workspace into a coursebook, the article templates, and the checks that keep new content in line with them.

Each language lives in its own workspace repository, which installs this package and runs `ol check` locally and in CI. The package itself holds nothing language-specific.

## What it provides

- **`ol check`** runs every content check in one pass: template conformance, the album audit (in workspaces that keep an `albums/` directory), and a strict docs build with warnings as errors. This is the command CI runs.
- **`ol validate`** checks articles and category indexes against the templates: required sections in order, frontmatter, banned characters, audio-examples block grammar, example and marking limits, and stock machine-writing vocabulary. The limits and the word list live in `ol/authoring/specs.yml`.
- **`ol audit`** cross-checks every `album.yml` track list against the audio-examples blocks in the docs, in both directions.
- **`ol/authoring/review-rubric.yml`** is the checklist for the part a script cannot judge: level, correctness, teaching value and plain language. Each item is answered pass, concern or fail.
- **`ol templates`** lists the article templates, or prints one to start a new article from.
- **`ol docs`** builds the coursebook, with `--live` for a local preview that rebuilds on save.
- **`ol outline`** prints the heading structure of the CEFR-level docs.
- The Sphinx extensions `ol.docs.audio_examples`, `ol.docs.roles` and `ol.docs.branding`, plus the shared stylesheet, fonts and brand assets.

## Install

```bash
uv add open-language
```

Until the first release is on PyPI, install from the repository:

```bash
uv add "open-language @ git+https://github.com/OpenLanguageStudio/open-language"
```

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
