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
1. OUT-OF-DOMAIN (is_out_of_domain = true):
   - Mark true ONLY if the query is completely unrelated to Indian government welfare (e.g., programming/code, school math homework, sports/IPL scores, cinema/movies, cooking recipes, commercial e-commerce shopping, personal jokes/flirts/dating).
   - If the user asks about ANY government scheme, subsidy, scholarship, loan, pension, ration, or citizen eligibility, it is strictly IN-DOMAIN (is_out_of_domain = false).
   - Context is critical: short answers like "Maharashtra", "21", "General", "Farmer" following prior questions are IN-DOMAIN.

   ⚠️ GEOGRAPHIC SCOPE — INDIA ONLY (is_out_of_domain = true for ALL of these):
   - Queries about studying, working, migrating, or living ABROAD or OVERSEAS are OUT-OF-DOMAIN.
   - Queries about foreign universities (Harvard, Oxford, MIT, NUS, etc.) are OUT-OF-DOMAIN.
   - Queries about foreign scholarship programs (Chevening, Fulbright, DAAD, Erasmus, Gates Cambridge, Rhodes, etc.) are OUT-OF-DOMAIN.
   - Queries about visas for foreign countries (US visa, UK visa, Schengen visa, student visa abroad) are OUT-OF-DOMAIN.
   - Queries about schemes, grants, or benefits from foreign governments (US, UK, Australia, Canada, EU, Germany, etc.) are OUT-OF-DOMAIN.
   - Queries about immigration, emigration, permanent residency abroad, or green cards are OUT-OF-DOMAIN.
   - Queries about working in foreign countries or international job permits are OUT-OF-DOMAIN.
   - If a query says "foreign education scheme" or "government scholarship for studying abroad in USA/UK/etc." — this is OUT-OF-DOMAIN because it pertains to foreign-country education, NOT an Indian welfare scheme.
   - EXCEPTION (always IN-DOMAIN): Indian government schemes that FUND Indians studying at Indian institutions (e.g., Central Sector Scholarship, PM-USP, Vidya Lakshmi loan portal, NSP scholarships) are ALWAYS in-domain regardless of the word "foreign" appearing in context.

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
        # Format recent conversation context
        history_summary = []
        for msg in (conversation_history or [])[-4:]:
            role = msg.get("role") or msg.get("sender") or "user"
            content = str(msg.get("content") or msg.get("text") or "").strip()[:200]
            if content:
                history_summary.append(f"{role.capitalize()}: {content}")

        history_str = "\n".join(history_summary) if history_summary else "No prior conversation."
        profile_str = json.dumps(user_profile, ensure_ascii=False) if user_profile else "{}"
        pref_lang = preferred_language or "auto"

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

        # Fallback if LLM is unavailable or returns malformed response
        logger.warning("LLM router returned invalid response or was unreachable; using safe fallback.")
        return self._fallback_route(user_query, conversation_history, user_profile, preferred_language=pref_lang)

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

        # Search terms from query words (filtering for ascii/alphanumeric or canonical terms)
        words = [w for w in re.findall(r"\b[a-zA-Z0-9-]+\b", query_for_intent) if len(w) > 3][:4]
        
        # If words are empty due to Indic native script, supply English domain terms based on detected language
        if not words:
            if lang_info["detected_language"] == "kn":
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

        is_agri = any(k in query_for_intent for k in ["farm", "kisan", "crop", "agri", "tractor", "pump", "raita", "sheti"])
        is_edu = any(k in query_for_intent for k in ["study", "student", "btech", "college", "school", "scholarship", "exam", "vidyanidhi", "chhatro"])
        is_biz = any(k in query_for_intent for k in ["business", "loan", "startup", "msme", "mudra", "shop", "manufacturing", "salavannu", "karj"])
        is_health = any(k in query_for_intent for k in ["health", "hospital", "doctor", "treatment", "disease", "elderly", "parent", "ayushman"])
        is_girl = any(k in query_for_intent for k in ["girl", "daughter", "single girl", "beti", "kanya"])

        if is_agri:
            target_sector = "Agriculture & Rural"
            target_role = "farmer"
            must_include.extend(["farm", "kisan", "agriculture"])
            must_exclude.extend(["scholarship", "matric", "student", "tuition", "housing", "pucca house", "girl child", "birth"])
        elif is_edu or is_girl:
            target_sector = "Education & Learning"
            target_role = "student"
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
