<!-- TEMPLATE: vocabulary article (one theme, 10 to 15 new words, or up to 20
     in a pack built on a word class)
     English kebab-case filename with a running number (at-the-beach-1): the
     next pack on the theme continues it.
     The shape and every limit are in docs/reference/page-standard.md.
     Replace {{PLACEHOLDERS}}; DELETE every template comment.
     FRONT MATTER: 'related:' lists page paths without .md, from the root with
     a leading / or relative to this folder. The build draws them as the last
     section, grouped by kind: write no '## Related articles' section. Only
     pages the reader would not reach by the next-page link, and no other
     article of this subcategory. 'skills:' names one or two skill ids of the
     level page. 'tags:' comes from track-tags.yml. Leave a key out when the
     repository does not use it yet.
-->
---
related: ["{{/level/category/page: a page to read next, without .md}}"]
skills: ["{{skill-id: an id from the level page's skills, one or two}}"]
tags: ["{{tag: from track-tags.yml}}"]
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
