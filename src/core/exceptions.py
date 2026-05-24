"""Domain exceptions for the slide-generator service.

All exceptions inherit `AppException` from `tempest_fastapi_sdk`. When raised
from a router/controller they are serialized by the SDK exception handler as
`{detail, code, details}` with the proper HTTP status code.
"""

from typing import ClassVar

from tempest_fastapi_sdk import AppException


class SlideGeneratorError(AppException):
	"""Base exception for the slide generator application."""

	status_code: int = 500
	message: str = "Slide generator internal error"
	code: ClassVar[str] = "SLIDE_GENERATOR_ERROR"

	def __init__(self, message: str | None = None) -> None:
		"""Initialize the base error.

		Args:
		    message: Optional override of the human-readable message.
		"""
		super().__init__(message=message)
		self.message = message or self.message


class EmptyInputError(SlideGeneratorError):
	"""Raised when the user submits empty or whitespace-only text."""

	status_code: int = 422
	message: str = "Input text is empty."
	code: ClassVar[str] = "EMPTY_INPUT"


class TextTooLargeError(SlideGeneratorError):
	"""Raised when the input text exceeds the configured maximum length."""

	status_code: int = 413
	message: str = "Input text exceeds the configured maximum length."
	code: ClassVar[str] = "TEXT_TOO_LARGE"


class PdfRenderError(SlideGeneratorError):
	"""Raised when the HTML-to-PDF conversion fails."""

	status_code: int = 500
	message: str = "Failed to render PDF output."
	code: ClassVar[str] = "PDF_RENDER_FAILED"
