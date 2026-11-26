# Authoring rules

The rules an article in a language repository follows that neither `ol validate` nor the review rubric holds. Read it with [the page standard](page-standard.md), which holds the shape of every page and how each rule is checked, and with the template for the article's category open. It applies to every language.

## Where the rules live

| Where | What it holds |
|---|---|
| `ol validate`, run by `ol check` | Every rule a script can measure. An article that fails it is not done. The limits are in `ol/authoring/specs.yml`. |
| [The page standard](page-standard.md) | The shape of every page, each rule with its check. |
| [Components](components.md) | How to write each part a page is built from: inline roles, notices, tables, tabs, cards. The kitchen-sink elements a page never uses, and why. |
| The templates, listed by `ol templates` | That shape as a starting point for each page type. Bend a template where the article needs it, such as tables with a little prose for adjective endings. The checks still apply. |
| `ol/authoring/review-rubric.yml` | The questions that need a reader: level, correctness, teaching value and plain language. |
| This page | Everything else. |

A rule is written in one of these places and nowhere else.

## A language repository

A language repository's `AGENTS.md` links this page and does not restate it. It adds only what one language needs: its set of Sphinx roles, its curriculum order, and the articles it holds up as the model for each category. It never contradicts a rule here.

## Categories

Each level has up to five categories, each a directory directly under the level: `how-to`, `situations`, `grammar`, `writing` and `vocabulary`. There are no others: `topics` is not in use. `ol validate` checks the menu these make (see `CONTEXT.md`, Menu).

## File names

- The file name of a published article never changes. Links depend on it. A track does not: its `:track:` gives its own name.
- Grammar file names are in the language being taught, such as `bestimmter-artikel`. Every other file name, and every directory that groups articles, is in English.

## Shape by category

[The page standard](page-standard.md) gives the sections of each category and their limits. This section holds what a writer needs beyond them.

**Grammar.** Grammar at B levels adds depth, such as exceptions and register, rather than more topics.

**How to.** A goal a learner meets in real situations. Its title finishes the phrase "How to ...", so it opens on a verb in its base form, such as "Order food and drink". `target-title:` names the goal in the language taught, `target-title: Sich vorstellen`, and the build draws it under the title, so no sentence says "German calls it ...". The lead says what the reader can do after the page. A second paragraph is optional: it states the one idea that organises the page, such as "formal or informal decides the questions", and never previews the sections below. Explanation sits at the top of the section it explains, just before its table or examples. Once a situation names the article, its situations are listed under Related articles and `## When to use it` is removed. The articles are read in any order, so an article names what it truly depends on in its Prerequisites, and nothing else.

**Situations.** One everyday scene, heard: the people, the place and what they say. A situation shows a how-to goal reached and teaches nothing itself, so it has no phrase tables and no explanation. Its front matter names the one to three how-to articles it puts to use (`how-to:`), at its level or below, and the build links both ways from there. Most are dialogues of six to twenty lines. Keep to the language of the level and of the linked how-to articles, so a learner who has read them can follow every line. A scene may come back at a higher level with harder language.

**Vocabulary.** One theme. At higher levels a pack may widen the words for one meaning ("Ways to say big"). A theme that cannot fill a pack with words at its level waits for a higher level.

**Writing.** One everyday scenario, in one register. There is no "The task" section, and no heading starts "Model text:". A levels cover emails, short messages and postcards. B levels add formal text types. A model text is written in flowing sentences to be read aloud, and it reaches its length with content, never filler.

## Phrase tables

A table of phrases earns its place through its Notes column. Phrases with nothing to note go in an `ol-examples` block, which also makes them playable, and a table whose Notes cells are all empty fails. A table of phrases has two columns, `Phrase` and `Notes`, and no table has a column for the translation. A phone has no room for three. Each phrase uses the `stack` role, which shows the translation beneath the phrase:

```markdown
| Phrase | Notes |
|---|---|
| {stack}`Guten Morgen \| Good morning` | Used until about noon. |
```

Write the separator as `\|` inside a table, because a table splits a cell at every pipe. Outside a table write ` | `. See the README for the role's details.

## Hear it in practice

A track closes the section it practises. In grammar, how-to and vocabulary, a body section may end in its audio block, or in two of them: a page with a formal and an informal track gives each its own section and puts the track at the end of it, rather than stacking the tracks at the end of the page. A page whose sections end in no track has `## Hear it in practice` after the body for it. In writing, each `## Example: <Situation>` holds its own `### Hear it in practice` instead.

A track written by an `examples` or `pairs` block carries 12 to 30 examples, about 20 for a 70 second track. Each half of a pair counts as one example. A `dialogue`, `passage` or `correspondence` block has no example count, so a text-message exchange of three to five examples is a whole track.

The audio block draws its own title. No heading repeats a track's `:title:` or `:title-en:`, so a track's title never appears in the sidebar or the page contents.

## Presenters

A page never names a presenter. Every audio block that writes its track names its presenters with `:presenters:`, and every `ol-examples` box names its one presenter the same way.

Write for the presenters, in every mode, wherever the lesson allows. The language being taught comes first. Within that, the examples fit the life of the presenter who says them: their work, family, town and interests. This matters most in `dialogue`, `passage` and `correspondence`.

1. At the start of each authoring run, read the presenters' profiles from the app.
2. Pick the presenters each block and box needs. A sentence that marks the gender of whoever says it, such as *Ich bin Krankenschwester*, needs a presenter it fits.
3. When a topic fits nobody, add the detail to a presenter's profile in the app first, such as making a presenter a basketball fan, and then write for them.

## The glossary

Link to an article before the glossary. The glossary holds grammar jargon and terms of the language taught that a general reader would not know, such as *dative* or *separable verb*. Everyday words, such as "question word", "noun" or "plural", are not on the term list and need no link. The first use of a listed term is linked by a link, in the same sentence, to the article that covers it. Only when no article covers it is it written as `{term}`. A grammar word that is not on the list may keep a `{term}` link, which opens its entry in place.

The glossary is the Terminology page. An entry sits in a `{glossary}` directive, with the term's name in the language taught after ` : ` when the language needs it, and an indented definition:

```markdown
:::{glossary}
Dative : Dativ
  The case of the indirect object, the person something is given to. *Example: dem Kind, to the child.*
:::
```

The page shows it as **Dative** (Dativ). An article links it with ``{term}`dative` ``, and with ``{term}`dative case <dative>` `` when it writes another form. An entry may hold several term lines, and each then resolves.

A language repository lists its own terms in `glossary-terms.yml`, next to `open-language.yml`, in the format the shared `ol/authoring/glossary-terms.yml` describes. A term on a list also matches with an `-s`. Name any other form under `forms`.

## Dashes

An en dash (–) appears in three places only: between the two halves of a title pair, as a dialogue dash inside a sentence in the language being taught, and as a placeholder in an empty table cell.

## Index pages

- A grammar index lists its articles in a logical order: the noun system, then verbs, sentence structure, modifiers and anything else.
- A how-to index never says to work through its articles in order: they are read in any order.

## Frontmatter

Write `html_meta.description` for the snippet a search engine shows under the title. On a how-to article, write `target-title:`, the goal in the language taught. Any other article may have one too.

On a level page, write the skills once under `skills:` in the front matter, each with an `id`, a `kind` of `know` or `can`, and a `text`. Draw them with `:::{skills} know` and `:::{skills} can` under the two sections, and write no list beside them. On an article, name one or two of the level's skill ids under `skills:`.

## Related articles

List related pages under `related:` in the front matter, as page paths without `.md`: relative to the page's folder, or from the root with a leading `/`. Write `related: [/a1/grammar/verbs/sein-und-haben, choose-between-du-and-sie]`. The build draws them as the last section, `## Related articles`, grouped by kind of page. Do not write the section, and write no `:::{situations}` or `:::{how-to-links}` box: the links they drew are drawn there too. A how-to article keeps `## When to use it` until a situation names it, and then the situations replace the section. An entry that names no page stops the build.

Keep `related:` short: a few close neighbours. The main way pages connect is a link in the text, at the point where the reader needs it. Such a link may name a page that is not written yet, with the path it should have: it is a wanted page, fails nothing and shows as plain text until the page exists. Add no marker or TODO beside it. `ol wanted` lists every wanted page with the pages that link to it, and `ol check` prints the list in its own section. A common mistake that another article explains ends with "(learn more: [](…))".

Link only pages a reader would not reach by the next-page link, and link no other article of the article's own subcategory.

## Tags

When the repository has `track-tags.yml`, give every audio block that writes a track a `:tags:` option and the article a `tags:` list in its front matter, each tag exactly as the file lists it under `grammar:` or `themes:`. A `:duplicate:` block needs no tags.
