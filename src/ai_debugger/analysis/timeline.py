from ai_debugger.models.schemas import LogEvent


def build_timeline(events: list[LogEvent], limit: int = 50) -> list[LogEvent]:
    dated = [e for e in events if e.timestamp]
    return sorted(dated, key=lambda e: e.timestamp)[:limit]
