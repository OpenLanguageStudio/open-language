# Changelog

## [Unreleased]

## [0.8.0] - 2026-11-01

### Changed: `ol check` holds every page to the page standard

`docs/reference/page-standard.md` sets the shape of every page, and every rule it tags V, M or B now has its check. This breaks most existing pages. On adopting this version, run `ol validate --write-baseline` once, and the baseline covers them until they are migrated. Menu errors are never baselined.

- `ol validate` now reads the top-level `index.md` and `terminology.md` as well as the level directories.
- Articles: lead and explanation lengths, the place of Prerequisites, title and heading limits, table columns and headers, an error on a column for the language taught next to one for its translation, sentence and paragraph limits, and the sections of each category in order. Article sections are declared under `sections` in `specs.yml`, which replaces `required_headings`.
- Level overview and Introduction pages are checked part by part. A category index opens with one to three sentences, and every index page removes the on-this-page navigation.
- These were warnings and are now errors: an `html_meta.description` over 160 characters, a heading that addresses the reader, and a Related articles link to a toctree neighbour.
- Grammar articles hold the Common mistakes admonition in the last body section, not in Summary.
- The menu step fails a `:numbered:` toctree on any page, a root toctree that is not hidden, and a category index whose H1 or sidebar title is not the bare category name.

### Added: the glossary

The Terminology page is now the glossary, written in `{glossary}` directives, and Sphinx's `term` role links to it. A technical term is any word on `ol/authoring/glossary-terms.yml`, which ships empty, or on a language repository's own `glossary-terms.yml`. `ol validate` fails a listed term with no entry or with two, an entry that is not one sentence and one example, and an article whose first use of a listed term is not linked. A build fails on a `{term}` the glossary does not hold. A glossary entry's name in the language taught, written `Noun : Nomen`, shows in brackets after the term.

### Added: the render check

`ol check` opens every top-level and index page and a sample of articles at a 360 pixel viewport after the build, and fails if a page scrolls sideways. A table or code block scrolling inside its own box does not count. A language repository needs the new `render` extra, `open-language[render]`, and a Chrome on the machine or Playwright's Chromium. `--skip-build` skips this step too.

### Changed: the templates follow the standard

Every template now has the standard's shape, and there is a new `vocabulary-article.md`. The stylesheet wraps a long word in a heading or the next-page link, so these no longer push a page wider than a phone.

## [0.7.0] - 2026-11-01

### Added: a page's plain examples can be read and spoken

`ol-examples` blocks stay as they are written, and these additions let them be heard:

- A page can name who speaks its `ol-examples` blocks with `presenter:` in its front matter, a presenter's slug. `ol validate` fails a value that is not a slug.
- `ol.docs.page_examples.PageExamples.read(doctree)` reads a built page's blocks into `ol.blocks.Example` values, as the reader sees each sentence: roles and emphasis gone, typographic quotation marks in. A block holding anything but sentences and translations gives none.
- `ol.blocks.BlockReader.spoken(text)` gives a sentence from a page's Markdown with its roles and emphasis removed.

### Changed: a sentence given twice in an `ol-examples` block fails

This breaks a page that repeats a sentence within one block, compared as it is spoken. `ol validate` names the block and the sentence. Remove one of the two.

## [0.6.0] - 2026-11-01

### Added: the `stack` role shows a phrase with its translation beneath

`ol.docs.roles` now provides the `stack` role: ``{stack}`Guten Morgen | Good morning` ``. It works in a table cell, a list item and a paragraph, and renders in the html, dirhtml and json builders. Phrase tables can drop the translation column: `| German | English | Notes |` becomes `| Phrase | Notes |`, so they fit a phone. Inside a Markdown table write the separator as `\|`. A text without ` | ` shows unstacked and warns with the page and line. The shared stylesheet styles the new `ol-stack` classes. The concepts and writing templates and the authoring rules use two-column phrase tables.

## [0.5.0] - 2026-10-20

### Changed: every language repository has the same top-level pages

This breaks language repositories with other top-level pages, or without one of these. The menu check now holds the top level to exactly four pages, in this menu order (#21):

| File | H1 |
|---|---|
| `index.md` | Introduction |
| `how_to_use.md` | How to use |
| `terminology.md` | Terminology |
| `contributing.md` | Contributing |

- Each page exists, has exactly that H1, and has at least one paragraph of prose below it.
- Any other `.md` at the top level fails. `README.md` and `AGENTS.md` are still never read as pages.
- The root toctree lists `how_to_use`, `terminology` and `contributing` in that order, then the levels. Any other top-level entry fails, and so does a missing one.

`ol templates` adds one template for each page: `introduction.md`, `how-to-use.md`, `terminology.md` and `contributing.md`. A new language starts from them.

To bring a repository into line, give each of the four pages its H1 and a paragraph of prose, list them in order in `index.md`, and move the content of any other top-level page into one of them.

## [0.4.0] - 2026-10-20

### Changed: every language repository builds the same menu

This breaks language repositories whose menu differs. `ol validate` without files, and so `ol check`, now checks the site menu, the toctrees of the top-level `index.md` and of each level index (#18):

- The top-level `index.md` is the Introduction page: its H1 is "Introduction". Its toctree lists the other top-level pages (`how_to_use`, `terminology`, `contributing`, ...) in any order, then the levels. No top-level page comes after a level.
- The levels are `a1/index`, `a2/index`, `b1/index` and `b2/index`, in that order. There are no levels above B2, so a `c1/` or `c2/` directory fails. Every level directory has an `index.md` listed in the menu, and a level index marked `orphan: true` fails.
- Each level index lists only `concepts/index`, `grammar/index`, `writing/index` and `vocabulary/index`, in that order. A level may leave a category out. Any other category directory under a level, such as `topics/` or `situations/`, fails.
- The menu holds nothing else: no external links, no other entries and no second toctree in these pages. A toctree inside an HTML comment is not read.

A menu error is never covered by `.ol-validate-baseline`. Each error names the file and says what to move or remove.

To bring a repository into line, move the top-level pages above the levels in `index.md`, list every level from A1 to B2, remove `orphan: true` from the level indexes, and move the articles in any other category into one of the four.

### Removed: the topics and situations categories

The `topics` and `situations` templates and their rules in `specs.yml` are gone, since the menu has no place for them. An article under `topics/` or `situations/` now fails, and the error says to move it into one of the four categories. Vocabulary articles replace topics, and material about understanding a scenario goes in a concepts article. The level index template lists the four categories in menu order.

## [0.3.0] - 2026-10-20

### Changed: a language repository keeps its pages at the top level

This breaks language repositories that keep their pages under `docs/`. `ol` now reads a repository's pages from its top level, where `conf.py` sits next to `open-language.yml`, and no longer looks in `docs/`.

- `ol check` and `ol docs` build the top level into `_build/html`.
- A page's level, category and name come from its path below the top level (`a1/grammar/dativ.md`), and site-root links (`/a1/grammar/dativ.md`) resolve from there.
- Paths in `.ol-validate-baseline` and in reports have no `docs/` prefix.
- `_build`, `.venv`, `.github`, `README.md` and `AGENTS.md` at the top level are never read as pages.

To move a repository, move everything under `docs/` to the top level, change `Path(__file__).parent.parent` to `Path(__file__).parent` in `conf.py`, add `_build`, `.venv`, `.github`, `README.md` and `AGENTS.md` to its `exclude_patterns`, and remove `docs/` from each line of `.ol-validate-baseline`.

`Language.docs_root` is the working directory unless `OPEN_LANGUAGE_DOCS` is set. `BlockCollection.from_docs` takes `exclude`, names directly under the root that are not pages. `ol validate` without `--workspace` takes the nearest folder above a file that holds `open-language.yml` as its workspace.

## [0.2.0] - 2026-10-19

### Changed: a track's address always gives its name

This breaks language repositories that write `:track: level/category`. A `:track:` value now has to be `level/category/name`. With only a level and a category, the block is refused as `bad_address`. Before, the page's file name was taken as the track's name, so renaming or moving a page, or adding a second block to it, quietly changed which track a block named.

For each block whose `:track:` gives two parts, add the page's file name as the third. `:track: a1/concepts` on `docs/a1/concepts/greetings.md` becomes `:track: a1/concepts/greetings`. The block then names the track it named before.

The article templates write all three parts. `BlockReader.address()` no longer takes the page.

## [0.1.0] - 2026-10-19

The first release.

### Changed: the audio-examples block takes the form the Open Language app reads

This breaks existing language repositories. For each `audio-examples` block:

- Replace `:album:` and `:name:` with `:track: level/category/name`. With only `:track: level/category`, the track's name is the page's file name.
- Remove `:voice:`, `:spotify:` and `:youtube-music:`. Each is now refused as `unknown_option`.
- Where a second page shows a track another page writes, give that block `:track:` and `:duplicate:` and nothing else, apart from `:tags:` if wanted.
- Give each sentence of a block once. Two sentences that differ only in spacing or emphasis are refused as `sentence_twice`.

`ol validate` refuses a block with a code for each problem (`unknown_option`, `bad_address`, `missing_examples`, `duplicate_writes`, `sentence_twice`, `written_twice`, `orphan_duplicate`), and reads every page of `docs/` for the last two.

### Added

- Contributor documentation: glossary, constitution and standards.
- Pre-commit hooks and Dependabot configuration.
- Authoring rules page (`docs/reference/authoring-rules.md`) for the rules a script cannot check and the rubric does not ask about.
- Review rubric items for category fit, Prerequisites, Related articles, the placement of "Hear it in practice", the lead paragraph, hedging, which language goes where, and layout.
- `ol validate` checks the rules below. Content that breaks one fails the check, so an author has to change it (or record it in `.ol-validate-baseline`):
  - No TODO or FIXME note in an article or index. Delete it.
  - No CEFR level and no category prefix ("Grammar:") in an article's title. Remove it from the H1.
  - No "References", "Additional reading", "Further reading" or "See also" section in an article. Move the links under Related articles, and external reading to the level index.
  - No hand-numbered headings ("## 1. Form"). Drop the number.
  - At most three links in a Prerequisites admonition. Keep the ones the article cannot be read without.
  - "Hear it in practice" is never collapsed in a dropdown. Remove the dropdown.
  - A vocabulary pack's word table has 10 to 20 words. Split or fill the pack.
  - A writing or vocabulary file name ends in a running number (`email-formal-1`, `at-the-beach-1`). Rename an unpublished article; record a published one in the baseline, because published file names never change.
- `ol validate` warns when Related articles links the article just before or after this one in its category index's toctree. Remove the link: the page footer already has it. This is a warning for now and becomes an error in a later version.
- `ol.blocks`, the public reader of the block and its refusals, which the app uses too.
- Sample blocks in `ol/authoring/samples/`, each marked accepted or refused, loaded with `ol.blocks.load_samples()`.
- A tags option, `:tags:`.

### Removed

- `ol audit`, and the audit step of `ol check`. Blocks no longer name an album, so there is nothing to check an `album.yml` against. The `album.yml` template and the album checks in `ol validate` are gone with it.
- `ol.docs_source`. Read blocks with `ol.blocks` instead.
- Streaming links on the rendered block.
