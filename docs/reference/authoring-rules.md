# Authoring rules

The rules an article in a language repository follows that neither `ol validate` nor the review rubric holds. Read it with the template for the article's category open. It applies to every language.

## Where the rules live

| Where | What it holds |
|---|---|
| `ol validate`, run by `ol check` | Every rule a script can measure. An article that fails it is not done. The limits are in `ol/authoring/specs.yml`. |
| The templates, listed by `ol templates` | The shape of an article in each category. Bend a template where the article needs it, such as tables with a little prose for adjective endings. The checks still apply. |
| `ol/authoring/review-rubric.yml` | The questions that need a reader: level, correctness, teaching value and plain language. |
| This page | Everything else. |

A rule is written in one of these places and nowhere else.

## A language repository

A language repository's `AGENTS.md` links this page and does not restate it. It adds only what one language needs: its set of Sphinx roles, its curriculum order, and the articles it holds up as the model for each category. It never contradicts a rule here.

## Categories

Each level has four categories, each a directory directly under the level: `grammar`, `concepts`, `writing` and `vocabulary`. `situations` is not in use; material about understanding a scenario goes in a concepts article.

## File names

- The file name of a published article never changes. Links depend on it. A track does not: its `:track:` gives its own name.
- Grammar file names are in the language being taught, such as `bestimmter-artikel`. Every other file name, and every directory that groups articles, is in English.

## Shape by category

**Grammar.** How the structure is built, then when and why it is used, then how it differs from the structure learners confuse it with, if there is one. Grammar at B levels adds depth, such as exceptions and register, rather than more topics.

**Concepts.** A goal a learner meets in real situations, then the phrases for it grouped by situation, then an optional short cultural note. Concepts are a curriculum read in order, so each names the article it builds on in its Prerequisites.

**Vocabulary.** One theme, with the word table at the top: 10 to 15 new words, or up to 20 in a pack built on a word class, such as common verbs. At higher levels a pack may widen the words for one meaning ("Ways to say big"). Its "Hear it in practice" section uses every word of the pack in a sentence. A theme that cannot fill a pack with words at its level waits for a higher level.

**Writing.** One everyday scenario, in one register. The writing template still has an older shape; follow this one:

1. An opening paragraph on what the text type is and when it is needed. There is no "The task" section.
2. `## Example: <Situation>`, with a capital after the colon, holding the model text, a short note on what makes it work, and its own `### Hear it in practice`. No heading starts "Model text:".
3. `## Building blocks`: the phrases that frame the register.
4. `## Summary`.

A levels cover emails, short messages and postcards. B levels add formal text types. A model text is written in flowing sentences to be read aloud, and it reaches its length with content, never filler.

## Hear it in practice

At the top level of an article the section is `## Hear it in practice`. Inside a sub-section, for one of several parallel forms, it is `### Hear it in practice`.

## Dashes

An en dash (–) appears in three places only: between the two halves of a title pair, as a dialogue dash inside a sentence in the language being taught, and as a placeholder in an empty table cell.

## Index pages

- A grammar index lists its articles in a logical order: the noun system, then verbs, sentence structure, modifiers and anything else.
- A concepts index lists its articles in the order they are learned.
- An index opens with one to three plain sentences on what its articles have in common.

## Frontmatter

Write `html_meta.description` for the snippet a search engine shows under the title.
