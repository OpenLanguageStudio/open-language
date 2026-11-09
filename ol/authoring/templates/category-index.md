<!-- TEMPLATE: index.md for <level>/<category>/ (or a grammar subcategory).
     Replace {{PLACEHOLDERS}}; DELETE every template comment.
     TITLE: the bare category name, the one the sidebar shows: "How to",
     "Grammar", "Writing" or "Vocabulary". A grammar subcategory takes its own
     name, such as "Articles".
     ORDERING: how-to articles are read in any order, so the index never says
     to work through them in sequence. Grammar toctrees use a LOGICAL order: noun system, verb system, sentence
     level, modifiers, other last.
     NO :numbered: on a toctree: the sidebar shows no section numbers.
     NO References/Additional-reading section here: external links live in the
     LEVEL index (templates/level-index.md). Nothing agent-facing, ever. -->
---
html_theme.sidebar_secondary.remove:
myst:
  html_meta:
    description: "{{ONE_SENTENCE: what this section covers at this level}}"
    keywords: "{{language}}, {{level_lc}}, {{category}}, {{keywords}}"
---

# {{TITLE: e.g. "Grammar", "How to", or subcategory "Articles"}}

{{1-3 plain sentences: what the articles here have in common.}}

```{toctree}
:maxdepth: 1

{{article-file-basename-no-extension}}
{{next-article}}
```
