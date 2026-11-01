<!-- TEMPLATE: concepts article (a goal a learner meets in real situations)
     Gold exemplar: german/a1/concepts/introducing-yourself.md
     FILENAME MUST BE ENGLISH kebab-case (reusable across languages).
     The shape and every limit are in docs/reference/page-standard.md.
     Replace {{PLACEHOLDERS}}; DELETE every template comment: no HTML comments
     may survive in the docs file.                                            -->
---
myst:
  html_meta:
    description: "{{SEARCH_SNIPPET_160_CHARS_OR_FEWER}}"
    keywords: "{{language}}, {{level_lc}}, concepts, {{PHRASINGS_A_LEARNER_WOULD_TYPE}}"
    "property=og:title": "{{ENGLISH_TITLE}}"
    "property=og:description": "{{SAME_AS_DESCRIPTION}}"
    "property=og:type": "article"
    author: "{{TITLE_FIELD_FROM_OPEN_LANGUAGE_YML}}"
---

# {{ENGLISH_TITLE}}
<!-- English, sentence case, five words or fewer. No level, no category, no
     number. -->

{{LEAD: one or two sentences, 20 to 50 words: what the page covers in plain
words, using the main phrasing from keywords at least once.}}

{{EXPLANATION: 40 to 120 words: the one idea of the page in plain language.
Write every technical term in it as {term}`term`. Lead and explanation together
are 180 words or fewer.}}
<!-- Do NOT address the reader. No "After this page you can ...", no "you will
     learn ...", no "Learn how to ..." either: any stock opener becomes the
     phrase every article starts with, which is the problem. Open on the
     CONTENT: the situation ("A cafe visit runs on a small, predictable script:
     ..."), the pattern ("A German self-introduction rests on four sentences:
     ..."), or the key word ("Weather talk costs almost nothing to learn: ...
     es"). Direct "you" is reserved for admonitions and example translations. -->
<!-- Vary the opening move between articles. Read the two neighbours in the
     toctree before writing this paragraph. -->

:::{admonition} Prerequisites
:class: note
Before reading this article, make sure you are comfortable with:
- [{{LEVEL}} > Grammar > {{PREREQ}}]({{/level/grammar/subcat/file.md}})
:::
<!-- CONDITIONAL: at most 3 links, and only when the concept truly cannot be
     used without that grammar (e.g. Polite Requests needs Konjunktiv II).
     Otherwise put grammar links in Related articles. -->

## When to use it

- {{situation 1}}
- {{situation 2}}
- {{situation 3}}

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
     `\|`. These are the chunks the learner memorises. -->

## {{OTHER_SECTION_HEADING_ENGLISH: e.g. "Formal or casual"}}

{{Short explanation}}

**Examples:**

:::{div} ol-examples
{{Native sentence}}
: {{English translation}}

{{Native sentence 2}}
: {{English translation 2}}
:::
<!-- Zero to three sections of this kind, with no H3s. -->

## Culture note

{{OPTIONAL: 80 words or fewer.}}

## Hear it in practice

:::{audio-examples}
:track: {{level_lc}}/concepts/{{track-name}}
:title: {{NATIVE_TITLE}}
:title-en: {{ENGLISH_TITLE}}

{{Native sentence 1}}
: {{English translation 1}}
:::
<!-- REQUIRED, in this position: before Summary. The heading puts the section
     in the on-this-page navigation. The block writes the track this page names
     (see templates/audio-examples-block.md). -->

## Summary

:::{admonition} Key points
:class: note

- {{key point 1}}
- {{key point 2}}
:::

:::{admonition} Common mistakes
:class: caution

- *{{Wrong}}* → {{Right}}. ({{why}})
:::

## Related articles

- [{{LEVEL}} > Grammar > {{SUPPORTING_GRAMMAR}}]({{/path.md}})
<!-- Links only. NEVER link the previous/next concept: Sphinx generates that
     navigation from the toctree and the theme renders it in the page footer.
     Related articles is for NON-adjacent links only: supporting grammar, a
     concept elsewhere in the sequence, a vocabulary pack. Leave the section out
     when it is empty. -->
