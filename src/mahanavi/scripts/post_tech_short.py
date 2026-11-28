"""Post one tech Short (Reddy Linux channel): card chosen by date and slot (channels/tech_series.py), rendered by video/tech_short.py.

    python -m mahanavi.scripts.post_tech_short --slot am|pm [--public] [--dry-run] [--date YYYY-MM-DD]
Skips quietly (exit 0) while the channel's OAuth token has not been added yet."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

from channels import tech_series as ts
from channels.engine import state as state_mod
from mahanavi.config import get_settings
from mahanavi.content import tech_bank
from mahanavi.exceptions import MahanaviError, YouTubeUploadError
from mahanavi.publishers import jitter, post_ledger
from mahanavi.video import tech_short

PLAYLIST = ("DevOps, Cloud and LLM Quick Tips | Reddy Linux",
            "Short daily tips on DevOps, Kubernetes, Docker, Terraform, Git, CI/CD, Linux, Azure, AWS, Google Cloud, LLMs, tokens and Vertex AI. "
            "devops tips, kubernetes tutorial, terraform tips, azure devops, aws tutorial, gcp tutorial, llm explained, tokenization explained.")
HASH = {"Kubernetes": "#Kubernetes #K8s", "Docker": "#Docker #Containers", "Terraform": "#Terraform #IaC", "Git": "#Git #GitHub",
        "CI/CD": "#CICD #GitHubActions", "DevSecOps": "#DevSecOps #Security", "Linux": "#Linux #SysAdmin", "Azure": "#Azure #Microsoft",
        "AWS": "#AWS #AmazonWebServices", "GCP": "#GCP #GoogleCloud", "LLM": "#LLM #GenAI", "Vertex AI": "#VertexAI #GoogleCloud #Gemini",
        "MLOps": "#MLOps #MachineLearning", "Observability": "#Observability #SRE", "DevOps": "#DevOps #SRE"}


def metadata(idx: int) -> tuple[str, str, list[str]]:
    cat, hook, code, points, take = tech_bank.CARDS[idx]
    title = f"{hook} | {cat} #Shorts"
    if len(title) > 100:
        title = f"{hook[:70].rstrip()} | {cat} #Shorts"
    body = [hook, ""]
    if code:
        body += ["Commands:", *code, ""]
    body += [f"{i + 1}. {p}" for i, p in enumerate(points)]
    body += ["", f"Takeaway: {take}", "", f"{HASH.get(cat, '#DevOps')} #DevOps #Cloud #TechTips #Shorts", "", "New tech tip every day. Subscribe to Reddy Linux."]
    tags = [cat, "devops", "cloud", "tech tips", "shorts", "kubernetes" if cat == "Kubernetes" else cat.lower(), "tutorial", "learn devops"]
    return title, "\n".join(body), list(dict.fromkeys(tags))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--slot", choices=sorted(ts.SLOTS), required=True)
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date", default="")
    a = ap.parse_args(argv)
    settings = get_settings()
    today = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(ts.IST).date()
    idx = ts.card_index(today, a.slot, tech_bank.count())
    if idx is None:
        print(f"Nothing to post on {today} ({a.slot}).")
        return 0
    try:
        title, desc, tags = metadata(idx)
        print(f"{today} {a.slot} card {idx + 1}\nTITLE: {title}\n{desc}\n")
        video = tech_short.render(idx, settings.output_dir / "tech" / f"tech_{idx + 1:03d}.mp4")
        print(f"Rendered: {video}")
        if a.dry_run:
            return 0
        tok = settings.youtube_token_file
        try:
            has_token = bool(json.loads(tok.read_text(encoding="utf-8")).get("refresh_token"))
        except Exception:  # noqa: BLE001
            has_token = False
        if not has_token:
            print("SKIP: the Reddy Linux channel has no OAuth token yet (see docs/tech_channel_setup.md).")
            return 0
        from googleapiclient.http import MediaFileUpload

        from mahanavi.publishers.youtube_shorts_uploader import DEFAULT_CATEGORY_ID, YouTubeShortsUploader

        youtube = YouTubeShortsUploader(settings)._build_service()  # noqa: SLF001
        got = youtube.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
        print(f"Token acts as channel: {got}")
        post_ledger.check(tok, title, desc)
        jitter.pause("tech short")
        body = {"snippet": {"title": title, "description": desc, "tags": tags, "categoryId": "28", "defaultLanguage": "en", "defaultAudioLanguage": "en"},
                "status": {"privacyStatus": "public" if a.public else "unlisted", "selfDeclaredMadeForKids": False}}
        media = MediaFileUpload(str(video), mimetype="video/mp4", chunksize=-1, resumable=True)
        video_id = str(youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()["id"])
        print(f"Uploaded: https://www.youtube.com/watch?v={video_id}")
        post_ledger.record(tok, title, desc, video_id)
        state = state_mod.load()
        state_mod.mark_posted(state, today.isoformat(), f"tech_{idx + 1}", video_id, True, dt.datetime.now(ts.IST).isoformat())
        state_mod.save(state)
        try:
            from channels.beej import playlists as pl
            from channels.engine import upload

            pid = upload.find_or_create_playlist(youtube, PLAYLIST[0], PLAYLIST[1], "en")
            print(f"Playlist: {'added' if pl.add_once(youtube, video_id, pid) else 'already listed'}")
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: could not add to the playlist: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 0
    except post_ledger.DuplicatePost as dup:
        print(f"SKIP: {dup}")
        return 0
    except (MahanaviError, YouTubeUploadError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
