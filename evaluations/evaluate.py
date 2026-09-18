"""Offline extraction evaluation; LLM quality is evaluated separately with a pinned local model."""

import json
from pathlib import Path

from ai_debugger.config import Settings
from ai_debugger.pipeline import analyze

base = Path(__file__).parent
for name, item in json.loads((base / "expectations.json").read_text()).items():
    result = analyze(base / item["file"], Settings(), provider=None)
    text = " ".join(c.pattern for c in result.clusters)
    hits = sum(term in text for term in item["expected_terms"])
    print(
        f"{name}: important-event recall {hits}/{len(item['expected_terms'])}; timeline events {len(result.timeline)}"
    )
