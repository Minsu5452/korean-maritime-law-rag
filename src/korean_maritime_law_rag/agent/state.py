from typing import Literal

from pydantic import BaseModel, Field

QueryType = Literal["single", "definition", "multihop", "unanswerable"]


class QueryTypeResult(BaseModel):
    query_type: QueryType


class EvidenceGrade(BaseModel):
    sufficient: bool
    reason: str = ""
    rewritten_query: str | None = None


class GeneratedAnswer(BaseModel):
    answer: str
    citations: list[str] = Field(default_factory=list)


class VerifiedAnswer(BaseModel):
    answer: str
    valid_citations: list[str] = Field(default_factory=list)
    invalid_citations: list[str] = Field(default_factory=list)
    low_confidence: bool = False


class CitedArticle(BaseModel):
    """답변이 인용한 조문의 표시용 메타데이터(doc_id를 사람이 읽는 형태로 해소)."""

    doc_id: str
    law_name: str
    article_no: str
    law_type: str = "법률"
    title: str = ""
    text: str = ""
    enforce_date: str | None = None  # 시행일 YYYYMMDD


class AgentResponse(BaseModel):
    answer: str
    citations: list[str] = Field(default_factory=list)
    evidence: list[CitedArticle] = Field(default_factory=list)
    invalid_citations: list[str] = Field(default_factory=list)
    query_type: QueryType
    strategy: str
    refused: bool = False
    low_confidence: bool = False
    evidence_sufficient: bool | None = None
    evidence_reason: str = ""
    rewritten_query: str | None = None
    retrieval_attempts: int = 0
    generation_attempts: int = 0
    used_live_fallback: bool = False
