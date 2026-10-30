"""Evidence validation, profile questions, and deterministic scheme evaluation."""

import re
from typing import Any, Dict, List, Optional, Tuple

from .whitelist import is_whitelisted_domain


SUPPORTED_FIELDS = {
    "state",
    "course_type",
    "annual_family_income",
    "loan_amount",
    "age",
    "social_category",
    "gender",
    "admission_status",
    "institution_type",
    "course_mode",
    "occupation",
    "landholding",
    "disability_status",
    "marital_status",
    "residency_status",
    "rural_urban",
    "business_type",
    "artisan_trade",
    "vendor_status",
    "farmer_status",
    "property_ownership",
    "bank_account",
    "course_duration",
    "bpl_status",
    "family_status",
    "landholding_category",
    "cultivable_land",
    "education_qualification",
    "single_girl_child",
    "class_10_marks_pct",
    "roof_rights",
    "electricity_consumption",
}
SUPPORTED_OPERATORS = {"eq", "neq", "in", "not_in", "lte", "lt", "gte", "gt", "between"}

FIELD_INFO = {
    "state": ("State / UT", "Which State / UT applies to you?"),
    "course_type": ("Course", "What course are you pursuing?"),
    "annual_family_income": ("Annual family income", "What is your family's annual income?"),
    "loan_amount": ("Loan amount", "What education-loan amount do you need?"),
    "age": ("Age", "What is your age?"),
    "social_category": ("Social category", "Which social category applies to you?"),
    "gender": ("Gender", "What is your gender?"),
    "admission_status": ("Admission", "Do you have confirmed admission?"),
    "institution_type": ("Institution", "What type of institution/course approval applies?"),
    "course_mode": ("Course mode", "Is your course full-time or part-time?"),
    "occupation": ("Occupation", "What is your current occupation or work status?"),
    "landholding": ("Landholding", "What best describes your landholding?"),
    "disability_status": ("Disability status", "Does the stated disability criterion apply to you?"),
    "marital_status": ("Marital status", "What is your marital status?"),
    "residency_status": ("Residency", "Does the stated residency/domicile criterion apply to you?"),
    "rural_urban": ("Area of residence", "Do you live in a rural or urban area?"),
    "business_type": ("Business type", "What type of business do you run or plan to start?"),
    "artisan_trade": ("Artisan trade", "Which artisan trade or craft applies to you?"),
    "vendor_status": ("Vendor status", "Are you a street vendor?"),
    "farmer_status": ("Farmer status", "Do you meet the scheme's farmer/cultivator condition?"),
    "property_ownership": ("Property ownership", "What best describes your property ownership?"),
    "bank_account": ("Bank account", "Do you meet the scheme's bank-account requirement?"),
    "course_duration": ("Course duration", "How long is your course?"),
    "bpl_status": ("BPL status", "Does the stated Below Poverty Line condition apply to you?"),
    "family_status": ("Family status", "Which family or beneficiary status applies to you?"),
    "landholding_category": ("Landholding category", "What is your landholding category?"),
    "cultivable_land": ("Cultivable land", "Do you own cultivable agricultural land?"),
    "education_qualification": ("Education qualification", "What is your highest educational qualification?"),
    "single_girl_child": ("Single girl child", "Are you an only girl child of your parents?"),
    "class_10_marks_pct": ("Class 10 percentage", "What was your Class 10 percentage?"),
    "roof_rights": ("Roof ownership", "Do you own an independent rooftop?"),
    "electricity_consumption": ("Electricity consumption", "What is your monthly electricity consumption (units)?"),
}

PROFILE_ALIASES = {
    "state": "state",
    "state ut": "state",
    "state / ut": "state",
    "region": "state",
    "course": "course_type",
    "course type": "course_type",
    "course level": "course_type",
    "annual family income": "annual_family_income",
    "family annual income": "annual_family_income",
    "family income": "annual_family_income",
    "income": "annual_family_income",
    "desired loan amount": "loan_amount",
    "loan amount": "loan_amount",
    "age": "age",
    "social category": "social_category",
    "category": "social_category",
    "gender": "gender",
    "admission": "admission_status",
    "admission status": "admission_status",
    "institution type": "institution_type",
    "course mode": "course_mode",
    "occupation": "occupation",
    "work status": "occupation",
    "landholding": "landholding",
    "land holding": "landholding",
    "disability": "disability_status",
    "disability status": "disability_status",
    "marital status": "marital_status",
    "residency": "residency_status",
    "residency status": "residency_status",
    "domicile": "residency_status",
    "rural urban": "rural_urban",
    "area of residence": "rural_urban",
    "business type": "business_type",
    "artisan trade": "artisan_trade",
    "vendor status": "vendor_status",
    "farmer status": "farmer_status",
    "property ownership": "property_ownership",
    "bank account": "bank_account",
    "course duration": "course_duration",
    "program duration": "course_duration",
    "programme duration": "course_duration",
    "bpl status": "bpl_status",
    "poverty status": "bpl_status",
    "family status": "family_status",
    "landholding category": "landholding_category",
    "cultivable land": "cultivable_land",
    "education qualification": "education_qualification",
    "education": "education_qualification",
    "single girl child": "single_girl_child",
    "class 10 marks pct": "class_10_marks_pct",
    "10th percentage": "class_10_marks_pct",
    "roof rights": "roof_rights",
    "independent roof": "roof_rights",
    "electricity consumption": "electricity_consumption",
}

_MONEY_RE = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*(lakh|lakhs|lac|crore|crores)?", re.IGNORECASE)
FIELD_EVIDENCE_TERMS = {
    "state": ("state", "domicile", "resident", "residence"),
    "course_type": ("course", "degree", "engineering", "technical", "professional", "programme", "program"),
    "annual_family_income": ("income", "earnings"),
    "loan_amount": ("loan", "credit", "borrow"),
    "age": ("age", "years"),
    "social_category": ("category", "caste", "obc", "minority", "scheduled caste", "scheduled tribe"),
    "gender": ("gender", "women", "woman", "girl", "female", "male"),
    "admission_status": ("admission", "enrol", "enroll"),
    "institution_type": ("institution", "university", "college", "aicte", "recognized", "recognised"),
    "course_mode": ("full time", "full time", "part time", "distance"),
    "occupation": ("occupation", "worker", "farmer", "vendor", "artisan", "employment"),
    "landholding": ("land", "acre", "hectare", "landholding"),
    "disability_status": ("disability", "disabled", "person with disability", "pwd"),
    "marital_status": ("marital", "married", "unmarried", "widow", "widowed"),
    "residency_status": ("resident", "residence", "domicile", "permanent resident"),
    "rural_urban": ("rural", "urban", "village", "municipal"),
    "business_type": ("business", "enterprise", "startup", "shop", "micro-enterprise"),
    "artisan_trade": ("artisan", "craft", "trade", "craftsperson", "traditional occupation"),
    "vendor_status": ("street vendor", "vendor", "hawker"),
    "farmer_status": ("farmer", "cultivator", "agricultural"),
    "property_ownership": ("house", "property", "owned", "ownership", "land"),
    "bank_account": ("bank account", "bank", "account", "aadhaar seeded"),
    "course_duration": ("course duration", "duration of course", "years"),
    "bpl_status": ("below poverty line", "bpl", "poverty line"),
    "family_status": ("family", "widow", "orphan", "single parent", "household"),
}


def normalize_profile(profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize only explicitly supplied profile keys; never infer answers."""
    normalized: Dict[str, Any] = {}
    for key, value in (profile or {}).items():
        normalized_key = re.sub(r"[_\s]+", " ", str(key).casefold()).strip()
        canonical_key = PROFILE_ALIASES.get(
            normalized_key
        )
        if normalized_key in SUPPORTED_FIELDS:
            canonical_key = normalized_key
        if canonical_key and value is not None and str(value).strip():
            normalized[canonical_key] = value

    # Smart semantic derivation for related welfare criteria
    occ = str(normalized.get("occupation", "")).casefold()
    if any(k in occ for k in ["farmer", "cultivator", "agri"]):
        if "farmer_status" not in normalized:
            normalized["farmer_status"] = "Farmer family"
        if "cultivable_land" not in normalized and normalized.get("landholding"):
            normalized["cultivable_land"] = "Yes"

    if "landholding" in normalized:
        lh_val = str(normalized["landholding"]).casefold()
        if "cultivable_land" not in normalized and lh_val not in ("none", "no", "landless", "0"):
            normalized["cultivable_land"] = "Yes"
        if "landholding_category" not in normalized:
            num = _parse_number(lh_val)
            if num is not None:
                ha = num if ("hectare" in lh_val or "ha" in lh_val) else (num / 2.47)
                if ha < 1.0:
                    normalized["landholding_category"] = "Marginal Farmer (< 1 Hectare)"
                elif ha <= 2.0:
                    normalized["landholding_category"] = "Small Farmer (1-2 Hectares)"
                else:
                    normalized["landholding_category"] = "Large / Medium Farmer (> 2 Hectares)"
            elif "marginal" in lh_val:
                normalized["landholding_category"] = "Marginal Farmer (< 1 Hectare)"
            elif "small" in lh_val:
                normalized["landholding_category"] = "Small Farmer (1-2 Hectares)"
            elif "large" in lh_val or "medium" in lh_val:
                normalized["landholding_category"] = "Large / Medium Farmer (> 2 Hectares)"

    return normalized


def _normalize_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).casefold()).strip()


def _parse_number(value: Any) -> Optional[float]:
    match = _MONEY_RE.search(str(value).casefold().replace("₹", "").replace("rs.", ""))
    if not match:
        return None
    number = float(match.group(1).replace(",", ""))
    unit = (match.group(2) or "").casefold()
    if unit in {"lakh", "lakhs", "lac"}:
        number *= 100_000
    elif unit in {"crore", "crores"}:
        number *= 10_000_000
    return number


def _number_mentions(text: str) -> List[float]:
    values = []
    normalized = str(text).casefold().replace("₹", "").replace("rs.", "")
    for match in _MONEY_RE.finditer(normalized):
        number = float(match.group(1).replace(",", ""))
        unit = (match.group(2) or "").casefold()
        if unit in {"lakh", "lakhs", "lac"}:
            number *= 100_000
        elif unit in {"crore", "crores"}:
            number *= 10_000_000
        values.append(number)
    return values


def _rule_matches_quotation(rule: Dict[str, Any], quote: str) -> bool:
    """Reject model interpretations that conflict with numeric/comparison words in the quote."""
    field, operator, value = rule.get("field"), rule.get("operator"), rule.get("value")
    normalized = quote.casefold()
    normalized_quote = _normalize_text(quote)
    field_terms = FIELD_EVIDENCE_TERMS.get(field, ())
    if not any(_normalize_text(term) in normalized_quote for term in field_terms):
        return False
    if operator in {"lte", "lt", "gte", "gt", "between"}:
        mentions = _number_mentions(quote)
        expected = (
            [float(value["min"]), float(value["max"])]
            if operator == "between" and isinstance(value, dict)
            else [float(value)]
            if isinstance(value, (int, float))
            else []
        )
        if not expected or any(
            not any(abs(number - target) < 0.01 for number in mentions)
            for target in expected
        ):
            return False
        if operator == "lte":
            return any(token in normalized for token in ("at most", "up to", "not exceed", "no more than", "not exceed", "<=", "maximum"))
        if operator == "lt":
            return any(token in normalized for token in ("less than", "below", "under", "<"))
        if operator == "gte":
            return any(token in normalized for token in ("at least", "not less than", ">=", "minimum"))
        if operator == "gt":
            return any(token in normalized for token in ("more than", "above", "greater than", ">", "exceeding"))
        return "between" in normalized or "to" in normalized or "–" in normalized or "-" in normalized

    expected_values = value if isinstance(value, list) else [value]
    quote_text = _normalize_text(quote)
    return all(
        _normalize_text(item) in quote_text
        for item in expected_values
        if str(item).strip()
    )


def _money_label(amount: float) -> str:
    if amount >= 100_000:
        return f"₹{amount / 100_000:g} lakh"
    return f"₹{amount:,.0f}"


def _field_options(rule: Dict[str, Any]) -> List[str]:
    field = rule["field"]
    operator = rule["operator"]
    value = rule.get("value")

    if field in {
        "annual_family_income", "loan_amount", "age", "course_duration", "landholding"
    } and operator in {
        "lte", "lt", "gte", "gt", "between"
    }:
        unit = "years" if field in {"age", "course_duration"} else "Ha" if field == "landholding" else None
        fmt = (lambda v: f"{v:g} {unit}") if unit else _money_label

        if operator == "between" and isinstance(value, dict):
            low, high = float(value["min"]), float(value["max"])
            low_label = fmt(low)
            high_label = fmt(high)
            return [
                f"Below {low_label}",
                f"{low_label}–{high_label}",
                f"Above {high_label}",
                "Not sure",
            ]
        amount = float(value)
        boundary = fmt(amount)
        if operator == "lte":
            return [f"At or below {boundary}", f"Above {boundary}", "Not sure"]
        if operator == "lt":
            return [f"Below {boundary}", f"At or above {boundary}", "Not sure"]
        if operator == "gte":
            return [f"Below {boundary}", f"At or above {boundary}", "Not sure"]
        return [f"At or below {boundary}", f"Above {boundary}", "Not sure"]

    if field == "course_type":
        return ["Engineering / B.Tech", "Other course", "Not sure"]
    if field == "admission_status":
        return ["Confirmed admission", "No admission yet", "Not sure"]
    if field == "course_mode":
        return ["Full-time", "Part-time / distance", "Not sure"]
    if operator in {"in", "not_in"} and isinstance(value, list):
        return [*(str(item) for item in value), "None of these", "Not sure"]
    return [str(value), "None of these", "Not sure"] if value is not None else ["Yes", "No", "Not sure"]


def profile_questions(
    rules: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Ask once for every supported rule field not already explicitly answered."""
    known = normalize_profile(profile)
    questions: List[Dict[str, Any]] = []
    seen = set()
    for rule in rules:
        field = rule.get("field")
        if field not in SUPPORTED_FIELDS or rule.get("operator") not in SUPPORTED_OPERATORS:
            continue
        if field in known or field in seen:
            continue
        seen.add(field)
        label, question = FIELD_INFO[field]
        questions.append({
            "id": field,
            "label": label,
            "question": question,
            "options": _field_options(rule),
        })
    return questions


def validate_rule_record(
    record: Dict[str, Any],
    source_url: str,
    page_text: str,
) -> Optional[Dict[str, Any]]:
    """Accept only supported rule shapes whose quoted evidence exists on an allowed source."""
    allowed, _, _ = is_whitelisted_domain(source_url)
    if not allowed or not isinstance(record, dict):
        return None

    scheme_name = str(record.get("scheme_name", "")).strip()
    raw_rules = record.get("eligibility_rules")
    if len(scheme_name) < 4 or not isinstance(raw_rules, list):
        return None

    normalized_page = re.sub(r"\s+", " ", page_text).casefold()
    benefit_quote = re.sub(
        r"\s+", " ", str(record.get("benefit_evidence_quote", "")).strip()
    )
    benefit = (
        str(record.get("benefit", "")).strip()
        if len(benefit_quote) >= 12
        and benefit_quote.casefold() in normalized_page
        else "Not established by the crawled evidence."
    )
    application_quote = re.sub(
        r"\s+", " ", str(record.get("application_evidence_quote", "")).strip()
    )
    application_process = (
        str(record.get("application_process", "")).strip()
        if len(application_quote) >= 12
        and application_quote.casefold() in normalized_page
        else ""
    )
    accepted_rules = []
    for rule in raw_rules:
        if not isinstance(rule, dict):
            continue
        field = rule.get("field")
        operator = rule.get("operator")
        quote = re.sub(r"\s+", " ", str(rule.get("evidence_quote", "")).strip())
        value = rule.get("value")
        if field not in SUPPORTED_FIELDS or operator not in SUPPORTED_OPERATORS:
            continue
        if len(quote) < 12 or re.sub(r"\s+", " ", quote).casefold() not in normalized_page:
            continue
        if not _rule_matches_quotation(rule, quote):
            continue
        if operator == "between":
            if not isinstance(value, dict) or not {"min", "max"} <= value.keys():
                continue
            if not all(isinstance(value[key], (int, float)) for key in ("min", "max")):
                continue
            if value["min"] > value["max"]:
                continue
        elif operator in {"in", "not_in"}:
            if not isinstance(value, list) or not value:
                continue
        elif operator in {"lte", "lt", "gte", "gt"}:
            if not isinstance(value, (int, float)):
                continue
        elif value is None or isinstance(value, (dict, list)):
            continue

        accepted_rules.append({
            "field": field,
            "operator": operator,
            "value": value,
            "rule_text": str(rule.get("rule_text", quote)).strip(),
            "evidence_quote": quote,
            "source_url": source_url,
        })

    if not accepted_rules:
        return None

    return {
        "scheme_name": scheme_name,
        "jurisdiction": str(record.get("jurisdiction", "Unknown")),
        "benefit": benefit,
        "benefit_evidence_quote": benefit_quote if benefit != "Not established by the crawled evidence." else "",
        "eligibility_rules": accepted_rules,
        "application_process": application_process,
        "application_evidence_quote": application_quote if application_process else "",
        "sources": [{"url": source_url, "title": str(record.get("source_title", ""))}],
        "evidence_status": "quoted_source_evidence",
    }


def _numeric_profile_interval(value: Any, field: str) -> Optional[Tuple[float, float]]:
    if isinstance(value, dict) and ("min" in value or "max" in value):
        low = float(value.get("min", 0.0))
        high = float(value.get("max", float("inf")))
        return (min(low, high), max(low, high))
    if isinstance(value, (int, float)):
        return (float(value), float(value))
    text = str(value).casefold().strip()
    if text in {
        "not sure", "prefer not to say", "unknown", "skipped",
        "other / prefer not to say",
    }:
        return None
    range_match = re.search(r"(.+?)\s*(?:-|–|to)\s*(.+)", text)
    if range_match:
        low, high = _parse_number(range_match.group(1)), _parse_number(range_match.group(2))
        if low is not None and high is not None:
            return (min(low, high), max(low, high))
    if field == "age":
        if "under" in text or ("below" in text and "at or below" not in text):
            number = _parse_number(text)
            return (0, number - 1e-9) if number is not None else None
        if ("above" in text or "over" in text) and "at or above" not in text:
            number = _parse_number(text)
            return (number + 1e-9, float("inf")) if number is not None else None
        if "at or below" in text or "below or equal" in text:
            number = _parse_number(text)
            return (0, number) if number is not None else None
        if "at or above" in text:
            number = _parse_number(text)
            return (number, float("inf")) if number is not None else None
    number = _parse_number(text)
    if number is not None:
        if "at or below" in text:
            return (0, number)
        if "at or above" in text:
            return (number, float("inf"))
        if "at or above" in text:
            return (number, float("inf"))
        if "above" in text or "over" in text:
            return (number + 1e-9, float("inf"))
        if "at or below" in text:
            return (0, number)
        if "below" in text or "under" in text:
            return (0, number - 1e-9)
        return (number, number)
    return None


def _compare_rule(rule: Dict[str, Any], profile: Dict[str, Any]) -> str:
    field, operator, expected = rule["field"], rule["operator"], rule.get("value")
    if field not in profile:
        return "UNKNOWN"
    actual = profile[field]

    if operator in {"lte", "lt", "gte", "gt", "between"}:
        interval = _numeric_profile_interval(actual, field)
        if interval is None:
            return "UNKNOWN"
        low, high = interval
        if operator == "lte":
            return "MET" if high <= expected else "NOT_MET" if low > expected else "UNKNOWN"
        if operator == "lt":
            return "MET" if high < expected else "NOT_MET" if low >= expected else "UNKNOWN"
        if operator == "gte":
            return "MET" if low >= expected else "NOT_MET" if high < expected else "UNKNOWN"
        if operator == "gt":
            return "MET" if low > expected else "NOT_MET" if high <= expected else "UNKNOWN"
        if isinstance(expected, dict):
            lower, upper = float(expected["min"]), float(expected["max"])
            if low >= lower and high <= upper:
                return "MET"
            if high < lower or low > upper:
                return "NOT_MET"
        return "UNKNOWN"

    actual_text = _normalize_text(actual)
    expected_values = expected if isinstance(expected, list) else [expected]
    expected_texts = [_normalize_text(value) for value in expected_values]
    matches = actual_text in expected_texts or any(
        token and (token in actual_text or actual_text in token)
        for token in expected_texts
    )
    if operator in {"eq", "in"}:
        if actual_text in {
            "not sure", "prefer not to say", "unknown", "other", "skipped",
            "other prefer not to say",
        }:
            return "UNKNOWN"
        return "MET" if matches else "NOT_MET"
    if operator in {"neq", "not_in"}:
        if actual_text in {
            "not sure", "prefer not to say", "unknown", "other", "skipped",
            "other prefer not to say",
        }:
            return "UNKNOWN"
        return "NOT_MET" if matches else "MET"
    return "UNKNOWN"


def evaluate_schemes(
    schemes: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Evaluate each cited supported rule without filling any missing profile values."""
    normalized = normalize_profile(profile)
    results = []
    for scheme in schemes:
        rules = scheme.get("eligibility_rules", [])
        field_values: Dict[Tuple[str, str], set] = {}
        for rule in rules:
            field_values.setdefault(
                (rule.get("field", ""), rule.get("operator", "")), set()
            ).add(str(rule.get("value")))
        checks = []
        for rule in rules:
            conflict = len(field_values[(rule.get("field", ""), rule.get("operator", ""))]) > 1
            checks.append({
                **rule,
                "status": "UNKNOWN" if conflict else _compare_rule(rule, normalized),
                "conflict": conflict,
            })
        statuses = [item["status"] for item in checks]
        has_source = bool(scheme.get("sources") or scheme.get("url") or scheme.get("source_portal"))
        if not statuses or not has_source:
            verdict = "not_evaluated"
        elif "NOT_MET" in statuses:
            verdict = "ineligible"
        elif all(status == "MET" for status in statuses):
            verdict = "meets_captured_rules"
        else:
            verdict = "needs_information"
        results.append({
            **scheme,
            "eligibility_matrix": checks,
            "eligibility_status": verdict,
        })
    return results
