from __future__ import annotations

from ai_debugger.llm.base import LLMProvider
from ai_debugger.models.schemas import AnalysisResult
from ai_debugger.prompts.verification import build_verification_prompt


def verify(provider: LLMProvider, analysis: AnalysisResult, timeline, clusters) -> AnalysisResult:
    try:
        return AnalysisResult.model_validate(
            provider.structured_generate(
                build_verification_prompt(analysis.model_dump(), timeline, clusters)
            )
        )
    except (ValueError, KeyError) as exc:
        analysis.verifier_notes.append(
            f"Verification output was invalid; retained first-pass analysis: {exc}"
        )
        return analysis
