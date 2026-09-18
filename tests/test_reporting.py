from ai_debugger.models.schemas import AnalysisResult, Hypothesis
from ai_debugger.reporting.markdown import render


def test_omits_empty_hypothesis_subsections():
    report = render(
        AnalysisResult(
            incident_summary="x", hypotheses=[Hypothesis(statement="y", confidence=0.5)]
        ),
        [],
        [],
    )
    assert "Supporting evidence:" not in report
    assert "To confirm:" not in report
