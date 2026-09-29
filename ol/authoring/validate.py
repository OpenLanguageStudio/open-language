#!/usr/bin/env python3
"""Validate Open Language docs articles / indexes against the authoring templates.

Usage:
    ol validate [--workspace /path/to/<language>] [--type TYPE] FILE [FILE...]

- FILE paths must live under <workspace>/docs/<level>/<category>/... ; the
  content type is inferred from the path (grammar/concepts/writing/topics/
  situations) unless --type is given.
- index.md files get index checks (toctree present, entries resolve, no orphan
  articles, no CEFR level in the title, no References section); other .md files
  get article checks per specs.yml.
- Every :::{audio-examples} block is checked in its ADR-0006 content form:
  required :album: backlink and :title:, example-pair grammar (single-line or
  :multiline:), no banned characters (text is fed to TTS verbatim), and, when
  --workspace is given or inferable, album dir + album.yml exist (and store no
  level/category/language) and the track name is listed in the album.yml
  tracks: list. Legacy :track: pointer blocks are ERRORs. Missing streaming
  links are reported as INFO (pending release).
- Stub files (< 200 bytes of body) are reported as STUB, not failed line by line.

Exit code: 1 if any ERROR, else 0. Dependency: PyYAML.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

SPECS_PATH = Path(__file__).resolve().parent / "specs.yml"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
SPECS = yaml.safe_load(SPECS_PATH.read_text(encoding="utf-8"))

CATEGORIES = ("grammar", "concepts", "writing", "topics", "vocabulary", "situations")
STUB_BODY_BYTES = 200


class Report:
    def __init__(self, path: Path):
        self.path = path
        self.items: list[tuple[str, str]] = []

    def error(self, msg):
        self.items.append(("ERROR", msg))

    def warn(self, msg):
        self.items.append(("WARN", msg))

    def info(self, msg):
        self.items.append(("INFO", msg))

    @property
    def failed(self):
        return any(lvl == "ERROR" for lvl, _ in self.items)


def split_frontmatter(text: str):
    """Return (frontmatter_dict_or_None, body). Tolerates BOM."""
    text = text.lstrip("﻿")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return None, text
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return {"__parse_error__": str(e)}, text[m.end() :]
    return fm or {}, text[m.end() :]


def infer_context(path: Path, workspace: Path | None):
    """Infer (workspace, level, category) from .../<ws>/docs/<level>/<category>/..."""
    parts = path.resolve().parts
    if "docs" not in parts:
        return workspace, None, None
    i = parts.index("docs")
    ws = workspace or Path(*parts[:i])
    level = parts[i + 1] if len(parts) > i + 1 else None
    category = parts[i + 2] if len(parts) > i + 2 else None
    if category is not None and category not in CATEGORIES:
        category = None
    return ws, level, category


def native_code(workspace: Path | None) -> str:
    """language_code from the workspace open-language.yml (fallback de)."""
    if workspace:
        cfg = workspace / "open-language.yml"
        if cfg.exists():
            data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
            return data.get("language_code") or "de"
    return "de"


AUDIO_BLOCK_OPTIONS = {
    "album",
    "name",
    "title",
    "title-en",
    "voice",
    "multiline",
    "spotify",
    "youtube-music",
    "track",
}
BANNED_EXAMPLE_CHARS = ("`", "{", "}")


def find_audio_examples(body: str):
    """Yield {'options': dict, 'body': [lines], 'line': n} per audio-examples block.

    ADR-0006 content form: the block holds the track (options + example pairs).
    Canonical fences only (three colons, unindented), and the validator polices
    the canonical form the engine's parser accepts more leniently.
    """
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() != ":::{audio-examples}":
            i += 1
            continue
        start = i
        i += 1
        options: dict[str, str] = {}
        while i < len(lines):
            m = re.match(r"^:([\w-]+):\s*(.*)$", lines[i].strip())
            if not m or m.group(1) not in AUDIO_BLOCK_OPTIONS:
                break
            options[m.group(1)] = m.group(2).strip().strip("<>")
            i += 1
        block_body: list[str] = []
        while i < len(lines) and lines[i].strip() != ":::":
            block_body.append(lines[i])
            i += 1
        yield {"options": options, "body": block_body, "line": start + 1}
        i += 1


def _example_pairs(rep: Report, where: str, body: list[str], multiline: bool) -> int:
    """Grammar-check the example body; return the number of pairs."""
    for raw in body:
        line = raw.strip()
        if any(c in line for c in BANNED_EXAMPLE_CHARS):
            rep.error(
                f"{where}: example line contains banned char (` {{ }}): "
                f"plain text only, it is fed to TTS verbatim: {line[:50]!r}"
            )
            return 0
    if multiline:
        groups: list[list[str]] = [[]]
        for raw in body:
            if raw.strip():
                groups[-1].append(raw.strip())
            elif groups[-1]:
                groups.append([])
        groups = [g for g in groups if g]
        for g in groups:
            natives = [ln for ln in g if not ln.startswith(":")]
            translations = [ln for ln in g if ln.startswith(":")]
            if not natives or not translations:
                rep.error(
                    f"{where}: multiline example needs native lines then "
                    "':'-prefixed translation lines"
                )
        return len(groups)
    pairs = 0
    pending = None
    for raw in body:
        line = raw.strip()
        if not line:
            if pending:
                rep.error(
                    f"{where}: native line without ': translation': {pending[:50]!r}"
                )
                pending = None
            continue
        if line.startswith(":"):
            if pending is None:
                rep.error(f"{where}: ': translation' line without a native line above")
            else:
                pairs += 1
                pending = None
        else:
            if pending is not None:
                rep.error(
                    f"{where}: two consecutive native lines: missing translation "
                    f"after {pending[:50]!r}"
                )
            pending = line
    if pending:
        rep.error(f"{where}: native line without ': translation': {pending[:50]!r}")
    return pairs


def check_audio_wiring(rep: Report, block: dict, path: Path, workspace: Path | None):
    opts = block["options"]
    where = f"audio-examples (line {block['line']})"
    if "track" in opts:
        rep.error(
            f"{where}: legacy ADR-0002 :track: pointer: the block itself must "
            "hold the track content (ADR-0006); run the authoring skill's "
            "block format"
        )
        return
    album = opts.get("album")
    if not album:
        rep.error(f"{where}: missing required :album: backlink")
        return
    if not opts.get("title"):
        rep.error(
            f"{where}: missing required :title: (native title, spoken in the intro)"
        )
    if not opts.get("title-en"):
        rep.warn(f"{where}: no :title-en: (store title falls back to the native title)")
    name = opts.get("name") or path.stem

    n_pairs = _example_pairs(rep, where, block["body"], "multiline" in opts)
    if "multiline" not in opts and 0 < n_pairs < 8:
        rep.warn(
            f"{where}: only {n_pairs} examples (over-author ~12-18 for the 70s budget)"
        )

    if not workspace:
        rep.warn("cannot wiring-check audio-examples (workspace unknown)")
        return
    album_dir = workspace / "albums" / album
    manifest = album_dir / "album.yml"
    if not album_dir.is_dir():
        rep.error(f"{where}: album dir missing: albums/{album}")
        return
    if not manifest.exists():
        rep.error(f"{where}: no album.yml in albums/{album}")
    else:
        meta = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
        for key in ("title", "voice"):
            if key not in meta:
                rep.error(f"albums/{album}/album.yml missing required key: {key}")
        for key in ("level", "category", "language"):
            if key in meta:
                rep.error(
                    f"albums/{album}/album.yml must not store '{key}' "
                    "(derived from path / open-language.yml)"
                )
        if name not in (meta.get("tracks") or []):
            rep.error(
                f"{where}: track name '{name}' not listed in "
                f"albums/{album}/album.yml tracks:"
            )
    if not (opts.get("spotify") or opts.get("youtube-music")):
        rep.info(f"{where}: no streaming links yet (pending release)")


def check_doc_links(rep: Report, body: str, workspace: Path | None):
    if not workspace:
        return
    docs = workspace / "docs"
    for m in re.finditer(r"\]\((/[^)#\s]+\.md)(#[^)]*)?\)", body):
        target = docs / m.group(1).lstrip("/")
        if not target.exists():
            rep.error(f"broken doc link: {m.group(1)}")


def check_common(rep: Report, body: str):
    """Convention checks shared by articles and indexes."""
    if "{practice}" in body:
        rep.error(
            "contains a {practice} block: ChatGPT practice sections are banned "
            "(keep learners on our platforms)"
        )
    if "<!--" in body:
        rep.error("contains an HTML comment: comments leak into the built HTML")
    if re.search(r"content agents?", body, re.I):
        rep.error("mentions 'content agents': tooling wording is never reader-facing")
    if re.search(r"\ba\d-outline\.yml", body, re.I):
        rep.error(
            "references a private planning file (outline yml) in user-facing content"
        )
    if ":::{seealso}" in body or "```{seealso}" in body:
        rep.error(
            "uses a seealso block: use a Prerequisites admonition (true dependency) "
            "or Related articles (everything else)"
        )
    if "{{" in body:
        rep.error("unfilled {{PLACEHOLDER}} left in file")
    for i, line in enumerate(body.splitlines(), 1):
        # Sphinx generates prev/next navigation from the toctree and the theme
        # renders it in the page footer. Hand-written neighbour links duplicate
        # it and go stale whenever the curriculum order changes.
        if re.match(r"^\s*[-*]\s*\**(next|previous|prev)\b[^:\n]{0,20}:", line, re.I):
            rep.error(
                f"manual navigation link on line {i} - never hand-write "
                "'Previous'/'Next' links; Sphinx generates prev/next from the "
                "toctree automatically. Related articles is for non-adjacent "
                "links only"
            )
            break
    for i, line in enumerate(body.splitlines(), 1):
        if "\u2014" in line:
            # Frozen store titles inside audio-examples options may carry em
            # dashes (published track titles are never retitled); prose may not.
            if re.match(r"^:title(-en)?:", line.strip()):
                continue
            rep.error(
                f"em dash on line {i} - never use em dashes; restructure the sentence"
            )
            break


_SECOND_PERSON = re.compile(r"\byou(?:r|rs|rself)?\b", re.I)
# Stock openers. Any of these becomes "the phrase every article starts with",
# which is the failure mode regardless of whether it says "you" (rule 18).
_STOCK_OPENER = re.compile(
    r"^\s*(after this (page|article)|by the end of th|in this (page|article)"
    r"|(this (page|article) )?(will )?teach(es)? you|learn how to|get started with"
    r"|welcome to|this (page|article) (shows|gives|helps) you)",
    re.I,
)


def check_direct_address(rep: Report, body: str):
    """Rule 18: body prose does not address the reader.

    Only the LEAD paragraph and H2/H3 headings are checked. Admonitions, example
    translations and glosses legitimately keep "you" (it is the English of
    du/Sie), and generic "you" describing real German use is allowed, so a
    whole-file sweep would be all false positives.
    """
    # Headings are a WARN, not an ERROR: concepts name a functional ability, and
    # "Saying who you are" is the category's framing rather than the instructional
    # address rule 18 targets. Flag it for a human, do not fail the build.
    for h in headings(body, 2) + headings(body, 3):
        if _SECOND_PERSON.search(h):
            rep.warn(
                f"heading addresses the reader: '{h}' - fine when it names a "
                "functional ability, wrong when it coaches ('The letters that "
                "trip you up'). Judgement call (rule 18)"
            )

    m = re.search(r"^# [^\n]+\n+", body, re.M)
    if not m:
        return
    lead, depth = [], 0
    for line in body[m.end() :].splitlines():
        s = line.strip()
        if s.startswith("#"):
            break
        if s.startswith(":::"):
            depth += -1 if (depth and re.fullmatch(r":{3,}", s)) else 1
            continue
        if depth or s.startswith((":", "|", ">", "-", "*")):
            continue
        if not s:
            if lead:
                break
            continue
        lead.append(s)
    text = " ".join(lead)
    if not text:
        return
    if _STOCK_OPENER.match(text):
        rep.error(
            f"lead paragraph uses a stock opener ('{text[:40]}...') - open on the "
            "content itself: the situation, the pattern, or the key word. Swapping "
            "one formula for another is the same problem (rule 18)"
        )
    elif _SECOND_PERSON.search(text):
        # WARN, not ERROR: generic "you" describing real German use is allowed, and
        # a lead may legitimately quote the word ("two words for *you*") or an
        # article title ("builds on introducing yourself"). A human decides.
        rep.warn(
            "lead paragraph uses 'you' - fine if it describes what a German "
            "speaker does, wrong if it addresses the reader about the course "
            "('you will learn', 'the forms you already know'). Check it (rule 18)"
        )


def headings(body: str, level: int = 2):
    prefix = "#" * level + " "
    return [
        line[len(prefix) :].strip()
        for line in body.splitlines()
        if line.startswith(prefix)
    ]


def validate_article(path: Path, ctype: str, workspace: Path | None) -> Report:
    rep = Report(path)
    spec = SPECS["types"].get(ctype)
    if spec is None:
        rep.error(f"unknown content type: {ctype}")
        return rep
    common = SPECS["common"]
    text = path.read_text(encoding="utf-8")
    if text.startswith("﻿"):
        rep.warn("file starts with a BOM (\\ufeff): remove it")
    fm, body = split_frontmatter(text)

    if len(body.strip()) < STUB_BODY_BYTES:
        rep.info("STUB: not yet authored (skipping template checks)")
        # even stubs must not leak notes into the built HTML
        if "<!--" in body:
            rep.error(
                "stub contains an HTML comment: comments leak into the built HTML"
            )
        return rep

    # frontmatter
    if fm is None:
        rep.error("missing YAML frontmatter (--- block)")
    elif "__parse_error__" in fm:
        rep.error(f"frontmatter does not parse: {fm['__parse_error__']}")
    else:
        if "html_meta" in fm:
            rep.error("top-level 'html_meta' is deprecated: nest it under 'myst:'")
        hm = (fm.get("myst") or {}).get("html_meta") or fm.get("html_meta") or {}
        desc = hm.get("description", "")
        if not desc:
            rep.error("html_meta.description missing/empty")
        elif len(desc) > common["description_max_chars"]:
            rep.warn(
                f"html_meta.description is {len(desc)} chars (aim <= {common['description_max_chars']})"
            )
        if not hm.get("keywords"):
            rep.error("html_meta.keywords missing/empty")

    check_common(rep, body)

    # H1: exactly one, no blockquote subtitle beneath it, must be followed by prose
    h1s = headings(body, 1)
    if len(h1s) != 1:
        rep.error(f"expected exactly one H1, found {len(h1s)}")
    if re.search(r"^# [^\n]+\n+> ", body, re.M):
        rep.error(
            "blockquote subtitle under the H1: subtitles were removed; "
            "English titles are self-explanatory"
        )
    if re.search(r"^# [^\n]+\n+#{1,6} ", body, re.M):
        rep.error(
            "H1 is immediately followed by a heading with no intro paragraph: "
            "add at least one sentence of plain prose under the title before any subheading"
        )

    check_direct_address(rep, body)

    # required section headings
    h2s = headings(body, 2)
    for pattern in spec.get("required_headings", []):
        if not any(re.search(pattern, h) for h in h2s):
            rep.error(f"missing required section heading matching: {pattern}")

    # standardized example format
    n_divs = len(re.findall(r":::\{div\}\s+ol-examples", body))
    if spec.get("require_examples_div") and n_divs == 0:
        rep.error(
            "no ':::{div} ol-examples' block: example pairs must use the "
            "standardized definition-list format"
        )
    # legacy bullet example pairs (native line + italic translation line)
    if re.search(r"^- [^\n]*\n  \*[^\n]*\*\s*$", body, re.M):
        rep.warn(
            "bullet-style example pairs found: convert to the ol-examples "
            "definition-list format"
        )

    if spec.get("require_summary_admonitions") and "admonition} Key points" not in body:
        rep.error("Summary lacks ':::{admonition} Key points' block")
    if (
        spec.get("require_common_mistakes")
        and "admonition} Common mistakes" not in body
    ):
        rep.error("Summary lacks ':::{admonition} Common mistakes' block")

    # english filename rule
    if spec.get("english_filename") and re.search(r"[äöüß]", path.stem):
        rep.error("filename must be English kebab-case (found umlaut/ß)")

    # "Hear it in practice" section order: heading before Summary, above the block
    hear = "## Hear it in practice"
    if (
        hear in body
        and "## Summary" in body
        and body.index(hear) > body.index("## Summary")
    ):
        rep.error("the 'Hear it in practice' section must come BEFORE Summary")

    # audio-examples blocks
    blocks = list(find_audio_examples(body))
    if len(blocks) < spec.get("min_audio_examples", 0):
        rep.error(
            f"needs >= {spec['min_audio_examples']} audio-examples block(s), found {len(blocks)} "
            "(every article carries its track)"
        )
    for block in blocks:
        check_audio_wiring(rep, block, path, workspace)

    if common.get("check_doc_links"):
        check_doc_links(rep, body, workspace)

    return rep


def validate_index(path: Path, ctype: str | None, workspace: Path | None) -> Report:
    rep = Report(path)
    text = path.read_text(encoding="utf-8")
    _fm, body = split_frontmatter(text)
    check_common(rep, body)

    # title rules: no CEFR level in category/subcategory index titles
    h1s = headings(body, 1)
    is_level_index = path.parent.parent.name == "docs"
    if h1s and not is_level_index and re.match(r"^[ABC][12]\b", h1s[0]):
        rep.error(
            f"index title '{h1s[0]}' contains the CEFR level: use the bare "
            "section name (e.g. 'Grammar')"
        )

    # References/Additional reading placement
    if not is_level_index and re.search(
        r"^## (References|Additional reading)", body, re.M
    ):
        rep.error(
            "external-links section belongs in the LEVEL index "
            "(docs/<level>/index.md, '## Additional reading'), not here"
        )

    m = re.search(r"```\{toctree\}\s*\n(.*?)```", body, re.S)
    if not m:
        rep.error("no toctree found")
        return rep
    # grammar subcategory indexes must explain their concept group
    if ctype == "grammar":
        h1_match = re.search(r"^# [^\n]+\n", body, re.M)
        if h1_match:
            between = body[h1_match.end() : body.index("```{toctree}")]
            if not between.strip():
                rep.error(
                    "index has no explanation paragraph - add 1-3 sentences on what "
                    "this grammar concept group is"
                )
    entries = [
        line.strip()
        for line in m.group(1).splitlines()
        if line.strip() and not line.strip().startswith(":")
    ]
    if not entries:
        rep.error("toctree is empty")
    directory = path.parent
    for e in entries:
        if not (
            (directory / f"{e}.md").exists()
            or (directory / e).with_suffix(".md").exists()
        ):
            rep.error(f"toctree entry does not resolve: {e}")
    listed = set(entries)
    for f in sorted(directory.glob("*.md")):
        if f.name != "index.md" and f.stem not in listed:
            rep.warn(f"article not in toctree (orphan): {f.name}")
    for d in sorted(p for p in directory.iterdir() if p.is_dir()):
        if (d / "index.md").exists() and f"{d.name}/index" not in listed:
            rep.warn(f"subcategory not in toctree: {d.name}/index")
    if ctype and SPECS["types"].get(ctype, {}).get("ordered"):
        rep.info(
            "ordered category: toctree order IS the learning sequence: review deliberately"
        )
    if check_links := SPECS["common"].get("check_doc_links"):
        _ = check_links
        check_doc_links(rep, body, workspace)
    return rep


def validate_file(
    path: Path, workspace: Path | None = None, ctype: str | None = None
) -> Report:
    """Validate one article or index file and return its report."""
    ws, _level, category = infer_context(path, workspace)
    ctype = ctype or category
    if path.name == "index.md":
        return validate_index(path, ctype, ws)
    if ctype is None:
        rep = Report(path)
        rep.error("cannot infer content type from path; pass --type")
        return rep
    return validate_article(path, ctype, ws)


def report_status(rep: Report) -> str:
    """OK, STUB or FAIL, as printed in the summary line."""
    if rep.failed:
        return "FAIL"
    return "STUB" if any("STUB" in m for _, m in rep.items) else "OK"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="language workspace root (contains docs/ and albums/)",
    )
    ap.add_argument(
        "--type",
        choices=CATEGORIES,
        default=None,
        help="override content type inferred from path",
    )
    args = ap.parse_args(argv)

    any_error = False
    for path in args.files:
        if not path.exists():
            print(f"ERROR {path}: file not found")
            any_error = True
            continue
        rep = validate_file(path, args.workspace, args.type)
        status = report_status(rep)
        print(f"[{status}] {path}")
        for lvl, msg in rep.items:
            print(f"    {lvl}: {msg}")
        any_error |= rep.failed
    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main())
