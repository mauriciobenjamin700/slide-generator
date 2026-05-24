"""`POST /slides/*` — slide deck generation endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from src.api.dependencies import get_slide_controller
from src.controllers import SlideController
from src.schemas import (
	GenerateSlidesRequestSchema,
	GenerateSlidesResponseSchema,
)

PPTX_MEDIA_TYPE: str = (
	"application/vnd.openxmlformats-officedocument.presentationml.presentation"
)
DOCX_MEDIA_TYPE: str = (
	"application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


router: APIRouter = APIRouter(prefix="/slides", tags=["slides"])


@router.post(
	"/generate",
	response_model=GenerateSlidesResponseSchema,
	summary="Parse text and return both the parsed deck and its HTML.",
)
async def generate_slides(
	payload: GenerateSlidesRequestSchema,
	controller: SlideController = Depends(get_slide_controller),
) -> GenerateSlidesResponseSchema:
	"""Parse the provided text into structured slides and render them as HTML.

	Args:
	    payload: The text and rendering options sent by the client.
	    controller: The injected slide controller.

	Returns:
	    The parsed deck schema together with the rendered HTML document.

	Raises:
	    EmptyInputError: 422 when the text is empty.
	    TextTooLargeError: 413 when the text exceeds the configured limit.
	"""
	return await controller.generate(payload)


@router.post(
	"/preview",
	response_class=HTMLResponse,
	summary="Return only the rendered HTML preview of the deck.",
)
async def preview_slides(
	payload: GenerateSlidesRequestSchema,
	controller: SlideController = Depends(get_slide_controller),
) -> HTMLResponse:
	"""Render the deck and return the raw HTML for an iframe preview.

	Args:
	    payload: The text and rendering options sent by the client.
	    controller: The injected slide controller.

	Returns:
	    An HTML response containing the rendered deck.
	"""
	result = await controller.generate(payload)
	return HTMLResponse(content=result.html)


@router.post(
	"/pdf",
	summary="Render the deck and return it as a downloadable PDF document.",
)
async def download_pdf(
	payload: GenerateSlidesRequestSchema,
	controller: SlideController = Depends(get_slide_controller),
) -> Response:
	"""Render the deck to PDF and return it with the proper download headers.

	Args:
	    payload: The text and rendering options sent by the client.
	    controller: The injected slide controller.

	Returns:
	    A `Response` containing the PDF bytes as `application/pdf`.
	"""
	pdf_bytes: bytes = await controller.generate_pdf(payload)
	return Response(
		content=pdf_bytes,
		media_type="application/pdf",
		headers={"Content-Disposition": 'attachment; filename="slides.pdf"'},
	)


@router.post(
	"/pptx",
	summary="Render the deck and return it as a downloadable PowerPoint file.",
)
async def download_pptx(
	payload: GenerateSlidesRequestSchema,
	controller: SlideController = Depends(get_slide_controller),
) -> Response:
	"""Render the deck to PPTX and return it as a download.

	Args:
	    payload: The text and rendering options sent by the client.
	    controller: The injected slide controller.

	Returns:
	    A `Response` containing the PPTX bytes.
	"""
	pptx_bytes: bytes = await controller.generate_pptx(payload)
	return Response(
		content=pptx_bytes,
		media_type=PPTX_MEDIA_TYPE,
		headers={"Content-Disposition": 'attachment; filename="slides.pptx"'},
	)


@router.post(
	"/docx",
	summary="Render the deck as a Word handout (1 slide per page with notes).",
)
async def download_docx(
	payload: GenerateSlidesRequestSchema,
	controller: SlideController = Depends(get_slide_controller),
) -> Response:
	"""Render the deck to DOCX (handout layout) and return it as a download.

	Args:
	    payload: The text and rendering options sent by the client.
	    controller: The injected slide controller.

	Returns:
	    A `Response` containing the DOCX bytes.
	"""
	docx_bytes: bytes = await controller.generate_docx(payload)
	return Response(
		content=docx_bytes,
		media_type=DOCX_MEDIA_TYPE,
		headers={"Content-Disposition": 'attachment; filename="slides_handout.docx"'},
	)


@router.post(
	"/markdown",
	response_class=PlainTextResponse,
	summary="Render the deck as reveal.js Markdown.",
)
async def download_markdown(
	payload: GenerateSlidesRequestSchema,
	controller: SlideController = Depends(get_slide_controller),
) -> PlainTextResponse:
	"""Render the deck to reveal.js Markdown and return it as a download.

	Args:
	    payload: The text and rendering options sent by the client.
	    controller: The injected slide controller.

	Returns:
	    A plain-text response containing the Markdown source.
	"""
	markdown: str = await controller.generate_markdown(payload)
	return PlainTextResponse(
		content=markdown,
		media_type="text/markdown; charset=utf-8",
		headers={"Content-Disposition": 'attachment; filename="slides.md"'},
	)
