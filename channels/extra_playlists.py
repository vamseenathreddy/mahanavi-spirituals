"""Extra playlists for the same videos, each aimed at a different search (lyrics/meaning, occasion, morning or benefit).
add_video() is called by the posters after the main playlist; backfill() copies the videos already posted (oldest first)."""
from __future__ import annotations

from channels.beej import playlists as pl
from channels.engine import upload

# series key -> (token file name, language)
CHANNELS = {
    "vishnu_te": ("youtube_token.json", "te"), "shiva_te": ("youtube_token.json", "te"), "jeevitha_te": ("youtube_token.json", "te"), "vedas_te": ("youtube_token.json", "te"), "lakshmi_te": ("youtube_token.json", "te"),
    "vishnu_hi": ("youtube_token_mantra_sangam.json", "hi"), "vedas_hi": ("youtube_token_mantra_sangam.json", "hi"),
    "lakshmi_hi": ("youtube_token_trance_beats.json", "hi"),
}

# Series whose extras are filled only by the daily sync job (sync_extra_playlists.py), never at upload time:
# key -> (token file, language, prefix of the main playlist's title)
SYNC_ONLY = {
    "chanakya_te": ("youtube_token.json", "te", "చాణక్య నీతి సూత్రాలు"),
    "gita_te": ("youtube_token.json", "te", "Bhagavad Gita Sloka"),
    "beej_te": ("youtube_token.json", "te", "బీజ మంత్రాలు"),
    "ramayana_te": ("youtube_token.json", "te", "Ramayana Stories"),
    "pooja_rules_te": ("youtube_token.json", "te", "పూజా నియమాలు"),
    "chanakya_hi": ("youtube_token_mantra_sangam.json", "hi", "चाणक्य नीति सूत्र"),
    "beej_hi_sangam": ("youtube_token_mantra_sangam.json", "hi", "बीज मंत्र"),
}

EXTRA: dict[str, list[tuple[str, str]]] = {
    "chanakya_te": [
        ("చాణక్య నీతి తెలుగులో | Chanakya Neeti Quotes in Telugu with Meaning",
         "చాణక్య నీతి సూక్తులు తెలుగు అర్థంతో, నేటి జీవితానికి ఉదాహరణలతో. chanakya neeti in telugu, chanakya quotes telugu, chanakya niti telugu meaning.\nChanakya Neeti quotes in Telugu with modern examples."),
        ("డబ్బు, స్నేహం, విజయం గురించి చాణక్య సూత్రాలు | Chanakya Success Tips Telugu",
         "డబ్బు, స్నేహితులు, శత్రువులు, విజయం గురించి చాణక్యుడు చెప్పిన మాటలు. chanakya success tips telugu, chanakya money advice telugu, chanakya friendship quotes.\nChanakya's advice on money, friends, enemies and success."),
    ],
    "chanakya_hi": [
        ("चाणक्य नीति हिंदी में | Chanakya Neeti Quotes in Hindi with Meaning",
         "चाणक्य नीति के सूत्र हिंदी अर्थ और आज के उदाहरणों के साथ। chanakya neeti in hindi, chanakya quotes hindi, chanakya niti hindi meaning.\nChanakya Neeti quotes in Hindi with modern examples."),
        ("पैसा, दोस्ती और सफलता पर चाणक्य के विचार | Chanakya Success Tips Hindi",
         "पैसा, दोस्त, दुश्मन और सफलता पर चाणक्य की सीख। chanakya success tips hindi, chanakya money advice hindi, chanakya friendship quotes hindi.\nChanakya's advice on money, friends, enemies and success."),
    ],
    "gita_te": [
        ("భగవద్గీత శ్లోకాలు తెలుగు అర్థంతో | Bhagavad Gita Slokas in Telugu with Meaning",
         "భగవద్గీత శ్లోకాలు తెలుగు అర్థంతో. bhagavad gita slokas telugu, gita sloka with meaning telugu, bhagavad gita telugu lyrics.\nBhagavad Gita verses with Telugu meaning."),
        ("గీతా సారం, జీవిత పాఠాలు | Bhagavad Gita Life Lessons Telugu Shorts",
         "కృష్ణుడు గీతలో చెప్పిన జీవిత పాఠాలు, చిన్న వీడియోలలో. gita saram telugu, krishna life lessons telugu, bhagavad gita quotes telugu.\nLife lessons from the Bhagavad Gita in short videos."),
    ],
    "beej_te": [
        ("బీజ మంత్రాలు జపం | Beej Mantra Chanting Telugu | Om Mantra Shorts",
         "ఉదయం ధ్యానానికి బీజ మంత్రాలు. beej mantra telugu, beeja mantralu, om mantra chanting telugu, meditation mantra telugu.\nBeej mantras for morning meditation."),
        ("ధ్యాన మంత్రాలు, శాంతి కోసం | Meditation Mantras for Peace Telugu",
         "మనశ్శాంతి, ఏకాగ్రత కోసం వినే చిన్న మంత్రాలు. meditation mantras telugu, peace mantra telugu, mantra for focus.\nShort mantras for calm and focus."),
    ],
    "beej_hi_sangam": [
        ("बीज मंत्र जाप | Beej Mantra Chanting Hindi | Om Mantra Shorts",
         "सुबह के ध्यान के लिए बीज मंत्र। beej mantra hindi, beej mantra jaap, om mantra chanting, meditation mantra hindi.\nBeej mantras for morning meditation."),
        ("ध्यान मंत्र, शांति के लिए | Meditation Mantras for Peace Hindi",
         "मन की शांति और एकाग्रता के लिए छोटे मंत्र। meditation mantra hindi, shanti mantra, mantra for focus.\nShort mantras for calm and focus."),
    ],
    "ramayana_te": [
        ("రామాయణ కథలు తెలుగులో | Ramayana Stories in Telugu for Kids and Family",
         "రామాయణంలోని చిన్న కథలు, కుటుంబమంతా చూడదగినవి. ramayana stories telugu, ramayanam kathalu, rama katha telugu.\nShort Ramayana stories in Telugu for the whole family."),
        ("శ్రీరాముడు, హనుమంతుడు కథలు | Rama and Hanuman Stories Telugu",
         "శ్రీరాముడు, హనుమంతుడు, సీతమ్మ కథలు. sri rama stories telugu, hanuman stories telugu, sita devi stories.\nStories of Rama, Hanuman and Sita."),
    ],
    "pooja_rules_te": [
        ("పూజా విధానం, నియమాలు తెలుగులో | Pooja Vidhanam Telugu Tips",
         "ఇంట్లో పూజ ఎలా చేయాలి, ఏమి చేయకూడదు అనే చిన్న సూచనలు. pooja vidhanam telugu, pooja niyamalu, how to do pooja at home telugu.\nShort tips on how to do pooja at home."),
        ("వారం వారం పూజలు, వ్రతాలు | Weekday Pooja and Vratham Tips Telugu",
         "సోమవారం నుంచి ఆదివారం వరకు ఏ రోజు ఏ దేవుని పూజ, ఏకాదశి, ప్రదోషం నియమాలు. weekday pooja telugu, vratham rules telugu, ekadashi rules telugu.\nWhich god to worship on which day, plus Ekadashi and Pradosham rules."),
    ],
    "jeevitha_te": [
        ("తెలుగు మంచి మాటలు | Telugu Good Words and Life Quotes",
         "ప్రతిరోజూ మనసుకు శాంతినిచ్చే తెలుగు మంచి మాటలు, జీవిత పాఠాలు. telugu good words, telugu life quotes, manchi matalu telugu, telugu quotes about life.\nShort Telugu life quotes with meaning."),
        ("ఉదయం స్ఫూర్తి మాటలు | Morning Motivation Telugu Shorts",
         "రోజును ఉత్సాహంగా మొదలుపెట్టడానికి తెలుగు స్ఫూర్తి మాటలు. morning motivation telugu, telugu motivational quotes, positive thoughts telugu.\nMorning motivation in Telugu."),
        ("సంబంధాలు, స్నేహం, కుటుంబం గురించి మాటలు | Telugu Quotes on Friendship and Family",
         "స్నేహం, తల్లిదండ్రులు, క్షమ, ప్రేమ గురించి తెలుగు సూక్తులు. friendship quotes telugu, family quotes telugu, forgiveness quotes telugu.\nTelugu quotes on friendship, family and forgiveness."),
    ],
    "shiva_te": [
        ("శివ పంచాక్షర స్తోత్రం, లింగాష్టకం తెలుగు అర్థంతో | Lingashtakam Telugu Lyrics with Meaning",
         "శివ పంచాక్షర స్తోత్రం, లింగాష్టకం శ్లోకాలు తెలుగు లిపిలో, అర్థంతో. lingashtakam telugu lyrics, shiva panchakshara stotram telugu, shiva stotram telugu with meaning.\nShiva Panchakshara Stotram and Lingashtakam with Telugu meaning."),
        ("సోమవారం శివ మంత్రాలు | Monday Shiva Mantras Telugu | Sivayya Mantralu",
         "సోమవారం, ప్రదోషం, శివరాత్రి రోజుల్లో చదవడానికి శివయ్య మంత్రాలు, శ్లోకాలు. sivayya mantralu, monday shiva pooja telugu, om namah shivaya telugu, pradosham slokalu.\nShiva mantras and slokas for Mondays, Pradosham and Shivaratri."),
        ("ఉదయం శివ శ్లోకం 1 నిమిషం | Morning Shiva Slokam Telugu Shorts | మహా భక్తి",
         "రోజును శివ స్మరణతో మొదలుపెట్టండి. morning shiva slokam telugu, shivaya slokam shorts, maha bhakti, daily shiva sloka.\nStart the day with a one-minute Shiva sloka."),
    ],
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


def _retry404(fn, tries: int = 5, wait: int = 15):
    """A playlist created a moment ago answers 404 for a few seconds; try again before giving up."""
    import time

    for i in range(tries):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            if i == tries - 1 or "404" not in str(exc):
                raise
            print(f"playlist not ready yet, waiting {wait}s")
            time.sleep(wait)


def add_video(yt, key: str, video_id: str, lang: str) -> None:
    """Add one new video to every extra playlist of this series; one failure never blocks the others."""
    for title, desc in EXTRA.get(key, []):
        try:
            pid = upload.find_or_create_playlist(yt, title, desc, lang)
            print(f"Playlist '{title[:30]}': {'added' if _retry404(lambda: pl.add_once(yt, video_id, pid)) else 'already listed'}")
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: extra playlist failed: {type(exc).__name__}: {exc}")


def backfill(yt, key: str, main_title: str, main_desc: str, lang: str, max_adds: int = 80) -> int:
    """Create the extra playlists and copy every video of the main playlist (oldest first); returns the number added."""
    main_id = upload.find_or_create_playlist(yt, main_title, main_desc, lang)
    import time

    for p_id, p_title, count in pl.list_playlists(yt):
        print(f"  channel playlist {p_id}: {p_title[:60]} ({count})")
    items = []
    for attempt in range(4):       # a playlist created a moment ago can answer 404 for a few seconds
        try:
            items = list(pl._pages(lambda t: yt.playlistItems().list(part="contentDetails", playlistId=main_id, maxResults=50, pageToken=t)))  # noqa: SLF001
            break
        except Exception as exc:  # noqa: BLE001
            print(f"main playlist {main_id} not readable yet ({type(exc).__name__}), attempt {attempt + 1}")
            if attempt == 3:
                raise
            time.sleep(20)
    vids = [i["contentDetails"]["videoId"] for i in sorted(items, key=lambda i: i["contentDetails"].get("videoPublishedAt", ""))]
    print(f"{key}: {len(vids)} videos in the main playlist")
    added = 0
    for title, desc in EXTRA.get(key, []):
        pid = upload.find_or_create_playlist(yt, title, desc, lang)
        present = _retry404(lambda: pl.playlist_video_ids(yt, pid))
        print(f"playlist https://www.youtube.com/playlist?list={pid} ({title[:40]}), {len(present)} already in it")
        for v in vids:
            if added >= max_adds:
                print(f"::notice::stopped at {max_adds} additions (API quota); run again to continue")
                return added
            if _retry404(lambda: pl.add_once(yt, v, pid, present)):
                added += 1
    return added


def sync(yt, key: str, budget: int) -> int:
    """Copy the videos of the series' main playlist (found by title, never created) into its extra playlists, oldest first, adding at most `budget`
    videos; stops quietly when YouTube says the daily quota is used up. Returns the number added."""
    prefix = SYNC_ONLY[key][2] if key in SYNC_ONLY else None
    main = None
    for pid, title, _count in pl.list_playlists(yt):
        if prefix and title.startswith(prefix):
            main = pid
            break
        if not prefix and title == MAIN_TITLES.get(key):
            main = pid
            break
    if main is None:
        print(f"{key}: main playlist not found yet, skipped")
        return 0
    lang = (SYNC_ONLY.get(key) or CHANNELS[key])[1 if key in SYNC_ONLY else 1]
    items = list(pl._pages(lambda t: yt.playlistItems().list(part="contentDetails", playlistId=main, maxResults=50, pageToken=t)))  # noqa: SLF001
    vids = [i["contentDetails"]["videoId"] for i in sorted(items, key=lambda i: i["contentDetails"].get("videoPublishedAt", ""))]
    added = 0
    for title, desc in EXTRA.get(key, []):
        try:
            pid = upload.find_or_create_playlist(yt, title, desc, lang)
            present = _retry404(lambda: pl.playlist_video_ids(yt, pid))
            for v in vids:
                if added >= budget:
                    return added
                if _retry404(lambda: pl.add_once(yt, v, pid, present)):
                    added += 1
        except Exception as exc:  # noqa: BLE001
            print(f"{key}: stopped ({type(exc).__name__}: {str(exc)[:120]})")
            if "quota" in str(exc).lower() or "429" in str(exc) or "RATE_LIMIT" in str(exc):
                return added
    return added


MAIN_TITLES: dict[str, str] = {}   # filled for the verse and Lakshmi series by scripts/ci/sync_extra_playlists.py
