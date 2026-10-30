import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv()

from app.crawler.llm_service import llm_service

test_queries = [
    "I run an unregistered EV battery recycling startup in Pune with 3 women employees, what subsidies exist?",
    "My sister is a divorcee living in Kerala with a physically challenged child, what cash aid or housing grant can she get?",
    "I am an ex-serviceman who wants a loan for dairy farming in Punjab",
    "I failed class 12th and want free vocational drone pilot training",
    "I am a trans person in Tamil Nadu looking for skill training and shelter support",
    "I want to export handloom sarees from Varanasi, need interest subsidy on looms"
]

for q in test_queries:
    print("=" * 80)
    print("TEST QUERY:", q)
    print("=" * 80)
    parsed = llm_service.parse_intent_and_beneficiary(q)
    if parsed:
        print("Applicant:", parsed.get("applicant"))
        print("Beneficiary:", parsed.get("beneficiary"))
        print("Domain:", parsed.get("domain"))
        print("Inferred Profile:", parsed.get("inferred_beneficiary_profile"))
        print("Questions:")
        for qn in parsed.get("profiler_questions", []):
            print(f"  - [{qn.get('id')}] {qn.get('label')}: {qn.get('question')}")
    else:
        print("Failed to parse via LLM")
    print()
