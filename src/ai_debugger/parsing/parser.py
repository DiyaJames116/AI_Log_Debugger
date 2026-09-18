from __future__ import annotations

import re
from pathlib import Path

from ai_debugger.models.schemas import LogEvent

from .formats import LEVEL, REQUEST, STATUS, TIMESTAMP, TRACE, parse_json, parse_timestamp

EXCEPTION = re.compile(r"\b([A-Za-z_][\w.]*(?:Exception|Error|Failure))\b")


def parse_line(line: str, source: Path, line_number: int) -> LogEvent:
    data = parse_json(line)
    if data:
        message = str(data.get("message") or data.get("msg") or data.get("error") or line)
        timestamp = parse_timestamp(
            str(data.get("timestamp") or data.get("time") or data.get("@timestamp") or "")
        )
        level = str(data.get("level") or data.get("severity") or "INFO").upper()
        status = data.get("status") or data.get("status_code") or data.get("http_status")
        return LogEvent(
            timestamp=timestamp,
            level=level,
            service=data.get("service"),
            component=data.get("component") or data.get("logger"),
            message=message,
            exception_type=data.get("exception_type"),
            request_id=data.get("request_id"),
            trace_id=data.get("trace_id"),
            http_status=int(status) if str(status).isdigit() else None,
            source_file=str(source),
            line_number=line_number,
            raw=line,
        )
    tm, lm, sm = TIMESTAMP.search(line), LEVEL.search(line), STATUS.search(line)
    em = EXCEPTION.search(line)
    message = line[tm.end() :].strip() if tm else line
    if lm:
        message = re.sub(
            r"\b(?:TRACE|DEBUG|INFO|WARN(?:ING)?|ERROR|FATAL|CRITICAL)\b\s*",
            "",
            message,
            count=1,
            flags=re.I,
        )
    return LogEvent(
        timestamp=parse_timestamp(tm.group("ts") if tm else None),
        level=(lm.group("level").upper().replace("WARNING", "WARN") if lm else "INFO"),
        message=message,
        exception_type=em.group(1) if em else None,
        request_id=(REQUEST.search(line).group(1) if REQUEST.search(line) else None),
        trace_id=(TRACE.search(line).group(1) if TRACE.search(line) else None),
        http_status=int(sm.group("status")) if sm else None,
        source_file=str(source),
        line_number=line_number,
        raw=line,
    )


def is_significant(event: LogEvent) -> bool:
    text = f"{event.message} {event.exception_type or ''}".lower()
    terms = (
        "exception",
        "traceback",
        "timeout",
        "failed",
        "failure",
        "refused",
        "exhausted",
        "crash",
        "oom",
        "out of memory",
        "unauthor",
        "forbidden",
    )
    return (
        event.level in {"WARN", "ERROR", "FATAL", "CRITICAL"}
        or bool(event.http_status and event.http_status >= 400)
        or any(t in text for t in terms)
    )
