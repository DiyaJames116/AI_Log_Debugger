from pathlib import Path

from ai_debugger.analysis.clustering import cluster_events
from ai_debugger.parsing import parse_line


def test_deduplicates_variable_ids():
    items = [
        parse_line(f"2026-01-01 00:00:0{i} ERROR connection timeout user={i}", Path("a.log"), i)
        for i in range(3)
    ]
    assert len(cluster_events(items)) == 1
