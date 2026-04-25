class SlideGeneratorError(Exception):
    """Base exception for the slide generator application."""

    def __init__(self, message: str) -> None:
        """Initialize the base error.

        Args:
            message: A human readable description of the failure.
        """
        super().__init__(message)
        self.message: str = message


class EmptyInputError(SlideGeneratorError):
    """Raised when the user submits empty or whitespace-only text."""


class TextTooLargeError(SlideGeneratorError):
    """Raised when the input text exceeds the configured maximum length."""


class PdfRenderError(SlideGeneratorError):
    """Raised when the HTML to PDF conversion fails."""
