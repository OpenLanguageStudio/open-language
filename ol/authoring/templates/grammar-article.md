<!-- TEMPLATE: grammar article (reference style, no learning order)
     Gold exemplar: german/docs/a1/grammar/artikel/bestimmter-artikel.md
     Detailed MyST/theme reference: open-language/.github/skills/grammar-article/
     Replace all {{PLACEHOLDERS}}; DELETE every template comment: no HTML
     comments may survive in the docs file (they leak into built HTML).      -->
---
myst:
  html_meta:
    description: "{{LEVEL_LC}} grammar: {{NATIVE_TOPIC_WORDS}}: {{ONE_SENTENCE_SUMMARY_MAX_155_CHARS}}"
    keywords: "{{language}}, {{language}} learning, {{level_lc}}, grammar, {{TOPIC_KEYWORDS_ENGLISH_AND_NATIVE}}"
    "property=og:title": "{{NATIVE_NAME}}: {{ENGLISH_TITLE}}"
    "property=og:description": "{{SAME_AS_DESCRIPTION}}"
    "property=og:type": "article"
    author: "{{TITLE_FIELD_FROM_OPEN_LANGUAGE_YML}}"
---

# {{ENGLISH_TITLE}}
<!-- Short English H1 (1-5 words): "Definite Articles", "The Dative Case".
     Article about ONE word → '"mit": Accompaniment and Transport'.
     NO blockquote subtitle. NO native-language-only titles. -->

:::{admonition} Prerequisites
:class: note
Before reading this article, make sure you are comfortable with:
- [{{LEVEL}} > Grammar > {{PREREQ_TITLE}}]({{/level/grammar/subcat/file.md}})
:::
<!-- CONDITIONAL: include ONLY when the reader genuinely cannot follow this
     page without the linked article. Grammar links only, one-way. When in
     doubt, OMIT and use Related articles instead. -->

{{INTRO_1_3_SENTENCES_PLAIN_ENGLISH: what this grammar does and when it turns up. No em dashes, anywhere, ever.}}
<!-- Do NOT address the reader. Write about the grammar, not about the reader
     or the page: "The dative marks to whom something happens", not "The dative
     lets you say to whom something happens"; "the familiar bracket", not "the
     bracket you already know"; "This page sets out …", not "This page shows
     you …". Direct "you" belongs in admonitions and example translations. -->



*Examples:*

- *{{ENGLISH_ONLY_EXAMPLE with the demonstrated feature in **bold**}}*
<!-- RARE: only when the concept is abstract enough to need pre-framing (e.g.
     passive voice, hypotheticals). Bold the exact feature being shown. Basic
     topics (articles, conjugation tables) get NO intro examples. Max 3. -->

## {{SECTION_HEADING_ENGLISH: native words only in italics, e.g. "The forms: *der*, *die*, *das*"}}
<!-- One H2 per genuinely distinct sub-rule. A short topic can be a single flow
     with no H2 sections at all: never invent sections to fill the template. -->

{{EXPLANATION: 1-3 sentences plain English; use a table for paradigms}}

| | Masculine | Feminine | Neuter | Plural |
|---|---|---|---|---|
| {{English row label}} | | | | |

**Examples:**

:::{div} ol-examples
{{Native sentence, roles/bold marking ONLY the teaching focus, e.g. Ich sehe {akk}`den` Turm.}}
: {{English translation}} {{(optional short note in parentheses)}}

{{Native sentence 2}}
: {{English translation 2}}
:::
<!-- 3-6 pairs per section. Definition list inside the ol-examples div:
     native = term, English = definition. No bullet lists for example pairs. -->

:::{note}
{{OPTIONAL: one nuance/contrast; prefer one admonition per section max (tip/note/warning)}}
:::

## Hear it in practice

:::{audio-examples}
:album: {{level_lc}}/grammar/{{album_name}}
:title: {{NATIVE_TITLE}}
:title-en: {{ENGLISH_TITLE}}

{{Native sentence 1}}
: {{English translation 1}}

{{Native sentence 2}}
: {{English translation 2}}
:::
<!-- REQUIRED, in this position: after the learning sections, before Summary.
     The ## Hear it in practice heading puts the section in the sidebar. The block IS the
     track (ADR-0006, see templates/audio-examples-block.md): ordered plain-text pairs,
     best first, over-author ~12-18; register the track name in album.yml. -->

## Summary

:::{admonition} Key points
:class: note

- {{key point 1}}
- {{key point 2}}
- {{key point 3}}
:::

:::{admonition} Common mistakes
:class: caution

- *{{Wrong sentence with \* marking the error}}* → {{Correct form in bold}}. ({{one-line why}})
:::
<!-- 3-6 mistakes actually made at this level. Key points ALWAYS before Common mistakes. -->

## Related articles

- [{{LEVEL}} > Grammar > {{RELATED}}]({{/path.md}})
<!-- Same-level links encouraged; cross-level only DOWN. Only existing files. -->
