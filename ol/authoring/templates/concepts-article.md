<!-- TEMPLATE: concepts article (functional ability, ORDERED curriculum)
     Gold exemplar: german/docs/a1/concepts/introducing-yourself.md
     FILENAME MUST BE ENGLISH kebab-case (reusable across languages).
     Replace {{PLACEHOLDERS}}; DELETE every template comment: no HTML comments
     may survive in the docs file.                                            -->
---
myst:
  html_meta:
    description: "{{LEVEL_LC}} concept: {{ENGLISH_TITLE_LC}}: {{ONE_SENTENCE_SUMMARY_MAX_155_CHARS}}"
    keywords: "{{language}}, {{level_lc}}, concepts, {{TOPIC_KEYWORDS}}"
    "property=og:title": "{{ENGLISH_TITLE}}"
    "property=og:description": "{{SAME_AS_DESCRIPTION}}"
    "property=og:type": "article"
    author: "{{TITLE_FIELD_FROM_OPEN_LANGUAGE_YML}}"
---

# {{ENGLISH_TITLE}}

:::{admonition} Prerequisites
:class: note
Before reading this article, make sure you are comfortable with:
- [{{LEVEL}} > Grammar > {{PREREQ}}]({{/level/grammar/subcat/file.md}})
:::
<!-- CONDITIONAL: only when the concept truly cannot be used without that
     grammar (e.g. Polite Requests needs Konjunktiv II). Otherwise put grammar
     links in Related articles. -->

{{1-3 sentences: the functional ability in plain English.}}
<!-- Do NOT address the reader. No "After this page you can …", no "you will
     learn …", no "Learn how to …" either: any stock opener becomes the phrase
     every article starts with, which is the problem. Open on the CONTENT:
     the situation ("A cafe visit runs on a small, predictable script: …"),
     the pattern ("A German self-introduction rests on four sentences: …"),
     or the key word ("Weather talk costs almost nothing to learn: … es").
     Direct "you" is reserved for admonitions and example translations. -->
<!-- Vary the opening move between articles. Read the two neighbours in the
     toctree before writing this paragraph. -->
<!-- Rule 17 still applies: the learner phrasings in html_meta.keywords must
     each appear somewhere in the body prose. -->



## When to use it

- {{situation 1}}
- {{situation 2}}
- {{situation 3}}

## Key phrases

| {{Native language name}} | English | Notes |
|---|---|---|
| {{phrase}} | {{translation}} | {{register/usage note}} |
<!-- 5-10 rows. These are the chunks the learner memorises. -->

---

## {{STEP_SECTION_HEADING_ENGLISH: e.g. "Saying who you are"}}

{{Short explanation}}

**Examples:**

:::{div} ol-examples
{{Native sentence}}
: {{English translation}}

{{Native sentence 2}}
: {{English translation 2}}
:::
<!-- 1-3 step sections that build the ability incrementally, 3-6 pairs each. -->

---

## Register and tone

{{OPTIONAL: formal/informal guidance, what natives actually say}}

## Hear it in practice

:::{audio-examples}
:album: {{level_lc}}/concepts/{{album_name}}
:title: {{NATIVE_TITLE}}
:title-en: {{ENGLISH_TITLE}}

{{Native sentence 1}}
: {{English translation 1}}
:::
<!-- REQUIRED, in this position: before Summary, with the ## Hear it in practice heading so
     it shows in the sidebar. The block IS the track (ADR-0006, see
     templates/audio-examples-block.md); register the track name in album.yml. -->

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
<!-- NEVER link the previous/next concept. Sphinx generates that navigation from the
     toctree and the theme renders it in the page footer. Manual neighbour links are
     duplicate, and they rot the moment the curriculum order changes. Related articles
     is for NON-adjacent links only: supporting grammar, a concept elsewhere in the
     sequence, a vocabulary pack. -->
