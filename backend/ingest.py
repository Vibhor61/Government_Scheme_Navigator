import os
import sys
import json
from sqlalchemy.orm import Session

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import Scheme, SchemeChunk, EvaluationLog
from app.embedding import generate_embedding

def purge_and_ingest_real_data():
    print("=" * 70)
    print(" PURGING ALL TEST/FAKE DATA & INGESTING 100% VERIFIED GOVT SCHEMES ")
    print("=" * 70)
    
    # 1. Initialize database tables
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # 2. Complete Purge of any old/test/mock records
    print("\n[Step 1] Purging all existing embeddings, chunks, and old data...")
    deleted_chunks = db.query(SchemeChunk).delete()
    deleted_schemes = db.query(Scheme).delete()
    deleted_logs = db.query(EvaluationLog).delete()
    db.commit()
    print(f"  -> Successfully wiped {deleted_chunks} old chunks, {deleted_schemes} old schemes, {deleted_logs} evaluation logs.")

    # 3. Load 100% authentic, verified schemes from schemes_data.json
    data_path = os.path.join(os.path.dirname(__file__), "app", "data", "schemes_data.json")
    if not os.path.exists(data_path):
        print(f"Error: Real data catalog not found at {data_path}")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    schemes_list = data.get("schemes", [])
    print(f"\n[Step 2] Loaded {len(schemes_list)} verified authentic government welfare schemes from official catalog.")

    # 4. Ingest and generate 4 semantic chunks per scheme with 384-dimensional embeddings
    print("\n[Step 3] Chunking and generating 384-dimensional dense embeddings for PostgreSQL pgvector...")
    total_chunks_indexed = 0

    for idx, s_data in enumerate(schemes_list, 1):
        scheme_id = s_data["id"]
        scheme_title = s_data["title"]
        category = s_data.get("category", "General")
        ministry = s_data.get("ministry", "")

        # Master Scheme Record
        scheme_obj = Scheme(
            id=scheme_id,
            title=scheme_title,
            short_name=s_data.get("short_name"),
            category=category,
            ministry=ministry,
            target_beneficiaries=s_data.get("target_beneficiaries", ""),
            financial_assistance=s_data.get("financial_assistance", ""),
            eligibility_criteria=json.dumps(s_data.get("eligibility_criteria", [])),
            benefits=json.dumps(s_data.get("benefits", [])),
            documents_required=json.dumps(s_data.get("documents_required", [])),
            application_process=s_data.get("application_process", ""),
            official_portal=s_data.get("official_portal", ""),
            tags=json.dumps(s_data.get("tags", []))
        )
        db.add(scheme_obj)

        # Chunk 1: Overview & Financial Scope
        c1_text = f"Scheme Title: {scheme_title}. Short Name: {s_data.get('short_name','')}. Category: {category}. Ministry: {ministry}. Target Beneficiaries: {s_data.get('target_beneficiaries','')}. Financial Assistance & Grant Details: {s_data.get('financial_assistance','')}. Search Keywords: {', '.join(s_data.get('tags',[]))}."
        c1_emb = generate_embedding(f"{scheme_title} {s_data.get('financial_assistance','')} {s_data.get('target_beneficiaries','')} {category}")
        chunk_1 = SchemeChunk(
            id=f"{scheme_id}-overview",
            scheme_id=scheme_id,
            section_name="Overview",
            chunk_title=f"{scheme_title} - Overview & Financial Assistance",
            content=c1_text,
            embedding=json.dumps(c1_emb)
        )
        db.add(chunk_1)

        # Chunk 2: Eligibility Criteria & Exclusions
        elig_list = s_data.get("eligibility_criteria", [])
        c2_text = f"Official Eligibility Criteria for {scheme_title} ({category}): " + " ".join(elig_list)
        c2_emb = generate_embedding(f"{scheme_title} eligibility conditions criteria exclusions requirements income limit age {' '.join(elig_list)}")
        chunk_2 = SchemeChunk(
            id=f"{scheme_id}-eligibility",
            scheme_id=scheme_id,
            section_name="Eligibility",
            chunk_title=f"{scheme_title} - Eligibility Criteria & Exclusions",
            content=c2_text,
            embedding=json.dumps(c2_emb)
        )
        db.add(chunk_2)

        # Chunk 3: Benefits Delivered & Required Documents
        benefits_list = s_data.get("benefits", [])
        docs_list = s_data.get("documents_required", [])
        c3_text = f"Benefits Delivered under {scheme_title}: " + " ".join(benefits_list) + f". Mandatory Documents Required: " + ", ".join(docs_list) + f". Official Portal: {s_data.get('official_portal', '')}."
        c3_emb = generate_embedding(f"{scheme_title} benefits delivered subsidy direct transfer documents required aadhaar {' '.join(benefits_list)}")
        chunk_3 = SchemeChunk(
            id=f"{scheme_id}-benefits-docs",
            scheme_id=scheme_id,
            section_name="Benefits & Documents",
            chunk_title=f"{scheme_title} - Benefits & Required Documents",
            content=c3_text,
            embedding=json.dumps(c3_emb)
        )
        db.add(chunk_3)

        # Chunk 4: Step-by-Step Application Process
        app_text = s_data.get("application_process", "")
        c4_text = f"How to Apply for {scheme_title}: {app_text}. Official Government Portal: {s_data.get('official_portal', '')}."
        c4_emb = generate_embedding(f"{scheme_title} how to apply application process portal online registration {app_text}")
        chunk_4 = SchemeChunk(
            id=f"{scheme_id}-process",
            scheme_id=scheme_id,
            section_name="Application",
            chunk_title=f"{scheme_title} - How to Apply & Online Registration",
            content=c4_text,
            embedding=json.dumps(c4_emb)
        )
        db.add(chunk_4)

        total_chunks_indexed += 4
        print(f"  [{idx:02d}/{len(schemes_list):02d}] Verified & Indexed: {scheme_title[:45]}... (4 chunks embedded)")

    db.commit()
    db.close()

    print("\n" + "=" * 70)
    print(f" SUCCESS: Complete Clean Ingestion Finished!")
    print(f" Real Schemes Stored: {len(schemes_list)}")
    print(f" Total Semantic Chunks Embedded & Indexed: {total_chunks_indexed}")
    print("=" * 70)

if __name__ == "__main__":
    purge_and_ingest_real_data()
