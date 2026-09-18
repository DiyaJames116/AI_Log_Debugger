from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ai_debugger.analysis.clustering import cluster_events
from ai_debugger.analysis.ranking import rank_clusters
from ai_debugger.analysis.retrieval import retrieve_context
from ai_debugger.analysis.timeline import build_timeline
from ai_debugger.config import Settings
from ai_debugger.ingestion import discover_logs, stream_lines
from ai_debugger.llm.base import LLMProvider
from ai_debugger.llm.normalization import normalize_analysis_payload
from ai_debugger.models.schemas import AnalysisResult, Evidence, LogEvent
from ai_debugger.parsing import is_significant, parse_line
from ai_debugger.prompts.analysis import build_analysis_prompt
from ai_debugger.security import redact
from ai_debugger.verification import verify


@dataclass
class PipelineResult:
    analysis: AnalysisResult
    events: list[LogEvent]
    clusters: list
    timeline: list[LogEvent]
    metrics: dict[str, int] = field(default_factory=dict)


def observed_only(clusters, timeline) -> AnalysisResult:
    facts = [f"{c.occurrences} occurrence(s) of '{c.pattern}'" for c in clusters[:8]]
    evidence = [
        Evidence(description=e.message, source_file=e.source_file, line_number=e.line_number)
        for e in timeline[:8]
    ]
    return AnalysisResult(
        incident_summary="Local evidence extraction completed. AI interpretation was not requested.",
        observed_facts=facts,
        evidence=evidence,
        recommended_investigation=[
            "Run with a local Ollama model to generate evidence-grounded hypotheses."
        ],
    )


def analyze(
    path: Path, settings: Settings, provider: LLMProvider | None = None, verification: bool = True
) -> PipelineResult:
    events = []
    total = 0
    for source in discover_logs(path):
        for line_no, line in stream_lines(source, settings.max_file_size, settings.max_lines):
            total += 1
            event = parse_line(redact(line) if settings.redact else line, source, line_no)
            if is_significant(event):
                events.append(event)
    clusters = rank_clusters(cluster_events(events))
    timeline = build_timeline(events)
    context = retrieve_context(clusters[:30], timeline, settings.max_context)
    analysis = observed_only(clusters, timeline)
    if provider:
        model_output = provider.structured_generate(
            build_analysis_prompt(timeline, clusters[:30], context)
        )
        analysis = AnalysisResult.model_validate(normalize_analysis_payload(model_output))
        if verification:
            analysis = verify(provider, analysis, timeline, clusters[:30])
    return PipelineResult(
        analysis,
        events,
        clusters[:30],
        timeline,
        {
            "lines": total,
            "events": len(events),
            "unique_patterns": len(clusters),
            "important": len(clusters[:30]),
            "context_chars": sum(len(e.raw) for e in context),
        },
    )
