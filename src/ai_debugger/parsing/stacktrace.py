from ai_debugger.models.schemas import LogEvent


def attach_stacktraces(events: list[LogEvent]) -> list[LogEvent]:
    """Attach indented traceback lines to the immediately preceding event."""
    previous = None
    for event in events:
        if previous and (event.raw.startswith((" ", "\t")) or event.raw.lstrip().startswith("at ")):
            previous.stack_trace = (previous.stack_trace or "") + "\n" + event.raw
        else:
            previous = event
    return events
