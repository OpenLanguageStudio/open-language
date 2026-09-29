<!-- TEMPLATE: index.md for docs/<level>/<category>/ (or a grammar subcategory).
     Replace {{PLACEHOLDERS}}; DELETE every template comment.
     TITLE: never include the CEFR level ("Grammar", not "A1 Grammar").
     ORDERING: concepts toctree order IS the learning sequence: deliberate.
     grammar toctrees use a LOGICAL order: noun system, verb system, sentence
     level, modifiers, other last. Grammar subcategory indexes MUST open with
     1-3 sentences explaining what the grammar concept group is.
     NO References/Additional-reading section here: external links live in the
     LEVEL index (templates/level-index.md). Nothing agent-facing, ever. -->
---
myst:
  html_meta:
    description: "{{ONE_SENTENCE: what this section covers at this level}}"
    keywords: "{{language}}, {{level_lc}}, {{category}}, {{keywords}}"
---

# {{TITLE: e.g. "Grammar", "Concepts", or subcategory "Articles"}}

{{1-3 sentences: what this section is and how to use it. For grammar: "reference,
not sequenced". For concepts: "work through in order: each builds on the last."}}

```{toctree}
:maxdepth: 1

{{article-file-basename-no-extension}}
{{next-article}}
```
