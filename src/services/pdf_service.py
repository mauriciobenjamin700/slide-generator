import asyncio
import io

from src.core import PdfRenderError


class PdfRenderService:
    """Converts an HTML document into a PDF byte buffer using WeasyPrint."""

    async def render(self, html: str) -> bytes:
        """Render the given HTML to a PDF.

        WeasyPrint runs synchronously and is wrapped with `asyncio.to_thread`
        so it does not block the FastAPI event loop.

        Args:
            html: The complete HTML document to convert.

        Returns:
            The generated PDF file content as bytes.

        Raises:
            PdfRenderError: If WeasyPrint fails to produce the PDF.
        """
        try:
            return await asyncio.to_thread(self._render_sync, html)
        except Exception as exc:
            raise PdfRenderError(f"Failed to render PDF: {exc}") from exc

    @staticmethod
    def _render_sync(html: str) -> bytes:
        """Synchronously generate a PDF from HTML.

        Args:
            html: The HTML document to render.

        Returns:
            The PDF document as bytes.
        """
        from weasyprint import HTML

        buffer: io.BytesIO = io.BytesIO()
        HTML(string=html).write_pdf(target=buffer)
        return buffer.getvalue()
