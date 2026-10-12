# pylint: disable=missing-module-docstring,missing-function-docstring

from fastapi.testclient import TestClient

from guardrail_rag.api.app import create_app

client = TestClient(create_app())


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_returns_grounded_answer_and_citation():
    response = client.post(
        "/query",
        json={
            "question": "What approvals are required for a production network change?",
            "role": "network_engineer",
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["answer"].startswith("Based on the available evidence:")
    assert body["citations"][0]["document_id"] == "net-change-policy-003"
    assert body["retrieved_count"] == 1
    assert body["refusal_reason"] is None
    assert body["request_id"]


def test_query_does_not_retrieve_unauthorized_document():
    response = client.post(
        "/query",
        json={
            "question": "What are the production network change requirements?",
            "role": "security_admin",
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["retrieved_count"] == 0
    assert body["citations"] == []
    assert body["refusal_reason"] == "insufficient_evidence"


def test_query_rejects_empty_question_and_invalid_role():
    empty = client.post("/query", json={"question": "", "role": "employee"})
    invalid_role = client.post("/query", json={"question": "hello", "role": "admin"})
    assert empty.status_code == 422
    assert invalid_role.status_code == 422
