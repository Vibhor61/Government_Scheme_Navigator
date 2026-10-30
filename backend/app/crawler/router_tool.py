"""
Router Tool: Agentic Tool Interface for Query Routing and Scope Classification.
Wraps SchemeRouter to provide standard tool execution for agentic planners.
"""

import logging
from typing import Any, Dict, List, Optional
from .router import scheme_router, SchemeRouter
from .observability import observe

logger = logging.getLogger("gov_scheme.tools.router")


class RouterTool:
    """
    Agentic Tool for Intent Classification, Scope Checking, and Criteria Extraction.
    Tool Name: 'scheme_router_tool'
    """

    name: str = "scheme_router_tool"
    description: str = (
        "Classifies citizen intent, detects out-of-domain questions, determines target workflow, "
        "decouples applicant from beneficiary, extracts open-ended criteria, and generates search signals."
    )

    def __init__(self, router_engine: Optional[SchemeRouter] = None):
        self.router = router_engine or scheme_router

    @observe(name="RouterTool.execute")
    def execute(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Executes Stage 2 routing on citizen query."""
        logger.info("Executing RouterTool for query: '%s'", (user_query or "")[:60])
        return self.router.route(
            user_query=user_query,
            conversation_history=conversation_history,
            user_profile=user_profile,
        )

    def run(self, **kwargs) -> Dict[str, Any]:
        """Convenience alias for execute."""
        return self.execute(**kwargs)


# Global singleton instance
router_tool = RouterTool()
