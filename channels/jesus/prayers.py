"""Short closing prayers for the bottom of Jesus Shorts (replaces the playlist line). Telugu for quote Shorts, English for quiz Shorts."""
from datetime import datetime, timedelta, timezone

PRAYERS = [
    ("ప్రభువా, ఈ వాక్యం చదివిన ప్రతి ఒక్కరికి నీ సమాధానం దయచేయి. ఆమేన్", "Lord, give Your peace to everyone reading this. Amen"),
    ("యెహోవా నిన్ను ఆశీర్వదించి నిన్ను కాపాడును గాక. ఆమేన్", "May the Lord bless you and keep you. Amen"),
    ("ప్రభువా, ఈ రోజు మాకు నీ బలం, నీ ధైర్యం ఇవ్వు. ఆమేన్", "Lord, give us Your strength and courage today. Amen"),
    ("దేవా, నీ మీద నమ్మకం ఉంచే హృదయాన్ని మాకు ఇవ్వు. ఆమేన్", "God, give us a heart that trusts in You. Amen"),
    ("ప్రభువా, అనారోగ్యంతో ఉన్నవారికి నీ స్వస్థత దయచేయి. ఆమేన్", "Lord, bring Your healing to all who are unwell. Amen"),
    ("ప్రభువా, మా కుటుంబాలను నీ ప్రేమతో నింపు. ఆమేన్", "Lord, fill our families with Your love. Amen"),
    ("ప్రభువా, ఈ రోజు సరైన దారిలో నడిపించు. ఆమేన్", "Lord, guide our steps on the right path today. Amen"),
    ("ప్రభువా, మా భయాలన్నీ తీసివేసి నీ శాంతి ఇవ్వు. ఆమేన్", "Lord, take away our fears and give us Your peace. Amen"),
    ("ప్రభువా, ఈ రోజు నీ కృపకు వందనాలు. ఆమేన్", "Lord, thank You for Your grace today. Amen"),
    ("ప్రభువా, నిరాశలో ఉన్నవారికి ఆశ ఇవ్వు. ఆమేన్", "Lord, give hope to those who feel hopeless. Amen"),
    ("ప్రభువా, మాకు జ్ఞానం, వివేకం ప్రసాదించు. ఆమేన్", "Lord, grant us wisdom and understanding. Amen"),
    ("ప్రభువా, క్షమించే, ప్రేమించే హృదయం ఇవ్వు. ఆమేన్", "Lord, give us hearts that forgive and love. Amen"),
    ("ప్రభువా, నీ రెక్కల నీడలో మమ్మల్ని కాపాడు. ఆమేన్", "Lord, keep us safe under the shadow of Your wings. Amen"),
    ("ప్రభువా, నీ సంతోషంతో మా హృదయాలను నింపు. ఆమేన్", "Lord, fill our hearts with Your joy. Amen"),
    ("ప్రభువా, మా విశ్వాసాన్ని బలపరచు. ఆమేన్", "Lord, strengthen our faith. Amen"),
    ("ప్రభువా, మా శ్రమను ఆశీర్వదించు. ఆమేన్", "Lord, bless the work of our hands. Amen"),
]


def _idx(offset: int = 0) -> int:
    now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    return (now.date().toordinal() * 3 + now.hour // 8 + offset) % len(PRAYERS)


def telugu() -> str:
    return PRAYERS[_idx()][0]


def english() -> str:
    return PRAYERS[_idx(5)][1]
