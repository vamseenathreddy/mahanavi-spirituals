"""
Abstract interfaces for every pluggable component in the pipeline.

Why this file matters: it's the contract that lets us swap implementations
without touching the orchestrator (pipeline.py) or any other module.

    - Need to switch Panchang from a dummy provider to a real API?
      Write a new PanchangProvider subclass. Nothing else changes.
    - YouTube Data API adds Community Post support later and you want
      to drop Playwright? Write a new Uploader subclass for YouTube.
    - Want to add a "WhatsApp Channel" publish target?
      Implement Uploader, register it in the pipeline's target list.

Every concrete implementation lives in its own module/package
(mahanavi.panchang.*, mahanavi.publishers.*, etc.) and is built in a
later step — this file only defines the shape.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path

from mahanavi.core.models import PanchangData, SeoContent, SelectedImage, UploadResult


class PanchangProvider(ABC):
    """Source of daily Telugu Panchang data. Swappable: API today, scraper tomorrow."""

    @abstractmethod
    def fetch(self, for_date: date) -> PanchangData:
        """Return Panchang details for the given date, or raise PanchangFetchError."""
        raise NotImplementedError


class ImageSelector(ABC):
    """Chooses today's devotional image, respecting non-repetition rules."""

    @abstractmethod
    def select_for_date(self, for_date: date) -> SelectedImage:
        """Return the chosen image for the given date, or raise ImageSelectionError."""
        raise NotImplementedError


class ImageRenderer(ABC):
    """Composes the final branded 1080x1350 image from raw inputs."""

    @abstractmethod
    def render(
        self,
        selected_image: SelectedImage,
        panchang: PanchangData,
        for_date: date,
    ) -> Path:
        """Return the path to the generated composed image."""
        raise NotImplementedError


class ContentGenerator(ABC):
    """Produces SEO title/description/hashtags/alt-text for a post."""

    @abstractmethod
    def generate(
        self,
        selected_image: SelectedImage,
        panchang: PanchangData,
        for_date: date,
    ) -> SeoContent:
        raise NotImplementedError


class Uploader(ABC):
    """Publishes a generated image + caption to one external platform."""

    @abstractmethod
    def publish(self, image_path: Path, seo: SeoContent) -> UploadResult:
        raise NotImplementedError


class Notifier(ABC):
    """Sends operator-facing notifications (success/failure) after a run."""

    @abstractmethod
    def notify(self, message: str, screenshot_path: Path | None = None) -> None:
        raise NotImplementedError
