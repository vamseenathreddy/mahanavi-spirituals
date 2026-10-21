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


def test_every_song_can_be_matched_to_its_full_video_title():
    assert all(s.match for s in song_clips.SONGS)

    class Fake:
        def channels(self): return self
        def playlistItems(self): return self
        def list(self, **kw):
            self.kw = kw; return self
        def execute(self):
            if "mine" in self.kw:
                return {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "U"}}}]}
            return {"items": [{"snippet": {"title": "Sri Jogulamba Ashtakam Can CHANGE Your Life", "resourceId": {"videoId": "abc"}}}]}

    jog = next(s for s in song_clips.SONGS if s.slug == "jogulamba_ashtakam")
    assert song_clips.full_video_link(Fake(), jog).endswith("abc")
