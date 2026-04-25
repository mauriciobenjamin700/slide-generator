from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, Response

from src.api.dependencies import get_slide_controller
from src.controllers import SlideController
from src.core import EmptyInputError, PdfRenderError, TextTooLargeError
from src.schemas import GenerateSlidesRequest, GenerateSlidesResponse

router: APIRouter = APIRouter(prefix="/api/slides", tags=["slides"])


@router.post(
    "/generate",
    response_model=GenerateSlidesResponse,
    summary="Parse text and return both the parsed deck and its HTML.",
)
async def generate_slides(
    payload: GenerateSlidesRequest,
    controller: SlideController = Depends(get_slide_controller),
) -> GenerateSlidesResponse:
    """Parse the provided text into structured slides and render them as HTML.

    Args:
        payload: The text and rendering options sent by the client.
        controller: The injected slide controller.

    Returns:
        The parsed deck schema together with the rendered HTML document.

    Raises:
        HTTPException: 422 when the text is empty or exceeds the maximum length.
    """
    try:
        return await controller.generate(payload)
    except EmptyInputError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    except TextTooLargeError as exc:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=exc.message) from exc


@router.post(
    "/preview",
    response_class=HTMLResponse,
    summary="Return only the rendered HTML preview of the deck.",
)
async def preview_slides(
    payload: GenerateSlidesRequest,
    controller: SlideController = Depends(get_slide_controller),
) -> HTMLResponse:
    """Render the deck and return the raw HTML document for embedding in an iframe.

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
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    except TextTooLargeError as exc:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=exc.message) from exc
    return HTMLResponse(content=result.html)


@router.post(
    "/pdf",
    summary="Render the deck and return it as a downloadable PDF document.",
)
async def download_pdf(
    payload: GenerateSlidesRequest,
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
    except EmptyInputError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    except TextTooLargeError as exc:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=exc.message) from exc
    except PdfRenderError as exc:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=exc.message) from exc
    filename: str = "slides.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
