from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str: ...
    def structured_generate(self, prompt: str) -> dict:
        import json

        raw = self.generate(prompt)
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end < start:
            raise ValueError("Model did not return a JSON object")
        return json.loads(raw[start : end + 1])
