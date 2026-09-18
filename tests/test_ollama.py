import httpx
import pytest

from ai_debugger.llm.ollama import OllamaProvider


def test_timeout_is_a_clean_runtime_error(monkeypatch):
    def fail(*args, **kwargs):
        raise httpx.ReadTimeout("slow")

    monkeypatch.setattr(httpx, "post", fail)
    with pytest.raises(RuntimeError, match="did not respond"):
        OllamaProvider("model", "http://127.0.0.1", timeout=1).generate("test")


def test_empty_json_is_a_clear_model_error(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": "{}"}

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: Response())
    with pytest.raises(RuntimeError, match="incomplete analysis"):
        OllamaProvider("model", "http://127.0.0.1").structured_generate("test")
