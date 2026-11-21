"""
Round 2 Advanced Benchmark: Testing 12 New Advanced Queries
  - 6 In-Scope: Untapped Welfare Sectors & Regional Scripts (PMMVY, PM SVANidhi, PMMSY, ADIP Divyangjan, Ujjwala, NRLM SHG)
  - 6 Out-of-Scope: Subtle Civic Administrative Services vs Welfare Entitlements (Passport PSK, Traffic Challan, ITR-1, Apollo Doctor OPD, RTO License, Gold Price)
"""

import sys
import json
import time
from app.crawler import crawler_agent

ROUND2_TEST_CASES = [
    # ── IN-SCOPE: Untapped Welfare Sectors & Regional Scripts ──────────────────
    {
        "id": "R2_01_maternity_pmmvy_hi",
        "category": "In-Scope Welfare",
        "lang": "Hindi (हिन्दी)",
        "query": "मेरी पहली डिलीवरी होने वाली है, क्या गर्भवती महिलाओं के लिए सरकार से 5000 रुपये की आर्थिक सहायता मिलती है?",
        "expected": "IN_DOMAIN",
        "expected_scheme_hint": "Matru Vandana / PMMVY",
        "description": "PMMVY ₹5,000 maternity cash incentive for pregnant mothers"
    },
    {
        "id": "R2_02_street_vendor_te",
        "category": "In-Scope Welfare",
        "lang": "Telugu (తెలుగు)",
        "query": "తోపుడు బండ్ల వ్యాపారులకు ఇచ్చే 10 వేల పీఎం స్వనిధి రుణం ఎలా పొందాలి?",
        "expected": "IN_DOMAIN",
        "expected_scheme_hint": "PM SVANidhi",
        "description": "PM SVANidhi ₹10,000 working capital loan for street vendors in Telugu"
    },
    {
        "id": "R2_03_fisheries_pmmsy_bn",
        "category": "In-Scope Welfare",
        "lang": "Bengali (বাংলা)",
        "query": "বায়োফ্লক মাছ চাষের জন্য সরকারি ভর্তুকি এবং প্রধানমন্ত্রী মৎস্য সম্পদ যোজনা সম্পর্কে জানান।",
        "expected": "IN_DOMAIN",
        "expected_scheme_hint": "PM Matsya Sampada",
        "description": "Biofloc fish farming subsidy under PMMSY in Bengali"
    },
    {
        "id": "R2_04_divyangjan_adip_ta",
        "category": "In-Scope Welfare",
        "lang": "Tamil (தமிழ்)",
        "query": "மாற்றுத்திறனாளிகளுக்கு இலவச மோட்டார் பொருத்தப்பட்ட மூன்று சக்கர வண்டி வழங்கும் அரசு திட்டம் எது?",
        "expected": "IN_DOMAIN",
        "expected_scheme_hint": "ADIP / Divyangjan",
        "description": "Motorized tricycle aid for Divyangjan under ADIP in Tamil"
    },
    {
        "id": "R2_05_ujjwala_lpg_mr",
        "category": "In-Scope Welfare",
        "lang": "Marathi (मराठी)",
        "query": "दारिद्र्यरेषेखालील (BPL) कुटुंबांसाठी मोफत गॅस कनेक्शन आणि उज्ज्वला योजना कशी मिळेल?",
        "expected": "IN_DOMAIN",
        "expected_scheme_hint": "PM Ujjwala",
        "description": "Free BPL LPG gas connection under PM Ujjwala Yojana in Marathi"
    },
    {
        "id": "R2_06_shg_nrlm_kn",
        "category": "In-Scope Welfare",
        "lang": "Kannada (ಕನ್ನಡ)",
        "query": "ಮಹಿಳಾ ಸ್ವಸಹಾಯ ಸಂಘಗಳಿಗೆ (SHG) ಸರ್ಕಾರದಿಂದ ಬಡ್ಡಿರಹಿತ ಸಾಲ ಸಿಗುತ್ತಾ?",
        "expected": "IN_DOMAIN",
        "expected_scheme_hint": "NRLM / SHG",
        "description": "Interest-subvented collateral-free loan for women SHGs in Kannada"
    },

    # ── OUT-OF-SCOPE: Civic Administration & Private Services vs Welfare ─────
    {
        "id": "R2_07_passport_psk_en",
        "category": "Out-of-Scope (Civic Admin)",
        "lang": "English",
        "query": "How to book Tatkal passport appointment slot at Regional Passport Office (PSK)?",
        "expected": "OUT_OF_DOMAIN",
        "description": "Administrative passport appointment booking (not welfare scheme)"
    },
    {
        "id": "R2_08_traffic_challan_hi",
        "category": "Out-of-Scope (Civic Fine)",
        "lang": "Hindi (हिन्दी)",
        "query": "ट्रैफिक पुलिस का कटा हुआ ई-चालान ऑनलाइन कैसे भरें?",
        "expected": "OUT_OF_DOMAIN",
        "description": "Traffic fine payment portal (not welfare benefit)"
    },
    {
        "id": "R2_09_itr_income_tax_hinglish",
        "category": "Out-of-Scope (Tax Compliance)",
        "lang": "Hinglish",
        "query": "Salary income ke liye ITR-1 Sahaj form online portal par kaise file karein?",
        "expected": "OUT_OF_DOMAIN",
        "description": "Income tax return filing compliance (not welfare grant)"
    },
    {
        "id": "R2_10_apollo_doctor_en",
        "category": "Out-of-Scope (Private Clinic)",
        "lang": "English",
        "query": "Apollo hospital me cardiologist doctor ki appointment booking kaise karein?",
        "expected": "OUT_OF_DOMAIN",
        "description": "Private hospital consultation appointment (not public welfare scheme)"
    },
    {
        "id": "R2_11_rto_license_en",
        "category": "Out-of-Scope (Civic License)",
        "lang": "English",
        "query": "RTO office driving test slot booking for permanent driving license.",
        "expected": "OUT_OF_DOMAIN",
        "description": "RTO driving license test scheduling (administrative licensing)"
    },
    {
        "id": "R2_12_gold_commodity_price_hi",
        "category": "Out-of-Scope (Commodity Price)",
        "lang": "Hindi (हिन्दी)",
        "query": "आज 24 कैरेट सोने का भाव क्या चल रहा है बाजार में?",
        "expected": "OUT_OF_DOMAIN",
        "description": "Commodity gold bullion price inquiry (not citizen welfare)"
    }
]

def run_round2():
    print("=" * 85)
    print("ROUND 2: ADVANCED MULTI-LINGUAL SCOPE & CIVIC/WELFARE BENCHMARK")
    print("=" * 85)

    results = []
    failures = []

    for idx, tc in enumerate(ROUND2_TEST_CASES, 1):
        q = tc["query"]
        expected = tc["expected"]
        
        start = time.time()
        agent_res = crawler_agent.run(user_query=q)
        duration_ms = round((time.time() - start) * 1000, 2)

        el_status = str(agent_res.get("eligibility_status") or "").upper()
        guard_status = str(agent_res.get("crawler_metrics", {}).get("guard_status") or "").upper()

        if "OUT_OF_DOMAIN" in guard_status or "OUT_OF_DOMAIN" in el_status:
            actual = "OUT_OF_DOMAIN"
        elif "SECURITY_BLOCKED" in guard_status:
            actual = "OUT_OF_DOMAIN"
        elif "PROMPT_INJECTION" in guard_status:
            actual = "PROMPT_INJECTION"
        else:
            actual = "IN_DOMAIN"

        passed = (actual == expected)
        best_scheme = agent_res.get("best_match_scheme", {})
        scheme_name = best_scheme.get("name") if best_scheme else "None"
        answer_preview = (agent_res.get("answer") or "")[:90].replace("\n", " ")

        res = {
            "id": tc["id"],
            "category": tc["category"],
            "lang": tc["lang"],
            "query": q[:60] + ("..." if len(q) > 60 else ""),
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "latency_ms": duration_ms,
            "scheme": scheme_name,
            "answer_preview": answer_preview,
            "description": tc["description"]
        }
        results.append(res)
        if not passed:
            failures.append(res)

        status_sym = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{idx:02d}/{len(ROUND2_TEST_CASES)}] {status_sym} | {tc['lang'][:10]:10} | Exp: {expected:14} | Act: {actual:14} | Matched: {scheme_name[:25]:25} | {tc['id']}")

    print("\n" + "=" * 85)
    print(f"SUMMARY: Total Tests: {len(ROUND2_TEST_CASES)} | Passed: {len(ROUND2_TEST_CASES) - len(failures)} | Failed: {len(failures)}")
    print("=" * 85)

    if failures:
        print("\n🚨 DETAILED FAILURE BREAKDOWN:")
        for f in failures:
            print(f"- Test ID: {f['id']} ({f['category']})")
            print(f"  Query: \"{f['query']}\"")
            print(f"  Expected: {f['expected']} | Actual: {f['actual']}")
            print(f"  Matched Scheme: {f['scheme']}")
            print(f"  Answer Preview: {f['answer_preview']}")
            print(f"  Description: {f['description']}\n")

    return results, failures

if __name__ == "__main__":
    run_round2()
