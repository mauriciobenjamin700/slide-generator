from src.schemas import (
    AnswerKeySchema,
    GenerateAnswerKeyRequestSchema,
    GenerateAnswerKeyResponseSchema,
)
from src.services import (
    AnswerKeyHtmlService,
    AnswerKeyParserService,
    PdfRenderService,
)


class AnswerKeyController:
    """Coordinate parsing, HTML rendering and PDF generation for answer keys."""

    def __init__(
        self,
        parser_service: AnswerKeyParserService,
        html_service: AnswerKeyHtmlService,
        pdf_service: PdfRenderService,
    ) -> None:
        """Initialize the controller with its required services.

        Args:
            parser_service: Service that converts text into an answer key.
            html_service: Service that renders an answer key as HTML.
            pdf_service: Service that converts HTML into a PDF.
        """
        self._parser: AnswerKeyParserService = parser_service
        self._html: AnswerKeyHtmlService = html_service
        self._pdf: PdfRenderService = pdf_service

    async def generate(
        self,
        request: GenerateAnswerKeyRequestSchema,
    ) -> GenerateAnswerKeyResponseSchema:
        """Parse text into an answer key and render it to HTML.

        Args:
            request: The user's generation request.

        Returns:
            The parsed answer key together with its rendered HTML.
        """
        answer_key: AnswerKeySchema = await self._parser.parse(
            text=request.text,
            title=request.title,
            subtitle=request.subtitle,
        )
        html: str = await self._html.render(
            answer_key=answer_key,
            theme=request.theme,
        )
        return GenerateAnswerKeyResponseSchema(
            answer_key=answer_key,
            html=html,
        )

    async def generate_pdf(
        self,
        request: GenerateAnswerKeyRequestSchema,
    ) -> bytes:
        """Parse text, render to HTML, and convert the HTML to PDF.

        Args:
            request: The user's generation request.

        Returns:
            The PDF document as bytes.
        """
        answer_key: AnswerKeySchema = await self._parser.parse(
            text=request.text,
            title=request.title,
            subtitle=request.subtitle,
        )
        html: str = await self._html.render(
            answer_key=answer_key,
            theme=request.theme,
        )
        return await self._pdf.render(html=html)
