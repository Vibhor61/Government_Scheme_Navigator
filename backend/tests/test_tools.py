"""Unit tests for RouterTool and CrawlerTool."""

import unittest
from unittest.mock import patch, MagicMock
from app.crawler.router_tool import router_tool, RouterTool
from app.crawler.crawler_tool import crawler_tool, CrawlerTool


class AgentToolsTests(unittest.TestCase):

    def test_router_tool_metadata(self):
        """RouterTool has proper name and description."""
        self.assertEqual(router_tool.name, "scheme_router_tool")
        self.assertIn("citizen intent", router_tool.description)

    @patch("app.crawler.router.SchemeRouter.route")
    def test_router_tool_execution(self, mock_route):
        """RouterTool delegates properly to SchemeRouter."""
        mock_route.return_value = {
            "workflow": "SCHEME_DISCOVERY",
            "is_out_of_domain": False,
            "target_schemes": [],
        }
        res = router_tool.run(user_query="Need student scholarship")
        self.assertEqual(res["workflow"], "SCHEME_DISCOVERY")
        mock_route.assert_called_once()

    def test_crawler_tool_metadata(self):
        """CrawlerTool has proper name and description."""
        self.assertEqual(crawler_tool.name, "gov_crawler_tool")
        self.assertIn("verified, whitelist-guarded", crawler_tool.description)

    def test_crawler_tool_security_block(self):
        """CrawlerTool blocks non-government URLs with security status."""
        res = crawler_tool.crawl_url("https://malicious-scam-site.com/fake")
        self.assertFalse(res["success"])
        self.assertEqual(res["security_status"], "SECURITY_BLOCK")
        self.assertEqual(res["status_code"], 403)

    def test_crawler_tool_search_url_builder(self):
        """CrawlerTool constructs proper myScheme search endpoints."""
        url = crawler_tool.build_search_url("solar pump", scope="Central")
        self.assertIn("q=solar+pump", url)
        self.assertIn("level=Central", url)
        self.assertTrue(url.startswith("https://www.myscheme.gov.in"))

    def test_crawler_tool_detail_url_builder(self):
        """CrawlerTool constructs proper myScheme detail endpoints."""
        url = crawler_tool.build_detail_url("pm-kisan-samman-nidhi")
        self.assertIsNotNone(url)
        self.assertIn("slug=pm-kisan-samman-nidhi", url)
        self.assertTrue(url.startswith("https://www.myscheme.gov.in"))

        # Invalid slug returns None
        self.assertIsNone(crawler_tool.build_detail_url("invalid_slug_with_special!@#"))

    @patch("app.crawler.crawler_engine.GovCrawlerEngine.crawl_url")
    def test_crawler_tool_dispatch(self, mock_crawl):
        """CrawlerTool executes crawl action properly."""
        mock_crawl.return_value = {
            "success": True,
            "url": "https://www.myscheme.gov.in",
            "extracted_text": "sample text",
        }
        res = crawler_tool.run(action="crawl", url="https://www.myscheme.gov.in")
        self.assertTrue(res["success"])
        mock_crawl.assert_called_once()


if __name__ == "__main__":
    unittest.main()
