<!-- TEMPLATE: index.md for <level>/ (the level overview page).
     Replace {{PLACEHOLDERS}}; DELETE every template comment.
     The H1 is the bare level name: the one place the CEFR level appears in a title.
     The lead and the two lists total 150 words or fewer. The page makes no claim
     about an exam, and may cite the Council of Europe descriptors, which are public.
     The toctree lists only these category indexes, in this order. Leave out a
     category the level does not have; never add another entry.
     "Additional reading" holds learner-facing external links only: no private
     files, no agent-facing wording. -->
---
html_theme.sidebar_secondary.remove:
---

# {{LEVEL: e.g. A1}}

{{Lead of 40 words or fewer: where the level sits in the CEFR and where it starts.}}

## What learners know

- {{3 to 5 bullets of 15 words or fewer: what the course has taught by the end of the level, in plain words.}}

## What learners can do

- {{4 to 6 bullets of 15 words or fewer, each starting with a verb in its base form, each something a learner could be asked to do and a listener could judge.}}

```{toctree}
:maxdepth: 2

{{concepts/index: when the category exists}}
{{grammar/index: when the category exists}}
{{writing/index: when the category exists}}
{{vocabulary/index: when the category exists}}
```

## Additional reading

- [{{Source name}}]({{URL}}): {{one-line learner-facing description}}
