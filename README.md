# Open Language

[![CI](https://github.com/OpenLanguageStudio/open-language/actions/workflows/ci.yml/badge.svg)](https://github.com/OpenLanguageStudio/open-language/actions/workflows/ci.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Authoring tools for the Open Language coursebooks: the Sphinx extensions that render a language workspace into a coursebook, the article templates, and the checks that keep new content in line with them.

Each language lives in its own workspace repository, which installs this package and runs `ol check` locally and in CI. The package itself holds nothing language-specific.

## What it provides

- **`ol check`** runs every content check in one pass: `ol validate`, a strict docs build with warnings as errors, then a render check that opens every built page at a 360 pixel viewport and fails if one scrolls sideways. This is the command CI runs. The render check needs the `render` extra (`open-language[render]`) and a Chrome on the machine, or Playwright's Chromium.
- **`ol validate`** checks articles and category indexes against the templates: required sections in order, frontmatter, titles, banned characters, `audio-examples` blocks with a code for each refusal, example and marking limits, Prerequisites and Related articles links, vocabulary pack size, file names, and stock machine-writing vocabulary. It also holds every page to the [page standard](docs/reference/page-standard.md): the opening paragraphs, heading and table limits, sentence and paragraph limits, the sections of each category, the level and Introduction pages, and the glossary. The limits and the word list live in `ol/authoring/specs.yml`. Run without files, it also checks the site menu (below).
- **`ol.blocks`** reads `audio-examples` blocks and says why a block is refused. The checks, the Sphinx extension and the Open Language app all read blocks through it. See [The audio-examples block](#the-audio-examples-block).
- **`ol/authoring/review-rubric.yml`** is the checklist for the part a script cannot judge: level, correctness, teaching value and plain language. Each item is answered pass, concern or fail.
- **[Authoring rules](docs/reference/authoring-rules.md)** holds the rules neither the checks nor the rubric cover. A language repository's `AGENTS.md` links it instead of restating it.
- **[Components](docs/reference/components.md)** shows how to write each part of a page, from roles and notices to card grids, and lists the Sphinx and sphinx-design elements a page never uses.
- **`ol templates`** lists the article templates, or prints one to start a new article from.
- **`ol docs`** builds the coursebook, with `--live` for a local preview that rebuilds on save.
- **`ol outline`** prints the heading structure of the CEFR-level docs.
- The Sphinx extensions `ol.docs.audio_examples` (which loads `ol.docs.page_examples` and `ol.docs.situations`), `ol.docs.roles` and `ol.docs.branding`, plus the shared stylesheet, fonts and brand assets.
- The page layout in `ol/docs/_templates`, which a workspace's `conf.py` adds to `templates_path`. Its footer says, on every page, that the text is © Open Language under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) and that the audio recordings are not covered by that licence: all rights reserved, no use for AI training.

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
├── open-language.yml      language code, name, title, description, translation_headers
├── conf.py
├── index.md
├── <level>/<category>/... the pages
└── .ol-validate-baseline  optional list of known failures
```

The pages sit at the top of the workspace, next to `conf.py`, and the build goes to `_build/html`. Paths in `.ol-validate-baseline` are relative to the workspace. `_build`, `.venv`, `.github`, `README.md` and `AGENTS.md` at the top are never read as pages.

Every workspace builds the same menu, and `ol validate` fails when it does not:

- The top level holds exactly four pages, each with its H1 and at least one paragraph of prose: `index.md` ("Introduction"), `how_to_use.md` ("How to use"), `terminology.md` ("Terminology") and `contributing.md` ("Contributing"). Any other `.md` there fails, apart from `README.md` and `AGENTS.md`. `ol templates` has a template for each: `introduction.md`, `how-to-use.md`, `terminology.md`, `contributing.md`.
- `index.md` is the Introduction page and holds the menu. Its one toctree lists `how_to_use`, `terminology` and `contributing` in that order, then `a1/index`, `a2/index`, `b1/index` and `b2/index` in that order.
- Every level directory has an `index.md` in that toctree, not marked `orphan: true`. There are no levels above B2.
- Each level index has one toctree listing only `how-to/index`, `situations/index`, `grammar/index`, `writing/index` and `vocabulary/index`, in that order. A level may leave a category out. A level has no other category directories.
- No external links or other entries in these toctrees. A menu error is never covered by the baseline.

`conf.py` loads the extensions and reads the workspace configuration:

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

## Plain examples

An `ol-examples` box shows sentences beside the explanation they illustrate, each with its translation under it. It holds a definition list, a sentence may be marked up with roles and bold, and `:presenters:` names the one presenter who says every sentence in it:

```markdown
:::{ol-examples}
:presenters: emilia
{article}`Der` Hafen ist groß.
: The harbour is big.
:::
```

The box is the `ol-examples` directive, `ol.docs.page_examples.ExamplesBox`. The module's `setup` registers it and `ol.docs.audio_examples` loads the module, so a language repository's `extensions` stay as they are. It is drawn as a `div` of class `ol-examples`. What is spoken is the sentence as the reader sees it, with its roles and emphasis gone. `ol validate` fails a box with no `:presenters:`, one that names more than one presenter or a value that is not a slug, and a box that gives one sentence twice. It cannot know who the presenters are, since that is not part of a language workspace. Whoever serves the pages decides what a name means.

`ol.docs.page_examples.PageExamples.read(doctree)` reads a built page's boxes into `ol.blocks.Example` values, in page order, each with its box's presenter as `presenter`, skipping a box that holds anything but sentences and translations. `ol.blocks.BlockReader.spoken(text)` gives the same sentence from a page's Markdown.

## The Situations and How to boxes

`ol.docs.situations` adds two boxes, written with no options and no body. A situation article names the how-to articles it puts to use in its front matter, and both boxes are drawn from that list (ADR 2):

```markdown
---
how-to:
  - /a1/how-to/introduce-yourself.md
---
# At a party

Lena meets Tom at a friend's party.

:::{how-to-links}
:::
```

- `how-to-links`, on a situation article, links each how-to article its front matter names, in that order.
- `situations`, on a how-to article, links every situation article whose front matter names it, at any level: by level, then in the order of that level's `situations/index` toctree.

Each link has the target page's title as its text, as a link with empty brackets does. A link to a page of another level is followed by the level badge. A box is drawn once every page is read, and a how-to article is written again whenever the list of situations naming it changes, so adding, removing or reordering a situation redraws the pages it names. A box that would link nothing warns and is left out.

Each box is a `div` of class `ol-links` and `ol-links--situations` or `ol-links--how-to-links`, holding a title and a list. `link-boxes.css` styles it from the accents in `marks.css`, so an app that draws the pages in its own theme links both files. `ol.docs.audio_examples` loads the module, so a language repository's `extensions` stay as they are.

## The stack role

`ol.docs.roles` adds the `stack` role, which shows a phrase with its translation beneath it. It suits a table cell, a list item or a sentence, where a separate column of translations would be too wide for a phone:

```markdown
Say {stack}`Guten Morgen | Good morning` to a friend.

| Phrase | Notes |
|---|---|
| {stack}`Guten Morgen \| Good morning` | Used until about noon. |
```

The phrase and its translation are separated by the first ` | ` (a space, a pipe and a space). The translation may contain more pipes. Inside a Markdown table a pipe splits the cell, so write the separator as `\|` there.

The role writes this HTML, with both texts escaped. `lang` is the `language_code` in `open-language.yml` and is left out when none is set:

```html
<span class="ol-stack"><span class="ol-stack-target" lang="de">Guten Morgen</span><span class="ol-stack-translation">Good morning</span></span>
```

The shared stylesheet shows the phrase in normal weight with the translation beneath it, smaller and muted. A text with no separator shows unstacked and warns with the page and line.

## The level role

`ol.docs.roles` also adds the `level` role, a level badge drawn in that level's colour. It follows a link to a page of another level:

```markdown
- [](/b1/grammar/relativsaetze.md) {level}`B1`
```

The colours are in `ol/levels.py`, `LEVEL_COLOURS`, the one place they are defined: album covers read the same table, so a level looks the same on a page and on a cover. The role writes the colour on the badge itself:

```html
<span class="ol-level ol-level--b1" style="background-color: #79b3a8; color: #1e1a15">B1</span>
```

A level other than A1, A2, B1 or B2 is a build warning with the page and line, and shows as plain text.

## Styling pages drawn outside the Sphinx site

`ol/docs/_static/marks.css` styles the marking roles and the level badge and nothing else, so a site that draws a coursebook's built HTML in its own theme links it on its own. The shared `stylesheet.css` imports it. Its dark colours apply under an `html` element whose `data-theme` ends in `dark`.

## The glossary

The Terminology page is the glossary, and its entries sit in Sphinx `{glossary}` directives. A technical term is any word on the shared `ol/authoring/glossary-terms.yml` or on a language repository's own `glossary-terms.yml`. `ol validate` fails a listed term with no entry, and the first use of a listed term in an article's prose unless it is written with the `term` role. The build fails on a `{term}` the glossary does not hold. [The authoring rules](docs/reference/authoring-rules.md#the-glossary) show the format.

## The audio-examples block

A block names a track by its address and either writes it, by giving its examples, or shows a track another block writes:

```markdown
:::{audio-examples}
:track: a2/grammar/nebensatz-mit-weil
:presenters: lina
:title: Nebensatz mit weil
:title-en: Subordinate clauses with weil
:tags: nebensatz, konjunktionen

Ich bleibe zu Hause, weil ich krank bin.
: I am staying at home because I am ill.
:::
```

| Option | Meaning |
|---|---|
| `:track:` | The track's address, `level/category/name`, in lower case. All three parts are always written: the name is never taken from the page. An album is never part of it. |
| `:title:` | The track's title in the language taught |
| `:title-en:` | The title in English |
| `:tags:` | Words that say what the track is about, separated by commas |
| `:presenters:` | The slugs of the presenters who say the track, separated by commas, in the order the mode gives them a meaning. Every block that writes carries it, and the first presenter speaks the spoken title. |
| `:mode:` | How the examples are read and spoken: `examples` (the default), `pairs`, `dialogue`, `passage` or `correspondence` |
| `:duplicate:` | The block shows a track another block writes and writes nothing. It carries only `:track:` and, if wanted, `:tags:`. |

The body holds the examples: a sentence, then its translation on the next line after `: `. A sentence and its translation are plain text, with no role markup, backticks or braces.

### Modes

| Mode | For | Presenters | Body |
|---|---|---|---|
| `examples` | One model sentence after another | Exactly 1 | A sentence, then `: translation`. |
| `pairs` | A question and its answer, or a prompt and its changed form | 1 or 2 | Groups of exactly two examples, separated by a blank line. The first presenter says the first example of every pair and the second presenter the second. With one presenter, they say both. |
| `dialogue` | A conversation, spoken or in text messages | 2 or more | Each sentence starts with its presenter's slug and a colon: `lina: Ist hier noch frei?`. A blank line ends an exchange. |
| `passage` | A connected text one presenter says in full: a letter, an email, a voicemail | Exactly 1 | Each example is its lines, then its translation's lines each after `: `. |
| `correspondence` | Written messages sent back and forth: emails, letters, postcards | 2 or more | Each message opens with a line holding only its presenter's slug and a colon, such as `lina:`, then its lines, then its translation's lines. |

In a `passage` example and a `correspondence` message, a blank line ends the example only after its translation, where the next line is the next example's text or the next message's slug line. Any blank line before that is a paragraph break, on the page and in the audio.

```markdown
:::{audio-examples}
:track: a1/grammar/doch
:title: Doch
:mode: pairs
:presenters: deniz, lina

Hast du keine Zeit?
: Don't you have time?
Doch, ich habe Zeit.
: Yes, I do have time.
:::
```

A block is refused with one of these codes:

| Code | The block |
|---|---|
| `unknown_option` | has an option it does not take, such as the retired `:album:`, `:name:`, `:voice:`, `:spotify:` or `:youtube-music:` |
| `bad_address` | has no `:track:`, or one that is not three lower-case names separated by `/` |
| `unknown_mode` | has a `:mode:` that is not one of the five. Its body is not read. |
| `missing_examples` | gives no examples and has no `:duplicate:` |
| `duplicate_writes` | has `:duplicate:` and gives examples, a title, an English title, a mode or presenters |
| `missing_presenters` | writes its track and has no `:presenters:` |
| `bad_presenters` | has a `:presenters:` value that is not a slug, names a presenter twice, or names the wrong number of presenters for its mode |
| `bad_pair` | is a `pairs` block with a group that is not exactly two examples |
| `presenter_not_listed` | is a `dialogue` or `correspondence` block with an example that names a presenter `:presenters:` does not list |
| `presenter_silent` | is a `dialogue` or `correspondence` block that lists a presenter who says nothing in it |
| `sentence_twice` | is an `examples` block that gives the same sentence twice, compared after Unicode normalisation, with spacing tidied and the emphasis marks `*` and `_` removed. Case and punctuation count. A conversation may repeat "Ja." on purpose, so no other mode is refused for it. |
| `written_twice` | writes a track another block writes too. Each of them is refused. |
| `orphan_duplicate` | has `:duplicate:` and names a track no block writes |
| `unknown_presenter` | names a presenter the language does not have. The package defines this code and never reports it: only the app knows the presenters. |

`written_twice` and `orphan_duplicate` need every page of a build, so `ol validate` reads every page of the workspace for them, whichever files it is checking. The Sphinx extension `ol.docs.audio_examples` reports each of the other codes as a build warning, and shows a duplicate with the examples of the block that writes its track. In a build, an option the block does not take is reported by MyST as an unknown option.

### Reading blocks in code

```python
from pathlib import Path

from ol.blocks import BlockCollection, BlockReader

reader = BlockReader()
block = reader.read(
    "a2/grammar/nebensatz-mit-weil",
    {
        "track": "a2/grammar/nebensatz-mit-weil",
        "title": "Nebensatz mit weil",
        "presenters": "lina",
    },
    [
        "Ich bleibe zu Hause, weil ich krank bin.",
        ": I am staying at home because I am ill.",
    ],
    line=12,
)
block.address  # "a2/grammar/nebensatz-mit-weil"
block.mode  # "examples"
block.presenters  # ("lina",)
block.examples  # (Example(sentence="Ich bleibe ...", translation="I am ...",
#                  presenter="lina", group=1),)
block.refusals  # ()

for refusal in BlockCollection.from_docs(Path("docs")).refusals():
    print(refusal.block.page, refusal.block.line, refusal.code, refusal.detail)
```

| Name | What it is |
|---|---|
| `BlockReader.read(page, options, body, line)` | Reads one block from its options, by name, and the lines of its body. A flag's value is ignored. |
| `BlockReader.find(page, text)` | Reads every block on a page of Markdown. A block quoted in a code fence is not a block. |
| `BlockReader.sentence_key(text)` | The form two sentences are compared in for `sentence_twice` |
| `Block` | One block: `page`, `line`, `address`, `level`, `category`, `name`, `title`, `title_en`, `tags`, `examples`, `mode`, `presenters`, `duplicate`, `writes` and `refusals`, the codes it earns on its own |
| `Example` | One example: `sentence`, `translation`, `presenter`, the slug of the presenter who says it, worked out from the block's mode, and `group`, the number of the pair, exchange or message thread it belongs to, counted from 1. In `examples` and `passage` each example is its own group, and every message of a `correspondence` block is in group 1. |
| `BlockFormatError` | Raised when a body cannot be read as examples, such as a sentence with no translation or a line with markup |
| `BlockCollection(blocks)` | Every block of a build. `from_pages(pages)` and `from_docs(root)` read them from Markdown. |
| `BlockCollection.refusals()` | Every `Refusal` of the build: each block's own, then the ones that need more than one page |
| `Refusal` | A refused `block` and its `code`, with an author-facing `detail`. `Refusal.CODES` lists every code, `Refusal.CROSS_PAGE` the ones that need every page and `Refusal.APP_ONLY` the ones only the app reports. |
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
