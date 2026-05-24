"""API routers."""

from src.api.routers.answer_keys import router as answer_keys_router
from src.api.routers.health import router as health_router
from src.api.routers.markdown import router as markdown_router
from src.api.routers.slides import router as slides_router

__all__: list[str] = [
	"answer_keys_router",
	"health_router",
	"markdown_router",
	"slides_router",
]
