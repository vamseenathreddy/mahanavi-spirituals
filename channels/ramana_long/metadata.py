"""SEO for the Self-enquiry video: a search-style title, chapters, sources, tags."""
from __future__ import annotations

from channels.ramana_long import script

PLAYLIST = "Ramana Maharshi Meditation and Self-Enquiry | Ramana Maharshi TV"


def _ts(sec: int) -> str:
    m, s = divmod(int(sec), 60)
    return f"{m}:{s:02d}"


def title() -> str:
    return "Ramana Maharshi Meditation Technique | Self-Enquiry (Who Am I?) Step by Step | ఆత్మవిచారణ"[:100]


def description(chapters: list[tuple[int, str]]) -> str:
    lines = [
        "Learn the meditation technique taught by Sri Ramana Maharshi: self-enquiry (Atma Vichara), the practice of asking "
        "'Who am I?' and turning attention back to the source of the mind. Step by step, with two silent practice sessions. "
        "Useful for beginners and for anyone searching for Ramana Maharshi teachings in English.",
        "",
        "రమణ మహర్షి బోధించిన ఆత్మవిచారణ (నేను ఎవరిని?) ధ్యాన పద్ధతి, దశల వారీగా, రెండు నిశ్శబ్ద సాధనలతో.",
        "", "Chapters:"]
    lines += [f"{_ts(s)} {label}" for s, label in chapters]
    lines += ["", "Sources: " + "; ".join(script.SOURCES) + ".",
              "This is an explanation in our own words; short phrases are credited to Who Am I? (Nan Yar?), copyright Sri Ramanasramam. "
              "Please read the original. Visuals are digitally created devotional artwork inspired by Sri Ramana Maharshi and Arunachala. "
              "The Om chant music is an original composition.",
              "", "Subscribe to Ramana Maharshi TV for a daily teaching in Telugu and English.",
              "", "#RamanaMaharshi #SelfEnquiry #WhoAmI #Meditation #శ్రీరమణమహర్షి"]
    return "\n".join(lines)


def tags() -> list[str]:
    base = ["Ramana Maharshi meditation technique", "Ramana Maharshi", "self enquiry", "self inquiry meditation", "who am I meditation",
            "Atma vichara", "Ramana Maharshi teachings in English", "Who am I Ramana Maharshi", "Nan Yar", "Advaita Vedanta",
            "guided meditation", "meditation for beginners", "Arunachala", "Tiruvannamalai", "రమణ మహర్షి", "ఆత్మవిచారణ",
            "నేను ఎవరిని", "spiritual reality in Telugu", "Ramana Maharshi TV"]
    out, n = [], 0
    for t in base:
        cost = len(t) + (2 if " " in t else 0) + 1
        if n + cost > 480:
            break
        out.append(t)
        n += cost
    return out


def comment() -> str:
    return "Short phrases are from Who Am I? (Nan Yar?) by Sri Ramana Maharshi, Sri Ramanasramam. Please read the original."
