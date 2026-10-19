"""This week's Andhra Pradesh government development news for the Friday video: real Telugu headlines from the last
7 days, positive and on topic, each with its own publication date and publisher. Nothing is invented or summarised
beyond what the headline says."""
from __future__ import annotations

import datetime as dt
import re
from zoneinfo import ZoneInfo

from channels.trending import sources
from channels.trending.sources import Story, complete

IST = ZoneInfo("Asia/Kolkata")
MONTHS = ["జనవరి", "ఫిబ్రవరి", "మార్చి", "ఏప్రిల్", "మే", "జూన్", "జూలై", "ఆగస్టు", "సెప్టెంబర్", "అక్టోబర్", "నవంబర్", "డిసెంబర్"]
WEEKDAYS = ["సోమవారం", "మంగళవారం", "బుధవారం", "గురువారం", "శుక్రవారం", "శనివారం", "ఆదివారం"]
MAX_ITEMS, MIN_ITEMS = 10, 4
# (niche filter, extra searches) : the government's own actions, projects and decisions of the week
QUERIES = {
    "development": ["ఆంధ్రప్రదేశ్ అభివృద్ధి పెట్టుబడులు", "ఏపీ ప్రభుత్వం శంకుస్థాపన", "ఏపీ కేబినెట్ నిర్ణయాలు",
                    "ఏపీ ప్రభుత్వం కొత్త పథకం ప్రారంభం", "ఆంధ్రప్రదేశ్ పరిశ్రమలు ఉద్యోగాలు"],
    "amaravati": ["అమరావతి రాజధాని పనులు", "అమరావతి నిర్మాణం"],
    "chandrababu": ["సీఎం చంద్రబాబు అభివృద్ధి శంకుస్థాపన", "చంద్రబాబు ప్రారంభోత్సవం"],
    "lokesh": ["మంత్రి లోకేశ్ ఉద్యోగాలు పెట్టుబడులు", "లోకేశ్ విద్య ఐటీ ప్రారంభం"],
    "nda": ["కూటమి ప్రభుత్వం ఆంధ్రప్రదేశ్ అభివృద్ధి"],
}
ACTION = ("శంకుస్థాపన", "ప్రారంభ", "ఒప్పందం", "మంజూరు", "నిధులు", "పెట్టుబడ", "ఉద్యోగ", "పథకం", "నిర్మాణ", "పనులు", "అనుమతి",
          "ఆమోదం", "కేటాయిం", "విడుదల", "అభివృద్ధి", "పరిశ్రమ", "హబ్", "ప్రాజెక్టు", "రహదారి", "విమానాశ్రయ", "పోర్టు")


def telugu_date(d: dt.date, weekday: bool = False) -> str:
    s = f"{d.day} {MONTHS[d.month - 1]} {d.year}"
    return f"{s} ({WEEKDAYS[d.weekday()]})" if weekday else s


def _tokens(text: str) -> set[str]:
    return {w for w in re.split(r"[\W_]+", text.casefold()) if len(w) > 2}


def _same_story(a: str, b: str) -> bool:
    ta, tb = _tokens(a), _tokens(b)
    return bool(ta and tb) and len(ta & tb) / min(len(ta), len(tb)) >= 0.6


def pick(stories: list[Story], today: dt.date, used: set[str], limit: int = MAX_ITEMS) -> list[dict]:
    """Newest-first dedupe, then oldest-first for reading as a week timeline. Only stories dated in the last 7 days."""
    start = today - dt.timedelta(days=6)
    items: list[dict] = []
    for s in sorted((x for x in stories if x.published), key=lambda x: x.published, reverse=True):
        day = s.published.astimezone(IST).date()
        head = complete(s.headline, 200)
        if not (start <= day <= today) or not head or s.key in used:
            continue
        if not any(w in head for w in ACTION):
            continue
        if any(_same_story(head, it["headline"]) for it in items):
            continue
        items.append({"date": day.isoformat(), "headline": head, "publisher": s.publisher, "link": s.link, "key": s.key})
        if len(items) >= limit:
            break
    items.sort(key=lambda it: it["date"])
    return items


def collect(today: dt.date, used: set[str] | None = None, fetch=sources.political_stories) -> list[dict]:
    pool: list[Story] = []
    for niche, queries in QUERIES.items():
        try:
            pool += fetch(niche, "te", days=7, queries=queries)
        except Exception as exc:  # noqa: BLE001 - one failing search must not lose the week
            print(f"::warning::weekly news '{niche}' failed: {type(exc).__name__}")
    return pick(pool, today, used or set())
