from __future__ import annotations

import httpx

from .base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, model: str, base_url: str, timeout: float = 600):
        self.model, self.base_url, self.timeout = model, base_url.rstrip("/"), timeout

    def generate(self, prompt: str) -> str:
        try:
            # Qwen's reasoning mode can consume a small model's entire response
            # budget before it emits JSON. Apply its control token only to Qwen;
            # other model families should receive a clean generic prompt.
            reasoning_control = "/no_think\n" if self.model.lower().startswith("qwen3") else ""
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": reasoning_control
                    + prompt
                    + "\nReturn one complete, non-empty JSON object now.",
                    "stream": False,
                    "format": "json",
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()["response"]
        except httpx.ConnectError as exc:
            raise RuntimeError(
                "Ollama is required for AI analysis. Install Ollama, start it, and download a supported model."
            ) from exc
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                f"Ollama did not respond within {self.timeout:g} seconds. The model may still be loading or needs more available RAM. Try --no-verification, a smaller model, or set AI_DEBUG_OLLAMA_TIMEOUT=900."
            ) from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

    def structured_generate(self, prompt: str) -> dict:
        import json

        raw = self.generate(prompt)
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end < start:
            raise RuntimeError(
                "The local model did not return JSON. Try a more capable model or use --offline for an evidence-only report."
            )
        try:
            payload = json.loads(raw[start : end + 1])
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "The local model returned malformed JSON. Try again, use a more capable model, or use --offline."
            ) from exc
        if not payload or not payload.get("incident_summary"):
            raise RuntimeError(
                "The local model returned an incomplete analysis. qwen3:1.7b may be too small for this structured task; try qwen3:4b or use --offline."
            )
        return payload

    def models(self) -> list[str]:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            return [m["name"] for m in response.json().get("models", [])]
        except httpx.HTTPError as exc:
            raise RuntimeError(
                "Ollama is required for AI analysis. Install Ollama, start it, and download a supported model."
            ) from exc
