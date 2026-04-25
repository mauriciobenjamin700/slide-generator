from functools import lru_cache

from src.controllers import AnswerKeyController, SlideController
from src.services import (
    AnswerKeyHtmlService,
    AnswerKeyParserService,
    PdfRenderService,
    SlideHtmlService,
    SlideParserService,
)


@lru_cache(maxsize=1)
def get_pdf_service() -> PdfRenderService:
    """Return the shared `PdfRenderService` for FastAPI DI.

    Returns:
        A singleton `PdfRenderService` reused by every controller.
    """
    return PdfRenderService()


@lru_cache(maxsize=1)
def get_slide_controller() -> SlideController:
    """Return the shared `SlideController` for FastAPI DI.

    The instance is cached so all requests share the same services.

    Returns:
        A singleton `SlideController` for the running process.
    """
    return SlideController(
        parser_service=SlideParserService(),
        html_service=SlideHtmlService(),
        pdf_service=get_pdf_service(),
    )


@lru_cache(maxsize=1)
def get_answer_key_controller() -> AnswerKeyController:
    """Return the shared `AnswerKeyController` for FastAPI DI.

    The instance is cached so all requests share the same services.

    Returns:
        A singleton `AnswerKeyController` for the running process.
    """
    return AnswerKeyController(
        parser_service=AnswerKeyParserService(),
        html_service=AnswerKeyHtmlService(),
        pdf_service=get_pdf_service(),
    )
