<!-- TEMPLATE: the audio-examples block. A block with examples writes its
track; the track is named by its address, never by an album. The block lives
in the article under "## Hear it in practice", AFTER the learning sections,
BEFORE Summary. Delete these comment lines: HTML comments are banned in docs. -->

:::{audio-examples}
:track: {{level}}/{{category}}/{{name}}
:title: {{NATIVE_TITLE: spoken aloud as the track intro}}
:title-en: {{ENGLISH_TITLE}}
:tags: {{tag}}, {{tag}}

{{Native sentence 1}}
: {{English translation 1}}

{{Native sentence 2}}
: {{English translation 2}}
:::

<!-- Options. A block takes these six and no others:
- :track: {{level}}/{{category}}/{{name}} : the track's address, in lower
  case. All three parts are always written: the name is never taken from
  the page. Never change an address once the track has audio.
- :title: / :title-en: : the title in the language taught (spoken) and in
  English. A title published in the stores keeps its dash: leave :title-en:
  out and the app keeps the title it holds.
- :tags: : words that say what the track is about, separated by commas.
- :multiline: : writing model texts only: examples become blank-line-separated
  groups (native lines, then ':'-prefixed translation lines); line breaks are
  kept on the page and in the audio.
- :duplicate: : shows a track another block writes, on this page too. It
  carries :track: and, if wanted, :tags:, and nothing else: no examples, no
  title, no English title.

Rules:
- ORDERED. Best and most representative sentences FIRST: the build cuts from
  the end when the ~70 s budget is reached (hard floor 45 s). Over-author
  ~12-18 short, natural, at-level sentences.
- Plain text ONLY: no roles, backticks or braces. The native line goes to the
  text-to-speech engine verbatim. Coherent ordering improves prosody.
- Each sentence appears once in a block, whatever its spacing or emphasis.
- One block writes a track. Any other page that shows it uses :duplicate:.
- Check the page with `ol validate`. -->
