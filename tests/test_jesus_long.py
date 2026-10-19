from channels.jesus_long import bank, metadata


def test_bank_has_complete_themes():
    d = bank.load()
    assert set(bank.ORDER) == set(d["themes"])
    for k, t in d["themes"].items():
        assert len(t["verses"]) == 15
        for v in t["verses"]:
            assert v["ref"] and len(v["text"].split()) >= 5 and "—" not in v["text"]


def test_theme_rotation_and_seo():
    k0, _ = bank.theme_for(0)
    assert bank.theme_for(len(bank.ORDER))[0] == k0
    _, th = bank.theme_for(0)
    t = metadata.title(th)
    assert len(t) <= 100 and "Bible Verses" in t
    d = metadata.description(th, [(0, "Introduction"), (14, "John 14:27")])
    assert "0:00 Introduction" in d and "0:14 John 14:27" in d and "#BibleVerses" in d
    assert "comment" not in d.lower()


def test_every_weekday_has_a_theme():
    import datetime as dt
    keys = {bank.theme_for_date(dt.date(2026, 10, 19) + dt.timedelta(days=i))[0] for i in range(7)}
    assert keys == set(bank.ORDER)
