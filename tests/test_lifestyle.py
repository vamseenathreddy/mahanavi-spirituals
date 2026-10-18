import os
from datetime import date

os.environ["LIFESTYLE_FAKE_TTS"] = "1"

from channels.lifestyle import post, render, topics, voice  # noqa: E402


def test_every_theme_has_sourced_points_in_both_languages():
    for th in topics.THEMES:
        n = len(th["te"]["points"])
        assert n in (12, 30) and len(th["hi"]["points"]) == n
        for lang in ("te", "hi"):
            assert all(t.strip() and b.strip() and s.strip() for t, b, s in th[lang]["points"])


def test_no_point_repeats_inside_a_video_or_across_themes():
    for lang in ("te", "hi"):
        titles, bodies = [], []
        for th in topics.THEMES:
            titles += [t for t, _b, _s in th[lang]["points"]]
            bodies += [b for _t, b, _s in th[lang]["points"]]
        assert len(set(titles)) == len(titles) and len(set(bodies)) == len(bodies)


def test_second_theme_is_30_points_and_next_sunday_picks_it():
    assert len(topics.THEMES[1]["te"]["points"]) == 30
    assert topics.theme_for(date(2026, 10, 25)) is topics.THEMES[1]
    assert topics.theme_for(date(2026, 10, 18)) is topics.THEMES[0]


def test_titles_are_hooks_with_a_question():
    for lang in ("te", "hi"):
        assert "?" in topics.THEMES[1][lang]["title"]


def test_no_em_dash_in_lifestyle_text():
    for th in topics.THEMES:
        for lang in ("te", "hi"):
            blob = th[lang]["title"] + "".join(t + b + s for t, b, s in th[lang]["points"])
            assert "\u2014" not in blob


def test_spans_voice_timeline_and_scroll_for_thirty_points(tmp_path):
    th = topics.THEMES[1]
    for lang in ("te", "hi"):
        spans: list = []
        strip = render.build_strip(lang, th, spans=spans)
        assert len(spans) == 30 + 2 and all(a < b for a, b in spans)
        texts = render.narration_texts(lang, th)
        assert len(texts) == len(spans)
        starts, total = voice.timeline([8.0] * len(texts), render.MIN_SECONDS)
        assert total >= 300 and starts == sorted(starts)
        ch = render.chapter_seconds(starts)
        assert len(ch) == 30 and all(b - a >= 10 for a, b in zip(ch, ch[1:]))
        expr = render.scroll_expr(spans, starts, [8.0] * len(texts))
        assert expr.count("clip(") == len(spans) - 1
        speed = (spans[-1][0] - spans[0][0]) / (starts[-1] - starts[0])
        assert speed > 50          # px per second: the old 12-point video scrolled at about 22
        assert strip.height > 12000


def test_voice_timeline_keeps_gaps_when_narration_is_long():
    starts, total = voice.timeline([12.0] * 32, 300)
    assert total >= 300 and all(b - a >= 12.0 for a, b in zip(starts, starts[1:]))


def test_fake_voice_clips_assemble(tmp_path):
    clips = voice.synth_clips(["one two three four five six", "seven eight nine"], "te", tmp_path)
    durs = voice.durations(clips)
    assert all(d > 1 for d in durs)
    starts, total = voice.timeline(durs, 20)
    voice.assemble(clips, starts, total, tmp_path / "v.wav")
    assert (tmp_path / "v.wav").stat().st_size > 20 * voice.RATE


def test_metadata_title_fits_and_description_has_chapters_and_disclaimer():
    for th in topics.THEMES:
        for key in ("te", "hi", "tb"):
            lang = post.CHANNELS[key]["lang"]
            n = len(th[lang]["points"])
            meta = post.metadata(key, th, [10 + 15 * i for i in range(n)])
            assert len(meta["title"]) <= 100
            assert "0:00" in meta["description"] and topics.DISCLAIMER[lang] in meta["description"]


def test_trance_beats_uses_its_own_backgrounds_and_music():
    ch = post.CHANNELS["tb"]
    assert sorted(ch["assets"].glob(ch["bg_glob"])) and sorted(ch["assets"].glob(ch["music_glob"]))
    assert ch["assets"] != post.CHANNELS["hi"]["assets"]


def test_gate_window_is_ten_to_ten_thirty():
    from channels.lifestyle import gate
    assert (gate.WINDOW_START.hour, gate.WINDOW_START.minute, gate.WINDOW_MINUTES) == (10, 0, 30)


def test_split_recording_cuts_at_pauses(tmp_path):
    import math, struct, wave
    from channels.lifestyle import voice
    R, buf = voice.RATE, bytearray()
    for i in range(5):
        buf += b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * (200 + i * 30) * k / R))) for k in range(R * 2))
        buf += b"\0\0" * int(R * 1.3)
    src = tmp_path / "take.wav"
    with wave.open(str(src), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(R); w.writeframes(bytes(buf))
    clips = voice.split_recording(src, 5, tmp_path / "w")
    assert len(clips) == 5
    import pytest
    with pytest.raises(RuntimeError):
        voice.split_recording(src, 9, tmp_path / "w2")
