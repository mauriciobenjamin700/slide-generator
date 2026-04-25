from functools import lru_cache

from src.controllers import SlideController
from src.services import PdfRenderService, SlideHtmlService, SlideParserService


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
        pdf_service=PdfRenderService(),
    )
