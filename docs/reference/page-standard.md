# Page standard

The shape of every page in a language repository, and how each rule is checked. It applies to every language. A page that follows it looks the same in German, French and Spanish, which is what makes the coursebooks one product.

Read it with [authoring rules](authoring-rules.md), which holds the rules about wording, and the template for the page's type open (`ol templates`).

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

An article is these parts, in this order. The four category sections below fill in the middle.

| # | Part | Rule | Check |
|---|---|---|---|
| 1 | Front matter | `html_meta.description` of 160 characters or fewer, written as the search snippet. `keywords` lists the phrasings a learner would type. | V |
| 2 | Title (H1) | One per page. English, sentence case, five words or fewer, no level, no category, no number. | V (count, prefix), R (case) |
| 3 | Lead paragraph | The first paragraph under the title. One or two sentences (20 to 50 words). Says what the page covers in plain words, and uses the main learner phrasing at least once. | V |
| 4 | Explanation paragraph | The second paragraph. States the one idea of the page in plain language (40 to 120 words). Every technical term in it is linked to the glossary. | V |
| 5 | Prerequisites | Optional admonition after the two opening paragraphs, before the first H2. At most 3 links, true dependencies only. | V |
| 6 | Body sections | The category's own sections (see below). | V |
| 7 | Hear it in practice | `## Hear it in practice` with the audio block, after the body and before the summary. | V |
| 8 | Summary | `## Summary`, as the template for the category shows. | V |
| 9 | Related articles | `## Related articles` at the very end, only links the reader would not reach by the next-page link. Omitted when empty. | V |

Parts 3 and 4 together stay at 180 words or fewer, so the first screen on a phone shows what the page is and why it matters, then the first heading.

### Headings

- Only H1, H2 and H3 exist. There is no H4. [V]
- An H3 appears only where the category's template names one: under `## Example: ...` in writing, to split one H2 into parallel forms in grammar, and for group names under `## Key phrases` in concepts. An article has at most 6 H3. [V]
- An article has at most 7 H2. A page that needs more is two pages. [V]
- A heading is 8 words or fewer, has no number and no closing punctuation, and does not address the reader. German words in a heading are in italics. [V]
- A heading never repeats the heading of its parent. [V]

### Tables

A table is read on a phone, where width is scarce and height is not.

- A word or phrase table has two columns: the phrase with its translation stacked beneath it, and Notes. There is no separate English column. [V: error on a header row that pairs a German column with an English one]
- A table has at most 3 columns. A table of forms, such as a declension, may have up to 5, and only in grammar. [V]
- A table has a header row, and no empty first header cell outside a table of forms. [V]
- At a 360 pixel viewport no page scrolls sideways. [B: render check in CI, see "Proof" below]

The stacked cell is written with the `stack` role: ``{stack}`Guten Morgen | Good morning` ``. Inside a pipe table the separator is written `\|`. Old tables with an English column stay in the baseline until they are migrated.

### Plain language and the glossary

- A sentence is 25 words or fewer, and a paragraph 5 sentences or fewer. Prose averages 18 words a sentence or fewer. [V: error over the limits, warning over the average]
- Prose is active voice. [R]
- A technical term is any word on the term list: the engine's shared list (`ol/authoring/glossary-terms.yml`) plus the language repository's own. Every term on the list has exactly one entry in the glossary. [V: a listed term with no entry is an error] [B: an unresolved `{term}` fails the build]
- The first use of a listed term in each article's prose is written as `{term}` and links to its entry. Headings, example sentences, the text of a link, tables of forms and the glossary itself are exempt. [V]
- A term's meaning is also given in the sentence where it is first used, in plain words, so a reader who does not click still follows. [R]
- A glossary entry has the term in bold, its name in the language taught in brackets when the language repository needs it, one sentence of 30 words or fewer, and one example. [V]
- No page sends the reader off the site to learn what a term means. [R]

Terms that are only a German word being taught, such as *der* or *Konjunktiv II* as the topic of its own article, are the subject of the page and are exempt on that page.

## The four categories

Where a page genuinely differs, add up to the limit shown for "other sections" between the named sections. The frame above does not bend.

### Grammar

| Order | Section | Rule |
|---|---|---|
| 1 | Opening paragraphs | Lead and explanation, as in the frame. |
| 2 | Form sections | One to three H2s on how the structure is built. Names say the question, such as *The forms: der, die, das*. |
| 3 | Use sections | One to three H2s on when and why it is used. |
| 4 | Contrast | Optional H2 on how it differs from the structure learners confuse it with. |
| 5 | Common mistakes | An admonition in the last body section, at least one. |
| 6 | Closing | Hear it in practice, Summary, Related articles. |

Form, use and contrast sections together do not exceed 5 H2s. Inline examples sit in `:::{div} ol-examples`, at most 3 pairs per section.

### Concepts

| Order | Section | Rule |
|---|---|---|
| 1 | Opening paragraphs | Lead and explanation. |
| 2 | `## When to use it` | The situations the goal arises in. |
| 3 | `## Key phrases` | The phrases, grouped by situation with H3 group names. Two columns at most. |
| 4 | Other sections | Zero to three H2s, such as how the phrases change with register. |
| 5 | Culture note | Optional, 80 words or fewer, under the heading `## Culture note`. |
| 6 | Closing | Hear it in practice, Summary, Related articles. |

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
| 4 | Closing | Hear it in practice (every word appears in a sentence), Summary, Related articles. |

## Index pages

An index page is not an article. It has no Hear it in practice and no summary.

### Category index

H1 is the bare category name: **Concepts**, **Grammar**, **Writing**, **Vocabulary**. [M] The page opens with one to three plain sentences on what its articles have in common. [V] The toctree lists the articles, hidden numbering off. A concepts index says the order is a suggestion and that any article can be read first. [R]

### Level overview page

H1 is the bare level name. The one place the CEFR level appears in a title. The page is, in order: [V]

1. A lead paragraph of 40 words or fewer: where the level sits in the CEFR and where it starts.
2. `## What learners know`: 3 to 5 bullets of 15 words or fewer. What the course has taught by the end of the level, in plain words.
3. `## What learners can do`: 4 to 6 bullets of 15 words or fewer. Each starts with a verb in its base form, and each is something a learner could be asked to do and a listener could judge.
4. The toctree of the level's categories, in the order concepts, grammar, writing, vocabulary. [M]
5. `## Additional reading`, as external links only.

Parts 1 to 3 total 150 words or fewer. Levels stop at B2 for now. A level page makes no claim about an exam. It may cite the Council of Europe descriptors, which are public. [R]

### Introduction page

The top-level `index.md`. H1 is exactly **Introduction**. [M] The sections are, in order, and no others: [V]

1. A lead of 60 words or fewer: what the coursebook is, who it is for, that it is free and open.
2. `## How the course works`: that the pages are not a sequence, that any page can be read first, and that each ends with sentences to listen to. 80 words or fewer.
3. `## Levels`: one bullet per level that exists, each linking to its level page, 20 words or fewer. A level that exists has a bullet, and a bullet names a level that exists.
4. `## Categories`: exactly four bullets, in the order concepts, grammar, writing, vocabulary, each linking to the first level's category index, 25 words or fewer.
5. `## Where to start`: two to four bullets, each pairing a situation with a link: new to the language, a single problem, an unfamiliar term. The last always links to the glossary.
6. The hidden toctree: `how_to_use`, `terminology`, `contributing`, then each level. [M]

The page is 350 words or fewer. [V]

## The menu

- The menu is plain. No toctree uses `:numbered:`, so the sidebar shows no section numbers. [M]
  - The course is not read in a line. A number says "first, second, third" and tells a reader who came for one problem that they skipped something.
  - Order still carries meaning in concepts: the toctree order is the suggested sequence, and the index says so.
- The sidebar names are the category names: **Concepts**, **Grammar**, **Writing**, **Vocabulary**. [M]
- On-this-page navigation shows on every article and is removed from every index page. [V]
  - On an article it is the way to reach *Hear it in practice* directly. With H2s capped at 7 and H3 left out of it, it stays short.
  - An index page is already a list; a second list beside it repeats it.
- The top-level pages and their order are those in `ol/authoring/menu.py`.

## Proof

A change meets the Open Language standard when `ol check` passes. It runs, in order:

1. `ol validate` for every V rule, against the baseline in `.ol-validate-baseline`, which only shrinks.
2. The menu step for every M rule. Its errors are never baselined.
3. `ol docs` with warnings as errors, for the B rules: unresolved links and terms.
4. A render check that opens a sample page of each type, and each index page, at 360 pixels and fails if the page scrolls sideways.

The R rules are the review rubric. A pull request description lists the rubric questions answered, and the reviewer ticks them. A change to a rule is a change to this page and to `specs.yml` in the same pull request.

CI runs `ol check` on every pull request to a language repository and blocks the merge on a failure. A new language repository starts with an empty baseline.
