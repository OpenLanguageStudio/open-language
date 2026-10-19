"""Read ``audio-examples`` blocks and the refusals the app and the checks report."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from importlib.resources import files
from pathlib import Path, PurePosixPath
from typing import ClassVar, NamedTuple

import yaml
from markdown_it import MarkdownIt
from mdit_py_plugins.colon_fence import colon_fence_plugin


class BlockFormatError(ValueError):
    """A block's examples cannot be read: a sentence or a translation is missing."""


class Example(NamedTuple):
    """One sentence in the language being taught and its English translation."""

    sentence: str
    translation: str


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
        examples: The examples, in the order the page gives them.
        multiline: Whether the block carries ``:multiline:``.
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
    multiline: bool
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
            ":title:, :title-en:, :tags:, :multiline: and :duplicate:."
        ),
        "bad_address": (
            "The block has no :track:, or its value is not a level, a category "
            "and a name separated by /, in lower case."
        ),
        "missing_examples": (
            "The block gives no examples and is not a :duplicate:. Add the "
            "examples, or add :duplicate: if another block writes the track."
        ),
        "duplicate_writes": (
            "A :duplicate: block writes nothing, so it cannot give examples, a "
            "title or an English title."
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
    }
    CODES: ClassVar[frozenset[str]] = frozenset(DETAILS)
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
        {"track", "title", "title-en", "tags", "multiline", "duplicate"}
    )
    SLUG: ClassVar[re.Pattern] = re.compile(r"[-a-z0-9_]+")
    # Example text reaches speech verbatim, so role markup and code are refused.
    BANNED: ClassVar[tuple[str, ...]] = ("`", "{", "}")
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
                Its last part names the track when ``:track:`` gives only a
                level and a category.
            options: Each option the block carries, by name. A flag's value is
                ignored, so docutils' ``None`` and an empty string both set it.
            body: The lines after the options.
            line: The line of the page the block starts on.

        Returns:
            The block, with the refusals it earns on its own.

        Raises:
            BlockFormatError: When the body cannot be read as examples.
        """
        multiline = "multiline" in options
        tags = (tag.strip() for tag in (options.get("tags") or "").split(","))
        block = Block(
            page=page,
            line=line,
            address=self.address(page, options.get("track") or ""),
            title=(options.get("title") or "").strip() or None,
            title_en=(options.get("title-en") or "").strip() or None,
            tags=tuple(tag for tag in tags if tag),
            examples=tuple(self.examples(body, multiline, f"{page}:{line}")),
            multiline=multiline,
            duplicate="duplicate" in options,
            refusals=(),
        )
        return replace(block, refusals=tuple(self.refusals(block, options)))

    def address(self, page: str, value: str) -> str | None:
        """Read a ``:track:`` value as an address.

        Args:
            page: The page's name, whose last part is the track's name when the
                value gives only a level and a category.
            value: The option's value.

        Returns:
            ``level/category/name``, or ``None`` when the value is not two or
            three lower-case names separated by ``/``.
        """
        parts = value.strip().split("/")
        if len(parts) == 2:
            parts.append(PurePosixPath(page).name)
        if len(parts) != 3 or not all(self.SLUG.fullmatch(part) for part in parts):
            return None
        return "/".join(parts)

    def refusals(self, block: Block, options: Mapping[str, str | None]) -> list[str]:
        """List the refusals a block earns on its own, in the order they are checked.

        A block with a bad address earns nothing more, because it names no
        track to check against.

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
        elif block.duplicate:
            if block.examples or block.title or block.title_en:
                found.append("duplicate_writes")
        elif not block.examples:
            found.append("missing_examples")
        else:
            keys = [self.sentence_key(example.sentence) for example in block.examples]
            if len(set(keys)) < len(keys):
                found.append("sentence_twice")
        return found

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

    def examples(
        self, body: Sequence[str], multiline: bool, where: str
    ) -> list[Example]:
        """Read a block's body as examples.

        A sentence is followed by its translation on the next line after ``: ``,
        and examples may be separated by blank lines. In a ``:multiline:`` block
        each example is a group of sentence lines then translation lines,
        separated from the next by a blank line, and keeps its line breaks.

        Args:
            body: The lines after the options.
            multiline: Whether the block carries ``:multiline:``.
            where: The page and line, for the error message.

        Returns:
            The examples, in order.

        Raises:
            BlockFormatError: When a sentence has no translation, a translation
                has no sentence, or a line holds markup.
        """
        lines = [raw.strip() for raw in body]
        for offset, line in enumerate(lines, start=1):
            if any(char in line for char in self.BANNED):
                msg = (
                    f"{where} (body line {offset}): example lines are plain text, "
                    f"with no markup: {line!r}"
                )
                raise BlockFormatError(msg)
        if multiline:
            return self.multiline_examples(lines, where)
        return self.single_line_examples(lines, where)

    def single_line_examples(self, lines: list[str], where: str) -> list[Example]:
        """Read examples of one sentence line and one translation line each.

        Args:
            lines: The body's lines, stripped.
            where: The page and line, for the error message.

        Returns:
            The examples, in order.

        Raises:
            BlockFormatError: When a sentence has no translation or a
                translation has no sentence.
        """
        examples = []
        sentence = None
        for offset, line in enumerate(lines, start=1):
            at = f"{where} (body line {offset})"
            if line.startswith(":"):
                translation = line[1:].strip()
                if sentence is None or not translation:
                    msg = f"{at}: a translation needs a sentence on the line above"
                    raise BlockFormatError(msg)
                examples.append(Example(sentence, translation))
                sentence = None
            elif sentence is not None:
                msg = f"{at}: the sentence {sentence!r} has no ': translation' line"
                raise BlockFormatError(msg)
            elif line:
                sentence = line
        if sentence is not None:
            msg = f"{where}: the sentence {sentence!r} has no ': translation' line"
            raise BlockFormatError(msg)
        return examples

    def multiline_examples(self, lines: list[str], where: str) -> list[Example]:
        """Read examples of several sentence lines then several translation lines.

        Args:
            lines: The body's lines, stripped.
            where: The page and line, for the error message.

        Returns:
            The examples, in order, each keeping its line breaks.

        Raises:
            BlockFormatError: When a group is not sentence lines followed by
                translation lines.
        """
        examples = []
        group: list[str] = []
        for offset, line in enumerate([*lines, ""], start=1):
            if line:
                group.append(line)
                continue
            if not group:
                continue
            split = next(
                (i for i, part in enumerate(group) if part.startswith(":")), None
            )
            sentences = group[:split]
            translations = [part[1:].strip() for part in group[split or 0 :]]
            if (
                split is None
                or not sentences
                or any(not part.startswith(":") for part in group[split:])
                or not all(translations)
            ):
                msg = (
                    f"{where} (body line {offset - 1}): an example is sentence "
                    "lines, then ': translation' lines, then a blank line"
                )
                raise BlockFormatError(msg)
            examples.append(Example("\n".join(sentences), "\n".join(translations)))
            group = []
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
        cls, root: Path, reader: BlockReader | None = None
    ) -> BlockCollection:
        """Read the blocks of every Markdown page under a docs directory.

        A directory whose name starts with ``_`` or ``.``, such as ``_build``,
        is skipped. A page's name is its path below ``root`` without ``.md``.

        Args:
            root: The docs directory.
            reader: The reader to use, a ``BlockReader`` unless given.

        Returns:
            The collection of every block under ``root``.

        Raises:
            BlockFormatError: When a block's body cannot be read as examples.
        """
        pages = {}
        for path in sorted(Path(root).rglob("*.md")):
            relative = path.relative_to(root)
            if any(part.startswith(("_", ".")) for part in relative.parts):
                continue
            pages[relative.with_suffix("").as_posix()] = path.read_text(
                encoding="utf-8"
            )
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
