"""Write the narration script for a week's video, to record in Suno (or anywhere) in the owner's own voice.

  PYTHONPATH=src:. python -m channels.lifestyle.script --lang te --date 2026-10-25 > script.txt

One block per narrated item (title, 30 points, subscribe line), numbered, blank line between blocks."""
import argparse
import datetime as dt

from channels.lifestyle import render as R, topics


def script(lang: str, day: dt.date) -> str:
    theme = topics.theme_for(day)
    texts = R.narration_texts(lang, theme)
    return "\n\n".join(texts) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="te")
    ap.add_argument("--date", required=True)
    a = ap.parse_args()
    print(script(a.lang, dt.date.fromisoformat(a.date)), end="")
