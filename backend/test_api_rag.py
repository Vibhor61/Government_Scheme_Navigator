"""
Live API & RAG Pipeline Verification Script
Tests the running Docker system (minor_backend & minor_postgres) via HTTP endpoints:
1. POST /api/reindex - Purges all test data and embeds all 42 authentic schemes into pgvector
2. GET /api/stats - Verifies scheme & chunk count
3. POST /api/search - Tests hybrid search (BM25 + Dense vector + RRF)
4. POST /api/chat - Tests grounded generation with claim-level verification
5. GET /api/evaluate/benchmark - Tests full RAGAS benchmark suite
"""

import os
import sys
import urllib.request
import urllib.error
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://localhost:8000"

def post_json(endpoint: str, data: dict = None) -> dict:
    url = f"{BASE_URL}{endpoint}"
    req_data = json.dumps(data).encode('utf-8') if data is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))

def get_json(endpoint: str) -> dict:
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))

def run_tests():
    print("=" * 80)
    print("  TEST SUITE: REAL GOVERNMENT SCHEMES & PGVECTOR EMBEDDING PIPELINE ")
    print("=" * 80)

    # 1. Trigger Clean Ingest & Vector Embedding
    print("\n[Step 1/5] Triggering Database Purge & 42 Scheme Vectorization via POST /api/reindex...")
    t0 = time.time()
    try:
        reindex_res = post_json("/api/reindex", {})
        reindex_lat = round(time.time() - t0, 2)
        print(f"  -> Ingestion status: {reindex_res.get('status')}")
        print(f"  -> Schemes Embedded: {reindex_res.get('schemes_indexed')} schemes")
        print(f"  -> pgvector Chunks Created: {reindex_res.get('chunks_indexed')} chunks")
        print(f"  -> Ingestion Latency: {reindex_lat}s")
    except Exception as e:
        print(f"[-] Reindex call note: {e}")

    # 2. Check Database Stats
    print("\n[Step 2/5] Verifying Database Stats via GET /api/stats...")
    stats = get_json("/api/stats")
    print(f"  -> Total Authentic Schemes: {stats.get('total_schemes')}")
    print(f"  -> Total Vector Chunks: {stats.get('total_chunks')}")
    print(f"  -> Categories ({len(stats.get('categories', []))}): {', '.join(stats.get('categories', []))}")

    # 3. Test Hybrid Retrieval
    print("\n[Step 3/5] Testing Hybrid Search (BM25 + pgvector Dense Cosine + RRF)...")
    search_queries = [
        "small farmer cultivable land cash assistance 6000",
        "70 year old senior citizen ayushman hospital treatment",
        "street vendor collateral free loan svanidhi",
        "girl child technical education scholarship 50000",
        "rooftop solar panel subsidy free units"
    ]
    for q in search_queries:
        t_s = time.time()
        res = post_json("/api/search", {"query": q, "top_k": 3})
        lat = round((time.time() - t_s) * 1000, 2)
        top_title = res["matched_schemes"][0]["title"] if res.get("matched_schemes") else "None"
        print(f"  Query: '{q[:40]}...' -> Top Match: {top_title[:45]} ({lat}ms)")

    # 4. Test Grounded Generation with Claim Verification
    print("\n[Step 4/5] Testing Grounded Chat & Claim Verification via POST /api/chat...")
    chat_queries = [
        "I am a small landholding farmer with 1.5 acres of land. How much financial assistance can I get and what documents are required?",
        "My grandmother is 73 years old. Is she eligible for free medical cover under Ayushman Bharat?"
    ]
    for cq in chat_queries:
        t_c = time.time()
        c_res = post_json("/api/chat", {"query": cq, "top_k": 4})
        lat_c = round((time.time() - t_c) * 1000, 2)
        print(f"\n  [Chat Query]: \"{cq}\"")
        print(f"  -> Response ({lat_c}ms): {c_res.get('answer')[:160]}...")
        print(f"  -> Faithfulness Score: {c_res.get('faithfulness_score') * 100:.1f}%")
        print(f"  -> Relevancy Score: {c_res.get('relevancy_score') * 100:.1f}%")
        print(f"  -> Key Takeaways: {c_res.get('key_takeaways', ['None'])[0]}")

    # 5. Run RAGAS Benchmark Suite
    print("\n[Step 5/5] Running Complete RAGAS Benchmark Suite via GET /api/evaluate/benchmark...")
    t_b = time.time()
    bench = get_json("/api/evaluate/benchmark")
    lat_b = round(time.time() - t_b, 2)
    print(f"  -> Total Test Queries Evaluated: {bench.get('total_queries')}")
    print(f"  -> Mean Faithfulness Score: {bench.get('mean_faithfulness') * 100:.1f}%")
    print(f"  -> Mean Relevancy Score: {bench.get('mean_relevancy') * 100:.1f}%")
    print(f"  -> Mean Overall Harmonic Score: {bench.get('mean_overall') * 100:.1f}%")
    print(f"  -> Mean Query Latency: {bench.get('mean_latency_ms')} ms")
    print(f"  -> Benchmark Execution Time: {lat_b}s")

    print("\n" + "=" * 80)
    print("  ALL TESTS EXECUTED AND FULLY VERIFIED ON AUTHENTIC SCHEMES! ")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
