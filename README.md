---
title: GovScheme AI Crawler
emoji: 🏛️
colorFrom: green
colorTo: emerald
sdk: docker
app_port: 7860
pinned: false
---

# GovScheme AI: Evidence-First Government Scheme Navigator
### National scheme discovery with source-grounded eligibility checks
**Department of Computer Science and Technology | Maharaja Agrasen Institute of Technology (MAIT)**  
*Minor Project — 7th Semester (Batch 2023–2027)*

---

## 📌 Project Overview
India administers hundreds of central and state welfare initiatives across agriculture, healthcare, education, and MSME sectors. However, many eligible citizens remain unaware because official portals are fragmented and administrative circulars are dense.

- **One nationwide scheme repository:** All topics search the myScheme national platform, which indexes Central and State/UT schemes. The crawler does not choose arbitrary state portals or add topic-specific portal patches.
- **LLM query planning, not URL authority:** The LLM can propose search terms for the single registered repository. The API path and host are constructed by deterministic code; an LLM cannot add hosts or authorize arbitrary requests.
- **Catalog-backed crawling:** Search results return scheme slugs and summaries. The crawler fetches scheme-detail records through myScheme's same-host API, with bounded query count, page size, and detail count.
- **Evidence validation:** Each extracted eligibility rule must include a quotation present in the fetched scheme record. Supported fields, operators, thresholds, and quotation context are checked before use. Benefits and application steps are shown only when their evidence quotations are also present.
- **Questionnaire and comparison:** Missing State/UT and supported rule fields are asked together when state-specific candidates are found. The evaluator compares explicit answers to cited rules; missing, ambiguous, or conflicting values remain unknown. Passing captured rules is not an approval or guarantee.
- **Exact-host security allowlist:** The active crawler allowlist contains only the exact myScheme host (and its `www` variant). A `.gov.in` or `.nic.in` suffix alone is not trusted; arbitrary subdomains and redirects are rejected.
- **Honest limits:** Coverage depends on myScheme's current catalog, search ranking, and detail records. The app does not claim exhaustive coverage and will not issue a verdict if it cannot retrieve and validate supported rules.
- **Crawler dashboard:** Shows portal registry entries, request status, cache activity, and trace details.

---

## 🏛 System Architecture & Agent Workflow

```
                               ┌───────────────────────────┐
                               │   Citizen Natural Query   │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │ Understand Scheme Request │
                               │ LLM Plan: Search Terms     │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                ┌────────────────────────────────────────────┐
                │ Search Central + State/UT catalogue       │
                │ Exact myScheme host + fixed internal API  │
                │ Bounded scheme-detail fetch               │
                └─────────────────────┬──────────────────────┘
                                      ▼
                                  ┌─────────────────────────────┐
                                  │ Exact registered-host check │
                                  └──────────────┬──────────────┘
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │ Extract quoted scheme rules │
                                  └──────────────┬──────────────┘
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │ Validate quotes + rule shape │
                                  └──────────────┬──────────────┘
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │ Ask missing supported facts │
                                  │ Compare deterministically   │
                                  │ Cite checks; preserve UNKNOWN│
                                  └─────────────────────────────┘
```

---

## 🚀 Quick Run (Docker)

Start both services with Docker Compose:
```bash
docker compose up --build
```
Open **[http://localhost:3000](http://localhost:3000)** in any web browser.

- 🕷️ **Crawler Agent & Mission Control:** [http://localhost:8000](http://localhost:8000) (select Crawler Agent tab)
- 📖 **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- 🔍 **Crawler Live Dashboard API:** [http://localhost:8000/api/crawler/dashboard](http://localhost:8000/api/crawler/dashboard)

Run focused backend checks in the Docker image:
```bash
docker compose run --build --rm minor_backend python -m unittest discover -s tests -v
```

---

## 🐳 Docker Deployment

The system is fully containerized with Docker Compose:

| Service | Container Name | Port | Description |
| :--- | :--- | :--- | :--- |
| **Backend API** | `minor_backend` | `8000` | FastAPI national scheme discovery workflow and crawler (with persistent SQLite website cache) |
| **Frontend UI** | `minor_frontend` | `3000` | Nginx + React.js SPA Dashboard |

Run using:
```bash
docker compose up --build
```

---

## 📊 Core Crawler Agent Capabilities

1. **Shared scheme flow:** Every query uses the same query-planning, myScheme search, scheme-detail retrieval, source-quote validation, questionnaire, and deterministic comparison steps.
2. **Minimal exact-host allowlist:** Only the myScheme repository host and its `www` variant are crawlable. Users cannot submit arbitrary `.gov.in` or `.nic.in` hosts.
3. **Central/state separation:** Scheme jurisdiction comes from myScheme records. State-specific scheme results are withheld until the user's State/UT is known.
4. **Content-aware extraction:** The crawler handles HTML, JSON, XML, plain text, and text-based PDF responses. HTML parsing tolerates void tags and malformed nesting; canonical redirects are followed only to explicitly registered hosts.
5. **Transport and extraction are reported separately:** TLS verification remains enabled. A page returning HTTP 200 with no readable static text is retried with a Playwright/Chromium renderer. Browser requests and redirects are restricted to exact registered HTTPS hosts; image-only pages still need OCR.
6. **Bounded evidence:** Rules are extracted at request time from fetched scheme records, rather than maintained in a manually curated database. A passing result means only that every captured supported rule passed; it does not guarantee the source record exposed every condition or imply approval. If extraction, evidence, or comparison is insufficient, the result remains unknown.

---

## 👥 Project Team
- **Department:** Computer Science and Technology, Maharaja Agrasen Institute of Technology
- **Batch:** 2023–2027 (7th Semester)
- **Team:** Vibhor, Himanshu, Pratyaksh
