"""
Comprehensive Scope Boundary & Edge-Case Test Suite for JanSahayak (myScheme).
Run: python test_scope.py (from the backend directory)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.crawler.domain_guard import check_domain_guard

# ── 1. HARD QUERIES: SHOULD BE BLOCKED (OUT_OF_DOMAIN) ─────────────────────
OOD_CASES = [
    # Foreign / Overseas Education (including user's exact query & typo)
    "schemes for foreign education",
    "schemes for foreign eucation",
    "government scholarship for studying abroad",
    "Indian government scheme for studying in USA",
    "scholarship for studying in UK",
    "how to study in Germany with Indian government support",
    "education loan for studying in Australia",
    "foreign education scheme for Indian students",
    "foreign eucation loan",
    "overseas education scholarship",
    "government benefit for living abroad",
    "schemes outside India",
    "loan to study in Singapore",
    "study abroad scholarship for Indian students",
    "scholarship for masters in Canada",
    "scholarship for Harvard university",
    "can government fund my degree at Oxford",
    "MIT admission and scholarship",
    "Chevening scholarship for Indian students",
    "Fulbright scholarship 2024",
    "DAAD scholarship Germany",
    "Erasmus Mundus scholarship Europe",
    "Rhodes scholarship Oxford",

    # Immigration, Visa, and Foreign Jobs
    "visa for studying in Canada",
    "immigration to USA",
    "how to get a green card",
    "work permit in UK",
    "h1b visa lottery process",
    "Schengen visa requirements",
    "how to settle in Australia with PR",

    # General Out-of-Domain (Coding, Homework, Entertainment, Shopping, Food)
    "how to write python code for quicksort",
    "solve quadratic equation 3x^2 + 5x - 2 = 0",
    "who won the IPL match yesterday",
    "recipe for butter chicken",
    "best smartphone under 20000 on amazon",
    "tell me a funny joke about doctors",
    "bitcoin trading strategy for beginners",
    "what is the capital of France",
]

# ── 2. LEGITIMATE QUERIES: SHOULD BE ALLOWED (IN_DOMAIN) ───────────────────
IN_DOMAIN_CASES = [
    # Indian Domestic Education Schemes
    "scholarship for BTech students in India",
    "Central Sector scholarship for college students",
    "PM-USP scholarship eligibility",
    "National Scholarship Portal registration",
    "education loan for engineering college in India",
    "Vidya Lakshmi portal loan",
    "NMMS scholarship for class 8",
    "Dr Ambedkar post matric scholarship",
    "fee reimbursement for OBC students in Telangana",
    "post matric scholarship for SC students in Maharashtra",
    "pre matric scholarship for minority students",
    "Kishori Shakti Yojana for adolescent girls",

    # Agriculture & Rural
    "PM-KISAN eligibility for small farmer",
    "PM Kusum solar irrigation pump subsidy",
    "kisan credit card limit and interest rate",
    "tractor subsidy under SMAM scheme",
    "soil health card scheme benefits",

    # Health & Social Welfare
    "Ayushman Bharat card kaise banaye",
    "PM-JAY 5 lakh hospital cashless treatment",
    "widow pension scheme rajasthan",
    "Indira Gandhi national old age pension",
    "Divyangjan disability pension eligibility",

    # Business, Housing & Energy
    "PM Surya Ghar solar subsidy",
    "Mudra loan for small business",
    "PMEGP 35 percent subsidy for manufacturing unit",
    "PM SVANidhi loan for street vendors",
    "Pradhan Mantri Awas Yojana Gramin pucca house",
    "Stand Up India loan for SC/ST women entrepreneurs",
]

PASS = 0
FAIL = 0
FAILURES = []

print("=" * 75)
print("JANSAHAYAK COMPREHENSIVE SCOPE BOUNDARY TEST SUITE")
print("=" * 75)

print("\n--- 1. OUT-OF-DOMAIN CASES (EXPECTED: OUT_OF_DOMAIN) ---")
for q in OOD_CASES:
    status, msg = check_domain_guard(q)
    ok = (status == "OUT_OF_DOMAIN")
    icon = "✅" if ok else "❌"
    print(f"{icon} [{status:16s}] {q}")
    if ok:
        PASS += 1
    else:
        FAIL += 1
        FAILURES.append(("SHOULD_BLOCK", q, status))

print("\n--- 2. IN-DOMAIN WELFARE CASES (EXPECTED: IN_DOMAIN) ---")
for q in IN_DOMAIN_CASES:
    status, msg = check_domain_guard(q)
    ok = (status == "IN_DOMAIN")
    icon = "✅" if ok else "❌"
    print(f"{icon} [{status:16s}] {q}")
    if ok:
        PASS += 1
    else:
        FAIL += 1
        FAILURES.append(("SHOULD_ALLOW", q, status))

total = PASS + FAIL
print("\n" + "=" * 75)
print(f"RESULTS: {PASS}/{total} PASSED  |  {FAIL} FAILED")
if FAILURES:
    print("\nFAILED CASES:")
    for kind, q, got in FAILURES:
        print(f"  [{kind}] got={got} | query: {q}")
else:
    print("ALL TESTS PASSED WITH 100% ACCURACY! 🎉")
print("=" * 75)
