"""
Questionnaire Tool: Dynamic LLM-Powered Eligibility Gap Analyzer and Question Generator.
Strict Rules:
  1. Never Repeat: If a fact is already known from query, conversation history, or profile, strictly omit it.
  2. Never Miss: Every unresolved mandatory rule of the fetched candidate schemes becomes an interactive question.
  3. Dynamic UI Types: <= 4 options -> radio, > 4 options -> dropdown, numeric -> number input.
  4. Single-Turn Batch: Returns all needed questions together in ONE list.
  5. Zero-Gap Detection: If all criteria are already satisfied, returns is_complete = True, questions = [].
"""

import json
import logging
from typing import Any, Dict, List, Optional
from ..config import settings
from .llm_service import llm_service
from .observability import observe

logger = logging.getLogger("gov_scheme.tools.questionnaire")

QUESTIONNAIRE_SYSTEM_PROMPT = """You are an expert Indian Government Scheme Eligibility Profiler and Dynamic Questionnaire Synthesizer.
Your job is to compare the official eligibility criteria of the candidate scheme(s) against what the citizen has already shared,
and produce an interactive questionnaire ONLY for the missing criteria.

CRITICAL RULES:
1. NEVER REPEAT (Strict Deduplication):
   - Review what the citizen has already stated in the current message, previous chat turns, and known profile.
   - If a criterion is already known or directly implied (e.g., they already said "I am 21", "I live in Haryana", "I am an OBC female", "I have confirmed admission in B.Tech"), DO NOT ask it again!
   - Mark it as RESOLVED.

2. NEVER MISS (Comprehensive Gap Detection):
   - Inspect the candidate schemes' official eligibility rules and exclusions.
   - Any mandatory criterion that is STILL UNKNOWN or UNVERIFIED must be formulated into an interactive question.

3. ZERO QUESTIONS IF COMPLETE:
   - If the user has already provided all required criteria to evaluate the schemes, return an empty array `[]` for "questions" and set "is_complete": true.

4. USER-FRIENDLY INTERACTIVE OPTIONS:
   - Translate dense bureaucratic legalese into plain, respectful, citizen-friendly questions.
   - Generate clear, unambiguous options.
   - For choices with <= 4 options: set "input_type": "radio" (pill buttons).
   - For choices with > 4 options (e.g. State/UT selector, list of 18 trades): set "input_type": "dropdown".
   - For continuous values (income in rupees, age in years, landholding in acres/hectares): set "input_type": "number".

Respond strictly in valid JSON matching this schema:
{
  "is_complete": false,
  "resolved_criteria": [
    {"criterion": "...", "value": "...", "source": "query / history"}
  ],
  "unresolved_criteria": [
    {"scheme": "...", "rule": "..."}
  ],
  "questions": [
    {
      "id": "short_unique_field_key",
      "label": "Short Field Label (e.g., Annual Family Income)",
      "question": "Clear, respectful question text",
      "input_type": "radio | dropdown | number",
      "options": ["Option 1", "Option 2", "Option 3"],
      "hint": "Why this is required by the candidate scheme",
      "required": true
    }
  ]
}"""


class QuestionnaireTool:
    """
    Agentic Tool for Dynamic Eligibility Gap Analysis.
    Tool Name: 'dynamic_questionnaire_tool'
    """

    name: str = "dynamic_questionnaire_tool"
    description: str = (
        "Performs dynamic gap analysis between fetched candidate scheme rules and citizen context. "
        "Formulates a strict, single-turn interactive questionnaire for unresolved criteria (never repeats, never misses)."
    )

    def __init__(self):
        self.llm = llm_service

    @observe(name="QuestionnaireTool.execute")
    def execute(
        self,
        candidate_schemes: List[Dict[str, Any]],
        known_criteria: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        user_query: str = "",
    ) -> Dict[str, Any]:
        """
        Executes dynamic gap analysis and synthesizes interactive questions for unresolved criteria.
        """
        if not candidate_schemes:
            logger.info("QuestionnaireTool: No candidate schemes provided; zero questions.")
            return {
                "is_complete": True,
                "resolved_criteria": [],
                "unresolved_criteria": [],
                "questions": [],
            }

        # Summarize candidate scheme rules
        compact_schemes = []
        for s in candidate_schemes[:4]:
            s_name = s.get("scheme_name") or s.get("name") or "Scheme"
            rules = s.get("eligibility_rules", [])
            guidelines = s.get("brief") or s.get("repository_summary") or ""
            compact_schemes.append({
                "scheme_name": s_name,
                "jurisdiction": s.get("jurisdiction") or s.get("level") or "Central",
                "rules": [
                    r.get("rule_text") or f"{r.get('field')} {r.get('operator')} {r.get('value')}"
                    for r in rules if isinstance(r, dict)
                ][:10],
                "guidelines_preview": guidelines[:400],
            })

        # Summarize conversation history
        history_summary = []
        for msg in (conversation_history or [])[-4:]:
            role = msg.get("role") or msg.get("sender") or "user"
            content = str(msg.get("content") or msg.get("text") or "").strip()[:200]
            if content:
                history_summary.append(f"{role.capitalize()}: {content}")

        history_str = "\n".join(history_summary) if history_summary else "No prior conversation."
        criteria_str = json.dumps(known_criteria or {}, ensure_ascii=False)
        profile_str = json.dumps(user_profile or {}, ensure_ascii=False)
        schemes_str = json.dumps(compact_schemes, ensure_ascii=False)

        prompt = f"""Incoming Citizen Query: "{user_query}"

Known Criteria Extracted by Router:
{criteria_str}

Accumulated User Profile:
{profile_str}

Recent Conversation History:
{history_str}

Candidate Schemes and Their Official Criteria:
{schemes_str}

Perform strict gap analysis. Identify what is already resolved vs what is still missing.
Generate questions strictly for unresolved criteria (never repeat what is known, never miss what is needed)."""

        result = self.llm._call_groq_json(
            prompt=prompt,
            system_prompt=QUESTIONNAIRE_SYSTEM_PROMPT,
            timeout=settings.LLM_TIMEOUT_SECONDS,
        )

        if result and isinstance(result, dict) and "questions" in result:
            questions = result.get("questions", [])
            logger.info(
                "QuestionnaireTool generated %d dynamic questions (is_complete=%s)",
                len(questions),
                result.get("is_complete"),
            )
            return result

        logger.warning("QuestionnaireTool LLM call returned invalid response; using fallback diffing.")
        return self._fallback_questionnaire(
            candidate_schemes=candidate_schemes,
            known_criteria=known_criteria,
            user_profile=user_profile,
        )

    def _fallback_questionnaire(
        self,
        candidate_schemes: List[Dict[str, Any]],
        known_criteria: Optional[Dict[str, Any]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Safety fallback if LLM is unreachable."""
        merged_known = {**(user_profile or {}), **(known_criteria or {})}
        questions = []
        seen_fields = set()

        for scheme in candidate_schemes:
            rules = scheme.get("eligibility_rules", [])
            for r in rules:
                if not isinstance(r, dict):
                    continue
                field = r.get("field")
                if not field or field in merged_known or field in seen_fields:
                    continue
                seen_fields.add(field)

                rule_text = r.get("rule_text") or field.replace("_", " ").title()
                val = r.get("value")
                options = ["Yes", "No", "Not sure"] if not isinstance(val, list) else [str(v) for v in val] + ["Other"]
                input_type = "dropdown" if len(options) > 4 else "radio"

                questions.append({
                    "id": field,
                    "label": field.replace("_", " ").title(),
                    "question": f"Does the following condition apply to you: '{rule_text}'?",
                    "input_type": input_type,
                    "options": options,
                    "hint": f"Required for {scheme.get('scheme_name', 'scheme')} eligibility.",
                    "required": True,
                })

        return {
            "is_complete": len(questions) == 0,
            "resolved_criteria": [{"criterion": k, "value": str(v)} for k, v in merged_known.items()],
            "unresolved_criteria": [],
            "questions": questions,
        }

    def run(self, **kwargs) -> Dict[str, Any]:
        """Convenience alias for execute."""
        return self.execute(**kwargs)


# Global singleton instance
questionnaire_tool = QuestionnaireTool()
