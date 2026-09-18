import json


def build_verification_prompt(analysis, timeline, clusters) -> str:
    return (
        """Verify this draft against supplied logs. Return the corrected analysis JSON using the same schema. Remove unsupported claims, lower confidence for weak evidence, and preserve fact/hypothesis separation.\nDRAFT:\n"""
        + json.dumps(analysis, default=str)
        + "\nTIMELINE:\n"
        + json.dumps([e.model_dump(mode="json") for e in timeline], default=str)
        + "\nCLUSTERS:\n"
        + json.dumps([c.model_dump(mode="json", exclude={"events"}) for c in clusters], default=str)
    )
