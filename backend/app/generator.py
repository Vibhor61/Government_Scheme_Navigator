import os
import re
import json
import httpx
from typing import List, Dict, Any, Tuple
from .config import settings

GROUNDED_SYSTEM_PROMPT = """You are the official Citizen Rights and Government Scheme Navigator AI.
Your purpose is to provide clear, helpful, and strictly fact-grounded information on Indian government welfare schemes.

CRITICAL GROUNDING RULES:
1. Answer ONLY using facts directly stated in the provided official scheme context chunks below.
2. DO NOT fabricate, guess, or assume eligibility criteria, benefit amounts, or conditions not present in the context.
3. Explicitly cite the source scheme name for every major claim (e.g., [PM-KISAN, Eligibility]).
4. State eligibility conditions clearly, point out any exclusion criteria, and explain step-by-step how the citizen should apply.
5. Provide structured markdown with bold headings, bullet points, and required documents.
"""

ACTIVE_GROQ_MODELS = [
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "llama3-8b-8192",
    "mixtral-8x7b-32768"
]

def generate_grounded_response(
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
    matched_schemes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    if not retrieved_chunks:
        return {
            "answer": "No matching government welfare schemes were found for your query. Please try searching with different keywords such as 'scholarship', 'farmer support', 'health insurance', or 'business loan'.",
            "key_takeaways": ["No matching scheme identified in the database."],
            "eligibility_assessment": [],
            "citations": []
        }

    context_str = ""
    for idx, c in enumerate(retrieved_chunks):
        context_str += f"\n[Document {idx+1}: {c['scheme_title']} | Section: {c['section_name']}]\n{c['content']}\n"

    # 1. Try Groq API with multi-model fallback
    if settings.GROQ_API_KEY:
        groq_resp = _call_groq_api(query, context_str, matched_schemes)
        if groq_resp:
            return groq_resp

    # 2. Try Gemini API if configured
    if settings.GEMINI_API_KEY:
        gemini_resp = _call_gemini_api(query, context_str, matched_schemes)
        if gemini_resp:
            return gemini_resp

    # 3. High-precision grounded synthesizer fallback
    return _synthesize_grounded_response(query, retrieved_chunks, matched_schemes)

def _call_groq_api(query: str, context: str, matched_schemes: List[Dict[str, Any]]) -> Dict[str, Any]:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"OFFICIAL VERIFIED SCHEME CONTEXT:\n{context}\n\nCITIZEN INQUIRY / SITUATION: {query}\n\nProvide a comprehensive, fact-grounded response citing official schemes."

    for model_name in ACTIVE_GROQ_MODELS:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": GROUNDED_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 1024
        }
        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    raw_answer = data["choices"][0]["message"]["content"]
                    
                    citations = []
                    for s in matched_schemes[:3]:
                        citations.append({
                            "scheme_id": s["id"],
                            "title": s["title"],
                            "ministry": s["ministry"],
                            "category": s["category"],
                            "official_portal": s.get("official_portal")
                        })
                    
                    lines = [l.strip() for l in raw_answer.split("\n") if l.strip().startswith("•") or l.strip().startswith("-")]
                    key_takeaways = [l.lstrip("•- ") for l in lines[:3]]
                    if not key_takeaways and matched_schemes:
                        key_takeaways.append(matched_schemes[0].get("financial_assistance", "Financial benefit available"))

                    return {
                        "answer": raw_answer,
                        "key_takeaways": key_takeaways,
                        "eligibility_assessment": [],
                        "citations": citations
                    }
                else:
                    print(f"Groq model {model_name} returned {res.status_code}: {res.text}. Trying next model...")
        except Exception as e:
            print(f"Groq model {model_name} call error: {e}. Trying next model...")

    return None

def _call_gemini_api(query: str, context: str, matched_schemes: List[Dict[str, Any]]) -> Dict[str, Any]:
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"{GROUNDED_SYSTEM_PROMPT}\n\nCONTEXT:\n{context}\n\nCITIZEN QUERY: {query}"
                }]
            }]
        }
        with httpx.Client(timeout=8.0) as client:
            res = client.post(url, json=payload)
            if res.status_code == 200:
                data = res.json()
                ans = data["candidates"][0]["content"]["parts"][0]["text"]
                citations = [{
                    "scheme_id": s["id"],
                    "title": s["title"],
                    "ministry": s["ministry"],
                    "category": s["category"],
                    "official_portal": s.get("official_portal")
                } for s in matched_schemes[:3]]
                return {
                    "answer": ans,
                    "key_takeaways": ["Verified via Google Gemini API"],
                    "eligibility_assessment": [],
                    "citations": citations
                }
    except Exception as e:
        print(f"Gemini API error: {e}")
    return None

def _synthesize_grounded_response(
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
    matched_schemes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    primary_scheme = matched_schemes[0] if matched_schemes else None
    scheme_title = primary_scheme['title'] if primary_scheme else retrieved_chunks[0]['scheme_title']

    eligibility_items = primary_scheme.get('eligibility_criteria', []) if primary_scheme else []
    benefit_items = primary_scheme.get('benefits', []) if primary_scheme else []
    docs_items = primary_scheme.get('documents_required', []) if primary_scheme else []
    app_process = primary_scheme.get('application_process', '') if primary_scheme else ''
    fin_assist = primary_scheme.get('financial_assistance', '') if primary_scheme else ''
    portal = primary_scheme.get('official_portal', '') if primary_scheme else ''

    answer_parts = []
    answer_parts.append(f"Based on official government guidelines, the most relevant welfare scheme for your inquiry is **{scheme_title}**.")
    
    if fin_assist:
        answer_parts.append(f"\n### 💰 Financial Assistance & Scope\n{fin_assist} *[Source: {scheme_title}]*")
        
    if eligibility_items:
        answer_parts.append("\n### 🎯 Key Eligibility Conditions")
        for e in eligibility_items:
            answer_parts.append(f"• {e}")

    if benefit_items:
        answer_parts.append("\n### ✨ Core Benefits Delivered")
        for b in benefit_items:
            answer_parts.append(f"• {b}")

    if docs_items:
        answer_parts.append("\n### 📋 Documents Required")
        for d in docs_items:
            answer_parts.append(f"• {d}")

    if app_process:
        answer_parts.append(f"\n### 📝 Step-by-Step Application Process\n{app_process}")

    if portal:
        answer_parts.append(f"\n🔗 **Official Portal:** [{portal}]({portal})")

    full_answer = "\n".join(answer_parts)

    key_takeaways = []
    if fin_assist:
        key_takeaways.append(fin_assist)
    if eligibility_items:
        key_takeaways.append(f"Eligibility: {eligibility_items[0][:120]}...")

    citations = []
    for s in matched_schemes[:3]:
        citations.append({
            "scheme_id": s["id"],
            "title": s["title"],
            "ministry": s["ministry"],
            "category": s["category"],
            "official_portal": s.get("official_portal")
        })

    return {
        "answer": full_answer,
        "key_takeaways": key_takeaways,
        "eligibility_assessment": [],
        "citations": citations
    }
