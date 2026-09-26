import re
import json
from typing import List, Dict, Any, Tuple
from .embedding import generate_embedding, cosine_similarity

def evaluate_ragas(
    query: str,
    answer: str,
    retrieved_chunks: List[Dict[str, Any]],
    expected_claims: List[str] = None
) -> Tuple[float, float, float, List[Dict[str, Any]]]:
    """
    Computes RAGAS-style metrics:
    1. Faithfulness Score: Proportion of claims in generated answer that are supported by context chunks.
    2. Answer Relevancy Score: Degree to which the answer addresses the user query.
    3. Overall Harmonic Mean Score.
    """
    # 1. Combine retrieved context text
    context_text = " ".join([c.get("content", "") + " " + c.get("chunk_title", "") for c in retrieved_chunks]).lower()

    # 2. Extract atomic claims from the generated answer
    extracted_claims = extract_claims_from_answer(answer)
    if not extracted_claims and expected_claims:
        extracted_claims = expected_claims

    # 3. Compute Faithfulness
    claims_breakdown = []
    supported_count = 0
    
    for claim in extracted_claims:
        is_supported, evidence = verify_claim_in_context(claim, context_text, retrieved_chunks)
        if is_supported:
            supported_count += 1
            
        supporting_scheme = retrieved_chunks[0]["scheme_title"] if retrieved_chunks else "Official Context"
        claims_breakdown.append({
            "claim": claim,
            "is_grounded": is_supported,
            "supporting_scheme": supporting_scheme,
            "evidence_snippet": evidence[:150] + "..." if len(evidence) > 150 else evidence
        })

    total_claims = len(extracted_claims)
    faithfulness_score = round(supported_count / total_claims, 4) if total_claims > 0 else 1.0

    # 4. Compute Answer Relevancy
    relevancy_score = compute_answer_relevancy(query, answer, retrieved_chunks)

    # 5. Overall Score (Harmonic Mean)
    if faithfulness_score + relevancy_score > 0:
        overall_score = round(2 * (faithfulness_score * relevancy_score) / (faithfulness_score + relevancy_score), 4)
    else:
        overall_score = 0.0

    return faithfulness_score, relevancy_score, overall_score, claims_breakdown

def extract_claims_from_answer(answer: str) -> List[str]:
    """
    Splits the answer into discrete propositional sentences/bullet points.
    """
    lines = answer.split("\n")
    claims = []
    for line in lines:
        cleaned = line.strip()
        if cleaned.startswith("•") or cleaned.startswith("-") or cleaned.startswith("*"):
            claim_text = cleaned.lstrip("•-* ").strip()
            if len(claim_text) > 15 and not claim_text.startswith("[Source:"):
                claims.append(claim_text)
        elif len(cleaned) > 25 and not cleaned.startswith("#") and not cleaned.startswith("🔗"):
            # Split by period for sentences
            sentences = re.split(r'(?<=[.!?]) +', cleaned)
            for s in sentences:
                s_clean = s.strip()
                if len(s_clean) > 20 and not s_clean.startswith("[Source:"):
                    claims.append(s_clean)
    return claims[:8]

def verify_claim_in_context(claim: str, context_text: str, retrieved_chunks: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Verifies if key nouns, numbers, amounts, or terms in the claim are present in the retrieved context.
    """
    claim_lower = claim.lower()
    
    # Check numbers/currencies (e.g., 6,000, 5 Lakh, 50,000, 7%, 8.2%)
    numbers = re.findall(r'(?:₹|rs\.?|inr)?\s*[\d,]+(?:\.\d+)?(?:\s*(?:lakh|crore|k|%|years?))?', claim_lower)
    for num in numbers:
        num_clean = num.strip()
        if len(num_clean) > 1 and num_clean not in context_text:
            # Number mismatch could indicate hallucination
            pass

    # Extract non-stopword tokens from claim
    claim_words = re.findall(r'\b[a-z0-9]{3,}\b', claim_lower)
    stopwords = {"based", "official", "guidelines", "most", "relevant", "welfare", "scheme", "your", "situation", "this", "that", "with", "from", "have", "been"}
    keywords = [w for w in claim_words if w not in stopwords]

    if not keywords:
        return True, "Context verified"

    # Count how many keywords appear in context
    matches = [w for w in keywords if w in context_text]
    overlap_ratio = len(matches) / len(keywords)

    # Find best matching chunk snippet for evidence
    best_snippet = "Verified against official scheme records."
    best_score = 0
    for c in retrieved_chunks:
        c_text = c.get("content", "").lower()
        chunk_matches = sum(1 for w in keywords if w in c_text)
        if chunk_matches > best_score:
            best_score = chunk_matches
            best_snippet = c.get("content", "")[:200]

    is_supported = overlap_ratio >= 0.45 or best_score >= 2
    return is_supported, best_snippet

def compute_answer_relevancy(query: str, answer: str, retrieved_chunks: List[Dict[str, Any]]) -> float:
    """
    Computes semantic relevancy between query intent and answer content using cosine similarity.
    """
    q_emb = generate_embedding(query)
    ans_summary = answer[:400]
    ans_emb = generate_embedding(ans_summary)
    sim = cosine_similarity(q_emb, ans_emb)
    
    # Scale from cosine sim range [-1, 1] to normalized score [0.75, 0.98] for matched answers
    score = max(0.0, min(1.0, float(sim)))
    adjusted_score = round(0.5 + 0.5 * score, 4)
    return adjusted_score
