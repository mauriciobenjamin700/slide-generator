from src.schemas import (
    GenerateSlidesRequest,
    GenerateSlidesResponse,
    SlideDeckSchema,
)
from src.services import PdfRenderService, SlideHtmlService, SlideParserService


class SlideController:
    """Coordinates parsing, HTML rendering, and PDF generation for slide decks."""

    def __init__(
        self,
        parser_service: SlideParserService,
        html_service: SlideHtmlService,
        pdf_service: PdfRenderService,
    ) -> None:
        """Initialize the controller with its required services.

        Args:
            parser_service: Service that converts text into a `SlideDeckSchema`.
            html_service: Service that renders a deck as HTML.
            pdf_service: Service that converts HTML into a PDF.
        """
        self._parser: SlideParserService = parser_service
        self._html: SlideHtmlService = html_service
        self._pdf: PdfRenderService = pdf_service

    async def generate(self, request: GenerateSlidesRequest) -> GenerateSlidesResponse:
        """Parse text into a deck and render it to HTML.

        Args:
            request: The user's generation request.

        Returns:
            The deck schema and rendered HTML wrapped in a response.
        """
        deck: SlideDeckSchema = await self._parser.parse(
            text=request.text, deck_title=request.deck_title,
        )
        html: str = await self._html.render(deck=deck, theme=request.theme)
        return GenerateSlidesResponse(deck=deck, html=html)

    async def generate_pdf(self, request: GenerateSlidesRequest) -> bytes:
        """Parse text, render to HTML, and convert the HTML to PDF.

        Args:
            request: The user's generation request.

        Returns:
            The PDF document as bytes.
        """
        deck: SlideDeckSchema = await self._parser.parse(
            text=request.text, deck_title=request.deck_title,
        )
        html: str = await self._html.render(deck=deck, theme=request.theme)
        return await self._pdf.render(html=html)
