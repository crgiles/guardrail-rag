"""Integration tests for safe request observability and provider failures."""

import json
import logging

from fastapi.testclient import TestClient

from guardrail_rag.api.app import create_app
from guardrail_rag.generation.openrouter import OpenRouterError
from guardrail_rag.observability.logging import JsonFormatter


class FailingProvider:  # pylint: disable=too-few-public-methods
    """Provider double that raises a controlled OpenRouter error."""
    def answer(self, question, chunks):
        """Raise a provider error for API error handling tests."""
        raise OpenRouterError("secret-provider-detail")


def test_request_id_header_and_safe_log(caplog):
    """Verify request IDs are returned and logs contain no request content."""
    client = TestClient(create_app())
    with caplog.at_level(logging.INFO, logger="guardrail_rag.api"):
        response = client.get("/health", headers={"x-request-id": "test-request"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "test-request"
    record = next(record for record in caplog.records if record.message == "request_completed")
    payload = json.loads(JsonFormatter().format(record))
    assert payload["request_id"] == "test-request"
    assert "headers" not in payload
    assert "body" not in payload


def test_provider_failure_is_stable_and_non_secret():
    """Verify provider details are not returned to API clients."""
    client = TestClient(create_app(provider=FailingProvider()))
    response = client.post("/query", json={"question": "network change policy", "role": "employee"})

    assert response.status_code == 200
    assert response.json()["refusal_reason"] == "provider_unavailable"
    assert "secret-provider-detail" not in response.text
