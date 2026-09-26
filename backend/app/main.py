import os
import json
import time
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from .config import settings
from .database import engine, get_db, Base
from .models import Scheme, SchemeChunk, EvaluationLog
from .schemas import (
    SearchQueryRequest, SearchResponse, RetrievedChunk, SchemeSummary, SchemeDetail,
    ChatQueryRequest, GroundedAnswerResponse, ClaimVerification,
    EvaluationRequest, EvaluationResult, BenchmarkRunResponse
)
from .retrieval import hybrid_search
from .generator import generate_grounded_response
from .evaluation import evaluate_ragas
from .embedding import generate_embedding, generate_embeddings_batch

# Initialize tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A Retrieval-Augmented System for Indian Government Welfare Scheme Discovery and Eligibility Awareness"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """Auto-seed database if empty on startup"""
    db = next(get_db())
    try:
        count = db.query(Scheme).count()
        if count == 0:
            print("Database empty. Seeding schemes and vector chunks...")
            seed_database(db)
    finally:
        db.close()

def seed_database(db: Session):
    data_path = os.path.join(os.path.dirname(__file__), "data", "schemes_data.json")
    if not os.path.exists(data_path):
        return
        
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for s_data in data.get("schemes", []):
        scheme = Scheme(
            id=s_data["id"],
            title=s_data["title"],
            short_name=s_data.get("short_name"),
            category=s_data["category"],
            ministry=s_data["ministry"],
            target_beneficiaries=s_data.get("target_beneficiaries", ""),
            financial_assistance=s_data.get("financial_assistance", ""),
            eligibility_criteria=json.dumps(s_data.get("eligibility_criteria", [])),
            benefits=json.dumps(s_data.get("benefits", [])),
            documents_required=json.dumps(s_data.get("documents_required", [])),
            application_process=s_data.get("application_process", ""),
            official_portal=s_data.get("official_portal", ""),
            tags=json.dumps(s_data.get("tags", []))
        )
        db.merge(scheme)
        
        # Create chunk 1: Overview & Financial
        chunk_overview = SchemeChunk(
            id=f"{s_data['id']}-overview",
            scheme_id=s_data["id"],
            section_name="Overview",
            chunk_title=f"{s_data['title']} - Overview & Financial Assistance",
            content=f"Scheme: {s_data['title']}. Ministry: {s_data['ministry']}. Target: {s_data.get('target_beneficiaries','')}. Financial Assistance: {s_data.get('financial_assistance','')}. Tags: {', '.join(s_data.get('tags',[]))}",
            embedding=json.dumps(generate_embedding(f"{s_data['title']} {s_data.get('financial_assistance','')} {s_data.get('target_beneficiaries','')} {s_data.get('category','')}"))
        )
        db.merge(chunk_overview)

        # Create chunk 2: Eligibility Criteria
        elig_text = " ".join(s_data.get("eligibility_criteria", []))
        chunk_elig = SchemeChunk(
            id=f"{s_data['id']}-eligibility",
            scheme_id=s_data["id"],
            section_name="Eligibility",
            chunk_title=f"{s_data['title']} - Eligibility Criteria & Exclusions",
            content=f"Eligibility criteria for {s_data['title']}: {elig_text}",
            embedding=json.dumps(generate_embedding(f"{s_data['title']} eligibility conditions criteria {elig_text}"))
        )
        db.merge(chunk_elig)

        # Create chunk 3: Benefits & Application Process
        benefits_text = " ".join(s_data.get("benefits", []))
        docs_text = " ".join(s_data.get("documents_required", []))
        chunk_app = SchemeChunk(
            id=f"{s_data['id']}-process",
            scheme_id=s_data["id"],
            section_name="Application & Benefits",
            chunk_title=f"{s_data['title']} - Benefits, Documents & How to Apply",
            content=f"Benefits: {benefits_text}. Required Documents: {docs_text}. Application Procedure: {s_data.get('application_process','')}. Official portal: {s_data.get('official_portal','')}",
            embedding=json.dumps(generate_embedding(f"{s_data['title']} benefits application process apply documents {benefits_text}"))
        )
        db.merge(chunk_app)

    db.commit()
    print("Seeding completed successfully!")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total_schemes = db.query(Scheme).count()
    total_chunks = db.query(SchemeChunk).count()
    total_logs = db.query(EvaluationLog).count()
    categories = db.query(Scheme.category).distinct().all()
    
    return {
        "total_schemes": total_schemes,
        "total_chunks": total_chunks,
        "total_evaluation_logs": total_logs,
        "categories": [c[0] for c in categories if c[0]],
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "hybrid_weights": {
            "lexical_weight": settings.FTS_WEIGHT,
            "dense_weight": settings.DENSE_WEIGHT,
            "rrf_k": settings.RRF_K
        }
    }

@app.post("/api/reindex")
def reindex_database_endpoint(db: Session = Depends(get_db)):
    """Purge all old/test records and re-index only authentic government schemes"""
    # 1. Purge old records
    db.query(SchemeChunk).delete()
    db.query(Scheme).delete()
    db.query(EvaluationLog).delete()
    db.commit()

    # 2. Re-seed with authentic data
    data_path = os.path.join(os.path.dirname(__file__), "data", "schemes_data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Authentic data catalog not found")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    schemes_list = data.get("schemes", [])
    total_chunks = 0

    for s_data in schemes_list:
        s_id = s_data["id"]
        scheme = Scheme(
            id=s_id,
            title=s_data["title"],
            short_name=s_data.get("short_name"),
            category=s_data["category"],
            ministry=s_data["ministry"],
            target_beneficiaries=s_data.get("target_beneficiaries", ""),
            financial_assistance=s_data.get("financial_assistance", ""),
            eligibility_criteria=json.dumps(s_data.get("eligibility_criteria", [])),
            benefits=json.dumps(s_data.get("benefits", [])),
            documents_required=json.dumps(s_data.get("documents_required", [])),
            application_process=s_data.get("application_process", ""),
            official_portal=s_data.get("official_portal", ""),
            tags=json.dumps(s_data.get("tags", []))
        )
        db.add(scheme)

        # Chunk 1: Overview
        c1_text = f"Scheme: {s_data['title']}. Ministry: {s_data['ministry']}. Target Beneficiaries: {s_data.get('target_beneficiaries','')}. Financial Assistance: {s_data.get('financial_assistance','')}. Tags: {', '.join(s_data.get('tags',[]))}"
        db.add(SchemeChunk(
            id=f"{s_id}-overview",
            scheme_id=s_id,
            section_name="Overview",
            chunk_title=f"{s_data['title']} - Overview & Financial Scope",
            content=c1_text,
            embedding=json.dumps(generate_embedding(f"{s_data['title']} {s_data.get('financial_assistance','')} {s_data.get('target_beneficiaries','')} {s_data.get('category','')}"))
        ))

        # Chunk 2: Eligibility
        elig_text = " ".join(s_data.get("eligibility_criteria", []))
        db.add(SchemeChunk(
            id=f"{s_id}-eligibility",
            scheme_id=s_id,
            section_name="Eligibility",
            chunk_title=f"{s_data['title']} - Eligibility Criteria & Exclusions",
            content=f"Official Eligibility criteria for {s_data['title']}: {elig_text}",
            embedding=json.dumps(generate_embedding(f"{s_data['title']} eligibility conditions criteria exclusions {elig_text}"))
        ))

        # Chunk 3: Benefits & Documents
        bens_text = " ".join(s_data.get("benefits", []))
        docs_text = " ".join(s_data.get("documents_required", []))
        db.add(SchemeChunk(
            id=f"{s_id}-benefits-docs",
            scheme_id=s_id,
            section_name="Benefits & Documents",
            chunk_title=f"{s_data['title']} - Benefits & Required Documents",
            content=f"Benefits: {bens_text}. Mandatory Documents: {docs_text}. Portal: {s_data.get('official_portal','')}",
            embedding=json.dumps(generate_embedding(f"{s_data['title']} benefits documents required aadhaar ration {bens_text}"))
        ))

        # Chunk 4: Application Procedure
        app_proc = s_data.get("application_process", "")
        db.add(SchemeChunk(
            id=f"{s_id}-process",
            scheme_id=s_id,
            section_name="Application",
            chunk_title=f"{s_data['title']} - Application Process & Portal",
            content=f"How to Apply for {s_data['title']}: {app_proc}. Official Portal: {s_data.get('official_portal','')}",
            embedding=json.dumps(generate_embedding(f"{s_data['title']} how to apply online application registration {app_proc}"))
        ))

        total_chunks += 4

    db.commit()

    return {
        "status": "success",
        "message": "All old/test embeddings wiped cleanly. Authentic schemes ingested & embedded.",
        "schemes_indexed": len(schemes_list),
        "chunks_indexed": total_chunks
    }

@app.get("/api/schemes", response_model=List[SchemeDetail])
def list_schemes(category: Optional[str] = None, search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Scheme)
    if category:
        query = query.filter(Scheme.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(
            (Scheme.title.ilike(f"%{search}%")) | 
            (Scheme.tags.ilike(f"%{search}%")) |
            (Scheme.target_beneficiaries.ilike(f"%{search}%"))
        )
    schemes = query.all()
    return [s.to_dict() for s in schemes]

@app.get("/api/schemes/{scheme_id}", response_model=SchemeDetail)
def get_scheme(scheme_id: str, db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme.to_dict()

@app.post("/api/search", response_model=SearchResponse)
def search_endpoint(req: SearchQueryRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    retrieved_chunks, matched_schemes = hybrid_search(
        db=db,
        query=req.query,
        top_k=req.top_k,
        category_filter=req.category
    )
    latency = round((time.time() - start_time) * 1000, 2)
    
    return {
        "query": req.query,
        "total_results": len(retrieved_chunks),
        "retrieved_chunks": retrieved_chunks,
        "matched_schemes": matched_schemes,
        "latency_ms": latency
    }

@app.post("/api/chat", response_model=GroundedAnswerResponse)
def chat_endpoint(req: ChatQueryRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    
    # 1. Hybrid Retrieval
    retrieved_chunks, matched_schemes = hybrid_search(
        db=db,
        query=req.query,
        top_k=req.top_k,
        category_filter=req.category
    )
    
    # 2. Grounded Generation
    gen_result = generate_grounded_response(
        query=req.query,
        retrieved_chunks=retrieved_chunks,
        matched_schemes=matched_schemes
    )
    
    answer_text = gen_result["answer"]
    
    # 3. RAGAS Evaluation
    faithfulness_score, relevancy_score, overall_score, claims_breakdown = evaluate_ragas(
        query=req.query,
        answer=answer_text,
        retrieved_chunks=retrieved_chunks
    )
    
    latency = round((time.time() - start_time) * 1000, 2)
    
    # 4. Save evaluation log
    try:
        log_entry = EvaluationLog(
            query=req.query,
            retrieved_chunks_json=json.dumps(retrieved_chunks),
            answer=answer_text,
            faithfulness_score=faithfulness_score,
            relevancy_score=relevancy_score,
            overall_score=overall_score,
            claims_breakdown_json=json.dumps(claims_breakdown),
            latency_ms=latency
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        print(f"Log save warning: {e}")

    return {
        "query": req.query,
        "answer": answer_text,
        "key_takeaways": gen_result.get("key_takeaways", []),
        "eligibility_assessment": gen_result.get("eligibility_assessment", []),
        "citations": gen_result.get("citations", []),
        "retrieved_chunks": retrieved_chunks,
        "faithfulness_score": faithfulness_score,
        "relevancy_score": relevancy_score,
        "claims_breakdown": claims_breakdown,
        "latency_ms": latency
    }

@app.post("/api/evaluate", response_model=EvaluationResult)
def evaluate_endpoint(req: EvaluationRequest):
    start_time = time.time()
    chunks = [{"content": c, "scheme_title": "Provided Context"} for c in req.context_chunks]
    faithfulness, relevancy, overall, claims = evaluate_ragas(
        query=req.query,
        answer=req.answer,
        retrieved_chunks=chunks
    )
    latency = round((time.time() - start_time) * 1000, 2)
    return {
        "query": req.query,
        "faithfulness_score": faithfulness,
        "relevancy_score": relevancy,
        "overall_score": overall,
        "claims_breakdown": claims,
        "latency_ms": latency
    }

@app.get("/api/evaluate/benchmark", response_model=BenchmarkRunResponse)
def run_benchmark_endpoint(db: Session = Depends(get_db)):
    test_file = os.path.join(os.path.dirname(__file__), "data", "test_questions.json")
    if not os.path.exists(test_file):
        raise HTTPException(status_code=404, detail="Test set file not found")
        
    with open(test_file, "r", encoding="utf-8") as f:
        test_data = json.load(f)
        
    test_set = test_data.get("test_set", [])
    results = []
    faith_scores = []
    rel_scores = []
    latencies = []
    
    for item in test_set:
        t0 = time.time()
        retrieved_chunks, matched_schemes = hybrid_search(
            db=db,
            query=item["query"],
            top_k=4
        )
        gen_res = generate_grounded_response(
            query=item["query"],
            retrieved_chunks=retrieved_chunks,
            matched_schemes=matched_schemes
        )
        f_score, r_score, o_score, claims = evaluate_ragas(
            query=item["query"],
            answer=gen_res["answer"],
            retrieved_chunks=retrieved_chunks,
            expected_claims=item.get("ground_truth_claims")
        )
        lat = round((time.time() - t0) * 1000, 2)
        
        faith_scores.append(f_score)
        rel_scores.append(r_score)
        latencies.append(lat)
        
        results.append({
            "id": item["id"],
            "query": item["query"],
            "expected_schemes": item.get("expected_schemes", []),
            "retrieved_schemes": [s["id"] for s in matched_schemes],
            "faithfulness_score": f_score,
            "relevancy_score": r_score,
            "overall_score": o_score,
            "claims_count": len(claims),
            "latency_ms": lat
        })

    mean_f = round(sum(faith_scores) / len(faith_scores), 4) if faith_scores else 1.0
    mean_r = round(sum(rel_scores) / len(rel_scores), 4) if rel_scores else 1.0
    mean_o = round(2 * (mean_f * mean_r) / (mean_f + mean_r), 4) if (mean_f + mean_r) > 0 else 1.0
    mean_l = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

    return {
        "total_queries": len(test_set),
        "mean_faithfulness": mean_f,
        "mean_relevancy": mean_r,
        "mean_overall": mean_o,
        "mean_latency_ms": mean_l,
        "results": results
    }

@app.get("/api/evaluation/history")
def get_evaluation_history(limit: int = 20, db: Session = Depends(get_db)):
    logs = db.query(EvaluationLog).order_by(EvaluationLog.created_at.desc()).limit(limit).all()
    return [log.to_dict() for log in logs]

# Serve static UI directly at root
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    @app.get("/", response_class=HTMLResponse)
    def read_root():
        index_path = os.path.join(static_dir, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    app.mount("/static", StaticFiles(directory=static_dir), name="static")
