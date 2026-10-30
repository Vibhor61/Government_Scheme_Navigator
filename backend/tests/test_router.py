"""Unit tests for Stage 2 LLM Router (backend/app/crawler/router.py)."""

import unittest
from unittest.mock import patch, MagicMock
from app.crawler.router import scheme_router, SchemeRouter


class SchemeRouterTests(unittest.TestCase):

    def setUp(self):
        self.router = SchemeRouter()

    def test_fallback_routing_greeting(self):
        """Fallback router properly classifies greetings."""
        res = self.router._fallback_route("Namaste, what can you do?")
        self.assertEqual(res["workflow"], "GREETING")
        self.assertFalse(res["is_out_of_domain"])

    def test_fallback_routing_out_of_domain(self):
        """Fallback router detects obvious out-of-domain queries."""
        res = self.router._fallback_route("Write a python script for binary search")
        self.assertTrue(res["is_out_of_domain"])

    def test_fallback_routing_beneficiary_decoupling(self):
        """Fallback router identifies when a query is on behalf of family members."""
        res = self.router._fallback_route("Need pension scheme for my mother aged 65")
        self.assertFalse(res["beneficiary"]["is_self"])
        self.assertFalse(res["is_out_of_domain"])

    def test_fallback_routing_criteria_extraction(self):
        """Fallback router extracts explicit profile facts like state and age."""
        res = self.router._fallback_route("I am 22 years old living in Haryana looking for education loan")
        self.assertFalse(res["is_out_of_domain"])
        criteria = res.get("extracted_criteria", {})
        self.assertEqual(criteria.get("state"), "Haryana")
        self.assertEqual(criteria.get("age"), 22)

    @patch("app.crawler.llm_service.llm_service._call_groq_json")
    def test_llm_routing_happy_path(self, mock_llm):
        """Router returns structured JSON from LLM call."""
        mock_llm.return_value = {
            "is_out_of_domain": False,
            "out_of_domain_reason": None,
            "polite_ood_refusal": None,
            "workflow": "SCHEME_LOOKUP",
            "target_schemes": ["PM Surya Ghar Muft Bijli Yojana"],
            "beneficiary": {
                "is_self": True,
                "applicant_role": "homeowner",
                "target_description": "self",
            },
            "extracted_criteria": {
                "state": "Uttar Pradesh",
                "age": None,
                "gender": None,
                "social_category": None,
                "annual_family_income": None,
                "occupation": None,
                "landholding": None,
                "disability_status": None,
                "marital_status": None,
            },
            "myscheme_search_terms": ["rooftop solar subsidy", "surya ghar"],
        }

        res = self.router.route("Tell me about PM Surya Ghar in Uttar Pradesh")
        self.assertEqual(res["workflow"], "SCHEME_LOOKUP")
        self.assertEqual(res["target_schemes"], ["PM Surya Ghar Muft Bijli Yojana"])
        self.assertEqual(res["extracted_criteria"]["state"], "Uttar Pradesh")
        self.assertFalse(res["is_out_of_domain"])

    @patch("app.crawler.llm_service.llm_service._call_groq_json")
    def test_llm_routing_open_ended_criteria(self, mock_llm):
        """Router supports arbitrary, open-ended eligibility criteria without field limits."""
        mock_llm.return_value = {
            "is_out_of_domain": False,
            "out_of_domain_reason": None,
            "polite_ood_refusal": None,
            "workflow": "SCHEME_DISCOVERY",
            "target_schemes": [],
            "beneficiary": {
                "is_self": True,
                "applicant_role": "farmer",
                "target_description": "self",
            },
            "extracted_criteria": {
                "land_type": "irrigated",
                "landholding_acres": 2.5,
                "irrigation_source": "diesel pump",
                "bpl_card": True,
                "marks_percentage": "82%",
                "electricity_meter_load_kw": 3,
                "roof_rights": "independent terrace ownership"
            },
            "myscheme_search_terms": ["solar pump subsidy", "pm kusum"],
        }

        res = self.router.route("I have 2.5 acres irrigated land with diesel pump and BPL card")
        criteria = res.get("extracted_criteria", {})
        self.assertEqual(criteria.get("land_type"), "irrigated")
        self.assertEqual(criteria.get("roof_rights"), "independent terrace ownership")
        self.assertTrue(criteria.get("bpl_card"))
        self.assertEqual(criteria.get("electricity_meter_load_kw"), 3)


if __name__ == "__main__":
    unittest.main()
