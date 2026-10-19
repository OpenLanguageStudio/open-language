# Open Language

[![CI](https://github.com/OpenLanguageStudio/open-language/actions/workflows/ci.yml/badge.svg)](https://github.com/OpenLanguageStudio/open-language/actions/workflows/ci.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Authoring tools for the Open Language coursebooks: the Sphinx extensions that render a language workspace into a coursebook, the article templates, and the checks that keep new content in line with them.

Each language lives in its own workspace repository, which installs this package and runs `ol check` locally and in CI. The package itself holds nothing language-specific.

## What it provides

- **`ol check`** runs every content check in one pass: template conformance and a strict docs build with warnings as errors. This is the command CI runs.
- **`ol validate`** checks articles and category indexes against the templates: required sections in order, frontmatter, titles, banned characters, `audio-examples` blocks with a code for each refusal, example and marking limits, Prerequisites and Related articles links, vocabulary pack size, file names, and stock machine-writing vocabulary. The limits and the word list live in `ol/authoring/specs.yml`.
- **`ol.blocks`** reads `audio-examples` blocks and says why a block is refused. The checks, the Sphinx extension and the Open Language app all read blocks through it. See [The audio-examples block](#the-audio-examples-block).
- **`ol/authoring/review-rubric.yml`** is the checklist for the part a script cannot judge: level, correctness, teaching value and plain language. Each item is answered pass, concern or fail.
- **[Authoring rules](docs/reference/authoring-rules.md)** holds the rules neither the checks nor the rubric cover. A language repository's `AGENTS.md` links it instead of restating it.
- **`ol templates`** lists the article templates, or prints one to start a new article from.
- **`ol docs`** builds the coursebook, with `--live` for a local preview that rebuilds on save.
- **`ol outline`** prints the heading structure of the CEFR-level docs.
- The Sphinx extensions `ol.docs.audio_examples`, `ol.docs.roles` and `ol.docs.branding`, plus the shared stylesheet, fonts and brand assets.

## Install

The package is installed from this repository and is not published to a package index. Pin a release tag:

```bash
uv add "open-language @ git+https://github.com/OpenLanguageStudio/open-language@v0.1.0"
```

Releases and their notes are listed on the repository's Releases page.

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

## The audio-examples block

A block names a track by its address and either writes it, by giving its examples, or shows a track another block writes:

```markdown
:::{audio-examples}
:track: a2/grammar/nebensatz-mit-weil
:title: Nebensatz mit weil
:title-en: Subordinate clauses with weil
:tags: nebensatz, konjunktionen

Ich bleibe zu Hause, weil ich krank bin.
: I am staying at home because I am ill.
:::
```

| Option | Meaning |
|---|---|
| `:track:` | The track's address, `level/category/name`, in lower case. With only `level/category`, the name is the page's own name. An album is never part of it. |
| `:title:` | The track's title in the language taught |
| `:title-en:` | The title in English |
| `:tags:` | Words that say what the track is about, separated by commas |
| `:multiline:` | Each example may run over several lines, as in a model text |
| `:duplicate:` | The block shows a track another block writes and writes nothing. It carries only `:track:` and, if wanted, `:tags:`. |

The body holds the examples: a sentence, then its translation on the next line after `: `. A sentence and its translation are plain text, with no role markup, backticks or braces.

A block is refused with one of these codes:

| Code | The block |
|---|---|
| `unknown_option` | has an option it does not take, such as the retired `:album:`, `:name:`, `:voice:`, `:spotify:` or `:youtube-music:` |
| `bad_address` | has no `:track:`, or one that is not two or three lower-case names separated by `/` |
| `missing_examples` | gives no examples and has no `:duplicate:` |
| `duplicate_writes` | has `:duplicate:` and gives examples, a title or an English title |
| `sentence_twice` | gives the same sentence twice, compared after Unicode normalisation, with spacing tidied and the emphasis marks `*` and `_` removed. Case and punctuation count. |
| `written_twice` | writes a track another block writes too. Each of them is refused. |
| `orphan_duplicate` | has `:duplicate:` and names a track no block writes |

The last two need every page of a build, so `ol validate` reads the whole `docs/` tree for them, whichever files it is checking. The Sphinx extension `ol.docs.audio_examples` reports each of the other codes as a build warning, and shows a duplicate with the examples of the block that writes its track. In a build, an option the block does not take is reported by MyST as an unknown option.

### Reading blocks in code

```python
from pathlib import Path

from ol.blocks import BlockCollection, BlockReader

reader = BlockReader()
block = reader.read(
    "a2/grammar/nebensatz-mit-weil",
    {"track": "a2/grammar", "title": "Nebensatz mit weil"},
    [
        "Ich bleibe zu Hause, weil ich krank bin.",
        ": I am staying at home because I am ill.",
    ],
    line=12,
)
block.address  # "a2/grammar/nebensatz-mit-weil"
block.examples  # (Example(sentence="Ich bleibe zu Hause, ...", translation="I am ..."),)
block.refusals  # ()

for refusal in BlockCollection.from_docs(Path("docs")).refusals():
    print(refusal.block.page, refusal.block.line, refusal.code, refusal.detail)
```

| Name | What it is |
|---|---|
| `BlockReader.read(page, options, body, line)` | Reads one block from its options, by name, and the lines of its body. A flag's value is ignored. |
| `BlockReader.find(page, text)` | Reads every block on a page of Markdown. A block quoted in a code fence is not a block. |
| `BlockReader.sentence_key(text)` | The form two sentences are compared in for `sentence_twice` |
| `Block` | One block: `page`, `line`, `address`, `level`, `category`, `name`, `title`, `title_en`, `tags`, `examples`, `multiline`, `duplicate`, `writes` and `refusals`, the codes it earns on its own |
| `Example` | One example: `sentence` and `translation` |
| `BlockFormatError` | Raised when a body cannot be read as examples, such as a sentence with no translation or a line with markup |
| `BlockCollection(blocks)` | Every block of a build. `from_pages(pages)` and `from_docs(root)` read them from Markdown. |
| `BlockCollection.refusals()` | Every `Refusal` of the build: each block's own, then the ones that need more than one page |
| `Refusal` | A refused `block` and its `code`, with an author-facing `detail`. `Refusal.CODES` lists every code and `Refusal.CROSS_PAGE` the ones that need every page. |
| `load_samples()` | The sample blocks in `ol/authoring/samples/`, each a `Sample` with its `pages` and the outcome it should get in `expect`: `accepted` or a refusal code. `Sample.blocks()` reads its pages. |

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
