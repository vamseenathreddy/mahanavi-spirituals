import numpy as np

from mahanavi.video import decor_clips as dc


def _px(rgb):
    return np.array([[rgb]], np.uint8).repeat(4, 0).repeat(4, 1)


def test_green_screen_removed_but_parrot_green_kept():
    assert dc.Clip._key(_px((0, 205, 0)), "strict")[..., 3].max() == 0
    assert dc.Clip._key(_px((150, 230, 40)), "strict")[..., 3].min() > 200     # the parrot stays
    assert dc.Clip._key(_px((90, 250, 30)), "floor")[..., 3].max() < 40        # the lit floor goes
    assert dc.Clip._key(_px((250, 250, 250)), "floor")[..., 3].min() == 255    # the unicorn stays


def test_decor_clips_exist():
    for v in dc.LAYERS.values():
        assert (dc.DECOR / v["file"]).exists()
