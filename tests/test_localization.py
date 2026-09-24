"""Behavior-level checks for the published, static legal pages."""

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("", "privacy", "terms", "children-privacy", "support")
LOCALES = {
    "en", "de", "es", "es-419", "fr", "hi", "ja", "ko",
    "pt", "pt-BR", "zh", "zh-Hant",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections = {}
        self.active = None
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section" and "locale-section" in attrs.get("class", "").split():
            self.active = attrs.get("data-locale")
            self.sections[self.active] = {"lang": attrs.get("lang"), "text": []}
        if tag == "a":
            self.links.append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag == "section":
            self.active = None

    def handle_data(self, data):
        if self.active is not None:
            self.sections[self.active]["text"].append(data)


class LocalizationRegressionTest(unittest.TestCase):
    def test_all_five_pages_have_app_locales_and_real_content(self):
        for page in PAGES:
            path = ROOT / page / "index.html"
            parser = PageParser()
            parser.feed(path.read_text(encoding="utf-8"))
            with self.subTest(page=page):
                self.assertEqual(LOCALES, set(parser.sections))
                for locale, section in parser.sections.items():
                    text = " ".join(section["text"])
                    self.assertTrue(section["lang"])
                    self.assertGreater(len(text), 220, (page, locale))
                    self.assertIn("Yido", text)
                    self.assertNotRegex(text, r"\[(?:TODO|TBD|待填写)\]")

    def test_private_contact_and_operator_are_visible_on_every_page(self):
        for page in PAGES:
            html = (ROOT / page / "index.html").read_text(encoding="utf-8")
            with self.subTest(page=page):
                self.assertIn("Wang Zhengzhong", html)
                self.assertIn("王正仲", html)
                self.assertIn("welcome.yido@foxmail.com", html)
                self.assertIn("mailto:welcome.yido@foxmail.com", html)

    def test_static_site_links_and_locale_controller_exist(self):
        for page in PAGES:
            html = (ROOT / page / "index.html").read_text(encoding="utf-8")
            with self.subTest(page=page):
                self.assertIn("assets/locale.js", html)
                self.assertEqual(12, len(re.findall(r'class="locale-choice"', html)))
                self.assertNotIn('href="/privacy/"', html)
        self.assertTrue((ROOT / "assets" / "locale.js").is_file())

    def test_support_does_not_send_families_to_private_repo_issues(self):
        html = (ROOT / "support" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("github.com/madlabx/yido/issues", html)
        self.assertEqual(24, html.count("mailto:welcome.yido@foxmail.com"))

    def test_terms_distinguish_app_experience_from_store_trial(self):
        html = (ROOT / "terms" / "index.html").read_text(encoding="utf-8")
        self.assertEqual(12, html.count('class="callout"'))
        self.assertIn("not an App Store or Google Play free trial", html)
        self.assertIn("不是 App Store 或 Google Play 的商店免费试用", html)

    def test_internal_links_resolve_to_existing_pages(self):
        for page in PAGES:
            path = ROOT / page / "index.html"
            parser = PageParser()
            parser.feed(path.read_text(encoding="utf-8"))
            for href in parser.links:
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc or href.startswith("#"):
                    continue
                target = (path.parent / parsed.path).resolve()
                if not parsed.path or parsed.path.endswith("/"):
                    target /= "index.html"
                with self.subTest(page=page, href=href):
                    self.assertTrue(target.is_file(), target)


if __name__ == "__main__":
    unittest.main()
