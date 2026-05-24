from src.schemas import (
	AnswerKeySchema,
	GenerateAnswerKeyRequestSchema,
	GenerateAnswerKeyResponseSchema,
)
from src.services import (
	AnswerKeyDocxService,
	AnswerKeyHtmlService,
	AnswerKeyMarkdownService,
	AnswerKeyParserService,
	PdfRenderService,
)


class AnswerKeyController:
	"""
	Coordinate parsing, HTML rendering and PDF generation for answer keys.
	"""

	def __init__(
		self,
		parser_service: AnswerKeyParserService,
		html_service: AnswerKeyHtmlService,
		pdf_service: PdfRenderService,
		docx_service: AnswerKeyDocxService,
		markdown_service: AnswerKeyMarkdownService,
	) -> None:
		"""Initialize the controller with its required services.

		Args:
		    parser_service: Service that converts text into an answer key.
		    html_service: Service that renders an answer key as HTML.
		    pdf_service: Service that converts HTML into a PDF.
		    docx_service: Service that renders an answer key as DOCX.
		    markdown_service: Service that renders an answer key as
		        Markdown.
		"""
		self._parser: AnswerKeyParserService = parser_service
		self._html: AnswerKeyHtmlService = html_service
		self._pdf: PdfRenderService = pdf_service
		self._docx: AnswerKeyDocxService = docx_service
		self._markdown: AnswerKeyMarkdownService = markdown_service

	async def _build_answer_key(
		self,
		request: GenerateAnswerKeyRequestSchema,
	) -> AnswerKeySchema:
		"""Parse the request text into an answer key schema.

		Args:
		    request: The user's generation request.

		Returns:
		    The parsed `AnswerKeySchema`.
		"""
		return await self._parser.parse(
			text=request.text,
			title=request.title,
			subtitle=request.subtitle,
		)

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
		answer_key: AnswerKeySchema = await self._build_answer_key(request)
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
		answer_key: AnswerKeySchema = await self._build_answer_key(request)
		html: str = await self._html.render(
			answer_key=answer_key,
			theme=request.theme,
		)
		return await self._pdf.render(html=html)

	async def generate_docx(
		self,
		request: GenerateAnswerKeyRequestSchema,
	) -> bytes:
		"""Parse text and render the answer key as a DOCX file.

		Args:
		    request: The user's generation request.

		Returns:
		    The DOCX document as bytes.
		"""
		answer_key: AnswerKeySchema = await self._build_answer_key(request)
		return await self._docx.render(answer_key=answer_key)

	async def generate_markdown(
		self,
		request: GenerateAnswerKeyRequestSchema,
	) -> str:
		"""Parse text and render the answer key as Markdown.

		Args:
		    request: The user's generation request.

		Returns:
		    The Markdown document as a string.
		"""
		answer_key: AnswerKeySchema = await self._build_answer_key(request)
		return await self._markdown.render(answer_key=answer_key)
