"""
Policy Interaction Engine: Dynamic Cross-Scheme Conflict & Stacking Intelligence.

Evaluates interactions across multiple official welfare schemes across ANY sector:
- Health & Medical (Ayushman Bharat, Jan Aushadhi, PM National Dialysis, Arogya Nidhi)
- Higher Education & Scholarships (NSP, Pragati, Vidya Lakshmi, CSIS)
- Women & Child Development (PMMVY, Sukanya Samriddhi, Ladli Behna, Janani Suraksha)
- MSME & Micro-Enterprise (PM SVANidhi, PMEGP, Mudra, Stand-Up India)
- Disability & Senior Citizens (Vay Vandana, ADIP, Vayoshri, UDID, Indira Gandhi Pension)
- Agriculture & Rural (PM-KISAN, KCC, PM Fasal Bima, PM-KUSUM)
- Housing & Habitat (PMAY-G, PMAY-U, State Awas, SBM, Ujjwala)

Methodology:
1. LLM-First Dynamic Policy Interaction Analysis (Groq JSON mode via llm_service)
2. Comprehensive Multi-Domain Deterministic Fallback (No single-sector hardcoding)
3. Integration with SourceConflictDetector for official circular discrepancies
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional
from .conflict_detector import SourceConflictDetector
from .llm_service import llm_service

logger = logging.getLogger("gov_scheme.policy_interaction")


POLICY_INTERACTION_SYSTEM_PROMPT = """You are the Senior Policy Analyst & Welfare Convergence Specialist for the Indian Government Scheme Navigator.
Your role is to analyze a set of discovered government welfare schemes for a citizen and evaluate:
1. CROSS-SCHEME CONFLICTS & EXCLUSIONS: Are there schemes in the list that conflict with each other or bar concurrent benefits?
   - Examples of real policy exclusions:
     * Housing: Cannot receive two pucca housing grants (e.g. Central PMAY vs State Housing).
     * Scholarship: Central/State guidelines strictly forbid claiming concurrent maintenance allowances in the same academic year.
     * Health: Statutory medical scheme beneficiaries (CGHS/ESIC) are excluded from AB-PMJAY unless qualifying under universal senior citizen (70+) rules.
     * Farmer income: PM-KISAN excludes income-tax payers, government servants, and institutional landholders.
     * Street vendor: 1st tranche cap vs escalation tranches.
2. WELFARE STACKING & CONVERGENCE: Can 2 or more schemes be stacked/combined synergistically to maximize total citizen benefits without policy violations?
   - Applicable to ANY domain:
     * Health: Combine hospitalization cover (AB-PMJAY) + discounted generic medicines (PM Jan Aushadhi) + state critical illness top-ups.
     * Education: Combine tuition fee waiver/scholarship (NSP) + interest-subsidized education loan (Vidya Lakshmi) + skill development (PMKVY).
     * Women & Child: Combine maternity benefit (PMMVY) + institutional delivery cash (JSY) + girl child savings (Sukanya Samriddhi).
     * MSME / Business: Combine capital margin money grant (PMEGP) + collateral-free working capital loan (Mudra / PM SVANidhi).
     * Senior Citizens / Disability: Combine healthcare (Vay Vandana 70+) + assistive living devices (Vayoshri / ADIP) + monthly pension.
     * Agriculture: Combine income support (PM-KISAN) + subsidized credit (KCC) + crop risk cover (PMFBY).

CRITICAL RULES:
- Ground all advice strictly in actual Indian welfare policy norms.
- Do NOT hallucinate fictitious scheme rules.
- If there is NO conflict among the schemes, set has_conflict = false and conflict = null.
- If schemes cannot be stacked (e.g. only 1 scheme exists), set welfare_stack = null.

Respond strictly in valid JSON matching this schema:
{
  "has_conflict": true | false,
  "conflict": {
    "title": "Clear conflict title citing the schemes",
    "discrepancy_field": "Short name of policy restriction (e.g. Concurrent Scholarship Bar, Dual Housing Grant Exclusivity)",
    "explanation": "Clear plain-language explanation of why both cannot be claimed simultaneously",
    "scheme_a": {"name": "Scheme A Name", "level": "Central | State"},
    "scheme_b": {"name": "Scheme B Name", "level": "Central | State"},
    "source_a": {"portal": "Scheme A Guidelines", "rule": "Exact exclusion rule or clause text"},
    "source_b": {"portal": "Scheme B Guidelines", "rule": "Duplicate application / de-duplication bar text"},
    "recommendation": {
      "preferred_scheme": "Recommended Scheme Name",
      "reason": "Why this scheme is better to prioritize (higher aid, direct DBT, etc.)",
      "action": "Immediate recommended step for the citizen"
    },
    "clarification_prompt": "Which scheme would you like to prioritize for detailed checking?",
    "options": ["Prioritize Scheme A", "Prioritize Scheme B", "Compare both options"]
  } | null,
  "welfare_stack": {
    "bundle_title": "Inspiring, domain-specific title with appropriate emoji (e.g. 🏥 Integrated Healthcare & Medication Protection Stack)",
    "bundle_type": "HEALTH_CONVERGENCE | STUDENT_CONVERGENCE | WOMEN_CHILD_CONVERGENCE | MSME_LIVELIHOOD_CONVERGENCE | SENIOR_DISABILITY_CONVERGENCE | AGRICULTURAL_CONVERGENCE | HABITAT_CONVERGENCE | MULTI_SECTOR_PORTFOLIO",
    "badge": "Policy Convergence Approved",
    "description": "Clear explanation of how these schemes work together synergistically",
    "total_financial_impact": "Summary of cumulative benefits (e.g. ₹5,00,000 Health Cover + 50-90% Discounted Generic Medicines)",
    "schemes": [
      {
        "name": "Scheme Name",
        "role": "Specific role (e.g. Hospitalization Shield, Tuition Support, Maternity Grant)",
        "benefit_summary": "1-sentence summary of benefit"
      }
    ],
    "application_sequence": [
      {
        "step": 1,
        "title": "Actionable step title",
        "instruction": "Clear instructions on which portal to visit and what to submit first"
      }
    ]
  } | null
}
"""


# -----------------------------------------------------------------------------
# Comprehensive Multi-Domain Taxonomy for Deterministic Fallback
# -----------------------------------------------------------------------------
SECTOR_TAXONOMY = {
    "health": {
        "keywords": {"health", "medical", "hospital", "hospitalization", "ayushman", "pmjay", "pm-jay", "medicine", "aushadhi", "dialysis", "treatment", "patient", "disease", "arogyasri", "swasthya"},
        "stack_title": "🏥 Integrated Universal Healthcare & Medication Stack",
        "stack_type": "HEALTH_CONVERGENCE",
        "default_impact": "₹5,00,000 Free In-Patient Cover + Subsidized Essential Medicines",
        "rationale": "Secondary/tertiary hospital treatment under Ayushman Bharat synergizes directly with Jan Aushadhi generic medicines and national screening programs.",
        "seq": [
            ("Verify PM-JAY / Golden Card Status", "Check your name on the Ayushman Bharat portal or visit nearest empanelled hospital Ayushman Mitra desk with your Aadhaar."),
            ("Access Subsidized Generic Medicines", "Locate your nearest Pradhan Mantri Jan Aushadhi Kendra for 50-90% lower prescription medicine costs."),
            ("State Chief Minister Relief Fund", "For specialized procedures beyond the ₹5L ceiling, submit an application to the State Health Society.")
        ]
    },
    "education": {
        "keywords": {"student", "students", "scholarship", "college", "school", "university", "btech", "degree", "tuition", "education", "fellowship", "stipend", "study", "pragati", "saksham", "vidya lakshmi"},
        "stack_title": "🎓 Student Higher Education & Academic Support Stack",
        "stack_type": "STUDENT_CONVERGENCE",
        "default_impact": "Full Course Tuition Fee Support + Subsidized Education Credit",
        "rationale": "Combine tuition fee waivers, central maintenance stipends, and interest-subsidized education loans concurrently without policy conflicts.",
        "seq": [
            ("Apply on National Scholarship Portal (NSP)", "Register on NSP using One-Time Registration (OTR) and submit your verified family income certificate."),
            ("Apply on PM Vidya Lakshmi Portal", "If supplementary financing is needed, apply for education loans with central interest subvention (CSIS)."),
            ("Institute Verification", "Ensure your college nodal officer verifies your student bonafide certificate before portal deadlines.")
        ]
    },
    "women_child": {
        "keywords": {"women", "woman", "girl", "maternity", "mother", "child", "children", "matru", "vandana", "sukanya", "samriddhi", "ladli", "janani", "poshan", "widow"},
        "stack_title": "👩‍👧 Comprehensive Women & Maternal Empowerment Stack",
        "stack_type": "WOMEN_CHILD_CONVERGENCE",
        "default_impact": "Direct DBT Cash Transfer + Subsidized Savings & Institutional Care",
        "rationale": "Maternal nutrition cash transfers (PMMVY) operate in full harmony with Janani Suraksha Yojana institutional delivery and Sukanya Samriddhi girl-child savings.",
        "seq": [
            ("Register Pregnancy / Mother-Child Card (MCP)", "Register at your local Anganwadi Centre / ASHA worker for PMMVY DBT installments."),
            ("Institutional Delivery Benefit", "Avail free delivery and transport incentive under Janani Suraksha Yojana at government hospital."),
            ("Open Sukanya Samriddhi Account", "Deposit initial savings at any post office or nationalized bank for highest tax-free compounding interest.")
        ]
    },
    "msme_business": {
        "keywords": {"business", "msme", "vendor", "street vendor", "entrepreneur", "enterprise", "startup", "mudra", "pmegp", "artisan", "vishwakarma", "loan", "credit", "svanidhi"},
        "stack_title": "💼 MSME Entrepreneurship & Working Capital Stack",
        "stack_type": "MSME_LIVELIHOOD_CONVERGENCE",
        "default_impact": "Capital Margin Grant (15-35%) + Collateral-Free Credit Guarantee",
        "rationale": "Micro-enterprises can combine capital margin grants (PMEGP) with credit guarantees (CGTMSE) and working capital lines (Mudra) without disqualification.",
        "seq": [
            ("Register Udyam Aadhaar", "Obtain instant, free Udyam MSME registration online on udyamregistration.gov.in."),
            ("Apply for PMEGP Capital Subsidy", "Submit project proposal on KVIC portal to secure up to 35% margin money government grant."),
            ("Avail Working Capital via Mudra", "Apply for Shishu/Kishore loan at your operational bank to fund ongoing inventory and receivables.")
        ]
    },
    "senior_disability": {
        "keywords": {"senior", "elderly", "pension", "old age", "disability", "disabled", "divyang", "divyangjan", "udid", "adip", "vayoshri", "vay vandana"},
        "stack_title": "🧓 Senior Citizen & Divyangjan Dignity & Care Stack",
        "stack_type": "SENIOR_DISABILITY_CONVERGENCE",
        "default_impact": "Universal Free Healthcare Cover + Assistive Living Devices + Monthly Pension",
        "rationale": "Universal health coverage under Ayushman Vay Vandana stacks concurrently with assistive living aids (Rashtriya Vayoshri / ADIP) and social security pensions.",
        "seq": [
            ("Obtain Ayushman Vay Vandana Card / UDID", "Generate your senior health card on the Ayushman app or apply for UDID card on swavlambancard.gov.in."),
            ("Apply for Assistive Devices", "Enroll at the District ALIMCO / Social Welfare camp for free hearing aids, wheelchairs, or spectacles."),
            ("Enroll in National Social Assistance (NSAP)", "Submit Aadhaar and bank details at the Tehsil / Block office for monthly Direct DBT pension.")
        ]
    },
    "housing": {
        "keywords": {"housing", "awas", "house", "home", "dwelling", "construction", "pucca house", "pmay", "ashraya"},
        "stack_title": "🏡 Integrated Rural & Urban Habitat Stack",
        "stack_type": "HABITAT_CONVERGENCE",
        "default_impact": "₹1,20,000 - ₹2,50,000 Housing Subsidy + Sanitation Grant + Free LPG Connection",
        "rationale": "Under Union convergence mandates, housing allotment automatically unlocks priority toilet construction grants and clean cooking gas.",
        "seq": [
            ("PMAY Geo-Tagged Sanction", "Complete Gram Panchayat / ULB verification for initial construction installment."),
            ("Claim SBM Sanitation Incentive", "Claim ₹12,000 toilet grant through the local authority upon plinth level inspection."),
            ("Avail PM Ujjwala Connection", "Present your housing sanction letter to the nearest LPG distributor for deposit-free LPG.")
        ]
    },
    "agriculture": {
        "keywords": {"farmer", "farmers", "farm", "farming", "agriculture", "kisan", "crop", "seed", "irrigation", "tractor", "fasal bima", "pmkisan", "pm-kisan", "kusum"},
        "stack_title": "🌾 Integrated Farmer Prosperity & Risk Shield Stack",
        "stack_type": "AGRICULTURAL_CONVERGENCE",
        "default_impact": "₹6,000/yr Direct Cash + Up to ₹3,00,000 Concessional Credit + Comprehensive Crop Insurance",
        "rationale": "PM-KISAN income support operates as the verified anchor for fast-track Kisan Credit Card issuance and seasonal crop insurance.",
        "seq": [
            ("Verify PM-KISAN Record", "Verify your land revenue records (Khatauni/ROR) on pmkisan.gov.in to obtain your DBT farmer ID."),
            ("Avail Concessional Kisan Credit Card", "Submit your PM-KISAN receipt at your bank for single-page KCC processing with 3% interest subvention."),
            ("Auto-Link PM Fasal Bima Yojana", "Enroll your cultivable area before the seasonal cutoff date for automated crop loss compensation.")
        ]
    }
}

MULTILINGUAL_TAXONOMY = {
    "hi": {
        "agriculture": {
            "stack_title": "🌾 एकीकृत किसान समृद्धि एवं सुरक्षा पैकेज",
            "rationale": "पीएम-किसान आय सहायता, किसान क्रेडिट कार्ड (KCC) और फसल बीमा योजना के साथ मिलकर किसान परिवारों को संपूर्ण वित्तीय सुरक्षा प्रदान करती है।",
            "default_impact": "₹6,000/वर्ष नकद DBT + ₹3,00,000 तक रियायती ऋण + व्यापक फसल बीमा",
            "seq": [
                ("पीएम-किसान रिकॉर्ड का सत्यापन", "pmkisan.gov.in पर अपने भूमि अभिलेख (खतौनी) का सत्यापन करें और अपनी किसान DBT आईडी प्राप्त करें।"),
                ("रियायती किसान क्रेडिट कार्ड (KCC)", "4% रियायती ब्याज दर पर कृषि ऋण हेतु बैंक शाखा में KCC आवेदन जमा करें।"),
                ("प्रधानमंत्री फसल बीमा योजना (PMFBY)", "प्राकृतिक आपदाओं से फसल सुरक्षा हेतु न्यूनतम प्रीमियम पर बीमा कराएं।")
            ]
        },
        "health": {
            "stack_title": "🏥 एकीकृत सार्वभौमिक स्वास्थ्य एवं औषधि सुरक्षा पैकेज",
            "rationale": "आयुष्मान भारत योजना के तहत मुफ्त अस्पताल उपचार जन औषधि केंद्रों की सस्ती जेनेरिक दवाओं के साथ मिलकर अधिकतम लाभ देता है।",
            "default_impact": "₹5,00,000 निःशुल्क अस्पताल उपचार + 50-90% सस्ती आवश्यक दवाएं",
            "seq": [
                ("आयुष्मान कार्ड / गोल्डन कार्ड बनवाएं", "निकटतम पैनलबद्ध अस्पताल में आयुष्मान मित्र डेस्क पर आधार कार्ड से गोल्डन कार्ड प्राप्त करें।"),
                ("सस्ती जेनेरिक दवाएं प्राप्त करें", "अपने नजदीकी प्रधानमंत्री जन औषधि केंद्र से 50-90% कम कीमत पर दवाएं खरीदें।"),
                ("मुख्यमंत्री राहत कोष सहायता", "गंभीर बीमारियों में ₹5 लाख से अधिक के उपचार हेतु राज्य स्वास्थ्य समिति में आवेदन करें।")
            ]
        },
        "education": {
            "stack_title": "🎓 विद्यार्थी उच्च शिक्षा एवं छात्रवृत्ति सहायता पैकेज",
            "rationale": "ट्यूशन फीस छूट, केंद्रीय रखरखाव छात्रवृत्ति और ब्याज-सब्सिडी वाले शिक्षा ऋण को बिना किसी नीतिगत टकराव के एक साथ लिया जा सकता है।",
            "default_impact": "पूर्ण पाठ्यक्रम शुल्क सहायता + रियायती शिक्षा ऋण",
            "seq": [
                ("राष्ट्रीय छात्रवृत्ति पोर्टल (NSP) पर आवेदन", "scholarships.gov.in पर वन-टाइम रजिस्ट्रेशन (OTR) कर आय प्रमाण पत्र जमा करें।"),
                ("पीएम विद्या लक्ष्मी पोर्टल पर ऋण आवेदन", "उच्च शिक्षा हेतु केंद्रीय ब्याज सब्सिडी (CSIS) के साथ शिक्षा ऋण आवेदन करें।"),
                ("संस्थान स्तर पर सत्यापन", "अंतिम तिथि से पहले अपने कॉलेज के नोडल अधिकारी से बोनाफाइड प्रमाणपत्र सत्यापित कराएं।")
            ]
        },
        "msme_business": {
            "stack_title": "💼 सूक्ष्म उद्यम एवं कार्यशील पूंजी सशक्तिकरण पैकेज",
            "rationale": "सूक्ष्म उद्यमी मार्जिन मनी अनुदान (PMEGP) और बिना गारंटी कार्यशील पूंजी ऋण (मुद्रा / पीएम स्वनिधि) को एक साथ प्राप्त कर सकते हैं।",
            "default_impact": "15-35% पूंजीगत सब्सिडी + गारंटी-मुक्त ऋण सुविधा",
            "seq": [
                ("उद्यम आधार ऑनलाइन पंजीकरण", "udyamregistration.gov.in पर मुफ्त और त्वरित उद्यम पंजीकरण प्राप्त करें।"),
                ("PMEGP मार्जिन मनी सब्सिडी आवेदन", "परियोजना लागत पर 35% तक सरकारी अनुदान प्राप्त करने हेतु KVIC पोर्टल पर आवेदन करें।"),
                ("मुद्रा कार्यशील पूंजी ऋण", "व्यापार विस्तार हेतु बैंक से शिशु/किशोर मुद्रा ऋण प्राप्त करें।")
            ]
        },
        "women_child": {
            "stack_title": "👩‍👧 व्यापक महिला एवं मातृत्व कल्याण पैकेज",
            "rationale": "मातृत्व पोषण सहायता (PMMVY) संस्थागत प्रसव (जननी सुरक्षा) और सुकन्या समृद्धि बालिका बचत के साथ मिलकर संपूर्ण सुरक्षा प्रदान करती है।",
            "default_impact": "प्रत्यक्ष DBT नकद सहायता + सुरक्षित बचत एवं स्वास्थ्य देखभाल",
            "seq": [
                ("मातृ एवं शिशु सुरक्षा कार्ड (MCP) पंजीकरण", "PMMVY किस्तों हेतु नजदीकी आंगनवाड़ी केंद्र या आशा कार्यकर्ता के पास पंजीकरण कराएं।"),
                ("संस्थागत प्रसव प्रोत्साहन", "सरकारी अस्पताल में सुरक्षित प्रसव कराकर जननी सुरक्षा योजना का नकद लाभ लें।"),
                ("सुकन्या समृद्धि खाता खोलें", "बालिका के नाम पर डाकघर या बैंक में उच्च ब्याज दर वाला बचत खाता खोलें।")
            ]
        },
        "senior_disability": {
            "stack_title": "🧓 वरिष्ठ नागरिक एवं दिव्यांगजन गरिमा व देखभाल पैकेज",
            "rationale": "आयुष्मान वय वंदना मुफ्त स्वास्थ्य कवर, सहायक उपकरण (राष्ट्रीय वयोश्री / ADIP) और मासिक सामाजिक सुरक्षा पेंशन एक साथ मिलती है।",
            "default_impact": "सार्वभौमिक निःशुल्क स्वास्थ्य कवर + सहायक उपकरण + मासिक पेंशन",
            "seq": [
                ("वय वंदना कार्ड / UDID प्राप्त करें", "आयुष्मान ऐप पर वरिष्ठ नागरिक स्वास्थ्य कार्ड और swavlambancard.gov.in पर UDID बनवाएं।"),
                ("मुफ्त सहायक उपकरण आवेदन", "पहिया कुर्सी, श्रवण यंत्र आदि हेतु जिला सामाजिक कल्याण शिविर में पंजीकरण कराएं।"),
                ("मासिक पेंशन हेतु नामांकन", "मासिक DBT पेंशन के लिए तहसील कार्यालय में आधार और बैंक विवरण जमा करें।")
            ]
        },
        "housing": {
            "stack_title": "🏡 एकीकृत ग्रामीण एवं शहरी आवास पैकेज",
            "rationale": "पीएम आवास आवंटन के साथ शौचालय निर्माण अनुदान और मुफ्त उज्ज्वला गैस कनेक्शन स्वतः प्राथमिकता पर उपलब्ध होते हैं।",
            "default_impact": "₹1,20,000 - ₹2,50,000 पक्का मकान सब्सिडी + शौचालय अनुदान + मुफ्त LPG",
            "seq": [
                ("PMAY जिओ-टैग्ड स्वीकृति", "पहली निर्माण किस्त हेतु ग्राम पंचायत / नगर निकाय से सत्यापन पूरा करें।"),
                ("स्वच्छ भारत शौचालय प्रोत्साहन", "प्लिंथ स्तर पर ₹12,000 का शौचालय अनुदान प्राप्त करें।"),
                ("पीएम उज्ज्वला गैस कनेक्शन", "आवास आवंटन पत्र दिखाकर मुफ्त गैस कनेक्शन प्राप्त करें।")
            ]
        }
    },
    "kn": {
        "agriculture": {
            "stack_title": "🌾 ಸಮಗ್ರ ರೈತ ಸಮೃದ್ಧಿ ಮತ್ತು ಬೆಳೆ ರಕ್ಷಣೆ ಪ್ಯಾಕೇಜ್",
            "rationale": "ಪಿಎಂ-ಕಿಸಾನ್ ಆರ್ಥಿಕ ನೆರವು, ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ ಮತ್ತು ಬೆಳೆ ವಿಮೆಯೊಂದಿಗೆ ಸಂಯೋಜನೆಗೊಂಡು ರೈತರಿಗೆ ಗರಿಷ್ಠ ಭದ್ರತೆ ನೀಡುತ್ತದೆ.",
            "default_impact": "₹6,000/ವರ್ಷ ನೇರ ನಗದು + ₹3,00,000 ವರೆಗೆ ಸಬ್ಸಿಡಿ ಕೃಷಿ ಸಾಲ + ಸಮಗ್ರ ಬೆಳೆ ವಿಮೆ",
            "seq": [
                ("ಪಿಎಂ-ಕಿಸಾನ್ ದಾಖಲೆ ಪರಿಶೀಲನೆ", "pmkisan.gov.in ನಲ್ಲಿ ನಿಮ್ಮ ಜಮೀನಿನ ಪಹಣಿ (RTC) ಪರಿಶೀಲಿಸಿ ನಿಮ್ಮ DBT ರೈತ ಐಡಿ ಪಡೆಯಿರಿ."),
                ("ಸಬ್ಸಿಡಿ ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC)", "ಶೇ 4 ರಿಯಾಯಿತಿ ಬಡ್ಡಿದರದಲ್ಲಿ ಕೃಷಿ ಸಾಲಕ್ಕಾಗಿ ಬ್ಯಾಂಕ್‌ನಲ್ಲಿ KCC ಅರ್ಜಿ ಸಲ್ಲಿಸಿ."),
                ("ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (PMFBY)", "ಬೆಳೆ ಹಾನಿಯ ನಷ್ಟ ತಡೆಗಟ್ಟಲು ಕನಿಷ್ಠ ಪ್ರೀಮಿಯಂ ಪಾವತಿಸಿ ನೋಂದಾಯಿಸಿ.")
            ]
        },
        "health": {
            "stack_title": "🏥 ಸಮಗ್ರ ಸಾರ್ವತ್ರಿಕ ಆರೋಗ್ಯ ಮತ್ತು ಔಷಧಿ ರಕ್ಷಣೆ ಪ್ಯಾಕೇಜ್",
            "rationale": "ಆಯುಷ್ಮಾನ್ ಭಾರತ್ ಯೋಜನೆಯಡಿ ಉಚಿತ ಆಸ್ಪತ್ರೆ ಚಿಕಿತ್ಸೆ ಜನೌಷಧಿ ಕೇಂದ್ರಗಳ ಕಡಿಮೆ ಬೆಲೆಯ ಔಷಧಿಗಳೊಂದಿಗೆ ಪೂರ್ಣ ರಕ್ಷಣೆ ನೀಡುತ್ತದೆ.",
            "default_impact": "₹5,00,000 ಉಚಿತ ಆಸ್ಪತ್ರೆ ಚಿಕಿತ್ಸೆ + 50-90% ಕಡಿಮೆ ಬೆಲೆಯ ಅಗತ್ಯ ಔಷಧಿಗಳು",
            "seq": [
                ("ಆಯುಷ್ಮಾನ್ ಕಾರ್ಡ್ ಪಡೆಯಿರಿ", "ಹತ್ತಿರದ ಸರ್ಕಾರಿ ಆಸ್ಪತ್ರೆಯಲ್ಲಿ ಆಯುಷ್ಮಾನ್ ಮಿತ್ರ ಸಹಾಯವಾಣಿಯಲ್ಲಿ ಆಧಾರ್ ನೀಡಿ ಗೋಲ್ಡನ್ ಕಾರ್ಡ್ ಪಡೆಯಿರಿ."),
                ("ಕಡಿಮೆ ಬೆಲೆಯ ಜನೌಷಧಿ ಔಷಧಿಗಳು", "ಹತ್ತಿರದ ಪ್ರಧಾನ ಮಂತ್ರಿ ಜನೌಷಧಿ ಕೇಂದ್ರದಿಂದ ರಿಯಾಯಿತಿ ದರದಲ್ಲಿ ಔಷಧಿಗಳನ್ನು ಪಡೆಯಿರಿ."),
                ("ಮುಖ್ಯಮಂತ್ರಿ ಪರಿಹಾರ ನಿಧಿ", "ಹೆಚ್ಚುವರಿ ವೈದ್ಯಕೀಯ ವೆಚ್ಚಗಳಿಗೆ ರಾಜ್ಯ ಆರೋಗ್ಯ ಇಲಾಖೆಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ.")
            ]
        },
        "education": {
            "stack_title": "🎓 ವಿದ್ಯಾರ್ಥಿ ಉನ್ನತ ಶಿಕ್ಷಣ ಮತ್ತು ವಿದ್ಯಾರ್ಥಿವೇತನ ಬೆಂಬಲ ಪ್ಯಾಕೇಜ್",
            "rationale": "ಬೋಧನಾ ಶುಲ್ಕ ಮನ್ನಾ, ನಿರ್ವಹಣಾ ವಿದ್ಯಾರ್ಥಿವೇತನ ಮತ್ತು ಸಬ್ಸಿಡಿ ಶಿಕ್ಷಣ ಸಾಲವನ್ನು ಯಾವುದೇ ನೀತಿ ಸಂಘರ್ಷವಿಲ್ಲದೆ ಪಡೆಯಬಹುದು.",
            "default_impact": "ಸಂಪೂರ್ಣ ಕೋರ್ಸ್ ಶುಲ್ಕ ಬೆಂಬಲ + ಸಬ್ಸಿಡಿ ಶಿಕ್ಷಣ ಸಾಲ",
            "seq": [
                ("ರಾಷ್ಟ್ರೀಯ ವಿದ್ಯಾರ್ಥಿವೇತನ ಪೋರ್ಟಲ್ (NSP) ಅರ್ಜಿ", "scholarships.gov.in ನಲ್ಲಿ ಒಟಿಆರ್ ನೋಂದಣಿ ಮಾಡಿ ಆದಾಯ ಪ್ರಮಾಣಪತ್ರ ಸಲ್ಲಿಸಿ."),
                ("ವಿದ್ಯಾ ಲಕ್ಷ್ಮಿ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಶಿಕ್ಷಣ ಸಾಲ", "ಕೇಂದ್ರ ಬಡ್ಡಿ ಸಬ್ಸಿಡಿಯೊಂದಿಗೆ ಶಿಕ್ಷಣ ಸಾಲಕ್ಕಾಗಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ."),
                ("ಕಾಲೇಜು ಮಟ್ಟದ ಪರಿಶೀಲನೆ", "ನಿಗದಿತ ದಿನಾಂಕದೊಳಗೆ ಕಾಲೇಜು ನೋಡಲ್ ಅಧಿಕಾರಿಯಿಂದ ದೃಢೀಕರಣ ಪೂರ್ಣಗೊಳಿಸಿ.")
            ]
        },
        "msme_business": {
            "stack_title": "💼 ಎಂಎಸ್ಎಂಇ ಉದ್ಯಮಶೀಲತೆ ಮತ್ತು ದುಡಿಯುವ ಬಂಡವಾಳ ಪ್ಯಾಕೇಜ್",
            "rationale": "ಉದ್ಯಮಿಗಳು ಬಂಡವಾಳ ಸಬ್ಸಿಡಿ (PMEGP) ಮತ್ತು ಶ್ಯೂರಿಟಿ ರಹಿತ ಮುದ್ರಾ ಸಾಲವನ್ನು ಒಟ್ಟಿಗೆ ಪಡೆದು ಉದ್ಯಮ ಬೆಳೆಸಬಹುದು.",
            "default_impact": "15-35% ಬಂಡವಾಳ ಸಬ್ಸಿಡಿ + ಗ್ಯಾರಂಟಿ ರಹಿತ ಸಾಲ ಸೌಲಭ್ಯ",
            "seq": [
                ("ಉದ್ಯಮ್ ಆಧಾರ್ ಆನ್‌ಲೈನ್ ನೋಂದಣಿ", "udyamregistration.gov.in ನಲ್ಲಿ ಉಚಿತ ಎಂಎಸ್ಎಂಇ ನೋಂದಣಿ ಪಡೆಯಿರಿ."),
                ("PMEGP ಮಾರ್ಜಿನ್ ಮನಿ ಸಬ್ಸಿಡಿ ಅರ್ಜಿ", "35% ವರೆಗೆ ಸರ್ಕಾರಿ ಅನುದಾನ ಪಡೆಯಲು ಕೆವಿಐಸಿ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ."),
                ("ಮುದ್ರಾ ದುಡಿಯುವ ಬಂಡವಾಳ ಸಾಲ", "ದಾಸ್ತಾನು ಮತ್ತು ನಿರ್ವಹಣೆಗೆ ಬ್ಯಾಂಕ್‌ನಿಂದ ಮುದ್ರಾ ಸಾಲ ಪಡೆಯಿರಿ.")
            ]
        },
        "women_child": {
            "stack_title": "👩‍👧 ಸಮಗ್ರ ಮಹಿಳಾ ಮತ್ತು ಮಾತೃ ಕಲ್ಯಾಣ ಪ್ಯಾಕೇಜ್",
            "rationale": "ಮಾತೃತ್ವ ಪೌಷ್ಟಿಕಾಂಶ ನೆರವು (PMMVY) ಸುರಕ್ಷಿತ ಹೆರಿಗೆ ಮತ್ತು ಸುಕನ್ಯಾ ಸಮೃದ್ಧಿ ಉಳಿತಾಯದೊಂದಿಗೆ ಮಹಿಳೆಯರಿಗೆ ಬಲ ನೀಡುತ್ತದೆ.",
            "default_impact": "ನೇರ ನಗದು ವರ್ಗಾವಣೆ + ಸುಭದ್ರ ಉಳಿತಾಯ ಮತ್ತು ಆರೋಗ್ಯ ರಕ್ಷಣೆ",
            "seq": [
                ("ತಾಯಿ ಮತ್ತು ಮಗು ಕಾರ್ಡ್ ನೋಂದಣಿ", "PMMVY ಕಂತುಗಳಿಗಾಗಿ ಸ್ಥಳೀಯ ಅಂಗನವಾಡಿ ಕೇಂದ್ರದಲ್ಲಿ ನೋಂದಾಯಿಸಿ."),
                ("ಸಂಸ್ಥಾಗತ ಹೆರಿಗೆ ಪ್ರೋತ್ಸಾಹಧನ", "ಸರ್ಕಾರಿ ಆಸ್ಪತ್ರೆಯಲ್ಲಿ ಉಚಿತ ಹೆರಿಗೆ ಮತ್ತು ಜನನಿ ಸುರಕ್ಷಾ ಯೋಜನೆಯ ಹಣ ಪಡೆಯಿರಿ."),
                ("ಸುಕನ್ಯಾ ಸಮೃದ್ಧಿ ಖಾತೆ ತೆರೆಯಿರಿ", "ಹೆಣ್ಣು ಮಗುವಿನ ಹೆಸರಿನಲ್ಲಿ ಅಂಚೆ ಕಚೇರಿಯಲ್ಲಿ ಗರಿಷ್ಠ ಬಡ್ಡಿಯ ಉಳಿತಾಯ ಖಾತೆ ತೆರೆಯಿರಿ.")
            ]
        },
        "senior_disability": {
            "stack_title": "🧓 ಹಿರಿಯ ನಾಗರಿಕರು ಮತ್ತು ದಿವ್ಯಾಂಗರ ಗೌರವ ರಕ್ಷಣೆ ಪ್ಯಾಕೇಜ್",
            "rationale": "ಆಯುಷ್ಮಾನ್ ವಯ ವಂದನಾ ಉಚಿತ ಆರೋಗ್ಯ ರಕ್ಷಣೆ, ಸಹಾಯಕ ಉಪಕರಣಗಳು ಮತ್ತು ಮಾಸಿಕ ಪಿಂಚಣಿ ಸೌಲಭ್ಯ ಒಟ್ಟಿಗೆ ಲಭ್ಯವಿದೆ.",
            "default_impact": "ಉಚಿತ ಆರೋಗ್ಯ ರಕ್ಷಣೆ + ಸಹಾಯಕ ಸಲಕರಣೆಗಳು + ಮಾಸಿಕ ಪಿಂಚಣಿ",
            "seq": [
                ("ವಯ ವಂದನಾ ಕಾರ್ಡ್ / UDID ಪಡೆಯಿರಿ", "ಆಯುಷ್ಮಾನ್ ಆಪ್ ಮೂಲಕ ಆರೋಗ್ಯ ಕಾರ್ಡ್ ಮತ್ತು swavlambancard.gov.in ನಲ್ಲಿ ಯುಡಿಐಡಿ ಕಾರ್ಡ್ ಪಡೆಯಿರಿ."),
                ("ಉಚಿತ ಸಹಾಯಕ ಸಲಕರಣೆ ಅರ್ಜಿ", "ಗಾಲಿಕುರ್ಚಿ, ಶ್ರವಣ ಸಾಧನಕ್ಕಾಗಿ ಜಿಲ್ಲಾ ಸಮಾಜ ಕಲ್ಯಾಣ ಶಿಬಿರದಲ್ಲಿ ನೋಂದಾಯಿಸಿ."),
                ("ಮಾಸಿಕ ಸಾಮಾಜಿಕ ಪಿಂಚಣಿ", "ಪ್ರತಿ ತಿಂಗಳ ಡಿಬಿಟಿ ಪಿಂಚಣಿಗಾಗಿ ತಾಲೂಕು ಕಚೇರಿಯಲ್ಲಿ ಬ್ಯಾಂಕ್ ವಿವರ ಸಲ್ಲಿಸಿ.")
            ]
        },
        "housing": {
            "stack_title": "🏡 ಸಮಗ್ರ ಗ್ರಾಮೀಣ ಮತ್ತು ನಗರ ವಸತಿ ಪ್ಯಾಕೇಜ್",
            "rationale": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಆವಾಸ್ ಯೋಜನೆಯಡಿ ಮನೆ ಮಂಜೂರಾತಿಯೊಂದಿಗೆ ಶೌಚಾಲಯ ನಿರ್ಮಾಣ ಧನಸಹಾಯ ಮತ್ತು ಉಚಿತ ಅನಿಲ ಸಂಪರ್ಕ ದೊರೆಯುತ್ತದೆ.",
            "default_impact": "₹1,20,000 - ₹2,50,000 ಮನೆ ಸಬ್ಸಿಡಿ + ಶೌಚಾಲಯ ಅನುದಾನ + ಉಚಿತ ಗ್ಯಾಸ್",
            "seq": [
                ("PMAY ಜಿಯೋ-ಟ್ಯಾಗ್ ಪರಿಶೀಲನೆ", "ಮೊದಲ ಕಂತಿನ ಹಣ ಬಿಡುಗಡೆಗೆ ಗ್ರಾಮ ಪಂಚಾಯತಿ ಪರಿಶೀಲನೆ ಪೂರ್ಣಗೊಳಿಸಿ."),
                ("ಸ್ವಚ್ಛ ಭಾರತ ಶೌಚಾಲಯ ಪ್ರೋತ್ಸಾಹಧನ", "ಶೌಚಾಲಯ ನಿರ್ಮಾಣಕ್ಕಾಗಿ ₹12,000 ಅನುದಾನ ಪಡೆಯಿರಿ."),
                ("ಪಿಎಂ ಉಜ್ವಲ ಗ್ಯಾಸ್ ಸಂಪರ್ಕ", "ಮನೆ ಮಂಜೂರಾತಿ ಪತ್ರ ತೋರಿಸಿ ಉಚಿತ ಎಲ್ಪಿಜಿ ಸಂಪರ್ಕ ಪಡೆಯಿರಿ.")
            ]
        }
    },
    "bn": {
        "agriculture": {
            "stack_title": "🌾 সুসংহত কৃষক সমৃদ্ধি ও সুরক্ষা প্যাকেজ",
            "rationale": "পিএম-কিষাণ সহায়তা কিষাণ ক্রেডিট কার্ড এবং ফসল বীমার সাথে সমন্বিত হয়ে সর্বোচ্চ আর্থিক সুরক্ষা নিশ্চিত করে।",
            "default_impact": "₹6,000/বছর সরাসরি DBT + ₹3,00,000 পর্যন্ত স্বল্প সুদে ঋণ + সম্পূর্ণ ফসল বীমা",
            "seq": [
                ("পিএম-কিষাণ রেকর্ড যাচাই", "pmkisan.gov.in পোর্টালে জমির খতিয়ান যাচাই করে আপনার কৃষক আইডি সংগ্রহ করুন।"),
                ("স্বল্প সুদে কিষাণ ক্রেডিট কার্ড (KCC)", "৪% হ্রাসকৃত সুদের হারে কৃষি ঋণের জন্য ব্যাংকে আবেদন জমা দিন।"),
                ("প্রধানমন্ত্রী ফসল বিমা যোজনা (PMFBY)", "ফসলের ক্ষতির ঝুঁকি এড়াতে ন্যূনতম প্রিমিয়ামে আবেদন করুন।")
            ]
        },
        "health": {
            "stack_title": "🏥 সার্বজনীন স্বাস্থ্য ও ওষুধ সুরক্ষা প্যাকেজ",
            "rationale": "আয়ুষ্মান ভারত প্রকল্পের অধীনে বিনামূল্যে হাসপাতালে চিকিৎসা এবং জন ঔষধি কেন্দ্রের সাশ্রয়ী ওষুধের সমন্বয়।",
            "default_impact": "₹৫,০০,০০০ বিনামূল্যে চিকিৎসা + ৫০-৯০% সাশ্রয়ী প্রয়োজনীয় ওষুধ",
            "seq": [
                ("আয়ুষ্মান গোল্ডেন কার্ড সংগ্রহ", "নিকটস্থ হাসপাতালে আয়ুষ্মান মিত্র ডেস্ক থেকে আধার দিয়ে গোল্ডেন কার্ড সংগ্রহ করুন।"),
                ("সাশ্রয়ী জেনেরিক ওষুধ", "জন ঔষধি কেন্দ্র থেকে হ্রাসকৃত মূল্যে প্রেসক্রিপশনের ওষুধ সংগ্রহ করুন।"),
                ("মুখ্যমন্ত্রী ত্রাণ তহবিল", "জটিল চিকিৎসার জন্য রাজ্য স্বাস্থ্য সংস্থায় আবেদন করুন।")
            ]
        },
        "education": {
            "stack_title": "🎓 শিক্ষার্থী উচ্চশিক্ষা ও বৃত্তি সহায়তা প্যাকেজ",
            "rationale": "টিউশন ফি মওকুফ, কেন্দ্রীয় রক্ষণাবেক্ষণ বৃত্তি এবং স্বল্প সুদে শিক্ষা ঋণ একসাথে গ্রহণ করা যায়।",
            "default_impact": "সম্পূর্ণ কোর্স ফি সহায়তা + স্বল্প সুদে শিক্ষা ঋণ",
            "seq": [
                ("জাতীয় স্কলারশিপ পোর্টাল (NSP) আবেদন", "scholarships.gov.in এ ওয়ান-টাইম রেজিস্ট্রেশন করে আয়ের শংসাপত্র জমা দিন।"),
                ("বিদ্যা লক্ষ্মী পোর্টালে ঋণ আবেদন", "কেন্দ্রীয় সুদ ভর্তুকির সাথে শিক্ষা ঋণের জন্য আবেদন করুন।"),
                ("কলেজ পর্যায়ে যাচাইকরণ", "নির্দিষ্ট সময়ের মধ্যে কলেজের নোডাল অফিসারের দ্বারা যাচাই সম্পন্ন করুন।")
            ]
        },
        "msme_business": {
            "stack_title": "💼 ক্ষুদ্র উদ্যোগ ও চলতি মূলধন সহায়তা প্যাকেজ",
            "rationale": "ক্ষুদ্র উদ্যোক্তারা মূলধন ভর্তুকি (PMEGP) এবং গ্যারান্টিবিহীন মুদ্রা ঋণ একসাথে পেতে পারেন।",
            "default_impact": "১৫-৩৫% মূলধন ভর্তুকি + জামানতবিহীন ঋণ সুবিধা",
            "seq": [
                ("উদ্যম আধার অনলাইন নিবন্ধন", "udyamregistration.gov.in এ বিনামূল্যে এমএসএমই নিবন্ধন সম্পন্ন করুন।"),
                ("PMEGP মার্জিন মানি আবেদন", "৩৫% পর্যন্ত সরকারি অনুদান পেতে কেভিআইসি পোর্টালে আবেদন করুন।"),
                ("মুদ্রা চলতি মূলধন ঋণ", "ব্যবসা পরিচালনার জন্য ব্যাংক থেকে মুদ্রা ঋণ গ্রহণ করুন।")
            ]
        },
        "women_child": {
            "stack_title": "👩‍👧 নারী ও মাতৃত্ব কল্যাণ সামগ্রিক প্যাকেজ",
            "rationale": "মাতৃত্বকালীন পুষ্টি সহায়তা (PMMVY), হাসপাতালে নিরাপদ প্রসব এবং সুকন্যা সমৃদ্ধি যোজনার সমন্বয়।",
            "default_impact": "সরাসরি ডিবিটি নগদ সহায়তা + সুরক্ষিত সঞ্চয় ও স্বাস্থ্যসেবা",
            "seq": [
                ("মা ও শিশু কার্ড নিবন্ধন", "স্থানীয় অঙ্গনওয়াড়ি কেন্দ্রে PMMVY কিস্তির জন্য নিবন্ধন করুন।"),
                ("হাসপাতালে প্রসবের প্রণোদনা", "সরকারি হাসপাতালে বিনামূল্যে প্রসব করিয়ে জননী সুরক্ষা যোজনার সুবিধা নিন।"),
                ("সুকন্যা সমৃদ্ধি অ্যাকাউন্ট খুলুন", "কন্যার নামে পোস্ট অফিসে সর্বোচ্চ সুদের সঞ্চয় অ্যাকাউন্ট খুলুন।")
            ]
        },
        "senior_disability": {
            "stack_title": "🧓 প্রবীণ নাগরিক ও দিব্যাঙ্গজন মর্যাদা সুরক্ষা প্যাকেজ",
            "rationale": "বিনামূল্যে স্বাস্থ্যসেবা, সহায়ক সরঞ্জাম (রাষ্ট্রীয় বয়োশ্রী / ADIP) এবং মাসিক পেনশনের সুবিধা।",
            "default_impact": "বিনামূল্যে চিকিৎসা কভার + সহায়ক সরঞ্জাম + মাসিক পেনশন",
            "seq": [
                ("বয় বন্দনা কার্ড / UDID তৈরি", "আয়ুষ্মান অ্যাপ ও swavlambancard.gov.in এ স্বাস্থ্য ও প্রতিবন্ধী কার্ড তৈরি করুন।"),
                ("সহায়ক সরঞ্জাম সংগ্রহ", "হুইলচেয়ার, শ্রবণযন্ত্রের জন্য জেলা সমাজকল্যাণ শিবিরে নাম নথিভুক্ত করুন।"),
                ("মাসিক ডিবিটি পেনশন", "মাসিক পেনশনের জন্য ব্লক অফিসে আধার ও ব্যাংক বিবরণ জমা দিন।")
            ]
        },
        "housing": {
            "stack_title": "🏡 গ্রামীণ ও নগর আবাসন প্যাকেজ",
            "rationale": "পাকা বাড়ি নির্মাণের আর্থিক অনুদান, শৌচাগার অনুদান এবং বিনামূল্যে রান্নার গ্যাস সংযোগ।",
            "default_impact": "₹১,২০,০০০ - ₹২,৫০,০০০ আবাসন ভর্তুকি + শৌচাগার অনুদান + ফ্রি গ্যাস",
            "seq": [
                ("PMAY জিও-ট্যাগ অনুমোদন", "নির্মাণ কিস্তির জন্য পঞ্চায়েত বা পুরসভা থেকে যাচাই করান।"),
                ("স্বচ্ছ ভারত শৌচাগার অনুদান", "শৌচাগার নির্মাণের জন্য ₹১২,০০০ অনুদান নিন।"),
                ("উজ্জ্বলা গ্যাস সংযোগ", "অনুমোদন পত্র দেখিয়ে বিনামূল্যে গ্যাস সংযোগ নিন।")
            ]
        }
    },
    "mr": {
        "agriculture": {
            "stack_title": "🌾 एकात्मिक शेतकरी समृद्धी आणि जोखीम सुरक्षा पॅकेज",
            "rationale": "पीएम-किसान उत्पन्न सहाय्य, किसान क्रेडिट कार्ड (KCC) आणि पीक विम्यासोबत एकत्र येऊन शेतकऱ्यांचे उत्पन्न वाढवते.",
            "default_impact": "₹६,०००/वर्ष थेट बँक खात्यात + ₹३,००,००० पर्यंत सवलतीचे कर्ज + सर्वसमावेशक पीक विमा",
            "seq": [
                ("पीएम-किसान नोंदणी पडताळणी", "pmkisan.gov.in वर तुमच्या 7/12 आणि 8A नोंदी तपासून DBT शेतकरी ओळखपत्र मिळवा."),
                ("सवलतीचे किसान क्रेडिट कार्ड (KCC)", "४% व्याजदरावर खेळत्या भांडवलासाठी जवळच्या बँक शाखेत अर्ज करा."),
                ("पंतप्रधान पीक विमा योजना (PMFBY)", "हंगामी पिकांच्या नुकसानीपासून संरक्षणासाठी वेळेत नोंदणी करा.")
            ]
        },
        "health": {
            "stack_title": "🏥 एकात्मिक सार्वत्रिक आरोग्य आणि औषध संरक्षण पॅकेज",
            "rationale": "आयुष्मान भारत मोफत रुग्णालय उपचार आणि जन औषधी केंद्रावरील स्वस्त जेनेरिक औषधांचा एकत्रित लाभ.",
            "default_impact": "₹५,००,००० मोफत रुग्णालय उपचार + ५०-९०% स्वस्त औषधे",
            "seq": [
                ("आयुष्मान कार्ड / गोल्डन कार्ड मिळवा", "जवळच्या रुग्णालयात आयुष्मान मित्राकडे आधार कार्ड देऊन गोल्डन कार्ड मिळवा."),
                ("स्वस्त जेनेरिक औषधे खरेदी करा", "पंतप्रधान जन औषधी केंद्रातून सवलतीच्या दरात औषधे मिळवा."),
                ("मुख्यमंत्री सहाय्यता निधी", "विशेष उपचारांसाठी राज्य आरोग्य समितीकडे अर्ज करा.")
            ]
        },
        "education": {
            "stack_title": "🎓 विद्यार्थी उच्च शिक्षण आणि शिष्यवृत्ती सहाय्य पॅकेज",
            "rationale": "ट्यूशन फी माफी, सरकारी निर्वाह भत्ता आणि सवलतीच्या दरातील शैक्षणिक कर्ज यांचा एकत्रित लाभ.",
            "default_impact": "संपूर्ण अभ्यासक्रम शुल्क सहाय्य + सवलतीचे शैक्षणिक कर्ज",
            "seq": [
                ("राष्ट्रीय शिष्यवृत्ती पोर्टल (NSP) अर्ज", "scholarships.gov.in वर नोंदणी करून उत्पन्नाचा दाखला जोडा."),
                ("विद्या लक्ष्मी पोर्टलवर कर्ज अर्ज", "व्याज सवलतीसह शैक्षणिक कर्जासाठी अर्ज करा."),
                ("महाविद्यालयीन पडताळणी", "मुदतीपूर्वी कॉलेजच्या नोडल अधिकाऱ्यांकडून पडताळणी पूर्ण करून घ्या.")
            ]
        },
        "msme_business": {
            "stack_title": "💼 एमएसएमई उद्योजकता आणि खेळते भांडवल पॅकेज",
            "rationale": "उद्योजक भांडवली अनुदान (PMEGP) आणि विनातारण मुद्रा कर्ज एकत्र घेऊन व्यवसाय वाढवू शकतात.",
            "default_impact": "१५-३५% भांडवली अनुदान + तारणमुक्त कर्ज हमी",
            "seq": [
                ("उद्यम आधार ऑनलाइन नोंदणी", "udyamregistration.gov.in वर मोफत एमएसएमई नोंदणी मिळवा."),
                ("PMEGP मार्जिन मनी अनुदान अर्ज", "३५% पर्यंत अनुदान मिळवण्यासाठी KVIC पोर्टलवर प्रकल्प सादर करा."),
                ("मुद्रा खेळते भांडवल कर्ज", "व्यवसाय विस्तारासाठी बँकेकडून मुद्रा कर्ज मिळवा.")
            ]
        },
        "women_child": {
            "stack_title": "👩‍👧 सर्वसमावेशक महिला व बाल संगोपन पॅकेज",
            "rationale": "मातृत्व पोषण सहाय्य (PMMVY), सुरक्षित प्रसूती प्रोत्साहन आणि सुकन्या समृद्धी योजनेचा एकत्रित लाभ.",
            "default_impact": "थेट डीबीटी रोख रक्कम + सुरक्षित बचत आणि आरोग्य सेवा",
            "seq": [
                ("माता आणि बाल संरक्षण कार्ड नोंदणी", "PMMVY हप्त्यांसाठी अंगणवाडी केंद्रात नोंदणी करा."),
                ("संस्थात्मक प्रसूती लाभ", "सरकारी रुग्णालयात मोफत प्रसूती करून जननी सुरक्षा योजनेचा लाभ घ्या."),
                ("सुकन्या समृद्धी खाते उघडा", "मुलीच्या नावे पोस्टात सर्वाधिक व्याज देणारे बचत खाते उघडा.")
            ]
        },
        "senior_disability": {
            "stack_title": "🧓 ज्येष्ठ नागरिक आणि दिव्यांग सन्मान पॅकेज",
            "rationale": "मोफत आरोग्य विमा, सहाय्यक उपकरणे (राष्ट्रीय वयोश्री / ADIP) आणि मासिक पेन्शनची सुरक्षा.",
            "default_impact": "मोफत आरोग्य कवच + सहाय्यक उपकरणे + मासिक पेन्शन",
            "seq": [
                ("वय वंदना कार्ड / UDID काढा", "आरोग्य कार्ड आणि swavlambancard.gov.in वर अपंगत्व कार्ड तयार करा."),
                ("मोफत सहाय्यक साधने मिळवा", "व्हीलचेअर, श्रवणयंत्रासाठी जिल्हा समाजकल्याण शिबिरात नाव नोंदवा."),
                ("मासिक डीबीटी पेन्शन", "दरमहा पेन्शनसाठी तहसील कार्यालयात बँक खाते जोडा.")
            ]
        },
        "housing": {
            "stack_title": "🏡 एकात्मिक ग्रामीण व शहरी घरकुल पॅकेज",
            "rationale": "घरकुल मंजुरीसोबत शौचालय अनुदान आणि मोफत उज्ज्वला गॅस कनेक्शन प्राधान्याने मिळते.",
            "default_impact": "₹१,२०,००० - ₹२,५०,००० घरकुल अनुदान + शौचालय अनुदान + मोफत गॅस",
            "seq": [
                ("PMAY जिओ-टॅगिंग मंजुरी", "अनुदानाचा हप्ता मिळवण्यासाठी ग्रामपंचायत किंवा पालिकेकडून तपासणी पूर्ण करा."),
                ("स्वच्छ भारत शौचालय अनुदान", "शौचालय बांधकामासाठी ₹१२,००० अनुदान मिळवा."),
                ("उज्ज्वला गॅस कनेक्शन", "घरकुल मंजुरी पत्र दाखवून मोफत गॅस मिळवा.")
            ]
        }
    },
    "ta": {
        "agriculture": {
            "stack_title": "🌾 ஒருங்கிணைந்த உழவர் முன்னேற்ற மற்றும் பயிர் பாதுகாப்பு தொகுப்பு",
            "rationale": "பிஎம்-கிசான் உதவித்தொகை, கிசான் கிரெடிட் கார்டு மற்றும் பயிர் காப்பீட்டுடன் இணைந்து அதிகபட்ச பலனை அளிக்கிறது.",
            "default_impact": "ஆண்டுக்கு ₹6,000 நேரடி உதவி + ₹3,00,000 வரை குறைந்த வட்டி கடன் + விரிவான பயிர் காப்பீடு",
            "seq": [
                ("பிஎம்-கிசான் பதிவை சரிபார்க்கவும்", "pmkisan.gov.in தளத்தில் நில வருவாய் ஆவணங்களை சரிபார்த்து உழவர் அடையாளத்தைப் பெறவும்."),
                ("குறைந்த வட்டி கிசான் கிரெடிட் கார்டு (KCC)", "4% சலுகை வட்டியில் விவசாய கடன் பெற வங்கியில் விண்ணப்பிக்கவும்."),
                ("பிரதம மந்திரி பயிர் காப்பீடு (PMFBY)", "பயிர் சேதத்திற்கு பாதுகாப்பளிக்க குறைந்த கட்டணத்தில் பதிவு செய்யவும்.")
            ]
        },
        "health": {
            "stack_title": "🏥 ஒருங்கிணைந்த மக்கள் நல்வாழ்வு மற்றும் மருத்துவ தொகுப்பு",
            "rationale": "ஆயுஷ்மான் பாரத் இலவச மருத்துவ சிகிச்சை மற்றும் மலிவு விலை மக்கள் மருந்தக மருந்துகளின் ஒருங்கிணைந்த பலன்.",
            "default_impact": "₹5,00,000 இலவச மருத்துவ சிகிச்சை + 50-90% வரை மலிவு மருந்துகள்",
            "seq": [
                ("ஆயுஷ்மான் அட்டை பெறவும்", "அருகிலுள்ள அரசு மருத்துவமனையில் ஆதார் வழங்கி ஆயுஷ்மான் அட்டை பெறவும்."),
                ("மலிவு விலை மருந்துகள்", "மக்கள் மருந்தக மையங்களில் குறைந்த விலையில் மருந்துகளை வாங்கவும்."),
                ("முதலமைச்சர் நிவாரண நிதி", "அதிநவீன மருத்துவ சிகிச்சைகளுக்கு கூடுதல் நிதி உதவி பெற விண்ணப்பிக்கவும்.")
            ]
        },
        "education": {
            "stack_title": "🎓 உயர்கல்வி மற்றும் கல்வி உதவித்தொகை தொகுப்பு",
            "rationale": "கல்விக் கட்டண விலக்கு, அரசு உதவித்தொகை மற்றும் குறைந்த வட்டி கல்விக் கடன் ஒருங்கிணைப்பு.",
            "default_impact": "முழுக் கல்விக் கட்டண ஆதரவு + சலுகை கல்விக் கடன்",
            "seq": [
                ("தேசிய உதவித்தொகை போர்டல் (NSP)", "scholarships.gov.in இல் பதிவு செய்து வருமானச் சான்றிதழைச் சமர்ப்பிக்கவும்."),
                ("வித்யா லட்சுமி கல்விக் கடன்", "வட்டி மானியத்துடன் கல்விக் கடன் பெற விண்ணப்பிக்கவும்."),
                ("கல்லூரி அளவிலான சரிபார்ப்பு", "கல்லூரி அலுவலர் மூலம் உரிய நேரத்தில் சான்றிதழைச் சரிபார்க்கவும்.")
            ]
        },
        "msme_business": {
            "stack_title": "💼 சிறுதொழில் முனைவோர் மூலதன உதவி தொகுப்பு",
            "rationale": "முதலீட்டு மானியம் (PMEGP) மற்றும் பிணையில்லா முத்ரா கடன் மூலம் தொழிலை விரிவுபடுத்தலாம்.",
            "default_impact": "15-35% மூலதன மானியம் + பிணையில்லா கடன் உத்தரவாதம்",
            "seq": [
                ("உத்யம் ஆதார் பதிவு", "udyamregistration.gov.in இல் இலவசமாக பதிவு செய்யவும்."),
                ("PMEGP மூலதன மானிய விண்ணப்பம்", "35% வரை மானியம் பெற கே.வி.ஐ.சி தளத்தில் திட்டத்தை சமர்ப்பிக்கவும்."),
                ("முத்ரா தொழில் கடன்", "தொழில் மூலதனத்திற்காக வங்கியில் முத்ரா கடன் பெறவும்.")
            ]
        },
        "women_child": {
            "stack_title": "👩‍👧 பெண்கள் மற்றும் மகப்பேறு நல பாதுகாப்பு தொகுப்பு",
            "rationale": "மகப்பேறு ஊட்டச்சத்து உதவி (PMMVY), இலவச பிரசவம் மற்றும் செல்வமகள் சேமிப்பு திட்டம்.",
            "default_impact": "நேரடி வங்கி நிதி உதவி + பாதுகாப்பான சேமிப்பு மற்றும் நல்வாழ்வு",
            "seq": [
                ("தாய் சேய் நல அட்டை பதிவு", "PMMVY தவணைகளுக்கு அங்கன்வாடி மையத்தில் பதிவு செய்யவும்."),
                ("அரசு பிரசவ நிதி நன்மை", "அரசு மருத்துவமனையில் இலவச பிரசவம் மற்றும் ஜனனி சுரக்ஷா உதவி பெறவும்."),
                ("செல்வமகள் சேமிப்புக் கணக்கு", "பெண் குழந்தையின் எதிர்காலத்திற்கு தபால் நிலையத்தில் சேமிப்புக் கணக்கு தொடங்கவும்.")
            ]
        },
        "senior_disability": {
            "stack_title": "🧓 முதியோர் மற்றும் மாற்றுத்திறனாளிகள் நலத் தொகுப்பு",
            "rationale": "இலவச மருத்துவக் காப்பீடு, உதவி உபகரணங்கள் மற்றும் மாதாந்திர ஓய்வூதியம்.",
            "default_impact": "இலவச மருத்துவ சிகிச்சை + உதவி உபகரணங்கள் + மாதாந்திர ஓய்வூதியம்",
            "seq": [
                ("வய வந்தனா / UDID அட்டை பெறவும்", "ஆயுஷ்மான் செயலி மற்றும் swavlambancard.gov.in இல் அட்டை பெறவும்."),
                ("இலவச உதவி உபகரணங்கள்", "சக்கர நாற்காலி, காதொலி கருவி பெற சமூக நல முகாமில் பதியவும்."),
                ("மாதாந்திர ஓய்வூதியம்", "வங்கி கணக்கில் நேரடி ஓய்வூதியம் பெற வட்டாட்சியர் அலுவலகத்தை அணுகவும்.")
            ]
        },
        "housing": {
            "stack_title": "🏡 கிராமப்புற மற்றும் நகர்ப்புற வீட்டு வசதி தொகுப்பு",
            "rationale": "வீட்டு மானியம், கழிப்பறை கட்டுமான உதவி மற்றும் இலவச எரிவாயு இணைப்பு.",
            "default_impact": "₹1,20,000 - ₹2,50,000 வீட்டு மானியம் + கழிப்பறை மானியம் + இலவச LPG",
            "seq": [
                ("PMAY நில அளவீட்டு ஒப்புதல்", "கட்டுமான தவணை பெற உள்ளாட்சி அமைப்பின் சரிபார்ப்பை முடிக்கவும்."),
                ("கழிப்பறை கட்டுமான நிதி", "தூய்மை இந்தியா திட்டத்தின் கீழ் ₹12,000 மானியம் பெறவும்."),
                ("உஜ்வாலா இலவச எரிவாயு", "ஒப்புதல் கடிதத்தை சமர்ப்பித்து இலவச சிலிண்டர் இணைப்பு பெறவும்.")
            ]
        }
    },
    "te": {
        "agriculture": {
            "stack_title": "🌾 సమగ్ర రైతు సంక్షేమ మరియు పంట రక్షణ ప్యాకేజీ",
            "rationale": "పీఎం-కిసాన్ ఆదాయ సహాయం కిసాన్ క్రెడిట్ కార్డ్ మరియు పంట బీమాతో కలిసి రైతులకు పూర్తి రక్షణ కల్పిస్తుంది.",
            "default_impact": "ఏడాదికి ₹6,000 ప్రత్యక్ష నగదు + ₹3,00,000 వరకు రాయితీ రుణం + సమగ్ర పంటల బీమా",
            "seq": [
                ("పీఎం-కిసాన్ రికార్డును ధృవీకరించండి", "pmkisan.gov.in లో భూమి రికార్డులను తనిఖీ చేసి రైతు గుర్తింపు పొందండి."),
                ("రాయితీ కిసాన్ క్రెడిట్ కార్డ్ (KCC)", "4% రాయితీ వడ్డీ రేటుతో వ్యవసాయ రుణం కోసం బ్యాంకులో దరఖాస్తు చేయండి."),
                ("ప్రధాన మంత్రి ఫసల్ బీమా యోజన (PMFBY)", "పంట నష్ట భద్రత కోసం నామమాత్రపు ప్రీమియంతో నమోదు చేసుకోండి.")
            ]
        },
        "health": {
            "stack_title": "🏥 సమగ్ర సార్వత్రిక ఆరోగ్య మరియు ఔషధ రక్షణ ప్యాకేజీ",
            "rationale": "ఆయుష్మాన్ భారత్ ఉచిత ఆసుపత్రి చికిత్స మరియు జన ఔషధి కేంద్రాల సరసమైన మందుల కలయిక.",
            "default_impact": "₹5,00,000 ఉచిత వైద్య చికిత్స + 50-90% చౌక మందులు",
            "seq": [
                ("ఆయుష్మాన్ కార్డు పొందండి", "సమీప ఆసుపత్రిలో ఆధార్ అందించి గోల్డెన్ కార్డు పొందండి."),
                ("సరసమైన ధరలో మందులు", "ప్రధాన మంత్రి జన ఔషధి కేంద్రం నుండి రాయితీతో మందులు పొందండి."),
                ("ముఖ్యమంత్రి సహాయ నిధి", "అదనపు వైద్య ఖర్చుల కోసం రాష్ట్ర ఆరోగ్య కమిటీకి దరఖాస్తు చేయండి.")
            ]
        },
        "education": {
            "stack_title": "🎓 విద్యార్థి ఉన్నత విద్య మరియు ఉపకార వేతన ప్యాకేజీ",
            "rationale": "ట్యూషన్ ఫీజు రీయింబర్స్‌మెంట్, నిర్వహణ భత్యం మరియు రాయితీ విద్యారుణాలు ఏకకాలంలో పొందవచ్చు.",
            "default_impact": "పూర్తి కోర్సు ఫీజు సహాయం + రాయితీ విద్యారుణం",
            "seq": [
                ("జాతీయ స్కాలర్‌షిప్ పోర్టల్ (NSP) దరఖాస్తు", "scholarships.gov.in లో నమోదు చేసి ఆదాయ ధృవీకరణ పత్రం సమర్పించండి."),
                ("విద్యా లక్ష్మి పోర్టల్ విద్యారుణం", "కేంద్ర వడ్డీ రాయితీతో విద్యారుణం కోసం దరఖాస్తు చేయండి."),
                ("కళాశాల స్థాయి ధృవీకరణ", "గడువులోగా కళాశాల నోడల్ అధికారి ద్వారా ధృవీకరణ పూర్తి చేయండి.")
            ]
        },
        "msme_business": {
            "stack_title": "💼 ఎంఎస్ఎంఈ వ్యవస్థాపకత మరియు వర్కింగ్ క్యాపిటల్ ప్యాకేజీ",
            "rationale": "మూలధన రాయితీ (PMEGP) మరియు పూచీకత్తు లేని ముద్రా రుణాన్ని కలిపి వ్యాపారాన్ని విస్తరించవచ్చు.",
            "default_impact": "15-35% మూలధన సబ్సిడీ + గ్యారెంటీ లేని రుణ సదుపాయం",
            "seq": [
                ("ఉద్యమ్ ఆధార్ ఆన్‌లైన్ రిజిస్ట్రేషన్", "udyamregistration.gov.in లో ఉచితంగా ఎంఎస్ఎంఈ నమోదు పొందండి."),
                ("PMEGP మార్జిన్ మనీ సబ్సిడీ", "35% వరకు ప్రభుత్వ రాయితీ కోసం కేవీఐసీ పోర్టల్‌లో దరఖాస్తు చేయండి."),
                ("ముద్రా వర్కింగ్ క్యాపిటల్ రుణం", "వ్యాపార నిర్వహణకు బ్యాంకు నుండి ముద్రా రుణం పొందండి.")
            ]
        },
        "women_child": {
            "stack_title": "👩‍👧 మహిళా మరియు శిశు సంక్షేమ ప్యాకేజీ",
            "rationale": "మాతృత్వ పోషకాహార సహాయం (PMMVY), సురక్షిత ప్రసవం మరియు సుకన్య సమృద్ధి సేవింగ్స్.",
            "default_impact": "ప్రత్యక్ష నగదు బదిలీ + సురక్షిత పొదుపు మరియు వైద్య రక్షణ",
            "seq": [
                ("తల్లీ బిడ్డ కార్డు నమోదు", "స్థానిక అంగన్‌వాడీ కేంద్రంలో PMMVY వాయిదాల కోసం నమోదు చేసుకోండి."),
                ("ఆసుపత్రి ప్రసవ ప్రోత్సాహకం", "ప్రభుత్వ ఆసుపత్రిలో ఉచిత ప్రసవం చేయించుకుని జననీ సురక్ష ప్రయోజనం పొందండి."),
                ("సుకన్య సమృద్ధి ఖాతా", "పోస్టాఫీసులో ఆడపిల్ల పేరున అత్యధిక వడ్డీతో పొదుపు ఖాతా తెరవండి.")
            ]
        },
        "senior_disability": {
            "stack_title": "🧓 వయోవృద్ధులు మరియు దివ్యాంగుల సంరక్షణ ప్యాకేజీ",
            "rationale": "ఉచిత ఆరోగ్య బీమా, సహాయక ఉపకరణాలు మరియు నెలవారీ పెన్షన్ రక్షణ.",
            "default_impact": "ఉచిత వైద్య రక్షణ + సహాయక పరికరాలు + నెలవారీ పెన్షన్",
            "seq": [
                ("వయ వందన / UDID కార్డు", "ఆయుష్మాన్ యాప్ మరియు swavlambancard.gov.in లో కార్డు పొందండి."),
                ("ఉచిత సహాయక పరికరాలు", "వీల్ చైర్, వినికిడి యంత్రాల కోసం సంక్షేమ శిబిరంలో నమోదు చేయండి."),
                ("నెలవారీ సామాజిక పింఛను", "నెలవారీ పెన్షన్ కోసం తహశీల్దార్ కార్యాలయంలో బ్యాంక్ వివరాలు సమర్పించండి.")
            ]
        },
        "housing": {
            "stack_title": "🏡 సమగ్ర గ్రామీణ మరియు పట్టణ గృహ నిర్మాణ ప్యాకేజీ",
            "rationale": "గృహ సబ్సిడీ, మరుగుదొడ్డి నిర్మాణ నిధులు మరియు ఉచిత గ్యాస్ కనెక్షన్ కలయిక.",
            "default_impact": "₹1,20,000 - ₹2,50,000 గృహ రాయితీ + మరుగుదొడ్డి నిధులు + ఉచిత గ్యాస్",
            "seq": [
                ("PMAY జియో-ట్యాగ్ ఆమోదం", "నిర్మాణ నిధుల కోసం పంచాయతీ లేదా మున్సిపల్ తనిఖీని పూర్తి చేయండి."),
                ("స్వచ్ఛ భారత్ మరుగుదొడ్డి గ్రాంట్", "మరుగుదొడ్డి నిర్మాణం కోసం ₹12,000 నిధులు పొందండి."),
                ("ఉజ్వల ఉచిత గ్యాస్ కనెక్షన్", "మంజూరు పత్రం చూపి ఉచిత ఎల్పీజీ కనెక్షన్ పొందండి.")
            ]
        }
    },
    "gu": {
        "agriculture": {
            "stack_title": "🌾 સંકલિત ખેડૂત સમૃદ્ધિ અને જોખમ રક્ષણ પેકેજ",
            "rationale": "પીએમ-કિસાન આવક સહાય કિસાન ક્રેડિટ કાર્ડ અને પાક વીમા સાથે મળીને ખેડૂતોને સર્વાંગી રક્ષણ આપે છે.",
            "default_impact": "વાર્ષિક ₹6,000 સીધી રોકડ + ₹3,00,000 સુધી સબસિડીવાળી લોન + વ્યાપક પાક વીમો",
            "seq": [
                ("પીએમ-કિસાન રેકોર્ડ ચકાસો", "pmkisan.gov.in પર જમીન રેકોર્ડ (૭/૧૨) ચકાસીને ખેડૂત આઈડી મેળવો."),
                ("સબસિડીવાળું કિસાન ક્રેડિટ કાર્ડ (KCC)", "૪% ના રાહત વ્યાજદરે કૃષિ લોન માટે બેંક શાખામાં અરજી કરો."),
                ("પ્રધાનમંત્રી ફસલ બીમા યોજના (PMFBY)", "પાકના નુકસાન સામે સુરક્ષા માટે લઘુત્તમ પ્રીમિયમ ભરીને નોંધણી કરાવો.")
            ]
        },
        "health": {
            "stack_title": "🏥 સર્વગ્રાહી આરોગ્ય અને દવા સુરક્ષા પેકેજ",
            "rationale": "આયુષ્માન ભારત યોજના હેઠળ મફત હોસ્પિટલ સારવાર અને જન ઔષધિ કેન્દ્રની સસ્તી જેનરિક દવાઓનો સંયુક્ત લાભ.",
            "default_impact": "₹૫,૦૦,૦૦૦ સુધી મફત સારવાર + ૫૦-૯૦% સસ્તી દવાઓ",
            "seq": [
                ("આયુષ્માન ગોલ્ડન કાર્ડ મેળવો", "નજીકની હોસ્પિટલમાં આધાર કાર્ડ આપીને ગોલ્ડન કાર્ડ કઢાવો."),
                ("સસ્તી જેનરિક દવાઓ મેળવો", "પ્રધાનમંત્રી જન ઔષધિ કેન્દ્ર પરથી રાહત દરે દવાઓ ખરીદો."),
                ("મુખ્યમંત્રી રાહત નિધિ", "જટિલ સારવાર માટે રાજ્ય આરોગ્ય સમિતિમાં અરજી કરો.")
            ]
        },
        "education": {
            "stack_title": "🎓 વિદ્યાર્થી ઉચ્ચ શિક્ષણ અને શિષ્યવૃત્તિ સહાય પેકેજ",
            "rationale": "ટ્યુશન ફી માફી, નિર્વાહ ભથ્થું અને સબસિડીવાળી એજ્યુકેશન લોનનો કોઈ પણ સંઘર્ષ વગર એકસાથે લાભ.",
            "default_impact": "સંપૂર્ણ કોર્સ ફી સહાય + રાહત દરે એજ્યુકેશન લોન",
            "seq": [
                ("રાષ્ટ્રીય સ્કોલરશીપ પોર્ટલ (NSP) અરજી", "scholarships.gov.in પર રજીસ્ટ્રેશન કરી આવક પ્રમાણપત્ર જોડો."),
                ("વિદ્યા લક્ષ્મી પોર્ટલ પર લોન અરજી", "વ્યાજ સબસિડી સાથે શિક્ષણ લોન માટે અરજી કરો."),
                ("કોલેજ કક્ષાએ ચકાસણી", "નિયત સમયમાં કોલેજના નોડલ અધિકારી દ્વારા પ્રમાણપત્ર ચકાસણી કરાવો.")
            ]
        },
        "msme_business": {
            "stack_title": "💼 એમએસએમઈ ઉદ્યોગસાહસિકતા અને કાર્યકારી મૂડી પેકેજ",
            "rationale": "મૂડી સબસિડી (PMEGP) અને ગેરંટી વિનાની મુદ્રા લોન એકસાથે મેળવીને વેપારનો વિસ્તાર કરી શકાય છે.",
            "default_impact": "૧૫-૩૫% મૂડી સબસિડી + તારણમુક્ત લોન ગેરંટી",
            "seq": [
                ("ઉદ્યમ આધાર ઓનલાઇન નોંધણી", "udyamregistration.gov.in પર મફત એમએસએમઈ નોંધણી મેળવો."),
                ("PMEGP માર્જિન મની સબસિડી", "૩૫% સુધીની સરકારી ગ્રાન્ટ માટે કેવીઆઈસી પોર્ટલ પર અરજી કરો."),
                ("મુદ્રા કાર્યકારી મૂડી લોન", "વેપારના સંચાલન માટે બેંકમાંથી મુદ્રા લોન મેળવો.")
            ]
        },
        "women_child": {
            "stack_title": "👩‍👧 મહિલા અને માતૃત્વ કલ્યાણ સંરક્ષણ પેકેજ",
            "rationale": "માતૃત્વ પોષણ સહાય (PMMVY), સંસ્થાકીય પ્રસૂતિ અને સુકન્યા સમૃદ્ધિ બચતનો સર્વાંગી લાભ.",
            "default_impact": "સીધી ડીબીટી રોકડ સહાય + સુરક્ષિત બચત અને આરોગ્ય સંભાળ",
            "seq": [
                ("મમતા કાર્ડ નોંધણી", "PMMVY સહાય માટે આંગણવાડી કેન્દ્રમાં નોંધણી કરાવો."),
                ("હોસ્પિટલ પ્રસૂતિ પ્રોત્સાહન", "સરકારી હોસ્પિટલમાં મફત પ્રસૂતિ કરાવી જનની સુરક્ષા યોજનાનો લાભ લો."),
                ("સુકન્યા સમૃદ્ધિ ખાતું ખોલાવો", "દીકરીના નામે પોસ્ટ ઓફિસમાં સૌથી વધુ વ્યાજ ધરાવતું ખાતું ખોલાવો.")
            ]
        },
        "senior_disability": {
            "stack_title": "🧓 વરિષ્ઠ નાગરિક અને દિવ્યાંગજન સન્માન પેકેજ",
            "rationale": "મફત આરોગ્ય કવચ, સહાયક સાધનો (રાષ્ટ્રીય વયોશ્રી / ADIP) અને માસિક પેન્શન સુરક્ષા.",
            "default_impact": "મફત સારવાર કવચ + સહાયક સાધનો + માસિક પેન્શન",
            "seq": [
                ("વય વંદના કાર્ડ / UDID કઢાવો", "આયુષ્માન એપ અને swavlambancard.gov.in પર કાર્ડ મેળવો."),
                ("મફત સહાયક સાધન અરજી", "વ્હીલચેયર, શ્રવણયંત્ર માટે સમાજ કલ્યાણ કેમ્પમાં નોંધણી કરાવો."),
                ("માસિક ડીબીટી પેન્શન", "દર મહિને પેન્શન મેળવવા તાલુકા કચેરીમાં બેંક વિગતો સબમિટ કરો.")
            ]
        },
        "housing": {
            "stack_title": "🏡 સંકલિત ગ્રામીણ અને શહેરી આવાસ પેકેજ",
            "rationale": "આવાસ સહાય, શૌચાલય નિર્માણ ગ્રાન્ટ અને મફત ઉજ્જવલા ગેસ કનેક્શન.",
            "default_impact": "₹૧,૨૦,૦૦૦ - ₹૨,૫૦,૦૦૦ આવાસ સબસિડી + શૌચાલય સહાય + મફત LPG",
            "seq": [
                ("PMAY જીઓ-ટેગ મંજૂરી", "બાંધકામ હપ્તા માટે ગ્રામ પંચાયત અથવા નગરપાલિકા દ્વારા ચકાસણી પૂર્ણ કરો."),
                ("સ્વચ્છ ભારત શૌચાલય ગ્રાન્ટ", "શૌચાલય બનાવવા માટે ₹૧૨,૦૦૦ સહાય મેળવો."),
                ("ઉજ્જવલા ગેસ કનેક્શન", "આવાસ મંજૂરી પત્ર બતાવીને મફત ગેસ કનેક્શન મેળવો.")
            ]
        }
    },
    "pa": {
        "agriculture": {
            "stack_title": "🌾 ਏਕੀਕ੍ਰਿਤ ਕਿਸਾਨ ਖੁਸ਼ਹਾਲੀ ਅਤੇ ਜੋਖਮ ਸੁਰੱਖਿਆ ਪੈਕੇਜ",
            "rationale": "ਪੀਐਮ-ਕਿਸਾਨ ਸਹਾਇਤਾ ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ (KCC) ਅਤੇ ਫਸਲ ਬੀਮੇ ਨਾਲ ਮਿਲ ਕੇ ਕਿਸਾਨਾਂ ਨੂੰ ਪੂਰੀ ਸੁਰੱਖਿਆ ਪ੍ਰਦਾਨ ਕਰਦੀ ਹੈ।",
            "default_impact": "₹6,000/ਸਾਲ ਸਿੱਧੀ ਨਕਦੀ + ₹3,00,000 ਤੱਕ ਰਿਆਇਤੀ ਕਰਜ਼ਾ + ਪੂਰਾ ਫਸਲ ਬੀਮਾ",
            "seq": [
                ("ਪੀਐਮ-ਕਿਸਾਨ ਰਿਕਾਰਡ ਦੀ ਜਾਂਚ", "pmkisan.gov.in 'ਤੇ ਆਪਣੇ ਜ਼ਮੀਨੀ ਰਿਕਾਰਡ ਦੀ ਪੁਸ਼ਟੀ ਕਰੋ ਅਤੇ ਕਿਸਾਨ ਆਈਡੀ ਪ੍ਰਾਪਤ ਕਰੋ।"),
                ("ਰਿਆਇਤੀ ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ (KCC)", "4% ਰਿਆਇਤੀ ਵਿਆਜ ਦਰ 'ਤੇ ਕਰਜ਼ੇ ਲਈ ਬੈਂਕ ਸ਼ਾਖਾ ਵਿੱਚ ਅਰਜ਼ੀ ਦਿਓ।"),
                ("ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਫਸਲ ਬੀਮਾ ਯੋਜਨਾ (PMFBY)", "ਫਸਲਾਂ ਦੇ ਨੁਕਸਾਨ ਤੋਂ ਬਚਾਅ ਲਈ ਘੱਟੋ-ਘੱਟ ਪ੍ਰੀਮੀਅਮ 'ਤੇ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਕਰੋ।")
            ]
        },
        "health": {
            "stack_title": "🏥 ਏਕੀਕ੍ਰਿਤ ਸਿਹਤ ਅਤੇ ਦਵਾਈ ਸੁਰੱਖਿਆ ਪੈਕੇਜ",
            "rationale": "ਆਯੂਸ਼ਮਾਨ ਭਾਰਤ ਤਹਿਤ ਮੁਫਤ ਹਸਪਤਾਲ ਇਲਾਜ ਅਤੇ ਜਨ ਔਸ਼ਧੀ ਕੇਂਦਰਾਂ ਤੋਂ ਸਸਤੀਆਂ ਦਵਾਈਆਂ ਦਾ ਸੰਯੁਕਤ ਲਾਭ।",
            "default_impact": "₹5,00,000 ਮੁਫ਼ਤ ਇਲਾਜ + 50-90% ਸਸਤੀਆਂ ਜ਼ਰੂਰੀ ਦਵਾਈਆਂ",
            "seq": [
                ("ਆਯੂਸ਼ਮਾਨ ਕਾਰਡ ਪ੍ਰਾਪਤ ਕਰੋ", "ਨੇੜਲੇ ਹਸਪਤਾਲ ਵਿੱਚ ਆਧਾਰ ਕਾਰਡ ਦਿਖਾ ਕੇ ਗੋਲਡਨ ਕਾਰਡ ਬਣਵਾਓ।"),
                ("ਸਸਤੀਆਂ ਜੈਨੇਰਿਕ ਦਵਾਈਆਂ", "ਜਨ ਔਸ਼ਧੀ ਕੇਂਦਰ ਤੋਂ ਰਿਆਇਤੀ ਦਰਾਂ 'ਤੇ ਦਵਾਈਆਂ ਪ੍ਰਾਪਤ ਕਰੋ।"),
                ("ਮੁੱਖ ਮੰਤਰੀ ਰਾਹਤ ਫੰਡ", "ਵੱਡੇ ਆਪ੍ਰੇਸ਼ਨਾਂ ਲਈ ਵਾਧੂ ਸਹਾਇਤਾ ਵਾਸਤੇ ਅਰਜ਼ੀ ਦਿਓ।")
            ]
        },
        "education": {
            "stack_title": "🎓 ਵਿਦਿਆਰਥੀ ਉੱਚ ਸਿੱਖਿਆ ਅਤੇ ਵਜ਼ੀਫ਼ਾ ਸਹਾਇਤਾ ਪੈਕੇਜ",
            "rationale": "ਟਿਊਸ਼ਨ ਫੀਸ ਮੁਆਫੀ, ਰੱਖ-ਰਖਾਅ ਵਜ਼ੀਫ਼ਾ ਅਤੇ ਸਸਤਾ ਸਿੱਖਿਆ ਕਰਜ਼ਾ ਬਿਨਾਂ ਕਿਸੇ ਰੁਕਾਵਟ ਦੇ ਇਕੱਠੇ ਲਏ ਜਾ ਸਕਦੇ ਹਨ।",
            "default_impact": "ਪੂਰੀ ਕੋਰਸ ਫੀਸ ਸਹਾਇਤਾ + ਰਿਆਇਤੀ ਸਿੱਖਿਆ ਕਰਜ਼ਾ",
            "seq": [
                ("ਨੈਸ਼ਨਲ ਸਕਾਲਰਸ਼ਿਪ ਪੋਰਟਲ (NSP) ਅਰਜ਼ੀ", "scholarships.gov.in 'ਤੇ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਕਰਕੇ ਆਮਦਨ ਸਰਟੀਫਿਕੇਟ ਜਮ੍ਹਾਂ ਕਰੋ।"),
                ("ਵਿੱਦਿਆ ਲਕਸ਼ਮੀ ਸਿੱਖਿਆ ਕਰਜ਼ਾ", "ਸਰਕਾਰੀ ਵਿਆਜ ਸਬਸਿਡੀ ਨਾਲ ਸਿੱਖਿਆ ਕਰਜ਼ੇ ਲਈ ਅਰਜ਼ੀ ਦਿਓ।"),
                ("ਕਾਲਜ ਪੱਧਰੀ ਪੁਸ਼ਟੀ", "ਸਮੇਂ ਸਿਰ ਕਾਲਜ ਅਧਿਕਾਰੀ ਤੋਂ ਸਰਟੀਫਿਕੇਟ ਵੈਰੀਫਾਈ ਕਰਵਾਓ।")
            ]
        },
        "msme_business": {
            "stack_title": "💼 ਐਮਐਸਐਮਈ ਉੱਦਮਤਾ ਅਤੇ ਵਰਕਿੰਗ ਕੈਪੀਟਲ ਪੈਕੇਜ",
            "rationale": "ਪੂੰਜੀ ਸਬਸਿਡੀ (PMEGP) ਅਤੇ ਬਿਨਾਂ ਗਾਰੰਟੀ ਮੁਦਰਾ ਕਰਜ਼ਾ ਇਕੱਠੇ ਲੈ ਕੇ ਕਾਰੋਬਾਰ ਵਧਾਓ।",
            "default_impact": "15-35% ਪੂੰਜੀਗਤ ਸਬਸਿਡੀ + ਗਾਰੰਟੀ-ਮੁਕਤ ਕਰਜ਼ਾ",
            "seq": [
                ("ਉੱਦਮ ਆਧਾਰ ਆਨਲਾਈਨ ਰਜਿਸਟ੍ਰੇਸ਼ਨ", "udyamregistration.gov.in 'ਤੇ ਮੁਫਤ ਐਮਐਸਐਮਈ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਕਰੋ।"),
                ("PMEGP ਮਾਰਜਿਨ ਮਨੀ ਸਬਸਿਡੀ", "35% ਤੱਕ ਗ੍ਰਾਂਟ ਲਈ ਕੇਵੀਆਈਸੀ ਪੋਰਟਲ 'ਤੇ ਅਰਜ਼ੀ ਦਿਓ।"),
                ("ਮੁਦਰਾ ਵਰਕਿੰਗ ਕੈਪੀਟਲ ਲੋਨ", "ਵਪਾਰ ਚਲਾਉਣ ਲਈ ਬੈਂਕ ਤੋਂ ਮੁਦਰਾ ਲੋਨ ਲਓ।")
            ]
        },
        "women_child": {
            "stack_title": "👩‍👧 ਮਹਿਲਾ ਅਤੇ ਜਣੇਪਾ ਭਲਾਈ ਸੁਰੱਖਿਆ ਪੈਕੇਜ",
            "rationale": "ਜਣੇਪਾ ਪੋਸ਼ਣ ਸਹਾਇਤਾ (PMMVY), ਹਸਪਤਾਲ ਡਿਲੀਵਰੀ ਅਤੇ ਸੁਕੰਨਿਆ ਸਮ੍ਰਿਧੀ ਬੱਚਤ।",
            "default_impact": "ਸਿੱਧੀ ਡੀਬੀਟੀ ਨਕਦੀ + ਸੁਰੱਖਿਅਤ ਬੱਚਤ ਅਤੇ ਸਿਹਤ ਸੰਭਾਲ",
            "seq": [
                ("ਮਾਂ-ਬੱਚਾ ਕਾਰਡ ਰਜਿਸਟ੍ਰੇਸ਼ਨ", "PMMVY ਕਿਸ਼ਤਾਂ ਲਈ ਆਂਗਣਵਾੜੀ ਕੇਂਦਰ ਵਿੱਚ ਨਾਮ ਦਰਜ ਕਰਵਾਓ।"),
                ("ਹਸਪਤਾਲ ਜਣੇਪਾ ਲਾਭ", "ਸਰਕਾਰੀ ਹਸਪਤਾਲ ਵਿੱਚ ਮੁਫ਼ਤ ਜਣੇਪਾ ਕਰਵਾ ਕੇ ਜਨਨੀ ਸੁਰੱਖਿਆ ਯੋਜਨਾ ਦਾ ਲਾਭ ਲਓ।"),
                ("ਸੁਕੰਨਿਆ ਸਮ੍ਰਿਧੀ ਖਾਤਾ", "ਧੀ ਦੇ ਨਾਮ 'ਤੇ ਡਾਕਖਾਨੇ ਵਿੱਚ ਸਭ ਤੋਂ ਵੱਧ ਵਿਆਜ ਵਾਲਾ ਖਾਤਾ ਖੁਲ੍ਹਵਾਓ।")
            ]
        },
        "senior_disability": {
            "stack_title": "🧓 ਬਜ਼ੁਰਗ ਅਤੇ ਦਿਵਿਆਂਗਜਨ ਸਨਮਾਨ ਪੈਕੇਜ",
            "rationale": "ਮੁਫ਼ਤ ਸਿਹਤ ਕਵਰ, ਸਹਾਇਕ ਉਪਕਰਨ (ਰਾਸ਼ਟਰੀ ਵਯੋਸ਼੍ਰੀ / ADIP) ਅਤੇ ਮਹੀਨਾਵਾਰ ਪੈਨਸ਼ਨ।",
            "default_impact": "ਮੁਫ਼ਤ ਇਲਾਜ + ਸਹਾਇਕ ਉਪਕਰਨ + ਮਹੀਨਾਵਾਰ ਪੈਨਸ਼ਨ",
            "seq": [
                ("ਵਯ ਵੰਦਨਾ ਕਾਰਡ / UDID ਬਣਵਾਓ", "ਆਯੂਸ਼ਮਾਨ ਐਪ ਅਤੇ swavlambancard.gov.in 'ਤੇ ਕਾਰਡ ਬਣਵਾਓ।"),
                ("ਮੁਫ਼ਤ ਸਹਾਇਕ ਉਪਕਰਨ ਅਰਜ਼ੀ", "ਵ੍ਹੀਲਚੇਅਰ, ਸੁਣਨ ਵਾਲੀ ਮਸ਼ੀਨ ਲਈ ਸਮਾਜ ਭਲਾਈ ਕੈਂਪ ਵਿੱਚ ਰਜਿਸਟਰ ਕਰੋ।"),
                ("ਮਹੀਨਾਵਾਰ ਡੀਬੀਟੀ ਪੈਨਸ਼ਨ", "ਹਰ ਮਹੀਨੇ ਪੈਨਸ਼ਨ ਲਈ ਤਹਿਸੀਲ ਦਫ਼ਤਰ ਵਿੱਚ ਬੈਂਕ ਖਾਤਾ ਜਮ੍ਹਾਂ ਕਰੋ।")
            ]
        },
        "housing": {
            "stack_title": "🏡 ਏਕੀਕ੍ਰਿਤ ਪੇਂਡੂ ਅਤੇ ਸ਼ਹਿਰੀ ਆਵਾਸ ਪੈਕੇਜ",
            "rationale": "ਮਕਾਨ ਸਬਸਿਡੀ, ਪਖਾਨਾ ਨਿਰਮਾਣ ਗ੍ਰਾਂਟ ਅਤੇ ਮੁਫ਼ਤ ਉੱਜਵਲਾ ਗੈਸ ਕੁਨੈਕਸ਼ਨ।",
            "default_impact": "₹1,20,000 - ₹2,50,000 ਆਵਾਸ ਸਬਸਿਡੀ + ਪਖਾਨਾ ਗ੍ਰਾਂਟ + ਮੁਫ਼ਤ LPG",
            "seq": [
                ("PMAY ਜੀਓ-ਟੈਗ ਮਨਜ਼ੂਰੀ", "ਕਿਸ਼ਤ ਜਾਰੀ ਕਰਨ ਲਈ ਪੰਚਾਇਤ ਤੋਂ ਤਸਦੀਕ ਪੂਰੀ ਕਰਵਾਓ।"),
                ("ਸਵੱਛ ਭਾਰਤ ਪਖਾਨਾ ਗ੍ਰਾਂਟ", "ਪਖਾਨਾ ਬਣਾਉਣ ਲਈ ₹12,000 ਗ੍ਰਾਂਟ ਲਓ।"),
                ("ਉੱਜਵਲਾ ਗੈਸ ਕੁਨੈਕਸ਼ਨ", "ਮਕਾਨ ਮਨਜ਼ੂਰੀ ਪੱਤਰ ਦਿਖਾ ਕੇ ਮੁਫ਼ਤ ਗੈਸ ਕੁਨੈਕਸ਼ਨ ਲਓ।")
            ]
        }
    }
}


def get_localized_sector_meta(sector_key: str, target_lang: str) -> Dict[str, Any]:
    """Returns localized sector metadata for the target language, falling back to English."""
    base_meta = SECTOR_TAXONOMY.get(sector_key, SECTOR_TAXONOMY["health"])
    if target_lang == "en" or not target_lang:
        return base_meta
    
    lang_dict = MULTILINGUAL_TAXONOMY.get(target_lang, MULTILINGUAL_TAXONOMY.get("hi", {}))
    localized = lang_dict.get(sector_key)
    if localized:
        return {
            **base_meta,
            "stack_title": localized.get("stack_title", base_meta["stack_title"]),
            "rationale": localized.get("rationale", base_meta["rationale"]),
            "default_impact": localized.get("default_impact", base_meta["default_impact"]),
            "seq": localized.get("seq", base_meta["seq"]),
        }
    return base_meta


def _classify_scheme_domain(scheme: Dict[str, Any]) -> str:
    """Classifies a scheme into its primary policy sector."""
    text_corpus = " ".join([
        str(scheme.get("scheme_name", "")),
        str(scheme.get("name", "")),
        str(scheme.get("slug", "")),
        str(scheme.get("category", "")),
        str(scheme.get("brief", "")),
        str(scheme.get("repository_summary", ""))
    ]).casefold()

    for sector, meta in SECTOR_TAXONOMY.items():
        for kw in meta["keywords"]:
            if kw in text_corpus:
                return sector
    return "general_welfare"


class PolicyInteractionEngine:
    """
    Evaluates policy interactions, cross-scheme exclusions, and synergistic welfare stacks.
    Uses LLM-first dynamic analysis with a multi-sector deterministic fallback.
    """

    @classmethod
    def evaluate(
        cls,
        schemes: List[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]] = None,
        user_query: str = "",
        crawled_results: Optional[List[Dict[str, Any]]] = None,
        target_language: str = "en",
        language_name: str = "English",
    ) -> Dict[str, Any]:
        """
        Runs comprehensive policy evaluation across candidate schemes.
        """
        if not schemes:
            return {
                "welfare_stack": None,
                "cross_scheme_conflicts": [],
                "conflict_alert": None
            }

        profile = user_profile or {}

        # 1. Check for single-scheme source discrepancies (existing detector)
        source_conflict = SourceConflictDetector.detect_conflicts(
            user_query=user_query,
            extracted_schemes=schemes,
            crawled_results=crawled_results or []
        )

        # 2. Attempt LLM-First Dynamic Analysis
        llm_result = cls._evaluate_with_llm(
            schemes=schemes,
            user_profile=profile,
            user_query=user_query,
            target_language=target_language,
            language_name=language_name,
        )

        if llm_result:
            conflicts = []
            if source_conflict and source_conflict.get("has_conflict"):
                conflicts.append(source_conflict)

            if llm_result.get("has_conflict") and llm_result.get("conflict"):
                llm_conflict = llm_result["conflict"]
                llm_conflict["has_conflict"] = True
                llm_conflict["alert_type"] = "CROSS_SCHEME_MUTUAL_EXCLUSION"
                conflicts.append(llm_conflict)

            welfare_stack = llm_result.get("welfare_stack")
            primary_conflict = conflicts[0] if conflicts else None

            return {
                "welfare_stack": welfare_stack,
                "cross_scheme_conflicts": conflicts,
                "conflict_alert": primary_conflict
            }

        # Zero synthetic fallback when LLM policy reasoning is unavailable or rate-limited
        logger.warning("LLM policy evaluation unavailable or hit rate limit; zero synthetic fallback generated.")
        conflicts = [source_conflict] if source_conflict and source_conflict.get("has_conflict") else []
        return {
            "welfare_stack": None,
            "cross_scheme_conflicts": conflicts,
            "conflict_alert": conflicts[0] if conflicts else None
        }

    @classmethod
    def _evaluate_with_llm(
        cls,
        schemes: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        user_query: str,
        target_language: str = "en",
        language_name: str = "English",
    ) -> Optional[Dict[str, Any]]:
        """Invokes Groq LLM to dynamically reason about policy interactions."""
        if not llm_service.api_key:
            return None

        schemes_context = []
        for s in schemes[:6]:
            schemes_context.append({
                "name": s.get("scheme_name") or s.get("name", "Unknown Scheme"),
                "level": s.get("level") or s.get("jurisdiction", "Central"),
                "category": s.get("category", "General"),
                "benefit": s.get("benefit") or (s.get("benefits") and s["benefits"][0]) or "",
                "brief": (s.get("brief") or s.get("repository_summary") or "")[:200],
                "eligibility_sample": [
                    r.get("rule_text") for r in s.get("eligibility_matrix", [])[:3]
                ] if s.get("eligibility_matrix") else []
            })

        lang_mandate = ""
        if target_language and target_language != "en":
            lang_mandate = (
                f"\nTARGET CITIZEN LANGUAGE: {language_name} (code: '{target_language}')\n"
                f"CRITICAL MULTILINGUAL MANDATE: You MUST write the 'bundle_title', 'description', 'total_financial_impact', scheme 'role' and 'benefit_summary', conflict 'title', 'explanation', and every step 'title' and 'instruction' in 'application_sequence' ENTIRELY in authentic native {language_name} script (e.g., Devanagari for Hindi/Marathi, Kannada for Kannada, Bengali for Bengali, Tamil for Tamil, Telugu for Telugu, Gujarati for Gujarati, Punjabi for Punjabi). "
                f"DO NOT WRITE IN ENGLISH for titles, descriptions, impact amounts, or application sequence steps! Keep only the official scheme names (like PM-KISAN, PM-KUSUM) and portal URLs intact.\n"
            )

        user_prompt = (
            f"Citizen Query: {user_query}\n"
            f"Known Citizen Profile: {json.dumps(user_profile)}\n"
            f"Discovered Government Schemes:\n{json.dumps(schemes_context, indent=2)}\n"
            f"{lang_mandate}\n"
            "Analyze these schemes for any mutual exclusions / policy conflicts and construct an optimal, "
            "synergistic Welfare Stacking Bundle if applicable."
        )

        try:
            res = llm_service._call_groq_json(
                prompt=user_prompt,
                system_prompt=POLICY_INTERACTION_SYSTEM_PROMPT,
                timeout=12.0
            )
            if res and isinstance(res, dict):
                return res
        except Exception as exc:
            logger.warning("LLM policy evaluation failed: %s", exc)

        return None

    @classmethod
    def _evaluate_deterministic_fallback(
        cls,
        schemes: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        user_query: str,
        source_conflict: Optional[Dict[str, Any]],
        target_language: str = "en",
        language_name: str = "English",
    ) -> Dict[str, Any]:
        """Robust multi-domain deterministic fallback covering all major sectors."""
        conflicts: List[Dict[str, Any]] = []
        if source_conflict and source_conflict.get("has_conflict"):
            conflicts.append(source_conflict)

        # Categorize schemes into sectors
        sector_map: Dict[str, List[Dict[str, Any]]] = {}
        for s in schemes:
            sec = _classify_scheme_domain(s)
            if sec not in sector_map:
                sector_map[sec] = []
            sector_map[sec].append(s)

        # Check for exclusive domain conflicts (e.g. 2 Housing schemes or 2 Scholarships)
        exclusive_sectors = {"housing", "education"}
        for sec in exclusive_sectors:
            competing = sector_map.get(sec, [])
            if len(competing) >= 2:
                s1, s2 = competing[0], competing[1]
                name1 = s1.get("scheme_name") or s1.get("name", "Scheme 1")
                name2 = s2.get("scheme_name") or s2.get("name", "Scheme 2")
                level1 = s1.get("level") or s1.get("jurisdiction", "Central")
                level2 = s2.get("level") or s2.get("jurisdiction", "State")

                rule_text = (
                    "Central/State guidelines strictly forbid claiming concurrent assistance for the same benefit."
                    if sec == "housing"
                    else "National Scholarship Portal guidelines prohibit holding multiple maintenance allowances simultaneously."
                )

                conflicts.append({
                    "has_conflict": True,
                    "scheme_id": f"{s1.get('slug', 'a')}-vs-{s2.get('slug', 'b')}",
                    "scheme_name": f"{name1} vs {name2}",
                    "alert_type": "CROSS_SCHEME_MUTUAL_EXCLUSION",
                    "severity": "HIGH",
                    "title": f"Policy Exclusion: Cannot Claim Both {name1} and {name2}",
                    "discrepancy_field": f"Dual {sec.capitalize()} Benefit Restriction",
                    "scheme_a": {"name": name1, "level": level1},
                    "scheme_b": {"name": name2, "level": level2},
                    "source_a": {"portal": f"{name1} Guidelines", "rule": rule_text},
                    "source_b": {"portal": f"{name2} Guidelines", "rule": "De-duplication audit rejects duplicate submissions."},
                    "explanation": (
                        f"Both '{name1}' and '{name2}' operate under the {sec.capitalize()} sector. "
                        f"Government guidelines bar concurrent enrollment in duplicate subsidy programs."
                    ),
                    "recommendation": {
                        "preferred_scheme": name1,
                        "reason": f"Prioritize {name1} for primary application; do not submit dual applications.",
                        "action": f"Apply to {name1} first. Only apply to {name2} if primary application is unfulfilled."
                    },
                    "clarification_prompt": f"Which scheme would you like to prioritize for detailed checking?",
                    "options": [f"Prioritize {name1}", f"Prioritize {name2}", "Compare both options"]
                })

        # Build synergistic welfare stack for the dominant sector
        welfare_stack = None
        if len(schemes) >= 2:
            # Pick dominant sector with most matches, or check query keywords
            q_lower = user_query.lower()
            target_sector = None

            for sec, meta in SECTOR_TAXONOMY.items():
                if any(kw in q_lower for kw in meta["keywords"]):
                    target_sector = sec
                    break

            if not target_sector:
                for sec, items in sector_map.items():
                    if sec != "general_welfare" and len(items) >= 1:
                        target_sector = sec
                        break

            if not target_sector:
                target_sector = "health" if "health" in sector_map else "agriculture"

            meta = get_localized_sector_meta(target_sector, target_language)

            stacked_items = []
            seen_names = set()
            for s in schemes[:4]:
                name = s.get("scheme_name") or s.get("name")
                if not name or name in seen_names:
                    continue
                seen_names.add(name)
                b_text = s.get("benefit") or (s.get("benefits") and s["benefits"][0]) or "Official welfare benefit"
                if isinstance(b_text, dict):
                    b_text = b_text.get("text", "")
                stacked_items.append({
                    "name": name,
                    "role": s.get("category", "Welfare Assistance"),
                    "benefit_summary": str(b_text)[:120],
                    "url": s.get("url", "https://www.myscheme.gov.in")
                })

            welfare_stack = {
                "bundle_title": meta["stack_title"],
                "bundle_type": meta["stack_type"],
                "badge": "Policy Convergence Approved",
                "description": meta["rationale"],
                "total_financial_impact": meta["default_impact"],
                "schemes": stacked_items,
                "application_sequence": [
                    {
                        "step": idx + 1,
                        "title": step[0],
                        "instruction": step[1]
                    }
                    for idx, step in enumerate(meta["seq"][:len(stacked_items)])
                ]
            }

        primary_conflict = conflicts[0] if conflicts else None

        return {
            "welfare_stack": welfare_stack,
            "cross_scheme_conflicts": conflicts,
            "conflict_alert": primary_conflict
        }
