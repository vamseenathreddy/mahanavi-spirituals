"""
Application configuration.

All runtime configuration is centralized here and loaded from environment
variables (populated from a .env file in development, or real environment
variables in Docker/CI/production). Nothing else in the codebase should
call os.environ directly — import `get_settings()` instead.

Using pydantic-settings gives us:
- Fail-fast validation (a missing/malformed value raises at startup,
  not at 5 AM when the scheduled job runs).
- A single typed object (`Settings`) that's easy to mock in tests.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from mahanavi.exceptions import ConfigError

# Project root = two levels up from this file (src/mahanavi/config.py -> project root)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

WEEKDAY_FOLDER_MAP: dict[int, str] = {
    0: "Monday_Shiva",
    1: "Tuesday_Hanuman",
    2: "Wednesday_Ganesha",
    3: "Thursday_Sai",
    4: "Friday_Lakshmi",
    5: "Saturday_Venkateswara",
    6: "Sunday_Surya",
}
# Note: Python's date.weekday() -> Monday=0 ... Sunday=6, matches the map above.


class Settings(BaseSettings):
    """Strongly-typed application settings, loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="MAHANAVI_",
        extra="ignore",
    )

    # --- Paths ---
    images_root: Path = Field(default=PROJECT_ROOT / "Images")
    assets_dir: Path = Field(default=PROJECT_ROOT / "assets")
    output_dir: Path = Field(default=PROJECT_ROOT / "data" / "generated")
    database_path: Path = Field(default=PROJECT_ROOT / "data" / "mahanavi.db")
    log_dir: Path = Field(default=PROJECT_ROOT / "data" / "logs")

    # --- Scheduling ---
    timezone: str = Field(default="Asia/Kolkata")
    post_hour: int = Field(default=5, ge=0, le=23)
    post_minute: int = Field(default=0, ge=0, le=59)

    # --- Branding ---
    channel_name: str = Field(default="Mahanavi Spirituals")
    watermark_text: str = Field(default="Mahanavi Spirituals")
    telugu_font_path: Path = Field(default=PROJECT_ROOT / "assets" / "fonts" / "NotoSansTelugu-Variable.ttf")
    logo_path: Path | None = Field(default=PROJECT_ROOT / "assets" / "logo" / "logo.png")

    # --- Image rendering ---
    canvas_width: int = Field(default=1080, gt=0)
    canvas_height: int = Field(default=1350, gt=0)
    image_output_format: str = Field(default="JPEG")
    image_output_quality: int = Field(default=95, ge=1, le=100)

    # --- Panchang provider ---
    panchang_provider: str = Field(default="dummy")  # "dummy" | "api" | "scraper"
    panchang_api_base_url: str | None = Field(default=None)
    panchang_api_key: str | None = Field(default=None)
    panchang_latitude: float = Field(default=17.3850)   # Hyderabad default
    panchang_longitude: float = Field(default=78.4867)

    # --- YouTube ---
    youtube_client_secrets_file: Path | None = Field(default=None)
    youtube_token_file: Path = Field(default=PROJECT_ROOT / "data" / "youtube_token.json")
    youtube_channel_id: str | None = Field(default=None)
    youtube_community_post_method: str = Field(default="playwright")  # "api" | "playwright"
    youtube_session_state_file: Path = Field(default=PROJECT_ROOT / "data" / "yt_session_state.json")

    # --- Telegram ---
    telegram_bot_token: str | None = Field(default=None)
    telegram_channel_id: str | None = Field(default=None)   # e.g. "@mahanavispirituals"
    telegram_admin_chat_id: str | None = Field(default=None)  # for operator notifications

    # --- Facebook / Instagram (optional) ---
    facebook_page_id: str | None = Field(default=None)
    facebook_page_access_token: str | None = Field(default=None)
    instagram_business_account_id: str | None = Field(default=None)
    instagram_access_token: str | None = Field(default=None)
    instagram_image_public_base_url: str | None = Field(default=None)

    # --- Content / SEO ---
    seo_max_caption_length: int = Field(default=1500, gt=0)

    max_retries: int = Field(default=3, ge=0)
    retry_backoff_seconds: float = Field(default=5.0, ge=0)

    # --- Feature toggles ---
    enable_facebook: bool = Field(default=False)
    enable_instagram: bool = Field(default=False)

    @model_validator(mode="before")
    @classmethod
    def _blank_env_vars_mean_unset(cls, data: object) -> object:
        """Treat an empty-string env var as 'not set' rather than a real value.

        Without this, MAHANAVI_LOGO_PATH= (present but empty) coerces to
        Path('.') — the current directory — instead of None, and the
        renderer would then try to open the working directory as an image.
        Any optional field left blank in .env should behave as if it were
        omitted entirely.
        """
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data

    @field_validator("images_root")
    @classmethod
    def _images_root_must_exist(cls, v: Path) -> Path:
        if not v.exists():
            raise ConfigError(
                f"images_root does not exist: {v}. "
                "Set MAHANAVI_IMAGES_ROOT or create the folder."
            )
        return v

    def weekday_folder(self, weekday: int) -> Path:
        """Return the image folder for a given Python weekday (Mon=0..Sun=6)."""
        try:
            folder_name = WEEKDAY_FOLDER_MAP[weekday]
        except KeyError as exc:
            raise ConfigError(f"Invalid weekday index: {weekday}") from exc
        return self.images_root / folder_name

    def ensure_runtime_dirs(self) -> None:
        """Create output/log/data directories if they don't exist yet."""
        for path in (self.output_dir, self.log_dir, self.database_path.parent):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached, process-wide Settings instance."""
    settings = Settings()
    settings.ensure_runtime_dirs()
    return settings
