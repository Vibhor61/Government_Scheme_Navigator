import unittest

from app.crawler.crawler_engine import SimpleHTMLTextExtractor


class CrawlerLinkContextTests(unittest.TestCase):
    def test_anchor_text_is_preserved_for_relevant_link_ranking(self):
        parser = SimpleHTMLTextExtractor("https://education.gov.in")
        parser.feed(
            '<html><body><a href="/schemes/csis">CSIS education loan guidelines</a></body></html>'
        )
        parser.close()

        self.assertEqual(
            parser.link_context,
            [{
                "url": "https://education.gov.in/schemes/csis",
                "text": "CSIS education loan guidelines",
            }],
        )


if __name__ == "__main__":
    unittest.main()
