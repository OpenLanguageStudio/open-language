# Changelog

## [Unreleased]

### Changed

- A track may close an H3 subsection, not only an H2 section (OL-W9). A grammar page that splits one H2 into parallel forms, such as one H3 per modal verb, can end each subsection with its own track. A track in the middle of a subsection still fails.

## [0.19.0] - 2026-11-27

### Changed: checks that can fail content that passed 0.18.0 (breaking)

- A keyword in `html_meta.keywords` that appears only in a table cell, and nowhere else on the page, fails (OL-W29). Say it in a sentence.
- A line of prose that discloses how the audio or the cast was made, such as "AI voices" or "fictional presenters", fails (OL-W31). The app says so.
- When `open-language.yml` sets `register_tabs:`, as in `register_tabs: [Formal (Sie), Informal (du)]`, a tab set whose labels name a register uses exactly those labels in that order (OL-W8). The finding cites the language's own rule that narrows OL-W8, such as DE-W1, when it has one.

### Added

- Every finding that enforces a writing rule starts with the rule's ID, as in `OL-W26: em dash on line 12`. Tagged so far: OL-W3, OL-W7, OL-W8, OL-W9, OL-W10, OL-W11, OL-W13, OL-W17, OL-W23, OL-W24, OL-W26, OL-W27, OL-W29, OL-W31 and OL-W32. The IDs are read from `docs/reference/writing-rules.md`, which now ships inside the package, and from the language repository's `standards/writing-<code>.md`. A check that cites an ID neither file defines raises, and a test fails.
- A page may bend a writing rule with `<!-- OL-W8 bent: reason -->`. The rule's findings on that page are dropped, bending a global rule also bends the language rules that narrow it, and `ol validate` and `ol check` list every bend at the end of their output. A bend of an undefined rule, or with no reason, fails. The build removes bend comments, and any other HTML comment still fails.
- `ol review-tier --pr N` works out the content review a pull request into a language repository needs: trivial, small or full, from its diff and its author's GitHub user id. With `--post` it sets the commit status `content-review` on the head commit, success for trivial and pending otherwise, and writes a comment saying in words what is needed.
- `ol review-status --pr N --verdict pass|fail --tier small|full --report FILE --model M` posts a review's verdict as the `content-review` status on the head commit and the report as a comment. It refuses a review below the tier needed, a stale `--sha`, and a full review by the writer's model.
- `docs/reference/content-review.md` describes the tiers, their limits and the workflow a language repository runs.

### Changed

- The messages for em dashes and hand-written navigation links use a colon where they had a spaced hyphen.

## [0.18.0] - 2026-11-26

### Changed: three rules that can fail content that passed 0.17.0 (breaking)

- A phrase table whose Notes cells are all empty fails. Phrases with nothing to note go in an `ol-examples` block, where they also play. A cell with only a dash counts as empty. The word table of a vocabulary article is exempt.
- A heading whose text is a track's `:title:` or `:title-en:` fails. The audio block draws its own title, and a track's title stays out of the sidebar and the page contents.
- In a how-to article, `## Hear it in practice` takes no H3s. The rule that an H3 there names its track is removed from grammar and how-to: a track now closes the section it practises (below). Situations keep their H3s for two versions of one scene.

### Added

- `target-title:` in an article's front matter holds the goal or topic in the language taught, one line of text. The build draws it straight under the H1 as `<p class="ol-target-title" lang="…">`, and in the PDF as a subtitle. It is not a heading, so no contents list names it. A how-to article without it is warned about. Any article may have one.
- The `culture-note` directive, `:::{culture-note}`, draws a notice titled "Culture note", of class `ol-culture-note`, in a violet no other notice uses, on the site and in the PDF. It may stand anywhere in the body of a how-to, grammar or writing article. It holds 80 words or fewer, an article has at most 3, it takes no title or options, it holds no other notice, and it does not count toward the free notices. A `## Culture note` heading is warned about, pointing to the directive.
- A track may close any body section of a grammar, how-to or vocabulary article: one or more audio blocks as the section's last blocks. `## Hear it in practice` is required only when no body section ends in a track. A track in the middle of a section fails.
- Wanted pages. A link in the text to a page that does not exist yet fails nothing: the build draws its text as `<span class="ol-wanted">` and logs it, and `ol validate` reports it as information. The source never changes: once the page is written, the next build draws a live link with no edit to the linking page. A link names a page when its path ends in `.md`, or has no file suffix and holds a `/`. The new `ol wanted` command lists each wanted page with the pages that link to it, `ol wanted --format json` writes the same list as JSON, and `ol check` prints it in its own section and still passes. `related:` stays strict: an entry that names no page still stops the build.
- A missing page close to a page that exists is a broken link, not a wanted page: an error in `ol validate` and a build warning, "broken link to X, did you mean Y?". Close means a page in the same directory whose file name is one letter away (two for a name of six letters or more), or a page of the same file name in another directory, `index` aside. `ol wanted` leaves these out.
- Every link has its own text. A link with empty text, `[](…)`, to a page not written yet is an error in `ol validate` and a build warning. One to a page that exists is warned about in `ol validate`.
- The first use of a listed term is also linked when its sentence links to an article of the Coursebook, the article that covers the term. The text of a link to an article is itself a linked use. The docs put an article link before the glossary.
- A common mistake may end with a link to the article that explains it, "(learn more in [Text](…))", which may name a wanted page.
- `ol/docs/_static/page-parts.css` styles the target-language title, the culture note and wanted pages, and the site stylesheet imports it.

### Changed

- A Prerequisites or hand-written Related articles link with its own text is no longer an error: links in those lists follow the same rule as every other link. The templates and docs write every link with its own text.
- The explanation paragraph is optional in a how-to article. When present it states the one idea that organises the page and never previews the sections below. Grammar, writing and vocabulary still need it.
- The shared term list, `ol/authoring/glossary-terms.yml`, holds grammar jargon only. Removed: adjective, future tense, noun, past tense, plural, present tense, question word, singular, tense, verb and word order. A `{term}` link to one of them still resolves where the glossary has an entry.
- The how-to template carries `target-title:`, an optional second paragraph, a culture note and a track at the end of a body section, and marks Hear it in practice as needed only when no section ends in a track. The page standard, the components page, the authoring rules, `specs.yml` and the review rubric describe the new frame. The page standard and the authoring rules describe wanted pages, and that reviewers triage each one before merge: accept it, and the page is queued, or drop the link.

## [0.17.0] - 2026-11-25

### Changed: Related articles are written in front matter (breaking for mixed pages)

A page that has both `related:` and a hand-written `## Related articles` section, or `related:` and a `situations` or `how-to-links` box, now fails `ol validate`, and the build warns about the first. The two boxes are retired: where a page has Related articles drawn from the front matter, a box draws nothing. A page that keeps only its hand-written section, or only a box, passes with a warning to move to `related:`. See ADR 3.

- A how-to article that a situation names no longer carries the box or `## When to use it`: the situations are listed under Related articles. A situation no longer needs `:::{how-to-links}`. A how-to article no situation names keeps `## When to use it`.
- The article templates carry `related:`, `skills:` and `tags:` and no Related articles section or box.

### Added

- `related:` in an article's front matter lists page paths without `.md`, relative to the page's folder or from the root with a leading `/`. The build draws them as the last section, Related articles, with a group for each kind of page in the order how to, situations, grammar, writing, vocabulary, and "More" for the rest. A page of another level is followed by its level badge. An entry that names no page, ends in `.md` or is not a string stops the build. `ol validate` checks each entry exists, is not the page itself, and follows the rules for Related articles: no neighbour in the toctree of a flat category, no article of the same subcategory.
- The links the Situations and How to boxes drew are drawn in the same section: a how-to article links the situations that name it, and a situation links the how-to articles it names.
- `skills:` in a level page's front matter lists the level's skills, each with an `id`, a `kind` of `know` or `can`, and a `text`, drawn by the new `:::{skills} know` and `:::{skills} can` directives under the page's two sections. The limits on bullets apply to the texts. A level page with hand-written bullets passes with a warning to move them into `skills:`.
- `skills:` in an article's front matter names one or two skill ids of its level page. `ol validate` reports an unknown id and a list of more than two, and warns about an article with none.
- `track-tags.yml` at a repository's root lists the allowed tags under `grammar:` and `themes:`. When it exists, every block that writes a track needs `:tags:` from the list, and an article's `tags:` front matter must be a list from it. An article with no `tags:` is warned about. A `:duplicate:` block needs no tags.

## [0.16.0] - 2026-11-23

### Added: Situations, a fifth category

A situation article is one everyday scene, heard: a conversation at a party, at the checkout, at a hotel desk. It shows a how-to goal reached and teaches nothing itself (ADR 2). A level lists its categories in the order how-to, situations, grammar, writing, vocabulary, and the sidebar names the new one Situations.

- `situations-article.md` is its template, and `specs.yml` holds its rules under `types.situations`. A situation has a lead that sets the scene, the `:::{how-to-links}` box, `## Hear it in practice` with one `dialogue`, `correspondence` or `passage` block (or two, each under an H3, for two versions of one scene), `## What to listen for` with two to four bullets, and optional Related articles. It has no tables, examples boxes or titled notices. A dialogue has 6 to 20 lines.
- A situation names the one to three how-to articles it puts to use in its front matter, under `how-to:`, at its level or below. `ol validate` checks each one exists.
- A how-to article that a situation names carries `:::{situations}` after its explanation in place of `## When to use it`. A how-to article no situation names keeps the section, so content that passed 0.15.0 still passes.
- The Introduction shows a card for each category the first level has, rather than exactly four.
- The review rubric gains `situation-at-level`.

- The directives `situations` and `how-to-links` draw the two boxes from the situations' front matter, each as a titled list of page links with the level badge after a page of another level. The Situations box lists situations by level, then in the order of the level's `situations/index`. A how-to article is written again when the situations naming it change, so a new situation shows on the pages it names without a fresh build. A box that would link nothing warns. `ol.docs.audio_examples` loads them, so a language repository's `conf.py` needs no change.
- `link-boxes.css` styles both boxes in the violet accent, in light and dark mode. The shared stylesheet imports it. An app that draws the pages in its own theme links it next to `marks.css`.

## [0.15.0] - 2026-11-21

### Changed: the Introduction has no button (breaking)

The "Start with A1" button under the Introduction's lead is withdrawn. A page has no buttons: `button-ref` is no longer a component, so `ol validate` reports it on any page, the Introduction included. Before a language repository pins this version, delete the `button-ref` block from its `index.md`. The Introduction's template, the page standard and the components page follow.

## [0.14.0] - 2026-11-17

### Changed: every block names its presenters, and has a mode (breaking)

Content that passed 0.13.0 fails this version until it is moved. Before a language repository pins it:

- Give every `audio-examples` block that writes its track `:presenters:`, the slug of the presenter who says it, or several slugs separated by commas. A duplicate block takes none.
- Replace `:multiline:` with `:mode: passage`. `:multiline:` is withdrawn and is now an unknown option.
- Rewrite every `:::{div} ol-examples` box as `:::{ol-examples}` with `:presenters: <slug>` on the line under it. sphinx-design's `div` refuses options it does not know, so the box is now a directive of its own, `ol-examples`, which `ol.docs.audio_examples` loads. It is still drawn as a `div` of class `ol-examples`.
- Remove `presenter:` from front matter. The field and its check are withdrawn: a page never names a presenter.

A block's `:mode:` says how its examples are read and spoken: `examples` (the default), `pairs`, `dialogue`, `passage` or `correspondence`. The README describes each one's body and how many presenters it takes. The reader gives the app `Block.mode`, `Block.presenters` in the order listed, and for each example `Example.presenter` and `Example.group`. `Block.multiline` is gone. `PageExamples.read` gives each example its box's presenter. The new refusals are `unknown_mode`, `missing_presenters`, `bad_presenters`, `bad_pair`, `presenter_not_listed` and `presenter_silent`. `sentence_twice` now applies to `examples` blocks only. `unknown_presenter` is defined for the app to report, and listed in `Refusal.APP_ONLY`. The template, the samples, the README, `CONTEXT.md` and the authoring rules follow, and ADR 1 records the design.

## [0.13.0] - 2026-11-15

### Added: the level role, drawn in the level's colour

``{level}`B1` `` draws a level as a small badge in that level's colour, the colour of the level's album covers: A1 #eeb849 and B1 #79b3a8 with dark text, A2 #a4563a and B2 #496695 with light text. The colours are defined once, in `ol/levels.py` (`LEVEL_COLOURS`), and the role writes them on the badge, so the badge has its colour wherever the HTML is drawn. A level other than A1 to B2 is a build warning. `ol.authoring.menu.LEVELS` now comes from `ol.levels`.

### Added: `marks.css`, the role styles on their own

The grammar marks and the level badge moved out of `stylesheet.css` into `ol/docs/_static/marks.css`, which `stylesheet.css` imports. A site that draws a coursebook in its own theme links `marks.css` alone and gets the marks without the Sphinx theme's styles. Its dark colours apply under any `html[data-theme]` ending in `dark`. The unused `.ol-level-a1` to `.ol-level-b2` classes and their `--level-*` variables are gone.

### Added: the components a page is built from

`ol validate` now holds every page to [the components](docs/reference/components.md) and the Components section of the page standard:

- Only the listed directives and roles. The roles are `stack`, `term`, `level`, `bdg-light` and the language repository's marking roles, read from `custom_roles` in its `conf.py`. How to use and Contributing may also use the interface roles, such as `kbd`, and are now checked too.
- Card grids only on index pages and the Introduction, the button only on the Introduction, the glossary only on Terminology, tabs only in grammar and how-to articles, a block quote only in writing articles, and no toctree in an article.
- No footnotes, struck-through text, highlighted spans, abbreviations or paragraphs of bold text alone, such as `**Examples:**`.
- Notices: `note`, `tip`, `important` and `warning`, and an `admonition` only as Prerequisites (`note`), Common mistakes (`caution`) or Key points (`note`). An article holds at most 3 free notices, 1 per H2 section and 1 `important`. A free notice is 60 words or fewer, and no notice holds another.
- No collapsible, an element that opens and closes on a click: no `dropdown` directive, no notice with `:class: dropdown` and no `<details>`, anywhere on a page. This replaces the check that only Hear it in practice was never collapsed.
- A level badge follows a link to a page of another level and names that level. A register badge holds `informal`, `formal` or `colloquial`, in a Notes cell.
- A tab set: one per article, 2 or 3 tabs with labels of 3 words or fewer, every tab holding a phrase table or every tab an example block, and nothing else.
- A card grid is `::::{grid} 1 1 2 2` with `:gutter: 3`, and each card links a page with `:link-type: doc`, takes that page's title, has no header, footer or picture, and holds one sentence of 15 words or fewer.
- Related articles and Prerequisites write each link with empty text, `- [](/a1/grammar/cases/akkusativ.md)`, followed by ``{level}`A1` `` when it goes to another level.

### Changed: the Introduction, level pages and category indexes show cards

- The Introduction has a primary button under its lead, "Start with A1", linking the first level's page. Its Levels and Categories sections are card grids: one card per level, its sentence 20 words or fewer, and four category cards, 25 words or fewer.
- A level page hides its toctree, which `ol validate`'s menu check now requires, and adds `## Categories` before Additional reading: a card per category, linking the toctree's pages in its order.
- A category index whose toctree lists subcategories hides it and shows a card per subcategory in the same order. A flat category index and a subcategory index show their toctree and have no cards.

The templates from `ol templates` show the new shapes.

This is a breaking change. Pages written to the old shapes, with named Related articles links, collapsibles or an unlisted directive or role, now fail `ol validate`. Run `ol validate --write-baseline` once on adopting this version to cover them until they are rewritten. The menu errors for a level toctree that is not hidden are not covered by the baseline.

## [0.12.0] - 2026-11-09

### Changed: the Concepts category is now How to

The category directory `concepts/` is now `how-to/`, and its index's H1 and sidebar name is "How to". `ol validate`, `ol templates` and the menu checks use the new name everywhere: a level index lists `how-to/index` first, and the Introduction's Categories list starts with `[How to](a1/how-to/index.md)`. The article template is now `how-to-article.md`.

A how-to title finishes the phrase "How to ...", so it opens on a verb in its base form, such as "Order food and drink" or "Introduce yourself". `ol validate` reports a title whose first word ends in -ing, such as "Ordering food and drink", or is a word that cannot be a verb, such as "The" or "Your". The five-word limit still applies.

How-to articles are read in any order. The category is no longer marked as ordered, and the templates and the page standard no longer ask its index to describe a suggested sequence.

This is a breaking change. A repository with a `concepts/` directory now fails `ol validate` until the directory is renamed `how-to/`, its index's H1 is "How to", its tracks are renamed to match and the level indexes and Introduction link the new paths.

### Added: the licence notice in every page's footer

Every page of a coursebook built with the shared layout now ends with: "Text © Open Language, licensed under CC BY-SA 4.0. Audio recordings are not covered by this licence: all rights reserved, no use for AI training." CC BY-SA 4.0 links to the licence. A language repository gets it by keeping `ol/docs/_templates` on its `templates_path`, as the language repositories already do. A JSON build carries only each page's body, so a site serving one draws its own notice.

### Added: the shared term list

`ol/authoring/glossary-terms.yml` now lists the grammar terms a coursebook in any language needs, such as `noun`, `verb` and `subject`. Every listed term must have an entry on a language repository's Terminology page, and the first use of each in an article's prose must link to it. Language-specific terms stay on the repository's own `glossary-terms.yml`.

This is a breaking change. A repository whose Terminology page lacks those entries, or whose article uses a listed term with no link, now fails `ol validate`. Add the entries and links, or on adopting this version run `ol validate --write-baseline` once, and the baseline covers those pages until they are fixed.

### Changed: no table has a translation column

`ol validate` now reports an error on a table of any category when a header cell holds `English`, `Translation` or `Meaning` as a whole word, in any position, such as `Core meaning`. Before, this fired only when another header named the language taught or a word such as `Word` or `Phrase`, so tables such as `Formal | Informal | English` passed. The translation goes under its phrase with the `stack` role, and anything else goes in a Notes column.

A header cell after the first may no longer be empty either, so a translation cannot sit in an unnamed column, as in `Singular | | Plural | |`. The first cell of a table of forms in grammar may still be empty.

A language repository adds the words its own headers use under `translation_headers` in `open-language.yml`, for example `translation_headers: [Bedeutung]`.

This is a breaking change. A page with such a column now fails `ol validate` until the column is gone, or until the page is in the baseline.

## [0.11.0] - 2026-11-02

### Changed: articles in a subcategory do not link each other

`ol validate` now reports an error when Related articles links another article of the same subcategory, a directory below a category such as `a1/grammar/articles/`. The directory already says the two belong together, and the subcategory's index links them all. Remove the link, and leave the section out if nothing remains. An article may still link articles outside its subcategory, and its own subcategory's index. In a subcategory this rule covers the toctree neighbour check, which now applies to flat category directories only, such as `b1/grammar/` or `a1/concepts/`. Pages that link this way now fail until the link is removed.

## [0.10.0] - 2026-11-01

### Changed: a term linked in the lead counts for the explanation

A term linked in the lead paragraph no longer has to be linked again in the explanation paragraph, so the same term is not linked twice two paragraphs apart. A term whose first use is in the explanation is still linked there. The "first use of the term" error now covers this case, and the separate "the explanation paragraph uses the term" error is gone.

### Added: a heading for each track under Hear it in practice

In grammar and concepts, a `## Hear it in practice` section with more than one audio block may put each block under its own H3 naming the track, so on-this-page reaches it. `ol validate` accepts these H3s when the section has several blocks, every block has an H3 and each H3 holds one block. They count towards the limit of 6 H3. The review rubric gains `track-heading`, which asks whether each H3 names its track. Vocabulary and writing are unchanged.

## [0.9.0] - 2026-11-01

### Added: paragraphs in a `:multiline:` block

A blank line inside a `:multiline:` example is now a paragraph break, in the text and in its translation, and it is kept on the page and in `Example.sentence` and `Example.translation` as one empty line. A blank line after the translation still ends the example when the next line is text, so every block that was valid before reads exactly as it did. A blank line between a text and its translation is allowed and means nothing. Blocks without `:multiline:` are unchanged.

## [0.8.2] - 2026-11-01

### Changed: the render check opens every built page

`ol check` now opens every page of the built site at a 360 pixel viewport, not a sample of articles, including the search and index pages Sphinx generates. A table or code block scrolling inside its own box still does not count. The check adds about a minute to a site of 230 pages. The `render.articles_per_type` setting in `specs.yml` is gone, and `ol.authoring.render.built_pages` replaces `sample_pages`.

## [0.8.1] - 2026-11-01

### Fixed: a link's text is not a use of a term

`ol validate` counted a listed term in a link's text as its first use, and asked for the `term` role there, where a link cannot hold one. The usual case is a Related articles entry that names another page, such as `[A1 > Grammar > The verb sein](/a1/grammar/sein.md)`. The text of a link is now exempt, and the page standard says so.

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
