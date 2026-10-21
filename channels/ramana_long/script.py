"""Script of the Self-enquiry long video for Ramana Maharshi TV (owner request 2026-10-21: a top search on the channel is
'ramana maharshi meditation technique'). The explanation is in the channel's own words; the only quotations are a few
short phrases credited to Sri Ramana's Who Am I? (Nan Yar?), published by Sri Ramanasramam (copyright Sri Ramanasramam),
so the text is not reproduced. Each slide: heading, English on-screen line, Telugu on-screen line, narration, pause after
(seconds of silent practice with the Om music)."""
from __future__ import annotations

TITLE_EN = "Ramana Maharshi Meditation Technique: Self-Enquiry (Who Am I?) Step by Step"
TITLE_TE = "రమణ మహర్షి ధ్యాన పద్ధతి: ఆత్మవిచారణ (నేను ఎవరిని?)"

SLIDES = [
    dict(label="Introduction", head="Self-Enquiry", en="The meditation technique of Sri Ramana Maharshi", te="శ్రీ రమణ మహర్షి ధ్యాన పద్ధతి",
         say="Welcome to Ramana Maharshi TV. In this video you will learn the meditation technique Sri Ramana Maharshi taught most "
             "often: self-enquiry, also called Atma Vichara. It is simple, it needs no mantra and no special place, and you can "
             "begin today. We will go step by step, with two short silent practice sessions. Sit comfortably, and let us begin.",
         pause=3),
    dict(label="What is self-enquiry", head="What is self-enquiry?", en="Turning attention back to the one who thinks", te="ఆలోచించే వానివైపు దృష్టిని మళ్లించడం",
         say="Most meditation asks you to focus on something outside yourself, such as a sound or an image. Self-enquiry turns your "
             "attention around, towards the one who is aware. Sri Ramana taught that the mind is only a bundle of thoughts, and that "
             "the first thought is the thought, I. Enquiry means following that I back to where it rises.",
         pause=4),
    dict(label="Step 1: Sit quietly", head="Step 1: Sit quietly", en="Back straight, eyes soft, body relaxed", te="వెన్ను నిటారుగా, కళ్లు మృదువుగా, శరీరం సడలింపుగా",
         say="Step one. Sit comfortably with your back straight and your hands resting. Close your eyes or keep them softly open. "
             "Take three slow breaths. There is nothing to achieve in this time. You are only going to watch your own mind.",
         pause=6),
    dict(label="Step 2: Notice a thought", head="Step 2: Notice a thought", en="Watch a thought arise, without following it", te="ఒక ఆలోచన రావడాన్ని గమనించండి, దాన్ని అనుసరించకండి",
         say="Step two. Soon a thought will arise. It may be a worry, a plan, or a memory. Do not push it away, and do not follow it "
             "into a story. Simply notice that a thought has arisen.",
         pause=6),
    dict(label="Step 3: To whom?", head="Step 3: Ask, to whom?", en="To whom does this thought arise? To me.", te="ఈ ఆలోచన ఎవరికి వచ్చింది? నాకు.",
         say="Step three is the heart of the practice. Ask yourself, to whom has this thought arisen? The answer is, to me. "
             "Now do not stop at the words. Ask, who am I, this me? Sri Ramana said that thoughts should be dealt with "
             "at the place where they arise, by turning inward, rather than by following them.",
         pause=8),
    dict(label="Step 4: Rest in the I", head="Step 4: Stay with the I", en="Not a mantra. Attention turned to the source.", te="మంత్రం కాదు. మూలం వైపు మళ్లిన దృష్టి.",
         say="Step four. The question, who am I, is not a mantra to repeat. It is a way of turning attention back to the feeling of "
             "I, the sense of simply being aware, which comes before any thought. Do not look for a clever answer. "
             "Stay with that quiet awareness for as long as it lasts.",
         pause=8),
    dict(label="Practice 1: Silent enquiry", head="Practice: two minutes", en="Silent self-enquiry", te="నిశ్శబ్ద ఆత్మవిచారణ",
         say="Now we will practise together for about two minutes. When a thought comes, ask, to whom does it arise? To me. Who am I? "
             "Then rest. Begin now.",
         pause=120),
    dict(label="Step 5: When thoughts return", head="Step 5: Begin again", en="Thoughts will return. Gently ask again.", te="ఆలోచనలు తిరిగి వస్తాయి. సున్నితంగా మళ్లీ ప్రశ్నించండి.",
         say="Step five. Thoughts will come back, again and again. This is not failure. Each time one arises, ask again, to whom? "
             "In Who Am I, Sri Ramana compares the enquiry to the stick used to stir a burning pyre. It destroys the other thoughts, "
             "and in the end it is destroyed itself, leaving only the Self.",
         pause=8),
    dict(label="Common mistakes", head="Common mistakes", en="Do not force. Do not analyse. Do not wait for visions.", te="బలవంతం వద్దు. విశ్లేషణ వద్దు. దర్శనాల కోసం ఎదురుచూడవద్దు.",
         say="Three common mistakes. First, forcing the mind to be silent. Second, analysing the question like a puzzle, "
             "instead of turning attention inward. Third, waiting for visions or special experiences. "
             "Sri Ramana said that practices such as breath control can quieten the mind for a while, "
             "but enquiry is the direct way, because it looks at the very source of the mind.",
         pause=8),
    dict(label="Surrender as another path", head="If enquiry feels difficult", en="Surrender to God, to the Self", te="ఆత్మవిచారణ కష్టమనిపిస్తే: శరణాగతి",
         say="If enquiry feels too hard at first, Sri Ramana taught that complete surrender is another way to the same goal. "
             "He compared it to a traveller who puts his luggage on the train instead of carrying it on his head. "
             "Give your worries to God, and rest.",
         pause=8),
    dict(label="Practice 2: Silent sitting", head="Practice: three minutes", en="Silent sitting", te="నిశ్శబ్ద ధ్యానం",
         say="Let us practise once more, for about three minutes. Use enquiry, or surrender, whichever feels natural. Begin now.",
         pause=180),
    dict(label="Closing", head="Daily practice", en="Ten quiet minutes every day", te="రోజూ పది నిమిషాల నిశ్శబ్దం",
         say="Thank you for sitting with me. Practise ten quiet minutes every day, at the same time if you can. "
             "This video is an introduction, and the teaching comes from Sri Ramana's own words in Who Am I, published by "
             "Sri Ramanasramam. Read the original, and visit Tiruvannamalai if you can. "
             "If this was useful, subscribe to Ramana Maharshi TV for daily teachings in Telugu and English. Om Namo Bhagavate Sri Ramanaya.",
         pause=6),
]

SOURCES = [
    "Who Am I? (Nan Yar?) by Sri Ramana Maharshi, Sri Ramanasramam, Tiruvannamalai",
    "Talks with Sri Ramana Maharshi, Sri Ramanasramam",
]
