from ai_debugger.models.schemas import AnalysisResult, ErrorCluster, LogEvent


def render(result: AnalysisResult, timeline: list[LogEvent], clusters: list[ErrorCluster]) -> str:
    lines = [
        "# AI LOG DEBUGGER",
        "",
        "## Incident Summary",
        result.incident_summary,
        "",
        "## Confidence",
        f"{result.confidence:.2f}",
        "",
        "## Observed Facts",
    ]
    lines += [f"- {x}" for x in result.observed_facts] or [
        "- No directly observed facts were classified."
    ]
    lines += ["", "## Root Cause Hypotheses"]
    for h in result.hypotheses:
        lines += [f"### {h.statement} ({h.confidence:.2f})"]
        if h.supporting_evidence:
            lines += ["**Supporting evidence:**", *[f"- {x}" for x in h.supporting_evidence]]
        if h.contradicting_evidence:
            lines += ["**Contradicting evidence:**", *[f"- {x}" for x in h.contradicting_evidence]]
        if h.confirmation_needed:
            lines += ["**To confirm:**", *[f"- {x}" for x in h.confirmation_needed]]
    lines += ["", "## Error Clusters"]
    lines += [
        f"- `{c.pattern}` — {c.occurrences} occurrences; score {c.score:.1f}" for c in clusters
    ]
    lines += ["", "## Timeline"]
    lines += [f"- {e.timestamp or 'unknown time'} — {e.level} — {e.message}" for e in timeline]
    for title, items in (
        ("Causal Chain", result.causal_chain),
        ("Recommended Investigation", result.recommended_investigation),
        ("Suggested Fixes", result.suggested_fixes),
    ):
        lines += ["", f"## {title}", *[f"- {x}" for x in items]]
    return "\n".join(lines) + "\n"
