"""
Bulk Scheme Ingestion & pgvector Embedding Engine
Loads the entire verified catalog of 40+ authentic government schemes from official sources,
chunks them into 4 distinct semantic representations per scheme (160+ total dense chunks),
and embeds them into PostgreSQL with 384-dimensional dense vectors.
"""

import os
import sys
import json
from sqlalchemy.orm import Session

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import Scheme, SchemeChunk, EvaluationLog
from app.embedding import generate_embedding

def run_bulk_ingestion():
    print("=" * 80)
    print(" BULK SCHEMES INGESTION & PGVECTOR EMBEDDING PIPELINE (OFFICIAL REPOSITORIES) ")
    print("=" * 80)

    # 1. Initialize Tables
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # 2. Wipe any old/test records cleanly
    print("\n[1/3] Purging any legacy chunks and records...")
    db.query(SchemeChunk).delete()
    db.query(Scheme).delete()
    db.query(EvaluationLog).delete()
    db.commit()
    print("  -> Clean purge completed successfully.")

    # 3. Load comprehensive official data catalog
    data_path = os.path.join(os.path.dirname(__file__), "app", "data", "schemes_data.json")
    if not os.path.exists(data_path):
        print(f"[-] Error: Data catalog not found at {data_path}")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    schemes_list = data.get("schemes", [])
    total_schemes = len(schemes_list)
    print(f"\n[2/3] Loaded {total_schemes} verified official schemes from: {data.get('source_registry')}")

    # 4. Ingest and Vectorize Chunks
    print(f"\n[3/3] Generating 384-dimensional dense embeddings for all 4 semantic facets per scheme...")
    total_chunks = 0

    for idx, s in enumerate(schemes_list, 1):
        s_id = s["id"]
        title = s["title"]
        category = s.get("category", "General")
        ministry = s.get("ministry", "")

        # Master Scheme Record
        scheme_obj = Scheme(
            id=s_id,
            title=title,
            short_name=s.get("short_name", ""),
            category=category,
            ministry=ministry,
            target_beneficiaries=s.get("target_beneficiaries", ""),
            financial_assistance=s.get("financial_assistance", ""),
            eligibility_criteria=json.dumps(s.get("eligibility_criteria", [])),
            benefits=json.dumps(s.get("benefits", [])),
            documents_required=json.dumps(s.get("documents_required", [])),
            application_process=s.get("application_process", ""),
            official_portal=s.get("official_portal", ""),
            tags=json.dumps(s.get("tags", []))
        )
        db.add(scheme_obj)

        # Facet 1: Overview & Financial Assistance Scope
        c1_text = f"Scheme: {title} ({s.get('short_name','')}). Category: {category}. Ministry: {ministry}. Target Beneficiaries: {s.get('target_beneficiaries','')}. Financial Assistance & Grants: {s.get('financial_assistance','')}. Keywords: {', '.join(s.get('tags', []))}."
        c1_emb = generate_embedding(f"{title} {s.get('financial_assistance','')} {s.get('target_beneficiaries','')} {category} {ministry}")
        db.add(SchemeChunk(
            id=f"{s_id}-overview",
            scheme_id=s_id,
            section_name="Overview",
            chunk_title=f"{title} - Overview & Financial Scope",
            content=c1_text,
            embedding=json.dumps(c1_emb)
        ))

        # Facet 2: Eligibility Criteria & Exclusions
        elig_list = s.get("eligibility_criteria", [])
        c2_text = f"Official Eligibility Criteria & Exclusions for {title} ({category}): " + " ".join(elig_list)
        c2_emb = generate_embedding(f"{title} eligibility criteria who is eligible requirements income limit age conditions {' '.join(elig_list)}")
        db.add(SchemeChunk(
            id=f"{s_id}-eligibility",
            scheme_id=s_id,
            section_name="Eligibility",
            chunk_title=f"{title} - Eligibility Criteria & Exclusions",
            content=c2_text,
            embedding=json.dumps(c2_emb)
        ))

        # Facet 3: Benefits & Mandatory Documents
        bens_list = s.get("benefits", [])
        docs_list = s.get("documents_required", [])
        c3_text = f"Benefits Delivered under {title}: " + " ".join(bens_list) + f". Mandatory Documents: " + ", ".join(docs_list) + f". Official Portal: {s.get('official_portal', '')}."
        c3_emb = generate_embedding(f"{title} benefits documents required proof certificate aadhaar ration card direct benefit {' '.join(bens_list)}")
        db.add(SchemeChunk(
            id=f"{s_id}-benefits-docs",
            scheme_id=s_id,
            section_name="Benefits & Documents",
            chunk_title=f"{title} - Benefits & Required Documents",
            content=c3_text,
            embedding=json.dumps(c3_emb)
        ))

        # Facet 4: Application Procedure & Online Registration
        proc = s.get("application_process", "")
        c4_text = f"How to Apply for {title}: {proc}. Official Government Portal: {s.get('official_portal', '')}."
        c4_emb = generate_embedding(f"{title} how to apply online application registration procedure portal {proc}")
        db.add(SchemeChunk(
            id=f"{s_id}-process",
            scheme_id=s_id,
            section_name="Application",
            chunk_title=f"{title} - Application Process & Online Registration",
            content=c4_text,
            embedding=json.dumps(c4_emb)
        ))

        total_chunks += 4
        print(f"  [{idx:02d}/{total_schemes:02d}] Indexed: {title[:48]}... (4 chunks vectorized)")

    db.commit()
    db.close()

    print("\n" + "=" * 80)
    print(f" [+] BULK INGESTION COMPLETED SUCCESSFULLY!")
    print(f" [+] Total Official Schemes Stored: {total_schemes}")
    print(f" [+] Total pgvector Chunks Embedded: {total_chunks}")
    print("=" * 80)

if __name__ == "__main__":
    run_bulk_ingestion()
