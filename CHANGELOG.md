# Changelog

## [Unreleased]

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
