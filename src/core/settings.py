"""Application settings loaded from environment variables."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from tempest_fastapi_sdk import BaseAppSettings


_SRC_DIR: Path = Path(__file__).resolve().parent.parent


class Settings(BaseAppSettings):
	"""Runtime settings for the slide-generator API.

	Values are loaded from environment variables (or a local `.env` file).
	Overrides `BaseAppSettings.model_config` to keep case-insensitive
	matching (lowercase field names map to `UPPER` env vars).
	"""

	model_config = SettingsConfigDict(
		env_file=".env",
		extra="ignore",
		case_sensitive=False,
		str_strip_whitespace=True,
		frozen=False,
	)

	app_name: str = Field(
		default="Slide Generator",
		description="Application display name.",
	)
	debug: bool = Field(default=False, description="Enable FastAPI debug features.")
	host: str = Field(default="127.0.0.1", description="Bind address for uvicorn.")
	port: int = Field(default=12003, description="Bind port for uvicorn.")
	max_text_length: int = Field(
		default=200_000,
		ge=1,
		description="Reject input bodies larger than this size (HTTP 413).",
	)

	base_dir: Path = Field(default=_SRC_DIR, description="Source root directory.")
	templates_dir: Path = Field(
		default=_SRC_DIR / "templates",
		description="Jinja2 templates directory.",
	)
	static_dir: Path = Field(
		default=_SRC_DIR / "static",
		description="Static assets directory served at `/static`.",
	)


_settings: Settings | None = None


def get_settings() -> Settings:
	"""Return a process-wide cached `Settings` instance.

	Returns:
	    The singleton settings object, instantiated lazily on first call.
	"""
	global _settings
	if _settings is None:
		_settings = Settings()
	return _settings


settings: Settings = get_settings()
