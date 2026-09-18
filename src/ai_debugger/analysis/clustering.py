from __future__ import annotations

import re
from collections import defaultdict

from ai_debugger.models.schemas import ErrorCluster, LogEvent


def normalize_message(message: str) -> str:
    message = re.sub(r"\b[0-9a-f]{8,}\b", "<id>", message, flags=re.I)
    message = re.sub(r"\b\d+\b", "<n>", message)
    message = re.sub(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "<ip>", message)
    return re.sub(r"\s+", " ", message.lower()).strip()[:300]


def cluster_events(events: list[LogEvent]) -> list[ErrorCluster]:
    buckets: dict[str, list[LogEvent]] = defaultdict(list)
    for event in events:
        buckets[normalize_message(event.message)].append(event)
    result = []
    for pattern, group in buckets.items():
        ordered = sorted(group, key=lambda e: e.timestamp or __import__("datetime").datetime.min)
        result.append(
            ErrorCluster(
                pattern=pattern,
                occurrences=len(group),
                first_seen=ordered[0].timestamp,
                last_seen=ordered[-1].timestamp,
                representative=group[0],
                events=group[:5],
            )
        )
    return result
