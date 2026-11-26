# Page standard

The shape of every page in a language repository, and how each rule is checked. It applies to every language. A page that follows it looks the same in German, French and Spanish, which is what makes the coursebooks one product.

Read it with [authoring rules](authoring-rules.md), which holds the rules about wording, [components](components.md), which shows how to write each part of a page, and the template for the page's type open (`ol templates`).

## Who the pages are for

The reader is an adult who has never studied grammar. They arrive from a web search for one German problem, read one page, and leave or jump elsewhere. So every page:

- stands on its own, without needing the page before it;
- opens with what it covers, in the words a learner would search with;
- uses plain words first, and a technical term only with a link to the glossary;
- puts the reader's next step, listening to the examples, at the end of the page.

## How a rule is checked

Every rule below carries a tag. A rule with no script behind it is not a rule.

| Tag | Check | When it runs |
|---|---|---|
| V | `ol validate`: measures the article's Markdown | `ol check`, CI, pre-commit |
| M | `ol check` menu step: measures toctrees and top-level pages | `ol check`, CI |
| B | The build: `ol docs` with warnings as errors | `ol check`, CI |
| R | The review rubric: a reader answers yes or no | Every pull request |

The numeric limits live in `ol/authoring/specs.yml`. This page names the rule and gives the current limit in brackets.

## The frame every article shares

An article is these parts, in this order. The five category sections below fill in the middle.

| # | Part | Rule | Check |
|---|---|---|---|
| 1 | Front matter | `html_meta.description` of 160 characters or fewer, written as the search snippet. `keywords` lists the phrasings a learner would type, and each is said in a sentence of the page, not only in a table cell (OL-W29). | V |
| 2 | Title (H1) | One per page. English, sentence case, five words or fewer, no level, no category, no number. `target-title:` in the front matter names the goal in the language taught, and the build draws it straight under the H1 as a subtitle (see Front matter keys). | V (count, prefix), R (case) |
| 3 | Lead paragraph | The first paragraph under the title. One or two sentences (20 to 50 words). Says what the page covers in plain words, and uses the main learner phrasing at least once. | V |
| 4 | Explanation paragraph | The second paragraph. States the one idea of the page in plain language (40 to 120 words). It never previews the sections below. Every technical term in it is linked, here or in the lead, so a term is not linked twice two paragraphs apart. Optional in how-to. | V |
| 5 | Prerequisites | Optional admonition after the two opening paragraphs, before the first H2. At most 3 links, true dependencies only, each a list item whose link has its own text, `- [The accusative](/a1/grammar/cases/akkusativ.md)`. | V |
| 6 | Body sections | The category's own sections (see below). In grammar, how-to and vocabulary a body section may end in the track that practises it. | V |
| 7 | Hear it in practice | `## Hear it in practice` with the audio block, after the body and before the summary. Required only when no body section ends in a track. | V |
| 8 | Summary | `## Summary`, as the template for the category shows. | V |
| 9 | Related articles | Drawn by the build from `related:` in the front matter (see Front matter keys), as the last section of the page. The page has no `## Related articles` section of its own. | V, B |

Parts 3 and 4 together stay at 180 words or fewer, so the first screen on a phone shows what the page is and why it matters, then the first heading.

### Front matter keys

Besides `html_meta`, an article's front matter holds:

- `related:` lists the pages a reader may want next, as page paths without `.md`, relative to the page's folder or from the root with a leading `/`: `related: [/a1/grammar/verbs/sein-und-haben, choose-between-du-and-sie]`. Each entry names a page that exists and is not the page itself. [V] An entry that names no page, ends in `.md` or is not a string stops the build. [B]
- `target-title:` is the goal or topic in the language taught, one line of text: `target-title: Sich vorstellen`. The build draws it straight under the H1, as `<p class="ol-target-title" lang="de">`. It is a subtitle, not a heading, so no contents list names it. Every how-to article has one, and a how-to article without it is warned about. Any other article may have one. A value that is not one line of text fails. [V, B] No sentence of the page names the goal in the language taught instead, such as "German calls it *sich vorstellen*". [R]
- `tags:` lists the tags of the article's tracks, each from the repository's `track-tags.yml` (see Tags).
- `skills:` names one or two skills of the level page, by id: `skills: [a1-meet-people]`. Each id is a skill listed in `skills:` on the article's level page, `<level>/index.md`. A list of more than two, or an id the level page does not list, fails. An article with no `skills:` is warned about until its level is migrated. [V]

### Related articles

The build draws the page's `related:` entries as the last section, `## Related articles`, one group for each kind of page. The groups follow the category order, how to, situations, grammar, writing and vocabulary, and a page that belongs to no category stands last under "More". Within a group the links keep the order of `related:`, and a page listed twice is linked once. Each link shows the target's title, and a page of another level is followed by that level as a level badge.

- Only links the reader would not reach by the next-page link belong in `related:`. In a subcategory, a directory below a category such as `a1/grammar/articles/`, an article relates to no other article of that subcategory: the directory already relates them and the subcategory index links them all. Links outside the subcategory are fine. In a flat category directory, such as `b1/grammar/` or `a1/how-to/`, sharing the directory says nothing about two topics being related, so only the toctree neighbours are left out. [V]
- The links the Situations and How to boxes drew are folded into the section: a how-to article links every situation whose `how-to:` front matter names it, and a situation links the how-to articles its own `how-to:` names. Both boxes are retired. A page with `related:` that still holds a box fails, and a page without `related:` is warned about. [V]
- The section is drawn when the page has no hand-written `## Related articles` and at least one link. A page with both `related:` and a hand-written section fails and the build warns. A page with only the hand-written section is warned about until its links move into `related:`. [V, B]

### Links in the text

A link in a sentence, at the point where the reader needs it, is the main way pages connect. `related:` stays short: a few close neighbours.

- Every link has its own text: `[the dative](/a1/grammar/cases/dativ.md)`. A link with empty text, `[](…)`, to a page that exists is warned about. To a page that does not exist it is an error. [V, B]
- A link may name a page that does not exist yet, with the path the page should have. It is a wanted page. The source never changes: the link is an ordinary link, the build draws its text as plain text in `<span class="ol-wanted">` until the page exists, and the first build after the page is written draws a live link, with no edit to the linking page. It fails nothing. `ol validate` reports it as information, `ol wanted` lists every wanted page with the pages that link to it (`--format json` for a machine), and `ol check` prints the same list in its own section. [V, B]
- A missing page close to one that exists is a broken link, not a wanted page, and is an error in `ol validate` and the build: "broken link, did you mean …?". Close means a page in the same directory whose file name is one letter away (two for a name of six letters or more), or a page of the same file name in another directory. [V, B]
- A link names a page when its path ends in `.md`, or has no file suffix and holds a `/`. [V]
- A link to a wanted page is for depth only: the page teaches its goal fully without it. Reviewers triage every wanted link before merge: they accept it, and the page is queued for writing, or the writer drops the link. Every wanted link left on the main branch is a page that has been commissioned. [R]
- `related:` is not text: an entry there that names no page still stops the build. [B]

### Tags

A language repository may hold `track-tags.yml` at its root, with two lists of strings, `grammar:` and `themes:`. The allowed tags are the two lists together. When the file exists: [V]

- A block that writes a track has a `:tags:` option. A `:duplicate:` block writes no track and needs none.
- Every tag in `:tags:` is in the list, written exactly as listed.
- An article's `tags:` front matter is a list of strings from the list. An article with no `tags:` is warned about until its level is migrated.
- The file itself is two lists of strings.

Without the file, tags are not checked.

### Headings

- Only H1, H2 and H3 exist. There is no H4. [V]
- An H3 appears only where the category's template names one: under `## Example: ...` in writing, to split one H2 into parallel forms in grammar, for group names under `## Key phrases` in how-to, and for the versions of a scene under `## Hear it in practice` in situations. An article has at most 6 H3, these included. [V]
- No heading repeats a track's title, its `:title:` or its `:title-en:`. The audio block draws its own title, and a track's title never appears in the sidebar. [V]
- An article has at most 7 H2. A page that needs more is two pages. [V]
- A heading is 8 words or fewer, has no number and no closing punctuation, and does not address the reader. German words in a heading are in italics. [V]
- A heading never repeats the heading of its parent. [V]

### Tables

A table is read on a phone, where width is scarce and height is not.

- A word or phrase table has two columns: the phrase with its translation stacked beneath it, and Notes. No table has a separate translation column. [V: error on any table, of any category, with a header cell holding English, Translation or Meaning as a whole word, or a word the language repository adds under `translation_headers` in `open-language.yml`]
- A table has at most 3 columns. A table of forms, such as a declension, may have up to 5, and only in grammar. [V]
- A table has a header row. Every header cell has a name, except the first cell of a table of forms. [V]
- A phrase table earns its place through its Notes column. A table whose Notes cells are all empty fails: phrases with nothing to note go in an `ol-examples` block, where they also play. The word table of a vocabulary article is exempt. [V]
- At a 360 pixel viewport no page scrolls sideways. [B: render check in CI, see "Proof" below]

The stacked cell is written with the `stack` role: ``{stack}`Guten Morgen | Good morning` ``. Inside a pipe table the separator is written `\|`. Old tables with an English column stay in the baseline until they are migrated.

### Plain language and the glossary

- A sentence is 25 words or fewer, and a paragraph 5 sentences or fewer. Prose averages 18 words a sentence or fewer. [V: error over the limits, warning over the average]
- Prose is active voice. [R]
- A technical term is any word on the term list: the engine's shared list (`ol/authoring/glossary-terms.yml`) plus the language repository's own. The list holds grammar jargon and terms in the language taught that a general reader would not know, such as *dative* or *separable verb*. Everyday words, such as "noun", "plural" or "question word", are not on it. Every term on the list has exactly one entry in the glossary. [V: a listed term with no entry is an error] [B: an unresolved `{term}` fails the build]
- The first use of a listed term in each article's prose is linked. A link to the article that covers it, in the same sentence, comes first. Otherwise the term is written as `{term}` and links to its glossary entry. The text of a link to an article is itself a linked use. Headings, example sentences, tables of forms and the glossary itself are exempt. [V: a first use with neither is an error] [R: an article link where one exists]
- A term's meaning is also given in the sentence where it is first used, in plain words, so a reader who does not click still follows. [R]
- A glossary entry has the term in bold, its name in the language taught in brackets when the language repository needs it, one sentence of 30 words or fewer, and one example. [V]
- A word that is not on the list may still be written as `{term}` when the glossary has an entry for it. [B]
- No page sends the reader off the site to learn what a term means. [R]

Terms that are only a German word being taught, such as *der* or *Konjunktiv II* as the topic of its own article, are the subject of the page and are exempt on that page.

## Components

A page is built from the components in [components](components.md), which shows how to write each one. The kit is small on purpose: a reader who has seen one page knows what every box, table and card on the next one means.

- A page uses no directive and no role that the components page does not list. [V: an unlisted directive or role is an error]
- A component that the components page limits to some pages appears on those pages only: card grids on index pages and the Introduction, the block quote in writing, forms tables in grammar, interface roles on How to use and Contributing. [V]
- Inline, a page has no footnotes, no strikethrough, no highlighted span and no abbreviation role. [V]
- A paragraph is never made of bold text alone, such as `**Examples:**`. A label that is needed is an H3, where the category's template names one; otherwise the block speaks for itself. [V]

### Notices

A notice is read as a break from the text. The fewer there are, the more each one is read.

- The free notices are `note`, `tip`, `important` and `warning`, each with its one meaning: `note` explains, `tip` helps a form stick, `important` is the rule a learner must not miss, `warning` names a trap. [V: kind] [R: meaning]
- A titled notice is one of three, each with its class: Prerequisites (`note`), Common mistakes (`caution`) and Key points (`note`). No other title. [V]
- A common mistake that another article explains ends with a link to it: "(learn more in [W-questions](/a1/grammar/questions/w-questions.md))". The link may name a wanted page. [R]
- An article has at most 3 free notices, at most 1 in each H2 section, and at most 1 `important`. [V]
- A free notice holds 60 words or fewer. [V]
- No notice holds another. [V]
- A culture note is the `culture-note` directive, with the fixed title "Culture note" and a colour of its own. It may stand anywhere in the body of a how-to, grammar or writing article, holds 80 words or fewer, and an article has at most 3. It does not count toward the free notices. A `## Culture note` heading is warned about: write the note as the directive. [V] It is short and concrete, about how people live with the language. [R]
- A reader who skips every notice still learns the page's one idea. A notice never holds the core rule of the page; the rule is in the text and the notice adds to it. [R]

### Badges

- A level badge, the `level` role, follows a link to a page of another level, and appears nowhere else. It holds the level of the linked page. [V] It is drawn in the level's colour, the colour of that level's album covers. [B]
- A register badge, `bdg-light`, holds `informal`, `formal` or `colloquial` in a Notes cell, and appears nowhere else. [V]
- No other badge is used. [V]

### Tabs and hidden content

Nothing on a page is hidden behind a click, except the versions in a tab set. A page has no collapsible element: no `dropdown` directive (sphinx-design's name for it), no notice with `:class: dropdown`, no `<details>`. [V]

- A tab set shows one set of phrases in 2 or 3 versions along one line, such as informal and formal. Each tab label is 3 words or fewer, and every tab holds the same kind of thing: a phrase table or an example block. An article has at most 1 tab set, in grammar or how-to only. [V] Register tabs use the labels the language sets in `register_tabs:` in `open-language.yml`, in that order (OL-W8, and the language rule that narrows it). [V] When the learner has to compare the versions, one table holds them side by side instead. [R]
- A tab never holds a heading, a notice, an audio block, Common mistakes or Key points. [V]

### Card grids

- A card grid is `::::{grid} 1 1 2 2` with `:gutter: 3`. Each card is a `grid-item-card` with `:link:` and `:link-type: doc`, no header, no footer and no picture. [V]
- A card's title is the title of the page it links to, and its body is one sentence of 15 words or fewer, unless the page's section sets another limit. [V]
- A page that shows cards for its toctree's entries hides the toctree with `:hidden:`, and its cards link the same pages in the same order. [V]
- A page has no buttons: the way into a page is a link or a card. [V]

## The five categories

Where a page genuinely differs, add up to the limit shown for "other sections" between the named sections. The frame above does not bend.

### Grammar

| Order | Section | Rule |
|---|---|---|
| 1 | Opening paragraphs | Lead and explanation, as in the frame. |
| 2 | Form sections | One to three H2s on how the structure is built. Names say the question, such as *The forms: der, die, das*. |
| 3 | Use sections | One to three H2s on when and why it is used. |
| 4 | Contrast | Optional H2 on how it differs from the structure learners confuse it with. |
| 5 | Common mistakes | An admonition in the last body section, at least one. |
| 6 | Closing | Hear it in practice when no section ends in a track, Summary, Related articles. |

Form, use and contrast sections together do not exceed 5 H2s. Inline examples sit in `:::{ol-examples}`, which names its one presenter with `:presenters:`, at most 3 pairs per section.

### How to

The H1 finishes the phrase "How to ...", so it opens on a verb in its base form: **Order food and drink**, **Introduce yourself**, never **Ordering food and drink**. The five-word limit still applies. [V]

| Order | Section | Rule |
|---|---|---|
| 1 | Opening paragraphs | The lead, then optionally a second paragraph that states the one idea that organises the page (on *Introduce yourself*: formal or informal decides the questions). It never previews later sections. |
| 2 | `## When to use it` | The situations the goal arises in. Once a situation article names the page in its `how-to:` front matter, the situations are listed under Related articles and the section is removed. [V] |
| 3 | `## Key phrases` | The phrases, grouped by situation with H3 group names. Two columns at most. |
| 4 | Other sections | Zero to three H2s, such as how the phrases change with register. Each ends in its track where it has one: a page with a formal and an informal track gives each its own section and closes it with its track. |
| 5 | Closing | Hear it in practice when no section ends in a track, Summary, Related articles. |

`target-title:` holds the goal in the language taught. Culture notes are `:::{culture-note}` directives in the body, where they fit. Where the same phrases come in a formal and an informal version, a tab set shows them, labelled `Formal (Sie)` and `Informal (du)` or the language's own, with an `ol-examples` block or a phrase table in each tab. Explanation sits at the top of the section it explains, just before its table or examples.

### Situations

One everyday scene, heard. A situation article shows a how-to goal reached and teaches nothing itself (ADR 2). Its H1 names the scene in English, five words or fewer, and does not finish "How to ...": **At a party**, **Paying at the checkout**. [R]

| Order | Section | Rule |
|---|---|---|
| 1 | Front matter `how-to:` | One to three links to how-to articles at the article's level or below, in the form `/a1/how-to/introduce-yourself.md`. [V] |
| 2 | Lead | One or two sentences, 20 to 50 words, setting the scene: who, where, what is happening. There is no explanation paragraph. [V] |
| 3 | Related articles | The how-to articles named in `how-to:` are linked under Related articles. The retired `:::{how-to-links}` box is allowed straight after the lead and is warned about. [V] |
| 4 | `## Hear it in practice` | One `dialogue`, `correspondence` or `passage` block, or two for two versions of one scene, each under its own H3. A dialogue has 6 to 20 lines. [V] |
| 5 | `## What to listen for` | Two to four bullets of 30 words or fewer, each pointing at one line of the scene. [V] |
| 6 | Closing | Related articles, optional. |

A situation article has no tables, no examples boxes, no Key points and no Common mistakes. [V]

### Writing

| Order | Section | Rule |
|---|---|---|
| 1 | Opening paragraphs | Lead and explanation: what the text type is and when it is needed. |
| 2 | `## Example: <Situation>` | The model text, a note of 60 words or fewer on why it works, and `### Hear it in practice`. One or two examples. The model text has 60 words or more. |
| 3 | `## Building blocks` | The phrases that frame the register. |
| 4 | Closing | Summary, Related articles. |

### Vocabulary

| Order | Section | Rule |
|---|---|---|
| 1 | Opening paragraphs | Lead and explanation: the theme and why these words go together. |
| 2 | `## The words` | One table of 10 to 15 words, or up to 20 in a pack built on a word class. Two columns: the word with its translation stacked, and Notes for plural, gender or use. |
| 3 | Other sections | Zero to two H2s, such as words that look alike. |
| 4 | Closing | Hear it in practice (every word appears in a sentence) when no section ends in a track, Summary, Related articles. |

## Index pages

An index page is not an article. It has no Hear it in practice and no summary.

### Category index

H1 is the bare category name: **How to**, **Situations**, **Grammar**, **Writing**, **Vocabulary**. [M] The page opens with one to three plain sentences on what its articles have in common. [V] The toctree lists the articles, hidden numbering off. A how-to index never says to work through its articles in order: they are read in any order. [R]

A category index whose toctree lists subcategories, such as A1 Grammar, hides its toctree and shows a card for each subcategory in a card grid, in the toctree's order. A flat category index, and every subcategory index, shows its toctree: a list of twenty articles is shorter on a phone than twenty cards. [V]

Every index page's H1 is in sentence case, as an article's is: **Grammatical cases**, not **Grammatical Cases**. [R]

### Level overview page

H1 is the bare level name. The one place the CEFR level appears in a title. The page is, in order: [V]

1. A lead paragraph of 40 words or fewer: where the level sits in the CEFR and where it starts.
2. `## What learners know`: 3 to 5 bullets of 15 words or fewer. What the course has taught by the end of the level, in plain words.
3. `## What learners can do`: 4 to 6 bullets of 15 words or fewer. Each starts with a verb in its base form, and each is something a learner could be asked to do and a listener could judge.
4. The toctree of the level's categories, in the order how-to, situations, grammar, writing, vocabulary, hidden. [M]
4. `## Categories`: a card grid of one card per category, in the toctree's order, each linking to the category index with one sentence of 15 words or fewer on what its pages hold.
6. `## Additional reading`, as external links only.

The skills are written once, in the page's front matter, and the two sections draw them:

```yaml
skills:
  - id: a1-meet-people
    kind: can          # know or can
    text: "Greet people, introduce themselves and others, and give personal details."
```

Each skill has a unique `id`, a `kind` of `know` or `can`, and a `text`. The section "What learners know" holds `:::{skills} know` and "What learners can do" holds `:::{skills} can`, each with no options and no body, and no hand-written list beside it. The build draws the texts of that kind, in front-matter order, and the limits above apply to those texts. A page with `skills:` uses the directive in both sections. A page still written with hand-written bullets passes with a warning to move them into `skills:`. [V]

Parts 1 to 3 total 150 words or fewer. Levels stop at B2 for now. A level page makes no claim about an exam. It may cite the Council of Europe descriptors, which are public. [R]

### Introduction page

The top-level `index.md`. H1 is exactly **Introduction**. [M] The sections are, in order, and no others: [V]

1. A lead of 60 words or fewer: what the coursebook is, who it is for, that it is free and open.
2. `## How the course works`: that the pages are not a sequence, that any page can be read first, and that each ends with sentences to listen to. 80 words or fewer.
3. `## Levels`: a card grid with one card per level that exists, each linking to its level page, its sentence 20 words or fewer. A level that exists has a card, and a card names a level that exists.
4. `## Categories`: a card grid of one card for each category the first level has, in the order how-to, situations, grammar, writing, vocabulary, each linking to the first level's category index, its sentence 25 words or fewer.
5. `## Where to start`: two to four bullets, each pairing a situation with a link: new to the language, a single problem, an unfamiliar term. The last always links to the glossary.
6. The hidden toctree: `how_to_use`, `terminology`, `contributing`, then each level. [M]

The page is 350 words or fewer. [V]

## The menu

- The menu is plain. No toctree uses `:numbered:`, so the sidebar shows no section numbers. [M]
  - The course is not read in a line. A number says "first, second, third" and tells a reader who came for one problem that they skipped something.
- The sidebar names are the category names: **How to**, **Grammar**, **Writing**, **Vocabulary**. [M]
- On-this-page navigation shows on every article and is removed from every index page. [V]
  - On an article it is the way to reach a section, and the track that closes it, directly. With H2s capped at 7 and H3s at 6, it stays short. A track's title is never a heading, so the list names sections, never tracks.
  - An index page is already a list; a second list beside it repeats it.
- The top-level pages and their order are those in `ol/authoring/menu.py`.

## Proof

A change meets the Open Language standard when `ol check` passes. It runs, in order:

1. `ol validate` for every V rule, against the baseline in `.ol-validate-baseline`, which only shrinks. The wanted pages are listed after it, for review, and fail nothing.
2. The menu step for every M rule. Its errors are never baselined.
3. `ol docs` with warnings as errors, for the B rules: unresolved terms and `related:` entries. A link in the text to a page that does not exist yet is a wanted page, and fails nothing.
4. A render check that opens every built page at 360 pixels and fails if a page scrolls sideways. A table or code block scrolling inside its own box does not count.

The R rules are the review rubric. A pull request description lists the rubric questions answered, and the reviewer ticks them. A change to a rule is a change to this page and to `specs.yml` in the same pull request.

CI runs `ol check` on every pull request to a language repository and blocks the merge on a failure. A new language repository starts with an empty baseline.
