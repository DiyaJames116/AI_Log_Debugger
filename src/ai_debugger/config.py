from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    model: str = os.getenv("AI_DEBUG_MODEL", "qwen3:8b")
    ollama_url: str = os.getenv("AI_DEBUG_OLLAMA_URL", "http://127.0.0.1:11434")
    ollama_timeout: float = float(os.getenv("AI_DEBUG_OLLAMA_TIMEOUT", "600"))
    max_file_size: int = 2 * 1024 * 1024 * 1024
    max_lines: int | None = None
    max_context: int = 12000
    redact: bool = True
