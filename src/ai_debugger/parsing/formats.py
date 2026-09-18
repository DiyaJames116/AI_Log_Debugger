from __future__ import annotations

import json
import re
from datetime import datetime

TIMESTAMP = re.compile(
    r"^\[?(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\]?\s*"
)
LEVEL = re.compile(r"\b(?P<level>TRACE|DEBUG|INFO|WARN(?:ING)?|ERROR|FATAL|CRITICAL)\b", re.I)
STATUS = re.compile(r"\b(?:HTTP(?:/\d(?:\.\d)?)?\s*)?(?P<status>[45]\d\d)\b")
REQUEST = re.compile(r"\b(?:request[_ -]?id|req_id)[=:]([\w-]+)", re.I)
TRACE = re.compile(r"\btrace[_ -]?id[=:]([\w-]+)", re.I)


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00").replace(",", "."))
    except ValueError:
        return None


def parse_json(line: str) -> dict | None:
    try:
        obj = json.loads(line)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None
