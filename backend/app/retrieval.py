import re
import math
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from .models import Scheme, SchemeChunk
from .embedding import generate_embedding, cosine_similarity
from .config import settings

def normalize_text(text: str) -> List[str]:
    # Extract lowercased alphanumeric tokens
    tokens = re.findall(r'\b[a-zA-Z0-9_]+\b', text.lower())
    # Filter common stop words
    stopwords = {"the", "a", "an", "in", "on", "of", "and", "or", "is", "for", "to", "with", "at", "by", "from", "i", "my", "we", "me", "am"}
    return [t for t in tokens if t not in stopwords]

def bm25_lexical_score(query_tokens: List[str], doc_tokens: List[str], avg_dl: float = 80.0, k1: float = 1.5, b: float = 0.75) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    dl = len(doc_tokens)
    score = 0.0
    doc_token_counts = {}
    for t in doc_tokens:
        doc_token_counts[t] = doc_token_counts.get(t, 0) + 1
        
    for q in query_tokens:
        tf = doc_token_counts.get(q, 0)
        if tf > 0:
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (dl / avg_dl))
            score += (numerator / denominator)
    return score

def hybrid_search(
    db: Session,
    query: str,
    top_k: int = 5,
    category_filter: str = None,
    fts_weight: float = None,
    dense_weight: float = None,
    rrf_k: int = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Executes hybrid retrieval:
    1. Lexical search across chunks
    2. Dense semantic vector search across chunks
    3. Reciprocal Rank Fusion (RRF) to merge and rerank results
    """
    fts_w = fts_weight if fts_weight is not None else settings.FTS_WEIGHT
    dense_w = dense_weight if dense_weight is not None else settings.DENSE_WEIGHT
    k_rrf = rrf_k if rrf_k is not None else settings.RRF_K

    # 1. Fetch chunks (optionally filter by scheme category)
    query_orm = db.query(SchemeChunk).join(Scheme)
    if category_filter:
        query_orm = query_orm.filter(Scheme.category.ilike(f"%{category_filter}%"))
    all_chunks = query_orm.all()

    if not all_chunks:
        return [], []

    # 2. Query tokens & Query embedding
    query_tokens = normalize_text(query)
    query_embedding = generate_embedding(query)

    # 3. Score lexical & stable feature-hash similarity.
    scored_items = []
    for chunk in all_chunks:
        # Lexical score
        chunk_text = f"{chunk.chunk_title} {chunk.section_name} {chunk.content} {chunk.scheme.title} {chunk.scheme.tags}"
        chunk_tokens = normalize_text(chunk_text)
        lex_score = bm25_lexical_score(query_tokens, chunk_tokens)
        
        # Exact keyword boost (e.g. "farmer", "ayushman", "scholarship", "girl", "tool")
        for q in query_tokens:
            if q in chunk.scheme.title.lower() or q in chunk.chunk_title.lower():
                lex_score += 2.0
            if q in (chunk.scheme.tags or "").lower():
                lex_score += 1.5

        # Recompute from source text: existing stored vectors may use a different hash seed.
        chunk_emb = generate_embedding(chunk_text)
        if chunk_emb:
            dense_score = cosine_similarity(query_embedding, chunk_emb)
        else:
            dense_score = 0.0

        scored_items.append({
            "chunk": chunk,
            "lexical_score": float(lex_score),
            "dense_score": float(dense_score)
        })

    # 4. Rank by Lexical
    ranked_by_lex = sorted(
        scored_items,
        key=lambda x: (-x["lexical_score"], x["chunk"].id),
    )
    lex_ranks = {item["chunk"].id: rank + 1 for rank, item in enumerate(ranked_by_lex)}

    # 5. Rank by Dense
    ranked_by_dense = sorted(
        scored_items,
        key=lambda x: (-x["dense_score"], x["chunk"].id),
    )
    dense_ranks = {item["chunk"].id: rank + 1 for rank, item in enumerate(ranked_by_dense)}

    # 6. Reciprocal Rank Fusion (RRF)
    for item in scored_items:
        c_id = item["chunk"].id
        r_lex = lex_ranks[c_id]
        r_dense = dense_ranks[c_id]
        
        rrf = (fts_w / (k_rrf + r_lex)) + (dense_w / (k_rrf + r_dense))
        item["rrf_score"] = float(rrf)

    # Sort final results by RRF score
    ranked_items = sorted(
        scored_items,
        key=lambda x: (
            -x["rrf_score"],
            -x["lexical_score"],
            -x["dense_score"],
            x["chunk"].id,
        ),
    )

    # Avoid letting multiple facets from one scheme crowd all other schemes out.
    final_ranked = []
    scheme_chunk_counts = {}
    for item in ranked_items:
        scheme_id = item["chunk"].scheme_id
        if scheme_chunk_counts.get(scheme_id, 0) >= 2:
            continue
        final_ranked.append(item)
        scheme_chunk_counts[scheme_id] = scheme_chunk_counts.get(scheme_id, 0) + 1
        if len(final_ranked) == top_k:
            break

    # Structure returned chunks
    retrieved_chunks = []
    matched_scheme_ids = []
    for item in final_ranked:
        chunk = item["chunk"]
        if chunk.scheme_id not in matched_scheme_ids:
            matched_scheme_ids.append(chunk.scheme_id)
        retrieved_chunks.append({
            "id": chunk.id,
            "scheme_id": chunk.scheme_id,
            "scheme_title": chunk.scheme.title,
            "section_name": chunk.section_name,
            "chunk_title": chunk.chunk_title,
            "content": chunk.content,
            "lexical_score": round(item["lexical_score"], 4),
            "dense_score": round(item["dense_score"], 4),
            "rrf_score": round(item["rrf_score"], 6),
            "official_portal": chunk.scheme.official_portal
        })

    # Fetch unique matched schemes
    matched_schemes = []
    if matched_scheme_ids:
        schemes = db.query(Scheme).filter(Scheme.id.in_(matched_scheme_ids)).all()
        schemes_by_id = {scheme.id: scheme for scheme in schemes}
        matched_schemes = [schemes_by_id[scheme_id].to_dict() for scheme_id in matched_scheme_ids]

    return retrieved_chunks, matched_schemes
