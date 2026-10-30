import unittest

from app.crawler.scheme_rules import (
    evaluate_schemes,
    profile_questions,
    validate_rule_record,
)


SOURCE_URL = "https://www.myscheme.gov.in/api/apisetu/schemes?slug=csis&lang=en"
PAGE_TEXT = (
    "Central Sector Interest Subsidy Scheme: The family income should not exceed "
    "₹4.5 lakh per annum for eligible students."
)
RULE_RECORD = {
    "scheme_name": "Central Sector Interest Subsidy Scheme",
    "jurisdiction": "Central",
    "benefit": "",
    "eligibility_rules": [
        {
            "field": "annual_family_income",
            "operator": "lte",
            "value": 450000,
            "rule_text": "Family income must not exceed ₹4.5 lakh.",
            "evidence_quote": "The family income should not exceed ₹4.5 lakh per annum",
        }
    ],
}


class SchemeRuleEvidenceTests(unittest.TestCase):
    def test_accepts_supported_rule_with_exact_source_quote(self):
        record = validate_rule_record(RULE_RECORD, SOURCE_URL, PAGE_TEXT)
        self.assertIsNotNone(record)
        self.assertEqual(len(record["eligibility_rules"]), 1)
        self.assertEqual(record["eligibility_rules"][0]["source_url"], SOURCE_URL)

    def test_rejects_quote_not_present_on_source_page(self):
        altered = {
            **RULE_RECORD,
            "eligibility_rules": [
                {
                    **RULE_RECORD["eligibility_rules"][0],
                    "evidence_quote": "Students may receive any amount of loan subsidy",
                }
            ],
        }
        self.assertIsNone(validate_rule_record(altered, SOURCE_URL, PAGE_TEXT))

    def test_rejects_model_threshold_that_disagrees_with_quote(self):
        altered = {
            **RULE_RECORD,
            "eligibility_rules": [
                {
                    **RULE_RECORD["eligibility_rules"][0],
                    "value": 800000,
                }
            ],
        }
        self.assertIsNone(validate_rule_record(altered, SOURCE_URL, PAGE_TEXT))

    def test_rejects_rule_field_not_supported_by_quote_context(self):
        altered = {
            **RULE_RECORD,
            "eligibility_rules": [
                {
                    **RULE_RECORD["eligibility_rules"][0],
                    "field": "loan_amount",
                }
            ],
        }
        self.assertIsNone(validate_rule_record(altered, SOURCE_URL, PAGE_TEXT))

    def test_rejects_unregistered_source_host(self):
        self.assertIsNone(
            validate_rule_record(
                RULE_RECORD,
                "https://example.com/fake",
                PAGE_TEXT,
            )
        )

    def test_numeric_income_threshold_and_questionnaire(self):
        scheme = validate_rule_record(RULE_RECORD, SOURCE_URL, PAGE_TEXT)
        questions = profile_questions(scheme["eligibility_rules"], {})
        self.assertEqual([question["id"] for question in questions], ["annual_family_income"])
        self.assertIn("At or below ₹4.5 lakh", questions[0]["options"])

        eligible = evaluate_schemes(
            [scheme],
            {"Family Annual Income": "At or below ₹4.5 lakh"},
        )[0]
        ineligible = evaluate_schemes(
            [scheme],
            {"Family Annual Income": "Above ₹4.5 lakh"},
        )[0]
        unresolved = evaluate_schemes(
            [scheme],
            {"Family Annual Income": "Not sure"},
        )[0]
        self.assertEqual(eligible["eligibility_status"], "meets_captured_rules")
        self.assertEqual(eligible["eligibility_matrix"][0]["status"], "MET")
        self.assertEqual(ineligible["eligibility_status"], "ineligible")
        self.assertEqual(unresolved["eligibility_status"], "needs_information")

    def test_skipped_sensitive_answer_remains_unresolved(self):
        scheme = {
            "scheme_name": "Category Support Scheme",
            "sources": [{"url": SOURCE_URL, "title": "Category Support Scheme"}],
            "eligibility_rules": [
                {
                    "field": "social_category",
                    "operator": "in",
                    "value": ["SC", "ST"],
                    "rule_text": "Applicant must belong to SC or ST.",
                    "evidence_quote": "The applicant category must be SC or ST.",
                    "source_url": SOURCE_URL,
                }
            ],
        }
        result = evaluate_schemes([scheme], {"social_category": "Skipped"})[0]

        self.assertEqual(result["eligibility_status"], "needs_information")
        self.assertEqual(result["eligibility_matrix"][0]["status"], "UNKNOWN")

    def test_conflicting_source_thresholds_remain_unknown(self):
        first = validate_rule_record(RULE_RECORD, SOURCE_URL, PAGE_TEXT)
        second_url = "https://www.myscheme.gov.in/api/apisetu/schemes?slug=older-csis&lang=en"
        second_text = "The family income shall not exceed ₹8 lakh per annum."
        second_raw = {
            **RULE_RECORD,
            "eligibility_rules": [
                {
                    **RULE_RECORD["eligibility_rules"][0],
                    "value": 800000,
                    "evidence_quote": "The family income shall not exceed ₹8 lakh per annum",
                }
            ],
        }
        second = validate_rule_record(second_raw, second_url, second_text)
        combined = {
            **first,
            "eligibility_rules": [
                first["eligibility_rules"][0],
                second["eligibility_rules"][0],
            ],
        }
        result = evaluate_schemes(
            [combined],
            {"annual_family_income": "₹3 lakh"},
        )[0]
        self.assertEqual(result["eligibility_status"], "needs_information")
        self.assertTrue(all(item["conflict"] for item in result["eligibility_matrix"]))
        self.assertTrue(all(item["status"] == "UNKNOWN" for item in result["eligibility_matrix"]))

    def test_strict_and_inclusive_thresholds_differ_at_boundary(self):
        scheme = validate_rule_record(RULE_RECORD, SOURCE_URL, PAGE_TEXT)
        inclusive = evaluate_schemes(
            [scheme],
            {"Family Annual Income": "₹4.5 lakh"},
        )[0]
        strict_record = {
            **RULE_RECORD,
            "eligibility_rules": [
                {
                    **RULE_RECORD["eligibility_rules"][0],
                    "operator": "lt",
                    "rule_text": "Family income must be less than ₹4.5 lakh.",
                    "evidence_quote": "The family income is less than ₹4.5 lakh per annum",
                }
            ],
        }
        strict_text = "The family income is less than ₹4.5 lakh per annum."
        strict_scheme = validate_rule_record(strict_record, SOURCE_URL, strict_text)
        strict = evaluate_schemes(
            [strict_scheme],
            {"Family Annual Income": "₹4.5 lakh"},
        )[0]
        self.assertEqual(inclusive["eligibility_status"], "meets_captured_rules")
        self.assertEqual(strict["eligibility_status"], "ineligible")

    def test_numeric_interval_comparison_does_not_falsely_fail_upper_bound(self):
        # A scheme with lower bound >= 18 and upper bound <= 50
        two_bound_scheme = {
            "scheme_name": "Vocational Education and Training Loan Scheme",
            "jurisdiction": "Central",
            "benefit": "Loan up to Rs. 4,00,000",
            "sources": [{"url": "https://www.myscheme.gov.in/schemes/vetls", "title": "VETLS"}],
            "eligibility_rules": [
                {
                    "field": "age",
                    "operator": "gte",
                    "value": 18,
                    "rule_text": "Minimum age 18 years on completion of the course",
                    "evidence_quote": "The candidate should attain a minimum age of 18 years on completion of the course.",
                    "source_url": "https://www.myscheme.gov.in/schemes/vetls",
                },
                {
                    "field": "age",
                    "operator": "lte",
                    "value": 50,
                    "rule_text": "Maximum age 50 years",
                    "evidence_quote": "The upper age limit is up to 50 years.",
                    "source_url": "https://www.myscheme.gov.in/schemes/vetls",
                },
            ],
        }

        # If citizen answers "At or above 18 years", rule 1 (gte 18) is MET.
        # Rule 2 (lte 50) must NOT be NOT_MET (since [18, inf] might be <= 50, e.g. 20, so it is UNKNOWN, not NOT_MET).
        res_open = evaluate_schemes([two_bound_scheme], {"age": "At or above 18 years"})[0]
        matrix_open = {item["rule_text"]: item["status"] for item in res_open["eligibility_matrix"]}
        self.assertEqual(matrix_open["Minimum age 18 years on completion of the course"], "MET")
        self.assertEqual(matrix_open["Maximum age 50 years"], "UNKNOWN")  # NOT "NOT_MET"!

        # If citizen gives concrete age 21, BOTH rules must be MET
        res_concrete = evaluate_schemes([two_bound_scheme], {"age": 21})[0]
        matrix_concrete = {item["rule_text"]: item["status"] for item in res_concrete["eligibility_matrix"]}
        self.assertEqual(matrix_concrete["Minimum age 18 years on completion of the course"], "MET")
        self.assertEqual(matrix_concrete["Maximum age 50 years"], "MET")
        self.assertEqual(res_concrete["eligibility_status"], "meets_captured_rules")

        # If citizen gives age 55, upper bound is NOT_MET
        res_old = evaluate_schemes([two_bound_scheme], {"age": 55})[0]
        matrix_old = {item["rule_text"]: item["status"] for item in res_old["eligibility_matrix"]}
        self.assertEqual(matrix_old["Minimum age 18 years on completion of the course"], "MET")
        self.assertEqual(matrix_old["Maximum age 50 years"], "NOT_MET")
        self.assertEqual(res_old["eligibility_status"], "ineligible")


if __name__ == "__main__":
    unittest.main()
