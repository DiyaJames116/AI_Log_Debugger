from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LogEvent(BaseModel):
    timestamp: datetime | None = None
    level: str = "INFO"
    service: str | None = None
    component: str | None = None
    message: str
    exception_type: str | None = None
    stack_trace: str | None = None
    request_id: str | None = None
    trace_id: str | None = None
    http_status: int | None = None
    source_file: str
    line_number: int
    raw: str


class ErrorCluster(BaseModel):
    pattern: str
    occurrences: int
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    representative: LogEvent
    events: list[LogEvent] = Field(default_factory=list)
    score: float = 0.0


class Evidence(BaseModel):
    description: str
    source_file: str | None = None
    line_number: int | None = None


class Hypothesis(BaseModel):
    statement: str
    confidence: float = Field(ge=0, le=1)
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    confirmation_needed: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    incident_summary: str
    observed_facts: list[str] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    root_cause: str | None = None
    confidence: float = Field(default=0, ge=0, le=1)
    evidence: list[Evidence] = Field(default_factory=list)
    causal_chain: list[str] = Field(default_factory=list)
    recommended_investigation: list[str] = Field(default_factory=list)
    suggested_fixes: list[str] = Field(default_factory=list)
    relevant_log_events: list[str] = Field(default_factory=list)
    verifier_notes: list[str] = Field(default_factory=list)
