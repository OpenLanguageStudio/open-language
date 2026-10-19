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

{{2-3 sentences of plain prose: what the learner will be able to write, in what
real context, and the register (formal/informal).}}

## Example: {{Situation, e.g. "Accepting an invitation"}}

{{1-2 sentences setting the situation: who writes to whom, and why.}}

### Hear it in practice

:::{audio-examples}
:track: {{level_lc}}/writing/{{example-name}}
:title: {{NATIVE_TITLE}}
:title-en: {{ENGLISH_TITLE}}
:multiline:

{{Model text line 1}}
{{Model text line 2}}
: {{Translation line 1}}
: {{Translation line 2}}
:::
<!-- REQUIRED: one or more "## Example: <Situation>" sections, each with its
     own "### Hear it in practice" holding a complete at-level model text
     (~60-120 words) read aloud. Each block writes its own track, so give each
     a name of its own in :track: (see templates/audio-examples-block.md);
     :multiline: keeps the text's line breaks on the page and in the audio. -->

## Building blocks

| Purpose | {{Native language name}} | English |
|---|---|---|
| Greeting (formal) | {{…}} | {{…}} |
| {{purpose}} | {{phrase}} | {{translation}} |

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

## Related articles

- [{{Related pages}}]({{/path.md}})
