"""
Guardrail & Scope Protection Engine for myScheme AI Assistant.
Provides enterprise-grade input validation:
  1. Character & Payload Flooding Defense (repetition, buffer flooding, keyboard smash, zero-width injection).
  2. URL & Link Pasting Guardrail (blocks untrusted third-party/commercial/phishing links; allows genuine *.gov.in / *.nic.in).
  3. Prompt Injection & Jailbreak Defense (resists override attacks, system leaks, and malicious command patterns).
  4. Out-of-Domain Scope Control (gracefully deflects non-welfare queries like coding, homework, sports, cinema).
  5. Official In-Domain Greetings & Context Preservation (warm guidance, maintains multi-turn profile context).
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Multi-word scheme terms
MULTI_WORD_SCHEME_TERMS = [
    "surya ghar", "matru vandana", "ration card", "jan dhan", "atal pension",
    "stand up india", "startup india", "seed fund", "interest subsidy",
    "fee reimbursement", "fee waiver", "digital india", "praman patra",
    "income certificate", "caste certificate", "dbt bharat", "senior citizen",
    "old age", "girl child", "daily wage", "poor family", "crop insurance",
    "solar pump", "solar rooftop", "street vendor", "disability pension",
    "widow pension", "old age pension", "differently abled", "below poverty line",
    "education loan", "higher education", "skill development", "kisan credit",
    "self help group", "women entrepreneur", "free electricity", "pucca house"
]

# Single-word scheme and welfare terms matched as whole words (tokens)
SINGLE_WORD_SCHEME_TERMS = {
    # Core welfare terminology
    "scheme", "schemes", "yojana", "yojna", "yojanayein", "subsidy", "subsidies",
    "pension", "pensions", "scholarship", "scholarships", "fellowship", "fellowships",
    "stipend", "stipends", "loan", "loans", "mudra", "pmegp", "bima", "insurance",
    "ayushman", "pmjay", "pmkisan", "pm-kisan", "kisan", "krishi", "crop", "fasal",
    "fertilizer", "fertilizers", "kusum", "awas", "pmay", "sukanya", "samriddhi",
    "ladli", "kanya", "poshan", "ration", "bpl", "aay", "antyodaya", "dbt", "welfare",
    "allowance", "allowances", "grant", "grants", "aid", "relief", "assistance",
    "support", "concession", "waiver", "reimbursement", "incentive", "incentives",
    "vishwakarma", "svanidhi", "government", "govt", "sarkari", "beneficiary",
    "beneficiaries", "eligibility", "eligible", "patrata", "patra", "aadhaar",
    "shramik", "mgnrega", "nrega", "pmjdy", "apy",
    
    # Target beneficiaries & demographics
    "farmer", "farmers", "cultivator", "cultivators", "student", "students",
    "graduate", "graduates", "unemployed", "jobseeker", "jobseekers", "widow",
    "widows", "divyang", "divyangjan", "pwd", "artisan", "artisans", "weaver",
    "weavers", "vendor", "vendors", "worker", "workers", "labourer", "laborer",
    "labourers", "laborers", "sc", "st", "obc", "minority", "minorities", "ews",
    "tribal", "tribals", "senior", "seniors", "youth", "women", "woman",
    "female", "girl", "girls", "children", "child", "infant", "mother", "mothers",
    "handicapped", "disabled", "orphan", "destitute",

    # Key sectors & resources
    "agriculture", "farming", "handicraft", "handloom", "textile", "cattle",
    "dairy", "fisheries", "poultry", "tractor", "irrigation", "seed", "seeds",
    "education", "school", "college", "university", "degree", "diploma", "hostel",
    "hospital", "medical", "treatment", "health", "healthcare", "medicine",
    "electricity", "solar", "rooftop", "housing", "house", "home", "shelter",
    "business", "startup", "msme", "microenterprise", "shopkeeper",

    # Indian States & Union Territories
    "andhra", "arunachal", "assam", "bihar", "chhattisgarh", "goa", "gujarat",
    "haryana", "himachal", "jharkhand", "karnataka", "kerala", "madhya",
    "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha",
    "punjab", "rajasthan", "sikkim", "tamil", "telangana", "tripura",
    "uttar", "uttarakhand", "bengal", "delhi", "jammu", "kashmir", "ladakh",
    "chandigarh", "puducherry", "pondicherry", "andaman", "nicobar", "lakshadweep"
}

# Regex patterns for negative out-of-domain queries
OUT_OF_DOMAIN_PATTERNS = [
    # Programming, coding, technical development
    r"\b(?:python|javascript|typescript|java|c\+\+|golang|rust|html|css|sql|react|vue|angular|django|flask|fastapi|node|npm|git|github|docker|kubernetes|pointer|recursion|algorithm|binary\s*search|leetcode|debug|compile|regex|write\s*(?:a\s*)?code|coding|programming|script|syntax\s*error)\b",
    
    # Mathematics, physics, school homework exercises
    r"\b(?:solve\s*(?:this|equation|problem|integral|derivative)|calculus|algebra|quadratic|trigonometry|pythagoras|physics\s*problem|chemistry\s*formula|molecular\s*weight|homework\s*help)\b",
    
    # Sports, games, entertainment, cinema
    r"\b(?:cricket|ipl|fifa|world\s*cup|football|messi|ronaldo|virat\s*kohli|rohit\s*sharma|dhoni|ipl\s*score|live\s*score|movie|cinema|actor|actress|bollywood|hollywood|netflix|box\s*office|trailer|song\s*lyrics|singer|spotify|album|minecraft|playstation|xbox)\b",
    
    # Cooking, food recipes, kitchen tips
    r"\b(?:recipe|how\s*to\s*(?:cook|bake|make\s*(?:pizza|cake|biryani|pasta|burger|tea|coffee|curry|paneer|roti|bread|soup|cookie)))\b",
    
    # E-commerce, commercial consumer electronics, private shopping
    r"\b(?:buy\s*(?:shoes|iphone|samsung|laptop|phone|tv|car|bike|watch|clothes)\s*online|amazon|flipkart|best\s*(?:smartphone|camera|headphones|laptop)\s*under|discount\s*coupon|promo\s*code|crypto|bitcoin|ethereum|share\s*market|stock\s*price)\b",
    
    # Personal chit-chat, jokes, riddles, flirts, weather
    r"\b(?:tell\s*(?:me\s*)?(?:a\s*)?joke|tell\s*(?:me\s*)?(?:a\s*)?story|poem|write\s*(?:a\s*)?poem|riddle|are\s*you\s*(?:human|real|alive|robot)|do\s*you\s*love\s*me|marry\s*me|who\s*made\s*you|flirt|weather\s*(?:in|today|tomorrow|forecast))\b",
    
    # World trivia, non-government history/geography
    r"\b(?:capital\s*of\s*(?!india\b)[a-z]+|who\s*was\s*(?:napoleon|einstein|shakespeare|alexander|hitler|columbus)|who\s*invented|speed\s*of\s*light|how\s*far\s*is\s*(?:the\s*)?(?:moon|sun|mars)|distance\s*to|explain\s*photosynthesis)\b"
]

# Prompt injection & jailbreak patterns
PROMPT_INJECTION_PATTERNS = [
    r"\b(?:ignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions|directions|rules|prompts))\b",
    r"\b(?:disregard\s+all\s+(?:rules|guidelines|constraints))\b",
    r"\b(?:you\s+are\s+now\s+(?:in\s+)?(?:dan|developer\s+mode|an?\s+unrestricted|unhinged|god\s+mode|jailbroken))\b",
    r"\b(?:jailbreak(?:\s+mode)?|bypass\s+(?:all\s+)?guardrails)\b",
    r"\b(?:system\s+prompt|reveal\s+(?:your\s+)?prompt|print\s+(?:the\s+)?system\s+prompt)\b",
    r"\b(?:pretend\s+you\s+have\s+no\s+(?:rules|restrictions|ethics))\b",
    r"<\s*script\b|javascript:|eval\s*\(|union\s+select\b",
]

GREETING_PATTERN = r"(?:^(?:hi|hello|hey|namaste|namaskar|pranam|good\s*(?:morning|afternoon|evening)|howdy|greetings|who\s*are\s*you|what\s*can\s*you\s*do|help|kya\s*kar\s*sakte\s*ho)[!?.\s]*$|\b(?:namaste|namaskar|hello|hi|good\s*morning|what\s*can\s*you\s*do)\b)"

# Broad URL and domain detection regex
URL_PATTERN = re.compile(
    r"(?:https?://|ftp://)[\w\d:#@%/;$()~_?\+-=\\\.&]+|"
    r"\bwww\.[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z0-9-.]+(?:/[\w\d:#@%/;$()~_?\+-=\\\.&]*)?|"
    r"\b[a-zA-Z0-9][-a-zA-Z0-9]*\.(?:com|org|net|xyz|info|biz|top|site|online|club|app|co|io|me|ru|cn|cc|store|live|vip|pro)(?:/[\w\d:#@%/;$()~_?\+-=\\\.&]*)?|"
    r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/[^\s]*)?|"
    r"\blocalhost(?::\d+)?(?:/[^\s]*)?",
    re.IGNORECASE
)


def is_greeting(query: str) -> bool:
    """Returns True if the user input is a pure greeting or capability inquiry."""
    trimmed = query.strip().casefold()
    if has_scheme_terms(trimmed):
        return False
    return bool(re.search(GREETING_PATTERN, trimmed)) and len(trimmed.split()) <= 8


def has_scheme_terms(text: str) -> bool:
    """Checks if text contains authentic whole-word scheme/welfare terms."""
    lowered = text.casefold()
    if any(mwt in lowered for mwt in MULTI_WORD_SCHEME_TERMS):
        return True
    tokens = set(re.findall(r"\b[a-z0-9]+(?:-[a-z0-9]+)*\b", lowered))
    return bool(tokens & SINGLE_WORD_SCHEME_TERMS)


def detect_flooding_or_spam(query: str) -> Tuple[bool, Optional[str]]:
    """
    Detects repeated characters, sequence repetition, keyboard smash,
    excessive length, and hidden/control character flooding.
    """
    if not query or not query.strip():
        return True, "Input is empty or contains only whitespace."

    # 1. Payload Length Check (Buffer / payload flooding)
    if len(query) > 800:
        return True, "Query exceeds the maximum allowed length of 800 characters."

    # 2. Repeated non-numeric characters (>= 5 in a row). Digit runs can be valid
    # profile data, such as an annual income of 200000.
    consec_match = re.search(r"([^\d])\1{4,}", query)
    if consec_match:
        matched_sample = consec_match.group(0)[:8]
        return True, f"Repetitive character flooding detected: '{matched_sample}'."

    # 3. Repeated phrase or sequence pattern flooding (e.g. asdfasdfasdfasdf, hahahahahaha)
    seq_match = re.search(r"(.{2,10})\1{3,}", query, re.IGNORECASE)
    if seq_match:
        return True, "Repeated sequence/phrase flooding detected."

    # 4. Monotony Check: Single character dominates > 40% of input in strings > 20 chars
    non_space_chars = [c for c in query if not c.isspace()]
    if len(non_space_chars) >= 20:
        from collections import Counter
        counts = Counter(non_space_chars)
        most_common_char, count = counts.most_common(1)[0]
        if count / len(non_space_chars) > 0.40:
            return True, f"High character monotony: character '{most_common_char}' repeated excessively."

    # 5. Keyboard Smashing / High Consonant Cluster (> 8 consonants with zero vowels)
    consonant_smash = re.search(r"\b[bcdfghjklmnpqrstvwxyz]{9,}\b", query.casefold())
    if consonant_smash:
        return True, f"Unintelligible keyboard smashing detected: '{consonant_smash.group(0)}'."

    # 6. Invisible / Zero-Width / Unauthorized Control Characters
    control_chars = re.findall(r"[\u200B-\u200D\uFEFF\u200E\u200F\u202A-\u202E\x00-\x08\x0B\x0C\x0E-\x1F]", query)
    if len(control_chars) >= 3:
        return True, "Unauthorized hidden or control characters detected."

    # 7. Empty or Pure Punctuation/Symbols Spam
    non_symbol_chars = re.sub(r"[\s\W_]+", "", query)
    if len(non_symbol_chars) == 0:
        return True, "Input contains only punctuation, whitespace, or symbols."

    return False, None


def detect_untrusted_urls(query: str) -> Tuple[bool, List[str], List[str]]:
    """
    Extracts all web URLs or hostnames from user input and verifies them against
    authentic Indian Government domains (*.gov.in / *.nic.in / myscheme.gov.in).
    Returns (has_untrusted, untrusted_list, trusted_list).
    """
    matches = URL_PATTERN.findall(query)
    if not matches:
        return False, [], []

    untrusted_urls = []
    trusted_gov_urls = []

    for item in matches:
        raw_url = item.strip()
        # Ensure scheme for urlparse
        candidate = raw_url if re.match(r"^https?://", raw_url, re.IGNORECASE) else f"https://{raw_url}"
        try:
            parsed = urlparse(candidate)
            hostname = (parsed.hostname or "").casefold().rstrip(".")
            if not hostname:
                continue

            # Check if host is valid Indian Government portal
            is_gov = (
                hostname == "myscheme.gov.in"
                or hostname.endswith(".myscheme.gov.in")
                or hostname.endswith(".gov.in")
                or hostname.endswith(".nic.in")
            )
            if is_gov:
                trusted_gov_urls.append(raw_url)
            else:
                untrusted_urls.append(raw_url)
        except Exception:
            untrusted_urls.append(raw_url)

    return bool(untrusted_urls), untrusted_urls, trusted_gov_urls


def detect_prompt_injection(query: str) -> Tuple[bool, Optional[str]]:
    """Detects adversarial jailbreaks, prompt injection, and command tampering attempts."""
    lowered = query.casefold()
    for pat in PROMPT_INJECTION_PATTERNS:
        if re.search(pat, lowered):
            return True, "Potential prompt injection or instruction override pattern detected."
    return False, None


def check_domain_guard(
    query: str,
    user_clarification: Optional[str] = None,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    user_profile: Optional[Dict[str, Any]] = None
) -> Tuple[str, Optional[str]]:
    """
    Evaluates incoming query across 5 security and domain guard levels:
      1. FLOODING_SPAM: Character repetition, sequence flooding, gibberish smash, excessive length.
      2. SECURITY_BLOCKED: Untrusted third-party, commercial, or non-gov URL pastings.
      3. PROMPT_INJECTION: Jailbreak or instruction override patterns.
      4. GREETING: Pure greetings or system capability inquiries.
      5. OUT_OF_DOMAIN: Questions outside Indian Government welfare schemes.
      6. IN_DOMAIN: Valid government welfare queries or multi-turn profile clarifications.
    
    Returns (guard_status, guard_message_or_refusal).
    """
    cleaned = (query or "").strip()

    # Empty check
    if not cleaned:
        if user_clarification:
            return "IN_DOMAIN", None
        return "FLOODING_SPAM", generate_flooding_refusal("Empty input provided. Please enter a valid question regarding government schemes.")

    # 1. Check for Flooding and Spam (Applies to all queries and clarifications)
    is_spam, spam_reason = detect_flooding_or_spam(cleaned)
    if is_spam:
        return "FLOODING_SPAM", generate_flooding_refusal(spam_reason or "Input formatting violation")

    # 2. Check for pure greeting or platform capability questions
    if is_greeting(cleaned):
        return "GREETING", None

    # 3. Check for Untrusted URL Pastings
    has_untrusted, untrusted_list, _ = detect_untrusted_urls(cleaned)
    if has_untrusted:
        return "SECURITY_BLOCKED", generate_untrusted_url_refusal(untrusted_list)

    # 4. Check for Prompt Injection & Jailbreak Attacks
    is_injection, _ = detect_prompt_injection(cleaned)
    if is_injection:
        return "PROMPT_INJECTION", generate_injection_refusal()

    # 5. Multi-Turn / Clarification Context
    # If the user is answering a questionnaire prompt or providing profile details
    if user_clarification:
        return "IN_DOMAIN", None

    if conversation_history and len(conversation_history) > 0:
        has_prior_scheme_context = any(
            any(k in str(m.get("content", "")).casefold() for k in ["scheme", "yojana", "eligib", "benefit", "state", "income", "loan"])
            for m in conversation_history
        )
        if has_prior_scheme_context:
            short_answers = {
                "yes", "no", "general", "obc", "sc", "st", "ews", "male", "female", "transgender",
                "student", "farmer", "single", "married", "urban", "rural", "landless",
                "artisan", "weaver", "vendor", "businessman", "salaried", "unemployed",
                "uttar pradesh", "delhi", "maharashtra", "bihar", "rajasthan", "punjab", "haryana"
            }
            if cleaned.casefold() in short_answers or len(cleaned.split()) <= 4:
                return "IN_DOMAIN", None

    lower_query = cleaned.casefold()

    # 6. Check for explicit out-of-domain patterns (coding, sports, cinema, homework, etc.)
    matched_ood = False
    for pat in OUT_OF_DOMAIN_PATTERNS:
        if re.search(pat, lower_query):
            matched_ood = True
            break

    # 7. Check for explicit scheme terms
    has_scheme = has_scheme_terms(lower_query)

    # 8. Check for explicit eligibility / application patterns
    has_eligibility = bool(re.search(
        r"\b(?:eligible|eligibility|apply|application|subsidy|subsidies|scholarship|scholarships|pension|pensions|yojana|scheme|schemes|welfare|benefit|benefits|patrata)\b",
        lower_query
    ))

    # Decision Matrix:
    # If explicit out-of-domain pattern matches (coding, recipes, sports, etc.):
    # Only allow if there is an explicit government scheme identifier (e.g. "is there a scheme for sports players")
    if matched_ood:
        strong_override = bool(re.search(
            r"\b(?:scheme|yojana|subsidy|scholarship|pension|pm-kisan|ayushman|myscheme|government|sarkari)\b",
            lower_query
        ))
        if not strong_override:
            return "OUT_OF_DOMAIN", generate_ood_refusal(cleaned)

    # If it contains scheme terms or eligibility phrasing
    if has_scheme or has_eligibility:
        return "IN_DOMAIN", None

    # If query has 3 or more words and ZERO scheme/welfare/citizen aid indicators
    words = cleaned.split()
    if len(words) >= 3:
        return "OUT_OF_DOMAIN", generate_ood_refusal(cleaned)

    # Short ambiguous inputs default to in-domain to allow multi-turn clarification
    return "IN_DOMAIN", None


# =========================================================================
# REFUSAL & GUIDANCE GENERATORS
# =========================================================================

def generate_flooding_refusal(reason: str) -> str:
    """Returns official notice when input is blocked due to flooding, repetition, or spam."""
    return (
        "⚠️ **Input Security Guardrail (Flooding / Spam Blocked)**\n\n"
        f"Your message was stopped by the system input filter because: **{reason}**\n\n"
        "To ensure fair access and prevent automated denial of service, "
        "**GovScheme AI** accepts clean, structured inquiries in English or Hindi.\n\n"
        "### How to Ask a Valid Question:\n"
        "- 🌾 *\"What subsidies are available for small farmers in Haryana?\"*\n"
        "- 🎓 *\"I need an education loan for B.Tech with low family income.\"*\n"
        "- 💼 *\"Tell me about collateral-free business loans under Mudra Yojana.\"*\n\n"
        "Please re-type your inquiry using standard text."
    )


def generate_untrusted_url_refusal(blocked_urls: List[str]) -> str:
    """Returns strict security warning when external/commercial/untrusted URLs are submitted."""
    url_preview = ", ".join(f"`{u}`" for u in blocked_urls[:3])
    return (
        "🛡️ **Security Guardrail Notice (Untrusted Link Blocked)**\n\n"
        f"The following external or unverified link(s) were detected and blocked: {url_preview}\n\n"
        "### Why Was This Blocked?\n"
        "For citizen safety, **anti-phishing protection**, and government compliance:\n"
        "- The GovScheme crawler operates on a **Strict Government Whitelist**.\n"
        "- Only authentic Indian Government domains ending with **`*.gov.in`** or **`*.nic.in`** "
        "(such as **`myscheme.gov.in`**) are authorized.\n"
        "- Visiting, crawling, or processing third-party commercial, blogging, or unverified portals is strictly disabled.\n\n"
        "### How to Proceed:\n"
        "You do not need to paste external links. Simply ask by scheme name or topic:\n"
        "- *\"How do I apply for PM Surya Ghar Muft Bijli Yojana?\"*\n"
        "- *\"What are the required documents for PM-KISAN?\"*\n"
        "- *\"Show me authentic scholarship schemes on National Scholarship Portal.\"*"
    )


def generate_injection_refusal() -> str:
    """Returns integrity notice when prompt injection or jailbreak attempts are detected."""
    return (
        "🛡️ **System Integrity Notice (Instruction Override Blocked)**\n\n"
        "Your input triggered an automated safety guardrail for prompt injection or system override attempts.\n\n"
        "**GovScheme AI** is dedicated exclusively to delivering evidence-grounded information on "
        "**Indian Central and State Government welfare schemes** from official gazettes and portals.\n\n"
        "System operating instructions and safety constraints cannot be bypassed. "
        "Please enter a legitimate inquiry regarding government welfare schemes, subsidies, or citizen eligibility."
    )


def generate_greeting_response(is_hindi: bool = False) -> str:
    """Returns official warm greeting and capability overview."""
    if is_hindi:
        return (
            "🙏 नमस्ते! मैं आपका **myScheme आधिकारिक AI सहायक** हूँ।\n\n"
            "मैं भारत सरकार (केंद्रीय) एवं सभी राज्य सरकारों की कल्याणकारी योजनाओं, "
            "छात्रवृत्तियों, ऋणों, सब्सिडी और स्वास्थ्य योजनाओं की आधिकारिक जानकारी तथा "
            "आपकी पात्रता की जांच करने में सहायता करता हूँ।\n\n"
            "**आप इन प्रमुख श्रेणियों के बारे में पूछ सकते हैं:**\n"
            "- 🌾 **कृषि:** पीएम-किसान, फसल बीमा, सोलर पंप सब्सिडी (पीएम-कुसुम)\n"
            "- 🎓 **शिक्षा:** इंजीनियरिंग एवं उच्च शिक्षा छात्रवृत्ति, विद्यालक्ष्मी शिक्षा ऋण\n"
            "- 🏥 **स्वास्थ्य:** आयुष्मान भारत (पीएम-जय) ₹5 लाख तक का कैशलेस इलाज\n"
            "- 💼 **स्वरोजगार एवं व्यापार:** मुद्रा लोन, पीएमईजीपी, पीएम स्वनिधि\n"
            "- ⚡ **ऊर्जा:** पीएम सूर्य घर मुफ्त बिजली योजना (सोलर रूफटॉप सब्सिडी)\n"
            "- 🏠 **आवास:** पीएम आवास योजना (शहरी एवं ग्रामीण)\n"
            "- 👵 **सामाजिक सुरक्षा:** वृद्धावस्था, विधवा एवं दिव्यांग पेंशन\n\n"
            "आप सीधे अपना प्रश्न पूछ सकते हैं, उदाहरण के लिए:\n"
            "*\"उत्तर प्रदेश में छोटे किसानों के लिए कौन-सी योजनाएं हैं?\"* या\n"
            "*\"बीटेक छात्रों के लिए सरकारी स्कॉलरशिप और लोन बताएं।\"*"
        )
    return (
        "🙏 **Namaste! I am your official myScheme AI Assistant.**\n\n"
        "I can help you discover authentic Central and State Government welfare schemes, "
        "verify your eligibility against official guidelines, and provide step-by-step application walkthroughs.\n\n"
        "### Key Areas I Can Assist You With:\n"
        "- 🌾 **Agriculture & Farming:** PM-KISAN, crop insurance (PMFBY), solar pump subsidies (PM-KUSUM)\n"
        "- 🎓 **Education & Students:** Scholarships for SC/ST/OBC/General, fee waivers, Vidyalakshmi education loans\n"
        "- 🏥 **Healthcare & Medical:** Ayushman Bharat (PM-JAY) ₹5 Lakh cover, Divyangjan disability aid\n"
        "- 💼 **Business & Self-Employment:** Mudra loans (Shishu/Kishore/Tarun), PMEGP, Stand-Up India, PM SVANidhi\n"
        "- ⚡ **Renewable Energy:** PM Surya Ghar Muft Bijli Yojana (rooftop solar subsidy up to ₹78,000)\n"
        "- 🏠 **Housing:** Pradhan Mantri Awas Yojana (PMAY Urban/Gramin)\n"
        "- 👵 **Social Security:** Old age, widow, and disability pensions (NSAP)\n\n"
        "Please type your query or describe your profile (age, state, occupation, income) to find your eligible schemes!"
    )


def generate_ood_refusal(user_query: str, is_hindi: bool = False) -> str:
    """Returns official out-of-domain scope restriction notice."""
    escaped_query = user_query[:100].replace("*", "").replace("`", "")
    if is_hindi:
        return (
            f"⚠️ **कार्यक्षेत्र सीमा सूचना (Out of Domain Notice)**\n\n"
            f"क्षमा करें, आपका प्रश्न (*\"{escaped_query}\"*) सरकारी योजनाओं के कार्यक्षेत्र से बाहर है। "
            f"मैं केवल **भारत सरकार (केंद्रीय) एवं राज्य सरकारों की कल्याणकारी योजनाओं, छात्रवृत्तियों, "
            f"सब्सिडी, ऋण एवं नागरिक पात्रता** के संबंध में आधिकारिक सहायता प्रदान करने हेतु अधिकृत हूँ।\n\n"
            f"**कृपया सरकारी योजनाओं से संबंधित प्रश्न पूछें, उदाहरण के लिए:**\n"
            f"- 🌾 *\"पीएम-किसान सम्मान निधि के तहत ₹6,000 की किस्त पाने की पात्रता क्या है?\"*\n"
            f"- 🎓 *\"इंजीनियरिंग कॉलेज के छात्रों के लिए केंद्र सरकार की कौन-सी छात्रवृत्ति उपलब्ध है?\"*\n"
            f"- 🏥 *\"आयुष्मान भारत कार्ड कैसे बनवाएं और इसके तहत क्या लाभ मिलते हैं?\"*\n"
            f"- 💼 *\"नया छोटा व्यापार शुरू करने के लिए मुद्रा लोन कैसे प्राप्त करें?\"*\n"
            f"- ⚡ *\"पीएम सूर्य घर योजना में सोलर पैनल लगाने पर कितनी सब्सिडी मिलती है?\"*\n\n"
            f"आप ऊपर दिए गए **Check Eligibility (5-Step Wizard)** टैब पर क्लिक करके भी अपनी पात्रता जांच सकते हैं।"
        )
    return (
        f"⚠️ **Scope Boundary Notice (myScheme Portal Guard)**\n\n"
        f"Your question (*\"{escaped_query}\"*) appears to be **outside the scope of Indian Government welfare schemes**.\n\n"
        f"I am an evidence-grounded assistant designed exclusively to help citizens navigate **official Central and State Government schemes, eligibility criteria, subsidies, and public benefits** on the **myScheme** portal.\n\n"
        f"### How I Can Help You:\n"
        f"- 🌾 **Agriculture:** PM-KISAN, tractor & solar pump subsidies, crop insurance\n"
        f"- 🎓 **Education:** Central Sector scholarships, B.Tech/medical education loans, fee reimbursement\n"
        f"- 🏥 **Healthcare:** Ayushman Bharat (PM-JAY) ₹5 Lakh cashless hospitalisation\n"
        f"- 💼 **Business:** Collateral-free Mudra & PMEGP loans for startups and MSMEs\n"
        f"- ⚡ **Energy:** PM Surya Ghar Muft Bijli Yojana rooftop solar subsidy\n"
        f"- 👵 **Pensions & Social Welfare:** Old age, widow, and disability pension schemes\n\n"
        f"Please rephrase your query around government benefits or click the **Check Eligibility (5-Step Wizard)** tab to check your profile directly!"
    )
