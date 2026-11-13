"""The subscribe reminder shown on every Telugu card Short, two lines at a larger size.

2026-11-14 (owner request): the generic "you may never see this channel again" line is replaced by a topic-specific
one in the same place on the card, e.g. "రేపటి ముహూర్తాల కోసం సబ్‌స్క్రైబ్ చేసి / ఆల్ నోటిఫికేషన్స్ బెల్ ఐకాన్ నొక్కండి".
`lines_for(topic)` returns the two lines for a card type."""

_TOPICS = {
    "muhurtam": "రేపటి ముహూర్తాల కోసం",
    "gita": "రేపటి గీతా శ్లోకం కోసం",
    "purana": "రేపటి పురాణ కథ కోసం",
    "purana_concept": "రేపటి పురాణ విశేషాల కోసం",
    "rashi": "మీ రాశి మంత్రం కోసం",
    "default": "రేపటి వీడియో కోసం",
}
_BELL = "ఆల్ నోటిఫికేషన్స్ బెల్ ఐకాన్ నొక్కండి"


def lines_for(topic: str = "default") -> tuple[str, str]:
    return (f"{_TOPICS.get(topic, _TOPICS['default'])} సబ్‌స్క్రైబ్ చేసి", _BELL)


OPINION_LINES = lines_for("muhurtam")
OPINION_TE = " ".join(OPINION_LINES)
OPINION_SIZE_FRAC = 0.062
