from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    query: str = Field(..., description="Citizen request for relevant government schemes and eligibility")
    force_live_crawl: bool = Field(False, description="Bypass cache and force live HTTP crawl of selected repository pages")
    user_clarification: Optional[str] = Field(None, description="User response providing State/UT or scheme-specific profile details")
    user_profile: Optional[Dict[str, Any]] = Field(None, description="Explicit profile answers used only for supported, source-quoted criteria")
    conversation_history: Optional[List[Dict[str, Any]]] = Field(None, description="Previous conversation turns for multi-turn dialogue")

class AgentQueryResponse(BaseModel):
    query: str
    answer: str
    key_takeaways: List[str] = []
    eligibility_checklist: List[Dict[str, Any]] = []
    eligibility_matrix: List[Dict[str, Any]] = []
    eligibility_status: str = "not_evaluated"
    best_match_scheme: Optional[Dict[str, Any]] = None
    other_schemes: List[Dict[str, Any]] = []
    profiler_questions: List[Dict[str, Any]] = []
    conflict_alert: Optional[Dict[str, Any]] = None
    resolution: Optional[Dict[str, Any]] = None
    missing_details: Optional[Dict[str, Any]] = None
    agent_trace: List[Dict[str, Any]]
    extracted_schemes: List[Dict[str, Any]]
    portal_results: List[Dict[str, Any]] = []
    crawled_sources: List[Dict[str, Any]]
    crawler_metrics: Dict[str, Any]
    welfare_stack: Optional[Dict[str, Any]] = None
    cross_scheme_conflicts: List[Dict[str, Any]] = []

class CrawlUrlRequest(BaseModel):
    url: str = Field(..., description="URL of an authentic Indian Government portal (*.gov.in / *.nic.in)")
    force_refresh: bool = Field(False, description="Bypass cache and force real-time fetch")
    deep_crawl: bool = Field(True, description="Enable 2-hop deep crawling of scheme guidelines and circulars")
    max_subpages: int = Field(2, description="Maximum number of candidate guideline subpages or PDFs to crawl")
