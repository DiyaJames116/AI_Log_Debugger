from html import escape

from .markdown import render as markdown


def render(result, timeline, clusters) -> str:
    body = escape(markdown(result, timeline, clusters))
    return f"<!doctype html><html><head><meta charset='utf-8'><title>AI Log Debugger report</title><style>body{{font:16px system-ui;max-width:960px;margin:3rem auto;padding:0 1rem;color:#172033}}pre{{white-space:pre-wrap;background:#f6f8fa;padding:1.5rem;border-radius:8px}} </style></head><body><pre>{body}</pre></body></html>"
