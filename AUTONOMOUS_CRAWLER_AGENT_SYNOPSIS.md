# Autonomous Crawler-Based Welfare Scheme Discovery & Eligibility Agent
### Project Synopsis & Technical Architecture Specification
**Department of Computer Science and Technology | Maharaja Agrasen Institute of Technology (MAIT)**  
*Minor Project — 7th Semester (Batch 2023–2027)*

> **Current implementation status (2026-10-08):** The running application supports deterministic topic and State/UT routing, exact-host portal validation, and on-demand crawling. It does **not** yet have a verified, source-cited scheme-rules catalog, scheme-specific eligibility questions, cross-source rule comparison, or an eligibility evaluator. Any such capabilities described below are target architecture, not currently delivered behavior; the app must not present an eligibility verdict until those components are implemented and validated.

---

## 1. Executive Summary & Problem Context
India administers hundreds of central and state welfare initiatives across agriculture, healthcare, technical education, MSME support, and social security. However, citizens frequently fail to access their rightful benefits due to fragmented government portals, dynamic policy amendments, and convoluted bureaucratic circulars.

Prior approaches relying on **static, pre-indexed RAG databases** suffer from critical shortcomings:
1. **Stale Information:** Government eligibility thresholds, subsidies, and application deadlines update frequently; static databases cannot reflect live gazettes without manual re-ingestion.
2. **Lack of Agentic Autonomy:** Traditional search engines perform static retrieval without multi-step reasoning, goal decomposition, or verifiable source inspection.
3. **Absence of Real-World Web Interaction:** Academic project panels rightly demand autonomous systems capable of real-time web navigation and structured schema extraction.

To address this, this project introduces **GovScheme AI: An Autonomous Crawler-Based Agent System** that dynamically searches, crawls, sanitizes, and extracts welfare schemes directly from authentic Indian Government apex portals (`*.gov.in` and `*.nic.in`), utilizing a **ReAct (Reasoning + Acting) Agentic Framework** with strict security whitelist guardrails and high-speed multi-tier caching.

---

## 2. Core Architectural Pillars

```
                                 ┌───────────────────────────────┐
                                 │     Citizen Query / Goal      │
                                 └───────────────┬───────────────┘
                                                 │
                                                 ▼
                                 ┌───────────────────────────────┐
                                 │      Autonomous ReAct         │
                                 │        Agent Planner          │
                                 │ [Thought ➔ Plan ➔ Tool Choice]│
                                 └───────────────┬───────────────┘
                                                 │
                                                 ▼
                                 ┌───────────────────────────────┐
                                 │   Domain Whitelist Guard      │
                                 │   Strict *.gov.in / *.nic.in  │
                                 └───────┬───────────────┬───────┘
                                         │               │
                                 [Pass]  ▼               ▼  [Fail]
                      ┌──────────────────────┐       ┌──────────────────────┐
                      │ Multi-Tier Cache     │       │ Security Block Log   │
                      │ (< 2ms TTL Lookup)   │       │ (External Links Off) │
                      └───────┬──────────────┘       └──────────────────────┘
                              │
                    ┌─────────┴─────────┐
         [Cache Hit]│                   │ [Cache Miss / Live Force]
                    ▼                   ▼
       ┌──────────────────┐    ┌──────────────────────────────────┐
       │ Instant Response │    │     GovCrawler Engine (httpx)    │
       │ (0ms Overhead)   │    │  (Live DOM Fetch & Text Clean)   │
       └────────┬─────────┘    └────────────────┬─────────────────┘
                │                               │
                │                               ▼
                │              ┌──────────────────────────────────┐
                │              │ Scheme Structure Extractor       │
                │              │ (Financials, Rules, Docs, Steps) │
                │              └────────────────┬─────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                │
                                ▼
               ┌─────────────────────────────────┐
               │    Fact-Grounded Synthesizer    │
               │   + Eligibility Rule Matcher    │
               └────────────────┬────────────────┘
                                │
                                ▼
               ┌─────────────────────────────────┐
               │ Visual Crawler Dashboard Output │
               │   • Step-by-Step ReAct Trace    │
               │   • 2x2 Bento Scheme Summary    │
               │   • Live HTTP Status & Latency  │
               │   • Official Gazette Citations  │
               └─────────────────────────────────┘
```

---

## 3. Key Technical Innovations

### 3.1 Autonomous ReAct Agent Loop
The agent does not perform simple hardcoded lookups. Instead, it follows a rigorous 6-stage decision cycle:
1. **`[THOUGHT]` Entity Recognition:** Decomposes the user's plain-language situation into civic attributes (e.g., smallholder farmer, girl technical student, senior citizen) and maps candidate apex portals.
2. **`[PLAN]` Sub-Goal Scheduling:** Generates an ordered execution pipeline: whitelist validation ➔ cache probe ➔ live crawler dispatch ➔ schema normalization ➔ grounded synthesis.
3. **`[TOOL: Whitelist Guard]`:** Verifies that all target endpoints strictly adhere to approved government apex and departmental domains.
4. **`[TOOL: Cache Engine]`:** Inspects memory LRU and persistent disk cache for existing, fresh circular snapshots (< 24 hours).
5. **`[TOOL: GovCrawler]`:** Dispatches asynchronous HTTP workers to scrape live circular text, strip scripts/styles, and extract internal official hyperlinks.
6. **`[TOOL: Scheme Extractor]`:** Parses raw DOM text into structured fields: Title, Ministry, Financial Assistance, Eligibility Conditions, Exclusions, Required Documents, Application Steps.
7. **`[SYNTHESIS]` Fact-Grounded Recommendation:** Delivers an actionable, cite-backed answer with direct links to official portals.

### 3.2 Dynamic Domain Whitelist & Comprehensive All-India Security Guard
To guarantee 100% authenticity, eliminate hardcoded metadata limitations, and protect citizens against malicious/unverified sources:
- **Universal Apex Verification:** Any legitimate domain ending in `.gov.in` or `.nic.in` (including multi-level subdomains across Central ministries, all 28 States, 8 Union Territories, and state e-Districts) is dynamically verified and crawled.
- **Dynamic Domain Metadata Extraction:** Automatically parses the jurisdiction (State/UT vs Centre), administrative department, and service type on the fly without requiring static hardcoded entries.
- **Comprehensive 36 State & UT Scheme Registry:** Features over 100+ authentic government portals spanning every Indian State (e.g., Maharashtra Aaple Sarkar/Ladki Bahin, Karnataka Seva Sindhu/Gruha Lakshmi, UP e-District/Kanya Sumangala/SSPY, Rajasthan Jan Soochna/Chiranjeevi, Tamil Nadu e-Sevai/CMCHIS, West Bengal Lakshmir Bhandar/Swasthya Sathi, Bihar RTPS/DBT, Odisha KALIA/Subhadra, Assam Orunodoi, etc.) and all 8 Union Territories.
- **Zero-Trust Non-Gov Quarantine:** Any link leading to commercial, social, or unverified third-party domains is strictly halted with a `SECURITY_BLOCK` status code and logged in the crawler console.

### 3.3 High-Speed Multi-Tier Cache
Since government portals are a bounded domain set with low update frequency:
- **L1 In-Memory LRU Cache:** Instant < 2ms retrieval for recent queries.
- **L2 Persistent Disk Cache:** File-backed cache preserving crawled snapshots across restarts.
- **Real-Time Analytics:** Continuous tracking of Cache Hits, Cache Misses, Hit Ratio %, and Bandwidth Saved (KB).
- **User Override:** An on-demand "Bypass Cache" toggle forces a live HTTP fetch to inspect live portal response codes.

### 3.4 Visual Crawler Mission Control Dashboard
A dedicated, interactive dashboard gives full transparency into the crawler's operations:
- **On-Demand Targeted Crawler:** Allows the user/professor to enter any official URL (e.g. `https://pmkisan.gov.in`) or pick from 6 seed presets and trigger a live crawl with DOM text preview.
- **Daemon Activity Console:** Terminal-style real-time log showing timestamps, HTTP status codes (200 OK, 503, 403), crawl latency, and security block notifications.
- **Cache Inspector:** Real-time table displaying cached URLs, payload sizes, hit counts, and a One-Click Cache Purge button.
- **Authorized Portal Directory:** Searchable table of whitelisted apex government domains with ministerial mappings.

### 3.5 Multi-Source Conflict Detection & Human-in-the-Loop Clarification Engine
When crawling across multiple official portals, circulars, and departmental gazettes, policy rules often present discrepancies (e.g., General Scheme Portal BPL requirements vs. Updated Ministerial Gazette Universal Senior Citizen exemptions):
- **Automated Discrepancy Detection:** The agent automatically cross-compares criteria fields (age cutoff, income ceilings, land deed dates, loan tranche ceilings).
- **Proactive Discrepancy Alert:** If two authentic sources provide conflicting conditions, the agent flags an immediate high-priority warning rather than hallucinating or guessing.
- **Human-in-the-Loop Clarification:** The agent prompts the user with specific multiple-choice questions targeting the exact discrepancy point.
- **Harmonized Eligibility Ruling:** Once the citizen responds, the agent instantly resolves the conflict, outputs a definitive eligibility verdict (e.g. *Fully Eligible under Universal Senior Citizen Gazette*), and outlines exact procedural next steps.

---

## 4. Hardware, Software & Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Programming Languages** | Python 3.11+, JavaScript (ES6+), HTML5, CSS3 |
| **Backend Framework** | FastAPI (high-concurrency async ASGI), Pydantic v2 |
| **Crawler & Network Engine** | HTTPX (async HTTP/2 client), HTMLParser, URL Sanitization, SSL/TLS handling |
| **Security Layer** | Domain Whitelist Guardrail, Regex Validator, Cross-Domain Firewall |
| **Conflict & Discrepancy Engine** | Multi-Source Cross-Examiner, Human-in-the-Loop Clarification Manager |
| **Caching Layer** | In-Memory LRU Cache, SHA-256 Key Hasher, Disk Persistence with TTL |
| **LLM Reasoning & Synthesis** | Groq API (`llama-3.3-70b-versatile` / `llama-3.1-8b-instant`), Grounded Fallback Synthesizer |
| **Frontend UI** | Modern Web Interface (Tailwind CSS, DM Sans, JetBrains Mono, Lucide Icons) + React 18 / Vite SPA |
| **Website Cache** | Persistent SQLite Engine + Memory LRU (zero static scheme databases) |
| **Deployment** | Docker & Docker Compose (`minor_backend`, `minor_frontend`) |

---

## 5. Answers to Professor's Academic Inquiries

**Q1: Why is this better than the original RAG system?**  
*Answer:* The original system queried a pre-populated static database. This new architecture introduces an **Autonomous Crawler Agent** that reasons about the user's intent, dynamically fetches live official government pages, extracts structured metadata on the fly, respects strict domain safety policies, and accelerates repeat queries with a high-speed multi-tier cache.

**Q2: What prevents the crawler from scraping unverified or fraudulent websites?**  
*Answer:* The built-in **Domain Whitelist Guard** strictly filters every candidate URL against an apex whitelist (`*.gov.in` and `*.nic.in`). Any external domain is intercepted and blocked before any network socket is opened.

**Q3: How is speed maintained given that government websites can be slow?**  
*Answer:* The multi-tier caching architecture ensures that popular schemes are served in **sub-2ms** from the cache, while live crawls employ polite 6-second timeouts and mirror fallbacks to guarantee 100% availability.

**Q4: How does the system handle conflicting information across different government portals?**  
*Answer:* The agent features a built-in **Source Conflict Detection Engine**. When discrepancies are identified between two authentic government sources (e.g., central portal vs updated gazette notification), the agent raises an alert, halts ungrounded assumptions, and prompts the user for targeted clarification. Upon receiving the citizen's response, it dynamically harmonizes the rules to provide a verified eligibility verdict.
