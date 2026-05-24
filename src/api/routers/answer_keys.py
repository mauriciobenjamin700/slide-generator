"""`POST /answer-keys/*` — answer key (gabarito) generation endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from src.api.dependencies import get_answer_key_controller
from src.controllers import AnswerKeyController
from src.schemas import (
	GenerateAnswerKeyRequestSchema,
	GenerateAnswerKeyResponseSchema,
)

DOCX_MEDIA_TYPE: str = (
	"application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


router: APIRouter = APIRouter(prefix="/answer-keys", tags=["answer-keys"])


@router.post(
	"/generate",
	response_model=GenerateAnswerKeyResponseSchema,
	summary="Parse text and return both the parsed answer key and its HTML.",
)
async def generate_answer_key(
	payload: GenerateAnswerKeyRequestSchema,
	controller: AnswerKeyController = Depends(get_answer_key_controller),
) -> GenerateAnswerKeyResponseSchema:
	"""Parse the text into a structured answer key and render it as HTML.

	Args:
	    payload: The text and rendering options sent by the client.
	    controller: The injected answer key controller.

	Returns:
	    The parsed answer key together with the rendered HTML document.

	Raises:
	    EmptyInputError: 422 when the text is empty.
	    TextTooLargeError: 413 when the text exceeds the configured limit.
	"""
	return await controller.generate(payload)


@router.post(
	"/preview",
	response_class=HTMLResponse,
	summary="Return only the rendered HTML preview of the answer key.",
)
async def preview_answer_key(
	payload: GenerateAnswerKeyRequestSchema,
	controller: AnswerKeyController = Depends(get_answer_key_controller),
) -> HTMLResponse:
	"""Render the answer key and return the raw HTML for an iframe preview.

	Args:
	    payload: The text and rendering options sent by the client.
	    controller: The injected answer key controller.

	Returns:
	    An HTML response containing the rendered document.
	"""
	result = await controller.generate(payload)
	return HTMLResponse(content=result.html)


@router.post(
	"/pdf",
	summary="Render the answer key as a downloadable PDF document.",
)
async def download_answer_key_pdf(
	payload: GenerateAnswerKeyRequestSchema,
	controller: AnswerKeyController = Depends(get_answer_key_controller),
) -> Response:
	"""Render the answer key to PDF and return it as a download.

	Args:
	    payload: The text and rendering options sent by the client.
	    controller: The injected answer key controller.

	Returns:
	    A `Response` containing the PDF bytes as `application/pdf`.
	"""
	pdf_bytes: bytes = await controller.generate_pdf(payload)
	return Response(
		content=pdf_bytes,
		media_type="application/pdf",
		headers={"Content-Disposition": 'attachment; filename="gabarito.pdf"'},
	)


@router.post(
	"/docx",
	summary="Render the answer key as a downloadable Word document.",
)
async def download_answer_key_docx(
	payload: GenerateAnswerKeyRequestSchema,
	controller: AnswerKeyController = Depends(get_answer_key_controller),
) -> Response:
	"""Render the answer key to DOCX and return it as a download.

	Args:
	    payload: The text and rendering options sent by the client.
	    controller: The injected answer key controller.

	Returns:
	    A `Response` containing the DOCX bytes.
	"""
	docx_bytes: bytes = await controller.generate_docx(payload)
	return Response(
		content=docx_bytes,
		media_type=DOCX_MEDIA_TYPE,
		headers={"Content-Disposition": 'attachment; filename="gabarito.docx"'},
	)


@router.post(
	"/markdown",
	response_class=PlainTextResponse,
	summary="Render the answer key as plain Markdown.",
)
async def download_answer_key_markdown(
	payload: GenerateAnswerKeyRequestSchema,
	controller: AnswerKeyController = Depends(get_answer_key_controller),
) -> PlainTextResponse:
	"""Render the answer key to Markdown and return it as a download.

	Args:
	    payload: The text and rendering options sent by the client.
	    controller: The injected answer key controller.

	Returns:
	    A plain-text response containing the Markdown source.
	"""
	markdown: str = await controller.generate_markdown(payload)
	return PlainTextResponse(
		content=markdown,
		media_type="text/markdown; charset=utf-8",
		headers={"Content-Disposition": 'attachment; filename="gabarito.md"'},
	)
