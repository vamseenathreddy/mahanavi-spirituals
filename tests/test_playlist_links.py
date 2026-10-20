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


def test_block_items_current_first_skips_missing(monkeypatch):
    items = (("A", "id", "1"), ("B", "id", "2"), ("C", "id", ""))
    out = pl.block_items(None, items, current="B", header="H:")
    lines = out.splitlines()
    assert lines[0] == "H:" and lines[1].startswith("▶ B:") and lines[2].startswith("▶ A:") and len(lines) == 3


def test_block_items_empty_when_nothing_found():
    assert pl.block_items(None, (("A", "id", ""),), current="A") == ""


def test_engine_playlist_cta_does_not_shrink_text():
    import dataclasses

    from channels.engine import render
    from channels.mantra_sangam import channel_config as mc

    row = {"text_primary": "ॐ गं गणपतये नमः", "text_secondary": "x", "id": "1", "category": "mantra"}
    base = mc.RENDER_CFG
    with_pl = dataclasses.replace(base, playlist_cta=pl.HI_LINE.format(x="मंत्र"))
    lay = base.layouts[0]
    assert render.fit_text(row, lay, base)[3] == render.fit_text(row, lay, with_pl)[3]
    layer = render.make_text_layer(row, lay, with_pl)
    assert layer.size == (1080, 1920)
