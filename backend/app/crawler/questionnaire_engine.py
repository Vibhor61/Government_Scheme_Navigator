"""
Targeted Eligibility Questionnaire Engine
Generates non-redundant, unified eligibility questionnaires based on:
1. Discovered scheme criteria & quoted evidence.
2. Information already provided in user query, multi-turn chat history, or explicit user profile.
3. Strict UI formatting:
   - All missing questions asked together in ONE single turn (no piecemeal back-and-forth).
   - Dynamic input types:
     * If options count > 4: input_type="dropdown"
     * If options count <= 4: input_type="radio"
     * If freeform numeric or text needed: input_type="number" or "text"
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from .portal_catalog import get_state_region_options
from .scheme_rules import (
    FIELD_INFO,
    PROFILE_ALIASES,
    SUPPORTED_FIELDS,
    SUPPORTED_OPERATORS,
    _field_options,
    normalize_profile,
)

logger = logging.getLogger("gov_scheme.questionnaire")


class TargetedQuestionnaireEngine:
    def __init__(self):
        pass

    def extract_known_profile_from_context(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        llm_extracted_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Extracts all known citizen facts from:
        1. Explicit user_profile dictionary
        2. LLM-extracted profile attributes from current query
        3. User-authored messages from the conversation history
        4. Current user query text
        """
        known: Dict[str, Any] = normalize_profile(user_profile)

        # Incorporate LLM extracted attributes if provided
        if llm_extracted_profile and isinstance(llm_extracted_profile, dict):
            normalized_llm = normalize_profile(llm_extracted_profile)
            for k, v in normalized_llm.items():
                if v is not None and (k not in known or known[k] is None):
                    known[k] = v

        # Aggregate text from current query and all previous user messages
        combined_texts = [user_query]
        for msg in conversation_history or []:
            if isinstance(msg, dict):
                if msg.get("role") != "user":
                    continue
                content = msg.get("content") or msg.get("text") or ""
                # Also inspect if structured profile answers were submitted in a previous turn
                if "profile" in msg and isinstance(msg["profile"], dict):
                    known.update(normalize_profile(msg["profile"]))
                if "user_profile" in msg and isinstance(msg["user_profile"], dict):
                    known.update(normalize_profile(msg["user_profile"]))
                if content:
                    combined_texts.append(content)

        full_context_text = " ".join(combined_texts).casefold()

        # Deterministic extraction of standard facts from full conversational text
        from .scheme_discovery_workflow import _profile_from_explicit_text
        context_profile = _profile_from_explicit_text(full_context_text)
        for k, v in context_profile.items():
            if k not in known or known[k] is None:
                known[k] = v

        # Only treat first-person statements as profile facts; topic requests are not identities.
        if "occupation" not in known:
            if re.search(
                r"\b(?:i am|i'm|i work as|i work on)\s+(?:(?:a|an)\s+)?"
                r"(?:(?:female|male|small|marginal)\s+)?(?:farmer|kisan|cultivator)\b",
                full_context_text,
            ):
                known["occupation"] = "Farmer"
            elif re.search(r"\b(?:i am|i'm)\s+(?:a\s+)?student\b", full_context_text):
                known["occupation"] = "Student"
            elif re.search(
                r"\b(?:i am|i'm|i work as)\s+(?:a\s+)?(?:street\s+)?"
                r"(?:vendor|hawker)\b",
                full_context_text,
            ):
                known["occupation"] = "Street vendor"
            elif re.search(
                r"\b(?:i am|i'm|i work as)\s+(?:an?\s+)?"
                r"(?:artisan|craftsperson|weaver|carpenter|blacksmith)\b",
                full_context_text,
            ):
                known["occupation"] = "Artisan / Craftsperson"

        if "disability_status" not in known:
            if re.search(r"\b(pwd|physically disabled|person with disability|handicapped|blind|locomotor)\b", full_context_text):
                known["disability_status"] = "Person with Benchmark Disability (PwD)"
            elif re.search(r"\b(no disability|not disabled|able[\s-]?bodied)\b", full_context_text):
                known["disability_status"] = "No disability"

        if "marital_status" not in known:
            if re.search(r"\b(widow|widowed)\b", full_context_text):
                known["marital_status"] = "Widowed"
            elif re.search(r"\b(married|husband|wife)\b", full_context_text):
                known["marital_status"] = "Married"
            elif re.search(r"\b(unmarried|single)\b", full_context_text):
                known["marital_status"] = "Unmarried"

        if "bpl_status" not in known:
            if re.search(r"\b(bpl card|below poverty line|antodaya|aay card)\b", full_context_text):
                known["bpl_status"] = "BPL / Antyodaya card holder"

        return known

    def build_targeted_questionnaire(
        self,
        schemes: List[Dict[str, Any]],
        user_query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        state_candidates_exist: bool = False,
        state_already_known: Optional[str] = None,
        llm_extracted_profile: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Builds the complete, non-redundant questionnaire strictly for candidate schemes.
        - Gathers missing criteria across all candidate schemes.
        - Prunes fields already supplied in conversation context or LLM extraction (NEVER REPEAT).
        - Ensures every criterion required by candidate schemes is addressed (NEVER MISS).
        - Dynamically assigns input_type:
          * options > 4 -> "dropdown"
          * options <= 4 -> "radio"
          * numeric values -> "number"
        Returns (questions_list, extracted_known_profile).
        """
        known_profile = self.extract_known_profile_from_context(
            user_query=user_query,
            conversation_history=conversation_history,
            user_profile=user_profile,
            llm_extracted_profile=llm_extracted_profile,
        )

        if state_already_known and "state" not in known_profile:
            known_profile["state"] = state_already_known

        # Collect all rules only from viable candidate schemes
        # Schemes that have already failed a rule based on known_profile should NOT ask further questions
        from .scheme_rules import _compare_rule

        candidate_rules: List[Dict[str, Any]] = []
        for s in schemes:
            rules = s.get("eligibility_rules", [])
            # If the scheme already has a rule evaluated as NOT_MET, user is disqualified from it.
            # Do NOT ask questions for a dead scheme!
            disqualified = False
            for rule in rules:
                if isinstance(rule, dict) and rule.get("field") in known_profile and known_profile[rule["field"]] is not None:
                    if _compare_rule(rule, known_profile) == "NOT_MET":
                        disqualified = True
                        break
            if disqualified:
                continue

            for rule in rules:
                if isinstance(rule, dict):
                    candidate_rules.append(rule)

        questions: List[Dict[str, Any]] = []
        seen_fields: Set[str] = set()

        # 1. State / UT Question if needed and not already known
        if (state_candidates_exist or not schemes) and not known_profile.get("state"):
            state_options = get_state_region_options()
            questions.append({
                "id": "state",
                "label": "State / UT of Residence",
                "question": "Which State or Union Territory do you reside in?",
                "input_type": "dropdown",  # 36 states/UTs > 4 -> dropdown
                "options": state_options,
                "required": True,
                "hint": "Required to check State Government specific schemes alongside Central schemes."
            })
            seen_fields.add("state")

        # 2. Group each field's rules so one question can cover every candidate scheme.
        rules_by_field: Dict[str, List[Dict[str, Any]]] = {}
        for rule in candidate_rules:
            field = rule.get("field")
            if not field or field not in SUPPORTED_FIELDS or rule.get("operator") not in SUPPORTED_OPERATORS:
                continue
            if field in known_profile and known_profile[field] is not None:
                continue
            rules_by_field.setdefault(field, []).append(rule)

        numeric_fields = {
            "annual_family_income", "loan_amount", "age", "course_duration", "landholding",
        }
        for field in FIELD_INFO:
            field_rules = rules_by_field.get(field, [])
            if not field_rules or field in seen_fields:
                continue
            seen_fields.add(field)
            first_rule = field_rules[0]
            label, question_text = FIELD_INFO[field]

            if field == "social_category" and any(
                rule.get("operator") == "in"
                and isinstance(rule.get("value"), list)
                and {str(item).casefold() for item in rule["value"]}
                == {"muslim", "christian", "sikh", "buddhist", "parsi", "jain"}
                for rule in field_rules
            ):
                label = "Community"
                question_text = "Which of these six notified minority communities, if any, applies to you?"

            signatures = {
                (rule.get("operator"), str(rule.get("value")))
                for rule in field_rules
            }
            if field in numeric_fields and len(signatures) > 1:
                input_type = "number"
                options = []
                unit = (
                    "years" if field in {"age", "course_duration"}
                    else "hectares" if field == "landholding"
                    else "rupees"
                )
                hint = (
                    f"Enter the exact value in {unit}; it will be checked against each "
                    "captured scheme threshold."
                )
            else:
                categorical_values: List[str] = []
                for rule in field_rules:
                    value = rule.get("value")
                    if rule.get("operator") in {"in", "not_in"} and isinstance(value, list):
                        categorical_values.extend(str(item) for item in value)
                    elif rule.get("operator") in {"eq", "neq"} and value is not None:
                        categorical_values.append(str(value))
                if len(set(categorical_values)) > 1:
                    options = list(dict.fromkeys(categorical_values)) + [
                        "None of these", "Not sure",
                    ]
                else:
                    options = _field_options(first_rule)
                input_type = "dropdown" if len(options) > 4 else "radio"
                hint = (
                    "Evaluates eligibility rules across the applicable schemes: "
                    + "; ".join(dict.fromkeys(
                        str(rule.get("rule_text", label)) for rule in field_rules
                    ))
                )

            questions.append({
                "id": field,
                "label": label,
                "question": question_text,
                "input_type": input_type,
                "options": options,
                "required": field == "state",
                "hint": hint,
            })

        return questions, known_profile


# Global engine instance
questionnaire_engine = TargetedQuestionnaireEngine()
