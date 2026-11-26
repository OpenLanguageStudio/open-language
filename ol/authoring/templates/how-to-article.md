<!-- TEMPLATE: how-to article (a goal a learner meets in real situations)
     Gold exemplar: german/a1/how-to/introduce-yourself.md
     FILENAME MUST BE ENGLISH kebab-case (reusable across languages).
     The shape and every limit are in docs/reference/page-standard.md.
     Replace {{PLACEHOLDERS}}; DELETE every template comment: no HTML comments
     may survive in the docs file.
     FRONT MATTER: 'related:' lists page paths without .md, from the root with
     a leading / or relative to this folder. The build draws them as the last
     section, grouped by kind: write no '## Related articles' section. Only
     pages the reader would not reach by the next-page link, and no other
     article of this subcategory. 'skills:' names one or two skill ids of the
     level page. 'tags:' comes from track-tags.yml. Leave a key out when the
     repository does not use it yet.
     'target-title:' is the goal in the language taught, one line. The build
     draws it under the H1 as a subtitle, so no sentence names the goal in the
     language taught ("German calls it ..."). A how-to article without it is
     warned about.
-->
---
target-title: "{{NATIVE_TITLE: the goal in the language taught}}"
related: ["{{/level/category/page: a page to read next, without .md}}"]
skills: ["{{skill-id: an id from the level page's skills, one or two}}"]
tags: ["{{tag: from track-tags.yml}}"]
myst:
  html_meta:
    description: "{{SEARCH_SNIPPET_160_CHARS_OR_FEWER}}"
    keywords: "{{language}}, {{level_lc}}, how to, {{PHRASINGS_A_LEARNER_WOULD_TYPE}}"
    "property=og:title": "{{ENGLISH_TITLE}}"
    "property=og:description": "{{SAME_AS_DESCRIPTION}}"
    "property=og:type": "article"
    author: "{{TITLE_FIELD_FROM_OPEN_LANGUAGE_YML}}"
---

# {{ENGLISH_TITLE}}
<!-- English, sentence case, five words or fewer. No level, no category, no
     number. The title finishes the phrase "How to ...", so it opens on a verb
     in its base form: "Order food and drink", "Introduce yourself", never
     "Ordering food and drink". -->

{{LEAD: one or two sentences, 20 to 50 words: what the page covers in plain
words, using the main phrasing from keywords at least once.}}

{{OPTIONAL SECOND PARAGRAPH: 40 to 120 words: the one idea that organises the
page, such as "formal or informal decides the questions". It never previews the
sections below: explanation sits at the top of the section it explains. Link a
technical term to the article that covers it, or write it as {term}`term` when
no article does. Lead and this paragraph together are 180 words or fewer.
Delete it when the lead is enough.}}
<!-- Do NOT address the reader. No "After this page you can ...", no "you will
     learn ...", no "Learn how to ..." either: any stock opener becomes the
     phrase every article starts with, which is the problem. Open on the
     CONTENT: the situation ("A cafe visit runs on a small, predictable script:
     ..."), the pattern ("A German self-introduction rests on four sentences:
     ..."), or the key word ("Weather talk costs almost nothing to learn: ...
     es"). Direct "you" is reserved for admonitions and example translations. -->
<!-- Vary the opening move between articles. Read two other articles in the
     category before writing this paragraph. -->

:::{admonition} Prerequisites
:class: note
Before reading this article, make sure you are comfortable with:
- [{{Link text: the page's subject}}]({{/level/grammar/subcat/file.md}})
<!-- Every link has its own text: never [](...). A link to a
     page of another level is followed by that level as a badge:
     - [The passive](/b1/grammar/passiv.md) {level}`B1` -->
:::
<!-- CONDITIONAL: at most 3 links, and only when the goal truly cannot be
     used without that grammar (e.g. Polite Requests needs Konjunktiv II).
     Otherwise link the grammar in the sentence that needs it. -->

## When to use it

- {{situation 1}}
- {{situation 2}}
- {{situation 3}}
<!-- Keep this section until a situation names this page in its 'how-to:' front
     matter. From then on the build lists those situations under Related
     articles, and this section goes (ol validate says so).
     Concrete scenes, each one a situation article could be written for:
     "Meeting a new colleague at work", not "Meeting people". -->

## Key phrases

### {{Group name: the situation, e.g. "Saying hello"}}

| Phrase | Notes |
|---|---|
| {stack}`{{phrase}} \| {{translation}}` | {{register/usage note}} |

### {{Next group}}

| Phrase | Notes |
|---|---|
| {stack}`{{phrase}} \| {{translation}}` | {{register/usage note}} |
<!-- Two columns, so the table fits a phone: the stack role shows the
     translation beneath the phrase. Inside a table write the separator as
     `\|`. These are the chunks the learner memorises.
     A table earns its place through its Notes column. Phrases with nothing to
     note go in an ol-examples block instead, where they also play: a table
     whose Notes cells are all empty fails.
     Where the same phrases come formal and informal, show them in one tab set
     with an ol-examples block (or a table) in each tab:
     :::::{tab-set}
     ::::{tab-item} Formal (Sie)
     :::{ol-examples}
     ...
     :::
     ::::
     ::::{tab-item} Informal (du)
     ...
     ::::
     ::::: -->

## {{OTHER_SECTION_HEADING_ENGLISH: e.g. "Meeting someone at work"}}

{{One or two sentences that explain this section, just before its examples.
Link what needs its own explanation to the article that should hold it, in the
sentence where it comes up, even when that article is not written yet.}}

:::{ol-examples}
:presenters: {{presenter slug}}
{{Native sentence}}
: {{English translation}}

{{Native sentence 2}}
: {{English translation 2}}
:::

:::{culture-note}
{{OPTIONAL: 80 words or fewer, short and concrete. Wherever it fits in the
body, at most 3 on the page.}}
:::

:::{audio-examples}
:track: {{level_lc}}/how-to/{{track-name}}
:title: {{NATIVE_TRACK_TITLE}}
:title-en: {{ENGLISH_TRACK_TITLE}}

{{Native sentence 1}}
: {{English translation 1}}
:::
<!-- Zero to three sections of this kind, with no H3s. A track closes the
     section it practises: it is the section's last block. A page with a
     formal and an informal track gives each its own section and ends each
     with its track. Never write a track's title as a heading: the block draws
     its own. Write no '## Culture note' section: use the culture-note
     directive. -->

## Hear it in practice

:::{audio-examples}
:track: {{level_lc}}/how-to/{{track-name}}
:title: {{NATIVE_TITLE}}
:title-en: {{ENGLISH_TITLE}}

{{Native sentence 1}}
: {{English translation 1}}
:::
<!-- REQUIRED only when no body section ends in a track, and then in this
     position: before Summary. Delete it when the tracks close their sections.
     The block writes the track this page names (see
     templates/audio-examples-block.md). No H3s here: the blocks draw their
     own titles. -->

## Summary

:::{admonition} Key points
:class: note

- {{key point 1}}
- {{key point 2}}
:::

:::{admonition} Common mistakes
:class: caution

- *{{Wrong}}* → {{Right}}. ({{why}})
- *{{Wrong}}* → {{Right}}. ({{why}}, learn more in [{{Link text}}]({{/level/grammar/page.md}}))
:::
<!-- Only mistakes that learners with the reader's language really make.
     A mistake another article explains ends with a link to it. -->
