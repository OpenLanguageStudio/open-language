# Content review

Every pull request into a language repository needs a content review before it
merges, and how much review depends on what it changes. A typo fix by the
repository owner needs none. A new page needs a careful one. The review shows on
the pull request as the commit status `content-review`, which the repository's
ruleset requires.

## Tiers

The tier is worked out in CI from the pull request's diff and its author's
numeric GitHub user id. A login is never used, because a login can be renamed
and then registered by someone else.

| Tier | When | What it needs |
|---|---|---|
| Trivial | The author is a trusted author, every changed line is a prose edit inside a page that already exists, and the pull request changes 10 lines or fewer | Nothing. CI sets the status to success. The content checks still have to pass. |
| Small | Not trivial, adds no page, changes no track, and changes 200 lines or fewer | A review by a fast model |
| Full | A new or renamed page, a changed track, or more than 200 changed lines | A review by a strong model that did not write the change |

A **prose edit** is a changed line that is not in the front matter, not in an
`audio-examples` block or an `ol-examples` box, not a code fence or directive
line, and not a heading. Across each page, the removed and the added lines link
to the same targets, so no link moves. A file that is not a page, such as
`uv.lock` or `conf.py`, is never a prose edit.

**Trusted authors** are the repository owner and the Open Language bot. An
outside contributor is never trivial, however small the change.

**Changed lines** are lines added plus lines removed, as GitHub counts them.
Ten is about five edited lines: a typo or two, or one reworded sentence. Two
hundred is where a fast model's review stops being enough: studies of code
review find that reviewers catch fewer defects past about 200 to 400 changed
lines in one review, and a coursebook review also checks every target-language
sentence.

The limits and the trusted authors are in `ol/authoring/specs.yml`, under
`content_review`.

## How the status moves

1. A pull request is opened or pushed to. The repository's content review
   workflow runs `ol review-tier --pr <number> --post`. A trivial pull request
   gets `success`. A small or full one gets `pending`, with the tier in the
   description, and a comment says in words what review it needs and why.
2. The reviewer reviews the head commit and posts the verdict as the bot:

   ```
   ol review-status --pr <number> --verdict pass --tier small \
     --report review.md --model <reviewing model> --sha <reviewed commit>
   ```

   The command posts `success` or `failure` on the head commit and the report as
   a pull request comment. It refuses a review lower than the tier the pull
   request needs, a review of a commit that is no longer the head, and a full
   review whose `--model` is the `--writer-model`.
3. A new push leaves the new head commit without a verdict. The workflow sets
   it to `pending` again, and the pull request blocks until it is reviewed
   again.

A full review checks every claim against the [writing rules](writing-rules.md)
(OL-W18 and OL-W19 especially), every target-language sentence for
naturalness, and the wanted pages (OL-W3). It answers the questions of the
review rubric, `ol/authoring/review-rubric.yml`. A small review reads the
changed lines and their paragraphs for the same things.

## Setting it up in a language repository

The workflow runs on `pull_request_target`, so it can set a status on pull
requests from forks. It checks out the base branch and never runs the pull
request's code: the tier is read from the GitHub API.

```yaml
name: Content review
on:
  pull_request_target:
    types: [opened, synchronize, reopened, ready_for_review]
    branches: [main]
permissions:
  contents: read
  statuses: write
  pull-requests: write
jobs:
  tier:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@v10.2.0
        with:
          python-version: "3.13"
      - run: uv sync --locked
      - run: uv run ol review-tier --pr ${{ github.event.pull_request.number }} --post
        env:
          GH_TOKEN: ${{ github.token }}
```

The ruleset on `main` requires the status check `content-review` beside the
content checks, from any source: the workflow sets it with the workflow's
token, and a reviewer with the bot's.

The bot posts verdicts, so its GitHub App needs the **Commit statuses: read and
write** repository permission, as well as **Pull requests: read and write** for
the report.
