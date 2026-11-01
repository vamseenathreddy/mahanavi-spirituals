"""post_shiva_song.py: upload the Karthika Masam Shiva song and its promo Shorts to Mahanavi Spirituals,
scheduled inside YouTube (uploaded private, YouTube makes it public at --publish-at).

  python -m mahanavi.scripts.post_shiva_song --kind long  --file shiva_assets/long/shiva_song_01.mp4 --thumb shiva_assets/long/thumb.jpg --publish-at 2026-11-02T05:30:00+05:30
  python -m mahanavi.scripts.post_shiva_song --kind short --variant glimpse --file shiva_assets/shorts/A.mp4 --publish-at 2026-11-01T11:00:00+05:30

No links are written anywhere: the Shorts lead viewers to the song through the shared playlist, the
on-screen end card, a shared hashtag and the song title in every description.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

from channels.engine import upload

PLAYLIST = "కార్తీక మాస శివ గీతాలు | Karthika Masam Shiva Songs"
SONG_TITLE = "కార్తీక మాస శివ గీతం | Karthika Masam Shiva Song | Om Namah Shivaya"
HASHTAGS = "#KarthikaMasam #ShivaSong #OmNamahShivaya #MahanaviSpirituals"
TAGS = ["Karthika Masam", "Shiva song", "Om Namah Shivaya", "Shiva bhajan", "Telugu devotional song", "Karthika Pournami",
        "కార్తీక మాసం", "శివ గీతం", "శివ భక్తి గీతాలు", "Mahanavi Spirituals", "Lord Shiva", "Shiva Tandava", "Neelakantha"]

LONG_DESC = (
    "కార్తీక మాసం శివ భక్తుల పవిత్ర మాసం. ఓం నమః శివాయ అంటూ ఈ శివ గీతాన్ని మీ కుటుంబంతో కలిసి వినండి.\n\n"
    "Karthika Masam is the most sacred month for Lord Shiva devotees. Listen to this Shiva song with your family "
    "on Karthika Somavaram, and light a lamp (deepam) for Shiva this month. Karthika Pournami is on 24 November 2026.\n\n"
    "ఈ గీతంలో: శివలింగ అభిషేకం, హాలాహల విషం స్వీకరించిన నీలకంఠుడు, శివ పార్వతి కుటుంబం, కార్తీక దీపోత్సవం, నటరాజ తాండవం.\n"
    "In this song: Shiva abhishekam, Neelakantha drinking the Halahala poison, the divine family of Shiva, Karthika deepotsavam, and the Nataraja tandava.\n\n"
    "ఇలాంటి భక్తి గీతాలు ప్రతి వారం కావాలంటే ఛానల్‌ను సబ్‌స్క్రైబ్ చేయండి.\n"
    "Subscribe to Mahanavi Spirituals for a new devotional song and daily Telugu devotion.\n\n"
    "ఈ వీడియోలోని సంగీతం, దృశ్యాలు AI సహాయంతో రూపొందించబడ్డాయి. / The music and visuals in this video were created with AI tools.\n\n"
    + HASHTAGS)

SHORT = {
    "glimpse": ("రేపు ఉదయం 5:30 కి | కార్తీక మాస శివ గీతం #Shorts",
                "రేపు ఉదయం 5:30 కి మహానవి స్పిరిచ్యువల్స్‌లో కొత్త శివ గీతం వస్తోంది.\n"
                "Tomorrow 5:30 AM: a new Shiva song for Karthika Masam is coming to Mahanavi Spirituals.\n"),
    "weekly": ("శివ గీతం: కార్తీక మాసం ప్రత్యేకం | Shiva Song #Shorts",
               "పూర్తి శివ గీతం ఛానల్‌లో ఉంది.\n"
               "The full song is on this channel: " + SONG_TITLE + " (see the Shiva Songs playlist).\n"),
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kind", choices=["long", "short"], required=True)
    ap.add_argument("--variant", choices=sorted(SHORT), default="weekly")
    ap.add_argument("--file", required=True)
    ap.add_argument("--thumb", default="")
    ap.add_argument("--publish-at", required=True, help="ISO time with offset, e.g. 2026-11-02T05:30:00+05:30")
    ap.add_argument("--token", default="./data/youtube_token.json")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    when = dt.datetime.fromisoformat(a.publish_at).astimezone(dt.timezone.utc)
    if when <= dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
        raise SystemExit(f"::error::--publish-at {a.publish_at} is not at least 5 minutes in the future")
    if a.kind == "long":
        title, desc = SONG_TITLE, LONG_DESC
    else:
        t, d = SHORT[a.variant]
        title, desc = t, d + "\n" + HASHTAGS + " #Shorts"
    print(f"{a.kind}: '{title}' -> public at {when:%Y-%m-%d %H:%M} UTC ({a.file})")
    if a.dry_run:
        return 0
    yt = upload.service(Path(a.token))
    got = yt.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
    if "mahanavi" not in got.lower():
        raise SystemExit(f"::error::token acts as channel '{got}', not Mahanavi Spirituals")
    vid = upload.upload_video(yt, a.file, title, desc, TAGS, publish_at=when, language="te")
    print(f"::notice::uploaded {vid} on '{got}', scheduled public at {a.publish_at}")
    if a.kind == "long" and a.thumb:
        from googleapiclient.http import MediaFileUpload
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(a.thumb, mimetype="image/jpeg")).execute()
            print("::notice::thumbnail set")
        except Exception as exc:  # noqa: BLE001
            print(f"::warning::thumbnail failed (channel may need phone verification): {exc}")
    try:
        pl = upload.find_or_create_playlist(yt, PLAYLIST, "Karthika Masam Shiva songs by Mahanavi Spirituals", "te")
        upload.add_to_playlist(yt, vid, pl)
        print("::notice::added to Shiva Songs playlist")
    except Exception as exc:  # noqa: BLE001
        print(f"::warning::playlist failed: {exc}")
    print(f"::notice::VIDEO_ID={vid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
