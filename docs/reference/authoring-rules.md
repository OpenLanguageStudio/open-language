# Authoring rules

The rules an article in a language repository follows that neither `ol validate` nor the review rubric holds. Read it with [the page standard](page-standard.md), which holds the shape of every page and how each rule is checked, and with the template for the article's category open. It applies to every language.

## Where the rules live

| Where | What it holds |
|---|---|
| `ol validate`, run by `ol check` | Every rule a script can measure. An article that fails it is not done. The limits are in `ol/authoring/specs.yml`. |
| [The page standard](page-standard.md) | The shape of every page, each rule with its check. |
| The templates, listed by `ol templates` | That shape as a starting point for each page type. Bend a template where the article needs it, such as tables with a little prose for adjective endings. The checks still apply. |
| `ol/authoring/review-rubric.yml` | The questions that need a reader: level, correctness, teaching value and plain language. |
| This page | Everything else. |

A rule is written in one of these places and nowhere else.

## A language repository

A language repository's `AGENTS.md` links this page and does not restate it. It adds only what one language needs: its set of Sphinx roles, its curriculum order, and the articles it holds up as the model for each category. It never contradicts a rule here.

## Categories

Each level has up to four categories, each a directory directly under the level: `concepts`, `grammar`, `writing` and `vocabulary`. There are no others: `topics` and `situations` are not in use, and material about understanding a scenario goes in a concepts article. `ol validate` checks the menu these make (see `CONTEXT.md`, Menu).

## File names

- The file name of a published article never changes. Links depend on it. A track does not: its `:track:` gives its own name.
- Grammar file names are in the language being taught, such as `bestimmter-artikel`. Every other file name, and every directory that groups articles, is in English.

## Shape by category

[The page standard](page-standard.md) gives the sections of each category and their limits. This section holds what a writer needs beyond them.

**Grammar.** Grammar at B levels adds depth, such as exceptions and register, rather than more topics.

**Concepts.** A goal a learner meets in real situations. The toctree order is a suggested sequence, so a concept names what it truly depends on in its Prerequisites, and nothing else.

**Vocabulary.** One theme. At higher levels a pack may widen the words for one meaning ("Ways to say big"). A theme that cannot fill a pack with words at its level waits for a higher level.

**Writing.** One everyday scenario, in one register. There is no "The task" section, and no heading starts "Model text:". A levels cover emails, short messages and postcards. B levels add formal text types. A model text is written in flowing sentences to be read aloud, and it reaches its length with content, never filler.

## Phrase tables

A table of phrases has two columns, `Phrase` and `Notes`, never a column for the language taught and another for English. A phone has no room for three. Each phrase uses the `stack` role, which shows the translation beneath the phrase:

```markdown
| Phrase | Notes |
|---|---|
| {stack}`Guten Morgen \| Good morning` | Used until about noon. |
```

Write the separator as `\|` inside a table, because a table splits a cell at every pipe. Outside a table write ` | `. See the README for the role's details.

## Hear it in practice

The section is `## Hear it in practice`. In writing, each `## Example: <Situation>` holds its own `### Hear it in practice` instead.

## The glossary

The glossary is the Terminology page. An entry sits in a `{glossary}` directive, with the term's name in the language taught after ` : ` when the language needs it, and an indented definition:

```markdown
:::{glossary}
Noun : Nomen
  A word that names a person, place or thing. *Example: der Hund, the dog.*
:::
```

The page shows it as **Noun** (Nomen). An article links it with ``{term}`noun` ``, and with ``{term}`nouns <noun>` `` when it writes another form. An entry may hold several term lines, and each then resolves.

A language repository lists its own terms in `glossary-terms.yml`, next to `open-language.yml`, in the format the shared `ol/authoring/glossary-terms.yml` describes. A term on a list also matches with an `-s`. Name any other form under `forms`.

## Dashes

An en dash (–) appears in three places only: between the two halves of a title pair, as a dialogue dash inside a sentence in the language being taught, and as a placeholder in an empty table cell.

## Index pages

- A grammar index lists its articles in a logical order: the noun system, then verbs, sentence structure, modifiers and anything else.
- A concepts index lists its articles in the suggested order, and says that any article can be read first.

## Frontmatter

Write `html_meta.description` for the snippet a search engine shows under the title.

Write `presenter:` with a presenter's slug to name who speaks the page's `ol-examples` blocks. One presenter speaks a whole page. Leave it out to use the language's usual presenter.
