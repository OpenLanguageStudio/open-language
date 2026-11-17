# 1. Track modes, and presenters named on every block

- **Status:** Proposed. Agreed with Sam in conversation on 2026-11-17, and the app side is being prototyped first.
- **Deciders:** Sam, Lex.

## Context

A block today writes one kind of track: one presenter says one example after another. That fits most grammar tracks, but not every lesson:

- Some lessons need a conversation between several presenters.
- Some need a question from one presenter and an answer from another, such as *doch* as the answer to a negative yes/no question.
- Writing lessons need a model text read in full by the presenter who wrote it, and some need an exchange of messages between presenters.

Who presents a track is also set in two places. The app holds each track's presenter, set through its API, and falls back to the album's presenter. A page can carry a `presenter:` field in its front matter, which the checks accept and nothing reads. Writing and conversation tracks have to be written for a particular presenter, so the page has to name them. Some sentences also mark the speaker's gender, such as *Ich bin Krankenschwester*, so even an ordinary track can need a particular presenter.

## Decision

### Every block names its presenters

A block that writes its track carries `:presenters:`. A duplicate block does not. The option takes one presenter slug or several, separated by commas, in the order the mode gives them a meaning. A page never names a presenter. The front-matter `presenter:` field is withdrawn, and its check goes with it.

The first presenter listed speaks the track's spoken title, in every mode.

### Inline examples name their presenter too

The short examples in an article's body (the `ol-examples` boxes) are recorded as well, so each box names its presenter with `:presenters:` and exactly one slug. This replaces the front-matter `presenter:` field, which set them for the whole page. How the option attaches to the box is settled in the build.

### A block has a mode

`:mode:` says how the block's examples are read and spoken. Leaving it out means `examples`.

| Mode | For | Presenters | Body |
|---|---|---|---|
| `examples` | One model sentence after another | Exactly 1 | As today: a sentence, then `: translation`. |
| `pairs` | A question and its answer; a prompt and its changed form (present to Perfekt, *du* to *Sie*) | 1 or 2 | Groups of exactly two examples, separated by a blank line. The first presenter says the first example of every pair, and the second presenter says the second. With one presenter, they say both. |
| `dialogue` | A conversation, spoken or in text messages | 2 or more | Each sentence starts with its presenter's slug and a colon: `lina: Ist hier noch frei?`. A blank line ends an exchange. |
| `passage` | A connected text one presenter says in full: a letter, an email, a voicemail, a short account | Exactly 1 | As `:multiline:` today: sentence lines, then `: translation` lines. Each group is one example and one recording. |
| `correspondence` | Written messages sent back and forth: emails, letters, postcards. Text messages are a `dialogue`, one message per example. | 2 or more | Each message opens with a line holding only its presenter's slug and a colon, such as `lina:`, followed by its sentence lines and then its translation lines. The next slug line starts the next message. A blank line inside a message is a paragraph break. Each message is one example and one recording. |

`passage` replaces `:multiline:`, which is withdrawn.

A slug cannot be mistaken for a sentence or a translation. A translation line starts with a colon. A slug is lower case and is followed by a colon. A sentence in the language taught does not start that way.

```
:::{audio-examples}
:track: a1/grammar/doch
:title: Doch
:mode: pairs
:presenters: deniz, lina

Hast du keine Zeit?
: Don't you have time?
Doch, ich habe Zeit.
: Yes, I do have time.

Kommst du nicht mit?
: Aren't you coming?
Doch, ich komme mit.
: Yes, I'm coming.
:::
```

```
:mode: dialogue
:presenters: lina, roman

lina: Guten Morgen! Ist hier noch frei?
: Good morning! Is this seat free?
roman: Ja, natürlich.
: Yes, of course.

lina: Danke. Kommen Sie oft hierher?
: Thanks. Do you come here often?
```

```
:mode: correspondence
:presenters: lina, roman

lina:
Lieber Roman,
hast du am Samstag Zeit?
Viele Grüße
Lina
: Dear Roman,
: are you free on Saturday?
: Best wishes,
: Lina

roman:
Liebe Lina,
ja, am Samstag habe ich Zeit.
Bis dann
Roman
: Dear Lina,
: yes, I'm free on Saturday.
: See you then,
: Roman
```

### What the checks refuse

The package refuses these, and the app reads blocks with the same code. The codes are suggestions, and the build settles them.

- `missing_presenters`: a block that writes has no `:presenters:`.
- `bad_presenters`: a value that is not a slug, a slug given twice, or the wrong number of presenters for the mode.
- `unknown_mode`: a `:mode:` that is not one of the five.
- `bad_pair`: a `pairs` group that is not exactly two examples.
- `presenter_not_listed`: a `dialogue` or `correspondence` example names a slug that `:presenters:` does not list.
- `presenter_silent`: a presenter listed for a `dialogue` or `correspondence` block who says nothing in it.

`sentence_twice` applies to `examples` blocks only. A conversation can repeat "Ja." or "Danke." on purpose.

The package cannot know which presenters exist, because the app holds them. The app refuses a slug it does not know, with the code `unknown_presenter`, which the package defines.

### What the app receives

The app already writes each block it reads to its block file as it stands, so the new fields reach it without new plumbing:

- `Block.mode`, and `Block.presenters` in the order the block lists them.
- `Example.presenter`: the slug of the presenter who says it, worked out from the mode. Every example has one, so the app never has to work it out again.
- `Example.group`: the number of the pair, exchange or message thread the example belongs to, counted from 1. In `examples` and `passage` each example is its own group.

On import, the app makes the first presenter the track's presenter and gives each example its presenter. The app's `Example` already has an optional presenter for this. A track a block writes takes its presenters from the block alone: the API no longer sets them, and the album's presenter no longer stands in. The pause between examples, including between the two halves of a pair, stays the app's and the learner's to set.

### Writing for a presenter

Content in every mode is tied to the presenters where the lesson allows. The language being taught comes first. Within that, examples fit the life of the presenter who says them: their work, family, town and interests. This matters most for `dialogue`, `passage` and `correspondence`. An author reads the presenters' profiles from the app at the start of each authoring run. When a topic fits nobody, the author may add the detail to a presenter's profile in the app (for instance, Max becomes a basketball fan) and then write for them. That step goes into the authoring rules.

## Consequences

- This is a breaking change under Article XII. Every block in a language repository needs `:presenters:`, and every `:multiline:` block becomes `:mode: passage`, before the repository pins the version that ships this. German has 162 blocks, 12 of them on `:multiline:` pages.
- The template `audio-examples-block.md`, its option list, the samples in `ol/authoring/samples/`, `CONTEXT.md` and the README change in the same pull request as the reader, under Articles IX and X.
- `CONTEXT.md` gains **Presenter** and **Mode**. **Speaker** goes under the terms deliberately not used: a person who says an example is always a presenter.
- Setting a track's presenter through the app's API stops being how presenters are chosen for tracks a block writes.
