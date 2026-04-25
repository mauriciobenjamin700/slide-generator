from functools import lru_cache

from src.controllers import SlideController
from src.services import PdfRenderService, SlideHtmlService, SlideParserService


@lru_cache(maxsize=1)
def get_slide_controller() -> SlideController:
    """Build (or return the cached) `SlideController` for FastAPI dependency injection.

    Returns:
        A singleton-style `SlideController` instance for the running process.
    """
    return SlideController(
        parser_service=SlideParserService(),
        html_service=SlideHtmlService(),
        pdf_service=PdfRenderService(),
    )
