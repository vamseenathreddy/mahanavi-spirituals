"""Domain models shared across the pipeline. Plain dataclasses, no ORM coupling."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum
from pathlib import Path


class Deity(str, Enum):
    SHIVA = "Shiva"
    HANUMAN = "Hanuman"
    GANESHA = "Ganesha"
    SAI = "Sai"
    LAKSHMI = "Lakshmi"
    VENKATESWARA = "Venkateswara"
    SURYA = "Surya"


@dataclass(frozen=True, slots=True)
class SelectedImage:
    """An image chosen for today's post."""
    path: Path
    folder_name: str          # e.g. "Monday_Shiva"
    filename: str              # e.g. "shiva_012.jpg"
    deity: Deity


@dataclass(frozen=True, slots=True)
class PanchangData:
    """Telugu Panchang details for a single day."""
    date_: date
    tithi: str
    nakshatram: str
    varjyam: str
    rahu_kalam: str
    yamagandam: str
    gulika_kalam: str
    durmuhurtham: str
    abhijit_muhurtham: str
    sunrise: time
    sunset: time
    # Added per explicit request for a richer Panchang breakdown — all
    # optional (default empty/None) so existing providers that don't
    # supply them keep working unchanged.
    karana: str = ""
    yoga: str = ""
    amrit_kaal: str = ""
    moonrise: time | None = None
    moonset: time | None = None
    festivals: list[str] = field(default_factory=list)
    marriage_muhurats: str = ""
    source: str = "unknown"   # which provider produced this (for auditing)


@dataclass(frozen=True, slots=True)
class SeoContent:
    """Generated SEO/caption content for a post."""
    title_telugu: str
    description_telugu: str
    keywords_english: list[str]
    hashtags_telugu: list[str]
    hashtags_trending: list[str]
    alt_text: str

    def full_caption(self) -> str:
        """Compose the final caption text used across platforms."""
        tags = " ".join(self.hashtags_telugu + self.hashtags_trending)
        return f"{self.title_telugu}\n\n{self.description_telugu}\n\n{tags}"


class PublishTarget(str, Enum):
    YOUTUBE = "youtube"
    TELEGRAM = "telegram"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"


@dataclass(slots=True)
class UploadResult:
    """Result of attempting to publish to one target."""
    target: PublishTarget
    success: bool
    post_url: str | None = None
    error_message: str | None = None
    screenshot_path: Path | None = None


@dataclass(slots=True)
class DailyRunResult:
    """Aggregate result of one full day's pipeline run — what gets logged/notified."""
    run_date: date
    selected_image: SelectedImage | None = None
    panchang: PanchangData | None = None
    seo: SeoContent | None = None
    generated_image_path: Path | None = None
    upload_results: list[UploadResult] = field(default_factory=list)

    @property
    def overall_success(self) -> bool:
        if not self.upload_results:
            return False
        return all(r.success for r in self.upload_results)
