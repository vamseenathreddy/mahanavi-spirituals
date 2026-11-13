"""Title, description and tags for the Lakshmi Ashtottara long video and its daily live loop (Telugu + English SEO)."""

TITLE = "Powerful Mahalakshmi Stotram | లక్ష్మీ అష్టోత్తర శతనామావళి | Lakshmi Devi 108 Names | Revathy VSL"

LIVE_TITLE = "LIVE Lakshmi Devi Songs | లక్ష్మీ అష్టోత్తర శతనామావళి | Powerful Mahalakshmi Stotram | Meditation"

DESCRIPTION = """శ్రీ లక్ష్మీ అష్టోత్తర శతనామావళి (108 నామాలు) ధ్యానం కోసం. ప్రశాంతంగా కళ్ళు మూసుకుని వినండి, మనసులో నామాలను స్మరించండి.

Sri Lakshmi Ashtottara Shatanamavali, the 108 names of Goddess Mahalakshmi, as a calm meditation chant in Telugu. Sit quietly, close your eyes and listen with devotion, especially on Fridays and during your daily puja.

Singer: Revathy VSL
Channel: Mahanavi Spirituals

శుక్రవారం లక్ష్మీ పూజ, వరలక్ష్మీ వ్రతం, దీపావళి, ధన త్రయోదశి వేళల్లో వినడానికి అనుకూలం.
Good for Friday Lakshmi puja, Varalakshmi Vratam, Diwali, Dhanteras, morning and evening prayer, and quiet meditation.

తెలుగులో ప్రతిరోజూ ఒక్కో నామం అర్థంతో Shorts చూడండి: Mahanavi Spirituals ఛానల్‌ను Subscribe చేయండి.
Watch one name with its meaning every day in Shorts. Subscribe to Mahanavi Spirituals for daily Telugu devotional content.

Music and vocals were produced with AI-assisted tools. This video contains realistic synthetic visuals.

Search words: Lakshmi devi songs, powerful Mahalakshmi stotram, devotional melody songs Telugu, manifestation meditation in Telugu, negative energy removal mantra, Telugu devotional songs.

#LakshmiAshtottara #Lakshmi108Names #LakshmiShatanamavali #MahalakshmiMantra #TeluguDevotional #MahanaviSpirituals #లక్ష్మీఅష్టోత్తరం
"""

TAGS = [
    "Lakshmi devi songs", "powerful Mahalakshmi stotram", "Lakshmi Ashtottara Shatanamavali", "Lakshmi 108 names",
    "లక్ష్మీ అష్టోత్తర శతనామావళి", "devotional melody songs Telugu", "manifestation meditation in Telugu",
    "negative energy removal mantra", "Telugu devotional songs", "Mahanavi Spirituals", "Revathy VSL",
    "Lakshmi mantra", "Friday Lakshmi puja", "Lakshmi meditation", "devotional songs channel",
]

assert len(TITLE) <= 100, len(TITLE)
assert len(LIVE_TITLE) <= 100, len(LIVE_TITLE)
assert sum(len(t) + 1 for t in TAGS) < 480
