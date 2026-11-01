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

- [{{LEVEL}}]({{level}}/index.md): {{what it covers, 20 words or fewer}}
<!-- One bullet per level that exists, each linking to its level page. -->

## Categories

- [Concepts]({{first_level}}/concepts/index.md): {{what to say in a situation, 25 words or fewer}}
- [Grammar]({{first_level}}/grammar/index.md): {{how the language is built}}
- [Writing]({{first_level}}/writing/index.md): {{model texts for everyday tasks}}
- [Vocabulary]({{first_level}}/vocabulary/index.md): {{word packs on one theme}}

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
