"""
Response Generator Tool: Adaptive, Free-Form Response Synthesizer.
Crafts natural, citizen-centered, cite-grounded Markdown responses.
Adapts freely to the exact conversational stage:
  - Middle Stage (questions pending): Introduces matching schemes and guides citizen on the interactive card.
  - Final Stage (criteria complete): Issues grounded verdict, benefits breakdown, required documents, and official links.
  - Comparison: Side-by-side comparative analysis.
  - Procedural: Step-by-step application process walkthrough.
  - Multilingual: Synthesizes responses natively in citizen's preferred language & script (Kannada, Hindi, Bengali, Tamil, etc.).
"""

import json
import logging
from typing import Any, Dict, List, Optional
from ..config import settings
from .llm_service import llm_service
from .observability import observe

logger = logging.getLogger("gov_scheme.tools.generator")

GENERATOR_SYSTEM_PROMPT = """You are the official myScheme Indian Government Welfare Scheme AI Assistant.
Your mission is to provide clear, empathetic, citizen-centric, and 100% evidence-grounded answers.

CRITICAL RULES ON QUESTIONS & FORMATTING (STRICTLY ENFORCED):
- NEVER WRITE QUESTIONS, CHECKLISTS OF OPTIONS, OR QUESTIONNAIRES IN YOUR TEXT RESPONSE.
- The web application automatically renders a dedicated interactive questionnaire card below your response for any missing criteria.
- In the text response, your role during the Middle Stage is ONLY to:
  * Warmly introduce the candidate schemes discovered.
  * Highlight their financial assistance amounts and key benefits.
  * Politely invite the citizen to fill in the interactive questions card shown below.
- Do NOT write things like "Please answer the following questions:", "[ ] Yes", "[ ] No", "Enter amount:", or bulleted lists of questions. Doing so is redundant and strictly forbidden.

GUIDING PRINCIPLES:
1. ADAPTIVE TO CONVERSATIONAL STAGE:
   - If Citizen has submitted questionnaire answers or query is an ELIGIBILITY EVALUATION:
     * PRIMARY MANDATE: YOUR MAIN FOCUS MUST BE DELIVERING A FULL, AUTHORITATIVE ELIGIBILITY EVALUATION FOR EACH SCHEME.
     * Deliver an Executive Verdict for each scheme: "✅ ELIGIBLE (Meets Captured Criteria)", "⚠️ CONDITIONAL (Requires Additional Verification)", or "❌ INELIGIBLE (Criteria Not Satisfied)".
     * Include a Markdown Criteria Evaluation Table:
       | Rule / Condition | Required Criteria | Your Detail | Status |
     * Calculate and clearly state the exact Financial Assistance / Subsidy amount they are entitled to receive.
     * Provide the mandatory Document Checklist required for submission.
     * Provide step-by-step application directions and direct link to the verified official portal (*.gov.in / *.nic.in).
     * DO NOT treat this as an initial discovery search; DO NOT ask the user to fill out the questionnaire again. Focus 100% on the evaluation.
   - If questions are being asked (Middle Stage - only if initial inquiry with zero profile):
     * Warmly introduce the candidate schemes discovered.
     * Highlight their key financial benefits and who they are designed for.
     * Politely explain that to confirm their exact eligibility tier or subsidy amount, they should answer the quick interactive questions presented on the card below.
   - If profile is complete (Final Stage):
     * Deliver a clear eligibility verdict based on the criteria.
     * Clearly summarize the financial assistance / subsidy / grant amount.
     * Provide an official Document Checklist required for application.
     * Provide the authentic official portal link (*.gov.in / *.nic.in) to apply.
   - If Workflow is COMPARISON:
     * Provide a clear side-by-side comparison table (benefits, eligibility limits, interest rates/subsidies, nodal ministry).
   - If Workflow is PROCEDURAL_GUIDE:
     * Provide a numbered, step-by-step application walkthrough (Online DigiLocker/Aadhaar registration vs Offline CSC center).
   - If Candidate Schemes list is EMPTY:
     * State clearly, politely, and transparently that no direct scheme matching this exact query was found in the official national repository.
     * Guide the citizen on which nodal ministry (e.g., Ministry of Agriculture, Ministry of MSME, State Department) or district office to contact for local or unindexed grants.
     * DO NOT invent fake schemes. Provide actionable next steps.

2. GROUNDING & HONESTY:
   - Ground all claims in the provided scheme guidelines and quotes.
   - Do not invent non-existent benefits or guarantee approvals.
   - Use clean, readable GitHub Markdown with emojis, bullet points, and bold section headers.

3. MULTILINGUAL & VERNACULAR SCRIPT SYNTHESIS:
   - When Target Language is NOT English (e.g., Kannada 'kn', Hindi 'hi', Bengali 'bn', Marathi 'mr', Tamil 'ta', Telugu 'te', Gujarati 'gu'):
     * Write the ENTIRE text response ('answer_markdown') and all 'key_takeaways' in authentic regional script (e.g., Kannada script ಕನ್ನಡ for Kannada, Devanagari script देवनागरी for Hindi/Marathi, Bengali script বাংলা, etc.).
     * Never generate transliterated English/Latin sentences when a regional language is requested (e.g., do not write 'nimma aayushya'; write 'ನಿಮ್ಮ ವಯಸ್ಸು').
     * PRESERVE OFFICIAL TECHNICAL ENTITIES:
       - Keep official scheme names identifiable: e.g. in Kannada: "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (PM-KCC Scheme)" or "ರೈತ ವಿದ್ಯಾನಿಧಿ ಯೋಜನೆ (Raita Vidyanidhi)".
       - Keep official URLs unchanged: e.g. [myScheme ಅಧಿಕೃತ ಪೋರ್ಟಲ್](https://www.myscheme.gov.in)
       - Keep Markdown table syntax (|---|) and status icons (✅, ⚠️, ❌) clean and intact.

Respond with JSON:
{
  "answer_markdown": "Full adaptive Markdown response for the citizen...",
  "key_takeaways": [
    "Key takeaway point 1",
    "Key takeaway point 2",
    "Key takeaway point 3"
  ]
}"""


class ResponseGeneratorTool:
    """
    Agentic Tool for Adaptive Free-Form Response Generation.
    Tool Name: 'response_generator_tool'
    """

    name: str = "response_generator_tool"
    description: str = (
        "Synthesizes natural, context-adaptive Markdown responses for citizens across all stages: "
        "introducing candidate schemes during clarification, issuing verdicts on completion, or comparing programs."
    )

    def __init__(self):
        self.llm = llm_service

    @observe(name="ResponseGeneratorTool.execute")
    def execute(
        self,
        user_query: str,
        workflow: str,
        candidate_schemes: List[Dict[str, Any]],
        questionnaire_status: Dict[str, Any],
        beneficiary_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        known_criteria: Optional[Dict[str, Any]] = None,
        evaluated_schemes: Optional[List[Dict[str, Any]]] = None,
        is_evaluation_turn: bool = False,
        target_language: str = "en",
        language_name: str = "English",
    ) -> Dict[str, Any]:
        """
        Executes adaptive free-form response generation with cross-lingual synthesis.
        """
        has_questions = bool(questionnaire_status.get("questions"))
        is_eval = is_evaluation_turn or workflow == "ELIGIBILITY_CHECK" or bool(evaluated_schemes and any(s.get("eligibility_matrix") for s in evaluated_schemes))

        if is_eval:
            stage_desc = (
                "ELIGIBILITY EVALUATION STAGE: The citizen has filled in their profile details / questionnaire. "
                "YOUR MAIN FOCUS MUST BE GIVING A FULL, RIGOROUS ELIGIBILITY EVALUATION FOR EACH SCHEME."
            )
        elif has_questions:
            stage_desc = (
                "MIDDLE STAGE (questions are being presented to the user to resolve remaining eligibility criteria)"
            )
        else:
            stage_desc = "FINAL STAGE (all criteria are resolved; deliver complete eligibility assessment)"

        compact_schemes = []
        for s in candidate_schemes[:4]:
            compact_schemes.append({
                "name": s.get("scheme_name") or s.get("name"),
                "jurisdiction": s.get("jurisdiction") or s.get("level") or "Central",
                "benefit": s.get("benefit") or (s.get("benefits") and s["benefits"][0]) or "Financial assistance",
                "eligibility_rules_summary": [
                    r.get("rule_text") or f"{r.get('field')} {r.get('operator')} {r.get('value')}"
                    for r in s.get("eligibility_rules", [])[:6] if isinstance(r, dict)
                ],
                "documents": s.get("documents", [])[:4],
                "application_steps": s.get("application_steps", [])[:3],
                "official_url": s.get("url") or (s.get("sources") and s["sources"][0].get("url")),
            })

        eval_summary = []
        if evaluated_schemes:
            for s in evaluated_schemes[:4]:
                s_name = s.get("scheme_name") or s.get("name")
                verdict = s.get("eligibility_status", "unknown")
                rule_checks = []
                for chk in s.get("eligibility_matrix", []):
                    rule_checks.append({
                        "rule": chk.get("label") or chk.get("rule_text") or f"{chk.get('field')} {chk.get('operator')} {chk.get('value')}",
                        "status": chk.get("status", "UNKNOWN"),
                    })
                eval_summary.append({
                    "scheme_name": s_name,
                    "overall_verdict": verdict,
                    "rule_evaluations": rule_checks,
                    "benefit": s.get("benefit") or (s.get("benefits") and s["benefits"][0]) or "Financial assistance",
                    "documents": s.get("documents", [])[:4],
                    "official_url": s.get("url"),
                })

        schemes_str = json.dumps(compact_schemes, ensure_ascii=False)
        eval_str = json.dumps(eval_summary, ensure_ascii=False, indent=2)
        q_status_str = json.dumps(questionnaire_status, ensure_ascii=False)
        criteria_str = json.dumps(known_criteria or {}, ensure_ascii=False)
        beneficiary_str = json.dumps(beneficiary_context or {}, ensure_ascii=False)

        prompt = f"""Current Conversational Stage: {stage_desc}
Workflow Type: {workflow}
User Query: "{user_query}"
Target Beneficiary: {beneficiary_str}
Known Criteria So Far: {criteria_str}

Candidate Schemes:
{schemes_str}

Deterministic Eligibility Evaluation Matrix:
{eval_str}

Questionnaire Status:
{q_status_str}

TARGET CITIZEN LANGUAGE: {language_name} (code: '{target_language}')
IMPORTANT LANGUAGE INSTRUCTIONS:
- Generate the entire Markdown response and all key takeaways in authentic {language_name} using native {language_name} script (e.g. Kannada script ಕನ್ನಡ for Kannada, Devanagari script for Hindi/Marathi, Bengali script for Bengali).
- Maintain an empathetic, culturally respectful, and clear government counselor tone.
- PRESERVE: Keep official scheme acronyms (e.g. PM-KISAN, Ayushman Bharat, Raita Vidyanidhi), official portal URLs (*.gov.in / *.nic.in), and Markdown table structure intact.

Generate a helpful, empathetic, beautifully structured Markdown response for the citizen."""

        result = self.llm._call_groq_json(
            prompt=prompt,
            system_prompt=GENERATOR_SYSTEM_PROMPT,
            timeout=settings.LLM_TIMEOUT_SECONDS,
        )

        if result and isinstance(result, dict) and "answer_markdown" in result:
            return result

        logger.warning("ResponseGeneratorTool LLM call returned invalid response; using fallback synthesis.")
        return self._fallback_generation(
            user_query=user_query,
            candidate_schemes=candidate_schemes,
            questionnaire_status=questionnaire_status,
            evaluated_schemes=evaluated_schemes,
            is_evaluation_turn=is_eval,
            known_criteria=known_criteria,
            target_language=target_language,
            language_name=language_name,
        )

    def _fallback_generation(
        self,
        user_query: str,
        candidate_schemes: List[Dict[str, Any]],
        questionnaire_status: Dict[str, Any],
        evaluated_schemes: Optional[List[Dict[str, Any]]] = None,
        is_evaluation_turn: bool = False,
        known_criteria: Optional[Dict[str, Any]] = None,
        target_language: str = "en",
        language_name: str = "English",
    ) -> Dict[str, Any]:
        """Deterministic safety fallback for response synthesis."""
        has_questions = bool(questionnaire_status.get("questions"))
        lines = []

        is_kn = target_language == "kn"
        is_hi = target_language in ("hi", "mr")

        # Localized header labels
        if is_kn:
            title_eval = "## 📋 ಅಧಿಕೃತ ಅರ್ಹತಾ ಮೌಲ್ಯಮಾಪನ ವರದಿ\n"
            desc_eval = "ನೀವು ಸಲ್ಲಿಸಿದ ಅರ್ಹತಾ ವಿವರಗಳ ಆಧಾರದ ಮೇಲೆ, ಸರ್ಕಾರದ ಮಾರ್ಗಸೂಚಿಗಳ ಪರಿಶೀಲನೆ ಇಲ್ಲಿದೆ:\n"
            benefit_lbl = "ಸೌಲಭ್ಯ ಮತ್ತು ಸಹಾಯಧನ:"
            docs_lbl = "ಅಗತ್ಯ ದಾಖಲೆಗಳು:"
            portal_lbl = "ಅಧಿಕೃತ ಪೋರ್ಟಲ್:"
        elif is_hi:
            title_eval = "## 📋 आधिकारिक पात्रता मूल्यांकन रिपोर्ट\n"
            desc_eval = "आपके द्वारा दिए गए पात्रता विवरण के आधार पर आधिकारिक मूल्यांकन:\n"
            benefit_lbl = "लाभ एवं वित्तीय सहायता:"
            docs_lbl = "आवश्यक दस्तावेज:"
            portal_lbl = "आधिकारिक पोर्टल:"
        else:
            title_eval = "## 📋 Official Eligibility Evaluation Report\n"
            desc_eval = "Based on the eligibility details you submitted, here is your verified evaluation against official government guidelines:\n"
            benefit_lbl = "Entitlement & Benefit:"
            docs_lbl = "Required Documents:"
            portal_lbl = "Official Portal:"

        # If this is an eligibility evaluation query, output full evaluation report
        if (is_evaluation_turn or evaluated_schemes) and candidate_schemes:
            lines.append(title_eval)
            lines.append(desc_eval)

            schemes_to_render = evaluated_schemes if evaluated_schemes else candidate_schemes
            for idx, s in enumerate(schemes_to_render[:4], 1):
                s_name = s.get("scheme_name") or s.get("name")
                s_level = s.get("jurisdiction") or s.get("level") or "Central"
                s_benefit = s.get("benefit") or (s.get("benefits") and s["benefits"][0]) or "Financial assistance"
                s_url = s.get("url") or "https://www.myscheme.gov.in"
                verdict = s.get("eligibility_status", "meets_captured_rules")
                rules_matrix = s.get("eligibility_matrix", [])

                if verdict == "meets_captured_rules":
                    verdict_badge = "✅ **Eligible: Meets Captured Criteria**"
                elif verdict == "ineligible":
                    verdict_badge = "❌ **Not Eligible: Criteria Not Satisfied**"
                else:
                    verdict_badge = "⚠️ **Conditional: Additional Details Required**"

                lines.append(f"### {idx}. **{s_name}** ({s_level})")
                lines.append(f"{verdict_badge}\n")
                lines.append(f"- **💰 {benefit_lbl}** {s_benefit}")

                if rules_matrix:
                    lines.append("\n**Criteria Verification Breakdown:**")
                    lines.append("| Eligibility Condition | Verification Status |")
                    lines.append("| :--- | :--- |")
                    for rule in rules_matrix[:6]:
                        r_label = rule.get("label") or rule.get("rule_text") or f"{rule.get('field')} {rule.get('operator')} {rule.get('value')}"
                        st = rule.get("status", "MET")
                        st_icon = "✅ MET" if st == "MET" else ("❌ NOT MET" if st == "NOT_MET" else "ℹ️ UNKNOWN")
                        lines.append(f"| {r_label} | {st_icon} |")

                docs = s.get("documents", [])
                if docs:
                    lines.append(f"\n- **📑 {docs_lbl}** {', '.join(docs[:4])}")

                lines.append(f"- **🌐 {portal_lbl}** [Apply on verified myScheme portal]({s_url})\n")

            return {
                "answer_markdown": "\n".join(lines),
                "key_takeaways": [
                    f"Completed full eligibility evaluation across {len(schemes_to_render)} official schemes.",
                    "Review the criteria checklist and document list above before submitting your application.",
                ],
            }

        if candidate_schemes:
            if is_kn:
                lines.append("🙏 **ನಿಮ್ಮ ಅಗತ್ಯಕ್ಕೆ ಹೊಂದಿಕೆಯಾಗುವ ಅಧಿಕೃತ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು:**\n")
            elif is_hi:
                lines.append("🙏 **आपकी आवश्यकता के अनुसार आधिकारिक सरकारी कल्याणकारी योजनाएं:**\n")
            else:
                lines.append("🙏 **Here are the official Government welfare schemes matching your request:**\n")

            for idx, s in enumerate(candidate_schemes[:4], 1):
                s_name = s.get("scheme_name") or s.get("name")
                s_level = s.get("jurisdiction") or s.get("level") or "Central"
                s_benefit = s.get("benefit") or (s.get("benefits") and s["benefits"][0]) or "Financial assistance"
                s_url = s.get("url") or "https://www.myscheme.gov.in"

                lines.append(f"### {idx}. **{s_name}** ({s_level})")
                lines.append(f"- **Key Benefit:** {s_benefit}")
                lines.append(f"- **Official Portal:** [View on myScheme]({s_url})\n")

            if has_questions:
                if is_kn:
                    lines.append("📋 **ಸಂಪೂರ್ಣ ಅರ್ಹತೆಯನ್ನು ಪರಿಶೀಲಿಸಲು ದಯವಿಟ್ಟು ಕೆಳಗಿನ ತ್ವರಿತ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಿ.**")
                elif is_hi:
                    lines.append("📋 **अपनी पूर्ण पात्रता जांचने के लिए कृपया नीचे दिए गए त्वरित प्रश्नों के उत्तर दें।**")
                else:
                    lines.append("📋 **Please answer the quick questions below** to verify your complete eligibility tier.")
            else:
                if is_kn:
                    lines.append("✅ **ನೀವು ಒದಗಿಸಿದ ವಿವರಗಳ ಪ್ರಕಾರ ಈ ಕಾರ್ಯಕ್ರಮಗಳಿಗೆ ನೀವು ಅರ್ಹರಾಗಿದ್ದೀರಿ.**")
                elif is_hi:
                    lines.append("✅ **प्रदान किए गए विवरण के आधार पर आप इन योजनाओं के लिए पात्र हैं।**")
                else:
                    lines.append("✅ **Based on the criteria provided, you meet the captured requirements for these programs.**")
        else:
            if is_kn:
                lines.append("ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ಸೂಕ್ತವಾದ ಯೋಜನೆಗಳಿಗಾಗಿ ಅಧಿಕೃತ myScheme ರಾಷ್ಟ್ರೀಯ ಭಂಡಾರದಲ್ಲಿ ಹುಡುಕಲಾಗಿದೆ.")
                lines.append("ದಯವಿಟ್ಟು ನಿಮ್ಮ ಅಗತ್ಯದ ಕ್ಷೇತ್ರವನ್ನು ನಿರ್ದಿಷ್ಟಪಡಿಸಿ (ಉದಾಹರಣೆಗೆ: ರೈತ ಸಹಾಯಧನ, ಶಿಕ್ಷಣ ವಿದ್ಯಾರ್ಥಿವೇತನ, ಆರೋಗ್ಯ ವಿಮೆ, ಅಥವಾ ವ್ಯಾಪಾರ ಸಾಲ).")
            elif is_hi:
                lines.append("मैंने आपके प्रश्न के अनुसार आधिकारिक myScheme राष्ट्रीय रिपॉजिटरी में खोज की है।")
                lines.append("कृपया अपनी आवश्यकता का क्षेत्र स्पष्ट करें (जैसे: किसान सब्सिडी, शिक्षा छात्रवृत्ति, स्वास्थ्य बीमा, या व्यापार ऋण)।")
            else:
                lines.append("I searched the official myScheme national repository for welfare programs matching your query.")
                lines.append("Please specify your primary area of need (e.g., farming subsidies, education scholarships, health insurance, or business loans) to see tailored schemes.")

        return {
            "answer_markdown": "\n".join(lines),
            "key_takeaways": [
                f"Evaluated {len(candidate_schemes)} official schemes from myScheme repository."
            ],
        }

    def run(self, **kwargs) -> Dict[str, Any]:
        """Convenience alias for execute."""
        return self.execute(**kwargs)


# Global singleton instance
response_generator_tool = ResponseGeneratorTool()
