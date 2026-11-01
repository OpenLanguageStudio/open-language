<!-- TEMPLATE: vocabulary article (one theme, 10 to 15 new words, or up to 20
     in a pack built on a word class)
     English kebab-case filename with a running number (at-the-beach-1): the
     next pack on the theme continues it.
     The shape and every limit are in docs/reference/page-standard.md.
     Replace {{PLACEHOLDERS}}; DELETE every template comment. -->
---
myst:
  html_meta:
    description: "{{SEARCH_SNIPPET_160_CHARS_OR_FEWER}}"
    keywords: "{{language}}, {{level_lc}}, vocabulary, {{PHRASINGS_A_LEARNER_WOULD_TYPE}}"
    "property=og:type": "article"
    author: "{{TITLE_FIELD_FROM_OPEN_LANGUAGE_YML}}"
---

# {{ENGLISH_TITLE: the theme, with no number}}

{{LEAD: one or two sentences, 20 to 50 words: the theme, using the main phrasing
from keywords at least once.}}

{{EXPLANATION: 40 to 120 words: why these words go together. Write every
technical term in it as {term}`term`.}}

## The words

| Word | Notes |
|---|---|
| {stack}`{{word}} \| {{translation}}` | {{plural, gender or use}} |
<!-- One table of 10 to 15 words, or up to 20 in a pack built on a word class.
     Two columns: the stack role shows the translation beneath the word. -->

## {{OTHER_SECTION_HEADING_ENGLISH: e.g. "Words that look alike"}}

{{OPTIONAL: zero to two sections of this kind.}}

## Hear it in practice

:::{audio-examples}
:track: {{level_lc}}/vocabulary/{{track-name}}
:title: {{NATIVE_TITLE}}
:title-en: {{ENGLISH_TITLE}}

{{Native sentence 1}}
: {{English translation 1}}
:::
<!-- REQUIRED: every word of the pack appears in a sentence. The block writes
     the track this page names (see templates/audio-examples-block.md). -->

## Summary

{{What the pack comes to, in a sentence or two.}}

## Related articles

- [{{Related pages}}]({{/path.md}})
<!-- Links only. Leave the section out when it is empty. -->
