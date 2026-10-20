<!-- TEMPLATE: index.md at the top level (the Introduction page).
     Replace {{PLACEHOLDERS}}; DELETE every template comment.
     The H1 is exactly "Introduction". This page holds the site menu: one
     toctree listing how_to_use, terminology and contributing in that order,
     then every level from a1/index to b2/index that exists. Nothing else goes
     in the toctree. -->
---
html_theme.sidebar_secondary.remove:
myst:
  html_meta:
    description: "{{ONE_SENTENCE: what this coursebook is}}"
    keywords: "{{language}}, {{language}} learning, {{language}} grammar, a1, a2, b1, b2"
---

# Introduction

{{1-2 paragraphs: what this coursebook is, who it is for, and that it is free
and open.}}

## Levels

{{The levels it covers, A1 to B2, and what a learner can do at the end of each.}}

## Categories

{{The four categories every level holds: concepts (what to say in a
situation), grammar (how the language is built), writing (model texts for
everyday tasks) and vocabulary (word packs on one theme).}}

```{toctree}
:maxdepth: 2
:hidden:

how_to_use
terminology
contributing
a1/index
a2/index
b1/index
b2/index
```
