"""
Policy Interaction Engine: Dynamic Cross-Scheme Conflict & Stacking Intelligence.

Evaluates interactions across multiple official welfare schemes across ANY sector:
- Health & Medical (Ayushman Bharat, Jan Aushadhi, PM National Dialysis, Arogya Nidhi)
- Higher Education & Scholarships (NSP, Pragati, Vidya Lakshmi, CSIS)
- Women & Child Development (PMMVY, Sukanya Samriddhi, Ladli Behna, Janani Suraksha)
- MSME & Micro-Enterprise (PM SVANidhi, PMEGP, Mudra, Stand-Up India)
- Disability & Senior Citizens (Vay Vandana, ADIP, Vayoshri, UDID, Indira Gandhi Pension)
- Agriculture & Rural (PM-KISAN, KCC, PM Fasal Bima, PM-KUSUM)
- Housing & Habitat (PMAY-G, PMAY-U, State Awas, SBM, Ujjwala)

Methodology:
1. LLM-First Dynamic Policy Interaction Analysis (Groq JSON mode via llm_service)
2. Comprehensive Multi-Domain Deterministic Fallback (No single-sector hardcoding)
3. Integration with SourceConflictDetector for official circular discrepancies
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional
from .conflict_detector import SourceConflictDetector
from .llm_service import llm_service

logger = logging.getLogger("gov_scheme.policy_interaction")


POLICY_INTERACTION_SYSTEM_PROMPT = """You are the Senior Policy Analyst & Welfare Convergence Specialist for the Indian Government Scheme Navigator.
Your role is to analyze a set of discovered government welfare schemes for a citizen and evaluate:
1. CROSS-SCHEME CONFLICTS & EXCLUSIONS: Are there schemes in the list that conflict with each other or bar concurrent benefits?
   - Examples of real policy exclusions:
     * Housing: Cannot receive two pucca housing grants (e.g. Central PMAY vs State Housing).
     * Scholarship: Central/State guidelines strictly forbid claiming concurrent maintenance allowances in the same academic year.
     * Health: Statutory medical scheme beneficiaries (CGHS/ESIC) are excluded from AB-PMJAY unless qualifying under universal senior citizen (70+) rules.
     * Farmer income: PM-KISAN excludes income-tax payers, government servants, and institutional landholders.
     * Street vendor: 1st tranche cap vs escalation tranches.
2. WELFARE STACKING & CONVERGENCE: Can 2 or more schemes be stacked/combined synergistically to maximize total citizen benefits without policy violations?
   - Applicable to ANY domain:
     * Health: Combine hospitalization cover (AB-PMJAY) + discounted generic medicines (PM Jan Aushadhi) + state critical illness top-ups.
     * Education: Combine tuition fee waiver/scholarship (NSP) + interest-subsidized education loan (Vidya Lakshmi) + skill development (PMKVY).
     * Women & Child: Combine maternity benefit (PMMVY) + institutional delivery cash (JSY) + girl child savings (Sukanya Samriddhi).
     * MSME / Business: Combine capital margin money grant (PMEGP) + collateral-free working capital loan (Mudra / PM SVANidhi).
     * Senior Citizens / Disability: Combine healthcare (Vay Vandana 70+) + assistive living devices (Vayoshri / ADIP) + monthly pension.
     * Agriculture: Combine income support (PM-KISAN) + subsidized credit (KCC) + crop risk cover (PMFBY).

CRITICAL RULES:
- Ground all advice strictly in actual Indian welfare policy norms.
- Do NOT hallucinate fictitious scheme rules.
- If there is NO conflict among the schemes, set has_conflict = false and conflict = null.
- If schemes cannot be stacked (e.g. only 1 scheme exists), set welfare_stack = null.

Respond strictly in valid JSON matching this schema:
{
  "has_conflict": true | false,
  "conflict": {
    "title": "Clear conflict title citing the schemes",
    "discrepancy_field": "Short name of policy restriction (e.g. Concurrent Scholarship Bar, Dual Housing Grant Exclusivity)",
    "explanation": "Clear plain-language explanation of why both cannot be claimed simultaneously",
    "scheme_a": {"name": "Scheme A Name", "level": "Central | State"},
    "scheme_b": {"name": "Scheme B Name", "level": "Central | State"},
    "source_a": {"portal": "Scheme A Guidelines", "rule": "Exact exclusion rule or clause text"},
    "source_b": {"portal": "Scheme B Guidelines", "rule": "Duplicate application / de-duplication bar text"},
    "recommendation": {
      "preferred_scheme": "Recommended Scheme Name",
      "reason": "Why this scheme is better to prioritize (higher aid, direct DBT, etc.)",
      "action": "Immediate recommended step for the citizen"
    },
    "clarification_prompt": "Which scheme would you like to prioritize for detailed checking?",
    "options": ["Prioritize Scheme A", "Prioritize Scheme B", "Compare both options"]
  } | null,
  "welfare_stack": {
    "bundle_title": "Inspiring, domain-specific title with appropriate emoji (e.g. 🏥 Integrated Healthcare & Medication Protection Stack)",
    "bundle_type": "HEALTH_CONVERGENCE | STUDENT_CONVERGENCE | WOMEN_CHILD_CONVERGENCE | MSME_LIVELIHOOD_CONVERGENCE | SENIOR_DISABILITY_CONVERGENCE | AGRICULTURAL_CONVERGENCE | HABITAT_CONVERGENCE | MULTI_SECTOR_PORTFOLIO",
    "badge": "Policy Convergence Approved",
    "description": "Clear explanation of how these schemes work together synergistically",
    "total_financial_impact": "Summary of cumulative benefits (e.g. ₹5,00,000 Health Cover + 50-90% Discounted Generic Medicines)",
    "schemes": [
      {
        "name": "Scheme Name",
        "role": "Specific role (e.g. Hospitalization Shield, Tuition Support, Maternity Grant)",
        "benefit_summary": "1-sentence summary of benefit"
      }
    ],
    "application_sequence": [
      {
        "step": 1,
        "title": "Actionable step title",
        "instruction": "Clear instructions on which portal to visit and what to submit first"
      }
    ]
  } | null
}
"""


# -----------------------------------------------------------------------------
# Comprehensive Multi-Domain Taxonomy for Deterministic Fallback
# -----------------------------------------------------------------------------
SECTOR_TAXONOMY = {
    "health": {
        "keywords": {"health", "medical", "hospital", "hospitalization", "ayushman", "pmjay", "pm-jay", "medicine", "aushadhi", "dialysis", "treatment", "patient", "disease", "arogyasri", "swasthya"},
        "stack_title": "🏥 Integrated Universal Healthcare & Medication Stack",
        "stack_type": "HEALTH_CONVERGENCE",
        "default_impact": "₹5,00,000 Free In-Patient Cover + Subsidized Essential Medicines",
        "rationale": "Secondary/tertiary hospital treatment under Ayushman Bharat synergizes directly with Jan Aushadhi generic medicines and national screening programs.",
        "seq": [
            ("Verify PM-JAY / Golden Card Status", "Check your name on the Ayushman Bharat portal or visit nearest empanelled hospital Ayushman Mitra desk with your Aadhaar."),
            ("Access Subsidized Generic Medicines", "Locate your nearest Pradhan Mantri Jan Aushadhi Kendra for 50-90% lower prescription medicine costs."),
            ("State Chief Minister Relief Fund", "For specialized procedures beyond the ₹5L ceiling, submit an application to the State Health Society.")
        ]
    },
    "education": {
        "keywords": {"student", "students", "scholarship", "college", "school", "university", "btech", "degree", "tuition", "education", "fellowship", "stipend", "study", "pragati", "saksham", "vidya lakshmi"},
        "stack_title": "🎓 Student Higher Education & Academic Support Stack",
        "stack_type": "STUDENT_CONVERGENCE",
        "default_impact": "Full Course Tuition Fee Support + Subsidized Education Credit",
        "rationale": "Combine tuition fee waivers, central maintenance stipends, and interest-subsidized education loans concurrently without policy conflicts.",
        "seq": [
            ("Apply on National Scholarship Portal (NSP)", "Register on NSP using One-Time Registration (OTR) and submit your verified family income certificate."),
            ("Apply on PM Vidya Lakshmi Portal", "If supplementary financing is needed, apply for education loans with central interest subvention (CSIS)."),
            ("Institute Verification", "Ensure your college nodal officer verifies your student bonafide certificate before portal deadlines.")
        ]
    },
    "women_child": {
        "keywords": {"women", "woman", "girl", "maternity", "mother", "child", "children", "matru", "vandana", "sukanya", "samriddhi", "ladli", "janani", "poshan", "widow"},
        "stack_title": "👩‍👧 Comprehensive Women & Maternal Empowerment Stack",
        "stack_type": "WOMEN_CHILD_CONVERGENCE",
        "default_impact": "Direct DBT Cash Transfer + Subsidized Savings & Institutional Care",
        "rationale": "Maternal nutrition cash transfers (PMMVY) operate in full harmony with Janani Suraksha Yojana institutional delivery and Sukanya Samriddhi girl-child savings.",
        "seq": [
            ("Register Pregnancy / Mother-Child Card (MCP)", "Register at your local Anganwadi Centre / ASHA worker for PMMVY DBT installments."),
            ("Institutional Delivery Benefit", "Avail free delivery and transport incentive under Janani Suraksha Yojana at government hospital."),
            ("Open Sukanya Samriddhi Account", "Deposit initial savings at any post office or nationalized bank for highest tax-free compounding interest.")
        ]
    },
    "msme_business": {
        "keywords": {"business", "msme", "vendor", "street vendor", "entrepreneur", "enterprise", "startup", "mudra", "pmegp", "artisan", "vishwakarma", "loan", "credit", "svanidhi"},
        "stack_title": "💼 MSME Entrepreneurship & Working Capital Stack",
        "stack_type": "MSME_LIVELIHOOD_CONVERGENCE",
        "default_impact": "Capital Margin Grant (15-35%) + Collateral-Free Credit Guarantee",
        "rationale": "Micro-enterprises can combine capital margin grants (PMEGP) with credit guarantees (CGTMSE) and working capital lines (Mudra) without disqualification.",
        "seq": [
            ("Register Udyam Aadhaar", "Obtain instant, free Udyam MSME registration online on udyamregistration.gov.in."),
            ("Apply for PMEGP Capital Subsidy", "Submit project proposal on KVIC portal to secure up to 35% margin money government grant."),
            ("Avail Working Capital via Mudra", "Apply for Shishu/Kishore loan at your operational bank to fund ongoing inventory and receivables.")
        ]
    },
    "senior_disability": {
        "keywords": {"senior", "elderly", "pension", "old age", "disability", "disabled", "divyang", "divyangjan", "udid", "adip", "vayoshri", "vay vandana"},
        "stack_title": "🧓 Senior Citizen & Divyangjan Dignity & Care Stack",
        "stack_type": "SENIOR_DISABILITY_CONVERGENCE",
        "default_impact": "Universal Free Healthcare Cover + Assistive Living Devices + Monthly Pension",
        "rationale": "Universal health coverage under Ayushman Vay Vandana stacks concurrently with assistive living aids (Rashtriya Vayoshri / ADIP) and social security pensions.",
        "seq": [
            ("Obtain Ayushman Vay Vandana Card / UDID", "Generate your senior health card on the Ayushman app or apply for UDID card on swavlambancard.gov.in."),
            ("Apply for Assistive Devices", "Enroll at the District ALIMCO / Social Welfare camp for free hearing aids, wheelchairs, or spectacles."),
            ("Enroll in National Social Assistance (NSAP)", "Submit Aadhaar and bank details at the Tehsil / Block office for monthly Direct DBT pension.")
        ]
    },
    "housing": {
        "keywords": {"housing", "awas", "house", "home", "dwelling", "construction", "pucca house", "pmay", "ashraya"},
        "stack_title": "🏡 Integrated Rural & Urban Habitat Stack",
        "stack_type": "HABITAT_CONVERGENCE",
        "default_impact": "₹1,20,000 - ₹2,50,000 Housing Subsidy + Sanitation Grant + Free LPG Connection",
        "rationale": "Under Union convergence mandates, housing allotment automatically unlocks priority toilet construction grants and clean cooking gas.",
        "seq": [
            ("PMAY Geo-Tagged Sanction", "Complete Gram Panchayat / ULB verification for initial construction installment."),
            ("Claim SBM Sanitation Incentive", "Claim ₹12,000 toilet grant through the local authority upon plinth level inspection."),
            ("Avail PM Ujjwala Connection", "Present your housing sanction letter to the nearest LPG distributor for deposit-free LPG.")
        ]
    },
    "agriculture": {
        "keywords": {"farmer", "farmers", "farm", "farming", "agriculture", "kisan", "crop", "seed", "irrigation", "tractor", "fasal bima", "pmkisan", "pm-kisan", "kusum"},
        "stack_title": "🌾 Integrated Farmer Prosperity & Risk Shield Stack",
        "stack_type": "AGRICULTURAL_CONVERGENCE",
        "default_impact": "₹6,000/yr Direct Cash + Up to ₹3,00,000 Concessional Credit + Comprehensive Crop Insurance",
        "rationale": "PM-KISAN income support operates as the verified anchor for fast-track Kisan Credit Card issuance and seasonal crop insurance.",
        "seq": [
            ("Verify PM-KISAN Record", "Verify your land revenue records (Khatauni/ROR) on pmkisan.gov.in to obtain your DBT farmer ID."),
            ("Avail Concessional Kisan Credit Card", "Submit your PM-KISAN receipt at your bank for single-page KCC processing with 3% interest subvention."),
            ("Auto-Link PM Fasal Bima Yojana", "Enroll your cultivable area before the seasonal cutoff date for automated crop loss compensation.")
        ]
    }
}


def _classify_scheme_domain(scheme: Dict[str, Any]) -> str:
    """Classifies a scheme into its primary policy sector."""
    text_corpus = " ".join([
        str(scheme.get("scheme_name", "")),
        str(scheme.get("name", "")),
        str(scheme.get("slug", "")),
        str(scheme.get("category", "")),
        str(scheme.get("brief", "")),
        str(scheme.get("repository_summary", ""))
    ]).casefold()

    for sector, meta in SECTOR_TAXONOMY.items():
        for kw in meta["keywords"]:
            if kw in text_corpus:
                return sector
    return "general_welfare"


class PolicyInteractionEngine:
    """
    Evaluates policy interactions, cross-scheme exclusions, and synergistic welfare stacks.
    Uses LLM-first dynamic analysis with a multi-sector deterministic fallback.
    """

    @classmethod
    def evaluate(
        cls,
        schemes: List[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]] = None,
        user_query: str = "",
        crawled_results: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Runs comprehensive policy evaluation across candidate schemes.
        """
        if not schemes:
            return {
                "welfare_stack": None,
                "cross_scheme_conflicts": [],
                "conflict_alert": None
            }

        profile = user_profile or {}

        # 1. Check for single-scheme source discrepancies (existing detector)
        source_conflict = SourceConflictDetector.detect_conflicts(
            user_query=user_query,
            extracted_schemes=schemes,
            crawled_results=crawled_results or []
        )

        # 2. Attempt LLM-First Dynamic Analysis
        llm_result = cls._evaluate_with_llm(
            schemes=schemes,
            user_profile=profile,
            user_query=user_query
        )

        if llm_result:
            conflicts = []
            if source_conflict and source_conflict.get("has_conflict"):
                conflicts.append(source_conflict)

            if llm_result.get("has_conflict") and llm_result.get("conflict"):
                llm_conflict = llm_result["conflict"]
                llm_conflict["has_conflict"] = True
                llm_conflict["alert_type"] = "CROSS_SCHEME_MUTUAL_EXCLUSION"
                conflicts.append(llm_conflict)

            welfare_stack = llm_result.get("welfare_stack")
            primary_conflict = conflicts[0] if conflicts else None

            return {
                "welfare_stack": welfare_stack,
                "cross_scheme_conflicts": conflicts,
                "conflict_alert": primary_conflict
            }

        # 3. Deterministic Multi-Sector Fallback Engine
        logger.info("Using multi-sector deterministic fallback for policy interaction.")
        return cls._evaluate_deterministic_fallback(
            schemes=schemes,
            user_profile=profile,
            user_query=user_query,
            source_conflict=source_conflict
        )

    @classmethod
    def _evaluate_with_llm(
        cls,
        schemes: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        user_query: str
    ) -> Optional[Dict[str, Any]]:
        """Invokes Groq LLM to dynamically reason about policy interactions."""
        if not llm_service.api_key:
            return None

        schemes_context = []
        for s in schemes[:6]:
            schemes_context.append({
                "name": s.get("scheme_name") or s.get("name", "Unknown Scheme"),
                "level": s.get("level") or s.get("jurisdiction", "Central"),
                "category": s.get("category", "General"),
                "benefit": s.get("benefit") or (s.get("benefits") and s["benefits"][0]) or "",
                "brief": (s.get("brief") or s.get("repository_summary") or "")[:200],
                "eligibility_sample": [
                    r.get("rule_text") for r in s.get("eligibility_matrix", [])[:3]
                ] if s.get("eligibility_matrix") else []
            })

        user_prompt = (
            f"Citizen Query: {user_query}\n"
            f"Known Citizen Profile: {json.dumps(user_profile)}\n"
            f"Discovered Government Schemes:\n{json.dumps(schemes_context, indent=2)}\n\n"
            "Analyze these schemes for any mutual exclusions / policy conflicts and construct an optimal, "
            "synergistic Welfare Stacking Bundle if applicable."
        )

        try:
            res = llm_service._call_groq_json(
                prompt=user_prompt,
                system_prompt=POLICY_INTERACTION_SYSTEM_PROMPT,
                timeout=12.0
            )
            if res and isinstance(res, dict):
                return res
        except Exception as exc:
            logger.warning("LLM policy evaluation failed: %s", exc)

        return None

    @classmethod
    def _evaluate_deterministic_fallback(
        cls,
        schemes: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        user_query: str,
        source_conflict: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Robust multi-domain deterministic fallback covering all major sectors."""
        conflicts: List[Dict[str, Any]] = []
        if source_conflict and source_conflict.get("has_conflict"):
            conflicts.append(source_conflict)

        # Categorize schemes into sectors
        sector_map: Dict[str, List[Dict[str, Any]]] = {}
        for s in schemes:
            sec = _classify_scheme_domain(s)
            if sec not in sector_map:
                sector_map[sec] = []
            sector_map[sec].append(s)

        # Check for exclusive domain conflicts (e.g. 2 Housing schemes or 2 Scholarships)
        exclusive_sectors = {"housing", "education"}
        for sec in exclusive_sectors:
            competing = sector_map.get(sec, [])
            if len(competing) >= 2:
                s1, s2 = competing[0], competing[1]
                name1 = s1.get("scheme_name") or s1.get("name", "Scheme 1")
                name2 = s2.get("scheme_name") or s2.get("name", "Scheme 2")
                level1 = s1.get("level") or s1.get("jurisdiction", "Central")
                level2 = s2.get("level") or s2.get("jurisdiction", "State")

                rule_text = (
                    "Central/State guidelines strictly forbid claiming concurrent assistance for the same benefit."
                    if sec == "housing"
                    else "National Scholarship Portal guidelines prohibit holding multiple maintenance allowances simultaneously."
                )

                conflicts.append({
                    "has_conflict": True,
                    "scheme_id": f"{s1.get('slug', 'a')}-vs-{s2.get('slug', 'b')}",
                    "scheme_name": f"{name1} vs {name2}",
                    "alert_type": "CROSS_SCHEME_MUTUAL_EXCLUSION",
                    "severity": "HIGH",
                    "title": f"Policy Exclusion: Cannot Claim Both {name1} and {name2}",
                    "discrepancy_field": f"Dual {sec.capitalize()} Benefit Restriction",
                    "scheme_a": {"name": name1, "level": level1},
                    "scheme_b": {"name": name2, "level": level2},
                    "source_a": {"portal": f"{name1} Guidelines", "rule": rule_text},
                    "source_b": {"portal": f"{name2} Guidelines", "rule": "De-duplication audit rejects duplicate submissions."},
                    "explanation": (
                        f"Both '{name1}' and '{name2}' operate under the {sec.capitalize()} sector. "
                        f"Government guidelines bar concurrent enrollment in duplicate subsidy programs."
                    ),
                    "recommendation": {
                        "preferred_scheme": name1,
                        "reason": f"Prioritize {name1} for primary application; do not submit dual applications.",
                        "action": f"Apply to {name1} first. Only apply to {name2} if primary application is unfulfilled."
                    },
                    "clarification_prompt": f"Which scheme would you like to prioritize for detailed checking?",
                    "options": [f"Prioritize {name1}", f"Prioritize {name2}", "Compare both options"]
                })

        # Build synergistic welfare stack for the dominant sector
        welfare_stack = None
        if len(schemes) >= 2:
            # Pick dominant sector with most matches, or check query keywords
            q_lower = user_query.lower()
            target_sector = None

            for sec, meta in SECTOR_TAXONOMY.items():
                if any(kw in q_lower for kw in meta["keywords"]):
                    target_sector = sec
                    break

            if not target_sector:
                for sec, items in sector_map.items():
                    if sec != "general_welfare" and len(items) >= 1:
                        target_sector = sec
                        break

            if not target_sector:
                target_sector = "health" if "health" in sector_map else "agriculture"

            meta = SECTOR_TAXONOMY.get(target_sector, SECTOR_TAXONOMY["health"])

            stacked_items = []
            seen_names = set()
            for s in schemes[:4]:
                name = s.get("scheme_name") or s.get("name")
                if not name or name in seen_names:
                    continue
                seen_names.add(name)
                b_text = s.get("benefit") or (s.get("benefits") and s["benefits"][0]) or "Official welfare benefit"
                if isinstance(b_text, dict):
                    b_text = b_text.get("text", "")
                stacked_items.append({
                    "name": name,
                    "role": s.get("category", "Welfare Assistance"),
                    "benefit_summary": str(b_text)[:120],
                    "url": s.get("url", "https://www.myscheme.gov.in")
                })

            welfare_stack = {
                "bundle_title": meta["stack_title"],
                "bundle_type": meta["stack_type"],
                "badge": "Policy Convergence Approved",
                "description": meta["rationale"],
                "total_financial_impact": meta["default_impact"],
                "schemes": stacked_items,
                "application_sequence": [
                    {
                        "step": idx + 1,
                        "title": step[0],
                        "instruction": step[1]
                    }
                    for idx, step in enumerate(meta["seq"][:len(stacked_items)])
                ]
            }

        primary_conflict = conflicts[0] if conflicts else None

        return {
            "welfare_stack": welfare_stack,
            "cross_scheme_conflicts": conflicts,
            "conflict_alert": primary_conflict
        }
