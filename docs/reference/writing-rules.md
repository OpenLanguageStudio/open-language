# Writing rules

These rules govern the wording and structure of every coursebook article, in every language.
The [page standard](page-standard.md) defines the checkable shape of a page. The
[authoring rules](authoring-rules.md) define files and front matter. Each rule states a
requirement and its reason. Examples are in German.

Rules for a single language are defined in that language's repository, in
`standards/writing-<language code>.md` (German: `DE-W1` onwards).

## Rule IDs

- Every rule has an ID: `OL-W<n>` in this file, `<LANG>-W<n>` in a language repository. Lint
  messages, review findings, and pull request and issue comments cite rules by ID.
- IDs are never renumbered or reused. A retired rule keeps its number and is marked *Retired*
  with the date. A new rule takes the next free number.
- A language rule may narrow a global rule for that language. It names the rule it narrows.

## Exceptions

An article may depart from a rule where the rule would harm the page. The departure is marked
in the source beside the affected text, with the rule ID and the reason:
`<!-- OL-W8 bent: this page compares the two registers line by line -->`. The pull request
states it. An unmarked departure is a review finding.

## Purpose

**OL-W1. Teach what people say.** Forms heard in everyday speech are listed first, including
where a textbook form is considered more correct. *Ich bin Anna* is as common an opener as
*Ich heiße Anna*; both are listed. Reason: the course prepares readers for real conversations,
not exams.

**OL-W2. One article, one goal.** Every paragraph serves the page's goal. A fact that belongs to
another topic (which countries take *der*, on a page about introductions) is linked to the
article that covers it, not explained on the page. Reason: digressions pull the reader away
from the page's goal.

**OL-W3. Link to the article that should exist.** A point that needs its own explanation links
to the article that should hold it, in the sentence where it comes up. If that article does not
exist, the link is still written, with its own text (OL-W17) and the path the article will have
(`<level>/<category>/<file-name>`, per the authoring rules). No marker or TODO is added. Until
the article exists the link renders as plain text; the build turns it into a live link once the
article is written. `ol wanted` lists every such link. Wanted links are for further depth only:
the page teaches its goal fully without them. Reason: the coursebook grows from the gaps its
writers find.
- At review, each wanted link is accepted, which adds the article to the writing queue, or
  removed. No wanted link is merged untriaged.

## Structure

**OL-W4. Explanation sits where it is used.** The page does not open with a preview of all its
sections. One or two sentences of explanation go at the top of the section they explain,
before its table or examples. Reason: the explanation is needed next to the material it
explains.

**OL-W5. One paragraph, one idea.** Sentences on different topics (verbs, question endings, age)
belong in different sections. A paragraph that cannot take a single heading is split.

**OL-W6. The opening states the goal.** The lead states what the reader can do after the page.
An optional second paragraph states the one idea that organises the page (on *Introduce
yourself*: register decides the questions). The opening never summarises the grammar that
follows.

**OL-W7. The target-language term appears once, under the title.** The H1 is in English. The
target-language name of the goal goes in `target-title:` in the front matter and renders under
the H1. The prose never restates it ("German calls it *sich vorstellen*"). A target-language
term in prose is translated in brackets at first use.

**OL-W8. Registers in tabs.** Phrases that exist in a formal and an informal version are shown
in a tab set, one tab per register, with an examples block in each tab. The language rules fix
the tab labels (German: DE-W1). This applies throughout the coursebook unless the page's point
is to mix registers.

**OL-W9. A track closes the section it practises.** A page with two tracks gives each its own
section, with the track at the end of it. Tracks are not stacked at the end of the page.

**OL-W10. Track titles are never headings.** The audio block renders its own title. Track
titles do not appear in the sidebar.

**OL-W11. Tables only with notes.** A phrase table requires a Notes column with content.
Phrases with nothing to note go in an `ol-examples` block, which also makes them playable.

**OL-W12. Asides are short and link onwards.** An aside is one or two sentences, followed by a
link to the article that covers the subject ("More in [Choose between du and Sie](…)"). It does
not re-teach another article.

**OL-W13. Culture notes use the `culture-note` directive,** placed where they fit, never a
`## Culture note` heading. They are short and concrete.

## Links

**OL-W14. Links sit in the text and point to articles.** An in-sentence link, at the point of
need, is the primary connection between pages. Front-matter `related:` is limited to a few close
neighbours.

**OL-W15. An article link takes precedence over the glossary.** The glossary covers grammar
terms and target-language terms a general reader does not know (*dative*, *separable verb*).
Everyday words ("question word") take no glossary link. A basic grammar word ("verb") may keep
its glossary link. Where an article covers the term, the link goes to the article.

**OL-W16. A common mistake that another article explains links to it.**

**OL-W17. Every link has its own text.**
`[Countries and languages](/a1/vocabulary/countries-and-languages-1.md)`, never `[](…)`.
Reason: an empty link borrows the target's title, and an article not yet written has none.

## Accuracy

**OL-W18. Claims hold for the reader's language.** The instruction language is English. A
feature English shares is not presented as a surprise or a difference: German *Ich bin 36* is
English *I am 36*. A claim true only for speakers of another language is false here. English
means British and American English; a claim true of only one names that variety (floor
numbering, "half four").

**OL-W19. Common mistakes are real.** Only mistakes that learners with the reader's language
actually make are listed. None is invented to fill the section. *Wo kommst du?* for *Woher
kommst du?* is real; *Ich bin heiße Anna* is not. A form native speakers use, including in
casual speech (*Ich mag schwimmen*), is not a mistake; where it matters it is taught as
register.

**OL-W20. Every article is fact-checked before merge** by a reviewer who did not write it. The
reviewer checks every claim against OL-W18, every common mistake against OL-W19, every
target-language sentence for naturalness, and every wanted link (OL-W3).

## Playability

**OL-W21. Every example on the page plays.** A line in an `ol-examples` box is always playable;
only a full track may be locked. A box line is copied word for word from a track line and uses
that recording.

## Style

**OL-W22. The tone is plain, warm and direct** throughout the coursebook.

**OL-W23. No AI-writing patterns:** stock vocabulary ("crucial", "seamless"), rule-of-three
padding, "not only… but also", inflated significance. Text that already reads well is not
rewritten.

**OL-W24. Short sentences, one job each.** A sentence that joins two topics with "and" is split.

**OL-W25. No filler sections.** A page has only the sections it needs.

**OL-W26.** No em dash in any text a reader or a platform sees.

**OL-W27.** Body prose does not address the reader ("you"). Direct address is limited to
notices and example translations. No stock openers ("Learn how to…", "After this page…").

**OL-W28.** Claims about third parties (exams, employers, stores, platforms) are hedged.

**OL-W29.** Every phrase in `keywords` appears in a body sentence; a table cell does not count.
Teaching takes precedence over search ranking.

**OL-W30.** Every first-person sentence is true of the presenter who says it.

**OL-W31.** Content contains no disclosure lines (AI voices, fictional presenters). The site
displays these.

**OL-W32.** Nothing the build generates is written by hand: previous/next links, section
numbers, Related articles from `related:`.

**OL-W33.** Writing articles are correspondence, never form-filling.
