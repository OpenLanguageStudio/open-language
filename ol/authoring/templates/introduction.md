<!-- TEMPLATE: index.md at the top level (the Introduction page).
     Replace {{PLACEHOLDERS}}; DELETE every template comment.
     The H1 is exactly "Introduction". The sections below are the only ones, in
     this order, and the page is 350 words or fewer. This page holds the site
     menu: one hidden toctree listing how_to_use, terminology and contributing
     in that order, then every level from a1/index to b2/index that exists.
     Nothing else goes in the toctree. -->
---
html_theme.sidebar_secondary.remove:
myst:
  html_meta:
    description: "{{ONE_SENTENCE: what this coursebook is}}"
    keywords: "{{language}}, {{language}} learning, {{language}} grammar, a1, a2, b1, b2"
---

# Introduction

{{Lead of 60 words or fewer: what this coursebook is, who it is for, and that it
is free and open.}}

## How the course works

{{80 words or fewer: that the pages are not a sequence, that any page can be
read first, and that each ends with sentences to listen to.}}

## Levels

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} {{LEVEL}}
:link: {{level}}/index
:link-type: doc

{{One sentence of 20 words or fewer: what the level covers.}}
:::
::::
<!-- One card per level that exists, in order, each linking to its level page.
     A card's title is the title of the page it opens. -->

## Categories

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} How to
:link: {{first_level}}/how-to/index
:link-type: doc

{{One sentence of 25 words or fewer: what to say in a situation.}}
:::

:::{grid-item-card} Situations
:link: {{first_level}}/situations/index
:link-type: doc

{{Everyday scenes to listen to.}}
:::

:::{grid-item-card} Grammar
:link: {{first_level}}/grammar/index
:link-type: doc

{{How the language is built.}}
:::

:::{grid-item-card} Writing
:link: {{first_level}}/writing/index
:link-type: doc

{{Model texts for everyday tasks.}}
:::

:::{grid-item-card} Vocabulary
:link: {{first_level}}/vocabulary/index
:link-type: doc

{{Word packs on one theme.}}
:::
::::

## Where to start

- {{New to the language}}: [{{link text}}]({{level}}/index.md)
- {{A single problem}}: [{{link text}}]({{path.md}})
- {{An unfamiliar term}}: [the glossary](terminology.md)
<!-- Two to four bullets, each pairing a situation with a link. The last always
     links to the glossary. -->

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
