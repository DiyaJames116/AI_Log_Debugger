from pathlib import Path

from ai_debugger.analysis.timeline import build_timeline
from ai_debugger.parsing import parse_line


def test_orders_events():
    later = parse_line("2026-01-01 00:00:02 ERROR later", Path("x"), 1)
    first = parse_line("2026-01-01 00:00:01 ERROR first", Path("x"), 2)
    assert build_timeline([later, first])[0].message == "first"
