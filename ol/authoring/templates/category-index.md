<!-- TEMPLATE: index.md for <level>/<category>/ (or a grammar subcategory).
     Replace {{PLACEHOLDERS}}; DELETE every template comment.
     TITLE: the bare category name, the one the sidebar shows: "How to",
     "Grammar", "Writing" or "Vocabulary". A grammar subcategory takes its own
     name, such as "Articles".
     ORDERING: how-to articles are read in any order, so the index never says
     to work through them in sequence. Grammar toctrees use a LOGICAL order: noun system, verb system, sentence
     level, modifiers, other last.
     NO :numbered: on a toctree: the sidebar shows no section numbers.
     SUBCATEGORIES: a category index whose toctree lists subcategories, such as
     A1 Grammar, hides its toctree and shows a card per subcategory below it,
     in the toctree's order. A flat category index, and a subcategory index,
     shows its toctree as the list of its articles, and has no cards.
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
<!-- With subcategories, add :hidden: to the toctree and follow it with:

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} {{Subcategory title, as its index page's H1}}
:link: {{subcategory}}/index
:link-type: doc

{{One sentence of 15 words or fewer.}}
:::
::::
-->
