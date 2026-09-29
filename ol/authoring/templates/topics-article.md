<!-- TEMPLATE: topics article (vocabulary theme, no ordering)
     Base exemplar: german/docs/b2/topics/smalltalk.md (pre-dates the 2026-07-09
     conventions: this template supersedes its formatting).
     English kebab-case filename. English headings only.
     Replace {{PLACEHOLDERS}}; DELETE every template comment. -->
---
myst:
  html_meta:
    description: "{{LEVEL_LC}} topic: {{ENGLISH_TITLE}}: vocabulary, phrases and examples for {{THEME_SUMMARY}}."
    keywords: "{{language}}, {{level_lc}}, topics, {{TOPIC_KEYWORDS}}"
    "property=og:type": "article"
    author: "{{TITLE_FIELD_FROM_OPEN_LANGUAGE_YML}}"
---

# {{ENGLISH_TITLE}}

{{INTRO_1_2_SENTENCES: what this theme covers and when it comes up}}
<!-- Do NOT address the reader in body prose. Direct "you" is for admonitions
     and example translations only. See SKILL.md rule 19. -->


## Vocabulary list

| {{Native language name}} | English |
|---|---|
| {{Noun, article-marked (e.g. "Anlass, der")}} | {{translation}} |
<!-- 20-40 rows at B-levels, 10-20 at A-levels. Nouns with article, verbs in
     infinitive; group loosely: nouns → verbs → adjectives → chunks. -->

## Useful phrases

| {{Native language name}} | English | Notes |
|---|---|---|
| {{phrase}} | {{translation}} | {{usage}} |

---

## {{OPTIONAL_SECTION_ENGLISH: short story / text using the vocabulary}}

{{A short at-level text (~100-200 words) using the vocabulary in context.}}

## {{OPTIONAL_SECTION_ENGLISH: dialogue}}

{{A short at-level dialogue. Receptive practice, not a production script.}}

---

## Summary

:::{admonition} Key points
:class: note

- {{key point}}
:::

---

:::{audio-examples}
:album: {{level_lc}}/topics/{{album_name}}
:title: {{NATIVE_TITLE}}
:title-en: {{ENGLISH_TITLE}}

{{Native sentence 1}}
: {{English translation 1}}
:::
<!-- REQUIRED once a topics album exists for this level. The block IS the
     track (ADR-0006, see templates/audio-examples-block.md). -->

---

## Related articles

- [{{Related grammar/concepts pages}}]({{/path.md}})
