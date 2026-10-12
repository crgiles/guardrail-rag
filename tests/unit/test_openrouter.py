# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,unused-argument,redefined-outer-name

import json
from datetime import date

import pytest

from guardrail_rag.generation.openrouter import OpenRouterError, OpenRouterProvider
from guardrail_rag.ingestion.models import Chunk, Document


@pytest.fixture
def chunk():
    document = Document(
        "doc-1", "Test policy", "ops", "internal", frozenset({"employee"}),
        "approved", 1, date(2026, 1, 1), "Production changes require peer review.",
    )
    return Chunk("doc-1:0", "doc-1", document.content, 0, document)


def test_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(OpenRouterError, match="API_KEY"):
        OpenRouterProvider()


def test_empty_chunks_refuse_without_network(monkeypatch):
    provider = OpenRouterProvider(api_key="test-key")
    result = provider.answer("question", [])
    assert result.refusal_reason == "insufficient_evidence"


def test_parses_openrouter_response(monkeypatch, chunk):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps({"choices": [{"message": {"content": "Grounded answer."}}]}).encode()

    def fake_urlopen(http_request, timeout):
        assert http_request.full_url.endswith("/chat/completions")
        assert timeout == 30.0
        return Response()

    monkeypatch.setattr("guardrail_rag.generation.openrouter.request.urlopen", fake_urlopen)
    result = OpenRouterProvider(api_key="test-key").answer("question", [chunk])
    assert result.answer == "Grounded answer."
