<!-- TEMPLATE: situations article (receptive, "at the …" setting)
     v1: NO live exemplar exists yet. Derived from CONTEXT.md: receptive
     vocabulary and expressions the learner will HEAR in a specific real-world
     setting: not a dialogue script. English kebab-case filename. English
     headings only. Replace {{PLACEHOLDERS}}; DELETE every template comment. -->
---
myst:
  html_meta:
    description: "{{LEVEL_LC}} situation: {{ENGLISH_TITLE}}, what you'll hear and need to understand {{SETTING_PHRASE}}."
    keywords: "{{language}}, {{level_lc}}, situations, {{KEYWORDS}}"
    "property=og:type": "article"
    author: "{{TITLE_FIELD_FROM_OPEN_LANGUAGE_YML}}"
---

# {{ENGLISH_TITLE: e.g. "At the supermarket checkout"}}

## The situation

{{2-3 sentences: the setting, who speaks to you, what typically happens.}}

## What you will hear

:::{div} ol-examples
{{Typical utterance heard in this setting}}
: {{English translation}} ({{who says it}})

{{Utterance 2}}
: {{English translation 2}}
:::
<!-- 8-15 pairs. Receptive focus: things said TO the learner. -->

## Key vocabulary

| {{Native language name}} | English |
|---|---|
| {{word}} | {{translation}} |

## How to respond

:::{div} ol-examples
{{Minimal viable answer}}
: {{English translation}}
:::
<!-- 3-6 minimal responses. Keep production minimal: receptive category. -->

---

## Summary

:::{admonition} Key points
:class: note

- {{key point}}
:::

---

:::{audio-examples}
:album: {{level_lc}}/situations/{{album_name}}
:title: {{NATIVE_TITLE}}
:title-en: {{ENGLISH_TITLE}}

{{Native sentence 1}}
: {{English translation 1}}
:::
<!-- REQUIRED once a situations album exists for this level. The block IS the
     track (ADR-0006, see templates/audio-examples-block.md). -->

---

## Related articles

- [{{Related grammar/concepts/topics pages}}]({{/path.md}})
