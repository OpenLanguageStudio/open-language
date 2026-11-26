# Writing rules

How to write a coursebook article, for every language. These are the judgement calls. The
[page standard](page-standard.md) holds the checkable shape of a page, and the
[authoring rules](authoring-rules.md) hold the file and front-matter rules. Each rule says what
to do and, briefly, why. When a review turns up something new, it is added as a rule.

Rules for one language only live in that language's repository, in
`standards/writing-<language code>.md` (German: `DE-W1` onwards).

## Rule IDs

- Every rule has an ID: `OL-W<n>` here, `<LANG>-W<n>` in a language repository. Cite the ID in
  lint messages, review findings, and pull request and issue comments.
- IDs are never renumbered or reused. A retired rule keeps its number, marked *Retired* with
  the date, so old citations still resolve. A new rule takes the next free number, wherever it
  sits on the page.
- A language rule may narrow a global rule for that language. It names the global rule it
  narrows.

## Bending a rule

These are guides, not laws. Some articles need a rule bent. When one does, mark the bend with
a comment beside it in the source, giving the rule ID and the reason:
`<!-- OL-W8 bent: this page compares the two registers line by line -->`, and say so in the
pull request. An unmarked bend is a review finding.

The examples are German, the first coursebook.

## Purpose

**OL-W1. Teach what people say, not what textbooks say.** List the forms heard in everyday
speech first, even when the textbook form is "more correct". *Ich bin Sam* is as common an
opener as *Ich heiße Sam*, so both are listed. Why: the course prepares readers for real
conversations, not exams.

**OL-W2. One article, one goal.** Every paragraph serves the page's goal. A fact that belongs to
another topic (which countries take *der*, on a page about introductions) gets a link to the
article that covers it, not a paragraph here. Why: side quests pull the reader away from what
the page promised.

**OL-W3. Write as if every article you need already exists.** When something needs its own
explanation, link to the article that should hold it, in the sentence where it comes up. If
that article doesn't exist, link to it anyway, with an ordinary link, its own text (OL-W17) and
the path it should have (`<level>/<category>/<file-name>`, as the authoring rules name files).
Add no marker or TODO: the link is its own marker. Until the page exists it shows as plain
text; once the page is written, the next build turns it into a live link with no edit to this
page. `ol wanted` lists every such link, worked out from the source on every run. Use wanted
links only for depth ("learn more"). A page must teach its goal fully without them. Why: the
coursebook grows from the gaps its writers find.
- At review, each wanted link is either accepted, which puts the page on the writing queue
  before merge, or removed, which means the writer drops the link. Nothing is merged
  untriaged, so every wanted link left on main is a page that has been commissioned.

## Where things go

**OL-W4. Explanation sits where it is used.** Don't open the page with a paragraph that previews
everything below. Put one or two sentences at the top of the section they explain, just before
its table or examples. Why: a reader looking at the questions wants the note about questions
next to them.

**OL-W5. One paragraph, one idea.** If consecutive sentences jump between topics (verbs, then
question endings, then age, then *Und du?*), they belong in different sections. Test: can the
paragraph be given a single heading?

**OL-W6. The opening frames the goal.** The lead says what the reader can do after the page. An
optional second paragraph states the one idea that organises the page (on *Introduce
yourself*: formal or informal decides the questions). It never summarises the grammar to come.

**OL-W7. Name the target-language term once, under the title.** The H1 is English. The
target-language name of the goal goes in `target-title:` in the front matter and is drawn
under the H1 as a subtitle. Never write a sentence such as "German calls it *sich
vorstellen*". When a target-language term has to appear in prose, translate it the first time,
in brackets.

**OL-W8. Registers as tabs, consistently.** Where the same phrases come in a formal and an
informal version, show them in a tab set, one tab per register, with an examples block in each
tab. The language's rules name the tab labels (German: DE-W1). Do this everywhere in the
coursebook unless the page's point is to mix them.

**OL-W9. A track closes the section it practises.** When a page has two tracks (formal and
informal, say), give each its own section and put the track at the end of it. Don't stack
tracks together at the end of the page.

**OL-W10. Never write a track's title as a heading.** The audio block draws its own title, and
track titles must not appear in the sidebar.

**OL-W11. Tables only when there is something to note.** A phrase table earns its place through
its Notes column. Phrases with nothing to note go in an `ol-examples` block, which also makes
them playable.

**OL-W12. Notes are short and point onwards.** An aside is one or two sentences, followed by a
link to the article that covers it in full ("More in [Choose between du and Sie](…)"). It
never re-teaches another article.

**OL-W13. Culture notes use the `culture-note` directive,** wherever they fit on the page, never
a `## Culture note` heading. Readers like them; keep them short and concrete.

## Links

**OL-W14. Link in the text, to articles.** A link inside a sentence, at the point where the
reader needs it, is the main way pages connect. It is what future link graphs will be built
from. Front-matter `related:` stays short and conservative: a few close neighbours.

**OL-W15. Link to an article before the glossary.** The glossary is for grammar jargon and
target-language terms that a general reader wouldn't know (*dative*, *separable verb*).
Everyday words such as "question word" need no glossary link; a grammar word like "verb" may
keep its link, which will open in place rather than leave the page. Where an article covers
the term, link to the article.

**OL-W16. Every common mistake that another article explains ends with a link to it.**

**OL-W17. Every link has its own text.** Write
`[Countries and languages](/a1/vocabulary/countries-and-languages-1.md)`, never an empty
`[](…)`. An empty link borrows the target's title, but a page that is not written yet has no
title, so the reader would see nothing useful. Text written into the sentence also reads
better than a pasted title.

## Accuracy

**OL-W18. Check every claim from the reader's language.** The instruction language is English,
so never call something a surprise or a difference when English does the same thing. German
*Ich bin 36* is English *I am 36*: no surprise. A claim that would hold only for another reader
(French, Spanish) is false here. English means British and American English: if a claim holds
for only one (floor numbering, "half four"), name that one.

**OL-W19. Common mistakes must be real.** List only mistakes that learners with the reader's
language really make. Never invent one to fill the box. Fewer is fine. *Wo kommst du?* for
*Woher kommst du?* is real; *Ich bin heiße Anna* is not. A form native speakers say, even
casually (*Ich mag schwimmen*), is not a mistake; teach it as register if it matters.

**OL-W20. A reviewer fact-checks before merge.** Each article is checked by a reviewer who is
not its writer. The reviewer checks every claim against OL-W18, every common mistake against
OL-W19, every target-language sentence for naturalness, and the wanted-pages list (OL-W3).

## Playability

**OL-W21. Every example on the page plays.** A line in an `ol-examples` box is always playable.
Only a full track may be locked. A box line is copied word for word from a track line, so it
reuses that recording.

## Voice

**OL-W22. Keep the tone consistent;** the wording is the writer's own. Plain, warm, direct.

**OL-W23. Know the AI-writing patterns and avoid them as you write.** These are stock vocabulary
("crucial", "seamless"), rule-of-three padding, "not only… but also", and inflated
significance. The reviewer fixes any that slip through. Never rewrite text that already reads
well.

**OL-W24. Short sentences, each with one job.** If a sentence needs "and" to join two topics,
split it.

**OL-W25. No filler sections.** Use only the sections the page needs.

## Standing rules

**OL-W26.** No em dash, anywhere a reader or a platform sees text.

**OL-W27.** No reader address ("you") in body prose. It belongs only in notices and in example
translations. No stock openers ("Learn how to…", "After this page…").

**OL-W28.** Hedge claims about third parties: exams, employers, stores, platforms.

**OL-W29.** Every phrasing in `keywords` appears in a body sentence a person would say; a table
cell doesn't count. Teaching beats discoverability.

**OL-W30.** Every first-person sentence is true of the presenter who says it.

**OL-W31.** No disclosure lines (AI voices, fictional presenters) in content. The site shows
those itself.

**OL-W32.** Never hand-write what the build generates: previous/next links, section numbers,
Related articles from `related:`.

**OL-W33.** Writing articles are correspondence, never form-filling.
