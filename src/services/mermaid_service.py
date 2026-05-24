"""Server-side Mermaid diagram rendering for PDF generation.

Uses Playwright with Chromium browser to render Mermaid diagrams locally
into inline SVG that WeasyPrint can embed in PDFs. Playwright is an
optional dependency — when it is not installed, mermaid blocks are
replaced with a styled error placeholder containing the original source.
"""

import asyncio
import base64
import concurrent.futures
import html
import logging
import re
from typing import Optional

try:
	from playwright.async_api import async_playwright
except ImportError:
	async_playwright = None  # type: ignore[assignment]

logger: logging.Logger = logging.getLogger(__name__)

MERMAID_MD_PATTERN: re.Pattern[str] = re.compile(
	r"```mermaid\s*\n(.*?)```",
	re.DOTALL,
)

MERMAID_JS_CDN: str = (
	"https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"
)

_PAGE_WIDTH_PX: float = 642.0


async def render_mermaid_via_playwright(
	diagram_source: str, timeout: int = 15
) -> Optional[str]:
	"""Render a Mermaid diagram to SVG using Playwright and Chromium.

	Args:
	    diagram_source: The raw Mermaid diagram text.
	    timeout: Request timeout in seconds.

	Returns:
	    The SVG markup as a string, or None if rendering failed.
	"""
	if async_playwright is None:
		logger.warning(
			"Playwright not installed; skipping mermaid rendering."
		)
		return None

	try:
		clean_source: str = diagram_source.strip()
		html_content: str = f"""<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<script src="{MERMAID_JS_CDN}"></script>
</head>
<body>
	<div id="mermaid-container"></div>
	<script>
		mermaid.initialize({{
			startOnLoad: false,
			theme: 'default',
			htmlLabels: false,
			flowchart: {{ htmlLabels: false }},
			sequence: {{ htmlLabels: false }}
		}});
	</script>
</body>
</html>"""

		async with async_playwright() as p:
			browser = await p.chromium.launch(
				args=["--no-sandbox", "--disable-setuid-sandbox"]
			)
			page = await browser.new_page()
			await page.set_viewport_size({"width": 1200, "height": 800})
			page.set_default_timeout(timeout * 1000)
			try:
				encoded: str = base64.b64encode(
					html_content.encode("utf-8")
				).decode("ascii")
				await page.goto(
					f"data:text/html;base64,{encoded}",
					wait_until="networkidle",
				)
				svg_html: str = await page.evaluate(
					"""async (source) => {
						const { svg } = await mermaid.render(
							'mermaid-diagram', source
						);
						return svg;
					}""",
					clean_source,
				)
				if not svg_html or "<svg" not in svg_html.lower():
					logger.warning("Invalid SVG from mermaid.render().")
					return None
				return svg_html
			except Exception as exc:
				logger.error(
					"Error during Playwright rendering: %s", exc
				)
				return None
			finally:
				await browser.close()
	except Exception as exc:
		logger.error("Unexpected mermaid render error: %s", exc)
		return None


def render_mermaid_to_svg(
	diagram_source: str, timeout: int = 15
) -> Optional[str]:
	"""Synchronous wrapper around the async Playwright rendering.

	Args:
	    diagram_source: The raw Mermaid diagram text.
	    timeout: Request timeout in seconds.

	Returns:
	    The SVG markup, or None if rendering failed or Playwright is
	    unavailable.
	"""
	try:
		return asyncio.run(
			render_mermaid_via_playwright(diagram_source, timeout)
		)
	except RuntimeError:
		with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
			future = pool.submit(
				asyncio.run,
				render_mermaid_via_playwright(diagram_source, timeout),
			)
			return future.result(timeout=timeout + 5)
	except Exception as exc:
		logger.error("Error in render_mermaid_to_svg wrapper: %s", exc)
		return None


def _fit_svg_to_page(svg: str) -> str:
	"""Resize SVG so it fits within A4 usable width.

	Args:
	    svg: The raw SVG markup.

	Returns:
	    SVG with adjusted width attributes.
	"""
	svg = re.sub(r'\sstyle="max-width:\s*[\d.]+px;"', "", svg)
	vb_match: Optional[re.Match[str]] = re.search(
		r'viewBox="[\d.\-]+\s+[\d.\-]+\s+([\d.]+)\s+([\d.]+)"', svg
	)
	if vb_match:
		vb_width: float = float(vb_match.group(1))
		width: float = min(vb_width, _PAGE_WIDTH_PX)
		svg = re.sub(r'width="100%"', f'width="{width:.0f}px"', svg)
	return svg


def _make_error_html(diagram_source: str, error_msg: str) -> str:
	"""Build the fallback HTML rendered when Mermaid cannot draw a block.

	Args:
	    diagram_source: The original mermaid source code.
	    error_msg: Description of the failure.

	Returns:
	    HTML string with a styled error box containing the source.
	"""
	escaped_source: str = html.escape(diagram_source.strip())
	escaped_msg: str = html.escape(error_msg)
	return (
		f'<div class="mermaid-error">'
		f"<strong>Erro ao renderizar diagrama Mermaid:</strong> "
		f"{escaped_msg}"
		f"<pre>{escaped_source}</pre>"
		f"</div>"
	)


def _replace_mermaid_match(match: re.Match[str]) -> str:
	"""Replace a single mermaid block with rendered SVG or an error box.

	Args:
	    match: The regex match for a mermaid block.

	Returns:
	    HTML string with rendered SVG or an error placeholder.
	"""
	diagram_source: str = match.group(1)
	svg: Optional[str] = render_mermaid_to_svg(diagram_source)
	if svg is not None:
		svg = _fit_svg_to_page(svg)
		return f'<div class="mermaid-diagram">{svg}</div>'
	return _make_error_html(
		diagram_source,
		"Nao foi possivel renderizar o diagrama. "
		"Verifique a sintaxe ou instale playwright.",
	)


def process_mermaid_blocks(md_content: str) -> str:
	"""Replace ```mermaid blocks in Markdown with inline SVG (or errors).

	Args:
	    md_content: The raw Markdown text.

	Returns:
	    The Markdown with mermaid blocks replaced.
	"""
	return MERMAID_MD_PATTERN.sub(_replace_mermaid_match, md_content)
