# pylint: disable=missing-module-docstring,missing-function-docstring

from datetime import date
from pathlib import Path

import pytest

from guardrail_rag.ingestion.corpus import CorpusError, DocumentStore, load_corpus
from guardrail_rag.ingestion.models import Document

CORPUS = Path(__file__).parents[2] / "data" / "synthetic"


def test_load_corpus_selects_current_approved_version():
    store = load_corpus(CORPUS)

    document_ids = {document.document_id for document in store.documents}
    assert "net-change-policy-003" in document_ids
    assert "net-change-policy-002" not in document_ids
    assert all(chunk.document_id in document_ids for chunk in store.chunks)


def test_store_filters_by_role_and_fails_closed_for_unknown_role():
    store = load_corpus(CORPUS)

    assert store.for_role("employee")
    assert not store.for_role("not-a-role")


def test_duplicate_document_ids_are_rejected():
    document = Document(
        "same", "Title", "ops", "internal", frozenset({"employee"}), "approved", 1,
        date(2026, 1, 1), "content",
    )
    with pytest.raises(CorpusError, match="duplicate document_id"):
        DocumentStore([document, document])


def test_multiple_approved_versions_in_one_family_are_rejected():
    first = Document(
        "policy-1", "Title", "ops", "internal", frozenset({"employee"}), "approved", 1,
        date(2025, 1, 1), "content",
    )
    second = Document(
        "policy-2", "Title", "ops", "internal", frozenset({"employee"}), "approved", 2,
        date(2026, 1, 1), "content", supersedes="policy-1",
    )
    with pytest.raises(CorpusError, match="multiple approved"):
        DocumentStore([first, second])
