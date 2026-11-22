"""
Extensive Multi-Turn, In-Domain, Out-of-Domain & Questionnaire Convergence Test Suite.
Tests live against http://localhost:8000/api/agent/query.
"""

import httpx
import json
import re
import time
from typing import Dict, Any, List

API_URL = "http://localhost:8000/api/agent/query"

# Regex patterns for regional scripts
SCRIPTS = {
    "kn": (r"[\u0C80-\u0CFF]", "Kannada"),
    "bn": (r"[\u0980-\u09FF]", "Bengali"),
    "mr": (r"[\u0900-\u097F]", "Marathi"),
    "ta": (r"[\u0B80-\u0BFF]", "Tamil"),
    "te": (r"[\u0C00-\u0C7F]", "Telugu"),
    "gu": (r"[\u0A80-\u0AFF]", "Gujarati"),
    "pa": (r"[\u0A00-\u0A7F]", "Punjabi"),
    "hi": (r"[\u0900-\u097F]", "Hindi"),
    "en": (r"[A-Za-z]", "English"),
}

def query_agent(payload: Dict[str, Any], timeout: float = 40.0) -> Dict[str, Any]:
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(API_URL, json=payload)
        return resp.json()

def test_multiturn_workflow(lang_code: str, query_turn1: str, answer_turn2: str, answer_turn3: str):
    script_regex, lang_name = SCRIPTS[lang_code]
    print(f"\n{'='*80}")
    print(f"TESTING 3-TURN WORKFLOW FOR {lang_name.upper()} [{lang_code}]")
    print(f"{'='*80}")

    # TURN 1: Initial query
    print(f"\n[Turn 1 Inquiry]: '{query_turn1}'")
    t1_payload = {
        "query": query_turn1,
        "language": lang_code,
        "conversation_history": [],
        "user_profile": {}
    }
    t1_res = query_agent(t1_payload)
    t1_ans = t1_res.get("answer", "")
    t1_questions = t1_res.get("profiler_questions", [])
    t1_q_ids = [q.get("id") for q in t1_questions if isinstance(q, dict)]

    t1_has_script = bool(re.search(script_regex, t1_ans))
    print(f"  -> Answer length: {len(t1_ans)} chars | Has {lang_name} Script: {t1_has_script}")
    print(f"  -> Generated {len(t1_questions)} questions: {t1_q_ids}")
    assert t1_has_script, f"Turn 1 answer should contain {lang_name} script"

    # TURN 2: Partial Profile Response
    print(f"\n[Turn 2 Answer]: '{answer_turn2}'")
    history_turn2 = [
        {"role": "user", "content": query_turn1},
        {"role": "assistant", "content": t1_ans}
    ]
    t2_profile = {"annual_family_income": 150000, "state": "Karnataka" if lang_code == "kn" else "West Bengal"}
    t2_payload = {
        "query": answer_turn2,
        "language": lang_code,
        "conversation_history": history_turn2,
        "user_profile": t2_profile
    }
    t2_res = query_agent(t2_payload)
    t2_ans = t2_res.get("answer", "")
    t2_questions = t2_res.get("profiler_questions", [])
    t2_q_ids = [q.get("id") for q in t2_questions if isinstance(q, dict)]

    print(f"  -> Generated {len(t2_questions)} questions after Turn 2: {t2_q_ids}")
    # Verify strict deduplication: income and state should NOT be asked again!
    repeated_fields = set(t2_q_ids).intersection({"annual_family_income", "state"})
    print(f"  -> Deduplication Check: Repeated fields = {repeated_fields} (Must be empty)")
    assert len(repeated_fields) == 0, f"Fields repeated in questionnaire: {repeated_fields}"

    # TURN 3: Full Profile Answer (Convergence)
    print(f"\n[Turn 3 Answer]: '{answer_turn3}'")
    history_turn3 = history_turn2 + [
        {"role": "user", "content": answer_turn2},
        {"role": "assistant", "content": t2_ans}
    ]
    t3_profile = {**t2_profile, "landholding_category": "small", "farmer_status": True, "social_category": "OBC"}
    t3_payload = {
        "query": answer_turn3,
        "language": lang_code,
        "conversation_history": history_turn3,
        "user_profile": t3_profile,
        "user_clarification": "All eligibility criteria answered"
    }
    t3_res = query_agent(t3_payload)
    t3_ans = t3_res.get("answer", "")
    t3_questions = t3_res.get("profiler_questions", [])

    t3_has_script = bool(re.search(script_regex, t3_ans))
    is_converged = len(t3_questions) == 0
    print(f"  -> Turn 3 Questions Remaining: {len(t3_questions)} (Expected 0 for completed profile)")
    print(f"  -> Full Evaluation Delivered in {lang_name}: {t3_has_script}")
    print(f"  -> Convergence: {'✅ SUCCESS' if is_converged and t3_has_script else '❌ FAILED'}")

    return is_converged and t3_has_script


def test_zero_gap_prompt(lang_code: str, query: str):
    """Tests that a fully-specified prompt results in 0 profiler questions immediately."""
    print(f"\n[Zero-Gap Test ({lang_code})]: '{query[:70]}...'")
    res = query_agent({"query": query, "language": lang_code})
    questions = res.get("profiler_questions", [])
    status = "✅ PASS (0 questions asked)" if len(questions) == 0 else f"❌ FAIL ({len(questions)} redundant questions)"
    print(f"  -> Result: {status}")
    return len(questions) == 0


def test_out_of_domain_suite():
    print(f"\n{'='*80}")
    print("TESTING OUT-OF-DOMAIN GUARDS ACROSS SECTORS & LANGUAGES")
    print(f"{'='*80}")

    ood_cases = [
        # (Language, Category, Query)
        ("en", "Commercial Bank Loan", "What is the HDFC Bank personal loan interest rate for 5 lakhs?"),
        ("hi", "Commercial Bank Loan", "ICICI बैंक से पर्सनल लोन कैसे लें और ब्याज दर क्या है?"),
        ("kn", "Retail Shopping", "ಮಹೀಂದ್ರಾ 575 ಟ್ರ್ಯಾಕ್ಟರ್ ಶೋರೂಮ್ ಆನ್-ರೋಡ್ ಬೆಲೆ ಎಷ್ಟು?"),
        ("bn", "Electronics Shopping", "ভারতে আইফোন ১৫ এর বর্তমান অফার এবং ডিসকাউন্ট কত?"),
        ("mr", "Casual Banter", "मला एक छान विनोद सांगा"),
        ("ta", "Casual Banter / Code", "Write a python script to reverse a string"),
        ("te", "Civic / Challan", "ట్రాఫిక్ చలాన్ ఆన్‌లైన్‌లో ఎలా చెల్లించాలి?"),
        ("gu", "Commodity / Bullion", "આજના ૨૪ કેરેટ સોનાના ભાવ શું છે?"),
        ("pa", "Sports / Cinema", "ਕੱਲ ਦੇ ਕ੍ਰਿਕਟ ਮੈਚ ਵਿੱਚ ਕੌਣ ਜਿੱਤਿਆ?"),
    ]

    passed = 0
    for lang, cat, q in ood_cases:
        res = query_agent({"query": q, "language": lang})
        is_ood = res.get("eligibility_status") == "out_of_domain"
        schemes_empty = len(res.get("extracted_schemes", [])) == 0
        questions_empty = len(res.get("profiler_questions", [])) == 0
        ans = res.get("answer", "")
        script_reg, _ = SCRIPTS[lang]
        has_script = bool(re.search(script_reg, ans))

        ok = (is_ood or "⚠️" in ans) and schemes_empty and questions_empty and has_script
        status = "✅ PASS (Correctly Deflected)" if ok else "❌ FAIL"
        print(f"  [{lang.upper()}] {cat:22} | {status} | OOD={is_ood} Schemes={len(res.get('extracted_schemes',[]))} | '{q[:40]}...'")
        if ok:
            passed += 1
        time.sleep(3.0)

    print(f"\n-> Out-of-Domain Suite: {passed}/{len(ood_cases)} passed.")
    return passed == len(ood_cases)


def test_in_domain_boundary_suite():
    print(f"\n{'='*80}")
    print("TESTING IN-DOMAIN BOUNDARY WORKFLOWS (NO FALSE DEFLECTIONS)")
    print(f"{'='*80}")

    in_domain_cases = [
        ("en", "Mudra Loans (PMMY)", "How can I apply for a 2 lakh Mudra loan for opening a small grocery shop?"),
        ("hi", "Ayushman Bharat", "आयुष्मान भारत योजना के तहत 5 लाख तक का मुफ्त इलाज कैसे मिलेगा?"),
        ("kn", "Solar Rooftop Subsidy", "ಪಿಎಂ ಸೂರ್ಯ ಘರ್ ಯೋಜನೆ ಅಡಿಯಲ್ಲಿ ಮನೆಗೆ ಸೋಲಾರ್ ರೂಫ್‌ಟಾಪ್ ಸಬ್ಸಿಡಿ ಹೇಗೆ ಪಡೆಯುವುದು?"),
        ("bn", "Farm Mechanization (SMAM)", "কৃষি যান্ত্রিকীকরণ সাব-মিশন (SMAM) প্রকল্পের অধীনে ট্রাক্টর ভর্তুকি কিভাবে পাব?"),
        ("mr", "Kisan Samman Nidhi", "पीएम किसान सन्मान निधीचे वार्षिक ६००० रुपये मिळवण्यासाठी पात्रता काय आहे?"),
        ("ta", "Post-Matric Scholarship", "மத்திய அரசின் போஸ்ட்-மெட்ரிக் கல்வி உதவித்தொகைக்கு (Post-Matric Scholarship) தகுதி என்ன?"),
        ("te", "Street Vendor Credit", "పీఎం స్వనిధి (PM SVANidhi) పథకం ద్వారా వీధి వ్యాపారులకు ఇచ్చే రుణం ఎంత?"),
        ("gu", "Stand-Up India Scheme", "મહિલાઓ માટે સ્ટેન્ડ-અપ ઇન્ડિયા યોજના (Stand-Up India Scheme) ની લોન સહાય કેવી રીતે મળે?")
    ]

    passed = 0
    for lang, name, q in in_domain_cases:
        res = query_agent({"query": q, "language": lang})
        ans = res.get("answer", "")
        # If transient rate-limit notice encountered from upstream provider, wait and retry once
        if "⚠️" in ans or "busy" in res.get("eligibility_status", ""):
            time.sleep(4.0)
            res = query_agent({"query": q, "language": lang})
            ans = res.get("answer", "")

        is_ood = res.get("eligibility_status") == "out_of_domain"
        schemes = res.get("extracted_schemes", [])
        script_reg, _ = SCRIPTS[lang]
        has_script = bool(re.search(script_reg, ans))

        ok = (not is_ood) and len(schemes) > 0 and has_script
        status = "✅ PASS (In-Domain Confirmed)" if ok else "❌ FAIL"
        print(f"  [{lang.upper()}] {name:24} | {status} | Schemes Found={len(schemes)} | {ans.replace(chr(10), ' ')[:50]}...")
        if ok:
            passed += 1
        time.sleep(3.0)

    print(f"\n-> In-Domain Boundary Suite: {passed}/{len(in_domain_cases)} passed.")
    return passed == len(in_domain_cases)


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("STARTING EXTENSIVE MULTI-TURN, OOD, AND IN-DOMAIN TEST SUITE")
    print("#"*80)

    # 1. Test Out-of-Domain Guards across all 8 languages
    ood_ok = test_out_of_domain_suite()

    # 2. Test In-Domain Boundary Programs across all 8 languages
    id_ok = test_in_domain_boundary_suite()

    # 3. Test Zero-Gap Prompts (Initial query already has full profile)
    zg_cases = [
        ("kn", "ನಾನು ಕರ್ನಾಟಕದ 21 ವರ್ಷದ ಓಬಿಸಿ ವಿದ್ಯಾರ್ಥಿನಿ, ನನ್ನ ಕುಟುಂಬದ ವಾರ್ಷಿಕ ಆದಾಯ 1.5 ಲಕ್ಷ ರೂಪಾಯಿ, ನನಗೆ ಬಿ.ಟೆಕ್ ಕಾಲೇಜು ವಿದ್ಯಾರ್ಥಿವೇತನ ಬೇಕು"),
        ("hi", "मैं उत्तर प्रदेश का 28 वर्षीय ओबीसी किसान हूं, मेरी वार्षिक पारिवारिक आय 1.2 लाख रुपये है और मेरे पास 1.5 एकड़ कृषि भूमि है, मुझे सोलर पंप सब्सिडी चाहिए"),
        ("en", "I am a 22-year-old female student from West Bengal with OBC category and family income 1.8 lakh seeking B.Tech scholarship")
    ]
    zg_results = [test_zero_gap_prompt(l, q) for l, q in zg_cases]
    zg_ok = all(zg_results)

    # 4. Multi-turn dialogue in Kannada
    kn_mt_ok = test_multiturn_workflow(
        lang_code="kn",
        query_turn1="ರೈತರಿಗೆ ಸರ್ಕಾರದ ಸಾಲ ಮತ್ತು ಯಂತ್ರೋಪಕರಣ ಸಬ್ಸಿಡಿ ಯೋಜನೆಗಳು ಯಾವುವು?",
        answer_turn2="ನಾನು ಕರ್ನಾಟಕದ ಸಣ್ಣ ರೈತ, ನನ್ನ ಕುಟುಂಬದ ವಾರ್ಷಿಕ ಆದಾಯ 1,50,000 ರೂ ಇದೆ.",
        answer_turn3="ನನ್ನ ಬಳಿ 2 ಹೆಕ್ಟೇರ್ ಕೃಷಿ ಭೂಮಿ ಇದೆ, ಮತ್ತು ನಾನು ಓಬಿಸಿ ವರ್ಗಕ್ಕೆ ಸೇರಿದವನು. ನನ್ನ ಅರ್ಹತೆಯನ್ನು ಪರಿಶೀಲಿಸಿ."
    )

    # 5. Multi-turn dialogue in Bengali
    bn_mt_ok = test_multiturn_workflow(
        lang_code="bn",
        query_turn1="কৃষকদের জন্য সরকারি ঋণ ও ট্র্যাক্টর ভর্তুকি প্রকল্প কি কি আছে?",
        answer_turn2="আমার বাড়ি পশ্চিমবঙ্গে এবং পারিবারিক বার্ষিক আয় ১,২০,০০০ টাকা।",
        answer_turn3="আমার ১.৫ হেক্টর চাষযোগ্য জমি আছে এবং আমি ওবিসি শ্রেণীর অন্তর্ভুক্ত। দয়া করে আমার যোগ্যতা মূল্যায়ন করুন।"
    )

    print("\n" + "="*80)
    print("FINAL SUMMARY REPORT")
    print("="*80)
    print(f"1. Out-of-Domain Guardrail Suite (8 Languages):  {'✅ PASSED' if ood_ok else '❌ FAILED'}")
    print(f"2. In-Domain Welfare Boundary Suite (8 Languages): {'✅ PASSED' if id_ok else '❌ FAILED'}")
    print(f"3. Zero-Gap Non-Redundancy Profiler:              {'✅ PASSED' if zg_ok else '❌ FAILED'}")
    print(f"4. Kannada 3-Turn Dialogue & Convergence:         {'✅ PASSED' if kn_mt_ok else '❌ FAILED'}")
    print(f"5. Bengali 3-Turn Dialogue & Convergence:         {'✅ PASSED' if bn_mt_ok else '❌ FAILED'}")
    print("="*80)
