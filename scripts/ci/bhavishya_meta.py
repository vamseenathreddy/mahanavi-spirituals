"""Title, description, tags for the Bhavishya Purana long text video (Telugu + English SEO)."""

TITLE = "Bhavishya Purana in Telugu | భవిష్య పురాణం: 11 జీవిత పాఠాలు | Life Lessons & Stories"

CHAPTERS = [
    ("0:00", "Intro | భవిష్య పురాణం"),
    ("0:10", "1. Kalavidu's Five Jewels | కళావిదుడి ఐదు రత్నాలు"),
    ("0:49", "2. Ratha Saptami | రథసప్తమి"),
    ("1:24", "3. Pancha Maha Yajnas | పంచ మహాయజ్ఞాలు"),
    ("2:05", "4. Pippalada Maharshi | పిప్పలాద మహర్షి"),
    ("2:49", "5. Roopasena and Veeravara | రూపసేనుడు, వీరవరుడు"),
    ("3:43", "6. Mother, Father, Guru | తల్లి, తండ్రి, గురువు"),
    ("4:18", "7. The Rules of Giving | దాన విధి"),
    ("5:03", "8. Gunakara's Sadhana | గుణాకరుడి సాధన"),
    ("5:49", "9. Gardens and Ponds | ఉద్యానవనాలు, చెరువులు"),
    ("6:25", "10. Karma, the Three Paths | కర్మ, మూడు మార్గాలు"),
    ("7:04", "11. Akshaya Tritiya and Annadanam | అక్షయ తృతీయ, అన్నదానం"),
    ("7:41", "Sarve Janah Sukhino Bhavantu"),
]

DESCRIPTION = """భవిష్య పురాణంలోని 11 జీవిత పాఠాలు, కథలు. ప్రశాంతమైన ధ్యాన సంగీతంతో, మీ వేగంతో చదువుతూ చూడండి.

11 life lessons and short stories from the Bhavishya Purana, written in Telugu on screen with calm meditation music. No voice, just read at your own pace. From the kindness of Kuchela-style sharing to the rules of giving, karma and Ratha Saptami.

Chapters:
""" + "\n".join(f"{t} {n}" for t, n in CHAPTERS) + """

తదుపరి రథసప్తమి: శనివారం, 13 ఫిబ్రవరి 2027
Next Ratha Saptami: Saturday, 13 February 2027

Source: Bhavishya Purana (from the Ashtadasa Puranalu). Stories are retold in simple words; please read the original text for full detail.

ప్రతిరోజూ పురాణ కథలు Shorts గా చూడటానికి Mahanavi Spirituals ను Subscribe చేయండి.
Subscribe to Mahanavi Spirituals for a Purana story every day in Shorts.

The artwork and music were created with AI-assisted tools. This video contains realistic synthetic visuals.

Search words: Bhavishya Purana in Telugu, భవిష్య పురాణం, Purana stories in Telugu, life lessons from Puranas, devotional songs channel, Telugu spiritual stories, Ratha Saptami.

#BhavishyaPurana #భవిష్యపురాణం #PuranaStories #TeluguDevotional #LifeLessons #RathaSaptami #MahanaviSpirituals
"""

TAGS = [
    "Bhavishya Purana in Telugu", "భవిష్య పురాణం", "Bhavishya Purana stories", "Purana stories in Telugu",
    "life lessons from Puranas", "Telugu spiritual stories", "Ratha Saptami", "Pancha Maha Yajna",
    "karma explained", "devotional songs channel", "meditation music", "Mahanavi Spirituals",
    "Telugu devotional", "Hindu stories", "Akshaya Tritiya",
]

assert len(TITLE) <= 100, len(TITLE)
assert sum(len(t) + (2 if " " in t else 0) + 1 for t in TAGS) < 480
