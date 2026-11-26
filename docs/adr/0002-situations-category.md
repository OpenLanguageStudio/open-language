# 2. Situations, a fifth category

- **Status:** Accepted, 2026-11-23.

## Context

A how-to article teaches a goal: the phrases, the patterns, what to watch for. It says where the goal comes up in `## When to use it`, as a list such as "Meeting someone for the first time" and "Checking in somewhere and giving your details". Nothing lets a learner hear that goal reached, between people, in an everyday scene.

Since ADR 1 a block can be a `dialogue`, so a page can carry a conversation with several presenters. That makes the scene itself worth a page: the conversation at a party, at the checkout, at a hotel desk. It trains listening and spoken interaction, which a how-to article, built for production, does not.

A `situations` category was tried before and withdrawn, because without dialogue it held nothing a how-to article did not.

## Decision

### The category

`situations` is the fifth category. A level lists its categories in the order how-to, situations, grammar, writing, vocabulary. The sidebar names it Situations.

### A situation article shows, and does not teach

A situation article is one everyday scene, heard. It holds:

| Order | Part | Rule |
|---|---|---|
| 1 | Title | The scene, in English: **At a party**, **Paying at the checkout**. Not a goal, so it does not finish "How to ...". |
| 2 | Lead | One or two sentences setting the scene: who, where, what is happening. No explanation paragraph follows. |
| 3 | `:::{how-to-links}` | The how-to articles the scene puts to use, as a box the build writes from the front matter. |
| 4 | `## Hear it in practice` | The scene's track: a `dialogue`, `correspondence` or `passage` block. Two blocks at most, each under its own H3, for two versions of one scene (with *du* and with *Sie*). |
| 5 | `## What to listen for` | Two to four bullets, each pointing at one line of the scene. |
| 6 | `## Related articles` | Optional: other situations, a vocabulary pack. |

It has no phrase tables, no examples boxes, no Key points and no Common mistakes. Phrases and explanation belong to the how-to article it links. If a situation article starts explaining, the course has two how-to categories.

### Links run both ways, written once

A situation names the how-to articles it uses in its front matter, one to three, each at its own level or below:

```yaml
---
how-to:
  - /a1/how-to/introduce-yourself.md
  - /a1/how-to/say-hello-and-goodbye.md
myst:
  ...
---
```

The front matter is the only place the link is written. Two directives read it:

- `:::{how-to-links}` on the situation article draws a box titled *How to* that links each article it names.
- `:::{situations}` on a how-to article draws a box titled *Situations* that links every situation article naming it, at any level. A situation of another level carries that level as a badge.

Neither directive takes options or a body. Neither list is written by hand, so neither goes stale when a situation is added.

### How-to articles

A how-to article with situations carries `:::{situations}` after its explanation (and after Prerequisites, when it has them) and drops `## When to use it`. A how-to article that no situation names yet keeps `## When to use it`. `ol validate` holds the two to the front matter: a how-to article named by a situation carries the box and not the section, and a box on an article no situation names is an error.

### Scenes come back

A scene may return at a higher level with harder language: *Paying at the checkout* at A1, *The wrong change* at B1. File names are unique within a level, not across levels.

## Consequences

- The engine gains the category, the template `situation-article.md`, its rules in `specs.yml` and its checks. The Introduction shows a card for each category the first level has, so a language without situations still passes.
- The engine gains the directives `situations` and `how-to-links` and their styles. The app imports tracks under `<level>/situations/`.
- A language repository adds `situations/index.md` to a level when it writes the first one, and lists it in the level's toctree after how-to.
- Situation tracks are store-ready on their own: *German at the Supermarket* is a title that sells.
