from ai_debugger.models.schemas import ErrorCluster, LogEvent


def retrieve_context(
    clusters: list[ErrorCluster], timeline: list[LogEvent], max_chars: int
) -> list[LogEvent]:
    selected: list[LogEvent] = []
    seen = set()
    for event in [*(c.representative for c in clusters), *timeline]:
        key = (event.source_file, event.line_number)
        if key not in seen and sum(len(x.raw) for x in selected) + len(event.raw) <= max_chars:
            selected.append(event)
            seen.add(key)
    return selected
