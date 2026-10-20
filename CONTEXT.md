# Open Language

The vocabulary of this package: the words to use in issues, commit messages,
test names, docstrings and documentation.

The Open Language app reads the same pages this package checks, and the two
share these words. Where the code still carries an older name, the entry says
so. The entry is the word to use, and the code is what changes.

## What the package works on

**Coursebook**:
The learning material for one language, built from that language's repository.
There is one Coursebook per language, and nothing may assume German is the only
one.

**Language repository**:
The repository holding one language's pages, such as `german`. It installs this
package and runs `ol check`. The code and the README still call it a
"workspace" (`Language`, `.ol-validate-baseline`, the `--workspace` handling);
those names change as the code is touched.
_Avoid_: workspace.

**Coursebook author**:
Someone who writes a language repository's pages.

**Article**:
One page of a Coursebook that teaches one thing, written from the template for
its category. An article has a level and a category, which come from its path:
`<level>/<category>/<name>.md`.
_Avoid_: lesson, page (when the article itself is meant).

**Category index**:
The `index.md` that lists a category's articles for one level. Its toctree order
is the learning sequence where the category is ordered.

**Level**:
A CEFR level, written in lower case in paths: `a1`, `a2`, `b1`, `b2`. There
are no levels above B2.

**Category**:
The kind of article, which decides its template: `concepts`, `grammar`,
`writing`, `vocabulary`. A level lists them in that order, and no other.

**Menu**:
The site's navigation, built from the toctree of the top-level `index.md` and of
each level index. The top-level `index.md` is the Introduction page. Its toctree
lists the other top-level pages, then the levels from A1 to B2.
_Avoid_: navigation, sidebar (when the toctrees are meant).

**Template**:
The Markdown file in `ol/authoring/templates/` that an article of a category is
started from. A template and the rules for its category in `specs.yml` change
together.

## What a learner hears

**Track**:
One lesson in sound: a spoken title followed by its examples in order. A track
is identified by its language, level, category and name.

**Address**:
A track's level, category and name within its language, such as
`a2/grammar/nebensatz-mit-weil`. It is what an `audio-examples` block names a
track by. An album is never part of it.

**Block**:
An `audio-examples` directive on an article. A block with examples writes its
track: its examples are the track's examples.
_Avoid_: listening block, audio block.

**Duplicate block**:
A block that shows a track another block writes. It carries `:duplicate:` and
the track's address, and it writes nothing.
_Avoid_: alias, reference, link.

**Example**:
One sentence in the language being taught, together with its translation. It is
the unit a track is made of.
_Avoid_: phrase, line, audio example.

**Sentence**:
The spoken text of an example, in the language being taught. Use it only when
the text itself is meant, as opposed to the translation.

**Translation**:
An example's meaning in English. It is never spoken.

**Tag**:
A word that says what a track is about, such as `dativ`. "Dativ" and "dativ"
are one tag.

## Checking

**Check**:
A rule a script can measure, run by `ol validate` or `ol check`. A check fails
with an error, or warns.

**Refusal**:
A block the checks reject, with a code naming why. The app reads blocks with the
same code, so a block this package refuses is one the app will not show.

**Baseline**:
The list in `.ol-validate-baseline` of older articles that fail the checks and
are known to. It only shrinks.

**Review rubric**:
The questions in `ol/authoring/review-rubric.yml` for what a script cannot
judge: level, correctness, teaching value and plain language. Each is answered
pass, concern or fail.

## Terms deliberately not used

**Workspace**:
See language repository.

**Lesson**:
Says neither article nor track. Use whichever is meant.
