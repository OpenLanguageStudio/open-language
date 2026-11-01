<!-- TEMPLATE: grammar article (reference style, no learning order)
     Gold exemplar: german/a1/grammar/articles/bestimmter-artikel.md
     The shape and every limit are in docs/reference/page-standard.md.
     Replace all {{PLACEHOLDERS}}; DELETE every template comment: no HTML
     comments may survive in the docs file (they leak into built HTML).      -->
---
myst:
  html_meta:
    description: "{{SEARCH_SNIPPET_160_CHARS_OR_FEWER}}"
    keywords: "{{language}}, {{level_lc}}, grammar, {{PHRASINGS_A_LEARNER_WOULD_TYPE}}"
    "property=og:title": "{{NATIVE_NAME}}: {{ENGLISH_TITLE}}"
    "property=og:description": "{{SAME_AS_DESCRIPTION}}"
    "property=og:type": "article"
    author: "{{TITLE_FIELD_FROM_OPEN_LANGUAGE_YML}}"
---

# {{ENGLISH_TITLE}}
<!-- English, sentence case, five words or fewer: "Definite articles".
     No level, no category, no number. NO blockquote subtitle. -->

{{LEAD: one or two sentences, 20 to 50 words: what the page covers in plain
words, using the main phrasing from keywords at least once.}}

{{EXPLANATION: 40 to 120 words: the one idea of the page in plain language.
Write every technical term in it as {term}`term`. Lead and explanation together
are 180 words or fewer.}}
<!-- Do NOT address the reader. Write about the grammar, not about the reader
     or the page: "The dative marks to whom something happens", not "The dative
     lets you say to whom something happens". Direct "you" belongs in
     admonitions and example translations. -->

:::{admonition} Prerequisites
:class: note
Before reading this article, make sure you are comfortable with:
- [{{LEVEL}} > Grammar > {{PREREQ_TITLE}}]({{/level/grammar/subcat/file.md}})
:::
<!-- CONDITIONAL: at most 3 links, true dependencies only. When in doubt, OMIT
     and use Related articles instead. -->

## {{FORM_SECTION: the question it answers, e.g. "The forms: *der*, *die*, *das*"}}
<!-- One to three H2s on how the structure is built, then one to three on when
     and why it is used, then an optional one on the structure learners confuse
     it with. Five at most in all. A heading is 8 words or fewer, has no number
     and no closing punctuation, and puts words in the language taught in
     italics. Split one H2 with H3s only for parallel forms. -->

{{EXPLANATION: 1-3 sentences plain English; use a table for paradigms}}

| | Masculine | Feminine | Neuter | Plural |
|---|---|---|---|---|
| {{English row label}} | | | | |
<!-- A table of forms has at most 5 columns. Any other table has at most 3. -->

**Examples:**

:::{div} ol-examples
{{Native sentence, roles/bold marking ONLY the teaching focus, e.g. Ich sehe {akk}`den` Turm.}}
: {{English translation}} {{(optional short note in parentheses)}}

{{Native sentence 2}}
: {{English translation 2}}
:::
<!-- At most 3 pairs per section. Definition list inside the ol-examples div:
     native = term, English = definition. No bullet lists for example pairs. -->

## {{USE_SECTION: e.g. "When to use *der*, *die*, *das*"}}

{{EXPLANATION}}

:::{note}
{{OPTIONAL: one nuance/contrast; prefer one admonition per section max (tip/note/warning)}}
:::

:::{admonition} Common mistakes
:class: caution

- *{{Wrong sentence with \* marking the error}}* → {{Correct form in bold}}. ({{one-line why}})
:::
<!-- REQUIRED, in the last body section: the mistakes actually made at this level. -->

## Hear it in practice

:::{audio-examples}
:track: {{level_lc}}/grammar/{{track-name}}
:title: {{NATIVE_TITLE}}
:title-en: {{ENGLISH_TITLE}}

{{Native sentence 1}}
: {{English translation 1}}

{{Native sentence 2}}
: {{English translation 2}}
:::
<!-- REQUIRED, in this position: after the learning sections, before Summary.
     The heading puts the section in the on-this-page navigation. The block
     writes the track this page names (see templates/audio-examples-block.md):
     ordered plain-text pairs, best first, over-author ~12-18.
     With several blocks here, each may sit under its own H3 naming that track,
     so on-this-page reaches it. Every block then has an H3, and they count
     towards the article's 6. -->

## Summary

:::{admonition} Key points
:class: note

- {{key point 1}}
- {{key point 2}}
- {{key point 3}}
:::

## Related articles

- [{{LEVEL}} > Grammar > {{RELATED}}]({{/path.md}})
<!-- Links only, none the reader would reach by the next-page link. In a
     subcategory such as a1/grammar/articles/, no other article of that
     subcategory: its index links them all. Leave the section out when it is
     empty. Same-level links encouraged; cross-level only DOWN. Only existing
     files. -->
