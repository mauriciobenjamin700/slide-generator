import re

from src.schemas import AnswerKeySchema

_HTML_TAG_RE: re.Pattern[str] = re.compile(r"<[^>]+>")


class AnswerKeyMarkdownService:
    """Render an `AnswerKeySchema` as a plain Markdown document."""

    async def render(self, answer_key: AnswerKeySchema) -> str:
        """Render the answer key as Markdown.

        Args:
            answer_key: The parsed answer key.

        Returns:
            A standalone Markdown string ready to be saved or piped.
        """
        lines: list[str] = [f"# {answer_key.title}", ""]
        if answer_key.subtitle:
            lines.append(f"_{answer_key.subtitle}_")
            lines.append("")

        for section in answer_key.sections:
            lines.append(f"## {section.title}")
            lines.append("")
            for item in section.items:
                question: str = _strip_inline_html(item.question).strip()
                answer: str = _strip_inline_html(item.answer).strip()
                lines.append(f"**{question}**")
                lines.append("")
                lines.append(f"> Resposta: {answer}")
                lines.append("")

        return "\n".join(lines).rstrip() + "\n"


def _strip_inline_html(text: str) -> str:
    """Remove inline HTML tags from a string.

    Args:
        text: The source text, possibly containing inline HTML.

    Returns:
        The text without HTML tags.
    """
    return _HTML_TAG_RE.sub("", text)
