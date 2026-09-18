from ai_debugger.llm.normalization import normalize_analysis_payload
from ai_debugger.models.schemas import AnalysisResult


def test_normalizes_event_objects_without_inventing_content():
    payload = {
        "incident_summary": "Failure observed",
        "observed_facts": [
            {"message": "connection timeout", "source_file": "app.log", "line_number": 4}
        ],
        "hypotheses": [{"statement": "Pool issue", "confidence": 0.5, "confirmation_needed": True}],
        "evidence": [{"source_file": "app.log", "line_number": 4}],
        "relevant_log_events": [{"message": "connection timeout"}],
    }
    result = AnalysisResult.model_validate(normalize_analysis_payload(payload))
    assert result.observed_facts == ["connection timeout"]
    assert result.hypotheses[0].confirmation_needed == ["Additional confirmation is required."]
    assert result.evidence[0].description == "Log event at app.log:4"


def test_normalizes_a_single_recommendation_string():
    payload = {
        "incident_summary": "Failure observed",
        "recommended_investigation": "Check network connectivity.",
    }
    result = AnalysisResult.model_validate(normalize_analysis_payload(payload))
    assert result.recommended_investigation == ["Check network connectivity."]


def test_normalizes_causal_link_object():
    payload = {
        "incident_summary": "Failure observed",
        "causal_chain": [{"cause": "Database", "effect": "API"}],
    }
    result = AnalysisResult.model_validate(normalize_analysis_payload(payload))
    assert result.causal_chain == ["Database → API"]


def test_normalizes_single_hypothesis_evidence_and_named_evidence_map():
    payload = {
        "incident_summary": "Failure observed",
        "hypotheses": [
            {
                "statement": "Database timeout",
                "confidence": 0.8,
                "supporting_evidence": {"message": "ConnectionTimeoutError"},
                "contradicting_evidence": {},
            }
        ],
        "evidence": {"ConnectionTimeoutError": {"source_file": "app.log", "line_number": 5}},
    }
    result = AnalysisResult.model_validate(normalize_analysis_payload(payload))
    assert result.hypotheses[0].supporting_evidence == ["ConnectionTimeoutError"]
    assert result.hypotheses[0].contradicting_evidence == []
    assert result.evidence[0].description == "ConnectionTimeoutError"


def test_normalizes_null_hypothesis_evidence_to_empty_lists():
    payload = {
        "incident_summary": "A Python exception was logged.",
        "hypotheses": [
            {
                "statement": "The application encountered an unhandled exception.",
                "confidence": 0.8,
                "supporting_evidence": ["Traceback in sample_python.log"],
                "contradicting_evidence": None,
                "confirmation_needed": None,
            }
        ],
    }

    result = AnalysisResult.model_validate(normalize_analysis_payload(payload))

    assert result.hypotheses[0].contradicting_evidence == []
    assert result.hypotheses[0].confirmation_needed == []


def test_normalizes_llama_hypothesis_name_aliases():
    payload = {
        "incident_summary": "Worker task failures were recorded.",
        "hypotheses": [
            {
                "name": "Worker task failure is caused by a database timeout.",
                "confidence": 80,
                "supporting_evidence": ["ConnectionTimeoutError"],
                "contradicting_evidence": None,
                "confirmation_needed": [],
            },
            {
                "name": "The task failure may be an unhandled application exception.",
                "likelihood": "0.4",
            },
        ],
    }

    result = AnalysisResult.model_validate(normalize_analysis_payload(payload))

    assert result.hypotheses[0].statement == "Worker task failure is caused by a database timeout."
    assert result.hypotheses[0].confidence == 0.8
    assert result.hypotheses[1].statement == "The task failure may be an unhandled application exception."
    assert result.hypotheses[1].confidence == 0.4
