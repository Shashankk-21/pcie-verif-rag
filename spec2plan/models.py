from typing import List

from pydantic import BaseModel, Field


class EvidenceChunk(BaseModel):
    id: str
    text: str
    source_filename: str
    page_number: int | None = None
    section_heading: str | None = None


class RetrievedEvidence(BaseModel):
    chunk: EvidenceChunk
    score: float
    lexical_score: float
    vector_score: float


class VerificationItem(BaseModel):
    requirement_id: str
    requirement_statement: str
    source_section: str | None = None
    source_page: int | None = None
    supporting_quotation: str
    verification_objective: str
    test_scenario: str
    expected_behavior: str
    relevant_signals: List[str] = Field(min_length=1)
    candidate_sva: str
    clock_reset_sampling_assumptions: str
    confidence_or_uncertainty: str
    evidence_ids: List[str] = Field(min_length=1)
    category: str


class VerificationPlan(BaseModel):
    query: str
    items: List[VerificationItem]
    uncovered_categories: List[str]


class EvidenceReport(BaseModel):
    query: str
    source_files: List[str]
    retrieved: List[RetrievedEvidence]
    evidence_categories: List[str]
    categories_without_evidence: List[str]
    note: str
