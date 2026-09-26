import json
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Scheme(Base):
    __tablename__ = "schemes"
    
    id = Column(String(100), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    short_name = Column(String(100), index=True)
    category = Column(String(100), index=True)
    ministry = Column(String(255))
    target_beneficiaries = Column(Text)
    financial_assistance = Column(Text)
    eligibility_criteria = Column(Text) # JSON string
    benefits = Column(Text) # JSON string
    documents_required = Column(Text) # JSON string
    application_process = Column(Text)
    official_portal = Column(String(255))
    tags = Column(Text) # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    chunks = relationship("SchemeChunk", back_populates="scheme", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "short_name": self.short_name,
            "category": self.category,
            "ministry": self.ministry,
            "target_beneficiaries": self.target_beneficiaries,
            "financial_assistance": self.financial_assistance,
            "eligibility_criteria": json.loads(self.eligibility_criteria or "[]"),
            "benefits": json.loads(self.benefits or "[]"),
            "documents_required": json.loads(self.documents_required or "[]"),
            "application_process": self.application_process,
            "official_portal": self.official_portal,
            "tags": json.loads(self.tags or "[]"),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class SchemeChunk(Base):
    __tablename__ = "scheme_chunks"
    
    id = Column(String(120), primary_key=True, index=True)
    scheme_id = Column(String(100), ForeignKey("schemes.id"), index=True)
    section_name = Column(String(100), index=True) # Overview, Eligibility, Benefits, Application, Documents
    chunk_title = Column(String(255))
    content = Column(Text, nullable=False)
    embedding = Column(Text) # JSON string array of floats (384-dim)
    
    scheme = relationship("Scheme", back_populates="chunks")

    def to_dict(self):
        return {
            "id": self.id,
            "scheme_id": self.scheme_id,
            "section_name": self.section_name,
            "chunk_title": self.chunk_title,
            "content": self.content,
            "scheme_title": self.scheme.title if self.scheme else ""
        }

class EvaluationLog(Base):
    __tablename__ = "evaluation_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(Text, nullable=False)
    retrieved_chunks_json = Column(Text) # JSON string of chunk info
    answer = Column(Text, nullable=False)
    faithfulness_score = Column(Float)
    relevancy_score = Column(Float)
    overall_score = Column(Float)
    claims_breakdown_json = Column(Text) # JSON of claims & verification
    latency_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "query": self.query,
            "retrieved_chunks": json.loads(self.retrieved_chunks_json or "[]"),
            "answer": self.answer,
            "faithfulness_score": self.faithfulness_score,
            "relevancy_score": self.relevancy_score,
            "overall_score": self.overall_score,
            "claims_breakdown": json.loads(self.claims_breakdown_json or "[]"),
            "latency_ms": self.latency_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
