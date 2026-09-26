from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SchemeSummary(BaseModel):
    id: str
    title: str
    short_name: Optional[str] = None
    category: str
    ministry: str
    target_beneficiaries: str
    financial_assistance: str
    tags: List[str] = []
    official_portal: Optional[str] = None

class SchemeDetail(SchemeSummary):
    eligibility_criteria: List[str]
    benefits: List[str]
    documents_required: List[str]
    application_process: str
    created_at: Optional[str] = None

class SearchQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language citizen search query")
    top_k: int = Field(5, description="Number of results to return")
    category: Optional[str] = Field(None, description="Optional category filter")

class RetrievedChunk(BaseModel):
    id: str
    scheme_id: str
    scheme_title: str
    section_name: str
    chunk_title: str
    content: str
    lexical_score: float
    dense_score: float
    rrf_score: float
    official_portal: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    total_results: int
    retrieved_chunks: List[RetrievedChunk]
    matched_schemes: List[SchemeSummary]
    latency_ms: float

class ChatQueryRequest(BaseModel):
    query: str = Field(..., description="Citizen natural language situation or question")
    top_k: int = Field(4, description="Context chunk count")
    category: Optional[str] = None
    evaluate: bool = Field(True, description="Whether to run RAGAS faithfulness & relevancy evaluation")

class ClaimVerification(BaseModel):
    claim: str
    is_grounded: bool
    supporting_scheme: str
    evidence_snippet: str

class GroundedAnswerResponse(BaseModel):
    query: str
    answer: str
    key_takeaways: List[str]
    eligibility_assessment: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    retrieved_chunks: List[RetrievedChunk]
    faithfulness_score: float
    relevancy_score: float
    claims_breakdown: List[ClaimVerification]
    latency_ms: float

class EvaluationRequest(BaseModel):
    query: str
    answer: str
    context_chunks: List[str]

class EvaluationResult(BaseModel):
    query: str
    faithfulness_score: float
    relevancy_score: float
    overall_score: float
    claims_breakdown: List[ClaimVerification]
    latency_ms: float

class BenchmarkRunResponse(BaseModel):
    total_queries: int
    mean_faithfulness: float
    mean_relevancy: float
    mean_overall: float
    mean_latency_ms: float
    results: List[Dict[str, Any]]
