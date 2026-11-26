# Components

The parts a Coursebook page is built from, how to write each one, and where it goes. Keep it open while writing a page, next to the template for the page's type.

A Coursebook page is MyST Markdown, built by Sphinx with sphinx-design, and the Open Language app draws it in the site's theme. The app's kitchen sink shows every element Sphinx and sphinx-design offer, as they look on the site: build it with `uv run python manage.py build_docs kitchen_sink` in the app repository and open `/kitchen-sink/` on the development server. Most of what it shows is for software documentation. A Coursebook page uses the components on this page and nothing else.

This page shows how to write each component. How many a page may hold, and where, are rules, and rules live in [the page standard](page-standard.md#components) only. Each entry below links to its rule.

## At a glance

| Component | Write it as | Use it for |
|---|---|---|
| Italics | `*der Hund*` | A word of the language taught, inside English prose or a heading. |
| Bold | `**den**` | The part of a form that changes: an ending, the corrected word in a mistake. |
| Marking role | ``{akk}`den` `` | The grammatical job of a word in an example sentence. The language repository lists its roles. |
| Stacked phrase | ``{stack}`Guten Morgen \| Good morning` `` | A phrase with its translation beneath it, in a table cell or a list. |
| Glossary term | ``{term}`accusative` `` | The first use of a listed technical term in an article's prose, when no article covers it. |
| Page link | `[](/a1/grammar/cases/akkusativ.md)` | A link to another page, or to a page not written yet. Empty brackets: the build writes the page's title. |
| Level badge | ``{level}`A1` `` | The level after a link to a page of another level, in that level's colour. |
| Register badge | ``{bdg-light}`informal` `` | A register in a Notes cell. |
| Example block | `:::{ol-examples}` with `:presenters:` | Example sentences with their translations, beside the explanation. |
| Audio block | `:::{audio-examples}` | A track, at the end of the section it practises or under Hear it in practice. |
| Situations box (retired) | `:::{situations}` | Folded into Related articles. Remove it. |
| How to box (retired) | `:::{how-to-links}` | Folded into Related articles. Remove it. |
| Skills list | `:::{skills} can` | On a level page, the skills of one kind, drawn from the front matter. `know` or `can`. |
| Notice | `:::{tip}` and three others | A fact set apart from the text: a nuance, a memory aid, a trap. |
| Titled notice | `:::{admonition} Common mistakes` | Prerequisites, Common mistakes and Key points, and no other title. |
| Culture note | `:::{culture-note}` | A short, concrete note on how people live with the language. How-to, grammar and writing. |
| Phrase table | Markdown pipe table | Phrases with something to note, two columns. |
| Forms table | Markdown pipe table | A paradigm: forms by gender, person or case. Grammar only. |
| Block quote | `> ...` | The model text in a writing article. |
| Tabs | `::::{tab-set}` | One set of phrases in two or three versions: *du* and *Sie*, spoken and written. |
| Card grid | `::::{grid} 1 1 2 2` | The way into the pages below an index page. Index pages and the Introduction only. |
| Toctree | `` ```{toctree} `` | The menu. Index pages only. |

The full list, which `ol validate` holds a page to:

- **Directives:** `ol-examples`, `audio-examples`, `note`, `tip`, `important`, `warning`, `admonition` (the three titles only), `culture-note` in how-to, grammar and writing, `skills` on level pages, `situations` on how-to articles and `how-to-links` on situation articles (both retired: see below), `tab-set`, `tab-item`, `grid`, `grid-item-card`, `toctree`, and `glossary` on the Terminology page.
- **Roles:** the language repository's marking roles, `stack`, `term`, `level` and `bdg-light`; on How to use and Contributing also `kbd`, `guilabel`, `menuselection`, `file`, `command` and `samp`.

## Inline

### Italics and bold

Italics mark a word of the language taught: *der*, *weil*, *Konjunktiv II*. Bold marks the part of a form that changes, so the eye finds it: Ich sehe **den** Mann. Bold is never used to stress an English word, and a paragraph made of nothing but bold text is never used as a label (see [Example blocks](#example-blocks)).

### Marking roles

A role marks the grammatical job of one word or one phrase in an example sentence, and the site colours it. The roles a language uses are listed in its repository's `AGENTS.md` and its `conf.py` (`custom_roles`). Mark only the teaching focus of the sentence:

```markdown
Ich gebe {dativ}`dem Kind` {akk}`den Ball`.
```

### Stacked phrase

`stack` shows a phrase with its translation beneath it. The separator is ` | `, written `\|` inside a table:

```markdown
| Phrase | Notes |
|---|---|
| {stack}`Die Rechnung, bitte. \| The bill, please.` | To the server, at the table. |
```

### Glossary term

``{term}`accusative` `` links a term to its entry on the Terminology page, and ``{term}`accusative case <accusative>` `` writes another form of it. Use it when no article covers the term. The glossary holds grammar jargon and terms of the language taught that a general reader would not know. An everyday word, such as "question word", needs no link. The [authoring rules](authoring-rules.md#the-glossary) give the entry format.

### Page links

Leave the text of a link to another Coursebook page empty. The build writes the target page's title, so a retitled page never leaves a stale link behind:

```markdown
- [](/a1/grammar/cases/akkusativ.md)
```

A link that needs words of its own inside a sentence keeps them: `the [accusative case](/a1/grammar/cases/akkusativ.md)`. Link in the text, at the point where the reader needs it, and to an article before the glossary: a link to the article that covers a term, in the sentence that first uses it, is the term's link.

A link may name a page that is not written yet, with the path it should have (`<level>/<category>/<file-name>.md`). It is a wanted page. Add no marker: until the page exists, the build draws the link's text, or the page's name as words, as plain text (`<span class="ol-wanted">`), and once the page is written the next build draws a live link. `ol wanted` lists every wanted page with the pages that link to it. Use a wanted link for depth only: the page teaches its goal without it. `related:` in the front matter takes pages that exist, and nothing else. A link off the site is written in full, with its text: `[Goethe-Institut: A1 Wortliste](https://...)`. External links appear only under a level page's Additional reading.

### Badges

A badge is a small label. A Coursebook page uses two kinds:

```markdown
- [](/b1/grammar/relativsaetze.md) {level}`B1`

| {stack}`Hallo! \| Hi!` | {bdg-light}`informal` |
```

`level` names a level, after a Related articles or Prerequisites link to a page of another level. It is drawn in that level's colour, the same colour as the level's album covers, so a level looks the same on a page, on a cover and in the app. `bdg-light` holds a register in a Notes cell: `informal`, `formal` or `colloquial`, and is neutral. No other badge colour is used: a green or red badge would read as right or wrong. [Rule](page-standard.md#badges)

## Blocks

### Example blocks

Example sentences sit in an `ol-examples` block, a definition list: the sentence, then its translation on the next line after `: `. Its first line under the opening is `:presenters:` with the slug of the one presenter who says every sentence in it. A box without it is refused. The section's heading and the block's own look say what it is, so no `**Examples:**` line goes above it.

```markdown
:::{ol-examples}
:presenters: emilia
Ich sehe {akk}`den` Turm.
: I see the tower.

Wir nehmen {akk}`die` Straßenbahn.
: We take the tram. (feminine, unchanged)
:::
```

[Rule](page-standard.md#the-four-categories), and the README of this package for what is spoken.

### Audio block

`audio-examples` writes or shows a track. In grammar, how-to and vocabulary a track closes the body section it practises: it is the section's last block, and two tracks may close one section. A page whose sections end in no track has `## Hear it in practice` for it instead. The block draws its own title, so no heading repeats the track's `:title:` or `:title-en:`. The block's options are in the README of this package and in `ol/authoring/templates/audio-examples-block.md`. It never sits inside a tab or a notice.

`ol-examples` and `audio-examples` are two directives on purpose. A box beside an explanation and a page's track are different things, and neither switches into the other on an option. Underneath they share one list, `ol/docs/example_list.py`: it reads a definition list as sentences and translations, gives each sentence in the form that identifies it, and draws the list. `audio-examples` adds the track's header, its translations button and the handling of a track that another page writes.

### Situations and How to boxes (retired)

The two boxes are folded into Related articles. The build draws a how-to article's situations, and a situation's how-to articles, under `## Related articles` from the situations' `how-to:` front matter, so no page writes a box. A page with `related:` that still holds one fails, and a page without `related:` is warned about. See [Related articles](page-standard.md#related-articles).

### Skills

A level page lists its skills once, under `skills:` in its front matter, and draws them with the directive: `:::{skills} know` under "What learners know" and `:::{skills} can` under "What learners can do". It takes no options and no body. The build writes a bullet list of the text of every skill of that kind, in front-matter order. [Rule](page-standard.md#level-overview-page)

### Notices

A notice sets one fact apart from the text. Each of the four kinds has one meaning and its own colour, so the reader knows what a box holds before reading it:

| Kind | Colour on the site | Holds |
|---|---|---|
| `note` | Blue grey | A fact that explains: background, a nuance, why a form is as it is. |
| `tip` | Green | A way to remember a form, or a shortcut. |
| `important` | Gold | The one rule of the page a learner must not miss. |
| `warning` | Orange | A trap: a false friend, a register blunder, a form that looks right and is not. |

```markdown
:::{tip}
Masculine nouns that end in *-er* for a person, such as *der Lehrer*, keep that ending in the plural.
:::
```

Three notices have fixed titles and fixed kinds. Prerequisites opens an article, Common mistakes closes its body, and Key points is the summary:

```markdown
:::{admonition} Prerequisites
:class: note
Before reading this article, make sure you are comfortable with:
- [](/a1/grammar/articles/bestimmter-artikel.md)
:::

:::{admonition} Common mistakes
:class: caution

- *\*Ich sehe der Mann.* → Ich sehe **den** Mann. (direct object, masculine)
- *\*Wo kommst du?* → **Woher** kommst du? (learn more: [](/a1/grammar/questions/w-questions.md))
:::

:::{admonition} Key points
:class: note

- Three genders: **der**, **die**, **das**.
:::
```

A common mistake that another article explains ends with a link to it, "(learn more: [](…))". The link may name a page not written yet. A wrong form in Common mistakes is in italics after an asterisk, the linguist's mark for a form no speaker uses, and its correction follows the arrow with the changed word in bold. Never strike a wrong form through: a screen reader reads struck text aloud as if it were right.

A culture note is a notice of its own, with the fixed title "Culture note" and a violet no other notice uses. It stands anywhere in the body of a how-to, grammar or writing article, where it fits, and never under a `## Culture note` heading. It holds 80 words or fewer, an article has at most 3, and it does not count toward the free notices. It takes no title and no options:

```markdown
:::{culture-note}
At work, Germans often give only their surname: *Müller*, with a handshake.
:::
```

`hint`, `caution`, `attention`, `danger`, `error`, `seealso`, `todo` and the version notes never appear. `hint` and `caution` repeat `tip` and `warning`. `danger` and `error` say something cannot be undone, which nothing in a language course is, and a red alarm box makes a learner anxious about a slip that costs nothing. [Rule](page-standard.md#notices)

### Tables

A table is a Markdown pipe table, so the checks can count its columns. A phrase table has two columns, Phrase and Notes, with the translation stacked in the first. It earns its place through its Notes column: a table whose Notes cells are all empty fails, and its phrases go in an example block instead, where they also play. A forms table, in grammar only, leaves its first header cell empty and names each row in the first column:

```markdown
| | Masculine | Feminine | Neuter | Plural |
|---|---|---|---|---|
| Nominative | der | die | das | die |
| Accusative | **den** | die | das | die |
```

The [page standard](page-standard.md#tables) holds the column limits.

### Block quote

A block quote holds the model text of a writing article, under its `## Example: ...` heading, with the text's own line breaks. It is used for nothing else.

### Tabs

Tabs show one set of phrases in two or three versions, of which a reader wants one: informal and formal, spoken and written, Germany, Austria and Switzerland. Each tab holds the same kind of thing, a phrase table or an example block. Formal and informal versions are labelled `Formal (Sie)` and `Informal (du)`, or the language's own, everywhere in the course. When a learner has to compare the versions, they go side by side in one table instead, because a tab hides the other side.

```markdown
:::::{tab-set}

::::{tab-item} Formal (Sie)
:::{ol-examples}
:presenters: emilia
Wie heißen Sie?
: What's your name?
:::
::::

::::{tab-item} Informal (du)
:::{ol-examples}
:presenters: emilia
Wie heißt du?
: What's your name?
:::
::::

:::::
```

[Rule](page-standard.md#tabs-and-hidden-content)

## Index pages

### Toctree

Every index page keeps its toctree, because the sidebar is built from it. A page that shows cards hides its toctree with `:hidden:`, so the reader does not see the same list twice. A flat category index shows its toctree as the list of its articles.

### Card grid

A card grid is the way into the pages below an index page. It is one column on a phone and two on a wider screen. A card's title is the target page's title, and its body is one plain sentence:

```markdown
::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} How to
:link: how-to/index
:link-type: doc

Everyday tasks, one per page: greeting, ordering, asking the way.
:::

::::
```

Cards have no header, no footer, no picture and no badge. [Rule](page-standard.md#card-grids)

## Page recipes

The [page standard](page-standard.md) gives every page's sections in order, and `ol templates` gives a starting file for each. These are the components each page is built from, top to bottom.

| Page | Built from |
|---|---|
| Introduction | Lead, `## How the course works`, `## Levels` as a card per level, `## Categories` as a card per category of the first level, `## Where to start` as a list, hidden toctree. |
| Level page | Lead, `## What learners know` and `## What learners can do` as skills lists, hidden toctree, `## Categories` as a card per category, `## Additional reading` as a list of external links. |
| Category index with subcategories | Lead, hidden toctree, a card per subcategory. |
| Flat category index, subcategory index | Lead, visible toctree. |
| Grammar article | Opening paragraphs, Prerequisites, form and use sections with forms tables, example blocks and a notice or culture note where one helps, each ending in its track where it has one, Common mistakes, Hear it in practice when no section ends in a track, Summary with Key points, Related articles. |
| How-to article | `target-title:`, the lead and an optional second paragraph, Prerequisites, When to use it until a situation names the article, Key phrases as phrase tables or example blocks (or one tab set of them), other sections each ending in its track, culture notes where they fit, Hear it in practice when no section ends in a track, Summary, Related articles. |
| Situation article | Lead, Hear it in practice with one or two dialogue, correspondence or passage blocks, What to listen for as a list, Related articles. |
| Writing article | Opening paragraphs, Prerequisites, one or two Example sections each with a block quote and its own Hear it in practice, Building blocks as a phrase table, Summary, Related articles. |
| Vocabulary article | Opening paragraphs, The words as one phrase table, Hear it in practice, Summary, Related articles. |

## Never used

Everything else in the kitchen sink stays out of a Coursebook page. This page calls an element that opens and closes on a click a collapsible element, or a collapsible. sphinx-design names its directive `dropdown`; that is the only place the word appears, because a dropdown means a menu. Most of it is software documentation. The rest fails a reader on a phone, or does a job another component already does.

| Element | Why not |
|---|---|
| Headings below H3 | A page that needs them is two pages. |
| Bullet lists nested more than one level, task lists | A list that deep is a table or two sections. |
| Definition lists outside an example block, field lists, option lists | They look like example blocks and are not spoken. |
| Epigraph, pull quote, highlights, line block | Decoration. A learner came for one problem. |
| Topic, sidebar, rubric, horizontal rule | A sidebar squeezes the text column to half on a tablet. The rest stand in for headings, which the on-this-page list cannot reach. |
| Footnotes, citations | They send a reader on a phone to the foot of the page and back. An aside goes in brackets or a note. |
| Abbreviations (`abbr`) | The explanation shows on hover, and a phone has no hover. A term goes in the glossary. |
| Highlighted spans (`.mark`), strikethrough, sub- and superscript | Highlight is what a marked phrase looks like. Struck text is read aloud as if it were right. |
| Interface roles (`kbd`, `guilabel`, `menuselection`, `file`, `command`, `samp`) | They describe software. The How to use and Contributing pages may use them. |
| Inline code, code blocks, console, diff, Python sessions, reference entries | Software documentation. A word of the language taught is in italics, never in code. |
| Maths | No language page needs it. |
| `list-table`, `csv-table` | The checks read pipe tables only, so a table written another way escapes the column limits. |
| `hlist` columns | A list of words is a phrase table, with room for notes. |
| Pictures and figures | No artwork exists yet. When it does, a picture is a figure with alt text, and this page gains an entry. |
| Collapsible elements (the `dropdown` directive) | They hide content. Anything worth writing on a page is worth showing: an aside is a notice, a detail is a sentence in the section, and a long digression is its own page. |
| Cards with headers or footers, and buttons (the `button-ref` directive) | One kind of card keeps every index page alike, and a link or a card is the way into a page. |
| `eval-rst` | Everything a page needs is in MyST. |
| Substitutions | A value set once in `conf.py` is a value a reader of the source cannot see. |
