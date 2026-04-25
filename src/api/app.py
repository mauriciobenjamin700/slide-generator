from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routers import slides_router
from src.core import settings


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance.

    Returns:
        The configured FastAPI application.
    """
    app: FastAPI = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Generate HTML/PDF slide decks from structured pedagogical text.",
        debug=settings.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(slides_router)

    app.mount(
        "/static",
        StaticFiles(directory=str(settings.static_dir)),
        name="static",
    )

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        """Health check endpoint.

        Returns:
            A small payload signaling the service is up.
        """
        return {"status": "ok"}

    @app.get("/", include_in_schema=False)
    async def root() -> FileResponse:
        """Serve the single-page frontend.

        Returns:
            The bundled `index.html` response.
        """
        return FileResponse(str(settings.static_dir / "index.html"))

    return app


app: FastAPI = create_app()
