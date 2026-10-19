# Domain docs

How to use this repository's domain documentation before working in the code.

## Read these first

- **`CONTEXT.md`** at the repository root. The glossary says which word to use. Read it
  before naming anything.
- **`docs/adr/`** for the decisions behind the area you are about to work in, once there
  are any.
- **`ol/authoring/specs.yml`** for the limits the checks enforce, and
  **`ol/authoring/review-rubric.yml`** for what a reviewer judges instead.

There is one context, so there is no `CONTEXT-MAP.md` and no per-context glossary.

## Use the glossary's vocabulary

When your output names a domain concept (an issue title, a test name, a check message, a
proposal), use the term as `CONTEXT.md` defines it. Never write "workspace" for a language
repository or "audio example" for an example.

If a concept you need is not in the glossary, either you are inventing language the project
does not use, or there is a real gap worth recording.

## Flag conflicts rather than overriding them

If what you are proposing contradicts a decision record or an article of `CONSTITUTION.md`,
say so explicitly and argue the case. Do not quietly work around it.
