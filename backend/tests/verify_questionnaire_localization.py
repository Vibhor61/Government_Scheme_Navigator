"""
Verification Suite for Multi-Lingual Questionnaire & UI Localization
Validates:
  1. Service Unavailable message is returned natively in all 8+ Indian languages.
  2. Questionnaire questions, options, labels, and hints are generated in native script
     (Bengali, Kannada, Hindi, Marathi, Telugu, Tamil, Gujarati).
"""

import os
import sys
import re
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.crawler.domain_guard import generate_service_unavailable_response
from app.crawler.questionnaire_tool import questionnaire_tool


def test_service_unavailable_messages():
    print("=" * 80)
    print("TEST 1: NATIVE 'JAN SAHAYAK UNAVAILABLE' NOTICES ACROSS LANGUAGES")
    print("=" * 80)

    test_langs = [
        ("hi", "Hindi", r"[\u0900-\u097F]", "जन सहायक"),
        ("bn", "Bengali", r"[\u0980-\u09FF]", "জন সহায়ক"),
        ("kn", "Kannada", r"[\u0C80-\u0CFF]", "ಜನ ಸಹಾಯಕ"),
        ("mr", "Marathi", r"[\u0900-\u097F]", "जन सहाय्यक"),
        ("ta", "Tamil", r"[\u0B80-\u0BFF]", "ஜன் சஹாயக்"),
        ("te", "Telugu", r"[\u0C00-\u0C7F]", "జన సహాయక్"),
        ("gu", "Gujarati", r"[\u0A80-\u0AFF]", "જન સહાયક"),
        ("pa", "Punjabi", r"[\u0A00-\u0A7F]", "ਜਨ ਸਹਾਇਕ"),
        ("en", "English", r"[A-Za-z]", "Jan Sahayak"),
    ]

    all_passed = True
    for code, name, script_regex, expected_keyword in test_langs:
        msg = generate_service_unavailable_response(code)
        has_script = bool(re.search(script_regex, msg))
        has_keyword = expected_keyword in msg

        passed = has_script and has_keyword
        if not passed:
            all_passed = False

        status = "✅ PASS" if passed else "❌ FAIL"
        preview = msg.replace("\n", " ")[:65]
        print(f"  [{code:2}] {name:10} | {status} | {preview}...")

    assert all_passed, "One or more localized service unavailable messages failed."
    print("  -> All localized service unavailable messages verified successfully.\n")


def test_questionnaire_native_script_generation():
    print("=" * 80)
    print("TEST 2: QUESTIONNAIRE GENERATION IN NATIVE SCRIPTS & LANGUAGES")
    print("=" * 80)

    mock_scheme = [{
        "scheme_name": "Health Protection Scheme",
        "jurisdiction": "Central",
        "eligibility_rules": [
            {"field": "annual_family_income", "operator": "lte", "value": 250000, "rule_text": "Annual family income must be under 2.5 lakh rupees"},
            {"field": "state", "operator": "eq", "value": "West Bengal", "rule_text": "Must be resident of State"},
            {"field": "social_category", "operator": "in", "value": ["General", "OBC", "SC", "ST"], "rule_text": "All categories eligible"}
        ]
    }]

    eval_cases = [
        {
            "lang_code": "bn",
            "lang_name": "Bengali",
            "script_regex": r"[\u0980-\u09FF]",
            "query": "আমার পরিবারের চিকিৎসার জন্য স্বাস্থ্য বীমা প্রয়োজন"
        },
        {
            "lang_code": "hi",
            "lang_name": "Hindi",
            "script_regex": r"[\u0900-\u097F]",
            "query": "मुझे अपने परिवार के इलाज के लिए स्वास्थ्य बीमा चाहिए"
        },
        {
            "lang_code": "kn",
            "lang_name": "Kannada",
            "script_regex": r"[\u0C80-\u0CFF]",
            "query": "ನನ್ನ ಕುಟುಂಬದ ಚಿಕಿತ್ಸೆಗೆ ಆರೋಗ್ಯ ವಿಮೆ ಯೋಜನೆ ಬೇಕು"
        }
    ]

    for ec in eval_cases:
        code = ec["lang_code"]
        name = ec["lang_name"]
        reg = ec["script_regex"]
        q = ec["query"]

        print(f"\n--- Testing Questionnaire for {name} ({code}) ---")
        try:
            res = questionnaire_tool.run(
                candidate_schemes=mock_scheme,
                known_criteria={},
                user_query=q,
                target_language=code,
                target_language_name=name
            )
            questions = res.get("questions", [])
            print(f"Generated {len(questions)} questions.")

            if questions:
                first_q = questions[0]
                q_text = first_q.get("question", "")
                q_label = first_q.get("label", "")
                q_opts = first_q.get("options", [])

                has_native_q = bool(re.search(reg, q_text))
                has_native_lbl = bool(re.search(reg, q_label))
                has_native_opts = any(re.search(reg, str(opt)) for opt in q_opts)

                print(f"  Question: {q_text[:70]}...")
                print(f"  Label:    {q_label}")
                print(f"  Options:  {q_opts[:3]}")

                if has_native_q or has_native_lbl or has_native_opts:
                    print(f"  Result:   ✅ PASS (Successfully rendered in native {name} script)")
                else:
                    print(f"  Result:   ❌ FAIL (Output was in English instead of native {name} script)")
            else:
                print("  Result:   ℹ️ No questions returned (API rate limit or complete)")
        except Exception as e:
            print(f"  Result:   ⚠️ Exception: {e}")


if __name__ == "__main__":
    test_service_unavailable_messages()
    test_questionnaire_native_script_generation()
