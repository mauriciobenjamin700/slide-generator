from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from src.api.dependencies import get_slide_controller
from src.controllers import SlideController
from src.core import EmptyInputError, PdfRenderError, TextTooLargeError
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


router: APIRouter = APIRouter(prefix="/api/slides", tags=["slides"])


def _raise_input_error(
    error: EmptyInputError | TextTooLargeError,
) -> None:
    """Translate parser input errors into HTTP exceptions.

    Args:
        error: The raised parser error.

    Raises:
        HTTPException: Mapped to 422 (empty) or 413 (too large).
    """
    if isinstance(error, EmptyInputError):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.message,
        ) from error
    raise HTTPException(
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail=error.message,
    ) from error


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
        HTTPException: 422 when the text is empty, 413 when it
            exceeds the configured maximum length.
    """
    try:
        return await controller.generate(payload)
    except EmptyInputError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.message,
        ) from exc
    except TextTooLargeError as exc:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=exc.message,
        ) from exc


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

    Raises:
        HTTPException: 422 / 413 on invalid or oversized input.
    """
    try:
        result = await controller.generate(payload)
    except EmptyInputError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.message,
        ) from exc
    except TextTooLargeError as exc:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=exc.message,
        ) from exc
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

    Raises:
        HTTPException: 422 / 413 on invalid input, 500 on rendering failure.
    """
    try:
        pdf_bytes: bytes = await controller.generate_pdf(payload)
    except (EmptyInputError, TextTooLargeError) as exc:
        _raise_input_error(exc)
    except PdfRenderError as exc:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.message,
        ) from exc
    filename: str = "slides.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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

    Raises:
        HTTPException: 422 / 413 on invalid input.
    """
    try:
        pptx_bytes: bytes = await controller.generate_pptx(payload)
    except (EmptyInputError, TextTooLargeError) as exc:
        _raise_input_error(exc)
    filename: str = "slides.pptx"
    return Response(
        content=pptx_bytes,
        media_type=PPTX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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

    Raises:
        HTTPException: 422 / 413 on invalid input.
    """
    try:
        docx_bytes: bytes = await controller.generate_docx(payload)
    except (EmptyInputError, TextTooLargeError) as exc:
        _raise_input_error(exc)
    filename: str = "slides_handout.docx"
    return Response(
        content=docx_bytes,
        media_type=DOCX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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

    Raises:
        HTTPException: 422 / 413 on invalid input.
    """
    try:
        markdown: str = await controller.generate_markdown(payload)
    except (EmptyInputError, TextTooLargeError) as exc:
        _raise_input_error(exc)
    filename: str = "slides.md"
    return PlainTextResponse(
        content=markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
