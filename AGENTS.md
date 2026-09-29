# AGENTS.md

Authoring tools for Open Language coursebooks: the `ol` CLI, the Sphinx extensions under `ol/docs/`, and the template validator under `ol/authoring/`. Nothing here is language-specific; each language is a separate workspace repository that installs this package.

## Commands

- Install: `uv sync`
- Test: `uv run pytest`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Build: `uv build`

## CI checks

`Lint`, `Test` and `Build` run on every pull request into `main` and on pushes to `main` (`.github/workflows/ci.yml`).

## Rules for changes

- A validator rule ships with a test in `ol/tests/test_validate.py` that breaks the fixture article and asserts the rule's error. A rule nobody has seen fail is not trusted.
- Templates in `ol/authoring/templates/` and the rules in `ol/authoring/specs.yml` change together. A template section the validator does not require, or a required section the template lacks, is a bug.
- Text that reaches a reader (validator messages, templates, docs) uses no em dashes.
- This package must never depend on audio or text-to-speech libraries. Audio production lives elsewhere and builds on this package, not the reverse.
