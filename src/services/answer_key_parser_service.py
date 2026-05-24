import re
from dataclasses import dataclass, field

from src.core import EmptyInputError, TextTooLargeError, settings
from src.schemas import (
	AnswerKeyItemSchema,
	AnswerKeySchema,
	AnswerKeySectionSchema,
)

QUESTION_RE: re.Pattern[str] = re.compile(
	r"^(\d+)\s*[.)]\s*(.+)$",
)
ANSWER_RE: re.Pattern[str] = re.compile(
	r"^(?:R|Resposta|A|Answer)\s*[:.]\s*(.*)$",
	re.IGNORECASE,
)
TITLE_PREFIXES: tuple[str, ...] = ("título:", "titulo:", "title:")
SUBTITLE_PREFIXES: tuple[str, ...] = (
	"subtítulo:",
	"subtitulo:",
	"subtitle:",
)

MAX_SECTION_TITLE_LENGTH: int = 120
MIN_SECTION_TITLE_LENGTH: int = 3


@dataclass
class _SectionDraft:
	"""Mutable draft of an answer key section while parsing."""

	title: str
	items: list[AnswerKeyItemSchema] = field(default_factory=list)


def _strip_prefix(line: str, prefixes: tuple[str, ...]) -> str | None:
	"""Return the value after a metadata prefix when present.

	Args:
	    line: A trimmed line of text.
	    prefixes: Lowercase prefixes to test against.

	Returns:
	    The trimmed value found after the matching prefix, or None
	    when no prefix matches.
	"""
	lowered: str = line.lower()
	for prefix in prefixes:
		if lowered.startswith(prefix):
			return line[len(prefix) :].strip()
	return None


def _looks_like_section(line: str) -> bool:
	"""Determine whether a line is most likely a section heading.

	Args:
	    line: A single, trimmed line of text.

	Returns:
	    True if the line resembles a heading (short, capitalized, and
	    not ending in sentence punctuation).
	"""
	if (
		len(line) > MAX_SECTION_TITLE_LENGTH
		or len(line) < MIN_SECTION_TITLE_LENGTH
	):
		return False
	if line[-1] in ".!,;":
		return False
	if not line[0].isalpha() or not line[0].isupper():
		return False
	return True


class AnswerKeyParserService:
	"""Parses structured plain text into a typed `AnswerKeySchema`."""

	async def parse(
		self,
		text: str,
		title: str | None = None,
		subtitle: str | None = None,
	) -> AnswerKeySchema:
		"""Parse the given text into an answer key document.

		Args:
		    text: The raw user-supplied text.
		    title: Optional override for the document title. Wins over
		        any ``Título:`` line found in the text.
		    subtitle: Optional override for the subtitle line. Wins
		        over any ``Subtítulo:`` line found in the text.

		Returns:
		    The parsed `AnswerKeySchema` ready for HTML rendering.

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

		parsed_title: str | None = None
		parsed_subtitle: str | None = None
		sections: list[_SectionDraft] = []
		current_section: _SectionDraft | None = None
		current_question: str | None = None
		current_answer_lines: list[str] = []
		in_answer: bool = False
		prev_blank: bool = True

		def flush_qa() -> None:
			"""Flush the running question/answer pair into the section."""
			nonlocal current_section, current_question
			nonlocal current_answer_lines, in_answer
			if current_question is None:
				return
			if current_section is None:
				current_section = _SectionDraft(title="")
				sections.append(current_section)
			answer_text: str = " ".join(
				line for line in current_answer_lines if line
			).strip()
			current_section.items.append(
				AnswerKeyItemSchema(
					question=current_question,
					answer=answer_text,
				),
			)
			current_question = None
			current_answer_lines = []
			in_answer = False

		for raw in text.splitlines():
			line: str = raw.strip()

			if not line:
				prev_blank = True
				continue

			title_value: str | None = _strip_prefix(line, TITLE_PREFIXES)
			if title_value is not None:
				flush_qa()
				parsed_title = title_value
				prev_blank = False
				continue

			subtitle_value: str | None = _strip_prefix(
				line,
				SUBTITLE_PREFIXES,
			)
			if subtitle_value is not None:
				flush_qa()
				parsed_subtitle = subtitle_value
				prev_blank = False
				continue

			question_match: re.Match[str] | None = QUESTION_RE.match(line)
			if question_match:
				flush_qa()
				current_question = line
				in_answer = False
				prev_blank = False
				continue

			answer_match: re.Match[str] | None = ANSWER_RE.match(line)
			if answer_match and current_question is not None:
				in_answer = True
				first_chunk: str = answer_match.group(1).strip()
				if first_chunk:
					current_answer_lines.append(first_chunk)
				prev_blank = False
				continue

			is_section_candidate: bool = (
				current_question is None or prev_blank
			) and _looks_like_section(line)
			if is_section_candidate:
				flush_qa()
				current_section = _SectionDraft(title=line)
				sections.append(current_section)
				prev_blank = False
				continue

			if in_answer:
				current_answer_lines.append(line)
			elif current_question is not None:
				current_question = f"{current_question} {line}"
			else:
				current_section = _SectionDraft(title=line)
				sections.append(current_section)

			prev_blank = False

		flush_qa()

		final_title: str = (
			title
			or parsed_title
			or (sections[0].title if sections and sections[0].title else "")
			or "Gabarito"
		)
		final_subtitle: str | None = subtitle or parsed_subtitle

		return AnswerKeySchema(
			title=final_title,
			subtitle=final_subtitle,
			sections=[
				AnswerKeySectionSchema(
					title=section.title,
					items=section.items,
				)
				for section in sections
				if section.items
			],
		)
