import tempfile
import unittest
from pathlib import Path

from bin.check_site_html import check_site


class SiteHtmlAccessibilityTests(unittest.TestCase):
    def check_fragment(self, html: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_text(html, encoding="utf-8")
            return check_site(Path(directory))

    def test_descriptive_image_alt_passes(self):
        self.assertEqual(self.check_fragment('<img src="poster.jpg" alt="Researcher presenting a poster">'), [])

    def test_missing_or_generic_image_alt_fails(self):
        errors = self.check_fragment('<img src="a.jpg"><img src="b.jpg" alt="image">')
        self.assertEqual(len(errors), 2)

    def test_explicitly_decorative_image_passes(self):
        self.assertEqual(self.check_fragment('<img src="divider.svg" alt="" role="presentation">'), [])

    def test_nested_links_fail(self):
        errors = self.check_fragment('<a href="/post/"><span><a href="/year/">2026</a></span></a>')
        self.assertEqual(len(errors), 1)


if __name__ == "__main__":
    unittest.main()
