from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.core import settings
from src.schemas import SlideDeckSchema


class SlideHtmlService:
    """Renders a `SlideDeckSchema` into the final HTML document."""

    def __init__(self) -> None:
        """Initialize the service with a Jinja2 environment for the templates dir."""
        self._env: Environment = Environment(
            loader=FileSystemLoader(str(settings.templates_dir)),
            autoescape=select_autoescape(enabled_extensions=("html",)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._styles: str = (settings.templates_dir / "slide_styles.css").read_text(
            encoding="utf-8",
        )

    async def render(self, deck: SlideDeckSchema, theme: str = "default") -> str:
        """Render a slide deck to a complete HTML document.

        Args:
            deck: The parsed slide deck.
            theme: The visual theme to apply. Either "default" or "dark".

        Returns:
            A standalone HTML string containing inline CSS and all slides.
        """
        template = self._env.get_template("slides.html")
        return template.render(
            deck=deck,
            theme=theme,
            slide_styles=self._styles,
        )
