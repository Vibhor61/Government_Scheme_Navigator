import os
import json
import time
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .config import settings
from .schemas import (
    AgentQueryRequest, AgentQueryResponse, CrawlUrlRequest
)
from .crawler import (
    crawler_agent, crawler_cache, gov_crawler, is_whitelisted_domain,
    get_whitelist_catalog, get_whitelist_summary_stats, SEED_GOVERNMENT_PORTALS
)

app = FastAPI(
    title="Government Scheme Navigator",
    version=settings.VERSION,
    description=(
        "An evidence-first government scheme discovery workflow using the national myScheme "
        "repository, source-quote validation, and deterministic criteria checks."
    )
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Government Scheme Navigator",
        "architecture": "Constrained myScheme repository search, scheme-detail crawling, quote validation, and deterministic rule evaluation",
        "security_policy": "Exact registered hosts only; wildcard government-domain access is disabled",
        "crawler_strategies": [
            "TLS-verified HTTP extraction for HTML, JSON, XML, plain text, and PDF",
            "Playwright/Chromium fallback for registered HTTPS pages with empty HTML",
        ],
        "eligibility_status": "Scheme criteria are evaluated only when supported by quotations checked against fetched myScheme records",
        "repository": "myScheme national repository indexing Central and State/UT schemes",
        "storage": "Registered repository plus on-demand crawling and persistent website cache"
    }

@app.get("/api/stats")
def get_stats():
    """Returns crawler agent status, live crawler metrics, and verified whitelist stats."""
    crawler_metrics = gov_crawler.get_crawler_metrics()
    whitelist_stats = get_whitelist_summary_stats()

    return {
        "service": "Government Scheme Navigator",
        "crawler_status": "Active Daemon",
        "active_crawlers": crawler_metrics.get("active_crawlers", 1),
        "total_crawls_dispatched": crawler_metrics.get("total_crawls", 0),
        "cache_hit_ratio": crawler_metrics.get("cache_stats", {}).get("hit_ratio_percent", 0),
        "whitelist_coverage": "One national scheme repository indexing Central and State/UT schemes",
        "total_verified_portals": whitelist_stats.get("total_portals", 0),
        "architecture": "Shared myScheme search, cited-rule extraction, and deterministic profile evaluation"
    }


# =========================================================================
# PORTAL NAVIGATION AND CRAWLER API ENDPOINTS
# =========================================================================

@app.post("/api/agent/query", response_model=AgentQueryResponse)
def agent_query_endpoint(req: AgentQueryRequest):
    """
    Search the national scheme repository and evaluate only source-verified rules.
    """
    return crawler_agent.run(
        user_query=req.query,
        force_live_crawl=req.force_live_crawl,
        user_clarification=req.user_clarification,
        user_profile=req.user_profile,
        conversation_history=req.conversation_history
    )

@app.post("/api/eligibility/check")
def check_eligibility_endpoint(profile: Dict[str, Any]):
    """
    Direct eligibility evaluation against myScheme national and state repository.
    """
    from .crawler.myscheme_catalog import match_schemes_for_profile
    matched = match_schemes_for_profile(profile)
    return {
        "status": "success",
        "total_matched": len(matched),
        "profile": profile,
        "schemes": matched
    }

@app.get("/api/schemes/catalog")
def get_schemes_catalog_endpoint():
    """
    Returns authentic flagship catalog indexed from myScheme.
    """
    from .crawler.myscheme_catalog import MYSCHEME_FLAGSHIP_CATALOG
    return {
        "status": "success",
        "total_schemes": len(MYSCHEME_FLAGSHIP_CATALOG),
        "schemes": MYSCHEME_FLAGSHIP_CATALOG
    }

@app.post("/api/crawler/crawl")
def crawl_url_endpoint(req: CrawlUrlRequest):
    """
    On-demand crawl endpoint restricted to verified Indian Government domains.
    Supports 2-hop deep crawling and PDF circular extraction.
    """
    return gov_crawler.crawl_url(
        req.url,
        force_refresh=req.force_refresh,
        deep_crawl=req.deep_crawl,
        max_subpages=req.max_subpages,
    )

@app.get("/api/crawler/dashboard")
def crawler_dashboard_endpoint():
    """Returns live crawler metrics, cache analytics, recent crawl events, seed portals, and whitelist stats."""
    return {
        "metrics": gov_crawler.get_crawler_metrics(),
        "recent_logs": list(reversed(gov_crawler.recent_logs[-40:])),
        "seed_portals": SEED_GOVERNMENT_PORTALS,
        "whitelist": get_whitelist_catalog(),
        "whitelist_stats": get_whitelist_summary_stats()
    }

@app.get("/api/crawler/cache")
def get_crawler_cache_endpoint():
    """Returns cache statistics and recent cached pages."""
    return {
        "stats": crawler_cache.get_stats(),
        "entries": crawler_cache.list_entries(limit=30)
    }

@app.post("/api/crawler/cache/clear")
def clear_crawler_cache_endpoint():
    """Clears multi-tier crawler cache."""
    crawler_cache.clear()
    return {"status": "success", "message": "Crawler cache cleared successfully."}

@app.get("/api/crawler/whitelist")
def get_crawler_whitelist_endpoint(
    jurisdiction: Optional[str] = Query(None, description="Central, State, or UT"),
    state: Optional[str] = Query(None, description="State or UT name"),
    category: Optional[str] = Query(None, description="Scheme category")
):
    """Returns active crawl repositories with optional metadata filters."""
    catalog = get_whitelist_catalog(jurisdiction_filter=jurisdiction, state_filter=state, category_filter=category)
    return {
        "catalog": catalog,
        "stats": get_whitelist_summary_stats(),
        "total_returned": len(catalog)
    }


# Serve static UI directly at root
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/", response_class=HTMLResponse)
    def read_root():
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse("<h1>GovScheme AI Backend Running</h1>")

    app.mount("/static", StaticFiles(directory=static_dir), name="static")
