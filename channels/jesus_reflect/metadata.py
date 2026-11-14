"""SEO for the Telugu reflection videos: Telugu title with the verse reference, chapters, tags, short pinned comment.
Channel rule: subscribe reminders only, no requests for comments. The story is labelled as illustrative."""
from __future__ import annotations

PLAYLIST = "వంశీ సందేశం: వచనం, కథ, నా అభిప్రాయం | Jesus Worship Waves"


def _ts(sec: int) -> str:
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def title(item: dict) -> str:
    t = f"{item['title_te']} | {item['ref_te']} | Bible Message in Telugu"
    return t if len(t) <= 100 else f"{item['title_te']} | {item['ref_te']}"[:100]


def description(item: dict, chapters: list[tuple[int, str]]) -> str:
    lines = [f"{item['title_te']} ({item['ref_te']} | {item['ref_en']}). ఒక బైబిల్ వచనం, ఒక చిన్న కథ, మరియు వంశీ అభిప్రాయం, ప్రార్థనతో.",
             "", f"Telugu Bible message on {item['ref_en']}: the verse, a short illustrative story and a personal reflection by Vamsee, with soft worship music.",
             "", "అధ్యాయాలు:"]
    lines += [f"{_ts(s)} {label}" for s, label in chapters]
    lines += ["", "గమనిక: కథ ఉదాహరణ కోసం చెప్పిన ఊహాత్మక కథ. ఇది వంశీ వ్యక్తిగత అభిప్రాయం.",
              "Note: the story is an illustration, and the reflection is Vamsee's personal opinion.",
              "", "ప్రతి బుధవారం, ఆదివారం కొత్త సందేశం కోసం Jesus Worship Waves ను సబ్‌స్క్రైబ్ చేయండి.",
              "", "#TeluguBibleMessage #తెలుగుబైబిల్ #JesusWorshipWaves #Telugu #BibleVerses"]
    return "\n".join(lines)


def tags(item: dict) -> list[str]:
    base = ["telugu bible message", "telugu christian message", "తెలుగు బైబిల్ వచనం", "బైబిల్ సందేశం", f"{item['ref_en']} telugu",
            item["title_te"], "telugu bible verses", "telugu devotion", "jesus telugu", "క్రైస్తవ సందేశం", "bible reflection telugu",
            "telugu christian video", "Jesus Worship Waves"]
    out, n = [], 0
    for t in base:
        if n + len(t) + 1 > 480:
            break
        out.append(t)
        n += len(t) + 1
    return out


def comment(item: dict) -> str:
    return f"{item['ref_te']}: వచనం, కథ, నా అభిప్రాయం అధ్యాయాల రూపంలో వివరణలో ఉన్నాయి. కథ ఊహాత్మకం. వంశీ"
