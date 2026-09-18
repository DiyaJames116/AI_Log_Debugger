from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path


def stream_lines(
    path: Path, max_file_size: int, max_lines: int | None = None
) -> Iterator[tuple[int, str]]:
    size = path.stat().st_size
    if size > max_file_size:
        raise ValueError(f"{path} is {size:,} bytes, over --max-file-size ({max_file_size:,})")
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, 1):
            if max_lines and number > max_lines:
                return
            yield number, line.rstrip("\n")
