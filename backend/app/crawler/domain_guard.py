"""
Guardrail & Scope Protection Engine for myScheme AI Assistant.
Provides enterprise-grade input validation:
  1. Character & Payload Flooding Defense (repetition, buffer flooding, keyboard smash, zero-width injection).
  2. URL & Link Pasting Guardrail (blocks untrusted third-party/commercial/phishing links; allows genuine *.gov.in / *.nic.in).
  3. Prompt Injection & Jailbreak Defense (resists override attacks, system leaks, and malicious command patterns).
  4. Out-of-Domain Scope Control (gracefully deflects non-welfare queries like coding, homework, sports, cinema).
  5. Geographic Scope Enforcement (blocks foreign/abroad/overseas/non-India queries even when scheme words appear).
  6. Official In-Domain Greetings & Context Preservation (warm guidance, maintains multi-turn profile context).
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Multi-word scheme terms (English)
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

# Multi-word scheme terms in Indic scripts
MULTI_WORD_INDIC_TERMS = [
    "एजुकेशन लोन", "शिक्षा ऋण", "छात्र ऋण", "हायर एजुकेशन", "पीएम किसान", "किसान सम्मान",
    "सूर्य घर", "मुद्रा लोन", "आयुष्मान भारत", "राशन कार्ड", "अटल पेंशन", "मातृ वंदना",
    "सुकन्या समृद्धि", "उज्ज्वला योजना", "पीएम आवास", "लखपति दीदी", "विद्या लक्ष्मी",
    "विद्या संबल", "विद्यानिधि", "लाडली बहना", "लाडली लक्ष्मी", "मुफ्त बिजली"
]

# Vernacular & Indic welfare terminology across major Indian scripts (Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, Gujarati, Punjabi)
INDIC_SCHEME_TERMS = {
    # Hindi / Devanagari core welfare words
    "योजना", "योजनाएं", "योजनाओं", "योजनाओ", "योजनां", "स्कीम", "स्कीम्स", "स्कीमे",
    "लोन", "ऋण", "कर्ज", "सब्सिडी", "अनुदान", "छात्रवृत्ति", "स्कॉलरशिप", "पेंशन",
    "बीमा", "राशन", "राशनकार्ड", "पात्रता", "पात्र", "आवेदन", "अप्लाई", "फॉर्म",
    "सरकारी", "सरकार", "लाभ", "लाभार्थी", "फायदा", "सहायता", "मदद", "छूट", "मुफ्त", "फ्री",
    
    # Demographics & beneficiaries (Hindi / Devanagari)
    "किसान", "विद्यार्थी", "छात्र", "छात्रा", "छात्रों", "महिला", "महिलाएं", "महिलाओ",
    "बेटी", "बालिका", "बच्चे", "गरीब", "बीपीएल", "श्रमिक", "मजदूर", "कामगार", "कारीगर",
    "दुकानदार", "व्यापारी", "दिव्यांग", "विकलांग", "वृद्ध", "बुजुर्ग", "विधवा", "युवा", "बेरोजगार",
    
    # Key sectors (Hindi / Devanagari)
    "शिक्षा", "एजुकेशन", "पढ़ाई", "शिक्षण", "स्कूल", "कॉलेज", "यूनिवर्सिटी", "डिग्री",
    "इंजीनियरिंग", "मेडिकल", "कृषि", "खेती", "फसल", "खाद", "उर्वरक", "बीज", "ट्रैक्टर",
    "पंप", "सोलर", "सौर", "बिजली", "स्वास्थ्य", "इलाज", "अस्पताल", "दवा", "आवास",
    "मकान", "घर", "मुद्रा", "पीएम", "आयुष्मान", "कुसुम", "उज्ज्वला", "स्वनिधि", "विश्वकर्मा", "सुकन्या",

    # Marathi specifics
    "शेतकरी", "शिष्यवृत्ती", "निवृत्तीवेतन", "विमा", "वीज", "आरोग्य", "औषध", "पीक", "बियाणे",

    # Bengali
    "যোজনা", "স্কিম", "ঋণ", "লোন", "ভাতা", "বৃত্তি", "স্কলারশিপ", "কৃষক", "ছাত্র", "শিক্ষা", "সাহায্য", "সরকারি",

    # Kannada
    "ಯೋಜನೆ", "ಸಾಲ", "ಸಬ್ಸಿಡಿ", "ವೇತನ", "ವಿದ್ಯಾರ್ಥಿವೇತನ", "ರೈತ", "ವಿದ್ಯಾರ್ಥಿ", "ಶಿಕ್ಷಣ", "ಅರ್ಜಿ", "ಸಹಾಯಧನ", "ಸರ್ಕಾರಿ",

    # Tamil
    "திட்டம்", "கடன்", "மானியம்", "உதவித்தொகை", "விவசாயி", "மாணவர்", "கல்வி", "அரசு",

    # Telugu
    "పథకం", "రుణం", "సబ్సిడీ", "రైతు", "విద్యార్థి", "చదువు", "పెన్షన్", "ప్రభుత్వ",

    # Gujarati
    "યોજના", "લોન", "સબસિડી", "શિષ્યવૃત્તિ", "ખેડૂત", "વિદ્યાર્થી", "શિક્ષણ", "સહાય", "સરકારી"
}

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

# ─────────────────────────────────────────────────────────────────────────────
# GEOGRAPHIC SCOPE: India-only. These patterns fire even when scheme/welfare
# words are present (e.g. "foreign education scheme", "UK scholarship").
# Evaluated with PRIORITY before the has_scheme_terms override.
# ─────────────────────────────────────────────────────────────────────────────
GEOGRAPHIC_OOD_PATTERNS = [
    # Explicit abroad / overseas / foreign keywords
    r"\b(?:abroad|abrod|overseas|videsh|videshi)\b",

    # Foreign education, foreign studies, foreign scholarships (including common typos like eucation, foriegn)
    r"\b(?:foreign|foriegn|foren)\s+(?:education|eucation|study|studies|scholarship|university|college|school|scheme|loan|degree|job|work|country|land|nation|government)\b",
    r"\b(?:education|eucation|study|studies|scholarship|loan|scheme|degree)\s+(?:in|for|at|to)?\s*(?:foreign|foriegn|foren)\b",

    # Outside India / International
    r"\b(?:outside\s+india|out\s+of\s+india|non-?indian\s+(?:university|college|school|government))\b",
    r"\b(?:international\s+(?:university|college|school)\s+(?:scholarship|scheme|grant|loan|admission))\b",

    # Foreign study/work destinations and degrees in foreign countries
    r"\b(?:study|studying|work(?:ing)?|live|living|settle|settling|migrate|migrating)\s+(?:in|to|at)\s+(?:usa|uk|us|uae|australia|canada|germany|france|japan|china|singapore|new\s+zealand|south\s+korea|italy|spain|netherlands|sweden|norway|denmark|switzerland|russia|brazil|mexico|south\s+africa|europe|united\s+states|united\s+kingdom|foreign\s+country|another\s+country|other\s+country)\b",
    r"\b(?:scholarship|education\s+loan|grant|scheme|fellowship|financial\s+aid)\s+(?:for\s+[\w\s]{1,25}\s+)?(?:in|at|to)\s+(?:usa|uk|us|uae|australia|canada|germany|france|japan|china|singapore|new\s+zealand|south\s+korea|italy|spain|netherlands|sweden|norway|denmark|switzerland|russia|brazil|mexico|south\s+africa|europe|united\s+states|united\s+kingdom)\b",
    r"\b(?:masters|bachelors|ms|mba|phd|degree|higher\s+studies)\s+(?:in|from|at)\s+(?:usa|uk|us|uae|australia|canada|germany|france|japan|china|singapore|new\s+zealand|south\s+korea|italy|spain|netherlands|sweden|norway|denmark|switzerland|europe|united\s+states|united\s+kingdom)\b",

    # Named foreign countries / regions — with government/study/scheme terms
    r"\b(?:united\s+states|united\s+kingdom|australia|canada|germany|france|japan|singapore|new\s+zealand|south\s+korea|italy|netherlands|sweden|norway|denmark|switzerland)\s+(?:government|university|college|school|scheme|grant|scholarship|visa|loan|education|study|student)\b",
    r"\b(?:government|university|college|scheme|grant|scholarship|visa|loan|education|study|student)\s+(?:in|at|of|from)\s+(?:united\s+states|united\s+kingdom|australia|canada|germany|france|japan|singapore|new\s+zealand|south\s+korea|italy|netherlands|sweden|norway|denmark|switzerland|usa|uk|uae)\b",

    # Named foreign universities/institutions — standalone triggers
    r"\b(?:harvard|mit|stanford|oxford|cambridge|yale|princeton|columbia|cornell|lse|imperial\s+college|nus|ntu\s+singapore|university\s+of\s+toronto|mcgill|university\s+of\s+melbourne|university\s+of\s+sydney|university\s+of\s+auckland|uc\s+berkeley|caltech)\b",

    # Named foreign scholarship programs — standalone triggers
    r"\b(?:chevening|commonwealth\s+scholarship|fulbright|daad|erasmus|gates\s+cambridge|rhodes\s+scholarship|rotary\s+scholarship|aga\s+khan\s+scholarship|inlaks|mext|korea\s+gks|australia\s+awards|canada\s+scholarship)\b",

    # Immigration, visa-abroad, work-abroad topics
    r"\b(?:work\s+(?:permit|visa)\s*(?:in|for|to)?\s*(?:uk|usa|canada|australia|germany|europe|abroad|overseas)?)\b",
    r"\b(?:immigration|emigrate|emigration|pr\s+(?:visa|card)|permanent\s+residency\s+(?:in|of|for)|green\s+card|greencard|h1b|tier\s*[1-5]\s*visa|schengen\s+visa)\b",
    r"\b(?:student\s+visa\s+(?:for|to|in)\s*(?:uk|usa|canada|australia|germany|europe|abroad|overseas)?)\b",

    # Explicitly non-Indian government
    r"\b(?:us\s+government|uk\s+government|australian\s+government|canadian\s+government|eu\s+(?:scheme|grant|fund)|world\s+bank\s+grant|un\s+(?:scholarship|grant|fellowship))\b",
]

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
    r"\b(?:capital\s*of\s*(?!india\b)[a-z]+|who\s*was\s*(?:napoleon|einstein|shakespeare|alexander|hitler|columbus)|who\s*invented|speed\s*of\s*light|how\s*far\s*is\s*(?:the\s*)?(?:moon|sun|mars)|distance\s*to|explain\s*photosynthesis)\b",

    # Private commercial banking and credit cards (without government scheme context)
    r"\b(?:hdfc|icici|axis\s*bank|kotak|bajaj\s*finserv)\s+(?:bank\s+)?(?:personal\s*loan|credit\s*card|gold\s*loan\s*emi|emi\s*calculator)\b",

    # Commercial vehicle showroom price and retail shopping (not government subsidy)
    r"\b(?:on\s*road\s*price|showroom\s*(?:price|discount)|dealer\s*price|dealer\s*showroom\s*discount|second\s*hand\s*(?:car|bike|tractor)\s*price)\b",

    # Direct clinical medical advice, symptom diagnosis, and prescription requests (not health insurance/schemes)
    r"\b(?:what\s+(?:tablet|medicine|\w+\s+tablet|\w+\s+medicine|tablet\s+or\s+medicine)|what\s+medicine\s+should\s+i\s+take|prescription|pain\s+relief\s+tablet|should\s+i\s+take\s+(?:for|to)|cure\s+my\s+(?:fever|pain|cough)|paining\s+severely|symptom\s+of\s+cancer|diagnose\s+my|fever\s+tablet|headache\s+medicine)\b",

    # Criminal law, police FIR registration, and civil property boundary disputes
    r"\b(?:police\s*(?:station|thana)?\s*(?:mein\s*)?fir|file\s*(?:a\s*)?police\s*fir|file\s*(?:an\s*)?fir|एफआईआर\s*(?:कैसे\s*)?दर्ज|पुलिस\s*थाना\s*में\s*एफआईआर|court\s*case\s*against|hire\s*(?:a\s*)?lawyer)\b"
]

# Prompt injection & jailbreak patterns (English & Indic)
PROMPT_INJECTION_PATTERNS = [
    r"\b(?:ignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions|directions|rules|prompts))\b",
    r"\b(?:disregard\s+all\s+(?:rules|guidelines|constraints))\b",
    r"\b(?:you\s+are\s+now\s+(?:in\s+)?(?:dan|developer\s+mode|an?\s+unrestricted|unhinged|god\s+mode|jailbroken))\b",
    r"\b(?:jailbreak(?:\s+mode)?|bypass\s+(?:all\s+)?guardrails)\b",
    r"\b(?:system\s+prompt|reveal\s+(?:your\s+)?prompt|print\s+(?:the\s+)?system\s+prompt)\b",
    r"\b(?:pretend\s+you\s+have\s+no\s+(?:rules|restrictions|ethics))\b",
    r"सिस्टम\s*निर्देश|सुरक्षा\s*नियम\s*बाईपास|प्रॉम्प्ट\s*(?:दिखाओ|प्रिंट\s*करो|स्क्रीन\s*पर)",
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
    """Checks if text contains authentic scheme/welfare terms in English or Indian scripts."""
    lowered = text.casefold()
    if any(mwt in lowered for mwt in MULTI_WORD_SCHEME_TERMS):
        return True
    if any(mwit in lowered for mwit in MULTI_WORD_INDIC_TERMS):
        return True
    if any(it in lowered for it in INDIC_SCHEME_TERMS):
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

    # 6. GEOGRAPHIC SCOPE CHECK — evaluated BEFORE general domain check.
    # Exemption: Legitimate Government of India welfare schemes for overseas studies (e.g. National Overseas Scholarship - NOS)
    is_goi_overseas_scheme = any(kw in lower_query for kw in [
        "national overseas scholarship", "nos scheme", "nos scholarship",
        "ministry of social justice", "dr. ambedkar overseas", "dr ambedkar central sector"
    ])
    if not is_goi_overseas_scheme:
        for pat in GEOGRAPHIC_OOD_PATTERNS:
            if re.search(pat, lower_query, re.IGNORECASE):
                return "OUT_OF_DOMAIN", generate_geographic_ood_refusal(cleaned)

    # 7. Check for explicit negative out-of-domain patterns (coding, sports, cinema, homework, recipes)
    matched_ood = False
    for pat in OUT_OF_DOMAIN_PATTERNS:
        if re.search(pat, lower_query):
            matched_ood = True
            break

    if matched_ood:
        return "OUT_OF_DOMAIN", generate_ood_refusal(cleaned)

    # All genuine citizen queries pass to Stage 2 Semantic LLM Router,
    # which natively understands intent, context, and multi-lingual semantics
    # without brittle static keyword dictionaries.
    return "IN_DOMAIN", None


# =========================================================================
# REFUSAL & GUIDANCE GENERATORS
# =========================================================================

def generate_geographic_ood_refusal(user_query: str) -> str:
    """
    Returns a clear, helpful refusal for queries about foreign/overseas/non-India
    schemes, scholarships, universities, visas, or international programs.
    """
    escaped_query = user_query[:120].replace("*", "\\*").replace("`", "\\`")
    return (
        "🌐 **Geographic Scope Notice — India-Only Platform**\n\n"
        f"Your question (*\"{escaped_query}\"*) appears to be about **foreign countries, overseas education, "
        "international scholarships, or non-Indian government programs**.\n\n"
        "**JanSahayak (myScheme) covers only official Indian Government schemes** — Central Government "
        "and all 36 State/UT government welfare programs for Indian citizens residing in India.\n\n"
        "---\n"
        "### 🇮🇳 What I Can Help With (India-only schemes):\n"
        "- 🎓 **Education Loans & Scholarships in India:** Central Sector Scholarship, PM-USP, "
        "National Means-Cum-Merit Scholarship (NMMS), Dr. Ambedkar Post-Matric Scholarship\n"
        "- 🏦 **Education Loans:** Vidya Lakshmi Portal (subsidised loans from PSU banks for Indian institutions)\n"
        "- 💼 **Skill Development:** PM Kaushal Vikas Yojana (PMKVY) for training in India\n"
        "- 🌾 **Agriculture, Housing, Health, Business** schemes funded by GoI\n\n"
        "---\n"
        "### 🔎 For Foreign Scholarships / Abroad Education, visit:\n"
        "- **Education Loans Abroad:** Indian banks (SBI, Bank of Baroda) offer forex education loans — ask your bank directly\n"
        "- **Fulbright, Chevening, DAAD, Erasmus** — apply via their official websites\n"
        "- **Study in India portal:** [https://www.studyinindia.gov.in](https://www.studyinindia.gov.in)\n\n"
        "Please ask about an **Indian government welfare scheme** and I'll be happy to help!"
    )


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
