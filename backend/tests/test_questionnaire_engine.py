"""
Unit tests for Targeted Questionnaire Engine:
1. Redundancy Elimination: Criteria explicitly stated in query or chat history are omitted from questions.
2. Complete in One Go: Missing criteria across multiple schemes are asked together in one questionnaire.
3. UI Input Type:
   - Options > 4 are marked with input_type='dropdown'.
   - Options <= 4 are marked with input_type='radio'.
4. Deduplication: Same field across 2 different schemes generates only 1 question.
"""

import unittest
from app.crawler.questionnaire_engine import questionnaire_engine


class TargetedQuestionnaireEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = questionnaire_engine

    def test_extract_known_profile_from_chat_context(self):
        query = "I am a female farmer looking for government schemes"
        history = [
            {"role": "user", "content": "Hello, I am 32 years old from Uttar Pradesh"},
            {"role": "assistant", "content": "I can help with schemes in UP."},
            {"role": "user", "content": "My annual family income is 1.5 lakh"},
        ]
        explicit_profile = {"social_category": "OBC"}

        known = self.engine.extract_known_profile_from_context(
            user_query=query,
            conversation_history=history,
            user_profile=explicit_profile,
        )

        self.assertEqual(known.get("state"), "Uttar Pradesh")
        self.assertEqual(known.get("gender"), "Woman")
        self.assertEqual(known.get("age"), 32)
        self.assertEqual(known.get("occupation"), "Farmer")
        self.assertEqual(known.get("social_category"), "OBC")
        self.assertTrue("1.5" in str(known.get("annual_family_income")) or known.get("annual_family_income") == 150000.0)

    def test_assistant_recommendations_are_not_treated_as_user_profile(self):
        known = self.engine.extract_known_profile_from_context(
            user_query="I need help buying farming equipment",
            conversation_history=[
                {
                    "role": "assistant",
                    "content": "The applicant is a farmer. Consider Education Loan Scheme.",
                },
            ],
            user_profile={},
        )

        self.assertNotIn("occupation", known)

    def test_requesting_schemes_does_not_assume_user_is_the_beneficiary(self):
        known = self.engine.extract_known_profile_from_context(
            user_query="Find student scholarships for my daughter",
            conversation_history=[],
            user_profile={},
        )

        self.assertNotIn("occupation", known)

    def test_questionnaire_prunes_already_known_facts(self):
        # Schemes requiring age, state, and income
        schemes = [
            {
                "scheme_name": "Scheme A",
                "eligibility_rules": [
                    {"field": "age", "operator": "lte", "value": 40, "rule_text": "Age <= 40"},
                    {"field": "state", "operator": "eq", "value": "Uttar Pradesh", "rule_text": "UP resident"},
                    {"field": "social_category", "operator": "in", "value": ["SC", "ST", "OBC"], "rule_text": "Reserved category"},
                ]
            }
        ]

        # Context where state and age are already known
        history = [
            {"role": "user", "content": "I am 25 years old from Uttar Pradesh"}
        ]
        
        questions, known = self.engine.build_targeted_questionnaire(
            schemes=schemes,
            user_query="Which schemes can I get?",
            conversation_history=history,
            user_profile={},
            state_candidates_exist=False,
            state_already_known="Uttar Pradesh"
        )

        # Neither state nor age should be in questions
        question_ids = [q["id"] for q in questions]
        self.assertNotIn("state", question_ids)
        self.assertNotIn("age", question_ids)

        # social_category was NOT provided, so it must be asked
        self.assertIn("social_category", question_ids)

    def test_dropdown_assigned_when_options_greater_than_four(self):
        # State question has 36 options -> must be dropdown
        questions, _ = self.engine.build_targeted_questionnaire(
            schemes=[],
            user_query="Looking for central schemes",
            conversation_history=[],
            user_profile={},
            state_candidates_exist=True,
            state_already_known=None,
        )
        state_q = next((q for q in questions if q["id"] == "state"), None)
        self.assertIsNotNone(state_q)
        self.assertEqual(state_q["input_type"], "dropdown")
        self.assertGreater(len(state_q["options"]), 4)

    def test_radio_assigned_when_options_less_than_or_equal_to_four(self):
        # Income threshold <= 2 lakh gives: Below, Above, Not sure (3 options) -> radio
        schemes = [
            {
                "scheme_name": "Scheme B",
                "eligibility_rules": [
                    {"field": "annual_family_income", "operator": "lte", "value": 200000, "rule_text": "Income <= 2 lakh"}
                ]
            }
        ]
        questions, _ = self.engine.build_targeted_questionnaire(
            schemes=schemes,
            user_query="Find schemes",
            conversation_history=[],
            user_profile={},
        )
        income_q = next((q for q in questions if q["id"] == "annual_family_income"), None)
        self.assertIsNotNone(income_q)
        self.assertEqual(income_q["input_type"], "radio")
        self.assertLessEqual(len(income_q["options"]), 4)

    def test_no_redundant_duplicate_questions_across_schemes(self):
        # 2 schemes both asking for landholding
        schemes = [
            {
                "scheme_name": "Scheme 1",
                "eligibility_rules": [
                    {"field": "landholding", "operator": "lte", "value": 2.0, "rule_text": "Land <= 2 ha"}
                ]
            },
            {
                "scheme_name": "Scheme 2",
                "eligibility_rules": [
                    {"field": "landholding", "operator": "lte", "value": 5.0, "rule_text": "Land <= 5 ha"}
                ]
            }
        ]
        questions, _ = self.engine.build_targeted_questionnaire(
            schemes=schemes,
            user_query="Kisan schemes",
            conversation_history=[],
            user_profile={},
        )
        land_questions = [q for q in questions if q["id"] == "landholding"]
        # Exactly 1 question generated in one go
        self.assertEqual(len(land_questions), 1)

    def test_community_question_uses_clear_non_response_options(self):
        schemes = [
            {
                "scheme_name": "Minority Support Scheme",
                "eligibility_rules": [
                    {
                        "field": "social_category",
                        "operator": "in",
                        "value": ["Muslim", "Christian", "Sikh", "Buddhist", "Parsi", "Jain"],
                        "rule_text": "Applicant must belong to one of the six notified minority communities.",
                    }
                ],
            }
        ]

        questions, _ = self.engine.build_targeted_questionnaire(
            schemes=schemes,
            user_query="Find support",
            conversation_history=[],
            user_profile={},
        )

        community_question = questions[0]
        self.assertEqual(community_question["label"], "Community")
        self.assertIn(
            "which of these six notified minority communities",
            community_question["question"].casefold(),
        )
        self.assertEqual(
            community_question["options"][-2:],
            ["None of these", "Not sure"],
        )
        self.assertFalse(
            any("prefer not to say" in option.casefold() for option in community_question["options"])
        )

    def test_numeric_question_covers_different_scheme_thresholds(self):
        schemes = [
            {
                "scheme_name": "Scheme A",
                "eligibility_rules": [
                    {
                        "field": "annual_family_income",
                        "operator": "lte",
                        "value": 200000,
                        "rule_text": "Income must not exceed ₹2 lakh.",
                    }
                ],
            },
            {
                "scheme_name": "Scheme B",
                "eligibility_rules": [
                    {
                        "field": "annual_family_income",
                        "operator": "lte",
                        "value": 500000,
                        "rule_text": "Income must not exceed ₹5 lakh.",
                    }
                ],
            },
        ]

        questions, _ = self.engine.build_targeted_questionnaire(
            schemes=schemes,
            user_query="Find schemes",
            conversation_history=[],
            user_profile={},
        )

        self.assertEqual(questions[0]["id"], "annual_family_income")
        self.assertEqual(questions[0]["input_type"], "number")
        self.assertEqual(questions[0]["options"], [])

    def test_disqualified_scheme_does_not_generate_questions(self):
        # A scheme requiring minority community and landholding
        schemes = [
            {
                "scheme_name": "Minority Farmer Scheme",
                "eligibility_rules": [
                    {"field": "social_category", "operator": "in", "value": ["Minority", "Muslim", "Sikh"], "rule_text": "Must be minority"},
                    {"field": "farmer_status", "operator": "eq", "value": "Yes", "rule_text": "Must be farmer"},
                    {"field": "landholding", "operator": "lte", "value": 2.0, "rule_text": "Small landholder"},
                ]
            },
            {
                "scheme_name": "General Education Loan Scheme",
                "eligibility_rules": [
                    {"field": "course_type", "operator": "eq", "value": "Engineering / B.Tech", "rule_text": "Course must be B.Tech"},
                ]
            }
        ]

        # User is General category (not in Minority list)
        user_profile = {"social_category": "General"}

        questions, _ = self.engine.build_targeted_questionnaire(
            schemes=schemes,
            user_query="I want education financing for a technical course",
            conversation_history=[],
            user_profile=user_profile,
        )

        question_ids = [q["id"] for q in questions]
        # Since Minority Farmer Scheme is already disqualified by social_category="General",
        # farmer_status and landholding MUST NOT be asked!
        self.assertNotIn("farmer_status", question_ids)
        self.assertNotIn("landholding", question_ids)
        # Course type for the viable scheme is missing and SHOULD be asked
        self.assertIn("course_type", question_ids)


if __name__ == "__main__":
    unittest.main()
