"""Unit tests for CentralAgentPlanner (backend/app/crawler/central_planner.py)."""

import unittest
from unittest.mock import patch, MagicMock
from app.crawler.central_planner import central_planner, CentralAgentPlanner


class CentralAgentPlannerTests(unittest.TestCase):

    def setUp(self):
        self.planner = CentralAgentPlanner()

    def test_guardrail_flooding_blocked_immediately(self):
        """Security guardrail intercepts spam at Step 0 before calling any tools."""
        res = self.planner.run("aaaaaaaaaaaaaaaaaaa")
        self.assertEqual(res["eligibility_status"], "flooding_spam")
        self.assertIn("Security Guardrail", res["agent_trace"][0]["title"])

    def test_guardrail_untrusted_url_blocked(self):
        """Security guardrail intercepts untrusted URLs at Step 0."""
        res = self.planner.run("Check this link: https://scam-site.com/fake")
        self.assertEqual(res["eligibility_status"], "security_blocked")
        self.assertFalse(res["crawler_metrics"]["security_whitelist_passed"])

    @patch("app.crawler.router_tool.RouterTool.execute")
    def test_out_of_domain_deflected(self, mock_router):
        """RouterTool detecting out-of-domain halts pipeline with polite refusal."""
        mock_router.return_value = {
            "is_out_of_domain": True,
            "out_of_domain_reason": "User is asking for Python programming code.",
            "polite_ood_refusal": "I can only help with Indian government welfare schemes.",
            "workflow": "OUT_OF_DOMAIN",
        }
        res = self.planner.run("Write a python program to calculate compound interest")
        self.assertEqual(res["eligibility_status"], "out_of_domain")
        self.assertIn("Indian government welfare", res["answer"])
        self.assertEqual(len(res["agent_trace"]), 1)

    @patch("app.crawler.router_tool.RouterTool.execute")
    def test_greeting_workflow(self, mock_router):
        """RouterTool detecting greeting returns official welcome."""
        mock_router.return_value = {
            "is_out_of_domain": False,
            "workflow": "GREETING",
            "target_schemes": [],
            "extracted_criteria": {},
        }
        res = self.planner.run("Hello, what can you do?")
        self.assertEqual(res["eligibility_status"], "greeting")
        self.assertIn("myScheme", res["answer"])

    @patch("app.crawler.generator_tool.ResponseGeneratorTool.execute")
    @patch("app.crawler.questionnaire_tool.QuestionnaireTool.execute")
    @patch("app.crawler.router_tool.RouterTool.execute")
    def test_full_4tool_pipeline_orchestration(self, mock_router, mock_q, mock_gen):
        """Central planner orchestrates Router -> Crawler -> Questionnaire -> Generator."""
        mock_router.return_value = {
            "is_out_of_domain": False,
            "workflow": "SCHEME_DISCOVERY",
            "target_schemes": ["PM Surya Ghar Muft Bijli Yojana"],
            "beneficiary": {"is_self": True, "target_description": "self"},
            "extracted_criteria": {"state": "Haryana"},
            "myscheme_search_terms": ["rooftop solar subsidy"],
        }
        mock_q.return_value = {
            "is_complete": False,
            "resolved_criteria": [{"criterion": "state", "value": "Haryana"}],
            "unresolved_criteria": [{"scheme": "PM Surya Ghar", "rule": "Roof ownership"}],
            "questions": [
                {
                    "id": "roof_rights",
                    "label": "Roof Rights",
                    "question": "Do you own an independent roof?",
                    "input_type": "radio",
                    "options": ["Yes", "No"],
                    "required": True,
                }
            ],
        }
        mock_gen.return_value = {
            "answer_markdown": "### PM Surya Ghar\nPlease answer the question below to confirm your eligibility.",
            "key_takeaways": ["PM Surya Ghar offers rooftop solar subsidy."],
        }

        res = self.planner.run("I live in Haryana and want rooftop solar subsidy")

        # Verify all tools were orchestrated in order
        mock_router.assert_called_once()
        mock_q.assert_called_once()
        mock_gen.assert_called_once()

        self.assertEqual(res["eligibility_status"], "needs_information")
        self.assertEqual(len(res["profiler_questions"]), 1)
        self.assertEqual(res["profiler_questions"][0]["id"], "roof_rights")
        self.assertIn("PM Surya Ghar", res["answer"])

        # Check trace contains all 4 tool steps
        step_types = [t.get("type") for t in res["agent_trace"]]
        self.assertIn("ROUTER", step_types)
        self.assertIn("CRAWLER", step_types)
        self.assertIn("QUESTIONNAIRE", step_types)
        self.assertIn("SYNTHESIZER", step_types)

    @patch("app.crawler.generator_tool.ResponseGeneratorTool.execute")
    @patch("app.crawler.router_tool.RouterTool.execute")
    def test_questionnaire_submission_focuses_on_full_eligibility_evaluation(self, mock_router, mock_gen):
        """When citizen submits questionnaire answers, focus transitions to full evaluation."""
        mock_router.return_value = {
            "is_out_of_domain": False,
            "workflow": "ELIGIBILITY_CHECK",
            "target_schemes": [],
            "beneficiary": {"is_self": True, "target_description": "self"},
            "extracted_criteria": {"occupation": "Farmer", "state": "Uttar Pradesh"},
            "myscheme_search_terms": ["pmkisan farmer"],
        }
        mock_gen.return_value = {
            "answer_markdown": "## Full Eligibility Evaluation\n✅ PM-KISAN: Eligible",
            "key_takeaways": ["You meet all criteria for PM-KISAN."],
        }

        history = [
            {"role": "user", "content": "I need financial support for farming in Uttar Pradesh"},
            {"role": "assistant", "content": "Here are schemes matching your request: Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)"}
        ]
        profile = {"occupation": "Farmer", "landholding": "2 acres", "state": "Uttar Pradesh"}

        res = self.planner.run(
            user_query="occupation: Farmer, landholding: 2 acres, state: Uttar Pradesh",
            user_profile=profile,
            conversation_history=history
        )

        # Generator must be called with evaluated_schemes and is_evaluation_turn=True
        mock_gen.assert_called_once()
        call_kwargs = mock_gen.call_args.kwargs
        self.assertTrue(call_kwargs.get("is_evaluation_turn"))
        self.assertIsNotNone(call_kwargs.get("evaluated_schemes"))

        # In response, eligibility matrix must be present and evaluated
        self.assertTrue(len(res["eligibility_matrix"]) > 0)
        top_scheme = res["eligibility_matrix"][0]
        self.assertIn(top_scheme.get("eligibility_status"), ("meets_captured_rules", "needs_information", "matches_found"))
        # No further questions should block the evaluation
        self.assertEqual(len(res["profiler_questions"]), 0)


if __name__ == "__main__":
    unittest.main()
