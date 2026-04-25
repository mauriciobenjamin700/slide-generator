from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
        str_strip_whitespace=True,
    )

    app_name: str = "Slide Generator"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    max_text_length: int = 200_000

    base_dir: Path = Path(__file__).resolve().parent.parent
    templates_dir: Path = Path(__file__).resolve().parent.parent / "templates"
    static_dir: Path = Path(__file__).resolve().parent.parent / "static"


settings: Settings = Settings()
