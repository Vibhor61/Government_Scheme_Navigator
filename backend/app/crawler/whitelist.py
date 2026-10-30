"""Exact-host allowlist for the national Central/State scheme repository."""

from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

STATE_UT_REGISTRY = {
    "ap": "Andhra Pradesh",
    "andhra pradesh": "Andhra Pradesh",
    "ar": "Arunachal Pradesh",
    "arunachal": "Arunachal Pradesh",
    "arunachal pradesh": "Arunachal Pradesh",
    "as": "Assam",
    "assam": "Assam",
    "br": "Bihar",
    "bihar": "Bihar",
    "cg": "Chhattisgarh",
    "chhattisgarh": "Chhattisgarh",
    "ga": "Goa",
    "goa": "Goa",
    "gj": "Gujarat",
    "gujarat": "Gujarat",
    "hr": "Haryana",
    "haryana": "Haryana",
    "hp": "Himachal Pradesh",
    "himachal": "Himachal Pradesh",
    "himachal pradesh": "Himachal Pradesh",
    "jh": "Jharkhand",
    "jharkhand": "Jharkhand",
    "ka": "Karnataka",
    "karnataka": "Karnataka",
    "kl": "Kerala",
    "kerala": "Kerala",
    "mp": "Madhya Pradesh",
    "madhya pradesh": "Madhya Pradesh",
    "mh": "Maharashtra",
    "maharashtra": "Maharashtra",
    "mn": "Manipur",
    "manipur": "Manipur",
    "ml": "Meghalaya",
    "meghalaya": "Meghalaya",
    "mz": "Mizoram",
    "mizoram": "Mizoram",
    "nl": "Nagaland",
    "nagaland": "Nagaland",
    "od": "Odisha",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "pb": "Punjab",
    "punjab": "Punjab",
    "rj": "Rajasthan",
    "rajasthan": "Rajasthan",
    "sk": "Sikkim",
    "sikkim": "Sikkim",
    "tn": "Tamil Nadu",
    "tamil nadu": "Tamil Nadu",
    "tg": "Telangana",
    "ts": "Telangana",
    "telangana": "Telangana",
    "tr": "Tripura",
    "tripura": "Tripura",
    "up": "Uttar Pradesh",
    "uttar pradesh": "Uttar Pradesh",
    "uk": "Uttarakhand",
    "uttarakhand": "Uttarakhand",
    "wb": "West Bengal",
    "west bengal": "West Bengal",
    "dl": "Delhi (NCT)",
    "delhi": "Delhi (NCT)",
    "national capital territory of delhi": "Delhi (NCT)",
    "jk": "Jammu & Kashmir",
    "jammu and kashmir": "Jammu & Kashmir",
    "jammu kashmir": "Jammu & Kashmir",
    "ladakh": "Ladakh",
    "la": "Ladakh",
    "ch": "Chandigarh",
    "chandigarh": "Chandigarh",
    "py": "Puducherry",
    "puducherry": "Puducherry",
    "pondicherry": "Puducherry",
    "an": "Andaman & Nicobar Islands",
    "andaman": "Andaman & Nicobar Islands",
    "andaman and nicobar islands": "Andaman & Nicobar Islands",
    "andaman nicobar islands": "Andaman & Nicobar Islands",
    "andaman nicobar": "Andaman & Nicobar Islands",
    "dd": "Dadra & Nagar Haveli and Daman & Diu",
    "dnh": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra and nagar haveli and daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra nagar haveli and daman diu": "Dadra & Nagar Haveli and Daman & Diu",
    "ld": "Lakshadweep",
    "lakshadweep": "Lakshadweep",
}

import re

CRAWL_SOURCE_CATALOG: List[Dict[str, Any]] = [
    {
        "domain": "myscheme.gov.in",
        "name": "myScheme National Scheme Repository",
        "level": "Central",
        "state": "Central and State/UT schemes",
        "category": "National scheme repository",
        "trust_score": "Registered official portal",
        "jurisdictions": ["Central", "State", "UT"],
    },
    {
        "domain": "pmkisan.gov.in",
        "name": "PM-KISAN Portal",
        "level": "Central",
        "state": "All India",
        "category": "Agriculture & Farmer Welfare",
        "trust_score": "Verified apex government portal",
        "jurisdictions": ["Central"],
    },
    {
        "domain": "scholarships.gov.in",
        "name": "National Scholarship Portal (NSP)",
        "level": "Central",
        "state": "All India",
        "category": "Education & Fellowships",
        "trust_score": "Verified apex government portal",
        "jurisdictions": ["Central", "State"],
    },
    {
        "domain": "dbtbharat.gov.in",
        "name": "Direct Benefit Transfer (DBT) Bharat",
        "level": "Central",
        "state": "All India",
        "category": "Social Welfare & Subsidies",
        "trust_score": "Verified apex government portal",
        "jurisdictions": ["Central", "State"],
    },
    {
        "domain": "agricoop.gov.in",
        "name": "Ministry of Agriculture & Farmers Welfare",
        "level": "Central",
        "state": "All India",
        "category": "Agriculture & Irrigation",
        "trust_score": "Verified ministry portal",
        "jurisdictions": ["Central"],
    },
    {
        "domain": "wcd.nic.in",
        "name": "Ministry of Women and Child Development",
        "level": "Central",
        "state": "All India",
        "category": "Women & Child Empowerment",
        "trust_score": "Verified ministry portal",
        "jurisdictions": ["Central"],
    },
    {
        "domain": "socialjustice.gov.in",
        "name": "Ministry of Social Justice and Empowerment",
        "level": "Central",
        "state": "All India",
        "category": "Social Justice & Inclusion",
        "trust_score": "Verified ministry portal",
        "jurisdictions": ["Central"],
    },
    {
        "domain": "msme.gov.in",
        "name": "Ministry of Micro, Small and Medium Enterprises",
        "level": "Central",
        "state": "All India",
        "category": "Business, Startup & MSME Loans",
        "trust_score": "Verified ministry portal",
        "jurisdictions": ["Central"],
    },
    {
        "domain": "edistrict.up.gov.in",
        "name": "Uttar Pradesh e-District & Citizen Services",
        "level": "State",
        "state": "Uttar Pradesh",
        "category": "State Welfare Services",
        "trust_score": "Verified state apex portal",
        "jurisdictions": ["State"],
    },
    {
        "domain": "aaplesarkar.mahaonline.gov.in",
        "name": "Maharashtra Aaple Sarkar Citizen Services",
        "level": "State",
        "state": "Maharashtra",
        "category": "State Welfare Services",
        "trust_score": "Verified state apex portal",
        "jurisdictions": ["State"],
    },
    {
        "domain": "sevasindhu.karnataka.gov.in",
        "name": "Karnataka Seva Sindhu Citizen Portal",
        "level": "State",
        "state": "Karnataka",
        "category": "State Welfare Services",
        "trust_score": "Verified state apex portal",
        "jurisdictions": ["State"],
    },
    {
        "domain": "jansoochna.rajasthan.gov.in",
        "name": "Rajasthan Jan Soochna Portal",
        "level": "State",
        "state": "Rajasthan",
        "category": "Public Information & Schemes",
        "trust_score": "Verified state apex portal",
        "jurisdictions": ["State"],
    },
]


def _registered_official_hosts() -> set:
    hosts = {portal["domain"].casefold() for portal in CRAWL_SOURCE_CATALOG}
    return hosts | {f"www.{host}" for host in hosts}


def is_valid_gov_host(host: str) -> bool:
    """
    Validates whether the host is an authentic Indian government domain (*.gov.in or *.nic.in).
    Strictly prevents spoofing like 'myscheme.gov.in.evil.com' or 'fake-gov.in'.
    """
    if not host:
        return False
    host = host.casefold().strip().rstrip(".")
    if not re.match(r"^[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?)+$", host):
        return False
    parts = host.split(".")
    return len(parts) >= 2 and parts[-2] in {"gov", "nic"} and parts[-1] == "in"


def is_whitelisted_domain(url: str, strict_repo_mode: bool = False) -> Tuple[bool, str, str]:
    """Allow authentic Indian government apex and departmental domains (*.gov.in and *.nic.in)."""
    if not url:
        return False, "", "Empty URL provided"

    try:
        parsed = urlparse(url)
        if parsed.scheme.casefold() not in {"http", "https"} or not parsed.hostname:
            return False, parsed.netloc.casefold(), "Only absolute HTTP(S) portal URLs are allowed"
        if parsed.username or parsed.password:
            return False, parsed.hostname.casefold(), "Credentials in portal URLs are not allowed"
        if parsed.port not in {None, 80, 443}:
            return False, parsed.hostname.casefold(), "Non-standard portal ports are not allowed"

        host = parsed.hostname.casefold().rstrip(".")

        if strict_repo_mode:
            if host not in _registered_official_hosts():
                return False, host, f"Access blocked: '{host}' is not a registered scheme repository host"
            return True, host, "Exact host is in the registered scheme repository registry"

        if is_valid_gov_host(host) or host in _registered_official_hosts():
            return True, host, "Verified authentic Indian Government domain (*.gov.in / *.nic.in)"

        return False, host, f"Access blocked: '{host}' is not an authorized .gov.in or .nic.in domain"
    except ValueError:
        return False, "", "Malformed portal URL"


def get_whitelist_catalog(
    jurisdiction_filter: Optional[str] = None,
    state_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return active crawl repositories with optional metadata filtering."""
    results = CRAWL_SOURCE_CATALOG

    if jurisdiction_filter:
        jurisdiction = jurisdiction_filter.casefold()
        results = [
            item for item in results
            if item.get("level", "").casefold() == jurisdiction
            or jurisdiction in {
                value.casefold() for value in item.get("jurisdictions", [])
            }
        ]
    if state_filter and state_filter.casefold() != "all":
        state = state_filter.casefold()
        results = [
            item for item in results
            if item.get("state", "").casefold() in {
                "all india", "central and state/ut schemes"
            }
            or state in item.get("state", "").casefold()
        ]
    if category_filter and category_filter.casefold() != "all":
        category = category_filter.casefold()
        results = [
            item for item in results
            if category in item.get("category", "").casefold()
        ]
    return results


def get_whitelist_summary_stats() -> Dict[str, Any]:
    """Return active crawler allowlist counts, excluding non-crawlable metadata."""
    central_count = sum(1 for p in CRAWL_SOURCE_CATALOG if p.get("level") == "Central")
    state_count = sum(1 for p in CRAWL_SOURCE_CATALOG if p.get("level") == "State")
    ut_count = sum(1 for p in CRAWL_SOURCE_CATALOG if p.get("level") == "UT")
    return {
        "total_portals": len(CRAWL_SOURCE_CATALOG),
        "registered_exact_hosts": len(_registered_official_hosts()),
        "central_portals": central_count,
        "state_portals": state_count,
        "ut_portals": ut_count,
        "repository_jurisdictions": ["Central", "State", "UT"],
        "registered_states_and_uts": len(set(STATE_UT_REGISTRY.values())),
        "state_scheme_coverage": "Comprehensive coverage of Central ministries and State/UT schemes",
        "apex_domains_allowed": ["*.gov.in", "*.nic.in"],
        "security_policy": "Strict apex and departmental Indian Government domains (*.gov.in / *.nic.in)",
    }


def detect_state_from_domain(domain: str) -> Optional[str]:
    """Dynamically parse State/UT names from domain components."""
    for part in domain.casefold().split("."):
        if part in STATE_UT_REGISTRY:
            return STATE_UT_REGISTRY[part]
    return None


def sanitize_gov_url(url: str) -> str:
    """Ensure an absolute HTTP(S) scheme before the exact-host check."""
    candidate = url.strip()
    parsed = urlparse(candidate)
    if parsed.scheme.casefold() in {"http", "https"}:
        return candidate
    return "https://" + candidate.lstrip("/")


def extract_domain_metadata(domain: str) -> Dict[str, Any]:
    """Return minimal metadata for an exact registered host."""
    normalized = domain.casefold().removeprefix("www.")
    repository = next(
        (item for item in CRAWL_SOURCE_CATALOG if item["domain"] == normalized),
        None,
    )
    if repository:
        return dict(repository)
    state = detect_state_from_domain(normalized)
    return {
        "domain": normalized,
        "name": normalized.upper(),
        "level": "State Government" if state else "Registered Portal",
        "state": state or "All India / Centre",
        "category": "National scheme repository" if normalized == "myscheme.gov.in" else "Unregistered",
        "trust_score": "Registered official portal" if state else "Not registered",
    }
