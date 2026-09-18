from ai_debugger.config import Settings
from ai_debugger.llm.base import LLMProvider
from ai_debugger.pipeline import analyze


class FakeLLM(LLMProvider):
    def generate(self, prompt):
        return '{"incident_summary":"Database trouble","observed_facts":["timeout logged"],"hypotheses":[{"statement":"Pool exhaustion","confidence":0.7}],"confidence":0.7}'


def test_pipeline_uses_structured_local_provider(tmp_path):
    f = tmp_path / "x.log"
    f.write_text("2026-01-01 00:00:00 ERROR connection timeout\n")
    r = analyze(f, Settings(), FakeLLM(), verification=False)
    assert r.analysis.root_cause is None and r.analysis.hypotheses[0].statement == "Pool exhaustion"


def test_streaming_max_lines(tmp_path):
    f = tmp_path / "x.log"
    f.write_text("2026-01-01 00:00:00 ERROR first\n2026-01-01 00:00:01 ERROR second\n")
    assert analyze(f, Settings(max_lines=1), None).metrics["lines"] == 1
