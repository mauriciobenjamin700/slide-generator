"""Convert raw Markdown text into a styled PDF using WeasyPrint."""

import asyncio
import io
import logging
from typing import Optional

import markdown
from weasyprint import HTML

from src.core import PdfRenderError
from src.services.abnt_styles import ABNT_CSS
from src.services.mermaid_service import process_mermaid_blocks

logger: logging.Logger = logging.getLogger(__name__)


MARKDOWN_EXTENSIONS: list[str] = [
	"fenced_code",
	"codehilite",
	"tables",
	"toc",
	"attr_list",
	"footnotes",
]


class MarkdownPdfService:
	"""Render Markdown text into a downloadable PDF document."""

	async def render(
		self,
		md_text: str,
		title: Optional[str] = None,
		render_mermaid: bool = False,
	) -> bytes:
		"""Convert Markdown text into PDF bytes.

		Heavy lifting (Markdown -> HTML -> PDF + optional mermaid render)
		runs inside `asyncio.to_thread` so it does not block the event
		loop.

		Args:
		    md_text: The raw Markdown source.
		    title: Optional document title used in <title>.
		    render_mermaid: If True, attempt to render ```mermaid blocks
		        via Playwright. Requires the optional `playwright`
		        dependency installed at runtime.

		Returns:
		    The generated PDF document as bytes.

		Raises:
		    PdfRenderError: If conversion fails for any reason.
		"""
		try:
			return await asyncio.to_thread(
				self._render_sync, md_text, title, render_mermaid
			)
		except Exception as exc:
			raise PdfRenderError(
				f"Failed to render Markdown to PDF: {exc}"
			) from exc

	@staticmethod
	def _render_sync(
		md_text: str, title: Optional[str], render_mermaid: bool
	) -> bytes:
		"""Synchronously convert Markdown to PDF.

		Args:
		    md_text: The raw Markdown source.
		    title: Optional document title.
		    render_mermaid: Whether to attempt mermaid rendering.

		Returns:
		    PDF bytes.
		"""
		processed: str = md_text
		if render_mermaid:
			processed = process_mermaid_blocks(processed)

		html_body: str = markdown.markdown(
			processed, extensions=MARKDOWN_EXTENSIONS
		)
		safe_title: str = title or "Documento"
		full_html: str = (
			"<!DOCTYPE html>"
			"<html><head>"
			'<meta charset="utf-8">'
			f"<title>{safe_title}</title>"
			"<style>"
			f"{ABNT_CSS}"
			"</style>"
			"</head>"
			f"<body>{html_body}</body>"
			"</html>"
		)

		buffer: io.BytesIO = io.BytesIO()
		HTML(string=full_html).write_pdf(target=buffer)
		return buffer.getvalue()
