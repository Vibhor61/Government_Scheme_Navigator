"""Extract candidate descriptive fields from crawled registered portal text.

Extracted claims are not source-cited scheme rules and must not be used to
evaluate eligibility.
"""

import re
from typing import Dict, Any, Optional
from .llm_service import llm_service


class SchemeExtractor:
    @staticmethod
    def extract_structured_scheme(raw_text: str, source_url: str, portal_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Parses text extracted from a crawled government portal into a normalized scheme schema.
        Extracts candidate text fields from a crawled page. The returned fields are
        not a verified scheme record and must not be used as eligibility rules.
        Missing facts remain explicitly unknown.
        """
        meta = portal_metadata or {}
        domain = meta.get("domain", source_url)

        # ---------------------------------------------------------------------
        # 1. Primary: Dynamic LLM Extraction (Zero Hardcoded Catalog Rules)
        # ---------------------------------------------------------------------
        if raw_text and len(raw_text.strip()) > 30:
            llm_extracted = llm_service.extract_scheme_from_crawled_text(
                raw_text=raw_text,
                source_url=source_url,
                portal_metadata=meta
            )
            if llm_extracted and llm_extracted.get("title"):
                return {
                    "title": llm_extracted.get("title") or meta.get("name", "Official Government Scheme"),
                    "short_name": llm_extracted.get("acronym") or meta.get("acronym", "GOV-SCHEME"),
                    "category": llm_extracted.get("category") or meta.get("category", "Public Welfare"),
                    "ministry": llm_extracted.get("ministry") or meta.get("ministry", "Government of India"),
                    "source_url": source_url,
                    "domain": domain,
                    "financial_assistance": llm_extracted.get("financial_assistance") or "Not stated in the crawled content.",
                    "eligibility_criteria": llm_extracted.get("eligibility_criteria") or [],
                    "documents_required": llm_extracted.get("documents_required") or [],
                    "application_process": llm_extracted.get("application_process") or "Application instructions were not found in the crawled content.",
                    "official_portal": source_url,
                    "extraction_status": "candidate_only",
                    "eligibility_rules_verified": False,
                }

        # ---------------------------------------------------------------------
        # 2. Resilient Generic Fallback (Universal NLP, Zero Hardcoded Scheme Names)
        # ---------------------------------------------------------------------
        title = meta.get("name", "")
        if not title:
            first_line = raw_text.split(".")[0].strip()
            title = first_line[:80] if len(first_line) > 10 else f"Official Portal Notice - {domain}"

        ministry = meta.get("ministry", "Government of India")
        category = meta.get("category", "Public Welfare")

        # Generic Currency / Benefit extraction
        money_matches = re.findall(
            r'(?:₹|Rs\.?|INR)\s*[\d,]+(?:\s*(?:per\s*(?:year|annum|month)|annually|lakh|crore|%))?',
            raw_text,
            re.IGNORECASE
        )
        if money_matches:
            financial_assistance = (
                f"Amounts found in page text ({', '.join(money_matches[:3])}); "
                "their association with this scheme could not be verified."
            )
        else:
            financial_assistance = "Financial assistance was not reliably identified in the crawled content."

        # Text fragments are not reliable proof that a sentence is a scheme rule.
        eligibility_criteria = []
        sentences = [s.strip() for s in re.split(r'[.\n]', raw_text) if len(s.strip()) > 15]
        documents_required = []
        # Generic Application Steps extraction
        app_steps = "Application instructions were not reliably identified in the crawled content."
        for s in sentences:
            if any(k in s.lower() for k in ["how to apply", "registration", "portal", "submit application", "online application"]):
                if len(s) < 220:
                    app_steps = s
                    break

        return {
            "title": title,
            "short_name": meta.get("acronym", "SCHEME"),
            "category": category,
            "ministry": ministry,
            "source_url": source_url,
            "domain": domain,
            "financial_assistance": financial_assistance,
            "eligibility_criteria": eligibility_criteria,
            "documents_required": documents_required,
            "application_process": app_steps,
            "official_portal": source_url,
            "extraction_status": "candidate_only",
            "eligibility_rules_verified": False,
        }
