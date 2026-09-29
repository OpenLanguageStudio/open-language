<!-- TEMPLATE: writing article (one written genre/task, output-focused)
     v1: NO live exemplar exists yet. One genre per article (email to your
     boss, vacation postcard, replying to an invitation). English kebab-case
     filename. English headings only. Replace {{PLACEHOLDERS}}; DELETE every
     template comment. -->
---
myst:
  html_meta:
    description: "{{LEVEL_LC}} writing: {{ENGLISH_TITLE}}: structure, phrases and a model text for {{GENRE_SUMMARY}}."
    keywords: "{{language}}, {{level_lc}}, writing, {{KEYWORDS}}"
    "property=og:type": "article"
    author: "{{TITLE_FIELD_FROM_OPEN_LANGUAGE_YML}}"
---

# {{ENGLISH_TITLE: e.g. "Replying to an invitation"}}

:::{admonition} Prerequisites
:class: note
Before reading this article, make sure you are comfortable with:
- [{{Grammar this task truly depends on}}]({{/path.md}})
:::
<!-- CONDITIONAL: omit unless genuinely required. -->

## The task

{{2-3 sentences: what the learner will be able to write, and in what real context.
Note the register (formal/informal).}}

## Structure

1. {{Opening: greeting formula}}
2. {{Body point 1}}
3. {{Body point 2}}
4. {{Closing: sign-off formula}}

## Building blocks

| Purpose | {{Native language name}} | English |
|---|---|---|
| Greeting (formal) | {{…}} | {{…}} |
| {{purpose}} | {{phrase}} | {{translation}} |

## Model text

{{A complete at-level model text (~40-120 words), followed by an English
translation in italics or a collapsible block.}}

---

## Summary

:::{admonition} Key points
:class: note

- {{key point}}
:::

:::{admonition} Common mistakes
:class: caution

- {{typical error in this genre}} → {{fix}}
:::

---

:::{audio-examples}
:album: {{level_lc}}/writing/{{album_name}}
:title: {{NATIVE_TITLE}}
:title-en: {{ENGLISH_TITLE}}
:multiline:

{{Model text line 1}}
{{Model text line 2}}
: {{Translation line 1}}
: {{Translation line 2}}
:::
<!-- REQUIRED once a writing album exists for this level (the model text read
     aloud). The block IS the track (ADR-0006); :multiline: keeps the text's
     line breaks on the page and in the audio. Register the name in album.yml. -->

---

## Related articles

- [{{Related pages}}]({{/path.md}})
