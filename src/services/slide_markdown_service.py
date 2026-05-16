from src.schemas import SlideDeckSchema, SlideKind, SlideSchema

_SLIDE_SEPARATOR: str = "\n\n---\n\n"


class SlideMarkdownService:
    """Render a `SlideDeckSchema` as reveal.js compatible Markdown."""

    async def render(self, deck: SlideDeckSchema) -> str:
        """Render the deck as a single Markdown document.

        The output uses reveal.js conventions: ``---`` separates slides
        and ``Note:`` blocks carry speaker notes.

        Args:
            deck: The parsed slide deck.

        Returns:
            A reveal.js-compatible Markdown string.
        """
        header: str = (
            f"<!-- Deck: {deck.title} -->\n"
            f"<!-- Total slides: {deck.total} -->\n"
        )
        slide_blocks: list[str] = [
            self._render_slide(slide) for slide in deck.slides
        ]
        body: str = _SLIDE_SEPARATOR.join(slide_blocks)
        return f"{header}\n{body}\n"

    def _render_slide(self, slide: SlideSchema) -> str:
        """Render a single slide as a Markdown block.

        Args:
            slide: The slide schema to render.

        Returns:
            The Markdown block for this slide, without trailing
            separators.
        """
        if slide.kind == SlideKind.LESSON_TITLE:
            block: str = self._render_lesson_title(slide)
        elif slide.kind == SlideKind.BULLETS:
            block = self._render_bullets(slide)
        elif slide.kind == SlideKind.CONCLUSION:
            block = self._render_content(slide, conclusion=True)
        else:
            block = self._render_content(slide, conclusion=False)

        if slide.notes:
            block += "\n\nNote:\n" + slide.notes

        return block

    @staticmethod
    def _render_lesson_title(slide: SlideSchema) -> str:
        """Render a hero/lesson-title slide.

        Args:
            slide: The slide schema.

        Returns:
            The Markdown block.
        """
        eyebrow: str = (
            f"<small>{slide.subtitle}</small>\n\n" if slide.subtitle else ""
        )
        return f"{eyebrow}# {slide.title}"

    @staticmethod
    def _render_content(
        slide: SlideSchema,
        conclusion: bool,
    ) -> str:
        """Render a paragraph-based content slide.

        Args:
            slide: The slide schema.
            conclusion: Whether this is the conclusion slide variant.

        Returns:
            The Markdown block.
        """
        eyebrow_parts: list[str] = []
        if conclusion:
            eyebrow_parts.append("Conclusão")
        elif slide.lesson_index is not None:
            eyebrow_parts.append(f"Aula {slide.lesson_index}")

        eyebrow: str = (
            f"<small>{' · '.join(eyebrow_parts)}</small>\n\n"
            if eyebrow_parts
            else ""
        )
        title: str = f"## {slide.title}"
        body: str = "\n\n".join(slide.paragraphs)
        return f"{eyebrow}{title}\n\n{body}".rstrip()

    @staticmethod
    def _render_bullets(slide: SlideSchema) -> str:
        """Render a bullet-list slide.

        Args:
            slide: The slide schema.

        Returns:
            The Markdown block.
        """
        eyebrow: str = (
            f"<small>Aula {slide.lesson_index}</small>\n\n"
            if slide.lesson_index is not None
            else ""
        )
        title: str = f"## {slide.title}"
        bullet_lines: list[str] = []
        for bullet in slide.bullets:
            if bullet.term:
                bullet_lines.append(
                    f"- **{bullet.term}**: {bullet.description}",
                )
            else:
                bullet_lines.append(f"- {bullet.description}")
        body: str = "\n".join(bullet_lines)
        return f"{eyebrow}{title}\n\n{body}"
