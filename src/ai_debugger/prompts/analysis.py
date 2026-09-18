import json


def build_analysis_prompt(timeline, clusters, context) -> str:
    payload = {
        "timeline": [e.model_dump(mode="json") for e in timeline],
        "error_clusters": [c.model_dump(mode="json", exclude={"events"}) for c in clusters],
        "context": [e.model_dump(mode="json") for e in context],
    }
    return (
        """You are a careful incident analyst. Analyze only this local log evidence. Return JSON matching: incident_summary, observed_facts (facts directly supported by logs), hypotheses (objects with statement, confidence 0-1, supporting_evidence, contradicting_evidence, confirmation_needed), root_cause (explicitly a hypothesis), confidence, evidence (objects description/source_file/line_number), causal_chain, recommended_investigation, suggested_fixes, relevant_log_events. Never invent lines or call a hypothesis fact.\n\nEVIDENCE:\n"""
        + json.dumps(payload, default=str)
    )
