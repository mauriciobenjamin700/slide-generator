import uvicorn

from src.core import settings


def main() -> None:
    """Run the slide generator API with uvicorn."""
    uvicorn.run(
        "src.api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
