from datetime import date
from pathlib import Path

import pytest

from guardrail_rag.authorization.policy import filter_authorized
from guardrail_rag.ingestion.markdown import chunk_document, parse_markdown
from guardrail_rag.ingestion.models import Document
from guardrail_rag.retrieval.simple import retrieve

FIXTURE = Path(__file__).parents[2] / "data" / "synthetic" / "network-policy.md"


def test_parse_and_chunk_document():
    document = parse_markdown(FIXTURE)
    assert document.document_id == "net-change-policy-003"
    assert document.effective_date == date(2026, 1, 15)
    assert chunk_document(document, max_words=5)[0].chunk_id == "net-change-policy-003:0"


def test_invalid_frontmatter_is_rejected(tmp_path):
    path = tmp_path / "bad.md"
    path.write_text("# no metadata", encoding="utf-8")
    with pytest.raises(ValueError, match="frontmatter"):
        parse_markdown(path)


def test_retrieval_filters_before_scoring():
    public = Document("public", "Public", "ops", "public", frozenset({"employee"}), "approved", 1, date.today(), "network change policy")
    restricted = Document("restricted", "Restricted", "security", "restricted", frozenset({"security_admin"}), "approved", 1, date.today(), "network change policy")
    chunks = chunk_document(public) + chunk_document(restricted)
    employee_results = retrieve(chunks, "network change policy", "employee")
    assert [chunk.document_id for chunk in employee_results] == ["public"]
    assert filter_authorized(chunks, "employee")[0].document_id == "public"
