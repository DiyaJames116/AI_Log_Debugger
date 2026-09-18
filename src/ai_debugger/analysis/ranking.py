from ai_debugger.models.schemas import ErrorCluster

WEIGHTS = {"CRITICAL": 10, "FATAL": 10, "ERROR": 7, "WARN": 3}


def rank_clusters(clusters: list[ErrorCluster]) -> list[ErrorCluster]:
    for c in clusters:
        e = c.representative
        text = e.message.lower()
        c.score = (
            WEIGHTS.get(e.level, 1) * 5
            + min(c.occurrences, 100) ** 0.5
            + (4 if e.stack_trace else 0)
            + (5 if (e.http_status or 0) >= 500 else 0)
            + sum(x in text for x in ("timeout", "exhausted", "refused", "oom", "crash", "failed"))
            * 2
        )
    return sorted(clusters, key=lambda c: c.score, reverse=True)
