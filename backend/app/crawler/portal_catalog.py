"""National scheme-repository metadata and State/UT profile choices."""

import re
from typing import Any, Dict, List, Optional, Tuple

from .whitelist import STATE_UT_REGISTRY

SEED_GOVERNMENT_PORTALS: List[Dict[str, Any]] = [
    {
        "id": "myscheme-portal",
        "name": "myScheme National Scheme Repository",
        "domain": "myscheme.gov.in",
        "url": "https://www.myscheme.gov.in",
        "level": "Central",
        "state": "Central and State/UT schemes",
        "category": "National scheme repository",
        "ministry": "Ministry of Electronics and Information Technology / NeGD",
        "keywords": ["government schemes", "eligibility", "benefits", "application"],
        "description": "National platform indexing schemes from Central and State/UT governments.",
    },
    {
        "id": "pmkisan-portal",
        "name": "PM-KISAN Samman Nidhi",
        "domain": "pmkisan.gov.in",
        "url": "https://pmkisan.gov.in",
        "level": "Central",
        "state": "All India",
        "category": "Agriculture & Farmer Welfare",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "keywords": ["farmer", "kisan", "landholding", "agriculture", "income support", "crop", "irrigation"],
        "description": "Direct income support and welfare initiative for Indian farmer families.",
    },
    {
        "id": "nsp-portal",
        "name": "National Scholarship Portal (NSP)",
        "domain": "scholarships.gov.in",
        "url": "https://scholarships.gov.in",
        "level": "Central",
        "state": "All India",
        "category": "Education & Fellowships",
        "ministry": "Ministry of Education & MeitY",
        "keywords": ["scholarship", "education", "student", "college", "school", "tuition", "merit", "fellowship"],
        "description": "Apex national platform for Central, UGC, and State government scholarships.",
    },
    {
        "id": "dbt-portal",
        "name": "Direct Benefit Transfer (DBT) Bharat",
        "domain": "dbtbharat.gov.in",
        "url": "https://dbtbharat.gov.in",
        "level": "Central",
        "state": "All India",
        "category": "Social Welfare & Direct Subsidies",
        "ministry": "Cabinet Secretariat",
        "keywords": ["dbt", "subsidy", "welfare", "bpl", "pension", "cash transfer"],
        "description": "Apex monitoring and delivery platform for government DBT schemes.",
    },
    {
        "id": "wcd-portal",
        "name": "Ministry of Women & Child Development",
        "domain": "wcd.nic.in",
        "url": "https://wcd.nic.in",
        "level": "Central",
        "state": "All India",
        "category": "Women & Child Empowerment",
        "ministry": "Ministry of Women and Child Development",
        "keywords": ["women", "woman", "child", "girl", "mother", "maternity", "poshan", "sukanya"],
        "description": "Central ministry overseeing schemes for women empowerment and child welfare.",
    },
    {
        "id": "msme-portal",
        "name": "Ministry of MSME",
        "domain": "msme.gov.in",
        "url": "https://msme.gov.in",
        "level": "Central",
        "state": "All India",
        "category": "Business, Startup & MSME Loans",
        "ministry": "Ministry of Micro, Small and Medium Enterprises",
        "keywords": ["msme", "business", "loan", "startup", "mudra", "subsidy", "entrepreneur", "artisan"],
        "description": "Credit, subsidy, and cluster development schemes for small enterprises.",
    },
    {
        "id": "up-edistrict",
        "name": "Uttar Pradesh e-District",
        "domain": "edistrict.up.gov.in",
        "url": "https://edistrict.up.gov.in",
        "level": "State",
        "state": "Uttar Pradesh",
        "category": "State Welfare Services",
        "ministry": "Government of Uttar Pradesh",
        "keywords": ["uttar pradesh", "up", "kanya sumangala", "sspy", "pension", "domicile"],
        "description": "Apex citizen service delivery portal for Uttar Pradesh state schemes.",
    },
    {
        "id": "maha-aaplesarkar",
        "name": "Maharashtra Aaple Sarkar",
        "domain": "aaplesarkar.mahaonline.gov.in",
        "url": "https://aaplesarkar.mahaonline.gov.in",
        "level": "State",
        "state": "Maharashtra",
        "category": "State Welfare Services",
        "ministry": "Government of Maharashtra",
        "keywords": ["maharashtra", "ladki bahin", "maha", "sanjay gandhi", "ration"],
        "description": "Citizen welfare service portal for Government of Maharashtra.",
    },
]


def get_state_region_options() -> List[str]:
    """Return supported State/UT names for repository filtering."""
    return ["All India / Centre", *sorted(set(STATE_UT_REGISTRY.values())), "Not sure"]


def _normalize_location_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def extract_state_from_query(query: str) -> Optional[str]:
    """Extract an explicitly named State/UT or its registered short alias."""
    normalized_query = f" {_normalize_location_text(query)} "
    states = set(STATE_UT_REGISTRY.values())
    for state in sorted(states, key=len, reverse=True):
        normalized_state = _normalize_location_text(state)
        if normalized_state and f" {normalized_state} " in normalized_query:
            return state

    for alias in sorted(STATE_UT_REGISTRY, key=len, reverse=True):
        if len(alias) < 4:
            continue
        normalized_alias = _normalize_location_text(alias)
        if normalized_alias and f" {normalized_alias} " in normalized_query:
            return STATE_UT_REGISTRY[alias]

    for code, state in STATE_UT_REGISTRY.items():
        if len(code) == 2 and code.isalpha() and re.search(
            rf"(?<![A-Za-z]){re.escape(code.upper())}(?![A-Za-z])", query
        ):
            return state
    return None


def find_relevant_portals_for_query(
    query: str,
    max_results: int = 4,
) -> List[Dict[str, Any]]:
    """Score and return relevant authentic government portals matching the query and jurisdiction."""
    query_lower = query.casefold()
    detected_state = extract_state_from_query(query)

    scored: List[Tuple[int, Dict[str, Any]]] = []
    for portal in SEED_GOVERNMENT_PORTALS:
        score = 0
        if portal["domain"] == "myscheme.gov.in":
            score += 1  # Always a baseline candidate

        # State matching
        portal_state = portal.get("state", "").casefold()
        if detected_state and detected_state.casefold() in portal_state:
            score += 5

        # Keyword matching
        for kw in portal.get("keywords", []):
            if kw.casefold() in query_lower:
                score += 3

        # Category matching
        category = portal.get("category", "").casefold()
        for token in query_lower.split():
            if len(token) > 3 and token in category:
                score += 2

        if score > 0 or portal["domain"] == "myscheme.gov.in":
            scored.append((score, portal))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [p for _, p in scored[:max_results]]
    if not results:
        results = [dict(SEED_GOVERNMENT_PORTALS[0])]
    return results
