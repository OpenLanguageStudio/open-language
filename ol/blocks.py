"""Read ``audio-examples`` blocks and the refusals the app and the checks report."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from importlib.resources import files
from pathlib import Path
from typing import ClassVar, NamedTuple

import yaml
from markdown_it import MarkdownIt
from mdit_py_plugins.colon_fence import colon_fence_plugin


class BlockFormatError(ValueError):
    """A block's examples cannot be read: a sentence or a translation is missing."""


class Example(NamedTuple):
    """One sentence in the language being taught, its translation and who says it.

    Args:
        sentence: The sentence, as the page gives it.
        translation: The English translation.
        presenter: The slug of the presenter who says it, worked out from the
            block's mode and ``:presenters:``. Empty when nothing names one,
            such as in a block refused as ``missing_presenters``.
        group: The pair, exchange or message thread the example belongs to,
            counted from 1. In ``examples`` and ``passage`` each example is its
            own group. ``0`` for an example that is not read from a block.
    """

    sentence: str
    translation: str
    presenter: str = ""
    group: int = 0


#: How many presenters each mode takes: the fewest, and the most or ``None``.
MODES: dict[str, tuple[int, int | None]] = {
    "examples": (1, 1),
    "pairs": (1, 2),
    "dialogue": (2, None),
    "passage": (1, 1),
    "correspondence": (2, None),
}
#: The modes in which the body names who says each example.
NAMED_MODES: frozenset[str] = frozenset({"dialogue", "correspondence"})


@dataclass(frozen=True)
class Block:
    """One ``audio-examples`` block as a page wrote it.

    Args:
        page: The page's name in the build, such as ``a2/grammar/weil``.
        line: The line of the page the block starts on.
        address: The track's address, ``level/category/name``, or ``None``
            when the block has no usable ``:track:``.
        title: The ``:title:``, or ``None`` when the block gives none.
        title_en: The ``:title-en:``, or ``None`` when the block gives none.
        tags: The ``:tags:``, as written.
        examples: The examples, in the order the page gives them, each with
            its presenter and group.
        mode: The ``:mode:``, one of ``MODES`` unless the block is refused as
            ``unknown_mode``. ``examples`` when the block gives none.
        presenters: The ``:presenters:`` slugs, in the order the block lists
            them. The first speaks the track's spoken title.
        duplicate: Whether the block carries ``:duplicate:``.
        refusals: The codes of the refusals the block earns on its own.
    """

    page: str
    line: int
    address: str | None
    title: str | None
    title_en: str | None
    tags: tuple[str, ...]
    examples: tuple[Example, ...]
    mode: str
    presenters: tuple[str, ...]
    duplicate: bool
    refusals: tuple[str, ...]

    @property
    def level(self) -> str | None:
        """The level part of the address."""
        return self.address.split("/")[0] if self.address else None

    @property
    def category(self) -> str | None:
        """The category part of the address."""
        return self.address.split("/")[1] if self.address else None

    @property
    def name(self) -> str | None:
        """The name part of the address."""
        return self.address.split("/")[2] if self.address else None

    @property
    def writes(self) -> bool:
        """Whether the block writes its track: it gives examples and is no duplicate.

        A block writes whatever else it is refused for, apart from a bad address.
        """
        return bool(self.address and self.examples and not self.duplicate)


@dataclass(frozen=True)
class Refusal:
    """A block the checks reject, and the code naming why.

    Args:
        block: The block refused.
        code: One of ``CODES``.
    """

    block: Block
    code: str

    DETAILS: ClassVar[dict[str, str]] = {
        "unknown_option": (
            "The block has an option it does not take. A block takes :track:, "
            ":title:, :title-en:, :tags:, :mode:, :presenters: and :duplicate:."
        ),
        "bad_address": (
            "The block has no :track:, or its value is not a level, a category "
            "and a name separated by /, in lower case."
        ),
        "unknown_mode": (
            "The block's :mode: is not examples, pairs, dialogue, passage or "
            "correspondence."
        ),
        "missing_examples": (
            "The block gives no examples and is not a :duplicate:. Add the "
            "examples, or add :duplicate: if another block writes the track."
        ),
        "duplicate_writes": (
            "A :duplicate: block writes nothing, so it cannot give examples, a "
            "title, an English title, a mode or presenters."
        ),
        "missing_presenters": (
            "The block writes its track but has no :presenters:. Name the "
            "presenter who says it, or the presenters, separated by commas."
        ),
        "bad_presenters": (
            "A :presenters: value is not a slug, a presenter is named twice, or "
            "the number of presenters is wrong for the mode: one for examples "
            "and passage, one or two for pairs, two or more for dialogue and "
            "correspondence."
        ),
        "bad_pair": (
            "A pairs block is groups of exactly two examples, separated by a "
            "blank line. One of its groups is not."
        ),
        "presenter_not_listed": (
            "An example names a presenter the block's :presenters: does not list."
        ),
        "presenter_silent": (
            "A presenter the block's :presenters: lists says nothing in it."
        ),
        "sentence_twice": (
            "The block gives the same sentence more than once, once spacing and "
            "emphasis are tidied."
        ),
        "written_twice": (
            "More than one block writes this track. Let one page write it and "
            "give the others :duplicate:."
        ),
        "orphan_duplicate": (
            "This :duplicate: block names a track no block writes. Write the "
            "track on one page."
        ),
        "unknown_presenter": (
            "The block names a presenter this language does not have."
        ),
    }
    CODES: ClassVar[frozenset[str]] = frozenset(DETAILS)
    #: The codes only the app reports, because only it knows the presenters.
    APP_ONLY: ClassVar[frozenset[str]] = frozenset({"unknown_presenter"})
    CROSS_PAGE: ClassVar[frozenset[str]] = frozenset(
        {"written_twice", "orphan_duplicate"}
    )

    @property
    def detail(self) -> str:
        """What is wrong with the block, for an author."""
        return self.DETAILS[self.code]


class BlockReader:
    """Read ``audio-examples`` blocks into ``Block`` objects.

    Subclass it and override a method to read blocks differently.
    """

    DIRECTIVE: ClassVar[str] = "audio-examples"
    OPTIONS: ClassVar[frozenset[str]] = frozenset(
        {"track", "title", "title-en", "tags", "mode", "presenters", "duplicate"}
    )
    SLUG: ClassVar[re.Pattern] = re.compile(r"[-a-z0-9_]+")
    #: A body line that names a presenter: a slug and a colon, then the sentence
    #: in ``dialogue`` or nothing in ``correspondence``. A translation line
    #: starts with a colon, and a sentence in the language taught does not
    #: start with a lower-case word run into a colon.
    NAMED_LINE: ClassVar[re.Pattern] = re.compile(r"([-a-z0-9_]+):(?:\s+(.*))?")
    # Example text reaches speech verbatim, so role markup and code are refused.
    BANNED: ClassVar[tuple[str, ...]] = ("`", "{", "}")
    ROLE: ClassVar[re.Pattern] = re.compile(r"\{[a-z-]+\}`([^`]*)`")
    markdown: ClassVar[MarkdownIt] = MarkdownIt("commonmark").use(colon_fence_plugin)

    def read(
        self,
        page: str,
        options: Mapping[str, str | None],
        body: Sequence[str],
        line: int = 0,
    ) -> Block:
        """Read one block from its options and the lines of its body.

        Args:
            page: The page's name in the build, such as ``a2/grammar/weil``.
            options: Each option the block carries, by name. A flag's value is
                ignored, so docutils' ``None`` and an empty string both set it.
            body: The lines after the options.
            line: The line of the page the block starts on.

        Returns:
            The block, with the refusals it earns on its own.

        Raises:
            BlockFormatError: When the body cannot be read as examples.
        """
        tags = (tag.strip() for tag in (options.get("tags") or "").split(","))
        listed = (slug.strip() for slug in (options.get("presenters") or "").split(","))
        mode = (options.get("mode") or "").strip() or "examples"
        block = Block(
            page=page,
            line=line,
            address=self.address(options.get("track") or ""),
            title=(options.get("title") or "").strip() or None,
            title_en=(options.get("title-en") or "").strip() or None,
            tags=tuple(tag for tag in tags if tag),
            examples=(),
            mode=mode,
            presenters=tuple(slug for slug in listed if slug),
            duplicate="duplicate" in options,
            refusals=(),
        )
        if mode in MODES:
            examples = self.examples(body, mode, f"{page}:{line}")
            block = replace(block, examples=tuple(self.assign(block, examples)))
        return replace(block, refusals=tuple(self.refusals(block, options)))

    def address(self, value: str) -> str | None:
        """Read a ``:track:`` value as an address.

        The name is never taken from the page, so a page can be renamed, moved
        or given a second block without changing which track a block names.

        Args:
            value: The option's value.

        Returns:
            ``level/category/name``, or ``None`` when the value is not three
            lower-case names separated by ``/``.
        """
        parts = value.strip().split("/")
        if len(parts) != 3 or not all(self.SLUG.fullmatch(part) for part in parts):
            return None
        return "/".join(parts)

    def refusals(self, block: Block, options: Mapping[str, str | None]) -> list[str]:
        """List the refusals a block earns on its own, in the order they are checked.

        A block with a bad address earns nothing more, because it names no
        track to check against, and nor does a block with an unknown mode,
        because its body is not read.

        Args:
            block: The block as read, with no refusals yet.
            options: Every option the block carries, by name.

        Returns:
            The refusal codes.
        """
        found = []
        if set(options) - self.OPTIONS:
            found.append("unknown_option")
        if block.address is None:
            found.append("bad_address")
        elif block.mode not in MODES:
            found.append("unknown_mode")
        elif block.duplicate:
            gives = block.examples or block.title or block.title_en
            if gives or "mode" in options or "presenters" in options:
                found.append("duplicate_writes")
        elif not block.examples:
            found.append("missing_examples")
        else:
            found += self.presenter_refusals(block)
            if block.mode == "pairs" and self.bad_pairs(block):
                found.append("bad_pair")
            if block.mode == "examples" and self.sentence_given_twice(block):
                found.append("sentence_twice")
        return found

    def presenter_refusals(self, block: Block) -> list[str]:
        """List the refusals a block that writes earns for its presenters.

        Args:
            block: The block as read.

        Returns:
            The refusal codes, in the order they are checked.
        """
        listed = block.presenters
        if not listed:
            return ["missing_presenters"]
        found = []
        fewest, most = MODES[block.mode]
        if (
            not all(self.SLUG.fullmatch(slug) for slug in listed)
            or len(set(listed)) < len(listed)
            or len(listed) < fewest
            or (most is not None and len(listed) > most)
        ):
            found.append("bad_presenters")
        if block.mode in NAMED_MODES:
            named = {example.presenter for example in block.examples}
            if named - set(listed):
                found.append("presenter_not_listed")
            if set(listed) - named:
                found.append("presenter_silent")
        return found

    @staticmethod
    def bad_pairs(block: Block) -> bool:
        """Whether a ``pairs`` block has a group that is not two examples.

        Args:
            block: The block as read.

        Returns:
            ``True`` when any group holds one example, or more than two.
        """
        sizes = Counter(example.group for example in block.examples)
        return any(size != 2 for size in sizes.values())

    def sentence_given_twice(self, block: Block) -> bool:
        """Whether a block gives one sentence twice, once it is tidied.

        Args:
            block: The block as read.

        Returns:
            ``True`` when two of its sentences have one ``sentence_key``.
        """
        keys = [self.sentence_key(example.sentence) for example in block.examples]
        return len(set(keys)) < len(keys)

    @staticmethod
    def assign(block: Block, examples: Sequence[Example]) -> list[Example]:
        """Give each example the presenter who says it.

        In ``examples`` and ``passage`` the one presenter says every example.
        In ``pairs`` the first presenter says the first example of every pair
        and the second presenter the second, or the one presenter both. In
        ``dialogue`` and ``correspondence`` the body names the presenter, so
        the example keeps it.

        Args:
            block: The block as read, with its mode and presenters.
            examples: The examples as the body gives them, each with its group.

        Returns:
            The examples, each with its presenter.
        """
        if block.mode in NAMED_MODES:
            return list(examples)
        listed = block.presenters or ("",)
        assigned = []
        place: Counter[int] = Counter()
        for example in examples:
            index = place[example.group] if block.mode == "pairs" else 0
            place[example.group] += 1
            presenter = listed[min(index, len(listed) - 1)]
            assigned.append(example._replace(presenter=presenter))
        return assigned

    @staticmethod
    def sentence_key(text: str) -> str:
        """Return what identifies a sentence within its track.

        The text is put in one Unicode form, the emphasis marks ``*`` and ``_``
        are removed and every run of spacing, new lines included, becomes one
        space. Case and punctuation stay, so "Du kommst." and "Du kommst?" are
        two sentences.

        Args:
            text: A sentence as a page gives it.

        Returns:
            The sentence's key.
        """
        text = unicodedata.normalize("NFC", text).replace("*", "").replace("_", "")
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def spoken(cls, text: str) -> str:
        """Return a sentence of an ``ol-examples`` block as a presenter says it.

        A page may mark up these sentences, so the roles go as well as what
        ``sentence_key`` removes.

        Args:
            text: A sentence as a page gives it.

        Returns:
            The sentence with its roles and emphasis removed and its spacing
            tidied.
        """
        return cls.sentence_key(cls.ROLE.sub(r"\1", text))

    def examples(self, body: Sequence[str], mode: str, where: str) -> list[Example]:
        """Read a block's body as examples, the way its mode writes them.

        In ``examples``, ``pairs`` and ``dialogue`` a sentence is followed by
        its translation on the next line after ``: ``. A blank line ends a pair
        or an exchange, and in ``examples`` it only separates. In ``dialogue``
        each sentence opens with its presenter's slug and a colon. In
        ``passage`` each example is sentence lines then translation lines,
        separated from the next by a blank line, and keeps its line breaks. In
        ``correspondence`` each message opens with a line holding only its
        presenter's slug and a colon.

        Args:
            body: The lines after the options.
            mode: The block's mode, one of ``MODES``.
            where: The page and line, for the error message.

        Returns:
            The examples, in order, each with its group, and with its presenter
            where the body names one.

        Raises:
            BlockFormatError: When a sentence has no translation, a translation
                has no sentence, a line holds markup, or a line that should
                name a presenter does not.
        """
        lines = [raw.strip() for raw in body]
        for offset, line in enumerate(lines, start=1):
            if any(char in line for char in self.BANNED):
                msg = (
                    f"{where} (body line {offset}): example lines are plain text, "
                    f"with no markup: {line!r}"
                )
                raise BlockFormatError(msg)
        if mode == "passage":
            return self.passage_examples(lines, where)
        if mode == "correspondence":
            return self.correspondence_examples(lines, where)
        examples = self.single_line_examples(lines, where, mode == "dialogue")
        if mode == "examples":
            return [
                example._replace(group=number)
                for number, example in enumerate(examples, start=1)
            ]
        return examples

    def single_line_examples(
        self, lines: list[str], where: str, named: bool = False
    ) -> list[Example]:
        """Read examples of one sentence line and one translation line each.

        Args:
            lines: The body's lines, stripped.
            where: The page and line, for the error message.
            named: Whether each sentence opens with its presenter's slug and a
                colon, as in ``dialogue``.

        Returns:
            The examples, in order, each numbered with the group of examples
            between blank lines it is in.

        Raises:
            BlockFormatError: When a sentence has no translation, a translation
                has no sentence, or a sentence names no presenter where it must.
        """
        examples = []
        sentence = None
        presenter = ""
        group = 1
        for offset, line in enumerate(lines, start=1):
            at = f"{where} (body line {offset})"
            if line.startswith(":"):
                translation = line[1:].strip()
                if sentence is None or not translation:
                    msg = f"{at}: a translation needs a sentence on the line above"
                    raise BlockFormatError(msg)
                examples.append(Example(sentence, translation, presenter, group))
                sentence = None
            elif sentence is not None:
                msg = f"{at}: the sentence {sentence!r} has no ': translation' line"
                raise BlockFormatError(msg)
            elif not line:
                if examples and examples[-1].group == group:
                    group += 1
            elif named:
                match = self.NAMED_LINE.fullmatch(line)
                if match is None or not match.group(2):
                    msg = (
                        f"{at}: a dialogue sentence opens with its presenter's "
                        f"slug and a colon, such as 'lina: Hallo!': {line!r}"
                    )
                    raise BlockFormatError(msg)
                presenter, sentence = match.group(1), match.group(2).strip()
            else:
                sentence = line
        if sentence is not None:
            msg = f"{where}: the sentence {sentence!r} has no ': translation' line"
            raise BlockFormatError(msg)
        return examples

    def passage_examples(self, lines: list[str], where: str) -> list[Example]:
        """Read examples of several sentence lines then several translation lines.

        A blank line ends an example only where the next line is a sentence and
        the example already has a translation. Any other blank line is inside
        the example: a paragraph break, kept as one empty line however many
        there are, or nothing at all between the sentences and the translations.

        Args:
            lines: The body's lines, stripped.
            where: The page and line, for the error message.

        Returns:
            The examples, in order, each keeping its line breaks and paragraphs
            and each its own group.

        Raises:
            BlockFormatError: When a group is not sentence lines followed by
                translation lines.
        """
        refused = (
            "{where} (body line {offset}): an example is sentence lines, then "
            "': translation' lines, then a blank line"
        )
        texts = []
        sentences: list[str] = []
        translations: list[str] = []
        blank = False
        for offset, line in enumerate(lines, start=1):
            if not line:
                blank = True
                continue
            is_translation = line.startswith(":")
            text = line[1:].strip() if is_translation else line
            ended = translations and not is_translation
            if not text or (is_translation and not sentences) or (ended and not blank):
                raise BlockFormatError(refused.format(where=where, offset=offset))
            if ended:
                texts.append(("\n".join(sentences), "\n".join(translations)))
                sentences, translations = [], []
                blank = False
            part = translations if is_translation else sentences
            part += ["", text] if blank and part else [text]
            blank = False
        if sentences and not translations:
            raise BlockFormatError(refused.format(where=where, offset=len(lines)))
        if sentences:
            texts.append(("\n".join(sentences), "\n".join(translations)))
        return [
            Example(sentence, translation, group=number)
            for number, (sentence, translation) in enumerate(texts, start=1)
        ]

    def correspondence_examples(self, lines: list[str], where: str) -> list[Example]:
        """Read messages, each opened by a line holding only its writer's slug.

        A line such as ``lina:`` starts a message and the next such line starts
        the next. Between them come the message's sentence lines and then its
        translation lines, read as one ``passage`` example. The messages are one
        thread, so all are in group 1.

        Args:
            lines: The body's lines, stripped.
            where: The page and line, for the error message.

        Returns:
            The messages, in order, each with its writer as its presenter.

        Raises:
            BlockFormatError: When the body does not open with a slug line, or a
                message is not sentence lines followed by translation lines.
        """
        messages: list[tuple[str, int, list[str]]] = []
        for offset, line in enumerate(lines, start=1):
            match = self.NAMED_LINE.fullmatch(line)
            if match is not None and match.group(2) is None:
                messages.append((match.group(1), offset, []))
            elif messages:
                messages[-1][2].append(line)
            elif line:
                msg = (
                    f"{where} (body line {offset}): a message opens with a line "
                    f"holding only its writer's slug and a colon, such as "
                    f"'lina:': {line!r}"
                )
                raise BlockFormatError(msg)
        examples = []
        for presenter, offset, text in messages:
            read = self.passage_examples(
                text, f"{where} (message at body line {offset})"
            )
            if len(read) != 1:
                msg = (
                    f"{where} (body line {offset}): a message is sentence lines, "
                    "then ': translation' lines, and the next message opens with "
                    "its writer's slug"
                )
                raise BlockFormatError(msg)
            examples.append(read[0]._replace(presenter=presenter, group=1))
        return examples

    def find(self, page: str, text: str) -> list[Block]:
        """Read every block on a page.

        Args:
            page: The page's name in the build.
            text: The page's Markdown. A block quoted inside a code fence is
                not a block.

        Returns:
            The page's blocks, in order.

        Raises:
            BlockFormatError: When a block's body cannot be read as examples.
        """
        lines = text.splitlines()
        blocks = []
        for token in self.markdown.parse(text):
            if token.type != "colon_fence" or token.map is None:
                continue
            if token.info.strip() != f"{{{self.DIRECTIVE}}}":
                continue
            start, end = token.map
            content = lines[start + 1 : end - 1]
            options, body_start = self.options(content)
            blocks.append(self.read(page, options, content[body_start:], start + 1))
        return blocks

    def options(self, lines: Sequence[str]) -> tuple[dict[str, str], int]:
        """Read the ``:name: value`` lines that open a block.

        Args:
            lines: The lines between the block's fences.

        Returns:
            The options by name, and the index of the first body line.
        """
        options: dict[str, str] = {}
        for index, raw in enumerate(lines):
            match = re.fullmatch(r":([\w-]+):(?:\s+(.*))?", raw.strip())
            if match is None:
                return options, index
            options[match.group(1)] = (match.group(2) or "").strip()
        return options, len(lines)


class BlockCollection:
    """Every block of a build, and the refusals that need more than one page.

    Args:
        blocks: The blocks, in page order.
    """

    def __init__(self, blocks: Iterable[Block]):
        self.blocks = list(blocks)

    @classmethod
    def from_pages(
        cls, pages: Mapping[str, str], reader: BlockReader | None = None
    ) -> BlockCollection:
        """Read the blocks of pages given as Markdown.

        Args:
            pages: Each page's Markdown, by page name.
            reader: The reader to use, a ``BlockReader`` unless given.

        Returns:
            The collection of every block on the pages.

        Raises:
            BlockFormatError: When a block's body cannot be read as examples.
        """
        reader = reader or BlockReader()
        return cls(
            block for page, text in pages.items() for block in reader.find(page, text)
        )

    @classmethod
    def from_docs(
        cls,
        root: Path,
        reader: BlockReader | None = None,
        exclude: Iterable[str] = (),
    ) -> BlockCollection:
        """Read the blocks of every Markdown page under a docs directory.

        A directory whose name starts with ``_`` or ``.``, such as ``_build``,
        is skipped, and so is a file or directory directly under ``root`` whose
        name is in ``exclude``. A page's name is its path below ``root`` without
        ``.md``.

        Args:
            root: The docs directory.
            reader: The reader to use, a ``BlockReader`` unless given.
            exclude: Names directly under ``root`` that are not pages, such as
                ``README.md`` when the docs directory is the repository root.

        Returns:
            The collection of every block under ``root``.

        Raises:
            BlockFormatError: When a block's body cannot be read as examples.
        """
        root = Path(root)
        excluded = set(exclude)
        paths = []
        for directory, dirnames, filenames in root.walk():
            top = directory == root
            dirnames[:] = [
                d
                for d in dirnames
                if not d.startswith(("_", ".")) and not (top and d in excluded)
            ]
            paths.extend(
                directory / f
                for f in filenames
                if f.endswith(".md")
                and not f.startswith(("_", "."))
                and not (top and f in excluded)
            )
        pages = {
            path.relative_to(root).with_suffix("").as_posix(): path.read_text(
                encoding="utf-8"
            )
            for path in sorted(paths)
        }
        return cls.from_pages(pages, reader)

    def refusals(self) -> list[Refusal]:
        """List every refusal of the build: each block's own, then the cross-page ones.

        Of the blocks with one address, more than one that writes is refused as
        ``written_twice``, each of them. A duplicate is refused as
        ``orphan_duplicate`` when no block writes its address, unless it is
        already refused for writing itself.

        Returns:
            The refusals, the blocks' own in page order first.
        """
        found = [
            Refusal(block, code) for block in self.blocks for code in block.refusals
        ]
        groups: dict[str, list[Block]] = {}
        for block in self.blocks:
            if block.address is not None:
                groups.setdefault(block.address, []).append(block)
        for group in groups.values():
            writers = [block for block in group if block.writes]
            if len(writers) > 1:
                found += [Refusal(block, "written_twice") for block in writers]
            if not writers:
                found += [
                    Refusal(block, "orphan_duplicate")
                    for block in group
                    if block.duplicate and "duplicate_writes" not in block.refusals
                ]
        return found


@dataclass(frozen=True)
class Sample:
    """A sample build of one or more pages, and the outcome it should get.

    Args:
        name: The sample's file name without ``.yml``.
        expect: ``accepted``, or the code of the one refusal the pages earn.
        description: What the sample shows.
        pages: Each page's Markdown, by page name.
    """

    name: str
    expect: str
    description: str
    pages: dict[str, str]

    def blocks(self, reader: BlockReader | None = None) -> list[Block]:
        """Read the blocks of the sample's pages.

        Args:
            reader: The reader to use, a ``BlockReader`` unless given.

        Returns:
            The blocks, page by page.
        """
        return BlockCollection.from_pages(self.pages, reader).blocks

    @classmethod
    def load_all(cls) -> list[Sample]:
        """Load the samples shipped in ``ol/authoring/samples/``.

        Returns:
            The samples, ordered by name.
        """
        samples = []
        folder = files("ol.authoring").joinpath("samples")
        for entry in sorted(folder.iterdir(), key=lambda entry: entry.name):
            if not entry.name.endswith(".yml"):
                continue
            data = yaml.safe_load(entry.read_text(encoding="utf-8"))
            samples.append(
                cls(
                    name=entry.name.removesuffix(".yml"),
                    expect=data["expect"],
                    description=data["description"],
                    pages=data["pages"],
                )
            )
        return samples


def load_samples() -> list[Sample]:
    """Load the sample blocks shipped in ``ol/authoring/samples/``.

    Returns:
        The samples, ordered by name.
    """
    return Sample.load_all()
