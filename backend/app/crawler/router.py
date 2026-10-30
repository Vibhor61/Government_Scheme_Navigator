"""
Stage 2 LLM Router: Single-Call Semantic Intent, Scope, and Criteria Extraction.
Evaluates:
  1. Out-of-Domain Detection (coding, sports, recipes, shopping, cinema vs legitimate welfare)
  2. Workflow Routing (GREETING, SCHEME_DISCOVERY, SCHEME_LOOKUP, ELIGIBILITY_CHECK, PROCEDURAL_GUIDE, SCHEME_COMPARISON)
  3. Applicant vs Target Beneficiary decoupling (is_self, target_description)
  4. Extracted Eligibility Criteria stated in the query (age, state, category, income, occupation, etc.)
  5. Repository Search Terms for myScheme
"""

import json
import logging
from typing import Any, Dict, List, Optional
from ..config import settings
from .llm_service import llm_service

logger = logging.getLogger("gov_scheme.router")


ROUTER_SYSTEM_PROMPT = """You are the official Central and State Indian Government Welfare Scheme Intent Router on the myScheme platform.
Your mandate is to analyze incoming citizen messages and make ONE authoritative routing decision and generate search intelligence.

CRITICAL ROUTING INSTRUCTIONS:
1. OUT-OF-DOMAIN (is_out_of_domain = true):
   - Mark true ONLY if the query is completely unrelated to Indian government welfare (e.g., programming/code, school math homework, sports/IPL scores, cinema/movies, cooking recipes, commercial e-commerce shopping, personal jokes/flirts/dating).
   - If the user asks about ANY government scheme, subsidy, scholarship, loan, pension, ration, or citizen eligibility, it is strictly IN-DOMAIN (is_out_of_domain = false).
   - Context is critical: short answers like "Maharashtra", "21", "General", "Farmer" following prior questions are IN-DOMAIN.

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

Respond strictly in valid JSON matching this schema:
{
  "is_out_of_domain": false,
  "out_of_domain_reason": null,
  "polite_ood_refusal": null,
  "workflow": "GREETING | SCHEME_DISCOVERY | SCHEME_LOOKUP | ELIGIBILITY_CHECK | PROCEDURAL_GUIDE | SCHEME_COMPARISON",
  "target_schemes": ["names of any specific schemes named by citizen"],
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
    "core_intent": "Concise summary of intent",
    "target_sector": "Agriculture & Rural | Education & Learning | ...",
    "target_role": "farmer | student | artisan | ...",
    "search_queries": ["query 1", "query 2", "query 3"],
    "must_include_keywords": ["keyword1", "keyword2", "keyword3"],
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

        prompt = f"""Incoming Citizen Message: "{user_query}"

Recent Chat History:
{history_str}

Accumulated User Profile:
{profile_str}

Analyze this message, classify the workflow, verify domain validity, and extract any stated eligibility criteria."""

        # Call Groq LLM in JSON mode
        result = self.llm._call_groq_json(
            prompt=prompt,
            system_prompt=ROUTER_SYSTEM_PROMPT,
            timeout=settings.LLM_TIMEOUT_SECONDS,
        )

        if result and isinstance(result, dict) and "workflow" in result:
            logger.info(
                "Router classified query as '%s' (is_ood=%s, target_schemes=%s)",
                result.get("workflow"),
                result.get("is_out_of_domain"),
                result.get("target_schemes"),
            )
            return result

        # Fallback if LLM is unavailable or returns malformed response
        logger.warning("LLM router returned invalid response or was unreachable; using safe fallback.")
        return self._fallback_route(user_query, conversation_history, user_profile)

    def _fallback_route(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Deterministic safety fallback if LLM inference is down."""
        from .domain_guard import is_greeting, OUT_OF_DOMAIN_PATTERNS
        from .scheme_discovery_workflow import _profile_from_explicit_text
        import re

        lower_query = (user_query or "").strip().casefold()
        is_greet = is_greeting(user_query)

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

        # Search terms from query words
        words = [w for w in re.findall(r"\b[a-zA-Z0-9-]+\b", query_for_intent) if len(w) > 3][:4]
        search_terms = [" ".join(words)] if words else ["government schemes"]

        # Determine target sector & exclusions based on keywords
        target_sector = "General Welfare"
        target_role = "citizen"
        must_include = words if words else ["scheme"]
        must_exclude = []

        if any(k in query_for_intent for k in ["farm", "kisan", "crop", "agri", "tractor", "pump"]):
            target_sector = "Agriculture & Rural"
            target_role = "farmer"
            must_include.extend(["farm", "kisan", "agriculture"])
            must_exclude.extend(["scholarship", "matric", "student", "tuition", "housing", "pucca house", "girl child", "birth"])
        elif any(k in query_for_intent for k in ["study", "student", "btech", "college", "school", "scholarship", "exam"]):
            target_sector = "Education & Learning"
            target_role = "student"
            must_include.extend(["scholarship", "student", "education"])
            must_exclude.extend(["farmer", "kisan", "crop", "tractor"])
        elif any(k in query_for_intent for k in ["business", "loan", "startup", "msme", "mudra", "shop", "manufacturing"]):
            target_sector = "Business & Entrepreneurship"
            target_role = "entrepreneur"
            must_include.extend(["business", "loan", "enterprise", "manufacturing", "PMEGP", "PMMY"])
            must_exclude.extend(["scholarship", "student", "matric", "crop", "farm"])
        elif any(k in query_for_intent for k in ["health", "hospital", "doctor", "treatment", "disease", "elderly", "parent"]):
            target_sector = "Healthcare & Wellness"
            target_role = "patient"
            must_include.extend(["health", "hospital", "Ayushman", "treatment"])
            must_exclude.extend(["scholarship", "student", "tractor", "farm"])
        elif any(k in query_for_intent for k in ["girl", "daughter", "single girl"]):
            target_sector = "Education & Learning"
            target_role = "student"
            must_include.extend(["girl", "scholarship", "CBSE", "daughter"])
            must_exclude.extend(["tractor", "farm", "business"])

        search_spec = {
            "core_intent": root_query[:80],
            "target_sector": target_sector,
            "target_role": target_role,
            "search_queries": [root_query] + search_terms,
            "must_include_keywords": list(set(must_include)),
            "must_exclude_keywords": list(set(must_exclude)),
        }

        return {
            "is_out_of_domain": matched_ood,
            "out_of_domain_reason": "Query appears outside government welfare scope." if matched_ood else None,
            "polite_ood_refusal": None,
            "workflow": "GREETING" if is_greet else workflow,
            "target_schemes": [],
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
