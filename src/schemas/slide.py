from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class SlideKind(str, Enum):
	"""Identifies the visual variant a slide should be rendered as."""

	LESSON_TITLE = "lesson_title"
	SECTION = "section"
	CONTENT = "content"
	BULLETS = "bullets"
	CONCLUSION = "conclusion"


class BulletItemSchema(BaseModel):
	"""A single bullet inside a `BULLETS` slide."""

	term: str | None = Field(
		default=None,
		description=(
			"Optional highlighted term shown before the description "
			"(e.g. 'Porta NOT')."
		),
	)
	description: str = Field(description="The bullet body text.")


class SlideSchema(BaseModel):
	"""A single slide ready to be rendered to HTML."""

	kind: SlideKind
	title: str = Field(description="Main title shown at the top of the slide.")
	subtitle: str | None = Field(
		default=None,
		description=(
			"Optional subtitle, used by lesson title and section slides."
		),
	)
	paragraphs: list[str] = Field(
		default_factory=list,
		description="Paragraph blocks rendered as body text.",
	)
	bullets: list[BulletItemSchema] = Field(
		default_factory=list,
		description="Bullet items rendered as a list. Used by BULLETS slides.",
	)
	lesson_index: int | None = Field(
		default=None,
		description=(
			"The 1-based index of the parent lesson, used in slide footers."
		),
	)
	slide_number: int = Field(
		default=0,
		description="The 1-based position of this slide in the deck.",
	)
	notes: str | None = Field(
		default=None,
		description=(
			"Optional speaker notes attached to this slide. Visible "
			"in DOCX handouts, PPTX speaker notes pane and reveal.js "
			"Markdown output."
		),
	)


class SlideDeckSchema(BaseModel):
	"""The full ordered collection of slides produced from an input text."""

	title: str = Field(
		description="Overall deck title, derived from the first lesson.",
	)
	slides: list[SlideSchema]

	@property
	def total(self) -> int:
		"""Return the total number of slides in the deck.

		Returns:
		    The number of slides currently in the deck.
		"""
		return len(self.slides)


class GenerateSlidesRequestSchema(BaseModel):
	"""Payload accepted by the slide generation endpoint."""

	text: str = Field(
		min_length=1,
		description="Raw structured text to convert into slides.",
	)
	deck_title: str | None = Field(
		default=None,
		description="Optional override for the deck title.",
	)
	theme: Literal["default", "dark"] = Field(
		default="default",
		description="Visual theme to apply when rendering the slides.",
	)


class GenerateSlidesResponseSchema(BaseModel):
	"""Response returned after parsing and rendering the slides as HTML."""

	deck: SlideDeckSchema
	html: str = Field(
		description="The fully rendered HTML document for the slides.",
	)
