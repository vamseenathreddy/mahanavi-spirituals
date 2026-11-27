"""
post_verse_series.py: one verse a day as a Short (series registry: channels/verse_series.py).

    python -m mahanavi.scripts.post_verse_series --series shiv_tandav_hi --dry-run --date 2026-11-10
    python -m mahanavi.scripts.post_verse_series --series shiv_tandav_hi --public

The "already posted today" marker lives in the channel's state file (STATE_FILE) under POST_SLOT. Posts unlisted unless --public.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys

from channels import verse_series as vs
from channels.engine import state as state_mod
from mahanavi.config import get_settings
from mahanavi.content.branding import brand_tags
from mahanavi.content.links import strip_links
from mahanavi.exceptions import MahanaviError, YouTubeUploadError
from mahanavi.publishers import jitter, post_ledger
from mahanavi.video import verse_short

SERIES_TAGS = {
    "shiv_tandav_hi": ["Shiv Tandav Stotram", "Shiva Tandava Stotram", "Shiv Tandav", "Shiv Tandav with meaning", "Shiv Tandav Hindi meaning",
                       "Ravana Shiv Tandav", "Shiva stotram", "Mahadev", "Shiva mantra", "stotram", "Hindi devotional", "Shorts"],
    "shiv_tandav_trance": ["Shiv Tandav trance", "Shiv Tandav trance beats", "Shiv Tandav chant", "Har Har Mahadev", "Mahadev trance", "Shiva trance",
                           "Shiva chant loop", "devotional trance", "Hindi devotional", "Mahadev status", "Shorts"],
    "vedas_te": ["Vedas", "Veda mantra", "Rigveda", "Yajurveda", "Samaveda", "Atharvaveda", "Veda mantra with meaning", "Vedic mantra",
                 "Telugu devotional", "వేద మంత్రం", "వేదాలు", "Hindu mantra", "Shorts"],
    "vedas_hi": ["Vedas", "Veda mantra", "Rigveda", "Yajurveda", "Samaveda", "Atharvaveda", "Veda mantra with meaning", "Vedic mantra",
                 "Hindi devotional", "वेद मंत्र", "चारों वेद", "Hindu mantra", "Shorts"],
    "vishnu_te": ["Vishnu Sahasranamam", "Vishnu Sahasranama", "Vishnu Sahasranama stotram", "vishnu sahasranama stotram telugu", "Vishnu stotram with meaning",
                  "Vishnu mantra", "Narayana", "Telugu devotional", "విష్ణు సహస్రనామం", "శ్రీ మహావిష్ణు", "Hindu mantra", "Shorts"],
    "vishnu_hi": ["Vishnu Sahasranamam", "Vishnu Sahasranama", "Vishnu Sahasranama stotram", "vishnu sahasranam in hindi", "Vishnu stotra with meaning",
                  "Vishnu mantra", "Narayan", "Hindi devotional", "विष्णु सहस्रनाम", "श्री हरि", "Hindu mantra", "Shorts"],
}
PLAYLISTS = {
    "shiv_tandav_hi": ("शिव ताण्डव स्तोत्र | श्लोक और हिंदी अर्थ | Shiv Tandav Stotram with Meaning",
                       "शिव ताण्डव स्तोत्र के सभी 15 श्लोक, हर श्लोक का हिंदी अर्थ, क्रम से। श्लोक 1 से शुरू करें।\n"
                       "Shiv Tandav Stotram, all 15 verses in order, each with its meaning in Hindi. Start from verse 1."),
    "shiv_tandav_trance": ("शिव ताण्डव ट्रांस | हर हर महादेव जाप | Shiv Tandav Trance Beats",
                           "शिव ताण्डव की धुन पर रोज़ एक ट्रांस जाप, 15 दिन।\nShiv Tandav trance chant loops, one every day for 15 days."),
    "vedas_te": ("నాలుగు వేదాలు | రోజుకో వేద మంత్రం | 4 Vedas Mantra with Meaning",
                 "ఋగ్వేదం, యజుర్వేదం, సామవేదం, అథర్వవేదం నుండి రోజుకో మంత్రం, తెలుగు అర్థంతో.\nOne mantra a day from the Rigveda, Yajurveda, Samaveda and Atharvaveda, with meaning."),
    "vishnu_te": ("విష్ణు సహస్రనామం | రోజుకో శ్లోకం | Vishnu Sahasranamam with Meaning",
                  "విష్ణు సహస్రనామ స్తోత్రం తెలుగు అర్థంతో, రోజుకో శ్లోకం. శ్రీ మహావిష్ణు స్తోత్రం, నారాయణ నామ స్మరణ, లక్ష్మీ నారాయణ భక్తి, గురువారం ఏకాదశి విష్ణు పూజకు అనువైన శ్లోకాలు. మొదటి శ్లోకం నుంచి క్రమంగా వినండి.\n"
                  "Vishnu Sahasranamam stotram in Telugu with meaning, one verse a day. Sri Maha Vishnu stotram, vishnu sahasranamam lyrics in Telugu with meaning, Narayana, Lakshmi Narayana, Ekadashi and Thursday Vishnu puja. Start from the first verse."),
    "vishnu_hi": ("विष्णु सहस्रनाम | रोज़ एक श्लोक अर्थ सहित | Vishnu Sahasranamam with Meaning",
                  "विष्णु सहस्रनाम स्तोत्र हिंदी अर्थ सहित, रोज़ एक श्लोक। श्री हरि नारायण स्तुति, लक्ष्मी नारायण भक्ति, एकादशी और गुरुवार विष्णु पूजा के लिए श्लोक। पहले श्लोक से क्रम में सुनें।\n"
                  "Vishnu Sahasranamam in Hindi with meaning, one verse a day. Vishnu sahasranam stotra lyrics, Shri Hari, Narayana, Lakshmi Narayana, Ekadashi and Thursday Vishnu puja. Start from the first verse."),
    "vedas_hi": ("चारों वेद | रोज़ एक वेद मंत्र अर्थ सहित | 4 Vedas Mantra with Meaning",
                 "ऋग्वेद, यजुर्वेद, सामवेद और अथर्ववेद से रोज़ एक मंत्र, हिंदी अर्थ के साथ।\nOne mantra a day from the four Vedas, with meaning in Hindi."),
}


def metadata(key: str, day: int) -> tuple[str, str, list[str], str, str]:
    """(title, description, tags, title_en, description_en); no links anywhere."""
    c = verse_short.content(key)
    verse, meaning = c.VERSES[day]
    n = day + 1
    if key in ("vishnu_te", "vishnu_hi"):
        from mahanavi.content import vishnu_sahasra as vh

        first = " ".join(verse.split("\n")[:2]).replace(" ।", "").strip()
        en = vh.EN_MEAN[day]
        if key == "vishnu_te":
            title = f"విష్ణు సహస్రనామం | {first} | అర్థంతో"
            hashtags = "#VishnuSahasranamam #విష్ణుసహస్రనామం #Vishnu #Shorts"
            desc = (f"శ్రీ విష్ణు సహస్రనామ స్తోత్రం\n\n{verse}\n\nఅర్థం: {meaning}\n\nMeaning in English: {en}\n\n"
                    f"విష్ణు సహస్రనామం రోజుకో శ్లోకం, అర్థంతో. కొత్తగా చూస్తున్నారా? ప్లేలిస్ట్ లో మొదటి నుంచి వినండి.\n\n"
                    f"Vishnu Sahasranamam, one verse a day with its meaning in Telugu and English.\n\n{hashtags}")
        else:
            title = f"विष्णु सहस्रनाम | {first} | अर्थ सहित"
            hashtags = "#VishnuSahasranamam #विष्णुसहस्रनाम #Vishnu #Shorts"
            desc = (f"श्री विष्णु सहस्रनाम स्तोत्र\n\n{verse}\n\nअर्थ: {meaning}\n\nMeaning in English: {en}\n\n"
                    f"विष्णु सहस्रनाम का एक श्लोक रोज़, अर्थ सहित। नए हैं? प्लेलिस्ट में पहले श्लोक से सुनें।\n\n"
                    f"Vishnu Sahasranamam, one verse a day with its meaning in Hindi and English.\n\n{hashtags}")
        title_en = "Vishnu Sahasranamam verse with meaning | Daily Vishnu Stotram"
        return title[:100], desc, SERIES_TAGS[key], title_en, f"Vishnu Sahasranamam: {en}\n\n{hashtags}"
    if key in ("vedas_te", "vedas_hi"):
        from mahanavi.content import vedas as vd

        m = vd.MANTRAS[day]
        if key == "vedas_te":
            title = m.title_te
            hashtags = "#Vedas #VedaMantra #" + vd.HEAD_EN[m.veda] + " #వేదాలు #Shorts"
            desc = (f"{m.ref_te}\n\n{m.sa}\n\n{m.te_read}\n\nఅర్థం: {m.te_mean}\n\nMeaning in English: {m.en_mean}\n\n"
                    f"నాలుగు వేదాల నుండి రోజుకో మంత్రం, అర్థంతో. ఇంతకు ముందు చూడనివారు ప్లేలిస్ట్ లో మొదటి నుండి చూడండి.\n\n"
                    f"One Vedic mantra every day with its meaning: {m.ref_en}.\n\n{hashtags}")
        else:
            title = m.title_hi
            hashtags = "#Vedas #VedaMantra #" + vd.HEAD_EN[m.veda] + " #वेद #Shorts"
            desc = (f"{m.ref_hi}\n\n{m.sa}\n\nअर्थ: {m.hi_mean}\n\nMeaning in English: {m.en_mean}\n\n"
                    f"चारों वेदों से रोज़ एक मंत्र, अर्थ सहित। नए हैं? प्लेलिस्ट में शुरू से देखें।\n\n"
                    f"One Vedic mantra every day with its meaning: {m.ref_en}.\n\n{hashtags}")
        return title[:100], desc, SERIES_TAGS[key], m.title_en[:100], f"{m.ref_en}: {m.en_mean}\n\n{hashtags}"
    if key == "shiv_tandav_hi":
        title = f"शिव ताण्डव स्तोत्र श्लोक {n} | हिंदी अर्थ सहित | Shiv Tandav Stotram"
        hashtags = "#ShivTandav #ShivTandavStotram #Mahadev #शिवताण्डव #Shorts"
        desc = (f"शिव ताण्डव स्तोत्र, श्लोक {n}\n\n{verse}\n\nअर्थ: {meaning}\n\nMeaning in English: {c.MEANING_EN[day]}\n\n"
                f"रावण रचित शिव ताण्डव स्तोत्र का एक श्लोक रोज़, हिंदी अर्थ के साथ। नए हैं? प्लेलिस्ट में श्लोक 1 से शुरू करें।\n\n"
                f"Shiv Tandav Stotram, verse {n} of {c.count()}, with its meaning in Hindi. One verse every day, none repeated.\n\n{hashtags}")
        title_en = f"Shiv Tandav Stotram, verse {n} with meaning"
        desc_en = f"Shiv Tandav Stotram, verse {n} of {c.count()}, with its meaning in Hindi. One verse every day.\n\n{hashtags}"
        return title[:100], desc, SERIES_TAGS[key], title_en, desc_en
    if key == "shiv_tandav_trance":
        line = verse.split("\n")[0]
        title = f"शिव ताण्डव ट्रांस जाप {n} | हर हर महादेव 🔱 | Mahadev Trance Beats"
        hashtags = "#ShivTandav #HarHarMahadev #MahadevTrance #महादेव #Shorts"
        desc = (f"शिव ताण्डव ट्रांस, जाप {n}\n\n{line}\n\nहर हर महादेव। हेडफ़ोन लगाकर सुनिए, यह जाप आपको भोलेनाथ से जोड़ेगा।\n\n"
                f"Shiv Tandav trance chant {n} of {c.count()}. One new chant loop every day.\n\n{hashtags}")
        return title[:100], desc, SERIES_TAGS[key], f"Shiv Tandav trance chant {n}, Har Har Mahadev", f"Shiv Tandav trance chant {n} of {c.count()}. One a day.\n\n{hashtags}"
    raise KeyError(key)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series", choices=sorted(vs.SERIES), required=True)
    ap.add_argument("--public", action="store_true", help="Upload public (default unlisted).")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date", default="")
    args = ap.parse_args(argv)
    s = vs.SERIES[args.series]
    settings = get_settings()
    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(vs.IST).date()
    day = vs.plan(args.series, today)
    if day is None:
        print(f"Nothing to post on {today} (series {args.series}: from {s.start} for {s.count} days).")
        return 0
    try:
        title, desc, tags, title_en, desc_en = metadata(args.series, day)
        desc, desc_en = strip_links(desc), strip_links(desc_en)
        print(f"{today} {args.series} day {day + 1}\nTITLE: {title}\n{desc}\n")
        from mahanavi.scripts.post_beej_mantra import music_for

        music = music_for(s.music_channel or s.channel, today, settings.alert_short_music_path)
        video = verse_short.render(args.series, day, settings.output_dir / "verse" / f"{args.series}_{day + 1:03d}.mp4", music)
        print(f"Rendered: {video}")
        if args.dry_run:
            return 0

        from googleapiclient.http import MediaFileUpload

        from mahanavi.publishers.youtube_shorts_uploader import DEFAULT_CATEGORY_ID, YouTubeShortsUploader

        youtube = YouTubeShortsUploader(settings)._build_service()  # noqa: SLF001
        got = youtube.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
        if s.channel_word not in got.lower():
            raise MahanaviError(f"NOT posting: the token acts as channel '{got}', expected the {s.channel_word} channel.")
        post_ledger.check(settings.youtube_token_file, title, desc)
        jitter.pause("verse short")
        body = {
            "snippet": {"title": title, "description": desc, "tags": [t for t in brand_tags(tags) if t.isascii()],
                        "categoryId": DEFAULT_CATEGORY_ID, "defaultLanguage": s.lang, "defaultAudioLanguage": s.lang},
            "status": {"privacyStatus": "public" if args.public else "unlisted", "selfDeclaredMadeForKids": False},
            "localizations": {"en": {"title": title_en[:100], "description": desc_en}},
        }
        media = MediaFileUpload(str(video), mimetype="video/mp4", chunksize=-1, resumable=True)
        video_id = str(youtube.videos().insert(part="snippet,status,localizations", body=body, media_body=media).execute()["id"])
        print(f"Channel: {got}\nUploaded: https://www.youtube.com/watch?v={video_id}")
        post_ledger.record(settings.youtube_token_file, title, desc, video_id)
        state = state_mod.load()
        state_mod.mark_posted(state, today.isoformat(), f"{args.series}_{day + 1}", video_id, True, dt.datetime.now(vs.IST).isoformat())
        state_mod.save(state)
        try:
            from channels.beej import playlists as pl
            from channels.engine import upload

            ptitle, pdesc = PLAYLISTS[args.series]
            pid = upload.find_or_create_playlist(youtube, ptitle, pdesc, s.lang)
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
