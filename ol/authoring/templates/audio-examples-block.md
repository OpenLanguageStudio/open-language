<!-- TEMPLATE: the audio-examples block: one block = one track (ADR-0006).
Lives in the article under "## Hear it in practice", AFTER the learning
sections, BEFORE Summary. The block IS the track: title, voice, streaming
links and examples all live here; album.yml lists only the track name in
play order. Delete these comment lines: HTML comments are banned in docs. -->

:::{audio-examples}
:album: {{level}}/{{category}}/{{album-name}}
:title: {{NATIVE_TITLE: spoken aloud as the track intro}}
:title-en: {{ENGLISH_TITLE}}

{{Native sentence 1}}
: {{English translation 1}}

{{Native sentence 2}}
: {{English translation 2}}
:::

<!-- Rules:
- ORDERED. Best/most-representative sentences FIRST: the build cuts from the
  end when the ~70 s budget is reached (hard floor 45 s), then trims this block
  to match. Over-author ~12-18 short, natural, at-level sentences.
- Plain text ONLY: no roles, backticks or braces: the native line goes to
  the text-to-speech engine verbatim. Coherent ordering improves prosody.
- :name: {{track-name}}  : REQUIRED if the article has more than one block
  (defaults to the article file stem). Never churn a name once audio exists.
- :voice: {{name}}       : only to override the album default.
- :multiline:            : writing model texts only: examples become
  blank-line-separated groups (native lines, then ':'-prefixed translation
  lines); line breaks are preserved on the page and in the audio.
- :spotify: / :youtube-music:: DO NOT AUTHOR; filled in after release.
- Register {{track-name}} in albums/{{level}}/{{category}}/{{album-name}}/album.yml
  tracks: (play order), then run validate_doc.py and `ol audit`. -->
