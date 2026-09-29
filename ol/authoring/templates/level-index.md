<!-- TEMPLATE: index.md for docs/<level>/ (the level landing page).
     Replace {{PLACEHOLDERS}}; DELETE every template comment.
     The H1 is the bare level name: the one place the CEFR level appears in a title.
     This page carries the level's "Additional reading" (learner-facing external
     links only: no private files, no agent-facing wording). -->
---
html_theme.sidebar_secondary.remove:
---

# {{LEVEL: e.g. A1}}

```{toctree}
:maxdepth: 2

grammar/index
concepts/index
{{writing/index: when the category exists}}
{{topics/index: when the category exists}}
{{situations/index: when the category exists}}
```

## Additional reading

External resources that complement this level.

- [{{Source name}}]({{URL}}): {{one-line learner-facing description}}
