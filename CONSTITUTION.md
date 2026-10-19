# Open Language Constitution

How the code in this repository is written. Read when planning a change and when
reviewing one.

## Core articles

### Article I — Testing
Every change follows [`docs/contributing/standards/testing.md`](docs/contributing/standards/testing.md): what gets a test
and what does not, the test-first cycle, test structure and fixtures, and the coverage floors.

### Article II — Simplicity
Start with the simplest design that satisfies the need. New dependencies, new abstractions,
and new infrastructure each require a stated justification. YAGNI over speculation.

### Article III — Anti-Abstraction
No wrapper layers, base classes, or "future-proofing" indirection without a present, concrete
second use. Prefer duplication over the wrong abstraction.

### Article IV — Integration-First
Contracts and integration points are designed and tested before internals are polished.
Acceptance scenarios exercise the package the way a language repository uses it: through
`ol check`, `ol validate` and a Sphinx build.

### Article V — Security & data-safety
Article text is untrusted input. It is parsed, never executed, and nothing in an article
decides which code runs or which file is read outside the language repository. Values
written into rendered HTML are escaped through docutils or Jinja, never built by string
interpolation. Secrets never appear in code, fixtures or version control.

### Article VI — Documentation
Public changes ship their docs in the same pull request: the README and `CHANGELOG.md`.
Docstrings and code comments follow
[`docs/contributing/standards/code-documentation.md`](docs/contributing/standards/code-documentation.md), and
the README's quickstart follows
[`docs/contributing/standards/documentation.md`](docs/contributing/standards/documentation.md).
The README carries a Scope & philosophy section.

### Article VII — Dependency discipline
A new runtime dependency requires a stated justification. Language repositories install
this package, so every dependency it adds is one they carry too.

### Article VIII — Cohesion (Python)
Related behaviour is grouped in a class, not scattered across module-level functions.

**The test:** two or more module-level functions that share a *subject* belong on a class.
They share a subject when they operate on the same data, take the same first argument, are
only meaningful in sequence, or are named around the same noun (`build_x`, `validate_x`,
`render_x`).

**Why.** A class is the extension point. Someone who needs different behaviour subclasses it
and overrides one method. A module of functions can only be monkey-patched, which is not a
supported interface and breaks on any internal change.

**Shape:** shared state or configuration → a regular class holding it. Grouping with no
shared state → still a class, with `@classmethod`/`@staticmethod`, or a small frozen
dataclass carrying the config. A module-level convenience function is only ever a thin
wrapper over the class.

**Framework first.** Where Sphinx, docutils or Typer already owns the grouping (a
`Directive`, a role function, a Typer command), use it rather than inventing a class.

**Exceptions:** a genuinely standalone pure function with no siblings; framework-dictated
shapes (`conftest.py` fixtures, Sphinx `setup()` hooks, CLI entry points); a module of
independent utilities that share no subject.

**This does not license abstraction.** Article III still holds.

## Project articles

### Article IX — One definition of the content standard
A rule a language repository is held to is written once, in this package, and the Open
Language app reads blocks through the same code. A rule is never restated in a language
repository, in the app, or in a second implementation here. Each rule ships with a test
that breaks the fixture article or a sample block and asserts the rule's error code.

### Article X — Templates and rules change together
A template in `ol/authoring/templates/` and the rules for its category in
`ol/authoring/specs.yml` change in the same pull request. A template section the checks do
not require, or a required section the template lacks, is a bug.

### Article XI — Nothing language-specific, nothing private
The package holds no language's content and no rule that only one language needs. It
depends on nothing private, and nothing in it is private. It never depends on audio or
text-to-speech libraries.

### Article XII — Compatibility
Language repositories pin a tagged version. A change that makes an article or block valid
today fail tomorrow is a breaking change: it bumps the minor version while the package is
below 1.0, and its CHANGELOG entry says what an author has to change.

### Article XIII — Stack norms
Python 3.13 and newer, uv-managed, built with hatchling. Ruff is the linter and formatter,
configured from `ruff-base.toml`. Installed from git; not published to a package index.
Text that reaches an author (check messages, templates, docs) uses no em dashes.

## Articles not adopted

- Internationalization — the package has no interface of its own to translate
- Data-model conventions (Django) — the package has no Django code and no models

## Quality bar

Read at planning and review; applies to every change.

- Tests pass and coverage stays above the floor CI enforces (`--cov-fail-under` in
  `.github/workflows/ci.yml`), and never falls on the code a change touches.
- `ruff check` and `ruff format --check` pass.
- The package builds, and the built wheel installs and runs `ol --help`.
- Every public change updates the README and `CHANGELOG.md` in the same pull request.

## Non-negotiables

- Lint, tests and build pass before a change merges. Nobody overrides a red check.
- The default branch requires one approval, and the author of a change never approves it.

---

**Version**: 1.0.0 | **Ratified**: 2026-10-19 | **Last Amended**: 2026-10-19
