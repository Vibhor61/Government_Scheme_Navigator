import unittest
from unittest.mock import MagicMock, patch
from io import BytesIO
from pypdf import PdfWriter

from app.crawler.crawler_engine import (
    GovCrawlerEngine,
    SimpleHTMLTextExtractor,
    rank_scheme_links,
)
from app.crawler.browser_crawler import is_allowed_browser_asset_request
from app.crawler.whitelist import is_whitelisted_domain, is_valid_gov_host


class DeepCrawlerEngineeringTests(unittest.TestCase):
    def setUp(self):
        self.crawler = GovCrawlerEngine(request_timeout=5.0)

    def test_gov_domain_validator(self):
        # Genuine Indian Government domains
        self.assertTrue(is_valid_gov_host("pmkisan.gov.in"))
        self.assertTrue(is_valid_gov_host("scholarships.gov.in"))
        self.assertTrue(is_valid_gov_host("wcd.nic.in"))
        self.assertTrue(is_valid_gov_host("edistrict.up.gov.in"))
        self.assertTrue(is_valid_gov_host("myscheme.gov.in"))

        # Spoofed and commercial domains must be blocked
        self.assertFalse(is_valid_gov_host("myscheme.gov.in.attacker.example"))
        self.assertFalse(is_valid_gov_host("fake-gov.in"))
        self.assertFalse(is_valid_gov_host("gov.in.evil.com"))
        self.assertFalse(is_valid_gov_host("google.com"))

    def test_browser_asset_cdn_allowlist(self):
        # CDN assets required for SPA hydration must be allowed
        self.assertTrue(is_allowed_browser_asset_request("https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/react.min.js"))
        self.assertTrue(is_allowed_browser_asset_request("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"))
        self.assertTrue(is_allowed_browser_asset_request("https://fonts.googleapis.com/css?family=Roboto"))
        self.assertTrue(is_allowed_browser_asset_request("https://pmkisan.gov.in/static/app.bundle.js"))

        # Trackers and external commercial domains must be blocked
        self.assertFalse(is_allowed_browser_asset_request("https://google-analytics.com/analytics.js"))
        self.assertFalse(is_allowed_browser_asset_request("https://unverified-third-party.com/tracker.js"))

    def test_rank_scheme_links_prioritizes_guidelines_and_pdfs(self):
        base_url = "https://pmkisan.gov.in"
        links = [
            "https://pmkisan.gov.in/Documents/Guidelines_PMKISAN.pdf",
            "https://pmkisan.gov.in/AboutScheme.aspx",
            "https://pmkisan.gov.in/Login.aspx",
            "https://pmkisan.gov.in/Tenders.aspx",
            "https://pmkisan.gov.in/FAQ.aspx",
        ]
        link_context = [
            {"url": "https://pmkisan.gov.in/Documents/Guidelines_PMKISAN.pdf", "text": "Operational Guidelines"},
            {"url": "https://pmkisan.gov.in/AboutScheme.aspx", "text": "About The Scheme and Eligibility"},
            {"url": "https://pmkisan.gov.in/Login.aspx", "text": "Officer Login"},
            {"url": "https://pmkisan.gov.in/Tenders.aspx", "text": "Active Tenders"},
            {"url": "https://pmkisan.gov.in/FAQ.aspx", "text": "Frequently Asked Questions"},
        ]

        ranked = rank_scheme_links(base_url, links, link_context)
        ranked_urls = [r["url"] for r in ranked]

        # Guidelines and About Scheme must be at the top
        self.assertIn("https://pmkisan.gov.in/Documents/Guidelines_PMKISAN.pdf", ranked_urls[:2])
        self.assertIn("https://pmkisan.gov.in/AboutScheme.aspx", ranked_urls[:2])

        # Login and Tenders must be excluded
        self.assertNotIn("https://pmkisan.gov.in/Login.aspx", ranked_urls)
        self.assertNotIn("https://pmkisan.gov.in/Tenders.aspx", ranked_urls)

    def test_pdf_extraction_page_segmentation(self):
        # Generate an in-memory PDF with pypdf
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.add_blank_page(width=72, height=72)
        pdf_stream = BytesIO()
        writer.write(pdf_stream)
        pdf_bytes = pdf_stream.getvalue()

        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/pdf"}
        mock_response.content = pdf_bytes

        extracted = GovCrawlerEngine._extract_response_content(
            mock_response,
            "https://pmkisan.gov.in/circular.pdf"
        )
        self.assertEqual(extracted["extractor"], "pdf")
        self.assertIn("circular.pdf", extracted["title"])

    def test_2hop_deep_crawl_integration(self):
        # Verify crawl_url follows top subpages when deep_crawl=True
        parent_url = "https://pmkisan.gov.in/index.html"
        parent_html = """
        <html>
        <head><title>PM-KISAN Apex Portal</title></head>
        <body>
            <h1>Welcome to PM-KISAN</h1>
            <a href="https://pmkisan.gov.in/guidelines.html">Scheme Guidelines and Eligibility</a>
            <a href="https://pmkisan.gov.in/login.html">Login</a>
        </body>
        </html>
        """
        subpage_html = """
        <html>
        <head><title>PM-KISAN Guidelines</title></head>
        <body>
            <h2>Eligibility Criteria</h2>
            <p>All landholding farmer families with cultivable land are eligible for income support of Rs. 6000 per year.</p>
        </body>
        </html>
        """

        def mock_get(url, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            resp.is_redirect = False
            resp.headers = {"content-type": "text/html; charset=utf-8"}
            if "guidelines" in url:
                resp.text = subpage_html
                resp.content = subpage_html.encode("utf-8")
            else:
                resp.text = parent_html
                resp.content = parent_html.encode("utf-8")
            return resp

        with patch("httpx.Client") as mock_client:
            instance = MagicMock()
            instance.get.side_effect = mock_get
            mock_client.return_value.__enter__.return_value = instance

            result = self.crawler.crawl_url(
                parent_url,
                force_refresh=True,
                deep_crawl=True,
                max_subpages=1
            )

            self.assertTrue(result["success"])
            self.assertEqual(len(result.get("deep_crawled_subpages", [])), 1)
            self.assertIn("DEEP CRAWL EVIDENCE", result["extracted_text"])
            self.assertIn("Rs. 6000 per year", result["extracted_text"])


if __name__ == "__main__":
    unittest.main()
