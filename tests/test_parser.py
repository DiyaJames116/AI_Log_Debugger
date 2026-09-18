from pathlib import Path

from ai_debugger.parsing import parse_line


def test_plain_timestamp_and_fields():
    event = parse_line(
        "2026-09-17 14:32:18 ERROR database timeout HTTP 503 request_id=abc", Path("x.log"), 7
    )
    assert (
        event.timestamp
        and event.level == "ERROR"
        and event.http_status == 503
        and event.request_id == "abc"
    )


def test_json_log():
    event = parse_line(
        '{"timestamp":"2026-09-17T14:32:18Z","level":"ERROR","message":"boom","service":"api"}',
        Path("x.jsonl"),
        1,
    )
    assert event.service == "api" and event.message == "boom"
