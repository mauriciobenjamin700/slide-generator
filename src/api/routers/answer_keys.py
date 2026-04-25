from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, Response

from src.api.dependencies import get_answer_key_controller
from src.controllers import AnswerKeyController
from src.core import EmptyInputError, PdfRenderError, TextTooLargeError
from src.schemas import (
    GenerateAnswerKeyRequestSchema,
    GenerateAnswerKeyResponseSchema,
)

router: APIRouter = APIRouter(
    prefix="/api/answer-keys",
    tags=["answer-keys"],
)


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
