import json

from ai_debugger.models.schemas import AnalysisResult


def render(result: AnalysisResult) -> str:
    return json.dumps(result.model_dump(mode="json"), indent=2, default=str)
