"""
Stage 2 LLM Router: Single-Call Semantic Intent, Scope, and Criteria Extraction.
Evaluates:
  1. Out-of-Domain Detection (coding, sports, recipes, shopping, cinema vs legitimate welfare)
  2. Workflow Routing (GREETING, SCHEME_DISCOVERY, SCHEME_LOOKUP, ELIGIBILITY_CHECK, PROCEDURAL_GUIDE, SCHEME_COMPARISON)
  3. Applicant vs Target Beneficiary decoupling (is_self, target_description)
  4. Extracted Eligibility Criteria stated in the query (age, state, category, income, occupation, etc.)
  5. Repository Search Terms for myScheme
  6. Cross-Lingual & Vernacular Recognition (Kannada, Hindi, Bengali, Tamil, Telugu, Marathi, etc. -> English search terms)
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from ..config import settings
from .llm_service import llm_service

logger = logging.getLogger("gov_scheme.router")

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
    "bn": "Bengali",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "ml": "Malayalam",
    "or": "Odia",
}


def detect_script_and_language(text: str, preferred: Optional[str] = "auto") -> Dict[str, str]:
    """
    Detects language, display name, and script type (native vs latin) from user text.
    Handles Indic native scripts and Romanized (Kanglish/Hinglish/Tanglish) text.
    """
    clean = (text or "").strip()

    # 1. Check Unicode character ranges for native scripts
    if re.search(r"[\u0C80-\u0CFF]", clean):
        return {"detected_language": "kn", "language_name": "Kannada", "script_type": "native"}
    if re.search(r"[\u0980-\u09FF]", clean):
        return {"detected_language": "bn", "language_name": "Bengali", "script_type": "native"}
    if re.search(r"[\u0B80-\u0BFF]", clean):
        return {"detected_language": "ta", "language_name": "Tamil", "script_type": "native"}
    if re.search(r"[\u0C00-\u0C7F]", clean):
        return {"detected_language": "te", "language_name": "Telugu", "script_type": "native"}
    if re.search(r"[\u0A80-\u0AFF]", clean):
        return {"detected_language": "gu", "language_name": "Gujarati", "script_type": "native"}
    if re.search(r"[\u0A00-\u0A7F]", clean):
        return {"detected_language": "pa", "language_name": "Punjabi", "script_type": "native"}
    if re.search(r"[\u0D00-\u0D7F]", clean):
        return {"detected_language": "ml", "language_name": "Malayalam", "script_type": "native"}
    if re.search(r"[\u0900-\u097F]", clean):
        lang = "mr" if preferred == "mr" else "hi"
        return {"detected_language": lang, "language_name": LANGUAGE_NAMES.get(lang, "Hindi"), "script_type": "native"}

    # 2. Check Romanized / Transliterated text (Latin script)
    lowered = clean.lower()

    if re.search(r"\b(nanage|nanna|beku|maadodu|yojane|raita|hege|salavannu|vidyanidhi|hosa|keli)\b", lowered):
        return {"detected_language": "kn", "language_name": "Kannada", "script_type": "latin"}

    if re.search(r"\b(mujhe|mera|meri|chahiye|yojana|yojna|sarkari|kisan|kaise|karo|batao|kisi|kya|pata|milega)\b", lowered):
        return {"detected_language": "hi", "language_name": "Hindi", "script_type": "latin"}

    if re.search(r"\b(amar|dorkar|jonno|kore|chhatro|shohayota|ki|bhabe)\b", lowered):
        return {"detected_language": "bn", "language_name": "Bengali", "script_type": "latin"}

    if re.search(r"\b(enakku|vendum|thittam|arasu|manavar|epadi)\b", lowered):
        return {"detected_language": "ta", "language_name": "Tamil", "script_type": "latin"}

    if re.search(r"\b(naaku|kaavali|pathakam|prabhutva|raitu|ela)\b", lowered):
        return {"detected_language": "te", "language_name": "Telugu", "script_type": "latin"}

    if re.search(r"\b(majhya|pahije|karava|yojna|sheti|shetiyojana|ahe|kasa)\b", lowered):
        return {"detected_language": "mr", "language_name": "Marathi", "script_type": "latin"}

    # 3. If explicit preferred language is set (and not 'auto')
    if preferred and preferred != "auto" and preferred in LANGUAGE_NAMES:
        return {"detected_language": preferred, "language_name": LANGUAGE_NAMES[preferred], "script_type": "latin"}

    return {"detected_language": "en", "language_name": "English", "script_type": "latin"}


ROUTER_SYSTEM_PROMPT = """You are the official Central and State Indian Government Welfare Scheme Intent Router on the myScheme platform.
Your mandate is to analyze incoming citizen messages and make ONE authoritative routing decision and generate search intelligence.

CRITICAL ROUTING INSTRUCTIONS:
1. OUT-OF-DOMAIN EVALUATION (is_out_of_domain = true):
   myScheme is STRICTLY for Indian Government welfare schemes, subsidies, citizen welfare grants, and public entitlements.
   
   Set is_out_of_domain = true for ANY of the following:
   A. COMMERCIAL PRIVATE FINANCE & BANKING:
      - Private bank personal loans, commercial credit cards, EMI calculators, or private vehicle/gold financing (e.g. "HDFC personal loan interest rate", "ICICI credit card", "Axis bank EMI calculator").
      - Note: Official Government welfare programs like Pradhan Mantri Mudra Yojana (PMMY), PMEGP, Stand-Up India, PM SVANidhi, and Vidya Lakshmi education loans are STRICTLY IN-DOMAIN. But purely commercial private bank retail loans are OUT-OF-DOMAIN.
   B. RETAIL PRODUCT & AUTOMOBILE SHOWROOM SHOPPING:
      - Showroom vehicle prices, on-road prices, dealer discounts, smartphone/electronics shopping (e.g. "Mahindra 575 DI tractor on road price", "iPhone discount", "best bike under 1 lakh").
      - Note: Government equipment or EV subsidies (like PM-KUSUM or SMAM mechanization subsidies) are IN-DOMAIN. Asking for retail dealer showroom prices is OUT-OF-DOMAIN.
   C. CLINICAL MEDICAL ADVICE & SYMPTOM PRESCRIPTIONS:
      - Requesting symptom diagnosis, medical advice, prescription medicines (e.g. "chest pain what tablet to take", "medicine for fever").
      - Note: Inquiring about government health insurance (Ayushman Bharat PM-JAY), Jan Aushadhi free medicines, or government hospital welfare is IN-DOMAIN.
   D. CRIMINAL LAW, PRIVATE PROPERTY DISPUTES, OR POLICE FIR:
      - Inquiries on filing criminal police FIRs, neighbor boundary disputes, private court litigation, hiring private lawyers.
      - Note: Official government legal aid (NALSA) or victim compensation schemes are IN-DOMAIN.
   E. PROGRAMMING, HOMEWORK, SPORTS, CINEMA, RECIPES, GENERAL CHAT:
      - Coding (Python, SQL), math homework, IPL/cricket scores, movie reviews, food recipes, casual banter.
   F. PURE FOREIGN PROGRAMS & INTERNATIONAL MATTERS:
      - Foreign university admissions, US/UK/Canada visas, foreign government financial aid (FAFSA, Chevening, Fulbright).
      - IMPORTANT EXCEPTION (STRICTLY IN-DOMAIN): Official Government of India schemes supporting citizens for overseas education (e.g. National Overseas Scholarship - NOS by Ministry of Social Justice for SC/ST students, or Dr. Ambedkar Central Sector Scheme) are ALWAYS IN-DOMAIN.
   G. ROUTINE CIVIC ADMINISTRATION, LICENSING & REGULATORY COMPLIANCE:
      - Routine administrative services: Booking Passport Seva Kendra (PSK) appointment slots, driving license testing, RTO vehicle registration (RC), or voter ID issuance.
      - Tax return compliance: Income tax return forms (ITR-1/Sahaj, ITR-2), GST filing, paying fines/penalties, or paying traffic police e-challans.
      - Commodity/bullion rates: Live 24k/22k gold prices, silver rates, stock market prices.
      - Private medical appointments: Booking doctor consultations or OPD slots at private hospitals (e.g. Apollo, Fortis).
      - Note: Routine civic administration and compliance are NOT welfare schemes. If the citizen is trying to book an administrative slot, file a tax return, pay a fine, or buy commodities, mark is_out_of_domain = true.

   When is_out_of_domain = true:
   - Provide a concise out_of_domain_reason.
   - Provide a helpful, polite polite_ood_refusal in the citizen's detected language explaining that JanSahayak exclusively guides Indian Government welfare benefits.

2. WORKFLOW CLASSIFICATION (workflow):
   - "GREETING": Greetings, namaste, hello, or asking what the platform can do.
   - "SCHEME_DISCOVERY": Citizen describes a problem or need without naming a specific scheme (e.g., "scholarship for BTech", "solar pump for farmers", "assistance for farming equipment").
   - "SCHEME_LOOKUP": Citizen names a specific scheme (e.g., "PM Surya Ghar", "Ayushman Bharat", "SMAM", "PM-KISAN").
   - "ELIGIBILITY_CHECK": Citizen asks if they qualify, provides personal demographics, or answers a follow-up question.
   - "PROCEDURAL_GUIDE": Citizen asks how to apply or what documents are required.
   - "SCHEME_COMPARISON": Citizen asks to compare two or more schemes (e.g., "Mudra vs PMEGP").

3. BENEFICIARY ANALYSIS:
   - Identify whether the citizen is asking for themselves (is_self: true) or on behalf of someone else (e.g., adult child asking for elderly parents, father asking for daughter).
   - State the target_description (e.g., "self", "elderly mother", "girl child", "small farmer").

4. OPEN-ENDED EXTRACTED CRITERIA (extracted_criteria):
   - Extract a flexible, unconstrained key-value object containing ANY eligibility facts, civic attributes, economic constraints, qualifications, or personal situations stated by the citizen.
   - DO NOT restrict yourself to any fixed list of fields. Government schemes have hundreds of unique conditions across sectors.
   - Capture whatever the user explicitly states using clear, descriptive keys. Examples:
     * Geography: state, district, city, area_type (rural/urban)
     * Demographics: age, gender, social_category (OBC/SC/ST/General/EWS), minority_status
     * Financials: annual_family_income, monthly_income, bpl_card_status, ration_card_type
     * Work / Business: occupation, employment_status, artisan_trade, street_vendor_lor, msme_type
     * Agriculture: landholding_size, land_type, crop_type, farm_equipment_need, irrigation_type
     * Education: education_level, course_name, 10th_12th_percentage, admission_status
     * Housing & Energy: house_ownership, roof_rights, electricity_meter_load_kw
   - If no specific criteria are stated, return an empty object {}.

5. SEARCH SPECIFICATION FOR CRAWLER (search_specification):
   - Formulate precise search intelligence for the Crawler Agent:
     * "core_intent": Concise 3-6 word summary of what the citizen is actually looking for.
     * "target_sector": Exact sector (e.g., "Agriculture & Rural", "Education & Learning", "Business & Entrepreneurship", "Handloom & Textiles", "Housing & Energy", "Healthcare & Wellness", "Women & Child", "Social Welfare").
     * "target_role": "farmer", "student", "artisan", "entrepreneur", "patient", "woman", or "general_citizen".
     * "search_queries": 3 to 4 distinct, official-portal-optimized search queries (e.g. for farm equipment: ["agricultural mechanization", "farm equipment subsidy", "tractor farm machinery", "kisan agriculture infrastructure"]).
     * "must_include_keywords": 4 to 8 essential domain keywords that matching schemes MUST relate to (e.g. ["equipment", "machinery", "tractor", "farm", "kisan", "mechanization"]).
     * "must_exclude_keywords": 4 to 8 conflicting domain keywords that matching schemes MUST NOT be about (e.g. ["scholarship", "matric", "student", "tuition", "housing", "pucca house", "pension", "girl child", "birth"]).

6. MULTILINGUAL & CROSS-LINGUAL INTELLIGENCE:
   - Identify the citizen's language and script:
     * "detected_language": ISO code ("en", "hi", "kn", "bn", "mr", "ta", "te", "gu", "pa", etc.).
     * "language_name": Full English name ("Kannada", "Hindi", "Bengali", "Marathi", "Tamil", "Telugu", "Gujarati", "English").
     * "script_type": "native" (written in vernacular script) or "latin" (written in English alphabet / transliterated).
   - MANDATORY CROSS-LINGUAL QUERY TRANSLATION:
     * Even if the citizen typed in Kannada, Hindi, Bengali, or Romanized alphabet (e.g., "nanage kisan loan beku", "mujhe tractor subsidy chahiye"), ALL search terms in "search_specification.search_queries", "myscheme_search_terms", and "must_include_keywords" MUST BE IN CANONICAL ENGLISH.
     * Official Indian government portals and myScheme databases index records in English. Translating search queries into English guarantees 100% accurate database matching.

Respond strictly in valid JSON matching this schema:
{
  "is_out_of_domain": false,
  "out_of_domain_reason": null,
  "polite_ood_refusal": null,
  "workflow": "GREETING | SCHEME_DISCOVERY | SCHEME_LOOKUP | ELIGIBILITY_CHECK | PROCEDURAL_GUIDE | SCHEME_COMPARISON",
  "target_schemes": ["names of any specific schemes named by citizen"],
  "detected_language": "en | hi | kn | bn | mr | ta | te | gu | pa",
  "language_name": "English | Hindi | Kannada | Bengali | Marathi | Tamil | Telugu | Gujarati | Punjabi",
  "script_type": "native | latin",
  "beneficiary": {
    "is_self": true,
    "applicant_role": "citizen / student / parent / adult child / farmer / artisan",
    "target_description": "self / elderly parents / girl child / marginal farmer"
  },
  "extracted_criteria": {
    "<attribute_name>": "<extracted_value>"
  },
  "myscheme_search_terms": ["term 1", "term 2"],
  "search_specification": {
    "core_intent": "Concise summary of intent in English",
    "target_sector": "Agriculture & Rural | Education & Learning | ...",
    "target_role": "farmer | student | artisan | ...",
    "search_queries": ["english query 1", "english query 2", "english query 3"],
    "must_include_keywords": ["english_kw1", "english_kw2", "english_kw3"],
    "must_exclude_keywords": ["term1", "term2", "term3"]
  }
}"""


class SchemeRouter:
    """Dedicated LLM Router for Stage 2 processing."""

    def __init__(self):
        self.llm = llm_service

    def route(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        preferred_language: Optional[str] = "auto",
    ) -> Dict[str, Any]:
        """
        Executes a single structured LLM call to route the query,
        detect Out-of-Domain, decouple beneficiaries, and extract any stated eligibility criteria.
        """
        pref_lang = preferred_language or "auto"
        lower_q = (user_query or "").strip().lower()

        # Fast-path: For questionnaire submissions, structured profile updates, or short follow-up answers,
        # use deterministic routing directly to preserve precious LLM rate limits for response generation.
        is_followup_criteria_response = bool(
            user_profile or
            (conversation_history and len(lower_q.split()) <= 5 and any(
                opt in lower_q for opt in [
                    "male", "female", "urban", "rural", "yes", "no", "general", "obc", "sc", "st",
                    "acre", "lakh", "farmer", "student", "age", "income", "karnataka", "up", "bihar",
                    "maharashtra", "tamil", "bengal", "gujarat", "punjab", "delhi", "haryana", "rajasthan"
                ]
            ))
        )
        if is_followup_criteria_response:
            logger.info("Fast-path: Deterministic routing for follow-up criteria turn (0 Groq tokens spent).")
            return self._fallback_route(
                user_query=user_query,
                conversation_history=conversation_history,
                user_profile=user_profile,
                preferred_language=pref_lang,
            )

        # Format recent conversation context
        history_summary = []
        for msg in (conversation_history or [])[-4:]:
            role = msg.get("role") or msg.get("sender") or "user"
            content = str(msg.get("content") or msg.get("text") or "").strip()[:200]
            if content:
                history_summary.append(f"{role.capitalize()}: {content}")

        history_str = "\n".join(history_summary) if history_summary else "No prior conversation."
        profile_str = json.dumps(user_profile, ensure_ascii=False) if user_profile else "{}"

        prompt = f"""Incoming Citizen Message: "{user_query}"

Citizen Preferred Interface Language: {pref_lang}

Recent Chat History:
{history_str}

Accumulated User Profile:
{profile_str}

Analyze this message, classify the workflow, identify language and script, formulate canonical English search specifications for the repository, and extract any stated eligibility criteria."""

        # Call Groq LLM in JSON mode
        result = self.llm._call_groq_json(
            prompt=prompt,
            system_prompt=ROUTER_SYSTEM_PROMPT,
            timeout=settings.LLM_TIMEOUT_SECONDS,
        )

        if result and isinstance(result, dict) and "workflow" in result:
            # Ensure language details are always present
            if not result.get("detected_language"):
                lang_info = detect_script_and_language(user_query, pref_lang)
                result.setdefault("detected_language", lang_info["detected_language"])
                result.setdefault("language_name", lang_info["language_name"])
                result.setdefault("script_type", lang_info["script_type"])

            logger.info(
                "Router classified query as '%s' (lang=%s, is_ood=%s, target_schemes=%s)",
                result.get("workflow"),
                result.get("detected_language"),
                result.get("is_out_of_domain"),
                result.get("target_schemes"),
            )
            return result

        # Seamlessly fallback to deterministic routing if LLM router returned invalid response or hit rate limit
        logger.warning("LLM router call failed or hit rate limit; seamlessly falling back to deterministic routing engine.")
        return self._fallback_route(
            user_query=user_query,
            conversation_history=conversation_history,
            user_profile=user_profile,
            preferred_language=pref_lang,
        )

    def _fallback_route(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        preferred_language: Optional[str] = "auto",
    ) -> Dict[str, Any]:
        """Deterministic safety fallback if LLM inference is down."""
        from .domain_guard import is_greeting, OUT_OF_DOMAIN_PATTERNS
        from .scheme_discovery_workflow import _profile_from_explicit_text
        import re

        lower_query = (user_query or "").strip().casefold()
        is_greet = is_greeting(user_query)

        # Detect script and language
        lang_info = detect_script_and_language(user_query, preferred_language)

        # Root query recovery from conversation history for follow-up turns
        root_query = user_query
        is_followup = False
        if conversation_history:
            prev_user_queries = [
                str(m.get("content") or m.get("text") or "").strip()
                for m in conversation_history
                if isinstance(m, dict) and (m.get("role") == "user" or m.get("sender") == "user")
            ]
            substantive = [
                q for q in prev_user_queries
                if len(q.split()) > 3 and not any(q.lower() == opt for opt in ["male", "female", "urban", "rural", "yes", "no", "general", "obc", "sc", "st"])
            ]
            if substantive and len(lower_query.split()) <= 4:
                root_query = substantive[-1]
                is_followup = True

        query_for_intent = root_query.casefold() if is_followup else lower_query

        # Rule-based OOD fallback
        matched_ood = False
        if not is_greet:
            from .domain_guard import GEOGRAPHIC_OOD_PATTERNS
            is_goi_overseas_scheme = any(kw in lower_query for kw in [
                "national overseas scholarship", "nos scheme", "nos scholarship",
                "ministry of social justice", "dr. ambedkar overseas", "dr ambedkar central sector"
            ])
            if not is_goi_overseas_scheme:
                for pat in GEOGRAPHIC_OOD_PATTERNS:
                    if re.search(pat, lower_query, re.IGNORECASE):
                        matched_ood = True
                        break
            if not matched_ood:
                for pat in OUT_OF_DOMAIN_PATTERNS:
                    if re.search(pat, lower_query):
                        matched_ood = True
                        break

        fallback_criteria = _profile_from_explicit_text(user_query)

        workflow = "SCHEME_DISCOVERY"
        if is_greet:
            workflow = "GREETING"
        elif is_followup:
            workflow = "ELIGIBILITY_CHECK"
        elif any(k in lower_query for k in ["how to apply", "application step", "documents required"]):
            workflow = "PROCEDURAL_GUIDE"
        elif " vs " in lower_query or "difference between" in lower_query:
            workflow = "SCHEME_COMPARISON"
        elif any(k in lower_query for k in ["eligible", "eligibility", "am i eligible"]) or len(fallback_criteria) >= 2:
            workflow = "ELIGIBILITY_CHECK"

        is_agri = any(k in query_for_intent for k in [
            "farm", "kisan", "crop", "agri", "tractor", "pump", "raita", "sheti", "agriculture",
            "किसान", "कृषि", "खेती", "फसल",
            "ಕೃಷಿ", "ರೈತ", "ಬೆಳೆ", "ಕೃಷಿಕ",
            "চাষ", "কৃষি", "কৃষক", "ফসল",
            "விவசாய", "உழவர்", "பயிர்", "வேளாண்",
            "వ్యవసాయ", "రైతు", "పంట",
            "ખેતી", "ખેડૂત", "પાક", "કૃષિ",
            "ਖੇਤੀ", "ਕਿਸਾਨ", "ਫਸਲ",
        ])
        is_edu = any(k in query_for_intent for k in [
            "study", "student", "btech", "college", "school", "scholarship", "exam", "vidyanidhi", "chhatro", "education",
            "शिक्षा", "एजुकेशन", "पढ़ाई", "छात्र", "विद्यार्थी", "छात्रवृत्ति", "स्कॉलरशिप",
            "ಶಿಕ್ಷಣ", "ವಿದ್ಯಾರ್ಥಿ", "ವಿದ್ಯಾರ್ಥಿವೇತನ", "ಶಾಲೆ", "ಕಾಲೇಜು",
            "শিক্ষা", "ছাত্র", "বৃত্তি", "স্কুল", "কলেজ",
            "கல்வி", "மாணவர்", "உதவித்தொகை", "பள்ளி", "கல்லூரி",
            "చదువు", "విద్య", "విద్యార్థి", "స్కాలర్‌షిప్", "పాఠశాల", "కళాశాల",
            "શિક્ષણ", "વિદ્યાર્થી", "શિષ્યવૃત્તિ", "શાળા", "કોલેજ",
            "ਸਿੱਖਿਆ", "ਵਿਦਿਆਰਥੀ", "ਵਜ਼ੀਫ਼ਾ", "ਸਕੂਲ", "ਕਾਲਜ",
        ])
        is_biz = any(k in query_for_intent for k in [
            "business", "loan", "startup", "msme", "mudra", "shop", "manufacturing", "salavannu", "karj",
            "व्यापार", "लोन", "ऋण", "कर्ज", "मुद्रा",
            "ಸಾಲ", "ವ್ಯಾಪಾರ", "ಉದ್ಯಮ",
            "ঋণ", "লোন", "ব্যবসা", "উদ্যোগ",
            "கடன்", "தொழில்", "வணிகம்",
            "రుణం", "వ్యాపారం", "ఉద్యోగం", "లోన్",
            "લોન", "વેપાર", "ધંધો", "કરજ",
            "ਕਰਜ਼ਾ", "ਲੋਨ", "ਕਾਰੋਬਾਰ", "ਵਪਾਰ",
        ])
        is_health = any(k in query_for_intent for k in [
            "health", "hospital", "doctor", "treatment", "disease", "elderly", "parent", "ayushman",
            "स्वास्थ्य", "इलाज", "अस्पताल", "दवा", "आयुष्मान", "आरोग्य",
            "ಆರೋಗ್ಯ", "ಆಸ್ಪತ್ರೆ", "ಔಷಧಿ", "ಚಿಕಿತ್ಸೆ",
            "স্বাস্থ্য", "হাসপাতাল", "ওষুধ", "চিকিৎসা",
            "சுகாதாரம்", "மருத்துவமனை", "மருந்து", "சிகிச்சை",
            "ఆరోగ్యం", "ఆసుపత్రి", "వైద్యం", "మందులు",
            "આરોગ્ય", "હોસ્પિટલ", "દવા", "સારવાર",
            "ਸਿਹਤ", "ਹਸਪਤਾਲ", "ਦਵਾਈ", "ਇਲਾਜ",
        ])
        is_girl = any(k in query_for_intent for k in ["girl", "daughter", "single girl", "beti", "kanya", "बेटी", "कन्या", "बालिका", "लाडली"])
        has_edu_loan = is_edu and any(k in query_for_intent for k in ["loan", "लोन", "ऋण", "कर्ज", "interest subsidy", "subsidy", "सब्सिडी", "ಸಾಲ", "రుణం"])

        # Search terms from query words (filtering for ascii/alphanumeric or canonical terms)
        words = [w for w in re.findall(r"\b[a-zA-Z0-9-]+\b", query_for_intent) if len(w) > 3][:4]
        
        # If words are empty due to Indic native script, supply English domain terms based on detected intent
        if not words:
            if is_agri:
                words = ["kisan", "farmer", "agriculture", "loan"]
            elif is_edu:
                words = ["scholarship", "student", "education"]
            elif is_biz:
                words = ["business", "loan", "msme"]
            elif is_health:
                words = ["health", "hospital", "ayushman"]
            elif lang_info["detected_language"] == "kn":
                words = ["karnataka", "welfare", "scheme"]
            elif lang_info["detected_language"] in ("hi", "mr"):
                words = ["central", "welfare", "scheme"]
            else:
                words = ["government", "scheme"]

        search_terms = [" ".join(words)] if words else ["government schemes"]

        # Determine target sector & exclusions based on keywords (supporting Romanized and English)
        target_sector = "General Welfare"
        target_role = "citizen"
        must_include = list(words) if words else ["scheme"]
        must_exclude = []

        if is_agri:
            target_sector = "Agriculture & Rural"
            target_role = "farmer"
            must_include.extend(["farm", "kisan", "agriculture"])
            must_exclude.extend(["scholarship", "matric", "student", "tuition", "housing", "pucca house", "girl child", "birth"])
        elif is_edu or is_girl:
            target_sector = "Education & Learning"
            target_role = "student"
            if has_edu_loan:
                must_include.extend(["education loan", "student loan", "interest subsidy", "Vidya Lakshmi", "education"])
            else:
                must_include.extend(["scholarship", "student", "education"])
            if is_girl:
                must_include.append("girl")
            must_exclude.extend(["farmer", "kisan", "crop", "tractor"])
        elif is_biz:
            target_sector = "Business & Entrepreneurship"
            target_role = "entrepreneur"
            must_include.extend(["business", "loan", "enterprise", "manufacturing", "PMEGP", "PMMY"])
            must_exclude.extend(["scholarship", "student", "matric", "crop", "farm"])
        elif is_health:
            target_sector = "Healthcare & Wellness"
            target_role = "patient"
            must_include.extend(["health", "hospital", "Ayushman", "treatment"])
            must_exclude.extend(["scholarship", "student", "tractor", "farm"])

        search_spec = {
            "core_intent": root_query[:80],
            "target_sector": target_sector,
            "target_role": target_role,
            "search_queries": [" ".join(must_include[:3])] + search_terms,
            "must_include_keywords": list(set(must_include)),
            "must_exclude_keywords": list(set(must_exclude)),
        }

        return {
            "is_out_of_domain": matched_ood,
            "out_of_domain_reason": "Query appears outside government welfare scope." if matched_ood else None,
            "polite_ood_refusal": None,
            "workflow": "GREETING" if is_greet else workflow,
            "target_schemes": [],
            "detected_language": lang_info["detected_language"],
            "language_name": lang_info["language_name"],
            "script_type": lang_info["script_type"],
            "beneficiary": {
                "is_self": not any(k in lower_query for k in ["for my mother", "for my father", "for my parents", "for my daughter", "for my son"]),
                "applicant_role": target_role,
                "target_description": "self",
            },
            "extracted_criteria": fallback_criteria,
            "myscheme_search_terms": search_terms,
            "search_specification": search_spec,
        }


# Global router singleton
scheme_router = SchemeRouter()
