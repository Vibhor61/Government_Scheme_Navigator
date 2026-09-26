# Citizen Rights and Government Scheme Navigator
### A Retrieval-Augmented Generation (RAG) System for Scheme Discovery and Eligibility Awareness
**Department of Computer Science and Technology | Maharaja Agrasen Institute of Technology (MAIT)**  
*Minor Project — 7th Semester (Batch 2023–2027)*

---

## 📌 Project Overview
India offers thousands of welfare schemes across agriculture, healthcare, education, and employment. However, many eligible citizens miss out because official documents use complex administrative language and fragmented portals.

**Citizen Rights and Government Scheme Navigator** bridges this gap:
- **Natural Language Querying:** Citizens describe their real-life situations in everyday language.
- **Dual-Arm Hybrid Retrieval:** Merges PostgreSQL Full-Text Search (lexical `tsvector`/BM25) with dense semantic embeddings (`pgvector` + `all-MiniLM-L6-v2`) using **Reciprocal Rank Fusion (RRF)**.
- **Fact-Grounded Generation:** Enforces strict prompt grounding with citations to official scheme circulars, preventing hallucination.
- **RAGAS Evaluation Framework:** Automated claim-level verification of **Faithfulness** and **Answer Relevancy**.
- **Social Impact:** Aligned with **UN Sustainable Development Goal 16 (Peace, Justice and Strong Institutions)**.

---

## 🏛 System Architecture & Hybrid Pipeline

```
                              ┌───────────────────────────┐
                              │   Citizen Natural Query   │
                              └─────────────┬─────────────┘
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     ▼                                             ▼
          ┌──────────────────────┐                     ┌──────────────────────┐
          │ Lexical Search (FTS) │                     │ Dense Vector Search  │
          │   tsvector / BM25    │                     │  pgvector / Cosine   │
          └──────────┬───────────┘                     └──────────┬───────────┘
                     │                                             │
                     └──────────────────────┬──────────────────────┘
                                            ▼
                              ┌───────────────────────────┐
                              │ Reciprocal Rank Fusion    │
                              │  Score = Σ (w / (60 + R)) │
                              └─────────────┬─────────────┘
                                            ▼
                              ┌───────────────────────────┐
                              │ Top-K Verified Chunks     │
                              └─────────────┬─────────────┘
                                            ▼
                              ┌───────────────────────────┐
                              │    Grounded Generator     │
                              │   (Strict Fact Context)   │
                              └─────────────┬─────────────┘
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     ▼                                             ▼
          ┌──────────────────────┐                     ┌──────────────────────┐
          │ Sourced Answer + URL │                     │   RAGAS Evaluation   │
          │   & Eligibility Card │                     │ Faithfulness & Rel.  │
          └──────────────────────┘                     └──────────────────────┘
```

---

## 🐳 Docker Deployment (Images prefixed with `minor_`)

All Docker services and container images strictly use the `minor_` prefix as required:

| Service | Image Name | Container Name | Port | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Database** | `pgvector/pgvector:pg16` | `minor_postgres` | `5432` | PostgreSQL 16 with pgvector extension |
| **Backend API** | `minor_backend:latest` | `minor_backend` | `8000` | FastAPI Hybrid RAG Engine |
| **Frontend UI** | `minor_frontend:latest` | `minor_frontend` | `3000` | Nginx + React.js web interface |

### 🚀 One-Shot Run with Docker Compose:
```bash
docker compose up --build
```
Once started:
- 🌐 **Web Interface:** [http://localhost:3000](http://localhost:3000) (or [http://localhost:8000](http://localhost:8000))
- 📖 **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- 🔍 **Health Status:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 💻 Standalone Python Run (Zero Setup Required)

If running directly on Windows without Docker:
```bash
# Run the server directly
python run_backend.py
```
Open **[http://localhost:8000](http://localhost:8000)** in any browser.

---

## 📊 RAGAS Evaluation Metrics

The system continuously verifies generated responses:
1. **Faithfulness Score ($\ge 98\%$):**
   $$\text{Faithfulness} = \frac{|\text{Supported Claims}|}{|\text{Total Claims in Answer}|}$$
   Every extracted fact (benefit amount, land size, age limit) is validated against official scheme texts.
2. **Answer Relevancy Score ($\ge 95\%$):**
   Evaluates semantic alignment between citizen intent and generated response summary.
3. **Execution Latency:**
   Sub-25ms hybrid retrieval and ranking pipeline.

---

## 📚 Real Welfare Schemes Covered
- **Agriculture:** PM-KISAN, Pradhan Mantri Fasal Bima Yojana (PMFBY).
- **Healthcare:** Ayushman Bharat (AB-PMJAY) including Senior Citizens (70+) coverage.
- **Education:** AICTE Pragati Scholarship for Girls, PM YASASVI, NMMSS.
- **Employment & Business:** PM SVANidhi (Street Vendors), PM Vishwakarma, PMMY (Mudra Loan), MGNREGA.
- **Social Security & Women:** Sukanya Samriddhi Yojana (SSY), Atal Pension Yojana (APY).

---

## 👥 Project Team
- **Department:** Computer Science and Technology, Maharaja Agrasen Institute of Technology
- **Batch:** 2023–2027 (7th Semester)
