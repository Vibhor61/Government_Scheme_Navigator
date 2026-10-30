import unittest
from unittest.mock import patch
from app.crawler.policy_interaction_engine import (
    PolicyInteractionEngine,
    _classify_scheme_domain,
)


class PolicyInteractionEngineTests(unittest.TestCase):
    def test_classify_all_sectors(self):
        self.assertEqual(_classify_scheme_domain({"scheme_name": "Ayushman Bharat PM-JAY"}), "health")
        self.assertEqual(_classify_scheme_domain({"scheme_name": "Post-Matric Scholarship"}), "education")
        self.assertEqual(_classify_scheme_domain({"scheme_name": "PM Mudra Yojana"}), "msme_business")
        self.assertEqual(_classify_scheme_domain({"scheme_name": "Pradhan Mantri Matru Vandana Yojana"}), "women_child")
        self.assertEqual(_classify_scheme_domain({"scheme_name": "Rashtriya Vayoshri Yojana for Elderly"}), "senior_disability")
        self.assertEqual(_classify_scheme_domain({"scheme_name": "PM-KISAN"}), "agriculture")
        self.assertEqual(_classify_scheme_domain({"scheme_name": "PMAY Gramin"}), "housing")

    def test_deterministic_fallback_health(self):
        schemes = [
            {
                "scheme_name": "Ayushman Bharat PM-JAY",
                "slug": "ab-pmjay",
                "category": "Health",
                "benefit": "Free hospitalization up to ₹5 lakh.",
            },
            {
                "scheme_name": "PM Bhartiya Janaushadhi Pariyojana",
                "slug": "pmbjp",
                "category": "Health",
                "benefit": "Quality generic medicines at 50% to 90% lesser prices.",
            },
        ]
        # Force deterministic fallback by setting llm_result to None
        with patch.object(PolicyInteractionEngine, "_evaluate_with_llm", return_value=None):
            res = PolicyInteractionEngine.evaluate(schemes=schemes, user_query="health schemes for treatment")
            stack = res.get("welfare_stack")
            self.assertIsNotNone(stack)
            self.assertEqual(stack.get("bundle_type"), "HEALTH_CONVERGENCE")
            self.assertGreaterEqual(len(stack.get("schemes", [])), 2)
            self.assertGreaterEqual(len(stack.get("application_sequence", [])), 2)

    def test_deterministic_fallback_scholarship_conflict(self):
        schemes = [
            {
                "scheme_name": "Central Sector Scheme of Scholarship",
                "slug": "csss",
                "category": "Education",
                "level": "Central",
            },
            {
                "scheme_name": "State Post-Matric Scholarship",
                "slug": "state-pms",
                "category": "Education",
                "level": "State",
            },
        ]
        with patch.object(PolicyInteractionEngine, "_evaluate_with_llm", return_value=None):
            res = PolicyInteractionEngine.evaluate(schemes=schemes, user_query="scholarships for engineering")
            conflicts = res.get("cross_scheme_conflicts", [])
            self.assertGreaterEqual(len(conflicts), 1)
            self.assertEqual(conflicts[0].get("alert_type"), "CROSS_SCHEME_MUTUAL_EXCLUSION")
            self.assertIsNotNone(res.get("conflict_alert"))

    def test_deterministic_fallback_msme_stacking(self):
        schemes = [
            {
                "scheme_name": "PM SVANidhi",
                "slug": "pm-svanidhi",
                "category": "Livelihood",
                "benefit": "Working capital loan up to ₹10,000.",
            },
            {
                "scheme_name": "PM Mudra Yojana",
                "slug": "mudra",
                "category": "MSME Loan",
                "benefit": "Collateral-free loan up to ₹10 Lakhs.",
            },
        ]
        with patch.object(PolicyInteractionEngine, "_evaluate_with_llm", return_value=None):
            res = PolicyInteractionEngine.evaluate(schemes=schemes, user_query="small business loan")
            stack = res.get("welfare_stack")
            self.assertIsNotNone(stack)
            self.assertEqual(stack.get("bundle_type"), "MSME_LIVELIHOOD_CONVERGENCE")

    def test_dynamic_llm_policy_integration(self):
        schemes = [
            {
                "scheme_name": "Ayushman Bharat PM-JAY",
                "slug": "ab-pmjay",
                "category": "Health",
                "benefit": "Hospitalization up to ₹5 lakh.",
            },
            {
                "scheme_name": "Jan Aushadhi Scheme",
                "slug": "pmbjp",
                "category": "Health",
                "benefit": "Discounted generic medicines.",
            },
        ]
        mock_llm_response = {
            "has_conflict": False,
            "conflict": None,
            "welfare_stack": {
                "bundle_title": "🏥 Universal Health & Medicine Stack",
                "bundle_type": "HEALTH_CONVERGENCE",
                "badge": "Policy Convergence Approved",
                "description": "Hospitalization and medicines combined.",
                "total_financial_impact": "₹5 Lakh Cover + Low Cost Meds",
                "schemes": [
                    {"name": "Ayushman Bharat", "role": "Hospital Cover"},
                    {"name": "Jan Aushadhi", "role": "Medicine Subsidy"}
                ],
                "application_sequence": [
                    {"step": 1, "title": "Get Golden Card", "instruction": "Visit portal"}
                ]
            }
        }
        with patch.object(PolicyInteractionEngine, "_evaluate_with_llm", return_value=mock_llm_response):
            res = PolicyInteractionEngine.evaluate(schemes=schemes, user_query="health cover")
            self.assertIsNotNone(res.get("welfare_stack"))
            self.assertEqual(res["welfare_stack"]["bundle_title"], "🏥 Universal Health & Medicine Stack")


if __name__ == "__main__":
    unittest.main()
