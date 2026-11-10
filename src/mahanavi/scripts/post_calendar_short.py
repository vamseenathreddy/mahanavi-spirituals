"""
post_calendar_short.py: Mahanavi calendar Shorts (content/calendar_days.py).

    python -m mahanavi.scripts.post_calendar_short --kind tomorrow --dry-run [--date 2026-10-28]
    python -m mahanavi.scripts.post_calendar_short --kind festivals --date 2026-10-28 --dry-run
    POST_SLOT=cal_tomorrow STATE_FILE=data/beej_state.json python -m mahanavi.scripts.post_calendar_short --kind tomorrow --public
--date is "today" (the post covers tomorrow / next month). Uploads public unless --private.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import sys
from zoneinfo import ZoneInfo

from channels.engine import state as state_mod
from channels.engine import upload as eng_upload
from channels.calendar.gate import next_month
from mahanavi.config import get_settings
from mahanavi.content import calendar_days as cal
from mahanavi.exceptions import MahanaviError, YouTubeUploadError
from mahanavi.images.request_card_renderer import RequestCardRenderer
from mahanavi.publishers.youtube_shorts_uploader import YouTubeShortsUploader
from mahanavi.scripts.post_request_short import assemble, upload

IST = ZoneInfo("Asia/Kolkata")


def build(kind: str, today: dt.date, channel: str = "mahanavi"):
    if channel != "mahanavi":  # Hindi channels (content/calendar_days_hi.py)
        from mahanavi.content import calendar_days_hi as hi

        if hi.stale(today):
            print(f"::warning::calendar_days_hi.FESTIVALS ends {hi.FESTIVALS_END}; add the next dates", file=sys.stderr)
        if kind == "today":
            keys = hi.observances(today)
            return hi.build_today(channel, today, keys) if keys else None
        if kind == "tomorrow":
            nxt = hi.next_special(today)
            return hi.build_tomorrow(channel, *nxt) if nxt else None
        y, m = next_month(today)
        return hi.build_festivals(channel, y, m) if kind == "festivals" else hi.build_vratas(channel, y, m)
    if cal.stale(today):
        print(f"::warning::calendar_days.FESTIVALS ends {cal.FESTIVALS_END}; add next year's festival dates", file=sys.stderr)
    if kind == "tips":
        return cal.build_tip(today)
    if kind == "today":
        keys = cal.observances(today)
        return cal.build_today(today, keys) if keys else None
    if kind == "tomorrow":
        nxt = cal.next_special(today)
        if nxt is None:
            return None
        return cal.build_tomorrow(*nxt)
    y, m = next_month(today)
    return cal.build_festivals(y, m) if kind == "festivals" else cal.build_vratas(y, m)


def _already_on_channel(youtube, title: str) -> bool:
    """True when a video whose title starts with this card's title (before the first '|') is in the channel's uploads (scheduled ones included)."""
    key = title.split("|")[0].strip()
    uploads = youtube.channels().list(part="contentDetails", mine=True).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    token = None
    for _ in range(40):
        resp = youtube.playlistItems().list(part="snippet", playlistId=uploads, maxResults=50, pageToken=token).execute()
        if any(key in it["snippet"]["title"] for it in resp["items"]):
            return True
        token = resp.get("nextPageToken")
        if not token:
            break
    return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kind", required=True, choices=cal.SPECIAL_KINDS)
    ap.add_argument("--channel", default="mahanavi", choices=["mahanavi", "mantra_sangam", "trance_beats"])
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date", default="")
    ap.add_argument("--month", default="", help="YYYY-MM: build the festivals/vratas card of exactly that month")
    ap.add_argument("--publish-at", default="", help="ISO time with offset: upload private and let YouTube publish it then")
    ap.add_argument("--skip-if-exists", action="store_true", help="do nothing when a video with this title is already on the channel")
    args = ap.parse_args(argv)
    settings = get_settings()
    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(IST).date()
    if args.month:
        y0, m0 = (int(x) for x in args.month.split("-"))
        today = dt.date(y0 - (m0 == 1), (m0 - 2) % 12 + 1, 15)     # "today" in the month before, so the card covers --month
    pl_kind = "tomorrow" if args.kind == "today" else args.kind   # the same-day post goes in the "tomorrow special" playlist
    try:
        if args.channel != "mahanavi" and args.kind == "tips":
            raise MahanaviError("pooja-rule tips exist only for the Telugu channel")
        spec = build(args.kind, today, args.channel)
        if spec is None:
            print("nothing special: no post")
            return 0
        print(f"{today} -> {spec.slug}: {spec.title}")
        out_dir = settings.output_dir / "calendar" / spec.slug
        renderer = RequestCardRenderer(settings)
        slides = renderer.render_all(spec, out_dir)
        if args.channel == "mahanavi":
            music = settings.alert_short_music_path
            if music is None or not music.exists():
                raise MahanaviError(f"Music file missing: {music}")
        else:
            from mahanavi.scripts.post_beej_mantra import music_for

            music = music_for(args.channel, today, settings.alert_short_music_path)
        video = assemble(spec, [s.path for s in slides], music, out_dir / f"{spec.slug}.mp4")
        print(f"Assembled: {video} ({spec.total_seconds:.1f}s)")
        if args.kind in ("festivals", "vratas") and len(slides) == 1:      # list cards: friendly animated characters behind the words
            try:
                from mahanavi.video import decor_clips

                bg_png, text_png = renderer.render_parts(spec, 0, out_dir / "parts")
                video = decor_clips.compose(bg_png, text_png, video, out_dir / f"{spec.slug}_decor.mp4")
                print(f"Decorated: {video}")
            except Exception as exc:  # noqa: BLE001  the plain card is always good enough to post
                print(f"::warning::decoration skipped: {type(exc).__name__}: {exc}", file=sys.stderr)
        if args.dry_run:
            return 0
        youtube = YouTubeShortsUploader(settings)._build_service()  # noqa: SLF001
        got = youtube.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
        if spec.expected_channel.lower() not in got.lower():
            raise MahanaviError(f"NOT posting: the token acts as channel '{got}', expected '{spec.expected_channel}'.")
        if args.skip_if_exists and _already_on_channel(youtube, spec.title):
            print(f"SKIP: '{spec.title}' is already on the channel")
            return 0
        if args.channel == "mahanavi":
            top = cal.playlist_block(youtube, pl_kind)
        else:
            from mahanavi.content import calendar_days_hi as hi

            top = hi.playlist_block(youtube, pl_kind)
        if top:
            spec = dataclasses.replace(spec, description_te=f"{top}\n\n{spec.description_te}")
        privacy = "private" if args.private else "public"   # 2026-10-22: never unlisted
        publish_at = ""
        if args.publish_at:
            when = dt.datetime.fromisoformat(args.publish_at)
            publish_at = when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            privacy = "private"
        video_id = upload(youtube, spec, video, privacy, publish_at)
        shown = f"private, goes public {args.publish_at}" if publish_at else privacy
        print(f"Channel: {got}\nUploaded ({shown}): https://www.youtube.com/watch?v={video_id}")
        print(f"::notice::calendar short uploaded ({shown}): https://www.youtube.com/watch?v={video_id}")
        if not publish_at:
            state = state_mod.load()
            state_mod.mark_posted(state, today.isoformat(), spec.slug, video_id, True, dt.datetime.now(IST).isoformat())
            state_mod.save(state)
        try:
            if args.channel == "mahanavi":
                pid = cal.playlist_ids(youtube)[pl_kind]
            else:
                from mahanavi.content import calendar_days_hi as hi

                pid = hi.playlist_ids(youtube)[pl_kind]
            eng_upload.add_to_playlist(youtube, video_id, pid)
            print("Playlist: added")
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: could not add to the playlist: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 0
    except (MahanaviError, YouTubeUploadError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        print(f"::error::calendar short failed: {str(exc)[:400]}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(f"::error::calendar short failed: {type(exc).__name__}: {str(exc)[:400]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
