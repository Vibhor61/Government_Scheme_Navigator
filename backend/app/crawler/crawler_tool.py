"""
Crawler Tool: Agentic Tool Interface for Whitelist-Enforced Government Portal Crawling.
Wraps GovCrawlerEngine to provide standard tool execution for agentic planners and workflows.
"""

import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from .crawler_engine import gov_crawler, GovCrawlerEngine
from .whitelist import is_whitelisted_domain
from .myscheme_catalog import MYSCHEME_FLAGSHIP_CATALOG
from .observability import observe

logger = logging.getLogger("gov_scheme.tools.crawler")

MYSCHEME_ROOT = "https://www.myscheme.gov.in"
MYSCHEME_SEARCH_PATH = "/api/apisetu/search/schemes"
MYSCHEME_DETAIL_PATH = "/api/apisetu/schemes"

MYSCHEME_PORTAL = {
    "id": "myscheme-portal",
    "name": "myScheme National Scheme Repository",
    "domain": "www.myscheme.gov.in",
    "url": MYSCHEME_ROOT,
    "level": "Central",
    "state": "Central and State/UT schemes",
    "category": "National scheme repository",
    "keywords": ["government schemes", "eligibility", "benefits", "application"],
}


class CrawlerTool:
    """
    Agentic Tool for Government Portal Navigation and Content Retrieval.
    Tool Name: 'gov_crawler_tool'
    Enforces exact *.gov.in / *.nic.in domain guardrails, Playwright SPA rendering,
    streaming PDF text extraction, and caching.
    """

    name: str = "gov_crawler_tool"
    description: str = (
        "Executes verified, whitelist-guarded HTTP and browser crawls against authentic "
        "Indian Government portals (*.gov.in / *.nic.in). Supports repository searches and scheme detail extraction."
    )

    def __init__(self, engine: Optional[GovCrawlerEngine] = None):
        self.engine = engine or gov_crawler

    def crawl_url(
        self,
        url: str,
        force_refresh: bool = False,
        deep_crawl: bool = True,
        max_subpages: int = 2,
    ) -> Dict[str, Any]:
        """
        Crawls a single authentic government URL with security allowlist check.
        """
        allowed, host, reason = is_whitelisted_domain(url)
        if not allowed:
            logger.warning("CrawlerTool security block for URL '%s': %s", url, reason)
            return {
                "success": False,
                "url": url,
                "domain": host,
                "error": reason,
                "security_status": "SECURITY_BLOCK",
                "extracted_text": "",
                "status_code": 403,
            }

        logger.info("CrawlerTool crawling URL: %s (force_refresh=%s)", url, force_refresh)
        return self.engine.crawl_url(
            target_url=url,
            force_refresh=force_refresh,
            deep_crawl=deep_crawl,
            max_subpages=max_subpages,
        )

    def build_search_url(
        self,
        term: str,
        scope: str = "Central",
        state: Optional[str] = None,
        page_size: int = 12,
    ) -> str:
        """Constructs an exact search endpoint URL for myScheme national catalog."""
        params = [
            ("q", term.strip()),
            ("lang", "en"),
            ("size", str(page_size)),
            ("from", "0"),
        ]
        if scope == "Central":
            params.append(("level", "Central"))
        elif state:
            params.append(("state", state.strip()))
        return f"{MYSCHEME_ROOT}{MYSCHEME_SEARCH_PATH}?{urlencode(params)}"

    def build_detail_url(self, slug: str) -> Optional[str]:
        """Constructs an exact scheme-detail endpoint URL on myScheme."""
        cleaned_slug = str(slug).strip()
        if not re.fullmatch(r"[A-Za-z0-9-]{1,120}", cleaned_slug):
            return None
        return f"{MYSCHEME_ROOT}{MYSCHEME_DETAIL_PATH}?{urlencode({'slug': cleaned_slug, 'lang': 'en'})}"

    def fetch_scheme_record(self, slug: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Fetches full scheme details for a given slug from myScheme."""
        detail_url = self.build_detail_url(slug)
        if not detail_url:
            return {
                "success": False,
                "error": f"Invalid scheme slug: '{slug}'",
                "extracted_text": "",
            }
        return self.crawl_url(detail_url, force_refresh=force_refresh, deep_crawl=False)

    def get_metrics(self) -> Dict[str, Any]:
        """Returns live crawler performance metrics and cache statistics."""
        return self.engine.get_crawler_metrics()

    @observe(name="CrawlerTool.discover_and_fetch")
    def discover_and_fetch(
        self,
        search_spec: Dict[str, Any],
        user_state: Optional[str] = None,
        force_live_crawl: bool = False,
    ) -> Dict[str, Any]:
        """
        Intelligent Candidate Discovery & Decision Gate Engine.
        Uses router search intelligence to autonomously query repositories,
        filter out domain conflicts, score genuine relevance, and selectively fetch scheme details.
        """
        core_intent = search_spec.get("core_intent", "")
        target_sector = (search_spec.get("target_sector") or "").lower()
        target_role = (search_spec.get("target_role") or "").lower()
        search_queries = search_spec.get("search_queries", []) or search_spec.get("myscheme_search_terms", [])
        must_include = [k.lower().strip() for k in search_spec.get("must_include_keywords", []) if k.strip()]
        must_exclude = [k.lower().strip() for k in search_spec.get("must_exclude_keywords", []) if k.strip()]
        target_schemes = [s.lower().strip() for s in search_spec.get("target_schemes", []) if s.strip()]

        logger.info(
            "CrawlerTool Decision Gate starting for intent='%s', sector='%s', role='%s', include=%s, exclude=%s",
            core_intent, target_sector, target_role, must_include, must_exclude
        )

        # Non-discriminating generic welfare stopwords to ignore during relevance scoring
        GENERIC_STOPWORDS = {
            "assistance", "financial", "support", "scheme", "schemes", "government",
            "welfare", "apply", "benefit", "benefits", "national", "central", "state",
            "yojana", "portal", "program", "programme", "india", "service", "help"
        }

        candidate_pool: List[Dict[str, Any]] = []
        seen_names = set()

        # Step 1: Explicit target scheme lookup (if citizen named a specific scheme)
        if target_schemes:
            for s in MYSCHEME_FLAGSHIP_CATALOG:
                s_name = s["name"].lower()
                if any(ts in s_name for ts in target_schemes):
                    if s["name"] not in seen_names:
                        candidate_pool.append(s)
                        seen_names.add(s["name"])

        # Step 2: Pool candidate schemes from indexed national catalog
        for s in MYSCHEME_FLAGSHIP_CATALOG:
            if s["name"] not in seen_names:
                candidate_pool.append(s)
                seen_names.add(s["name"])

        # Step 3: Run Decision Gate on all candidates
        approved_candidates: List[Dict[str, Any]] = []
        discarded_summary: List[str] = []

        for scheme in candidate_pool:
            s_name = scheme.get("name", "").lower()
            s_brief = scheme.get("brief", "").lower()
            s_cat = scheme.get("category", "").lower()
            s_level = scheme.get("level", "Central")
            s_state = scheme.get("state", "All India")
            combined_text = f"{s_name} {s_brief} {s_cat}"

            # Gate A: Hard Exclusion Check (Disqualify conflicting domains)
            hit_exclusion = None
            for exc in must_exclude:
                if exc not in GENERIC_STOPWORDS and exc in combined_text:
                    hit_exclusion = exc
                    break

            if hit_exclusion:
                discarded_summary.append(f"Rejected '{scheme['name']}' due to exclusion keyword '{hit_exclusion}'")
                continue

            # Gate B: Hard Role Conflict Check
            rules = scheme.get("eligibility_rules", [])
            has_role_conflict = False
            for rule in rules:
                field = rule.get("field", "")
                val = str(rule.get("value", "")).lower()

                # If candidate requires Student, but user is Farmer/Artisan/etc.
                if field == "occupation" and "student" in val and target_role and "student" not in target_role:
                    has_role_conflict = True
                    break
                # If candidate requires Farmer, but user is Student
                if field == "occupation" and "farmer" in val and target_role and "farmer" not in target_role:
                    has_role_conflict = True
                    break
                # If candidate is explicitly female-only (e.g. girl child/maternity), but target role is farmer
                if field == "gender" and val in ("female", "woman", "girl") and target_role in ("farmer", "artisan"):
                    has_role_conflict = True
                    break

            if has_role_conflict:
                discarded_summary.append(f"Rejected '{scheme['name']}' due to role conflict with '{target_role}'")
                continue

            # Gate C: State Constraint Check
            if s_level == "State" and s_state != "All India" and user_state:
                if user_state.lower() not in s_state.lower():
                    discarded_summary.append(f"Rejected '{scheme['name']}' (state '{s_state}' != user '{user_state}')")
                    continue

            # Gate D: Domain & Keyword Relevance Scoring (0 - 100)
            score = 0

            # 1. Title keyword overlap with must_include keywords
            for inc in must_include:
                if inc in GENERIC_STOPWORDS or len(inc) < 3:
                    continue
                if inc in s_name:
                    score += 35
                elif inc in s_brief:
                    score += 15

            # 2. Query phrase exact match
            for q in search_queries:
                q_clean = q.lower().strip()
                if q_clean and len(q_clean) > 4 and q_clean not in GENERIC_STOPWORDS:
                    if q_clean in s_name or q_clean in s_brief:
                        score += 30

            # 3. Sector / Category alignment
            if target_sector:
                if target_sector in s_cat or any(w in s_cat for w in target_sector.split() if w not in GENERIC_STOPWORDS and len(w) > 4):
                    score += 25

            # 4. Target scheme explicit match bonus
            if any(ts in s_name for ts in target_schemes):
                score += 50

            # Decision Threshold: Require at least 30 relevance score to pass
            if score >= 30:
                approved_candidates.append({
                    "scheme": scheme,
                    "relevance_score": score,
                })
            else:
                discarded_summary.append(f"Filtered '{scheme['name']}' (insufficient relevance score: {score}/100)")

        # Sort by relevance score descending
        approved_candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
        top_schemes = [item["scheme"] for item in approved_candidates[:4]]

        logger.info(
            "CrawlerTool Decision Gate completed. Approved: %d schemes (%s). Discarded: %d candidates.",
            len(top_schemes),
            [s["name"] for s in top_schemes],
            len(discarded_summary)
        )

        return {
            "candidate_schemes": top_schemes,
            "total_evaluated": len(candidate_pool),
            "approved_count": len(top_schemes),
            "discarded_count": len(discarded_summary),
            "decision_logs": discarded_summary[:10],
            "search_queries_used": search_queries,
            "target_sector": target_sector,
        }

    def execute(self, action: str = "crawl", **kwargs) -> Any:
        """
        Unified tool dispatch method.
        Actions:
          - 'crawl': crawl a single portal or guideline URL
          - 'fetch_detail': fetch scheme details by slug
          - 'metrics': get live crawler metrics
        """
        if action == "fetch_detail":
            return self.fetch_scheme_record(
                slug=kwargs.get("slug", ""),
                force_refresh=kwargs.get("force_refresh", False),
            )
        elif action == "metrics":
            return self.get_metrics()
        else:
            return self.crawl_url(
                url=kwargs.get("url", ""),
                force_refresh=kwargs.get("force_refresh", False),
                deep_crawl=kwargs.get("deep_crawl", True),
                max_subpages=kwargs.get("max_subpages", 2),
            )

    def run(self, **kwargs) -> Any:
        """Convenience alias for execute."""
        return self.execute(**kwargs)


# Global singleton crawler tool
crawler_tool = CrawlerTool()
