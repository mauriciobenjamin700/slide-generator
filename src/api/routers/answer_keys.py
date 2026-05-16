from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from src.api.dependencies import get_answer_key_controller
from src.controllers import AnswerKeyController
from src.core import EmptyInputError, PdfRenderError, TextTooLargeError
from src.schemas import (
    GenerateAnswerKeyRequestSchema,
    GenerateAnswerKeyResponseSchema,
)

DOCX_MEDIA_TYPE: str = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


router: APIRouter = APIRouter(
    prefix="/api/answer-keys",
    tags=["answer-keys"],
)


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
        HTTPException: 422 when the text is empty, 413 when it exceeds
            the configured maximum length.
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

    Raises:
        HTTPException: 422 / 413 on invalid input, 500 on rendering
            failure.
    """
    try:
        pdf_bytes: bytes = await controller.generate_pdf(payload)
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
    except PdfRenderError as exc:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.message,
        ) from exc
    filename: str = "gabarito.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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

    Raises:
        HTTPException: 422 / 413 on invalid input.
    """
    try:
        docx_bytes: bytes = await controller.generate_docx(payload)
    except (EmptyInputError, TextTooLargeError) as exc:
        _raise_input_error(exc)
    filename: str = "gabarito.docx"
    return Response(
        content=docx_bytes,
        media_type=DOCX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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

    Raises:
        HTTPException: 422 / 413 on invalid input.
    """
    try:
        markdown: str = await controller.generate_markdown(payload)
    except (EmptyInputError, TextTooLargeError) as exc:
        _raise_input_error(exc)
    filename: str = "gabarito.md"
    return PlainTextResponse(
        content=markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
