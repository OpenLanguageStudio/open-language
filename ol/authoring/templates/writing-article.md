<!-- TEMPLATE: writing article (one everyday scenario, in one register)
     One genre per article (email to your boss, vacation postcard, replying to
     an invitation). English kebab-case filename, numbered per register family
     (email-formal-1). English headings only.
     The shape and every limit are in docs/reference/page-standard.md.
     Replace {{PLACEHOLDERS}}; DELETE every template comment. -->
---
myst:
  html_meta:
    description: "{{SEARCH_SNIPPET_160_CHARS_OR_FEWER}}"
    keywords: "{{language}}, {{level_lc}}, writing, {{PHRASINGS_A_LEARNER_WOULD_TYPE}}"
    "property=og:type": "article"
    author: "{{TITLE_FIELD_FROM_OPEN_LANGUAGE_YML}}"
---

# {{ENGLISH_TITLE: e.g. "Replying to an invitation"}}

{{LEAD: one or two sentences, 20 to 50 words: what the text type is, using the
main phrasing from keywords at least once.}}

{{EXPLANATION: 40 to 120 words: when the text is needed and the register it is
written in. Write every technical term in it as {term}`term`.}}

:::{admonition} Prerequisites
:class: note
Before reading this article, make sure you are comfortable with:
- [{{Grammar this task truly depends on}}]({{/path.md}})
:::
<!-- CONDITIONAL: at most 3 links, omit unless genuinely required. -->

## Example: {{Situation, with a capital: "Accepting an invitation"}}

{{1-2 sentences setting the situation: who writes to whom, and why.}}

> {{The model text, with its line breaks}}

{{A note of 60 words or fewer on why it works.}}

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
<!-- One or two "## Example: <Situation>" sections, each with its own
     "### Hear it in practice" holding a complete at-level model text of 60
     words or more, read aloud. Each block writes its own track, so give each a
     name of its own in :track: (see templates/audio-examples-block.md);
     :multiline: keeps the text's line breaks on the page and in the audio. -->

## Building blocks

| Phrase | Notes |
|---|---|
| {stack}`{{phrase}} \| {{translation}}` | {{where it goes in the text}} |

## Summary

:::{admonition} Key points
:class: note

- {{key point}}
:::

:::{admonition} Common mistakes
:class: caution

- {{typical error in this genre}} → {{fix}}
:::

## Related articles

- [{{Related pages}}]({{/path.md}})
<!-- Links only. Leave the section out when it is empty. -->
