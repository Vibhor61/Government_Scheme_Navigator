import unittest

from app.crawler.deterministic_tools import select_official_portals
from app.crawler.portal_catalog import extract_state_from_query
from app.crawler.whitelist import (
    get_whitelist_catalog,
    get_whitelist_summary_stats,
    is_whitelisted_domain,
)


class RepositoryWhitelistTests(unittest.TestCase):
    def test_allows_only_myscheme_exact_host_and_www_variant(self):
        for url in (
            "https://myscheme.gov.in",
            "https://www.myscheme.gov.in/api/apisetu/search/schemes?lang=en",
        ):
            with self.subTest(url=url):
                self.assertTrue(is_whitelisted_domain(url, strict_repo_mode=True)[0])

        for url in (
            "https://api.myscheme.gov.in",
            "https://education.gov.in",
            "https://vidyalakshmi.co.in",
            "https://myscheme.gov.in.attacker.example",
            "https://myscheme.gov.in.evil",
            "https://user@myscheme.gov.in",
            "https://myscheme.gov.in:8443",
        ):
            with self.subTest(url=url):
                self.assertFalse(is_whitelisted_domain(url, strict_repo_mode=True)[0])

    def test_allows_genuine_government_domains(self):
        for url in (
            "https://myscheme.gov.in",
            "https://pmkisan.gov.in",
            "https://scholarships.gov.in",
            "https://edistrict.up.gov.in",
            "https://wcd.nic.in",
        ):
            with self.subTest(url=url):
                self.assertTrue(is_whitelisted_domain(url)[0])

        for url in (
            "https://vidyalakshmi.co.in",
            "https://myscheme.gov.in.attacker.example",
            "https://myscheme.gov.in.evil",
            "https://user@myscheme.gov.in",
            "https://myscheme.gov.in:8443",
            "https://fake-gov.in",
        ):
            with self.subTest(url=url):
                self.assertFalse(is_whitelisted_domain(url)[0])

    def test_active_whitelist_catalog_and_stats(self):
        catalog = get_whitelist_catalog()
        stats = get_whitelist_summary_stats()

        self.assertGreaterEqual(len(catalog), 1)
        self.assertTrue(any(item["domain"] == "myscheme.gov.in" for item in catalog))
        self.assertGreaterEqual(stats["total_portals"], 1)
        self.assertGreaterEqual(stats["central_portals"], 1)
        self.assertGreaterEqual(len(get_whitelist_catalog(jurisdiction_filter="Central")), 1)

    def test_state_extraction_handles_full_names_without_matching_common_words(self):
        self.assertEqual(
            extract_state_from_query("I need schemes in Andhra Pradesh"),
            "Andhra Pradesh",
        )
        self.assertEqual(
            extract_state_from_query("I am in UP and need a scholarship"),
            "Uttar Pradesh",
        )
        self.assertIsNone(
            extract_state_from_query("I want to set up a small business"),
        )

    def test_shared_selector_never_falls_back_to_unrelated_state_portal(self):
        selection = select_official_portals(
            "I need B.Tech education loan support",
            "Haryana",
        )

        self.assertEqual(selection["state"], [])
        self.assertTrue(any(portal["domain"] == "myscheme.gov.in" for portal in selection["central"]))


if __name__ == "__main__":
    unittest.main()
