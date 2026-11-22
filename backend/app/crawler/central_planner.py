"""
Central Agent Planner: Unified 4-Tool Orchestrator for Citizen Welfare Exploration.
Coordinates:
  1. Stage 0: Deterministic Input Security Guardrails (0ms defense)
  2. Tool 1: RouterTool (intent, scope, open-ended criteria, beneficiary)
  3. Tool 2: CrawlerTool (whitelist-enforced portal search and detail extraction)
  4. Tool 3: QuestionnaireTool (dynamic semantic diffing: never repeat, never miss)
  5. Tool 4: ResponseGeneratorTool (adaptive free-form Markdown synthesis)
"""

import json
import logging
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from .domain_guard import (
    check_domain_guard,
    generate_greeting_response,
    generate_ood_refusal,
)
from .router_tool import router_tool, RouterTool
from .crawler_tool import crawler_tool, CrawlerTool, MYSCHEME_PORTAL
from .questionnaire_tool import questionnaire_tool, QuestionnaireTool
from .generator_tool import response_generator_tool, ResponseGeneratorTool
from .myscheme_catalog import MYSCHEME_FLAGSHIP_CATALOG
from .scheme_rules import evaluate_schemes
from .policy_interaction_engine import PolicyInteractionEngine
from .observability import observe, flush_telemetry

logger = logging.getLogger("gov_scheme.central_planner")


class CentralAgentPlanner:
    """
    Central ReAct Orchestrator coordinating RouterTool, CrawlerTool,
    QuestionnaireTool, and ResponseGeneratorTool into a seamless citizen experience.
    """

    def __init__(
        self,
        router: Optional[RouterTool] = None,
        crawler: Optional[CrawlerTool] = None,
        questionnaire: Optional[QuestionnaireTool] = None,
        generator: Optional[ResponseGeneratorTool] = None,
    ):
        self.router = router or router_tool
        self.crawler = crawler or crawler_tool
        self.questionnaire = questionnaire or questionnaire_tool
        self.generator = generator or response_generator_tool

    @observe(name="CentralAgentPlanner.run")
    def run(
        self,
        user_query: str,
        force_live_crawl: bool = False,
        user_clarification: Optional[str] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        language: Optional[str] = "auto",
    ) -> Dict[str, Any]:
        """
        Executes the 5-step agentic orchestration cycle.
        """
        started = time.time()
        trace: List[Dict[str, Any]] = []

        # =========================================================================
        # STAGE 0: Fast Deterministic Security Guardrails (< 1ms)
        # =========================================================================
        guard_status, guard_message = check_domain_guard(
            query=user_query,
            user_clarification=user_clarification,
            conversation_history=conversation_history,
            user_profile=user_profile,
            lang_code=language,
        )

        if guard_status in ("FLOODING_SPAM", "SECURITY_BLOCKED", "PROMPT_INJECTION", "OUT_OF_DOMAIN"):
            lat = round((time.time() - started) * 1000, 2)
            trace.append({
                "step": 0,
                "type": "GUARD",
                "title": f"Security Guardrail: {guard_status}",
                "observation": guard_message or "Security check intercepted input.",
                "status": guard_status,
                "latency_ms": lat,
            })
            return {
                "query": user_query,
                "answer": guard_message or "Input stopped by security filter.",
                "key_takeaways": [
                    "Query lies outside the scope of Indian Government welfare schemes."
                    if guard_status == "OUT_OF_DOMAIN"
                    else f"Input was blocked by {guard_status} guardrail."
                ],
                "eligibility_checklist": [],
                "eligibility_matrix": [],
                "eligibility_status": guard_status.lower(),
                "best_match_scheme": None,
                "other_schemes": [],
                "profiler_questions": [],
                "conflict_alert": None,
                "resolution": None,
                "missing_details": None,
                "agent_trace": trace,
                "extracted_schemes": [],
                "portal_results": [],
                "crawled_sources": [],
                "crawler_metrics": {
                    "total_execution_ms": int(lat),
                    "security_whitelist_passed": guard_status != "SECURITY_BLOCKED",
                    "guard_status": guard_status,
                },
            }

        # =========================================================================
        # TOOL 1: RouterTool (Intent, Scope, Open-Ended Criteria, Beneficiary)
        # =========================================================================
        t1_start = time.time()
        router_res = self.router.run(
            user_query=user_query,
            conversation_history=conversation_history,
            user_profile=user_profile,
            preferred_language=language,
        )
        t1_lat = round((time.time() - t1_start) * 1000, 2)

        from .router import LANGUAGE_NAMES
        detected_lang = router_res.get("detected_language") or "en"
        detected_name = router_res.get("language_name") or "English"
        script_type = router_res.get("script_type") or "latin"

        if language and language != "auto" and language in LANGUAGE_NAMES:
            target_lang = language
            target_lang_name = LANGUAGE_NAMES[language]
        else:
            target_lang = detected_lang
            target_lang_name = detected_name

        # Check for upstream AI service unavailable / rate limit -> recover via deterministic router
        if router_res.get("is_service_unavailable"):
            logger.warning("Router reported service unavailable / rate limit; activating deterministic fallback routing.")
            router_res = self.router._fallback_route(
                user_query=user_query,
                conversation_history=conversation_history,
                user_profile=user_profile,
                preferred_language=language,
            )
            detected_lang = router_res.get("detected_language") or "en"
            detected_name = router_res.get("language_name") or "English"
            script_type = router_res.get("script_type") or "latin"

            if language and language != "auto" and language in LANGUAGE_NAMES:
                target_lang = language
                target_lang_name = LANGUAGE_NAMES[language]
            else:
                target_lang = detected_lang
                target_lang_name = detected_name

        # Check for Out-of-Domain via Router LLM
        if router_res.get("is_out_of_domain"):
            ood_answer = router_res.get("polite_ood_refusal")
            # If router polite refusal is missing or doesn't match regional script, use canonical localized template
            if not ood_answer or (target_lang != "en" and not re.search(r"[^\u0000-\u007F]", ood_answer)):
                ood_answer = generate_ood_refusal(user_query, lang_code=target_lang)
            trace.append({
                "step": 1,
                "type": "ROUTER",
                "tool_name": self.router.name,
                "title": "Stage 1: Intent Routing (Out-of-Domain Intercepted)",
                "observation": router_res.get("out_of_domain_reason") or "Non-welfare inquiry deflected with official guidance.",
                "status": "OUT_OF_DOMAIN",
                "latency_ms": t1_lat,
            })
            return {
                "query": user_query,
                "answer": ood_answer,
                "key_takeaways": ["Query lies outside the scope of Indian Government welfare schemes."],
                "eligibility_checklist": [],
                "eligibility_matrix": [],
                "eligibility_status": "out_of_domain",
                "best_match_scheme": None,
                "other_schemes": [],
                "profiler_questions": [],
                "conflict_alert": None,
                "resolution": None,
                "missing_details": None,
                "agent_trace": trace,
                "extracted_schemes": [],
                "portal_results": [],
                "crawled_sources": [],
                "crawler_metrics": {
                    "total_execution_ms": int(t1_lat),
                    "security_whitelist_passed": True,
                    "guard_status": "OUT_OF_DOMAIN",
                },
            }

        # Check for pure greeting
        if router_res.get("workflow") == "GREETING":
            if target_lang == "kn":
                greet_ans = (
                    "🙏 **ನಮಸ್ಕಾರ! ನಾನು ಜನಸಹಾಯಕ AI (JanSahayak AI) - ಭಾರತ ಸರ್ಕಾರದ ಅಧಿಕೃತ ಯೋಜನೆಗಳ ಮಾರ್ಗದರ್ಶಿ ಸಹಾಯಕ.**\n\n"
                    "ನಾನು ನಿಮಗೆ ಕೇಂದ್ರ ಮತ್ತು ರಾಜ್ಯ ಸರ್ಕಾರಗಳ ಅಧಿಕೃತ ಯೋಜನೆಗಳು, ಕೃಷಿ ಸಹಾಯಧನ, ವಿದ್ಯಾರ್ಥಿವೇತನ ಮತ್ತು ಸಾಲಗಳ ಬಗ್ಗೆ ಅಧಿಕೃತ ಮಾಹಿತಿಯನ್ನು ಒದಗಿಸುತ್ತೇನೆ.\n\n"
                    "**ನೀವು ಯಾವುದರ ಬಗ್ಗೆ ತಿಳಿಯಲು ಬಯಸುತ್ತೀರಿ?**\n"
                    "- 🌾 ಕೃಷಿ ಮತ್ತು ರೈತ ಕಲ್ಯಾಣ ಯೋಜನೆಗಳು (PM-KISAN, KCC, ಕೃಷಿ ಯಂತ್ರೋಪಕರಣಗಳು)\n"
                    "- 🎓 ವಿದ್ಯಾರ್ಥಿವೇತನ ಮತ್ತು ಶಿಕ್ಷಣ ನೆರವು (ರೈತ ವಿದ್ಯಾನಿಧಿ, ಮೆಟ್ರಿಕ್ ನಂತರದ ಸ್ಕಾಲರ್‌ಶಿಪ್)\n"
                    "- 💼 ವ್ಯಾಪಾರ ಸಾಲಗಳು ಮತ್ತು ಮುದ್ರಾ ಯೋಜನೆ (Mudra, PMEGP)\n"
                    "- 🏥 ಆಯುಷ್ಮಾನ್ ಭಾರತ್ ಮತ್ತು ಆರೋಗ್ಯ ವಿಮೆ"
                )
            elif target_lang in ("hi", "mr"):
                greet_ans = (
                    "🙏 **नमस्ते! मैं जनसहायक AI (JanSahayak AI) हूँ - भारत सरकार की योजनाओं का आधिकारिक सहायक।**\n\n"
                    "मैं myScheme राष्ट्रीय रिपॉजिटरी से सत्यापित योजनाओं, सब्सिडी, छात्रवृत्ति और ऋणों की सही जानकारी प्रदान करता हूँ।\n\n"
                    "**आप किस प्रकार की योजना की तलाश कर रहे हैं?**\n"
                    "- 🌾 कृषि एवं किसान कल्याण (PM-KISAN, KCC, कृषि यंत्र सब्सिडी)\n"
                    "- 🎓 छात्रवृत्ति एवं शिक्षा सहायता (Post-Matric, National Scholarship)\n"
                    "- 💼 व्यवसाय ऋण (Mudra, PMEGP)\n"
                    "- 🏥 स्वास्थ्य एवं चिकित्सा सहायता (Ayushman Bharat)"
                )
            else:
                greet_ans = generate_greeting_response()

            trace.append({
                "step": 1,
                "type": "ROUTER",
                "tool_name": self.router.name,
                "title": f"Stage 1: Welcome & Orientation ({target_lang_name})",
                "observation": f"Greeting handled in {target_lang_name} [{target_lang}].",
                "status": "GREETING",
                "latency_ms": t1_lat,
            })
            return {
                "query": user_query,
                "answer": greet_ans,
                "key_takeaways": [f"Welcome to the official myScheme Indian Government Welfare Assistant ({target_lang_name})."],
                "eligibility_checklist": [],
                "eligibility_matrix": [],
                "eligibility_status": "greeting",
                "best_match_scheme": None,
                "other_schemes": [],
                "profiler_questions": [],
                "conflict_alert": None,
                "resolution": None,
                "missing_details": None,
                "agent_trace": trace,
                "extracted_schemes": [],
                "portal_results": [],
                "crawled_sources": [],
                "crawler_metrics": {
                    "total_execution_ms": int(t1_lat),
                    "security_whitelist_passed": True,
                    "guard_status": "GREETING",
                },
                "detected_language": target_lang,
                "language_name": target_lang_name,
            }

        beneficiary = router_res.get("beneficiary", {})
        extracted_criteria = router_res.get("extracted_criteria", {})
        target_schemes = router_res.get("target_schemes", [])
        search_terms = router_res.get("myscheme_search_terms", [])
        workflow = router_res.get("workflow", "SCHEME_DISCOVERY")

        # Detect if this turn is an eligibility questionnaire submission
        is_questionnaire_submission = bool(
            user_profile or
            user_clarification or
            workflow == "ELIGIBILITY_CHECK" or
            (conversation_history and any(
                isinstance(m, dict) and m.get("role") == "assistant" and any(k in str(m.get("content", "")).lower() for k in ["question", "eligibility", "confirm"])
                for m in conversation_history[-2:]
            ) and any(opt in user_query.lower() for opt in [":", "acre", "farmer", "student", "income", "lakh", "general", "obc", "sc", "st"]))
        )
        if is_questionnaire_submission:
            workflow = "ELIGIBILITY_CHECK"

        # Anchor on conversation context and prior schemes if user is answering follow-up questions
        history_schemes = []
        root_query = user_query
        if conversation_history:
            for m in reversed(conversation_history[-4:]):
                txt = str(m.get("content") or m.get("text") or "")
                for s in MYSCHEME_FLAGSHIP_CATALOG:
                    s_name = s.get("name", "")
                    s_slug = s.get("slug", "")
                    if s_name.lower() in txt.lower() or (s_slug and s_slug.lower() in txt.lower()):
                        if s["name"] not in [x["name"] for x in history_schemes]:
                            history_schemes.append(s)

            user_messages = [
                str(m.get("content") or m.get("text") or "").strip()
                for m in conversation_history
                if isinstance(m, dict) and (m.get("role") == "user" or m.get("sender") == "user")
            ]
            substantive = [
                q for q in user_messages
                if len(q.split()) > 3 and not any(q.lower() == opt for opt in ["male", "female", "urban", "rural", "yes", "no", "general", "obc", "sc", "st"]) and ":" not in q
            ]
            if substantive:
                root_query = substantive[-1]

        if is_questionnaire_submission and history_schemes and not target_schemes:
            target_schemes = [s["name"] for s in history_schemes]

        spec_queries = router_res.get("search_specification", {}).get("search_queries") or search_terms
        trace.append({
            "step": 1,
            "type": "ROUTER",
            "tool_name": self.router.name,
            "title": f"Stage 1: Intent & Cross-Lingual Routing ({target_lang_name} [{target_lang}])",
            "observation": (
                f"Workflow: {workflow}. Language: {target_lang_name} ({script_type}). "
                f"English search queries: {spec_queries[:2]}. "
                f"Beneficiary: {beneficiary.get('target_description', 'self')}. "
                f"Criteria extracted: {list(extracted_criteria.keys())}."
            ),
            "status": "COMPLETED",
            "latency_ms": t1_lat,
        })

        # =========================================================================
        # TOOL 2: CrawlerTool (Autonomous Search & Decision Gate)
        # =========================================================================
        t2_start = time.time()
        user_state = extracted_criteria.get("state") or (user_profile or {}).get("state")

        search_spec = router_res.get("search_specification") or {
            "core_intent": root_query[:80] if is_questionnaire_submission else user_query[:60],
            "target_sector": router_res.get("target_sector", ""),
            "target_role": beneficiary.get("applicant_role", "citizen"),
            "search_queries": ([root_query] if is_questionnaire_submission and root_query != user_query else []) + (search_terms or [user_query]),
            "must_include_keywords": [w for w in root_query.lower().split() if len(w) > 3] if is_questionnaire_submission else search_terms,
            "must_exclude_keywords": [],
            "target_schemes": target_schemes,
        }
        if "target_schemes" not in search_spec and target_schemes:
            search_spec["target_schemes"] = target_schemes

        crawler_res = self.crawler.discover_and_fetch(
            search_spec=search_spec,
            user_state=user_state,
            force_live_crawl=force_live_crawl,
        )
        candidate_schemes = crawler_res.get("candidate_schemes", [])

        # Retain candidate schemes from history during questionnaire evaluation
        if is_questionnaire_submission and history_schemes:
            existing_names = {s["name"] for s in candidate_schemes}
            for hs in history_schemes:
                if hs["name"] not in existing_names:
                    candidate_schemes.append(hs)
                    existing_names.add(hs["name"])

        # Root intent recovery for follow-up turns if search yielded 0 schemes
        if not candidate_schemes and conversation_history:
            user_messages = [
                str(m.get("content") or m.get("text") or "").strip()
                for m in conversation_history
                if isinstance(m, dict) and (m.get("role") == "user" or m.get("sender") == "user")
            ]
            substantive = [
                q for q in user_messages
                if len(q.split()) > 3 and not any(q.lower() == opt for opt in ["male", "female", "urban", "rural", "yes", "no", "general", "obc", "sc", "st"])
            ]
            if substantive:
                root_query = substantive[-1]
                logger.info("Follow-up turn '%s' yielded 0 schemes; re-anchoring discovery on root query '%s'", user_query, root_query)
                anchor_spec = {
                    "core_intent": root_query[:80],
                    "target_sector": router_res.get("target_sector", ""),
                    "target_role": beneficiary.get("applicant_role", "citizen"),
                    "search_queries": [root_query],
                    "must_include_keywords": [w for w in root_query.lower().split() if len(w) > 3],
                    "must_exclude_keywords": [],
                }
                retry_res = self.crawler.discover_and_fetch(
                    search_spec=anchor_spec,
                    user_state=user_state,
                    force_live_crawl=force_live_crawl,
                )
                candidate_schemes = retry_res.get("candidate_schemes", [])

        t2_lat = round((time.time() - t2_start) * 1000, 2)

        trace.append({
            "step": 2,
            "type": "CRAWLER",
            "tool_name": self.crawler.name,
            "title": f"Stage 2: Autonomous Scheme Discovery ({len(candidate_schemes)} approved)",
            "observation": (
                f"Evaluated {crawler_res.get('total_evaluated', 0)} repository records. "
                f"Approved {len(candidate_schemes)} schemes: "
                f"{', '.join(s.get('name', 'Scheme') for s in candidate_schemes[:3]) if candidate_schemes else 'No direct scheme matches passed gate'}. "
                f"Filtered {crawler_res.get('discarded_count', 0)} domain/role conflicts."
            ),
            "status": "COMPLETED",
            "latency_ms": t2_lat,
        })

        # =========================================================================
        # TOOL 3: QuestionnaireTool (Dynamic Semantic Diffing)
        # =========================================================================
        t3_start = time.time()
        merged_profile = {**(user_profile or {}), **extracted_criteria}
        if user_clarification:
            merged_profile["clarification"] = user_clarification

        if is_questionnaire_submission:
            # Citizen has submitted questionnaire answers; focus now transitions to full evaluation
            questions = []
            q_res = {"is_complete": True, "questions": [], "resolved_criteria": list(merged_profile.keys())}
        elif candidate_schemes:
            q_res = self.questionnaire.run(
                candidate_schemes=candidate_schemes,
                known_criteria=merged_profile,
                conversation_history=conversation_history,
                user_profile=user_profile,
                user_query=user_query,
                target_language=target_lang,
                target_language_name=target_lang_name,
            )
            questions = q_res.get("questions", [])
        else:
            q_res = {"is_complete": True, "questions": [], "resolved_criteria": []}
            questions = []

        t3_lat = round((time.time() - t3_start) * 1000, 2)
        questions = q_res.get("questions", [])

        trace.append({
            "step": 3,
            "type": "QUESTIONNAIRE",
            "tool_name": self.questionnaire.name,
            "title": f"Stage 3: Dynamic Questionnaire ({len(questions)} missing criteria)",
            "observation": (
                f"Resolved {len(q_res.get('resolved_criteria', []))} criteria. "
                f"Synthesized {len(questions)} interactive questions (is_complete={q_res.get('is_complete')})."
            ),
            "status": "COMPLETED",
            "latency_ms": t3_lat,
        })

        # =========================================================================
        # STAGE 4: Deterministic Rule Matrix Evaluation
        # =========================================================================
        evaluated = evaluate_schemes(candidate_schemes, merged_profile)

        # =========================================================================
        # TOOL 4: ResponseGeneratorTool (Adaptive Free-Form Markdown Synthesis)
        # =========================================================================
        t4_start = time.time()
        gen_res = self.generator.run(
            user_query=user_query,
            workflow=workflow,
            candidate_schemes=candidate_schemes,
            questionnaire_status={"has_questions": bool(questions), "questions": questions},
            beneficiary_context=beneficiary,
            conversation_history=conversation_history,
            known_criteria=merged_profile,
            evaluated_schemes=evaluated,
            is_evaluation_turn=is_questionnaire_submission,
            target_language=target_lang,
            language_name=target_lang_name,
        )
        t4_lat = round((time.time() - t4_start) * 1000, 2)

        trace.append({
            "step": 4,
            "type": "SYNTHESIZER",
            "tool_name": self.generator.name,
            "title": f"Stage 4: Adaptive Markdown Synthesis ({'Middle Stage' if questions else 'Final Stage'})",
            "observation": "Generated evidence-grounded response adapted to the current conversational state.",
            "status": "COMPLETED",
            "latency_ms": t4_lat,
        })

        # =========================================================================
        # STAGE 5: Policy Interaction, Cross-Scheme Conflicts & Stacking
        # =========================================================================
        t5_start = time.time()
        policy_res = PolicyInteractionEngine.evaluate(
            schemes=candidate_schemes,
            user_profile=merged_profile,
            user_query=user_query,
            crawled_results=[{"url": s.get("url", ""), "title": s.get("name", "")} for s in candidate_schemes],
            target_language=target_lang,
            language_name=target_lang_name,
        )
        t5_lat = round((time.time() - t5_start) * 1000, 2)

        conflicts_found = len(policy_res.get("cross_scheme_conflicts", []))
        has_stack = bool(policy_res.get("welfare_stack"))

        trace.append({
            "step": 5,
            "type": "POLICY_INTERACTION",
            "tool_name": "PolicyInteractionEngine",
            "title": f"Stage 5: Cross-Scheme Conflict & Stacking Intelligence ({conflicts_found} conflicts, {'Stack generated' if has_stack else 'No bundle needed'})",
            "observation": (
                f"Evaluated policy interactions across {len(candidate_schemes)} schemes. "
                f"Detected {conflicts_found} policy exclusion conflicts. "
                f"{'Formulated synergistic package: ' + policy_res['welfare_stack']['bundle_title'] if has_stack else 'No multi-scheme stacking bundle needed'}."
            ),
            "status": "COMPLETED",
            "latency_ms": t5_lat,
        })

        total_exec_ms = int((time.time() - started) * 1000)

        # Map eligibility status string
        if not user_state and any(s.get("level") == "State" for s in candidate_schemes):
            el_status = "needs_location"
        elif any(s.get("eligibility_status") == "meets_captured_rules" for s in evaluated):
            el_status = "matches_found"
        elif any(s.get("eligibility_status") == "ineligible" for s in evaluated):
            el_status = "ineligible"
        elif questions:
            el_status = "needs_information"
        else:
            el_status = "matches_found" if candidate_schemes else "not_evaluated"

        flush_telemetry()

        return {
            "query": user_query,
            "answer": gen_res.get("answer_markdown", ""),
            "key_takeaways": gen_res.get("key_takeaways", []),
            "eligibility_checklist": [],
            "eligibility_matrix": evaluated,
            "eligibility_status": el_status,
            "best_match_scheme": candidate_schemes[0] if candidate_schemes else None,
            "other_schemes": candidate_schemes[1:],
            "profiler_questions": questions,
            "conflict_alert": policy_res.get("conflict_alert"),
            "cross_scheme_conflicts": policy_res.get("cross_scheme_conflicts", []),
            "welfare_stack": policy_res.get("welfare_stack"),
            "resolution": None,
            "missing_details": None,
            "agent_trace": trace,
            "extracted_schemes": candidate_schemes,
            "portal_results": [],
            "crawled_sources": [{"url": s.get("url", ""), "title": s.get("name", "")} for s in candidate_schemes],
            "crawler_metrics": {
                "total_execution_ms": total_exec_ms,
                "portals_crawled": len(candidate_schemes),
                "security_whitelist_passed": True,
                "eligibility_evaluated": len(questions) == 0,
                "workflow_stage": workflow,
            },
            "detected_language": target_lang,
            "language_name": target_lang_name,
        }


# Global central planner singleton
central_planner = CentralAgentPlanner()
