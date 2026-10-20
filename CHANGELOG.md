# Changelog

## [Unreleased]

### Added: a language repository may keep its pages at the top level

A language repository no longer needs a `docs/` folder. When `docs/conf.py` exists, the pages are read from `docs/` as before. Otherwise they are read from the top of the repository, where `conf.py` sits next to `open-language.yml`. Nothing changes for a repository that keeps its pages under `docs/`.

In a repository without `docs/`:

- `ol check` and `ol docs` build the top level into `_build/html`.
- A page's level, category and name come from its path below the top level (`a1/grammar/dativ.md`), and site-root links (`/a1/grammar/dativ.md`) resolve from there.
- Paths in `.ol-validate-baseline` and in reports have no `docs/` prefix.
- `_build`, `.venv`, `.github`, `README.md` and `AGENTS.md` at the top level are never read as pages.

To move a repository, move everything under `docs/` to the top level, change `Path(__file__).parent.parent` to `Path(__file__).parent` in `conf.py`, add `_build`, `.venv`, `.github`, `README.md` and `AGENTS.md` to its `exclude_patterns`, and remove `docs/` from each line of `.ol-validate-baseline`.

`Language.docs_root` follows the same rule. `BlockCollection.from_docs` takes `exclude`, names directly under the root that are not pages.

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
