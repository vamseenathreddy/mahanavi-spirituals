from mahanavi.publishers import desc_clean as d


def test_removes_all_variants():
    te = "శ్రీ మంత్రం\n\nఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు\n\nfooter"
    assert "మళ్లీ" not in d.clean(te) and "footer" in d.clean(te)
    te2 = "x ఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే\nఈ ఛానల్ మీకు\nమళ్లీ కనిపించకపోవచ్చు 🙏 y"
    assert "కనిపించ" not in d.clean(te2)
    assert "కనిపించ" not in d.clean("ఇప్పుడే సబ్‌స్క్రైబ్ చేయండి, లేకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు")
    hi = "अभी सब्सक्राइब नहीं किया तो यह चैनल आपको दोबारा शायद न दिखे 🙏\nrest"
    assert d.clean(hi) == "rest"
    assert "दिखे" not in d.clean("अभी सब्सक्राइब करें, वरना यह चैनल शायद दोबारा आपको न दिखे")
    en = "YOU MAY NEVER SEE THIS\nCHANNEL AGAIN UNLESS YOU\nSUBSCRIBE RIGHT NOW\nkeep"
    assert d.clean(en) == "keep"
    assert d.clean("You may never see this channel again unless you subscribe right now! 🙏 Subscribe for more.") == "Subscribe for more."


def test_other_text_untouched():
    t = "రోజూ ఉదయం కొత్త మంత్రం\n\nసబ్‌స్క్రైబ్ చేయండి"
    assert d.clean(t) == t


def test_wrap_cleans_insert_body_and_localizations():
    seen = {}

    class V:
        def insert(self, **kw):
            seen.update(kw)
            return "req"

    class Y:
        def videos(self):
            return V()

    y = d.wrap(Y())
    body = {"snippet": {"description": "a You may never see this channel again unless you subscribe right now."},
            "localizations": {"en": {"description": "b You may never see this channel again unless you subscribe right now!"}}}
    assert y.videos().insert(part="snippet", body=body) == "req"
    assert seen["body"]["snippet"]["description"] == "a"
    assert seen["body"]["localizations"]["en"]["description"] == "b"
