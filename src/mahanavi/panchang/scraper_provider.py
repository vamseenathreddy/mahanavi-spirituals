"""
ScraperPanchangProvider: fetches Panchang data by scraping an HTML page.

Use this if you don't have (or don't want to pay for) a Panchang API.
Because website markup changes without notice, this class takes its CSS
selectors as configuration rather than hardcoding them — when a site's
HTML changes, you update the selector map, not the code.

`selectors` maps our PanchangData field names -> CSS selectors, e.g.:
    {
        "tithi": "#tithi-value",
        "nakshatram": ".panchang-table .nakshatram td.value",
        ...
    }

NOTE: This is a template, not a working scraper for any specific site —
you must supply `url_template` and `selectors` matching whichever Telugu
Panchang website you choose to scrape, and confirm scraping is permitted
by that site's terms of service/robots.txt before deploying this.
"""

from __future__ import annotations

import logging
from datetime import date

import requests
from bs4 import BeautifulSoup

from mahanavi.core.interfaces import PanchangProvider
from mahanavi.core.models import PanchangData
from mahanavi.exceptions import PanchangFetchError, RetryExhaustedError
from mahanavi.panchang.utils import parse_time_string
from mahanavi.retry import retry_with_backoff

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = (
    "tithi", "nakshatram", "varjyam", "rahu_kalam", "yamagandam",
    "gulika_kalam", "durmuhurtham", "abhijit_muhurtham", "sunrise", "sunset",
)


class ScraperPanchangProvider(PanchangProvider):
    """Scrapes Panchang data from a configurable HTML page + CSS selector map."""

    def __init__(
        self,
        url_template: str,
        selectors: dict[str, str],
        max_retries: int = 3,
        backoff_seconds: float = 5.0,
        timeout_seconds: float = 10.0,
        session: requests.Session | None = None,
        user_agent: str = "Mozilla/5.0 (compatible; MahanaviSpiritualsBot/1.0)",
    ) -> None:
        missing = [f for f in REQUIRED_FIELDS if f not in selectors]
        if missing:
            raise PanchangFetchError(
                f"ScraperPanchangProvider is missing selectors for: {missing}"
            )
        self._url_template = url_template
        self._selectors = selectors
        self._timeout_seconds = timeout_seconds
        self._session = session or requests.Session()
        self._session.headers.setdefault("User-Agent", user_agent)

        self._fetch_html = retry_with_backoff(
            max_retries=max_retries,
            backoff_seconds=backoff_seconds,
            exceptions=(requests.RequestException,),
        )(self._fetch_html_uncached)

    def fetch(self, for_date: date) -> PanchangData:
        url = self._url_template.format(date=for_date.isoformat())
        try:
            html = self._fetch_html(url)
        except RetryExhaustedError as exc:
            raise PanchangFetchError(f"Failed to fetch Panchang page: {url}") from exc

        soup = BeautifulSoup(html, "html.parser")
        values = self._extract_values(soup)

        return PanchangData(
            date_=for_date,
            tithi=values["tithi"],
            nakshatram=values["nakshatram"],
            varjyam=values["varjyam"],
            rahu_kalam=values["rahu_kalam"],
            yamagandam=values["yamagandam"],
            gulika_kalam=values["gulika_kalam"],
            durmuhurtham=values["durmuhurtham"],
            abhijit_muhurtham=values["abhijit_muhurtham"],
            sunrise=parse_time_string(values["sunrise"]),
            sunset=parse_time_string(values["sunset"]),
            source="scraper",
        )

    def _fetch_html_uncached(self, url: str) -> str:
        response = self._session.get(url, timeout=self._timeout_seconds)
        response.raise_for_status()
        return str(response.text)

    def _extract_values(self, soup: BeautifulSoup) -> dict[str, str]:
        values: dict[str, str] = {}
        for field, selector in self._selectors.items():
            element = soup.select_one(selector)
            if element is None:
                raise PanchangFetchError(
                    f"Selector for '{field}' matched nothing: '{selector}'. "
                    "The source website's markup may have changed — update "
                    "the selector map in your panchang config."
                )
            values[field] = element.get_text(strip=True)
        return values
