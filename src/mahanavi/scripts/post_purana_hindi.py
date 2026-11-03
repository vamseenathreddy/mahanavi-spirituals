"""post_purana_hindi.py: the Hindi Purana Concept Short for Divine Mantra Sangam (--channel sangam) and Devotional Trance Beats
(--channel trance). Fresh-only: the next entry that has a Hindi version, is not paused, is not in this channel's used registry
(Drive-synced data/purana_concept_used_<channel>.json) and is not already on the channel. Nothing fresh left: stop and alert.

    python -m mahanavi.scripts.post_purana_hindi --channel sangam --dry-run
    python -m mahanavi.scripts.post_purana_hindi --channel trance --public
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from zoneinfo import ZoneInfo

from channels.engine import state as state_mod
from channels.engine import used_registry
from channels.engine.exhausted import stop
from mahanavi.config import get_settings
from mahanavi.content import purana_concept_hindi as ph
from mahanavi.content.branding import brand_tags
from mahanavi.content.links import strip_links
from mahanavi.content.purana_concept_shorts import PURANA_CONCEPT_SHORTS, is_paused
from mahanavi.exceptions import MahanaviError, YouTubeUploadError
from mahanavi.publishers import jitter, post_ledger
from mahanavi.publishers.recent_titles import is_posted, ledger_titles, recent_titles

IST = ZoneInfo("Asia/Kolkata")
CHANNEL_WORD = {"sangam": "mantra sangam", "trance": "trance"}
SLOT = {"sangam": "purana_hi_sangam", "trance": "purana_hi_trance"}
PLAYLIST = ("पुराण ज्ञान | Purana Concepts in Hindi",
            "हर दूसरे दिन पुराणों से एक नई बात: पवित्र क्षेत्र, व्रत, धर्म प्रश्न, पौराणिक सूचियाँ और पात्र पहेली। कोई दोबारा नहीं आती।\n"
            "A new Purana concept every other day in Hindi: sacred places, vows, dharma Q&A, lists and character quizzes. None repeated.")
DISCLAIMER = "ये बातें प्रसिद्ध पौराणिक परंपरा पर आधारित हैं, मान्यताओं को मान्यता ही कहा गया है।\nयह संदेश अपने प्रियजनों को WhatsApp पर भेजिए।"
TYPE_TAGS = {"sloka": "purana quotes", "sacred_place": "hindu temples", "vratha": "hindu vrat", "dharma_qa": "dharma",
             "trivia_list": "hindu mythology", "character_quiz": "mythology quiz"}


def used_file(channel: str) -> str:
    return f"purana_concept_used_{channel}.json"


def cid(i: int) -> str:
    return used_registry.content_id("hi", ph.HINDI[i].title, ph.HINDI[i].body)


def pick_next(used: set[str], titles: list[str], channel: str, ledger_check=None) -> int:
    """Index of the first fresh concept for this channel, or -1."""
    title_counts: dict[str, int] = {}
    for i in ph.HINDI:
        title_counts[ph.HINDI[i].title] = title_counts.get(ph.HINDI[i].title, 0) + 1
    for i, c in enumerate(PURANA_CONCEPT_SHORTS):
        if i not in ph.HINDI or is_paused(c) or cid(i) in used:
            continue
        if title_counts[ph.HINDI[i].title] == 1 and is_posted(titles, ph.HINDI[i].title):
            print(f"Duplicate guard: '{ph.HINDI[i].title}' is already on the channel -- not posting it again.")
            used_registry.add(used_file(channel), cid(i))
            continue
        if ledger_check is not None:
            try:
                ledger_check(*metadata(i)[:2])
            except post_ledger.DuplicatePost as dup:
                print(f"Duplicate guard (ledger): {dup} -- not posting it again.")
                used_registry.add(used_file(channel), cid(i))
                continue
        return i
    return -1


def metadata(i: int) -> tuple[str, str, list[str], str, str]:
    c, h = PURANA_CONCEPT_SHORTS[i], ph.HINDI[i]
    kind = c.concept_type.value
    title = f"{h.title} | पुराण ज्ञान"[:98]
    hashtags = "#Purana #पुराण #Hindi #Shorts"
    body = f"🙏 {h.invocation}\n\n{ph.LABEL[kind]}: {h.title}\n\n{h.body}\n\n{h.purana}\n\n{DISCLAIMER}\n\n{hashtags}"
    tags = ["purana", "purana stories", "hindu dharma", "hindu mythology", "sanatan dharma", TYPE_TAGS[kind], "Shorts", "hindi"]
    title_en = f"Purana Concept: {c.title_en}"
    desc_en = f"A Purana concept in Hindi: {c.title_en}. One new concept every other day.\n\n{hashtags}"
    return title, body, tags, title_en, desc_en


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--channel", choices=sorted(CHANNEL_WORD), required=True)
    ap.add_argument("--public", action="store_true", help="Upload public (default unlisted).")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--index", type=int, default=None, help="Force an entry (testing); the used registry is left unchanged.")
    args = ap.parse_args(argv)
    settings = get_settings()
    today = dt.datetime.now(IST).date()
    try:
        from googleapiclient.http import MediaFileUpload

        from mahanavi.publishers.youtube_shorts_uploader import DEFAULT_CATEGORY_ID, YouTubeShortsUploader
        from mahanavi.scripts.post_beej_mantra import music_for
        from mahanavi.video import purana_concept_hindi_short as video_mod

        youtube = YouTubeShortsUploader(settings)._build_service()  # noqa: SLF001
        got = youtube.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
        if CHANNEL_WORD[args.channel] not in got.lower():
            raise MahanaviError(f"NOT posting: the token acts as channel '{got}', expected the {CHANNEL_WORD[args.channel]} channel.")
        if args.index is not None:
            i = args.index
        else:
            titles = recent_titles(youtube) + ledger_titles(settings.youtube_token_file)
            i = pick_next(used_registry.load(used_file(args.channel)), titles, args.channel,
                          lambda t, d: post_ledger.check(settings.youtube_token_file, t, d))
            if i < 0:
                return stop(f"Purana Concept Short ({args.channel})", "every Hindi concept is already used on this channel")
        title, desc, tags, title_en, desc_en = metadata(i)
        desc, desc_en = strip_links(desc), strip_links(desc_en)
        print(f"{today} {args.channel} concept {i}: {title}\n{desc}\n")
        music = music_for("mantra_sangam", today, settings.alert_short_music_path)
        video = video_mod.render(i, settings.output_dir / "purana_hi" / f"{args.channel}_{i:03d}.mp4", music, today)
        print(f"Rendered: {video}")
        if args.dry_run:
            return 0
        post_ledger.check(settings.youtube_token_file, title, desc)
        jitter.pause("series short")
        body = {
            "snippet": {"title": title, "description": desc, "tags": [t for t in brand_tags(tags) if t.isascii()],
                        "categoryId": DEFAULT_CATEGORY_ID, "defaultLanguage": "hi", "defaultAudioLanguage": "hi"},
            "status": {"privacyStatus": "public" if args.public else "unlisted", "selfDeclaredMadeForKids": False},
            "localizations": {"en": {"title": title_en[:100], "description": desc_en}},
        }
        media = MediaFileUpload(str(video), mimetype="video/mp4", chunksize=-1, resumable=True)
        video_id = str(youtube.videos().insert(part="snippet,status,localizations", body=body, media_body=media).execute()["id"])
        print(f"Channel: {got}\nUploaded: https://www.youtube.com/watch?v={video_id}")
        post_ledger.record(settings.youtube_token_file, title, desc, video_id)
        if args.index is None:
            used_registry.add(used_file(args.channel), cid(i))
            print(f"Marked as used: {ph.HINDI[i].title}")
        state = state_mod.load()
        state_mod.mark_posted(state, today.isoformat(), f"purana_hi_{i}", video_id, True, dt.datetime.now(IST).isoformat())
        state_mod.save(state)
        try:
            from channels.beej import playlists as pl
            from channels.engine import upload

            pid = upload.find_or_create_playlist(youtube, PLAYLIST[0], PLAYLIST[1], "hi")
            print(f"Playlist: {'added' if pl.add_once(youtube, video_id, pid) else 'already listed'}")
        except Exception as exc:  # noqa: BLE001  a playlist failure must never lose the upload
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
