"""Conservative adapters for equivalent JSON shapes emitted by local models."""

from __future__ import annotations

from typing import Any


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if isinstance(value.get("cause"), str) and isinstance(value.get("effect"), str):
            return f"{value['cause']} → {value['effect']}"
        for key in ("message", "description", "statement", "text", "content"):
            if isinstance(value.get(key), str) and value[key].strip():
                return value[key]
        source, line = value.get("source_file"), value.get("line_number")
        if source:
            return f"Log event at {source}{':' + str(line) if line else ''}"
    return str(value)


def _first_text(mapping: dict[str, Any], fields: tuple[str, ...]) -> str | None:
    """Return the first non-empty text value among equivalent model field names."""
    for field in fields:
        value = mapping.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def normalize_analysis_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Map harmless shape variations to AnalysisResult without inventing evidence."""
    result = dict(payload)
    for field in (
        "observed_facts",
        "relevant_log_events",
        "causal_chain",
        "recommended_investigation",
        "suggested_fixes",
        "verifier_notes",
    ):
        value = result.get(field)
        if value is None:
            result[field] = []
        elif isinstance(value, list):
            result[field] = [_text(item) for item in value]
        elif isinstance(value, (str, dict)):
            result[field] = [_text(value)]
    evidence_value = result.get("evidence")
    if evidence_value is None:
        result["evidence"] = []
    elif isinstance(evidence_value, dict):
        if {"description", "message", "source_file", "line_number"} & evidence_value.keys():
            evidence_value = [evidence_value]
        else:
            # Some models emit {"error text": {"source_file": ..., "line_number": ...}}.
            evidence_value = [
                {"description": description, **(location if isinstance(location, dict) else {})}
                for description, location in evidence_value.items()
            ]
    elif isinstance(evidence_value, str):
        evidence_value = [{"description": evidence_value}]
    if isinstance(evidence_value, list):
        evidence = []
        for item in evidence_value:
            if isinstance(item, dict):
                normalized = dict(item)
                normalized.setdefault("description", _text(item))
                evidence.append(normalized)
            else:
                evidence.append({"description": _text(item)})
        result["evidence"] = evidence
    if result.get("hypotheses") is None:
        result["hypotheses"] = []
    elif isinstance(result.get("hypotheses"), list):
        hypotheses = []
        for item in result["hypotheses"]:
            if not isinstance(item, dict):
                hypotheses.append({"statement": _text(item), "confidence": 0.0})
                continue
            normalized = dict(item)
            # llama3.2:3b sometimes labels a hypothesis with ``name`` rather
            # than the prompt's requested ``statement``. They mean the same
            # thing in the report schema.
            normalized["statement"] = _first_text(
                normalized, ("statement", "name", "hypothesis", "title", "description")
            ) or "Unspecified hypothesis returned by the local model."
            confidence = normalized.get(
                "confidence",
                normalized.get("probability", normalized.get("likelihood", 0.0)),
            )
            try:
                confidence = float(confidence)
            except (TypeError, ValueError):
                confidence = 0.0
            # A model may express confidence as a percentage instead of 0–1.
            normalized["confidence"] = confidence / 100 if 1 < confidence <= 100 else confidence
            if not 0 <= normalized["confidence"] <= 1:
                normalized["confidence"] = 0.0
            for field in ("supporting_evidence", "contradicting_evidence", "confirmation_needed"):
                value = normalized.get(field)
                # Local models commonly use JSON null to express that no
                # evidence is available. The schema represents that as an
                # empty list, just as it does when the field is omitted.
                if value is None:
                    normalized[field] = []
                elif isinstance(value, bool):
                    normalized[field] = ["Additional confirmation is required."] if value else []
                elif isinstance(value, str):
                    normalized[field] = [value]
                elif isinstance(value, dict):
                    normalized[field] = [_text(value)] if value else []
                elif isinstance(value, list):
                    normalized[field] = [_text(entry) for entry in value]
            hypotheses.append(normalized)
        result["hypotheses"] = hypotheses
    return result
