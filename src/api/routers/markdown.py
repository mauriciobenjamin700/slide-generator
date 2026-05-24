"""`POST /markdown/*` — raw Markdown to PDF conversion."""

import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import Response

from src.api.dependencies import get_markdown_pdf_service
from src.core import EmptyInputError, PdfRenderError, TextTooLargeError, settings
from src.schemas import MarkdownPdfRequestSchema
from src.services import MarkdownPdfService


router: APIRouter = APIRouter(prefix="/markdown", tags=["markdown"])


def _safe_stem(value: str | None) -> str:
	"""Sanitize a string for use as a download filename stem.

	Args:
	    value: Raw user-provided string.

	Returns:
	    A filesystem-safe stem (alphanumerics, dash, underscore only).
	"""
	stem: str = (value or "documento").strip() or "documento"
	return "".join(
		c if c.isalnum() or c in ("-", "_") else "_" for c in stem
	)


def _extract_zip_safely(zip_path: Path, dest: Path) -> None:
	"""Extract a ZIP archive rejecting absolute/parent-traversal paths.

	Args:
	    zip_path: The uploaded ZIP file on disk.
	    dest: Destination directory.

	Raises:
	    PdfRenderError: If an unsafe member is detected.
	"""
	with zipfile.ZipFile(zip_path, "r") as zf:
		for member in zf.namelist():
			normalized: Path = (dest / member).resolve()
			if not str(normalized).startswith(str(dest.resolve())):
				raise PdfRenderError(
					f"Arquivo inseguro no ZIP: {member}"
				)
		zf.extractall(dest)


def _find_first_markdown(root: Path) -> Path | None:
	"""Return the first `.md` file found inside `root`, or None.

	Args:
	    root: Directory to walk.

	Returns:
	    Path to the first matching `.md` file, or None.
	"""
	for path in sorted(root.rglob("*.md")):
		if path.is_file():
			return path
	return None


@router.post(
	"/pdf",
	summary="Convert raw Markdown text into a downloadable PDF.",
)
async def convert_markdown_to_pdf(
	payload: MarkdownPdfRequestSchema,
	service: MarkdownPdfService = Depends(get_markdown_pdf_service),
) -> Response:
	"""Convert raw Markdown to a styled PDF document.

	Args:
	    payload: The Markdown source plus optional rendering flags.
	    service: The injected MarkdownPdfService instance.

	Returns:
	    A Response carrying the PDF bytes with download headers.

	Raises:
	    EmptyInputError: 422 when the text is empty.
	    TextTooLargeError: 413 when the text exceeds the configured limit.
	    PdfRenderError: 500 when WeasyPrint fails to render the document.
	"""
	text: str = payload.text.strip()
	if not text:
		raise EmptyInputError("O texto Markdown não pode estar vazio.")
	if len(text) > settings.max_text_length:
		raise TextTooLargeError("O texto excede o tamanho máximo permitido.")
	pdf_bytes: bytes = await service.render(
		md_text=text,
		title=payload.title,
		render_mermaid=payload.render_mermaid,
	)
	filename: str = f"{_safe_stem(payload.title)}.pdf"
	return Response(
		content=pdf_bytes,
		media_type="application/pdf",
		headers={"Content-Disposition": f'attachment; filename="{filename}"'},
	)


@router.post(
	"/pdf-zip",
	summary=(
		"Upload a ZIP containing one `.md` file plus its image assets and "
		"return the rendered PDF."
	),
)
async def convert_markdown_zip_to_pdf(
	file: UploadFile = File(
		..., description="ZIP archive containing one `.md` and its assets."
	),
	title: str | None = Form(default=None),
	render_mermaid: bool = Form(default=False),
	service: MarkdownPdfService = Depends(get_markdown_pdf_service),
) -> Response:
	"""Convert a ZIP-packaged Markdown bundle to PDF.

	The archive must contain exactly one Markdown file (`.md`) alongside
	any images it references with relative paths. WeasyPrint uses the
	extraction directory as `base_url`, so `<img src="img/foo.png">` is
	resolved against the unpacked files.

	Args:
	    file: The uploaded ZIP archive.
	    title: Optional document title used in <title> and filename.
	    render_mermaid: Whether to attempt mermaid block rendering.
	    service: The injected MarkdownPdfService instance.

	Returns:
	    A Response carrying the PDF bytes.

	Raises:
	    EmptyInputError: 422 when no `.md` is found inside the ZIP.
	    TextTooLargeError: 413 when the Markdown exceeds the size limit.
	    PdfRenderError: 500 on extraction or rendering failure.
	"""
	if not file.filename or not file.filename.lower().endswith(".zip"):
		raise PdfRenderError("Arquivo enviado nao e um ZIP (.zip).")

	zip_bytes: bytes = await file.read()
	if not zip_bytes:
		raise EmptyInputError("Arquivo ZIP esta vazio.")

	with tempfile.TemporaryDirectory() as tmp:
		tmp_dir: Path = Path(tmp)
		zip_path: Path = tmp_dir / "upload.zip"
		zip_path.write_bytes(zip_bytes)

		try:
			_extract_zip_safely(zip_path, tmp_dir)
		except zipfile.BadZipFile as exc:
			raise PdfRenderError(f"ZIP invalido: {exc}") from exc

		md_path: Path | None = _find_first_markdown(tmp_dir)
		if md_path is None:
			raise EmptyInputError(
				"Nenhum arquivo Markdown (.md) encontrado no ZIP."
			)

		md_text: str = md_path.read_text(encoding="utf-8").strip()
		if not md_text:
			raise EmptyInputError("O arquivo Markdown do ZIP esta vazio.")
		if len(md_text) > settings.max_text_length:
			raise TextTooLargeError(
				"O texto excede o tamanho maximo permitido."
			)

		effective_title: str | None = title or md_path.stem
		pdf_bytes: bytes = await service.render(
			md_text=md_text,
			title=effective_title,
			render_mermaid=render_mermaid,
			base_dir=md_path.parent,
		)

	filename: str = f"{_safe_stem(effective_title)}.pdf"
	return Response(
		content=pdf_bytes,
		media_type="application/pdf",
		headers={"Content-Disposition": f'attachment; filename="{filename}"'},
	)
