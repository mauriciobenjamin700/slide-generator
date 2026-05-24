"""FastAPI dependency providers for slide-generator controllers."""

from functools import lru_cache

from src.controllers import AnswerKeyController, SlideController
from src.services import (
	AnswerKeyDocxService,
	AnswerKeyHtmlService,
	AnswerKeyMarkdownService,
	AnswerKeyParserService,
	MarkdownPdfService,
	PdfRenderService,
	SlideDocxService,
	SlideHtmlService,
	SlideMarkdownService,
	SlideParserService,
	SlidePptxService,
)


@lru_cache(maxsize=1)
def get_markdown_pdf_service() -> MarkdownPdfService:
	"""Return the shared `MarkdownPdfService` for FastAPI DI.

	Returns:
	    A singleton `MarkdownPdfService` reused by every request.
	"""
	return MarkdownPdfService()


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

	Returns:
	    A singleton `SlideController` for the running process.
	"""
	return SlideController(
		parser_service=SlideParserService(),
		html_service=SlideHtmlService(),
		pdf_service=get_pdf_service(),
		pptx_service=SlidePptxService(),
		docx_service=SlideDocxService(),
		markdown_service=SlideMarkdownService(),
	)


@lru_cache(maxsize=1)
def get_answer_key_controller() -> AnswerKeyController:
	"""Return the shared `AnswerKeyController` for FastAPI DI.

	Returns:
	    A singleton `AnswerKeyController` for the running process.
	"""
	return AnswerKeyController(
		parser_service=AnswerKeyParserService(),
		html_service=AnswerKeyHtmlService(),
		pdf_service=get_pdf_service(),
		docx_service=AnswerKeyDocxService(),
		markdown_service=AnswerKeyMarkdownService(),
	)
