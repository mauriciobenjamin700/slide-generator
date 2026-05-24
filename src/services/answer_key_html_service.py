from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.core import settings
from src.schemas import AnswerKeySchema


class AnswerKeyHtmlService:
	"""Renders an `AnswerKeySchema` into a complete HTML document."""

	def __init__(self) -> None:
		"""Initialize the Jinja2 environment for the templates dir."""
		self._env: Environment = Environment(
			loader=FileSystemLoader(str(settings.templates_dir)),
			autoescape=select_autoescape(enabled_extensions=("html",)),
			trim_blocks=True,
			lstrip_blocks=True,
		)
		self._styles: str = (
			settings.templates_dir / "answer_key_styles.css"
		).read_text(encoding="utf-8")

	async def render(
		self,
		answer_key: AnswerKeySchema,
		theme: str = "default",
	) -> str:
		"""Render an answer key into a standalone HTML document.

		Args:
		    answer_key: The parsed answer key to render.
		    theme: The visual theme to apply. Either "default" or "dark".

		Returns:
		    A standalone HTML string with inline CSS, ready for the
		    browser preview or for the PDF renderer.
		"""
		template = self._env.get_template("answer_key.html")
		return template.render(
			answer_key=answer_key,
			theme=theme,
			answer_key_styles=self._styles,
		)
