"""Uvicorn launcher and module-level FastAPI instance.

`app` is exposed here so external loaders (uvicorn CLI, ASGI servers, tests)
can import `src.server:app` without triggering side effects on package import.
"""

import uvicorn

from src.api.app import app
from src.core import get_settings

__all__: list[str] = ["app", "run"]


def run() -> None:
	"""Start the uvicorn server using configured host/port."""
	settings = get_settings()
	uvicorn.run(
		"src.server:app",
		host=settings.host,
		port=settings.port,
		reload=settings.debug,
	)


if __name__ == "__main__":
	run()
