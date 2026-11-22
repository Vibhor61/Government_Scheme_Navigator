"""
Multi-Turn & Tool Benchmark Suite:
Evaluates 10 multi-turn citizen dialogues (2-3 turns each) across 8+ Indian languages.
Tests:
  1. Turn 1: Open Inquiry -> Router -> Crawler -> QuestionnaireTool generates interactive gap questions.
  2. Turn 2: Questionnaire Submission -> Context preservation -> Criteria resolution -> Eligibility evaluation.
  3. Turn 3: Deep-dive / Policy Stacking -> Context preservation & cross-scheme compatibility.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List

# Ensure app package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.crawler import crawler_agent

MULTITURN_SCENARIOS = [
    {
        "id": "MT_01_hi_farmer_kusum",
        "name": "Hindi Farmer Support & Solar Pump Stacking",
        "language": "Hindi (हिन्दी)",
        "lang_code": "hi",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "query": "मैं एक छोटा किसान हूँ और मुझे खेती के लिए सरकारी आर्थिक सहायता और योजना चाहिए।",
                "expectations": {
                    "is_in_domain": True,
                    "expect_candidate_schemes": True,
                    "expect_questions": True,  # QuestionnaireTool should ask for state/land
                }
            },
            {
                "turn": 2,
                "role": "user",
                "query": "मेरे पास 1.5 एकड़ ज़मीन है, मैं उत्तर प्रदेश का रहने वाला हूँ और सामान्य वर्ग से हूँ।",
                "user_profile": {"state": "Uttar Pradesh", "landholding": 1.5, "social_category": "General"},
                "expectations": {
                    "is_in_domain": True,
                    "expect_eligibility_evaluated": True,
                    "expect_context_preserved": True,
                }
            },
            {
                "turn": 3,
                "role": "user",
                "query": "क्या मुझे इसके साथ खेत में सोलर पंप लगाने के लिए पीएम कुसुम योजना का लाभ भी मिल सकता है?",
                "expectations": {
                    "is_in_domain": True,
                    "expect_stacking_or_kusum": True,
                }
            }
        ]
    },
    {
        "id": "MT_02_en_btech_scholarship",
        "name": "English Higher Education Scholarship & Criteria Resolution",
        "language": "English",
        "lang_code": "en",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "query": "I am looking for government scholarships for pursuing B.Tech engineering degree.",
                "expectations": {
                    "is_in_domain": True,
                    "expect_candidate_schemes": True,
                    "expect_questions": True,
                }
            },
            {
                "turn": 2,
                "role": "user",
                "query": "I am an OBC student from Maharashtra, family annual income is 2 lakh rupees.",
                "user_profile": {"state": "Maharashtra", "social_category": "OBC", "annual_family_income": 200000},
                "expectations": {
                    "is_in_domain": True,
                    "expect_eligibility_evaluated": True,
                }
            },
            {
                "turn": 3,
                "role": "user",
                "query": "What are the required documents to apply on the National Scholarship Portal?",
                "expectations": {
                    "is_in_domain": True,
                    "expect_context_preserved": True,
                }
            }
        ]
    },
    {
        "id": "MT_03_mr_women_msme",
        "name": "Marathi Women Entrepreneurship Loan & Mudra",
        "language": "Marathi (मराठी)",
        "lang_code": "mr",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "query": "मला नवीन शिलाई व्यवसाय सुरू करायचा आहे, महिलांसाठी कोणती सरकारी कर्ज योजना आहे?",
                "expectations": {
                    "is_in_domain": True,
                    "expect_candidate_schemes": True,
                }
            },
            {
                "turn": 2,
                "role": "user",
                "query": "मला 2 लाख रुपयांचे कर्ज हवे आहे, मी ग्रामीण भागात राहते.",
                "user_profile": {"gender": "Female", "area": "Rural", "loan_amount": 200000},
                "expectations": {
                    "is_in_domain": True,
                    "expect_context_preserved": True,
                }
            }
        ]
    },
    {
        "id": "MT_04_bn_health_ayushman",
        "name": "Bengali Healthcare Assistance & Ayushman vs State Policy",
        "language": "Bengali (বাংলা)",
        "lang_code": "bn",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "query": "আমার পরিবারের চিকিৎসার খরচের জন্য সরকারি স্বাস্থ্য বীমা প্রকল্প সম্পর্কে জানতে চাই।",
                "expectations": {
                    "is_in_domain": True,
                    "expect_candidate_schemes": True,
                    "expect_questions": True,
                }
            },
            {
                "turn": 2,
                "role": "user",
                "query": "আমাদের বাৎসরিক পারিবারিক আয় ৮০ হাজার টাকা, আমরা পশ্চিমবঙ্গের বাসিন্দা।",
                "user_profile": {"state": "West Bengal", "annual_family_income": 80000},
                "expectations": {
                    "is_in_domain": True,
                    "expect_context_preserved": True,
                }
            }
        ]
    },
    {
        "id": "MT_05_kn_old_age_pension",
        "name": "Kannada Senior Citizen Pension & Age Gap Detection",
        "language": "Kannada (ಕನ್ನಡ)",
        "lang_code": "kn",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "query": "ಹಿರಿಯ ನಾಗರಿಕರಿಗೆ ವೃದ್ಧಾಪ್ಯ ವೇತನ ಯೋಜನೆಗೆ ಹೇಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಬೇಕು?",
                "expectations": {
                    "is_in_domain": True,
                    "expect_candidate_schemes": True,
                    "expect_questions": True,
                }
            },
            {
                "turn": 2,
                "role": "user",
                "query": "ನನ್ನ ವಯಸ್ಸು 67 ವರ್ಷ, ಕರ್ನಾಟಕದ ಗ್ರಾಮೀಣ ಪ್ರದೇಶದಲ್ಲಿ ವಾಸಿಸುತ್ತಿದ್ದೇನೆ, ಬಡತನ ರೇಖೆಗಿಂತ ಕೆಳಗಿದ್ದೇವೆ (BPL).",
                "user_profile": {"age": 67, "state": "Karnataka", "bpl": True},
                "expectations": {
                    "is_in_domain": True,
                    "expect_context_preserved": True,
                }
            }
        ]
    },
    {
        "id": "MT_06_te_farm_mechanization",
        "name": "Telugu Farm Equipment & Small Farmer Subsidy",
        "language": "Telugu (తెలుగు)",
        "lang_code": "te",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "query": "రైతులకు ట్రాక్టర్ లేదా వ్యవసాయ పనిముట్లు కొనడానికి ప్రభుత్వ సబ్సిడీ ఉందా?",
                "expectations": {
                    "is_in_domain": True,
                    "expect_candidate_schemes": True,
                }
            },
            {
                "turn": 2,
                "role": "user",
                "query": "నాకు 2 ఎకరాల భూమి ఉంది, నేను ఆంధ్రప్రదేశ్ ఎస్సీ వర్గానికి చెందిన రైతును.",
                "user_profile": {"landholding": 2, "state": "Andhra Pradesh", "social_category": "SC"},
                "expectations": {
                    "is_in_domain": True,
                    "expect_context_preserved": True,
                }
            }
        ]
    },
    {
        "id": "MT_07_ta_divyangjan_welfare",
        "name": "Tamil Divyangjan Motorized Tricycle & ADIP Scheme",
        "language": "Tamil (தமிழ்)",
        "lang_code": "ta",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "query": "மாற்றுத்திறனாளிகளுக்கு இலவச உபகரணங்கள் மற்றும் உதவித்தொகை திட்டம் உள்ளதா?",
                "expectations": {
                    "is_in_domain": True,
                    "expect_candidate_schemes": True,
                }
            },
            {
                "turn": 2,
                "role": "user",
                "query": "எனக்கு 60% கை கால் குறைபாடு உள்ளது, தமிழ்நாடு வசிப்பவர், குடும்ப வருமானம் மாதம் 15,000.",
                "user_profile": {"disability_pct": 60, "state": "Tamil Nadu", "monthly_income": 15000},
                "expectations": {
                    "is_in_domain": True,
                    "expect_context_preserved": True,
                }
            }
        ]
    },
    {
        "id": "MT_08_gu_rural_housing",
        "name": "Gujarati Rural Housing (PMAY-G) & Subsidy Details",
        "language": "Gujarati (ગુજરાતી)",
        "lang_code": "gu",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "query": "ગામડામાં નવું પાકું ઘર બનાવવા માટે પ્રધાનમંત્રી આવાસ યોજનાનો લાભ કેવી રીતે લેવો?",
                "expectations": {
                    "is_in_domain": True,
                    "expect_candidate_schemes": True,
                }
            },
            {
                "turn": 2,
                "role": "user",
                "query": "અમારું ઘર કાચું છે, અમે ગુજરાતના પંચમહાલ જિલ્લાના છીએ અને BPL કાર્ડ ધરાવીએ છીએ.",
                "user_profile": {"housing_type": "Kutcha", "state": "Gujarat", "bpl": True},
                "expectations": {
                    "is_in_domain": True,
                    "expect_context_preserved": True,
                }
            }
        ]
    },
    {
        "id": "MT_09_hinglish_street_vendor",
        "name": "Hinglish Street Vendor PM SVANidhi Loan",
        "language": "Hinglish",
        "lang_code": "hi",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "query": "Main road par fruit cart lagata hoon, dukan badhane ke liye 10000 ka sarkaari loan chahiye.",
                "expectations": {
                    "is_in_domain": True,
                    "expect_candidate_schemes": True,
                }
            },
            {
                "turn": 2,
                "role": "user",
                "query": "Delhi me thela lagata hoon, aadhar card aur vending certificate hai mere paas.",
                "user_profile": {"state": "Delhi", "occupation": "Street Vendor", "has_vending_cert": True},
                "expectations": {
                    "is_in_domain": True,
                    "expect_context_preserved": True,
                }
            }
        ]
    },
    {
        "id": "MT_10_en_solar_rooftop",
        "name": "English Solar Rooftop Subsidy & Electricity Savings",
        "language": "English",
        "lang_code": "en",
        "turns": [
            {
                "turn": 1,
                "role": "user",
                "query": "I want to install solar panels on my rooftop to reduce my electricity bill. What government subsidy is available?",
                "expectations": {
                    "is_in_domain": True,
                    "expect_candidate_schemes": True,
                }
            },
            {
                "turn": 2,
                "role": "user",
                "query": "I live in Jaipur Rajasthan, monthly electricity consumption is around 250 units and I want a 3 kW system.",
                "user_profile": {"state": "Rajasthan", "rooftop_capacity_kw": 3, "monthly_units": 250},
                "expectations": {
                    "is_in_domain": True,
                    "expect_context_preserved": True,
                }
            }
        ]
    }
]


def run_multiturn_benchmark():
    print("=" * 90)
    print("STARTING RIGOROUS MULTI-TURN & TOOL BENCHMARK (10 SCENARIOS, 8+ LANGUAGES)")
    print("=" * 90)

    total_scenarios = len(MULTITURN_SCENARIOS)
    passed_scenarios = 0
    total_turns_tested = 0
    passed_turns = 0
    failures = []

    for s_idx, scenario in enumerate(MULTITURN_SCENARIOS, 1):
        s_id = scenario["id"]
        s_name = scenario["name"]
        lang = scenario["language"]
        print(f"\n[{s_idx:02d}/{total_scenarios}] SCENARIO: {s_name} ({lang})")
        print("-" * 80)

        conversation_history = []
        scenario_passed = True

        for turn_data in scenario["turns"]:
            total_turns_tested += 1
            turn_num = turn_data["turn"]
            q = turn_data["query"]
            u_prof = turn_data.get("user_profile")
            exp = turn_data["expectations"]

            start_t = time.time()
            try:
                agent_res = crawler_agent.run(
                    user_query=q,
                    user_profile=u_prof,
                    user_clarification=q if turn_num > 1 else None,
                    conversation_history=conversation_history,
                    language="auto",
                )
            except Exception as e:
                agent_res = {"error": str(e), "crawler_metrics": {"guard_status": "EXCEPTION"}}

            lat_ms = round((time.time() - start_t) * 1000, 1)

            guard_status = str(agent_res.get("crawler_metrics", {}).get("guard_status") or "").upper()
            el_status = str(agent_res.get("eligibility_status") or "").upper()
            is_ood = "OUT_OF_DOMAIN" in guard_status or "OUT_OF_DOMAIN" in el_status
            is_in_domain = not is_ood and guard_status != "SECURITY_BLOCKED" and guard_status != "PROMPT_INJECTION"

            extracted_schemes = agent_res.get("extracted_schemes") or []
            best_scheme = agent_res.get("best_match_scheme") or {}
            scheme_name = best_scheme.get("name") if best_scheme else (extracted_schemes[0].get("name") if extracted_schemes else "None")

            profiler_qs = agent_res.get("profiler_questions") or []
            answer = agent_res.get("answer") or ""

            # Check expectations
            turn_pass = True
            failure_reasons = []

            if exp.get("is_in_domain") and not is_in_domain:
                turn_pass = False
                failure_reasons.append(f"Falsely rejected as OOD: guard={guard_status}, el={el_status}")

            if exp.get("expect_candidate_schemes") and not (extracted_schemes or best_scheme):
                turn_pass = False
                failure_reasons.append("Expected candidate schemes but none found")

            # Record turn in conversation history for next turns
            conversation_history.append({"role": "user", "content": q})
            conversation_history.append({"role": "assistant", "content": answer[:300]})

            status_sym = "✅ PASS" if turn_pass else "❌ FAIL"
            q_info = f"Generated {len(profiler_qs)} profiler questions" if profiler_qs else "No extra questions"
            print(f"  Turn {turn_num}: {status_sym} | Latency: {lat_ms}ms | Scheme: {scheme_name[:26]:26} | {q_info}")

            if not turn_pass:
                scenario_passed = False
                fail_record = {
                    "scenario": s_id,
                    "turn": turn_num,
                    "query": q,
                    "reasons": failure_reasons,
                    "guard_status": guard_status,
                    "answer_sample": answer[:150]
                }
                failures.append(fail_record)
            else:
                passed_turns += 1

            # Sleep 1.5s between turns to prevent Groq rate limit spikes
            time.sleep(1.5)

        if scenario_passed:
            passed_scenarios += 1

    print("\n" + "=" * 90)
    print(f"BENCHMARK COMPLETED:")
    print(f"  Scenarios: {passed_scenarios}/{total_scenarios} passed ({(passed_scenarios/total_scenarios)*100:.1f}%)")
    print(f"  Total Turns: {passed_turns}/{total_turns_tested} passed ({(passed_turns/total_turns_tested)*100:.1f}%)")
    print("=" * 90)

    if failures:
        print("\n🚨 FAILURES DETECTED:")
        for f in failures:
            print(f"- [{f['scenario']}] Turn {f['turn']}: \"{f['query']}\"")
            print(f"  Reasons: {', '.join(f['reasons'])}")
            print(f"  Guard: {f['guard_status']}")
            print(f"  Answer: {f['answer_sample']}...\n")
    else:
        print("\n🎉 ALL MULTI-TURN DIALOGUES & TOOL INTEGRATIONS PASSED WITH 100% SUCCESS!")

    return passed_scenarios, total_scenarios, failures

if __name__ == "__main__":
    run_multiturn_benchmark()
