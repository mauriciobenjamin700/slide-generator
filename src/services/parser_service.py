import re
from dataclasses import dataclass, field

from src.core import EmptyInputError, TextTooLargeError, settings
from src.schemas import (
    BulletItemSchema,
    SlideDeckSchema,
    SlideKind,
    SlideSchema,
)

LESSON_RE: re.Pattern[str] = re.compile(
    r"^Aula\s+(\d+)\s*:\s*(.+?)\s*$",
    re.IGNORECASE,
)

JUNK_LINES: set[str] = {
    "shutterstock",
    "explorar",
    "voltar",
    "compartilhar",
    "baixar",
    "ver mais",
    "fechar",
    "anúncio",
    "publicidade",
}

MAX_CHARS_PER_CONTENT_SLIDE: int = 700
MAX_BULLETS_PER_SLIDE: int = 6
MAX_BULLET_HEAD_LENGTH: int = 80
MAX_BULLET_HEAD_WORDS: int = 8
MIN_BULLET_TAIL_LENGTH: int = 20
MAX_SECTION_TITLE_LENGTH: int = 90
MIN_SECTION_TITLE_LENGTH: int = 4

SENTENCE_VERB_TOKENS: tuple[str, ...] = (
    " é ",
    " são ",
    " foi ",
    " foram ",
    " era ",
    " eram ",
    " será ",
    " serão ",
    " está ",
    " estão ",
    " esteve ",
    " tem ",
    " têm ",
    " possui ",
    " possuem ",
    " baseia-se ",
    " trata-se ",
)


@dataclass
class _Section:
    """Internal grouping of paragraphs and bullets under a section title."""

    title: str
    paragraphs: list[str] = field(default_factory=list)
    bullets: list[BulletItemSchema] = field(default_factory=list)


@dataclass
class _Lesson:
    """Internal grouping of sections under an `Aula N:` header."""

    index: int
    title: str
    sections: list[_Section] = field(default_factory=list)


def _is_junk(line: str) -> bool:
    """Check whether a line is a known non-content artifact.

    Args:
        line: A single, trimmed line of text.

    Returns:
        True if the line should be discarded.
    """
    return line.strip().lower() in JUNK_LINES


def _try_parse_bullet(line: str) -> tuple[str, str] | None:
    """Detect a `Term: description` bullet line.

    Args:
        line: A single, trimmed line of text.

    Returns:
        A `(term, description)` pair when the line looks like a bullet,
        else None.
    """
    if ":" not in line:
        return None
    head, _, tail = line.partition(":")
    head = head.strip()
    tail = tail.strip()
    if not head or not tail:
        return None
    if not head[0].isupper():
        return None
    if len(head) > MAX_BULLET_HEAD_LENGTH:
        return None
    if len(tail) < MIN_BULLET_TAIL_LENGTH:
        return None
    if len(head.split()) > MAX_BULLET_HEAD_WORDS:
        return None
    if any(ch in head for ch in ".,!?;"):
        return None
    if head.count("(") != head.count(")"):
        return None
    head_with_padding: str = f" {head.lower()} "
    if any(token in head_with_padding for token in SENTENCE_VERB_TOKENS):
        return None
    return head, tail


def _looks_like_section(line: str) -> bool:
    """Determine whether a line is most likely a section heading.

    Args:
        line: A single, trimmed line of text.

    Returns:
        True if the line resembles a short, capitalized heading.
    """
    if (
        len(line) > MAX_SECTION_TITLE_LENGTH
        or len(line) < MIN_SECTION_TITLE_LENGTH
    ):
        return False
    if line[-1] in ".!,;:":
        return False
    if not line[0].isupper():
        return False
    if " " not in line and len(line) < 8:
        return False
    return True


def _chunk_paragraphs(paragraphs: list[str]) -> list[list[str]]:
    """Split a list of paragraphs into slide-sized chunks.

    Args:
        paragraphs: The full list of paragraphs for a section.

    Returns:
        A list of paragraph groups. Each group is small enough for one slide.
    """
    chunks: list[list[str]] = []
    current: list[str] = []
    current_chars: int = 0
    for paragraph in paragraphs:
        paragraph_length: int = len(paragraph)
        if (
            current
            and current_chars + paragraph_length > MAX_CHARS_PER_CONTENT_SLIDE
        ):
            chunks.append(current)
            current = []
            current_chars = 0
        current.append(paragraph)
        current_chars += paragraph_length
    if current:
        chunks.append(current)
    return chunks


def _chunk_bullets(
    bullets: list[BulletItemSchema],
) -> list[list[BulletItemSchema]]:
    """Split a list of bullets into groups that fit on a single slide.

    Args:
        bullets: The full list of bullet items.

    Returns:
        A list of bullet groups, each at most `MAX_BULLETS_PER_SLIDE` long.
    """
    if not bullets:
        return []
    return [
        bullets[i : i + MAX_BULLETS_PER_SLIDE]
        for i in range(0, len(bullets), MAX_BULLETS_PER_SLIDE)
    ]


class SlideParserService:
    """Parses structured pedagogical text into a typed `SlideDeckSchema`."""

    async def parse(
        self,
        text: str,
        deck_title: str | None = None,
    ) -> SlideDeckSchema:
        """Parse the given text into a deck of slides.

        Args:
            text: The raw user-supplied text containing one or more
                `Aula N:` blocks.
            deck_title: Optional override for the deck title. When
                omitted the title is taken from the first lesson, or
                defaults to "Slides".

        Returns:
            A fully populated `SlideDeckSchema` ready for HTML rendering.

        Raises:
            EmptyInputError: If the text is empty or whitespace only.
            TextTooLargeError: If the text exceeds the configured
                maximum length.
        """
        if not text or not text.strip():
            raise EmptyInputError("Input text is empty.")
        if len(text) > settings.max_text_length:
            raise TextTooLargeError(
                "Input text exceeds the maximum of "
                f"{settings.max_text_length} characters.",
            )
        lessons: list[_Lesson] = self._extract_lessons(text)
        slides: list[SlideSchema] = self._build_slides(lessons)
        title: str = deck_title or (lessons[0].title if lessons else "Slides")
        return SlideDeckSchema(title=title, slides=slides)

    def _extract_lessons(self, text: str) -> list[_Lesson]:
        """Walk the text line by line and group it into lessons and sections.

        Args:
            text: The raw user input.

        Returns:
            A list of `_Lesson` objects in their original order.
        """
        lessons: list[_Lesson] = []
        current_lesson: _Lesson | None = None
        current_section: _Section | None = None
        paragraph_buffer: list[str] = []

        def flush_paragraph() -> None:
            """Flush the running paragraph buffer into the current section."""
            nonlocal current_section
            if not paragraph_buffer:
                return
            if current_section is None and current_lesson is not None:
                current_section = _Section(title=current_lesson.title)
                current_lesson.sections.append(current_section)
            if current_section is not None:
                current_section.paragraphs.append(
                    " ".join(paragraph_buffer).strip(),
                )
            paragraph_buffer.clear()

        for raw in text.splitlines():
            line: str = raw.strip()
            if not line:
                flush_paragraph()
                continue
            if _is_junk(line):
                flush_paragraph()
                continue

            lesson_match: re.Match[str] | None = LESSON_RE.match(line)
            if lesson_match:
                flush_paragraph()
                current_lesson = _Lesson(
                    index=int(lesson_match.group(1)),
                    title=lesson_match.group(2).strip(),
                )
                current_section = None
                lessons.append(current_lesson)
                continue

            if current_lesson is None:
                current_lesson = _Lesson(index=1, title="Conteúdo")
                lessons.append(current_lesson)

            bullet: tuple[str, str] | None = _try_parse_bullet(line)
            if bullet is not None:
                flush_paragraph()
                if current_section is None:
                    current_section = _Section(title=current_lesson.title)
                    current_lesson.sections.append(current_section)
                current_section.bullets.append(
                    BulletItemSchema(term=bullet[0], description=bullet[1]),
                )
                continue

            if _looks_like_section(line):
                flush_paragraph()
                current_section = _Section(title=line)
                current_lesson.sections.append(current_section)
                continue

            paragraph_buffer.append(line)

        flush_paragraph()
        return lessons

    def _build_slides(self, lessons: list[_Lesson]) -> list[SlideSchema]:
        """Convert grouped lessons and sections into a flat ordered slide list.

        Args:
            lessons: The lessons produced by `_extract_lessons`.

        Returns:
            A list of `SlideSchema` ready to be rendered, with `slide_number`
            populated in order.
        """
        slides: list[SlideSchema] = []
        for lesson in lessons:
            slides.append(
                SlideSchema(
                    kind=SlideKind.LESSON_TITLE,
                    title=lesson.title,
                    subtitle=f"Aula {lesson.index}",
                    lesson_index=lesson.index,
                ),
            )
            for section in lesson.sections:
                if not section.paragraphs and not section.bullets:
                    continue
                is_conclusion: bool = "conclus" in section.title.lower()
                paragraph_kind: SlideKind = (
                    SlideKind.CONCLUSION
                    if is_conclusion
                    else SlideKind.CONTENT
                )
                for paragraph_chunk in _chunk_paragraphs(section.paragraphs):
                    slides.append(
                        SlideSchema(
                            kind=paragraph_kind,
                            title=section.title,
                            paragraphs=paragraph_chunk,
                            lesson_index=lesson.index,
                        ),
                    )
                for bullet_chunk in _chunk_bullets(section.bullets):
                    slides.append(
                        SlideSchema(
                            kind=SlideKind.BULLETS,
                            title=section.title,
                            bullets=bullet_chunk,
                            lesson_index=lesson.index,
                        ),
                    )

        for index, slide in enumerate(slides, start=1):
            slide.slide_number = index
        return slides
