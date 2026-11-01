from mahanavi.content.links import strip_links


def test_label_only_link_lines_are_dropped():
    t = "Intro line\n\n🎬 వీడియోలు: https://www.youtube.com/@MahanaviSpirituals/videos\n📱 షార్ట్స్: https://www.youtube.com/@MahanaviSpirituals/shorts\n\n#Shorts"
    assert strip_links(t) == "Intro line\n\n#Shorts"


def test_text_kept_when_a_link_is_inline():
    assert strip_links("Source: Eenadu https://eenadu.net/x") == "Source: Eenadu"
    assert strip_links("Join: https://chat.whatsapp.com/abc\nతమ్ముళ్లూ #TDP") == "తమ్ముళ్లూ #TDP"


def test_no_links_unchanged():
    t = "ఓం నమః శివాయ\n\n#Shiva @MahanaviSpirituals"
    assert strip_links(t) == t and strip_links(None) == "" and strip_links("") == ""
