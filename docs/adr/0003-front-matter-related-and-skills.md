# 3. Related links and skills live in front matter

- **Status:** Accepted.

## Context

An article's related links were written twice over. Authors wrote a `## Related articles` list by hand, and ADR 2 added two boxes, `situations` and `how-to-links`, that the build filled from the situations' `how-to:` front matter. A reader met up to three separate link lists at the foot of a page, and an author had to know which of them to write and which the build drew.

A level page's "What learners know" and "What learners can do" were hand-written bullets with no identity. Nothing tied an article to the skill it teaches, so no check, and no consumer of the pages, could say which articles cover which skills.

## Decision

Front matter is the one source of both.

- **Related links.** An article lists `related:`, page paths without `.md`, relative to its folder or from the root with a leading `/`. The build draws them as the last section, `## Related articles`, with one group for each kind of page, in the category order how-to, situations, grammar, writing, vocabulary, and pages of no category last under "More". Links keep the author's order within a group.
- **The boxes are folded in.** The links the two boxes drew now appear in the same section: the situations naming a how-to article, and the how-to articles a situation names. The directives stay readable so existing pages build, but they draw nothing where the section is drawn, and `ol validate` asks for their removal.
- **A missing page fails the build.** An entry that names no page, ends in `.md` or is not a list of strings is an error, and the build stops. A related link that quietly disappears is worse than a build that fails.
- **Skills.** A level page lists its skills once in `skills:`, each with an `id`, a `kind` of `know` or `can`, and a `text`. The `skills` directive draws them under the level page's two sections, and the existing limits on bullets apply to the texts. An article names one or two skill ids in its own `skills:`, and `ol validate` holds each to the level page's list.
- **Tags.** A repository may list its allowed tags in `track-tags.yml`. When it does, blocks that write a track and articles carry tags from it.

### Transition

Content migrates page by page, so the rules separate what is unfinished from what is wrong.

- A page that has the older form alone passes with a warning: a hand-written `## Related articles` section, hand-written bullets on a level page, a box, an article with no `skills:` or `tags:`.
- A page that mixes the two forms fails: `related:` together with a hand-written section, or `related:` together with a box. The build also warns about the first. A page that holds both cannot say which is the truth.
- A build never warns about an unfinished page, because a language repository builds with warnings as errors. Only `ol validate` does.

## Consequences

- An author writes each link once, in front matter, and a reader meets one list.
- Moving a page, or adding a situation, changes the links of the pages it touches, and the build writes those pages again.
- A repository that has migrated can ask which articles teach a skill, because the ids are on both sides.
- Content that passed before this change still passes, with warnings, until it adopts `related:`. A page that adopts it and keeps a hand-written section or a box fails.
