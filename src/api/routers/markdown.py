"""`POST /markdown/*` — raw Markdown to PDF conversion."""

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from src.api.dependencies import get_markdown_pdf_service
from src.core import EmptyInputError, TextTooLargeError, settings
from src.schemas import MarkdownPdfRequestSchema
from src.services import MarkdownPdfService


router: APIRouter = APIRouter(prefix="/markdown", tags=["markdown"])


@router.post(
	"/pdf",
	summary="Convert raw Markdown text into a downloadable PDF.",
)
async def convert_markdown_to_pdf(
	payload: MarkdownPdfRequestSchema,
	service: MarkdownPdfService = Depends(get_markdown_pdf_service),
) -> Response:
	"""Convert raw Markdown to a styled PDF document.

	Args:
	    payload: The Markdown source plus optional rendering flags.
	    service: The injected MarkdownPdfService instance.

	Returns:
	    A Response carrying the PDF bytes with download headers.

	Raises:
	    EmptyInputError: 422 when the text is empty.
	    TextTooLargeError: 413 when the text exceeds the configured limit.
	    PdfRenderError: 500 when WeasyPrint fails to render the document.
	"""
	text: str = payload.text.strip()
	if not text:
		raise EmptyInputError("O texto Markdown não pode estar vazio.")
	if len(text) > settings.max_text_length:
		raise TextTooLargeError("O texto excede o tamanho máximo permitido.")
	pdf_bytes: bytes = await service.render(
		md_text=text,
		title=payload.title,
		render_mermaid=payload.render_mermaid,
	)
	filename_stem: str = (payload.title or "documento").strip() or "documento"
	safe_stem: str = "".join(
		c if c.isalnum() or c in ("-", "_") else "_" for c in filename_stem
	)
	filename: str = f"{safe_stem}.pdf"
	return Response(
		content=pdf_bytes,
		media_type="application/pdf",
		headers={"Content-Disposition": f'attachment; filename="{filename}"'},
	)
