"""Extra playlists for the same videos, each aimed at a different search (lyrics/meaning, occasion, morning or benefit).
add_video() is called by the posters after the main playlist; backfill() copies the videos already posted (oldest first)."""
from __future__ import annotations

from channels.beej import playlists as pl
from channels.engine import upload

# series key -> (token file name, language)
CHANNELS = {
    "vishnu_te": ("youtube_token.json", "te"), "vedas_te": ("youtube_token.json", "te"), "lakshmi_te": ("youtube_token.json", "te"),
    "vishnu_hi": ("youtube_token_mantra_sangam.json", "hi"), "vedas_hi": ("youtube_token_mantra_sangam.json", "hi"),
    "lakshmi_hi": ("youtube_token_trance_beats.json", "hi"),
}

EXTRA: dict[str, list[tuple[str, str]]] = {
    "vishnu_te": [
        ("విష్ణు సహస్రనామం తెలుగు అర్థంతో | Vishnu Sahasranamam Lyrics in Telugu with Meaning",
         "విష్ణు సహస్రనామం శ్లోకాలు తెలుగు లిపిలో, ప్రతి శ్లోకానికి సులభమైన తెలుగు అర్థంతో. vishnu sahasranamam lyrics in telugu with meaning, vishnu sahasranama stotram telugu, sri vishnu sahasranamam telugu lyrics.\nVishnu Sahasranamam verses in Telugu script with a simple meaning for each."),
        ("ఏకాదశి, గురువారం విష్ణు శ్లోకాలు | Ekadashi and Thursday Vishnu Slokas Telugu",
         "ఏకాదశి, గురువారం విష్ణు పూజలో చదవడానికి విష్ణు సహస్రనామ శ్లోకాలు. ekadashi slokas telugu, thursday vishnu pooja telugu, narayana stotram telugu.\nVishnu slokas for Ekadashi and Thursday worship, with meaning."),
        ("ఉదయం 1 నిమిషం శ్లోకాలు | Morning Slokas Telugu | Vishnu Stotram Shorts",
         "ఉదయం లేవగానే ఒక నిమిషంలో వినే విష్ణు శ్లోకాలు. morning slokas telugu, vishnu stotram shorts telugu, daily sloka telugu, sri maha vishnu slokas.\nOne-minute Vishnu slokas to start the day."),
    ],
    "vishnu_hi": [
        ("विष्णु सहस्रनाम हिंदी अर्थ सहित | Vishnu Sahasranamam Lyrics in Hindi with Meaning",
         "विष्णु सहस्रनाम के श्लोक देवनागरी में, हर श्लोक का सरल हिंदी अर्थ। vishnu sahasranamam in hindi with meaning, विष्णु सहस्रनाम लिरिक्स हिंदी, vishnu sahasranam stotra hindi.\nVishnu Sahasranamam verses in Devanagari with a simple Hindi meaning."),
        ("एकादशी और गुरुवार विष्णु श्लोक | Ekadashi and Thursday Vishnu Shlok Hindi",
         "एकादशी और गुरुवार की विष्णु पूजा में पढ़ने के लिए विष्णु सहस्रनाम श्लोक। ekadashi shlok hindi, guruvar vishnu puja, narayan stotra hindi.\nVishnu shlokas for Ekadashi and Thursday worship, with meaning."),
        ("सुबह 1 मिनट श्लोक | Morning Shlok Hindi | Vishnu Stotra Shorts",
         "सुबह उठते ही एक मिनट में सुनें विष्णु श्लोक। morning shlok hindi, vishnu stotra shorts, daily shlok, shri hari mantra.\nOne-minute Vishnu shlokas to start the day."),
    ],
    "vedas_te": [
        ("వేద మంత్రాలు తెలుగు అర్థంతో | Vedic Mantras with Telugu Meaning",
         "వేద మంత్రాలు సంస్కృత పాఠంతో, తెలుగులో సులభమైన అర్థంతో. vedic mantras with meaning in telugu, veda mantra telugu, rigveda mantra telugu, yajurveda mantra telugu.\nVedic mantras with a simple Telugu meaning."),
        ("శాంతి మంత్రాలు | Vedic Shanti Mantras Telugu",
         "మనశ్శాంతి, ఏకాగ్రత కోసం వినే వేద మంత్రాలు. shanti mantra telugu, vedic chanting for peace, om shanti mantra telugu.\nVedic mantras to listen to for calm and focus."),
        ("ఉదయం వేద మంత్రం 1 నిమిషం | Morning Vedic Mantra Telugu Shorts",
         "రోజు మొదలుపెట్టే ముందు ఒక నిమిషం వేద మంత్రం. morning vedic mantra telugu, daily veda mantra shorts, mantra for morning.\nOne-minute Vedic mantra to start the day."),
    ],
    "vedas_hi": [
        ("वेद मंत्र हिंदी अर्थ सहित | Vedic Mantras with Hindi Meaning",
         "वेद मंत्र संस्कृत पाठ और सरल हिंदी अर्थ के साथ। vedic mantras with meaning in hindi, ved mantra hindi, rigveda mantra hindi, yajurveda mantra hindi.\nVedic mantras with a simple Hindi meaning."),
        ("शांति मंत्र | Vedic Shanti Mantras Hindi",
         "मन की शांति और एकाग्रता के लिए सुनें वेद मंत्र। shanti mantra hindi, vedic chanting for peace, om shanti mantra hindi.\nVedic mantras to listen to for calm and focus."),
        ("सुबह का वेद मंत्र 1 मिनट | Morning Vedic Mantra Hindi Shorts",
         "दिन शुरू करने से पहले एक मिनट वेद मंत्र। morning vedic mantra hindi, daily ved mantra shorts, subah ke mantra.\nOne-minute Vedic mantra to start the day."),
    ],
    "lakshmi_te": [
        ("లక్ష్మీ అష్టోత్తర శతనామావళి తెలుగు అర్థంతో | Lakshmi Ashtottara Shatanamavali Telugu",
         "లక్ష్మీ అష్టోత్తర శతనామావళి నామాలు, ప్రతి నామానికి అర్థంతో. lakshmi ashtottara shatanamavali telugu, lakshmi 108 names telugu with meaning, sri lakshmi ashtothram telugu lyrics.\nLakshmi 108 names with the meaning of each name."),
        ("శుక్రవారం లక్ష్మీ పూజ | Friday Lakshmi Pooja Telugu",
         "శుక్రవారం లక్ష్మీ పూజలో చదవడానికి లక్ష్మీ నామాలు. friday lakshmi pooja telugu, lakshmi devi pooja vidhanam, varalakshmi vratham telugu.\nLakshmi names for Friday worship."),
        ("ఐశ్వర్యం, శాంతి కోసం లక్ష్మీ నామాలు | Lakshmi Mantras for Prosperity Telugu",
         "ఇంట్లో శాంతి, శుభం కోసం ప్రార్థనగా వినే లక్ష్మీ నామాలు. lakshmi mantra for prosperity telugu, lakshmi devi stotram telugu, mahalakshmi names telugu.\nLakshmi names to listen to as a prayer for prosperity and peace at home."),
    ],
    "lakshmi_hi": [
        ("लक्ष्मी अष्टोत्तर शतनाम हिंदी अर्थ सहित | Lakshmi Ashtottara Shatanamavali Hindi",
         "लक्ष्मी अष्टोत्तर शतनाम, हर नाम के अर्थ के साथ। lakshmi ashtottara shatanamavali hindi, lakshmi 108 names hindi with meaning, laxmi ashtothram hindi lyrics.\nLakshmi 108 names with the meaning of each name."),
        ("शुक्रवार लक्ष्मी पूजा | Friday Lakshmi Puja Hindi",
         "शुक्रवार की लक्ष्मी पूजा में पढ़ने के लिए लक्ष्मी नाम। friday lakshmi puja hindi, laxmi puja vidhi, mahalakshmi mantra hindi.\nLakshmi names for Friday worship."),
        ("सुख समृद्धि के लिए लक्ष्मी नाम | Lakshmi Mantras for Prosperity Hindi",
         "घर में सुख, शांति और शुभता की प्रार्थना के रूप में सुनें लक्ष्मी नाम। lakshmi mantra for prosperity hindi, laxmi stotra hindi, mahalakshmi names hindi.\nLakshmi names to listen to as a prayer for prosperity and peace at home."),
    ],
}


def add_video(yt, key: str, video_id: str, lang: str) -> None:
    """Add one new video to every extra playlist of this series; one failure never blocks the others."""
    for title, desc in EXTRA.get(key, []):
        try:
            pid = upload.find_or_create_playlist(yt, title, desc, lang)
            print(f"Playlist '{title[:30]}': {'added' if pl.add_once(yt, video_id, pid) else 'already listed'}")
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: extra playlist failed: {type(exc).__name__}: {exc}")


def backfill(yt, key: str, main_title: str, main_desc: str, lang: str, max_adds: int = 80) -> int:
    """Create the extra playlists and copy every video of the main playlist (oldest first); returns the number added."""
    main_id = upload.find_or_create_playlist(yt, main_title, main_desc, lang)
    items = list(pl._pages(lambda t: yt.playlistItems().list(part="contentDetails", playlistId=main_id, maxResults=50, pageToken=t)))  # noqa: SLF001
    vids = [i["contentDetails"]["videoId"] for i in sorted(items, key=lambda i: i["contentDetails"].get("videoPublishedAt", ""))]
    print(f"{key}: {len(vids)} videos in the main playlist")
    added = 0
    for title, desc in EXTRA.get(key, []):
        pid = upload.find_or_create_playlist(yt, title, desc, lang)
        present = pl.playlist_video_ids(yt, pid)
        print(f"playlist https://www.youtube.com/playlist?list={pid} ({title[:40]}), {len(present)} already in it")
        for v in vids:
            if added >= max_adds:
                print(f"::notice::stopped at {max_adds} additions (API quota); run again to continue")
                return added
            if pl.add_once(yt, v, pid, present):
                added += 1
    return added
