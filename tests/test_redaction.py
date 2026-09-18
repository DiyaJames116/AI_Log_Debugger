from ai_debugger.security import redact


def test_redacts_bearer_jwt_and_password():
    text = redact("Authorization: Bearer eyJaaa.bbb.ccc password=hunter2")
    assert "hunter2" not in text and "eyJaaa" not in text and "[REDACTED]" in text
