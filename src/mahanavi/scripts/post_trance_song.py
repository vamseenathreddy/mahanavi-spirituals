"""post_trance_song.py: upload the Shiva psychedelic trance video to Devotional Trance Beats.

  python -m mahanavi.scripts.post_trance_song --file shiva_assets/long/shiva_trance_01.mp4 --thumb shiva_assets/long/shiva_trance_01.jpg [--privacy public|unlisted]

No links are written in the description; viewers find the other songs through the playlist.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from channels.engine import upload

PLAYLIST = "शिव ट्रान्स | Shiva Trance Mantras"
TITLE = "शिव ट्रान्स | हर हर महादेव | Om Namah Shivaya Psychedelic Trance"
HASHTAGS = "#ShivaTrance #HarHarMahadev #OmNamahShivaya #DevotionalTranceBeats #Mahakal"
TAGS = ["Shiva trance", "Shiva psychedelic trance", "Om Namah Shivaya", "Har Har Mahadev", "Bholenath", "Mahakal",
        "Shiv tandav trance", "Shiva mantra", "mantra trance", "devotional trance", "Shiva bhajan", "goa trance Shiva",
        "Mahadev status", "Devotional Trance Beats"]
DESC = (
    "ॐ नमः शिवाय। हर हर महादेव। भोलेनाथ, महाकाल, कैलाशपति के नाम का यह ट्रान्स आपको ध्यान की गहराई में ले जाएगा।\n"
    "हेडफ़ोन लगाइए, आँखें बंद कीजिए और मंत्र की धुन में खो जाइए।\n\n"
    "Om Namah Shivaya. Har Har Mahadev. A Shiva psychedelic trance built on simple Sanskrit mantras, a rolling bass, damru and tribal drums. "
    "Put on your headphones, close your eyes and let the chant carry you.\n\n"
    "इस गीत में: ॐ नमः शिवाय, हर हर महादेव, शम्भो शंकर, ॐ त्र्यम्बकं यजामहे।\n"
    "Mantras in this track: Om Namah Shivaya, Har Har Mahadev, Shambho Shankara, Om Tryambakam Yajamahe.\n\n"
    "ऐसे और ट्रान्स मंत्रों के लिए चैनल को सब्सक्राइब कीजिए और इसे उनके साथ बाँटिए जो महादेव से प्रेम करते हैं।\n"
    "Subscribe to Devotional Trance Beats for more mantra trance and share this with someone who loves Mahadev.\n\n"
    "इस वीडियो का संगीत और दृश्य AI की मदद से बनाए गए हैं। / The music and visuals in this video were created with AI assistance.\n\n"
    + HASHTAGS)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", required=True)
    ap.add_argument("--thumb", default="")
    ap.add_argument("--privacy", choices=["public", "unlisted"], default="public")
    ap.add_argument("--token", default="./data/youtube_token_trance_beats.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--playlist-only", default="", metavar="VIDEO_ID", help="Only add this existing video to the playlist.")
    a = ap.parse_args(argv)
    if a.playlist_only:
        yt = upload.service(Path(a.token))
        pl = upload.find_or_create_playlist(yt, PLAYLIST, "Shiva mantra trance by Devotional Trance Beats", "hi")
        upload.add_to_playlist(yt, a.playlist_only, pl)
        print(f"::notice::added {a.playlist_only} to the Shiva Trance playlist")
        return 0
    print(f"'{TITLE}' ({len(TITLE)} chars) -> {a.privacy} ({a.file})")
    if a.dry_run:
        return 0
    yt = upload.service(Path(a.token))
    got = yt.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
    if "trance" not in got.lower():
        raise SystemExit(f"::error::token acts as channel '{got}', not Devotional Trance Beats")
    vid = upload.upload_video(yt, a.file, TITLE, DESC, TAGS, privacy_status=a.privacy, language="hi")
    print(f"::notice::uploaded {vid} on '{got}' ({a.privacy})")
    if a.thumb:
        from googleapiclient.http import MediaFileUpload
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(a.thumb, mimetype="image/jpeg")).execute()
            print("::notice::thumbnail set")
        except Exception as exc:  # noqa: BLE001
            print(f"::warning::thumbnail failed (channel may need phone verification): {exc}")
    try:
        pl = upload.find_or_create_playlist(yt, PLAYLIST, "Shiva mantra trance by Devotional Trance Beats", "hi")
        upload.add_to_playlist(yt, vid, pl)
        print("::notice::added to the Shiva Trance playlist")
    except Exception as exc:  # noqa: BLE001
        print(f"::warning::playlist failed: {exc}")
    print(f"::notice::VIDEO_ID={vid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
