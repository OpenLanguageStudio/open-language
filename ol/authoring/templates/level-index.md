<!-- TEMPLATE: index.md for <level>/ (the level overview page).
     Replace {{PLACEHOLDERS}}; DELETE every template comment.
     The H1 is the bare level name: the one place the CEFR level appears in a title.
     The lead and the two lists total 150 words or fewer. The page makes no claim
     about an exam, and may cite the Council of Europe descriptors, which are public.
     The toctree lists only these category indexes, in this order, and is
     hidden: the Categories cards show it, linking the same pages in the same
     order. Leave out a category the level does not have, and its card; never
     add another entry.
     SKILLS: the level's skills are written once, under 'skills:' in the front
     matter, and the two directives below draw them. Each skill has a unique
     id, a kind (know or can) and a text. The limits of the two lists apply to
     the texts. Write no bullets beside a directive.
     "Additional reading" holds learner-facing external links only: no private
     files, no agent-facing wording. -->
---
html_theme.sidebar_secondary.remove:
skills:
  - id: "{{level_lc}}-{{skill-name}}"
    kind: know
    text: "{{3 to 5 skills of kind know, each 15 words or fewer: what the course has taught by the end of the level, in plain words.}}"
  - id: "{{level_lc}}-{{skill-name}}"
    kind: can
    text: "{{4 to 6 skills of kind can, each 15 words or fewer, starting with a verb in its base form, each something a learner could be asked to do and a listener could judge.}}"
---

# {{LEVEL: e.g. A1}}

{{Lead of 40 words or fewer: where the level sits in the CEFR and where it starts.}}

## What learners know

:::{skills} know
:::

## What learners can do

:::{skills} can
:::

```{toctree}
:maxdepth: 2
:hidden:

{{how-to/index: when the category exists}}
{{situations/index: when the category exists}}
{{grammar/index: when the category exists}}
{{writing/index: when the category exists}}
{{vocabulary/index: when the category exists}}
```

## Categories

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} How to
:link: how-to/index
:link-type: doc

{{One sentence of 15 words or fewer on what the category's pages hold.}}
:::

:::{grid-item-card} Situations
:link: situations/index
:link-type: doc

{{One sentence.}}
:::

:::{grid-item-card} Grammar
:link: grammar/index
:link-type: doc

{{One sentence.}}
:::

:::{grid-item-card} Writing
:link: writing/index
:link-type: doc

{{One sentence.}}
:::

:::{grid-item-card} Vocabulary
:link: vocabulary/index
:link-type: doc

{{One sentence.}}
:::
::::

## Additional reading

- [{{Source name}}]({{URL}}): {{one-line learner-facing description}}
