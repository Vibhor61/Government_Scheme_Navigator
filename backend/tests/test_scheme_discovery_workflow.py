import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from app.crawler.agent_planner import AutonomousAgentPlanner
from app.crawler.crawler_engine import _result_extracted_text
from app.crawler.scheme_discovery_workflow import (
    MYSCHEME_PORTAL,
    _build_search_terms,
    _search_hits,
    _select_hits,
    run_scheme_discovery_workflow,
)
from app.crawler.deterministic_tools import classify_query

ARTISAN_RULE_QUOTE = (
    "The applicant must be a registered artisan engaged in a traditional trade."
)


def _hit(name, slug, level, states):
    return {
        "id": slug,
        "fields": {
            "schemeName": name,
            "briefDescription": f"Support for {name}.",
            "level": level,
            "beneficiaryState": states,
            "slug": slug,
        },
    }


def _search_page(url):
    query = parse_qs(urlparse(url).query)
    filters = json.loads(query["q"][0])
    level = next(item["value"] for item in filters if item["identifier"] == "level")
    if level == "Central":
        hits = [_hit("National Artisan Support", "national-artisan", "Central", ["All"])]
    else:
        hits = [_hit("Haryana Artisan Grant", "haryana-artisan", "State", ["Haryana"])]
    return {
        "data": {
            "hits": {
                "items": hits,
                "total": len(hits),
            }
        }
    }


def _detail_page(slug):
    name = "Haryana Artisan Grant" if slug == "haryana-artisan" else "National Artisan Support"
    return {
        "data": {
            "en": {
                "schemeName": name,
                "briefDescription": f"Support for {name}.",
                "eligibilityCriteria": {"description": ARTISAN_RULE_QUOTE},
                "benefits": [],
                "applicationProcess": [],
            }
        }
    }


class SchemeDiscoveryWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.crawl_urls = []

    def test_farming_equipment_query_filters_unrelated_scheme_hits(self):
        irrigation = _hit(
            "Large Cardamom Irrigation Land Development",
            "cardamom-irrigation",
            "Central",
            ["All"],
        )
        machinery = _hit(
            "Farm Mechanization Support",
            "farm-mechanization",
            "Central",
            ["All"],
        )
        education = _hit(
            "Education Loan Scheme",
            "education-loan",
            "Central",
            ["All"],
        )
        page = {
            "success": True,
            "extracted_text": json.dumps({
                "data": {"hits": {"items": [irrigation, education, machinery]}}
            }),
        }

        self.assertEqual(
            classify_query("I want support for my farming equipments"),
            "agriculture",
        )
        self.assertEqual(
            _build_search_terms(
                "I want support for my farming equipments",
                ["farm machinery agricultural equipment subsidy"],
            ),
            [
                "I want support for my farming equipments",
                "farm machinery agricultural equipment subsidy",
            ],
        )
        selected = _select_hits([page], state=None, search_terms=[
            "I want support for my farming equipments",
            "farm machinery agricultural equipment subsidy",
        ])
        self.assertEqual(
            [hit["fields"]["schemeName"] for hit in selected],
            ["Farm Mechanization Support"],
        )

    def test_relevance_ranking_filters_noise_for_non_agriculture_queries(self):
        scholarships = _hit("Student Scholarship Support", "scholarship", "Central", ["All"])
        farm_support = _hit("Farm Mechanization Support", "farm-support", "Central", ["All"])
        page = {
            "success": True,
            "extracted_text": json.dumps({
                "data": {"hits": {"items": [farm_support, scholarships]}}
            }),
        }

        selected = _select_hits(
            [page],
            state=None,
            search_terms=["financial help for students", "student scholarship"],
        )

        self.assertEqual(
            [hit["fields"]["schemeName"] for hit in selected],
            ["Student Scholarship Support"],
        )

    def test_complete_json_search_response_is_preserved_and_parsed(self):
        hit = _hit("National Artisan Support", "national-artisan", "Central", ["All"])
        payload = {
            "data": {
                "facets": [{"label": "x" * 13_000}],
                "hits": {"items": [hit], "total": 1},
            }
        }
        original_text = json.dumps(payload)

        stored_text = _result_extracted_text(original_text, "json")
        page = {"success": True, "extracted_text": stored_text}

        self.assertGreater(len(original_text), 12_000)
        self.assertEqual(stored_text, original_text)
        self.assertEqual(_search_hits(page), [hit])

    def test_oversized_json_response_is_not_silently_truncated(self):
        with self.assertRaisesRegex(ValueError, "extraction limit"):
            _result_extracted_text("{" + "x" * 250_000, "json")

    def test_html_response_remains_bounded(self):
        self.assertEqual(
            len(_result_extracted_text("x" * 12_001, "html")),
            12_000,
        )

    def _crawl(self, url, force_refresh=False):
        self.crawl_urls.append(url)
        parsed = urlparse(url)
        self.assertIn(parsed.hostname, {"myscheme.gov.in", "www.myscheme.gov.in"})
        if parsed.path.endswith("/search/schemes"):
            payload = _search_page(url)
        else:
            slug = parse_qs(parsed.query).get("slug", [""])[0]
            payload = _detail_page(slug)
        text = json.dumps(payload, ensure_ascii=False)
        return {
            "success": True,
            "url": url,
            "domain": parsed.hostname,
            "title": "myScheme",
            "content_length": len(text),
            "extracted_text": text,
            "security_status": "REGISTERED_OFFICIAL_PORTAL",
            "extractor": "json",
            "cache_hit": False,
            "latency_ms": 1,
        }

    @staticmethod
    def _extract(_page_text, source_url, _metadata=None):
        slug = parse_qs(urlparse(source_url).query).get("slug", [""])[0]
        name = "Haryana Artisan Grant" if slug == "haryana-artisan" else "National Artisan Support"
        return {
            "scheme_name": name,
            "source_title": name,
            "jurisdiction": "Central" if slug == "national-artisan" else "Haryana",
            "benefit": "",
            "benefit_evidence_quote": "",
            "eligibility_rules": [
                {
                    "field": "occupation",
                    "operator": "eq",
                    "value": "artisan",
                    "rule_text": "The applicant must be a registered artisan.",
                    "evidence_quote": ARTISAN_RULE_QUOTE,
                }
            ],
            "application_process": "",
            "application_evidence_quote": "",
        }

    @patch("app.crawler.scheme_discovery_workflow.gov_crawler.crawl_url")
    @patch("app.crawler.scheme_discovery_workflow.llm_service.extract_scheme_rule_record")
    @patch("app.crawler.scheme_discovery_workflow.llm_service.plan_registered_search")
    def test_state_and_central_rules_are_searched_and_compared_for_any_topic(
        self, plan, extract, crawl
    ):
        plan.return_value = {
            "selected_domains": ["www.myscheme.gov.in"],
            "search_terms": ["artisan support"],
        }
        extract.side_effect = self._extract
        crawl.side_effect = self._crawl

        result = run_scheme_discovery_workflow(
            "I am an artisan in Haryana",
            user_profile={
                "State / UT": "Haryana",
                "Occupation": "Artisan / craft worker",
            },
        )

        self.assertEqual(plan.call_args.args[2], [MYSCHEME_PORTAL])
        self.assertEqual(result["eligibility_status"], "matches_found")
        self.assertEqual(
            {scheme["scheme_name"] for scheme in result["other_schemes"]},
            {"National Artisan Support", "Haryana Artisan Grant"},
        )
        self.assertEqual(len(result["profiler_questions"]), 0)
        self.assertTrue(self.crawl_urls)
        self.assertTrue(all(urlparse(url).hostname == "www.myscheme.gov.in" for url in self.crawl_urls))

    @patch("app.crawler.scheme_discovery_workflow.gov_crawler.crawl_url")
    @patch("app.crawler.scheme_discovery_workflow.llm_service.extract_scheme_rule_record")
    @patch("app.crawler.scheme_discovery_workflow.llm_service.plan_registered_search")
    def test_missing_state_withholds_state_results_and_asks_once(
        self, plan, extract, crawl
    ):
        plan.return_value = {"selected_domains": [], "search_terms": []}
        extract.side_effect = self._extract
        crawl.side_effect = self._crawl

        result = run_scheme_discovery_workflow("Find support for artisans")

        self.assertEqual(result["eligibility_status"], "needs_location")
        self.assertEqual(
            [question["id"] for question in result["profiler_questions"]],
            ["state", "occupation"],
        )
        self.assertEqual(
            [scheme["scheme_name"] for scheme in result["other_schemes"]],
            ["National Artisan Support"],
        )
        self.assertNotIn("Haryana Artisan Grant", result["answer"])

    @patch("app.crawler.agent_planner.run_scheme_discovery_workflow")
    def test_planner_uses_shared_workflow_for_non_education_queries(self, workflow):
        workflow.return_value = {"query": "street vendor loan"}

        result = AutonomousAgentPlanner().run("street vendor loan")

        self.assertEqual(result, {"query": "street vendor loan"})
        workflow.assert_called_once()


if __name__ == "__main__":
    unittest.main()
