"""Deterministic query routing, portal selection, and profile-question tools."""

import re
from typing import Any, Dict, List, Optional

from .portal_catalog import SEED_GOVERNMENT_PORTALS, get_state_region_options
from .whitelist import is_whitelisted_domain


TOPIC_KEYWORDS = {
    "education": {
        "education", "student", "students", "college", "school", "university",
        "btech", "degree", "course", "scholarship", "tuition", "study", "loan",
    },
    "agriculture": {
        "farmer", "farmers", "farm", "farming", "agriculture", "agricultural",
        "kisan", "crop", "tractor", "tractors", "seed", "irrigation", "land",
        "equipment", "equipments", "machinery", "machine", "implement",
        "implements", "harvester", "sprayer", "cultivator", "mechanization",
        "mechanisation",
    },
    "health": {
        "health", "medical", "hospital", "treatment", "insurance", "medicine",
        "ayushman", "disability",
    },
    "housing": {
        "housing", "house", "home", "awas", "rent", "construction",
    },
    "employment": {
        "employment", "job", "jobs", "unemployment", "worker", "workers",
        "labour", "labor", "pension", "retirement",
    },
    "business": {
        "business", "entrepreneur", "enterprise", "vendor", "artisan", "mudra",
        "startup", "working", "capital",
    },
    "women_child": {
        "women", "woman", "girl", "girls", "mother", "maternity", "child",
        "children", "widow",
    },
    "energy": {
        "solar", "energy", "electricity", "power", "bijli", "rooftop",
    },
}

TOPIC_PORTAL_TERMS = {
    "education": TOPIC_KEYWORDS["education"] - {"loan"},
    "agriculture": TOPIC_KEYWORDS["agriculture"],
    "health": TOPIC_KEYWORDS["health"],
    "housing": TOPIC_KEYWORDS["housing"],
    "employment": TOPIC_KEYWORDS["employment"],
    "business": TOPIC_KEYWORDS["business"],
    "women_child": TOPIC_KEYWORDS["women_child"],
    "energy": TOPIC_KEYWORDS["energy"],
    "general": {"scheme", "schemes", "welfare", "citizen", "government", "portal"},
}

PROFILE_QUESTION_TEMPLATES = {
    "education": (
        ("income", "Family Annual Income", "What is your family’s annual income?", ["Under ₹2.5 lakh", "₹2.5–4.5 lakh", "₹4.5–8 lakh", "Above ₹8 lakh", "Not sure"]),
        ("course", "Course Type", "What course are you taking?", ["Engineering / B.Tech", "Other professional course", "General degree", "Other / Not sure"]),
        ("loan_amount", "Desired Loan Amount", "How much education loan do you need?", ["Up to ₹4 lakh", "₹4–7.5 lakh", "₹7.5–10 lakh", "Above ₹10 lakh", "Not sure"]),
        ("social_category", "Social Category", "Which social category applies to you?", ["General", "SC", "ST", "OBC", "Minority", "Prefer not to say"]),
        ("gender", "Gender", "What is your gender?", ["Woman", "Man", "Other / Prefer not to say"]),
    ),
    "agriculture": (
        ("occupation", "Applicant Occupation", "Are you applying as a farmer or agricultural worker?", ["Farmer / cultivator", "Agricultural worker", "Other", "Prefer not to say"]),
        ("landholding", "Landholding", "What best describes your landholding?", ["Landowner", "Tenant / leased land", "Landless", "Not sure"]),
        ("income", "Family Annual Income", "What is your family’s annual income?", ["Under ₹2.5 lakh", "₹2.5–5 lakh", "₹5–8 lakh", "Above ₹8 lakh", "Not sure"]),
        ("social_category", "Social Category", "Which social category applies to you?", ["General", "SC", "ST", "OBC", "Prefer not to say"]),
    ),
    "health": (
        ("age", "Age", "What is your age group?", ["Under 18", "18–59", "60–69", "70 or older", "Prefer not to say"]),
        ("income", "Family Annual Income", "What is your family’s annual income?", ["Under ₹2.5 lakh", "₹2.5–5 lakh", "₹5–8 lakh", "Above ₹8 lakh", "Not sure"]),
        ("social_category", "Social Category", "Which social category applies to you?", ["General", "SC", "ST", "OBC", "Prefer not to say"]),
    ),
    "housing": (
        ("income", "Family Annual Income", "What is your family’s annual income?", ["EWS", "LIG", "MIG", "Above these categories", "Not sure"]),
        ("occupation", "Current Housing", "Do you or your family own a permanent house?", ["Yes", "No", "Not sure"]),
    ),
    "employment": (
        ("age", "Age", "What is your age group?", ["Under 18", "18–24", "25–59", "60 or older", "Prefer not to say"]),
        ("occupation", "Employment Status", "What is your current work status?", ["Employed", "Unemployed", "Self-employed", "Informal / unorganised worker", "Other"]),
        ("income", "Family Annual Income", "What is your family’s annual income?", ["Under ₹2.5 lakh", "₹2.5–5 lakh", "₹5–8 lakh", "Above ₹8 lakh", "Not sure"]),
    ),
    "business": (
        ("occupation", "Business Type", "What best describes your work or business?", ["Street vendor", "Artisan / craft worker", "Small business", "Starting a business", "Other"]),
        ("loan_amount", "Desired Loan Amount", "How much financial support do you need?", ["Up to ₹1 lakh", "₹1–5 lakh", "₹5–10 lakh", "Above ₹10 lakh", "Not sure"]),
        ("social_category", "Social Category", "Which social category applies to you?", ["General", "SC", "ST", "OBC", "Prefer not to say"]),
    ),
    "women_child": (
        ("age", "Age", "What is your age group?", ["Under 18", "18–24", "25–59", "60 or older", "Prefer not to say"]),
        ("income", "Family Annual Income", "What is your family’s annual income?", ["Under ₹2.5 lakh", "₹2.5–5 lakh", "₹5–8 lakh", "Above ₹8 lakh", "Not sure"]),
        ("gender", "Gender", "Who is the applicant?", ["Woman / girl", "Man / boy", "Other / Prefer not to say"]),
    ),
    "energy": (
        ("occupation", "Electricity Connection", "What type of electricity connection do you have?", ["Domestic household", "Agricultural", "Commercial", "No connection / Not sure"]),
        ("income", "Family Annual Income", "What is your family’s annual income?", ["Under ₹2.5 lakh", "₹2.5–5 lakh", "₹5–8 lakh", "Above ₹8 lakh", "Not sure"]),
    ),
    "general": (
        ("age", "Age", "What is your age group?", ["Under 18", "18–24", "25–59", "60 or older", "Prefer not to say"]),
        ("income", "Family Annual Income", "What is your family’s annual income?", ["Under ₹2.5 lakh", "₹2.5–5 lakh", "₹5–8 lakh", "Above ₹8 lakh", "Not sure"]),
        ("social_category", "Social Category", "Which social category applies to you?", ["General", "SC", "ST", "OBC", "Minority", "Prefer not to say"]),
        ("occupation", "Occupation", "What best describes your current work?", ["Student", "Farmer", "Employed", "Self-employed", "Unemployed", "Other"]),
    ),
}


def classify_query(query: str) -> str:
    """Choose a topic by fixed keyword rules, resolving relational intent and target beneficiaries first."""
    lower = query.casefold()
    terms = set(re.findall(r"[a-z0-9]+", lower))

    # Relational Check: Beneficiary overrides applicant
    # e.g., "i am a graduate need loan for old parents" -> Target is senior parents, not student education loan!
    is_for_parents = bool(
        re.search(r"\b(old\s*parents|elderly\s*parents|for\s+(?:my\s+)?(?:old|elderly|aging|retired)?\s*(?:parents|father|mother|grandmother|grandfather|senior|elderly))\b", lower)
    )
    if is_for_parents:
        if terms & {"health", "medical", "hospital", "treatment", "ayushman", "surgery"}:
            return "health"
        if terms & {"pension", "pensions", "nsap", "vridha", "retirement"}:
            return "employment"
        return "general"

    if "education" in terms and terms & {"loan", "loans"}:
        return "education"
    if terms & {"btech", "student", "students", "college"} and terms & {
        "loan", "loans", "tuition", "education",
    }:
        return "education"
    scores = {
        topic: len(terms & keywords)
        for topic, keywords in TOPIC_KEYWORDS.items()
    }
    best_topic = max(scores, key=scores.get)
    return best_topic if scores[best_topic] else "general"


def infer_profile_from_text(text: str) -> Dict[str, Any]:
    """Deterministically extracts beneficiary demographic and eligibility attributes from natural text."""
    if not text:
        return {}

    inferred: Dict[str, Any] = {}
    lower = text.casefold()

    # Relational Beneficiary Checks:
    # 1. Beneficiary is elderly parents/grandparents
    if re.search(r"\b(old\s*parents|elderly\s*parents|for\s+(?:my\s+)?(?:old|elderly|aging|retired)?\s*(?:parents|father|mother|grandmother|grandfather|senior))\b", lower):
        inferred["age"] = "60 or older"
        # Since beneficiary is elderly parents, do NOT assign student or 18-24 even if applicant is "graduate"
        return inferred

    # 2. Beneficiary is daughter / girl child
    if re.search(r"\b(for\s+(?:my\s+)?(?:single\s+)?(?:daughter|girl\s*child|beti|kanya)|single\s*girl\s*child)\b", lower):
        inferred["gender"] = "Woman / girl"
        inferred["age"] = "Under 18"
        return inferred

    # 1. Gender (if not relational or self-applied)
    if re.search(r"\b(girl|girls|daughter|daughters|woman|women|female|females|lady|ladies|mother|mothers|widow|widows|maternity|pregnant|pregnancy|lactating|mahila|kanya|beti|balika)\b", lower):
        inferred["gender"] = "Woman / girl"
    elif re.search(r"\b(boy|boys|son|sons|man|men|male|males|father|fathers|husband|purush|balak)\b", lower):
        inferred["gender"] = "Man / boy"

    # 2. Age group
    explicit_age = None
    age_match = re.search(r"\b(?:age|aged|am)\s*[:=]?\s*(\d{1,2})\b", lower)
    if not age_match:
        age_match = re.search(r"\b(\d{1,2})\s*(?:years?|yrs?)(?:\s*old)?\b", lower)
    if age_match:
        try:
            val = int(age_match.group(1))
            if val < 18:
                explicit_age = "Under 18"
            elif 18 <= val <= 24:
                explicit_age = "18–24"
            elif 25 <= val <= 59:
                explicit_age = "25–59"
            else:
                explicit_age = "60 or older"
        except (ValueError, IndexError):
            pass

    if explicit_age:
        inferred["age"] = explicit_age
    elif re.search(r"\b(child|children|minor|minors|kid|kids|infant|baby|babies|girl\s*child|boy\s*child|single\s*girl\s*child|school\s*going|school\s*student|matric|primary\s*school|high\s*school|balak|balika|shishu)\b", lower):
        inferred["age"] = "Under 18"
    elif re.search(r"\b(senior\s*citizen|senior\s*citizens|elderly|old\s*age|old-age|pensioner|pensioners|retired|retirement|vridha|60\+|70\+)\b", lower):
        inferred["age"] = "60 or older"
    elif re.search(r"\b(college|undergraduate|ug|btech|b\.tech|be\b|b\.e\b|intermediate|polytechnic|diploma\s*student|fresher|youth)\b", lower):
        inferred["age"] = "18–24"
    elif re.search(r"\b(middle\s*aged?|working\s*age|salaried)\b", lower):
        inferred["age"] = "25–59"

    # 3. Occupation
    if re.search(r"\b(farmer|farmers|kisan|cultivator|cultivators|agriculture|agricultural\s*worker|small\s*farmer|marginal\s*farmer|krishi)\b", lower):
        inferred["occupation"] = "Farmer / cultivator"
    elif re.search(r"\b(student|students|studying|study|scholarship|college\s*student|school\s*student|btech)\b", lower):
        inferred["occupation"] = "Student"
    elif re.search(r"\b(street\s*vendor|street\s*vendors|vendor|vendors|hawker|hawkers|rehri|patri|thela|thelewal[a-z]*|svanidhi)\b", lower):
        inferred["occupation"] = "Street vendor"
    elif re.search(r"\b(artisan|artisans|craftsman|craftsmen|craftsperson|vishwakarma|weaver|weavers|bunkar|carpenter|potter|blacksmith|goldsmith|cobbler|tailor)\b", lower):
        inferred["occupation"] = "Artisan / craft worker"
    elif re.search(r"\b(business|entrepreneur|entrepreneurs|startup|startups|shopkeeper|trader|traders|enterprise|msme|self[\s-]employed)\b", lower):
        inferred["occupation"] = "Business owner / self-employed"

    # 4. Course (Education)
    if re.search(r"\b(btech|b\.tech|engineering|b\.e\b|be\b|polytechnic|mtech|m\.tech)\b", lower):
        inferred["course"] = "Engineering / B.Tech"
    elif re.search(r"\b(mbbs|medical|neet|bds|nursing|b\.pharm|mpharm)\b", lower):
        inferred["course"] = "Other professional course"
    elif re.search(r"\b(ba|bsc|bcom|b\.a\b|b\.sc\b|b\.com\b|graduation|undergraduate)\b", lower):
        inferred["course"] = "General degree"

    # 5. Social Category
    if re.search(r"\b(sc|scheduled\s*caste|dalit)\b", lower):
        inferred["social_category"] = "SC"
    elif re.search(r"\b(st|scheduled\s*tribe|adivasi|tribal)\b", lower):
        inferred["social_category"] = "ST"
    elif re.search(r"\b(obc|other\s*backward\s*class)\b", lower):
        inferred["social_category"] = "OBC"
    elif re.search(r"\b(minority|minorities|muslim|christian|sikh|jain|buddhist|parsi)\b", lower):
        inferred["social_category"] = "Minority"

    # 6. Landholding
    if re.search(r"\b(landless|no\s*land)\b", lower):
        inferred["landholding"] = "Landless"
    elif re.search(r"\b(tenant|leased\s*land)\b", lower):
        inferred["landholding"] = "Tenant / leased land"
    elif re.search(r"\b(landowner|own\s*land|marginal\s*farmer|small\s*farmer|\d+\s*acres?|\d+\s*hectares?)\b", lower):
        inferred["landholding"] = "Landowner"

    # 7. Income
    if re.search(r"\b(bpl|below\s*poverty\s*line|poor\s*family|economically\s*weaker|ews)\b", lower):
        inferred["income"] = "Under ₹2.5 lakh"
    elif re.search(r"\b(?:under|below|less\s*than|<)?\s*(?:₹|rs\.?|inr)?\s*(?:2\.5|2|1|1\.5)\s*lakh\b", lower):
        inferred["income"] = "Under ₹2.5 lakh"

    return inferred


STOP_WORDS = {
    "i", "want", "to", "know", "benefits", "benefit", "for", "the", "a", "an", "in",
    "of", "and", "or", "is", "are", "what", "how", "can", "get", "scheme", "schemes",
    "yojana", "portal", "portals", "help", "me", "tell", "about", "any", "which", "my",
    "need", "details", "check", "official", "government", "govt", "gov", "apply",
    "application", "information", "info", "list", "do", "does", "have", "with",
}


def score_portal_for_query(
    portal: Dict[str, Any],
    query: str,
    topic: str,
    semantic_intent: Optional[Dict[str, Any]] = None
) -> float:
    """Computes an open-domain relevance score for a portal, combining LLM search signals with keyword gates."""
    lower_query = query.casefold()
    raw_tokens = [t for t in re.findall(r"[a-z0-9]+", lower_query) if len(t) > 1]
    query_tokens = set(raw_tokens) - STOP_WORDS

    name = str(portal.get("name", "")).casefold()
    desc = str(portal.get("description", "")).casefold()
    cat = str(portal.get("category", "")).casefold()
    ministry = str(portal.get("ministry", "")).casefold()
    keywords = [str(k).casefold() for k in portal.get("keywords", [])]
    kw_text = " ".join(keywords)
    portal_text = f"{name} {desc} {cat} {ministry} {kw_text}"
    portal_tokens = set(re.findall(r"[a-z0-9]+", portal_text))

    score = 0.0

    # -------------------------------------------------------------------------
    # 1. Tier 1: Open-Domain Semantic Intent Signals (from LLM if available)
    # -------------------------------------------------------------------------
    if semantic_intent:
        search_signals = [str(s).casefold() for s in semantic_intent.get("search_signals", []) if str(s).strip()]
        for signal in search_signals:
            if signal in portal_text:
                score += 20.0
            sig_tokens = set(signal.split())
            if sig_tokens and sig_tokens.issubset(portal_tokens):
                score += 15.0

        disqualifying = [str(d).casefold() for d in semantic_intent.get("disqualifying_domains", []) if str(d).strip()]
        for disq in disqualifying:
            if disq in portal_text and not any(sig in portal_text for sig in search_signals):
                score -= 40.0

        beneficiary_cat = semantic_intent.get("beneficiary", {}).get("category", "")
        if beneficiary_cat == "senior_citizen":
            if any(k in portal_text for k in ["senior citizen", "pension", "70 years", "ayushman", "nsap"]):
                score += 20.0
            if any(k in portal_text for k in ["student scholarship", "education loan", "vidyalakshmi", "pragati"]):
                score -= 50.0
        elif beneficiary_cat in {"student", "education"}:
            if any(k in portal_text for k in ["scholarship", "education loan", "student", "tuition"]):
                score += 20.0
        elif beneficiary_cat == "farmer":
            if any(k in portal_text for k in ["farmer", "kisan", "crop", "agriculture", "fasal"]):
                score += 20.0
        elif beneficiary_cat in {"msme_vendor", "business"}:
            if any(k in portal_text for k in ["msme", "startup", "vendor", "mudra", "stand up india", "artisan"]):
                score += 20.0

    # -------------------------------------------------------------------------
    # 2. Tier 2: Relational & Direct Syntactic Hard-Gates
    # -------------------------------------------------------------------------
    is_for_parents = bool(
        re.search(r"\b(old\s*parents|elderly\s*parents|for\s+(?:my\s+)?(?:old|elderly|aging|retired)?\s*(?:parents|father|mother|grandmother|grandfather|senior))\b", lower_query)
    )
    if is_for_parents:
        if any(k in portal_text for k in ["vidyalakshmi", "education loan", "student scholarship", "aicte", "pragati", "btech"]):
            return 0.0
        if any(k in portal_text for k in ["senior citizen", "70 years", "old age pension", "ayushman", "nsap", "pmjay", "myscheme"]):
            score += 25.0

    if query_tokens & {"girl", "child", "children", "daughter", "female", "women", "kanya", "beti", "balika", "mahila"}:
        if not any(k in portal_text for k in ["girl", "child", "daughter", "women", "woman", "mahila", "kanya", "beti", "balika", "female", "scholarship", "myscheme"]):
            return 0.0

    if query_tokens & {"farmer", "kisan", "crop", "agriculture", "tractor", "cultivation"}:
        if not any(k in portal_text for k in ["farmer", "kisan", "crop", "agriculture", "cultivator", "land", "seed", "rural", "irrigation", "soil", "fasal", "myscheme"]):
            return 0.0

    if query_tokens & {"vendor", "street vendor", "hawker", "svanidhi"}:
        if not any(k in portal_text for k in ["vendor", "hawker", "svanidhi", "street", "micro", "mudra", "myscheme"]):
            return 0.0

    # 3. Direct N-Gram and Token Overlaps
    for i in range(len(raw_tokens) - 1):
        bigram = f"{raw_tokens[i]} {raw_tokens[i+1]}"
        if bigram not in {"want to", "to know", "i want", "benefits for", "what is", "how can"}:
            if bigram in portal_text:
                score += 15.0

    ambiguous_modifiers = {"single", "small", "first", "direct", "online", "new", "main"}
    for token in query_tokens:
        if token in ambiguous_modifiers:
            continue
        if any(token in kw for kw in keywords):
            score += 8.0
        elif token in name:
            score += 6.0
        elif token in desc or token in cat:
            score += 3.0

    topic_kw = TOPIC_PORTAL_TERMS.get(topic, set())
    overlap = len(portal_tokens & topic_kw)
    score += min(overlap, 4) * 1.5

    # Apex National Platform baseline
    if "myscheme" in portal.get("domain", ""):
        score += 5.0

    return score


def _portal_text(portal: Dict[str, Any]) -> str:
    return " ".join(
        str(portal.get(key, ""))
        for key in ("name", "category", "ministry", "description")
    ) + " " + " ".join(str(word) for word in portal.get("keywords", []))


def _topic_score(portal: Dict[str, Any], topic: str) -> int:
    terms = set(re.findall(r"[a-z0-9]+", _portal_text(portal).casefold()))
    return len(terms & TOPIC_PORTAL_TERMS[topic])


def _catalog_portals() -> List[Dict[str, Any]]:
    by_domain: Dict[str, Dict[str, Any]] = {}
    for item in SEED_GOVERNMENT_PORTALS:
        by_domain[item["domain"].casefold()] = dict(item)
    return list(by_domain.values())


def select_official_portals(
    query: str,
    state: str,
    semantic_intent: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Select matching central and explicitly catalogued portals grounded in query and semantic intent."""
    topic = classify_query(query)
    portals = _catalog_portals()
    registered = []
    for portal in portals:
        allowed, _, _ = is_whitelisted_domain(portal["url"])
        if allowed:
            registered.append(portal)

    central_candidates = [
        (portal, score_portal_for_query(portal, query, topic, semantic_intent))
        for portal in registered
        if portal.get("level") == "Central"
    ]
    central = [
        portal for portal, score in central_candidates
        if score >= 5.0
    ]
    central.sort(
        key=lambda p: (-score_portal_for_query(p, query, topic, semantic_intent), p["name"].casefold())
    )

    state_portals = []
    if state and state not in {"All India", "All India / Centre", "Central", "Centre"}:
        state_candidates = [
            (portal, score_portal_for_query(portal, query, topic, semantic_intent))
            for portal in registered
            if portal.get("state") == state and portal.get("level") in {"State", "UT"}
        ]
        state_portals = [
            portal for portal, score in state_candidates
            if score >= 5.0
        ]
        state_portals.sort(
            key=lambda p: (-score_portal_for_query(p, query, topic, semantic_intent), p["name"].casefold())
        )

    return {
        "topic": topic,
        "central": central[:4],
        "state": state_portals[:4],
    }


def profile_questions(
    topic: str,
    profile: Dict[str, Any],
    known_state: Optional[str],
    query: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Build deterministic profile questions, skipping attributes already known or inferred from query."""
    if not known_state:
        return [{
            "id": "state",
            "label": "State / UT",
            "question": "Which state or union territory do you live in?",
            "options": get_state_region_options(),
        }]

    inferred = infer_profile_from_text(query or "")
    merged_profile = {**inferred, **profile}

    normalized_keys = [
        re.sub(r"[^a-z0-9]+", " ", str(key).casefold()).strip()
        for key, value in merged_profile.items()
        if value is not None and str(value).strip()
    ]
    aliases = {
        "age": ("age", "years old", "birth"),
        "income": ("income", "earnings"),
        "course": ("course", "degree", "program", "study"),
        "loan_amount": ("loan amount", "loan quantum", "loan size", "desired loan"),
        "social_category": ("social category", "caste", "category", "minority"),
        "gender": ("gender", "sex", "woman", "female", "male"),
        "occupation": ("occupation", "profession", "employment", "farmer", "business type"),
        "landholding": ("landholding", "land ownership", "landowner"),
    }

    def field_is_known(field: str) -> bool:
        return any(
            alias in key
            for key in normalized_keys
            for alias in aliases[field]
        )

    questions: List[Dict[str, Any]] = []
    templates = PROFILE_QUESTION_TEMPLATES.get(topic, PROFILE_QUESTION_TEMPLATES["general"])
    for field, label, question, options in templates:
        if field_is_known(field):
            continue
        questions.append({
            "id": field,
            "label": label,
            "question": question,
            "options": options,
        })
    return questions


def group_portal_results(portals: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Present selected official portals with explicit nationwide/state scope."""
    results: List[Dict[str, Any]] = []
    groups = [("Central / nationwide", portals.get("central", []))]
    if portals.get("state"):
        groups.append((portals.get("state_name", "State / UT"), portals.get("state", [])))

    for jurisdiction, entries in groups:
        for portal in entries:
            results.append({
                "jurisdiction": jurisdiction,
                "name": portal["name"],
                "domain": portal["domain"],
                "url": portal["url"],
                "category": portal.get("category", ""),
                "level": portal.get("level", ""),
            })
    return results
