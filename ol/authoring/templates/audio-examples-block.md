<!-- TEMPLATE: the audio-examples block. A block with examples writes its
track; the track is named by its address, never by an album. The block lives
in the article under "## Hear it in practice", AFTER the learning sections,
BEFORE Summary. Delete these comment lines: HTML comments are banned in docs. -->

:::{audio-examples}
:track: {{level}}/{{category}}/{{name}}
:presenters: {{presenter-slug}}
:title: {{NATIVE_TITLE: spoken aloud as the track intro}}
:title-en: {{ENGLISH_TITLE}}
:tags: {{tag}}, {{tag}}

{{Native sentence 1}}
: {{English translation 1}}

{{Native sentence 2}}
: {{English translation 2}}
:::

<!-- Options. A block takes these seven and no others:
- :track: {{level}}/{{category}}/{{name}} : the track's address, in lower
  case. All three parts are always written: the name is never taken from
  the page. Never change an address once the track has audio.
- :title: / :title-en: : the title in the language taught (spoken) and in
  English. A title published in the stores keeps its dash: leave :title-en:
  out and the app keeps the title it holds.
- :tags: : words that say what the track is about, separated by commas.
- :presenters: : every block that writes its track carries it. One presenter
  slug, or several separated by commas, in the order the mode gives them a
  meaning. The first speaks the track's spoken title. Pages never name a
  presenter in their front matter. Write for the presenters: their work,
  family, town and interests, from their profiles in the app.
- :mode: : how the examples are read and spoken. Leave it out for examples.
  - examples (1 presenter): a sentence, then ': translation'.
  - pairs (1 or 2): groups of exactly two examples separated by a blank line,
    such as a question and its answer. The first presenter says the first of
    every pair and the second the second.
  - dialogue (2 or more): each sentence opens with its presenter's slug and a
    colon, such as 'lina: Ist hier noch frei?'. A blank line ends an exchange.
  - passage (1): a connected text, such as a letter or a voicemail. Each
    group is sentence lines then ':'-prefixed translation lines, separated by
    a blank line. Line breaks are kept on the page and in the audio, and a
    blank line inside the sentence or translation lines is a paragraph break.
  - correspondence (2 or more): messages back and forth. Each message opens
    with a line holding only its presenter's slug and a colon, such as
    'lina:', then its sentence lines, then its translation lines.
- :duplicate: : shows a track another block writes, on this page too. It
  carries :track: and, if wanted, :tags:, and nothing else: no examples, no
  title, no English title, no mode and no presenters.

Rules:
- ORDERED. Best and most representative sentences FIRST: the build cuts from
  the end when the ~70 s budget is reached (hard floor 45 s). Over-author
  ~12-18 short, natural, at-level sentences.
- Plain text ONLY: no roles, backticks or braces. The native line goes to the
  text-to-speech engine verbatim. Coherent ordering improves prosody.
- In examples mode each sentence appears once in a block, whatever its spacing
  or emphasis. A dialogue may repeat "Ja." or "Danke." on purpose.
- One block writes a track. Any other page that shows it uses :duplicate:.
- Check the page with `ol validate`. -->
