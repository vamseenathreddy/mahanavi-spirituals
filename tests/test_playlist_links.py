from __future__ import annotations

from channels import playlist_links as pl


class _Seo:
    description = "BODY #a #b"

    def full_caption(self):
        return "CAP"

    title = "T"


def test_with_playlists_prepends_and_passes_through():
    w = pl.WithPlaylists(_Seo(), "TOP")
    assert w.description.startswith("TOP\n\nBODY")
    assert w.full_caption() == "TOP\n\nCAP"
    assert w.title == "T"


def test_with_playlists_empty_top_is_noop():
    w = pl.WithPlaylists(_Seo(), "")
    assert w.description == "BODY #a #b"


def test_block_current_first_and_all_three(monkeypatch):
    monkeypatch.setattr(pl, "resolve", lambda y, s: {"beej": "B", "puranas": "P", "muhurtas": "M"})
    lines = pl.block(None, None, "muhurtas").splitlines()
    assert "list=M" in lines[1] and lines[1].startswith("▶ ఈ ప్లేలిస్ట్")
    assert [("list=" + x) in "".join(lines) for x in "BPM"] == [True] * 3


def test_block_empty_on_failure(monkeypatch):
    def boom(y, s):
        raise RuntimeError("x")
    monkeypatch.setattr(pl, "resolve", boom)
    assert pl.block(None, None, "beej") == ""


def test_card_lines_three_short_lines():
    for v in pl.CARD_LINES.values():
        assert len(v.split("\n")) == 3
