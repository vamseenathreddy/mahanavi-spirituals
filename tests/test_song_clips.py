from datetime import date, timedelta

from mahanavi.content import song_clips


def test_every_song_has_clips_and_all_are_under_15_seconds():
    for song in song_clips.SONGS:
        clips = song_clips.clips_for(song)
        assert clips, song.slug
        assert all(path.exists() and 5 <= secs < 15 for path, secs in clips), song.slug


def test_rotation_uses_each_song_then_each_clip_without_early_repeat():
    start = date(2026, 10, 21)
    seen = [song_clips.pick(start + timedelta(days=i))[1] for i in range(len(song_clips.SONGS) * 8)]
    assert len(set(seen)) == len(seen)


def test_build_spec_fits_a_short():
    spec, clip = song_clips.build(date(2026, 10, 21))
    assert spec.total_seconds < 15 and clip.exists() and len(spec.title) <= 100
