"""Tests for document ingestion and deterministic retrieval."""

from datetime import date
from pathlib import Path

import pytest

from guardrail_rag.authorization.policy import filter_authorized
from guardrail_rag.ingestion.markdown import chunk_document, parse_markdown
from guardrail_rag.ingestion.models import Document
from guardrail_rag.retrieval.simple import retrieve

FIXTURE = Path(__file__).parents[2] / "data" / "synthetic" / "network-policy.md"


def test_parse_and_chunk_document():
    """Parse metadata and produce stable chunk IDs."""
    document = parse_markdown(FIXTURE)
    assert document.document_id == "net-change-policy-003"
    assert document.effective_date == date(2026, 1, 15)
    assert chunk_document(document, max_words=5)[0].chunk_id == "net-change-policy-003:0"


def test_invalid_frontmatter_is_rejected(tmp_path):
    """Reject Markdown without YAML frontmatter."""
    path = tmp_path / "bad.md"
    path.write_text("# no metadata", encoding="utf-8")
    with pytest.raises(ValueError, match="frontmatter"):
        parse_markdown(path)


def test_retrieval_filters_before_scoring():
    """Never return a chunk the caller role cannot access."""
    public = Document(
        "public", "Public", "ops", "public", frozenset({"employee"}), "approved", 1,
        date.today(), "network change policy",
    )
    restricted = Document(
        "restricted", "Restricted", "security", "restricted", frozenset({"security_admin"}),
        "approved", 1, date.today(), "network change policy",
    )
    chunks = chunk_document(public) + chunk_document(restricted)
    employee_results = retrieve(chunks, "network change policy", "employee")
    assert [chunk.document_id for chunk in employee_results] == ["public"]
    assert filter_authorized(chunks, "employee")[0].document_id == "public"


def test_unrelated_query_returns_no_results():
    """Reject unrelated questions without a query-specific workaround."""
    document = parse_markdown(FIXTURE)
    assert retrieve(chunk_document(document), "annual bonus percentage", "employee") == []


def test_stop_word_only_query_returns_no_results():
    """Return no results when normalization removes every query term."""
    document = parse_markdown(FIXTURE)
    assert retrieve(chunk_document(document), "what is the", "employee") == []


def test_invalid_retrieval_parameters_are_rejected():
    """Reject invalid limits and score thresholds."""
    document = parse_markdown(FIXTURE)
    chunks = chunk_document(document)
    with pytest.raises(ValueError, match="limit"):
        retrieve(chunks, "network policy", "employee", limit=0)
    with pytest.raises(ValueError, match="minimum_score"):
        retrieve(chunks, "network policy", "employee", minimum_score=1.1)


def test_tie_breaking_is_deterministic():
    """Resolve equal scores by stable chunk ID ordering."""
    first = Document(
        "first", "First", "ops", "public", frozenset({"employee"}), "approved", 1,
        date.today(), "alpha beta",
    )
    second = Document(
        "second", "Second", "ops", "public", frozenset({"employee"}), "approved", 1,
        date.today(), "alpha beta",
    )
    chunks = chunk_document(second) + chunk_document(first)
    results = retrieve(chunks, "alpha beta", "employee", limit=2)
    assert [chunk.document_id for chunk in results] == ["first", "second"]
