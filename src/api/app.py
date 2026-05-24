"""FastAPI application factory for the slide-generator service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from tempest_fastapi_sdk import register_exception_handlers

from src.api.routers import (
	answer_keys_router,
	health_router,
	markdown_router,
	slides_router,
)
from src.core import get_settings


def create_app() -> FastAPI:
	"""Build and configure the FastAPI application instance.

	Returns:
	    The configured FastAPI application.
	"""
	settings = get_settings()

	app: FastAPI = FastAPI(
		title=settings.app_name,
		version="0.1.0",
		description=(
			"Generate HTML/PDF slide decks from structured pedagogical text."
		),
		debug=settings.debug,
	)

	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	register_exception_handlers(app)

	app.include_router(health_router)
	app.include_router(slides_router, prefix="/api")
	app.include_router(answer_keys_router, prefix="/api")
	app.include_router(markdown_router, prefix="/api")

	app.mount(
		"/static",
		StaticFiles(directory=str(settings.static_dir)),
		name="static",
	)

	@app.get("/", include_in_schema=False)
	async def root() -> FileResponse:
		"""Serve the single-page frontend.

		Returns:
		    The bundled `index.html` response.
		"""
		return FileResponse(str(settings.static_dir / "index.html"))

	return app


app: FastAPI = create_app()
