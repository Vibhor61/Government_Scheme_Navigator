"""
Autonomous Scheme Intelligence Agent & Multi-Step Planner
Coordinates the 5 specialized assistant tools into a unified execution plan:
  Step 1: Parse Intent & Beneficiary (decouple applicant from beneficiary, extract context).
  Step 2: Plan & Execute Official Portal Searches (exact *.gov.in / *.nic.in allowlist).
  Step 3: Deep Crawl & Harvest Evidence (2-hop crawl, SPA hydration, streaming PDF parsing).
  Step 4: Quoted Evidence Extraction & Deterministic Matrix Evaluation (zero hallucinations).
  Step 5: Generate Non-Redundant Targeted Questionnaire (all in one go, dropdowns > 4, radio <= 4).
"""

import logging
import time
from typing import Any, Dict, List, Optional

from .scheme_discovery_workflow import run_scheme_discovery_workflow
from .questionnaire_engine import questionnaire_engine
from .crawler_engine import gov_crawler
from .llm_service import llm_service
from .whitelist import is_valid_gov_host, sanitize_gov_url
from .router_tool import router_tool
from .crawler_tool import crawler_tool

logger = logging.getLogger("gov_scheme.agent_planner")


class SchemeAgentPlanner:
    """
    Autonomous multi-step planner for citizen scheme discovery and eligibility resolution.
    Orchestrates search, deep crawling, evidence checking, and dynamic profiling.
    """

    def __init__(self):
        self.router_tool = router_tool
        self.crawler_tool = crawler_tool
        self.questionnaire = questionnaire_engine
        self.crawler = gov_crawler
        self.llm = llm_service

    def plan_execution_steps(
        self,
        user_query: str,
        user_profile: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generates a transparent multi-step execution plan:
        1. Context & Beneficiary Intent Analysis
        2. Official Scheme Discovery & Repository Search
        3. Deep Crawling of Official Guidelines & PDF Circulars
        4. Quoted-Rule Extraction & Deterministic Profile Check
        5. Single-Turn Targeted Questionnaire Formulation
        """
        known_profile = self.questionnaire.extract_known_profile_from_context(
            user_query=user_query,
            conversation_history=conversation_history,
            user_profile=user_profile
        )

        steps = [
            {
                "step": 1,
                "tool": "parse_intent_and_beneficiary",
                "objective": "Analyze citizen request, decouple applicant from beneficiary, and extract known attributes.",
                "known_attributes": list(known_profile.keys()),
            },
            {
                "step": 2,
                "tool": "myscheme_search",
                "objective": "Query official government repository with exact *.gov.in allowlist enforcement.",
                "scope": "Central + State" if known_profile.get("state") else "Central (withhold State until confirmed)",
            },
            {
                "step": 3,
                "tool": "crawl_scheme_details",
                "objective": "2-hop deep crawl of candidate guidelines and official circular PDFs.",
                "features": ["SPA Hydration", "In-Memory PDF Parsing", "SSL Fallback Tolerance"],
            },
            {
                "step": 4,
                "tool": "extract_and_validate_rule_record",
                "objective": "Extract eligibility rules backed exclusively by exact verbatim quotations from official text.",
                "guardrail": "Zero hallucination: uncited criteria remain UNKNOWN.",
            },
            {
                "step": 5,
                "tool": "build_targeted_questionnaire",
                "objective": "Ask all missing criteria in one single turn without redundancy; options > 4 as dropdown, <= 4 as radio.",
                "status": "Evaluated after rule synthesis",
            }
        ]
        return steps

    def run(
        self,
        user_query: str,
        force_live_crawl: bool = False,
        user_clarification: Optional[str] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Executes the autonomous agent workflow across all 5 tools.
        """
        logger.info("Executing autonomous agent planner for query: %s", user_query[:60])
        response = run_scheme_discovery_workflow(
            user_query=user_query,
            force_live_crawl=force_live_crawl,
            user_clarification=user_clarification,
            user_profile=user_profile,
            conversation_history=conversation_history,
        )

        # Attach high-level planning trace if agent_trace list was produced by workflow
        if isinstance(response, dict) and "agent_trace" in response:
            if not any(t.get("type") == "AGENT_PLANNER" for t in response["agent_trace"]):
                plan_steps = self.plan_execution_steps(
                    user_query=user_query,
                    user_profile=user_profile,
                    conversation_history=conversation_history
                )
                response["agent_trace"].insert(0, {
                    "step": 0,
                    "type": "AGENT_PLANNER",
                    "title": "Autonomous 5-Tool Execution Plan",
                    "observation": "Generated 5-step verified execution plan across authentic government portals.",
                    "details": plan_steps,
                    "latency_ms": 0,
                    "status": "PLANNED",
                })
        return response


# Compatibility alias
AutonomousAgentPlanner = SchemeAgentPlanner
CrawlerAgent = SchemeAgentPlanner

# Global agent singleton
crawler_agent = SchemeAgentPlanner()
