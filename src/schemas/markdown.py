from pydantic import BaseModel, Field


class MarkdownPdfRequestSchema(BaseModel):
	"""Payload for converting raw Markdown text into a PDF document."""

	text: str = Field(
		description="Raw Markdown source to be converted.",
		min_length=1,
	)
	title: str | None = Field(
		default=None,
		description=(
			"Optional document title used in <title> and as the "
			"suggested download filename stem."
		),
	)
	render_mermaid: bool = Field(
		default=False,
		description=(
			"When True, attempt to render ```mermaid fenced blocks via "
			"Playwright + Chromium. Requires the optional `playwright` "
			"package installed at runtime."
		),
	)
