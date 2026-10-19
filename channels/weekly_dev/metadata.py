"""SEO for the Friday video: a searchable Telugu + English title, a description that lists every dated item, tags,
a playlist and a pinned comment."""
from __future__ import annotations

import datetime as dt

from channels.trending import config as cfg
from channels.weekly_dev.collect import MONTHS, telugu_date

PLAYLIST_TITLE = "ఏపీ అభివృద్ధి వారపు నివేదిక | AP Development Weekly - Pulse Boosting"
EN_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _range(items: list[dict]) -> tuple[dt.date, dt.date]:
    return dt.date.fromisoformat(items[0]["date"]), dt.date.fromisoformat(items[-1]["date"])


def en_range(a: dt.date, b: dt.date) -> str:
    if (a.month, a.year) == (b.month, b.year):
        return f"{a.day}-{b.day} {EN_MONTHS[b.month - 1]} {b.year}"
    return f"{a.day} {EN_MONTHS[a.month - 1]} - {b.day} {EN_MONTHS[b.month - 1]} {b.year}"


def title(items: list[dict]) -> str:
    a, b = _range(items)
    t = f"ఈ వారం ఆంధ్రప్రదేశ్ అభివృద్ధి | AP Govt Development Update | {en_range(a, b)}"
    return t if len(t) <= 100 else t[:97].rsplit(" ", 1)[0] + "..."


def tags(items: list[dict]) -> list[str]:
    base = ["ఆంధ్రప్రదేశ్ అభివృద్ధి", "ఏపీ ప్రభుత్వం", "AP development", "Andhra Pradesh development", "AP government",
            "Amaravati", "అమరావతి", "Chandrababu Naidu", "చంద్రబాబు నాయుడు", "Nara Lokesh", "నారా లోకేశ్", "TDP", "తెలుగుదేశం",
            "Telugu news", "AP news today", "weekly update", "AP development works", "ఈ వారం అభివృద్ధి", "Pulse Boosting"]
    out, n = [], 0
    for t in base:
        if n + len(t) + 1 > 480:
            break
        out.append(t)
        n += len(t) + 1
    return out


def description(items: list[dict]) -> str:
    a, b = _range(items)
    lines = [f"ఈ వారం ({telugu_date(a)} నుంచి {telugu_date(b)} వరకు) ఆంధ్రప్రదేశ్ ప్రభుత్వం చేపట్టిన అభివృద్ధి కార్యక్రమాలు, తేదీలతో సహా.",
             f"AP government development actions this week ({en_range(a, b)}): projects, investments, approvals and launches, each with its date.",
             "", "📅 ఈ వారం ముఖ్యాంశాలు:"]
    for it in items:
        d = dt.date.fromisoformat(it["date"])
        lines.append(f"• {d.day} {MONTHS[d.month - 1]}: {it['headline']} (మూలం: {it['publisher']})")
    lines += ["", "ప్రతి శుక్రవారం ఈ వారం అభివృద్ధి వార్తలు. అన్ని వార్తలు తెలుగు వార్తా సంస్థల నుంచి తీసుకున్నవి; ప్రతి అంశానికి మూలం పేరు ఇచ్చాం.",
              "", cfg.CTA["te"][2], f"💬 WhatsApp: {cfg.WHATSAPP_URL}", f"✈️ Telegram: {cfg.TELEGRAM_URL}", "",
              "#APDevelopment #Amaravati #TDP #AndhraPradesh #TeluguNews #PulseBoosting"]
    return "\n".join(lines)


def comment(items: list[dict]) -> str:
    pubs = ", ".join(sorted({it["publisher"] for it in items}))
    return f"మూలాలు: {pubs}\n{cfg.CTA['te'][2]} జై తెలుగుదేశం!"
