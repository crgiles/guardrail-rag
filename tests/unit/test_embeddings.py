"""Tests for deterministic semantic retrieval."""

from datetime import date

import pytest

from guardrail_rag.ingestion.markdown import chunk_document
from guardrail_rag.ingestion.models import Document
from guardrail_rag.retrieval.embeddings import HashEmbeddingModel, retrieve_semantic


def _document(document_id: str, roles: frozenset[str], content: str) -> Document:
    """Build a small document fixture."""
    return Document(
        document_id,
        document_id,
        "ops",
        "internal",
        roles,
        "approved",
        1,
        date(2026, 1, 1),
        content,
    )


def test_hash_embeddings_are_deterministic_and_normalized():
    """Hash embeddings are reproducible and unit length."""
    model = HashEmbeddingModel()
    first = model.embed("network change policy")
    second = model.embed("network change policy")
    assert first == second
    assert sum(value * value for value in first) == pytest.approx(1.0)


def test_semantic_retrieval_filters_authorization():
    """Semantic retrieval excludes unauthorized chunks before ranking."""
    allowed = chunk_document(
        _document("allowed", frozenset({"employee"}), "network changes require review")
    )
    restricted = chunk_document(
        _document("restricted", frozenset({"security_admin"}), "network changes require review")
    )
    results = retrieve_semantic(allowed + restricted, "network change review", "employee")
    assert [chunk.document_id for chunk in results] == ["allowed"]


def test_semantic_retrieval_is_deterministic():
    """Equal semantic scores use stable chunk IDs as a tie-breaker."""
    first = chunk_document(_document("first", frozenset({"employee"}), "network change review"))
    second = chunk_document(_document("second", frozenset({"employee"}), "network change review"))
    results = retrieve_semantic(first + second, "network change review", "employee", limit=2)
    assert [chunk.document_id for chunk in results] == ["first", "second"]


def test_semantic_retrieval_validates_inputs():
    """Reject empty queries and invalid score thresholds."""
    with pytest.raises(ValueError, match="query"):
        retrieve_semantic([], "", "employee")
    with pytest.raises(ValueError, match="minimum_score"):
        retrieve_semantic([], "network", "employee", minimum_score=2)
