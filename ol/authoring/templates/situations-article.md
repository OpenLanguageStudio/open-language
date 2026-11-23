<!-- TEMPLATE: situation article (one everyday scene, heard)
     Decision: docs/adr/0002-situations-category.md
     FILENAME MUST BE ENGLISH kebab-case, from the title: at-a-party.md.
     The shape and every limit are in docs/reference/page-standard.md.
     A situation SHOWS a how-to goal reached. It teaches nothing itself: no
     phrase tables, no examples boxes, no Key points, no Common mistakes.
     If a line needs explaining, the explanation belongs in the how-to article.
     Replace {{PLACEHOLDERS}}; DELETE every template comment: no HTML comments
     may survive in the docs file.                                            -->
---
how-to:
  - /{{level_lc}}/how-to/{{how-to-article}}.md
myst:
  html_meta:
    description: "{{SEARCH_SNIPPET_160_CHARS_OR_FEWER}}"
    keywords: "{{language}}, {{level_lc}}, situations, {{PHRASINGS_A_LEARNER_WOULD_TYPE}}"
    "property=og:title": "{{ENGLISH_TITLE}}"
    "property=og:description": "{{SAME_AS_DESCRIPTION}}"
    "property=og:type": "article"
    author: "{{TITLE_FIELD_FROM_OPEN_LANGUAGE_YML}}"
---
<!-- how-to: ONE TO THREE how-to articles the scene puts to use, at this level
     or below. This list is the only place the link is written: the build draws
     it as the How to box on this page AND as the Situations box on each
     how-to article named here. Never write those links by hand.
     Each how-to article named here must carry ':::{situations}' in place of
     its '## When to use it' section (ol validate says so). -->

# {{ENGLISH_TITLE}}
<!-- The scene, in English, sentence case, five words or fewer: "At a party",
     "Paying at the checkout", "Checking in at a hotel". It is a scene, not a
     goal, so it does not finish "How to ...". No level, no category, no
     number. A scene may come back at a higher level with harder language:
     "Paying at the checkout" at A1, "The wrong change" at B1. -->

{{LEAD: one or two sentences, 20 to 50 words, setting the scene: who, where,
what is happening, and what the main presenter wants from it. Use the main
phrasing from keywords at least once.}}
<!-- Do NOT address the reader, and do not explain any German here. Open on
     the scene: "Lina has just moved to Freiburg, and her new colleague Deniz
     has invited her to a birthday party where she knows nobody."
     There is no explanation paragraph. -->

:::{how-to-links}
:::
<!-- REQUIRED, straight after the lead, with no options and no body. -->

## Hear it in practice

:::{audio-examples}
:track: {{level_lc}}/situations/{{track-name}}
:title: {{NATIVE_TITLE}}
:title-en: {{ENGLISH_TITLE}}
:mode: dialogue
:presenters: {{main presenter}}, {{other presenter}}

{{slug}}: {{Native line}}
: {{English translation}}
{{slug}}: {{Native line}}
: {{English translation}}

{{slug}}: {{Native line}}
: {{English translation}}
:::
<!-- REQUIRED. Mode dialogue (most scenes), correspondence (a written
     exchange: emails, letters) or passage (one voice: an announcement, a
     voicemail). Text messages are a dialogue.
     A dialogue has 6 to 20 lines. The first presenter listed is the person
     the scene follows: they speak the spoken title and appear on the right.
     A blank line ends an exchange.
     Write natural speech AT THE LEVEL: only the grammar and words of this
     level and of the how-to articles named in the front matter, so a learner
     who has read them follows every line. Keep the fillers real people use
     (na, also, ach so) and the small talk around the goal: a scene is more
     than its key phrases.
     A second block is allowed for a second version of the SAME scene, such
     as the same exchange with Sie instead of du. Then each block stands under
     its own H3 naming that version. A different scene is its own page. -->

## What to listen for

- {{One line of the scene, quoted in italics, and what it does: *Und was machst du so?* keeps small talk going after the names.}}
- {{Another line}}
<!-- Two to four bullets, 30 words or fewer each. Point at what is in the
     scene: a reply that changes register, a filler, a question turned back,
     how the conversation ends. Never a grammar lesson: link that instead. -->

## Related articles

- []({{/path.md}})
<!-- OPTIONAL. Links only: another situation, a vocabulary pack. The how-to
     articles are already in the How to box, so do not repeat them here.
     Leave the section out when it is empty. -->
