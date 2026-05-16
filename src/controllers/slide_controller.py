from src.schemas import (
    GenerateSlidesRequestSchema,
    GenerateSlidesResponseSchema,
    SlideDeckSchema,
)
from src.services import (
    PdfRenderService,
    SlideDocxService,
    SlideHtmlService,
    SlideMarkdownService,
    SlideParserService,
    SlidePptxService,
)


class SlideController:
    """Coordinate parsing and rendering of slide decks across formats."""

    def __init__(
        self,
        parser_service: SlideParserService,
        html_service: SlideHtmlService,
        pdf_service: PdfRenderService,
        pptx_service: SlidePptxService,
        docx_service: SlideDocxService,
        markdown_service: SlideMarkdownService,
    ) -> None:
        """Initialize the controller with its required services.

        Args:
            parser_service: Service that converts text into a deck.
            html_service: Service that renders a deck as HTML.
            pdf_service: Service that converts HTML into a PDF.
            pptx_service: Service that renders a deck as PPTX.
            docx_service: Service that renders a deck as a DOCX handout.
            markdown_service: Service that renders a deck as reveal.js
                Markdown.
        """
        self._parser: SlideParserService = parser_service
        self._html: SlideHtmlService = html_service
        self._pdf: PdfRenderService = pdf_service
        self._pptx: SlidePptxService = pptx_service
        self._docx: SlideDocxService = docx_service
        self._markdown: SlideMarkdownService = markdown_service

    async def _build_deck(
        self,
        request: GenerateSlidesRequestSchema,
    ) -> SlideDeckSchema:
        """Parse the request text into a deck schema.

        Args:
            request: The user's generation request.

        Returns:
            The parsed `SlideDeckSchema`.
        """
        return await self._parser.parse(
            text=request.text,
            deck_title=request.deck_title,
        )

    async def generate(
        self,
        request: GenerateSlidesRequestSchema,
    ) -> GenerateSlidesResponseSchema:
        """Parse text into a deck and render it to HTML.

        Args:
            request: The user's generation request.

        Returns:
            The deck schema and rendered HTML wrapped in a response.
        """
        deck: SlideDeckSchema = await self._build_deck(request)
        html: str = await self._html.render(deck=deck, theme=request.theme)
        return GenerateSlidesResponseSchema(deck=deck, html=html)

    async def generate_pdf(
        self,
        request: GenerateSlidesRequestSchema,
    ) -> bytes:
        """Parse text, render to HTML, and convert the HTML to PDF.

        Args:
            request: The user's generation request.

        Returns:
            The PDF document as bytes.
        """
        deck: SlideDeckSchema = await self._build_deck(request)
        html: str = await self._html.render(deck=deck, theme=request.theme)
        return await self._pdf.render(html=html)

    async def generate_pptx(
        self,
        request: GenerateSlidesRequestSchema,
    ) -> bytes:
        """Parse text and render the deck as a PPTX file.

        Args:
            request: The user's generation request.

        Returns:
            The PPTX document as bytes.
        """
        deck: SlideDeckSchema = await self._build_deck(request)
        return await self._pptx.render(deck=deck, theme=request.theme)

    async def generate_docx(
        self,
        request: GenerateSlidesRequestSchema,
    ) -> bytes:
        """Parse text and render the deck as a DOCX handout.

        Args:
            request: The user's generation request.

        Returns:
            The DOCX document as bytes.
        """
        deck: SlideDeckSchema = await self._build_deck(request)
        return await self._docx.render(deck=deck)

    async def generate_markdown(
        self,
        request: GenerateSlidesRequestSchema,
    ) -> str:
        """Parse text and render the deck as reveal.js Markdown.

        Args:
            request: The user's generation request.

        Returns:
            The Markdown document as a string.
        """
        deck: SlideDeckSchema = await self._build_deck(request)
        return await self._markdown.render(deck=deck)
