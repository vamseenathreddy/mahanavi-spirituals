

def test_devotee_stories_come_first_in_the_life_slot():
    import datetime as dt

    from src.pick import choose_row

    rows = [{"id": "l001", "category": "life", "english": "x", "special": ""},
            {"id": "d001", "category": "life", "english": "y", "special": ""},
            {"id": "q001", "category": "quote", "english": "z", "special": ""}]
    row, _ = choose_row(rows, dt.date(2026, 10, 22), [], slot="life")
    assert row["id"] == "d001"
