from typing import Literal

from pydantic import BaseModel, Field


class AnswerKeyItemSchema(BaseModel):
	"""A single question/answer pair inside an answer key section."""

	question: str = Field(
		description=(
			"The full question text, including any leading numbering "
			"(e.g. '1. Explique...')."
		),
	)
	answer: str = Field(
		description="The answer body associated with the question.",
	)


class AnswerKeySectionSchema(BaseModel):
	"""A grouped section of items inside an answer key."""

	title: str = Field(
		description=(
			"Section heading shown above its items "
			"(e.g. 'Parte 1: Portas Lógicas')."
		),
	)
	items: list[AnswerKeyItemSchema] = Field(
		default_factory=list,
		description="Ordered question/answer pairs in this section.",
	)


class AnswerKeySchema(BaseModel):
	"""The full answer key document ready to be rendered to HTML."""

	title: str = Field(
		description="Main title shown at the top of the document.",
	)
	subtitle: str | None = Field(
		default=None,
		description="Optional subtitle displayed under the main title.",
	)
	sections: list[AnswerKeySectionSchema] = Field(
		default_factory=list,
		description="Ordered list of sections composing the answer key.",
	)

	@property
	def total_items(self) -> int:
		"""Return the total number of question/answer pairs.

		Returns:
		    The total count of items across every section.
		"""
		return sum(len(section.items) for section in self.sections)


class GenerateAnswerKeyRequestSchema(BaseModel):
	"""Payload accepted by the answer key generation endpoint."""

	text: str = Field(
		min_length=1,
		description=(
			"Raw structured text to convert into an answer key. "
			"Supports 'Título:', 'Subtítulo:', 'Parte N:' headers, "
			"numbered questions and 'R:' / 'Resposta:' answers."
		),
	)
	title: str | None = Field(
		default=None,
		description=(
			"Optional override for the document title. When omitted, the "
			"title is taken from the 'Título:' line in the input text."
		),
	)
	subtitle: str | None = Field(
		default=None,
		description="Optional override for the subtitle line.",
	)
	theme: Literal["default", "dark"] = Field(
		default="default",
		description="Visual theme to apply when rendering the answer key.",
	)


class GenerateAnswerKeyResponseSchema(BaseModel):
	"""Response returned after parsing and rendering the answer key."""

	answer_key: AnswerKeySchema
	html: str = Field(
		description="The fully rendered HTML document for the answer key.",
	)
