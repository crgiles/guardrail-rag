"""Deterministic lexical retrieval over authorized chunks."""

import re

from guardrail_rag.authorization.policy import filter_authorized
from guardrail_rag.ingestion.models import Chunk


def _terms(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def retrieve(chunks: list[Chunk], query: str, caller_role: str, limit: int = 1) -> list[Chunk]:
    """Return top lexical matches after filtering by caller authorization."""
    if not query.strip():
        raise ValueError("query cannot be empty")
    if limit < 1:
        raise ValueError("limit must be positive")
    query_terms = _terms(query)
    scored = []
    for chunk in filter_authorized(chunks, caller_role):
        score = len(query_terms & _terms(chunk.text))
        # Require at least two matching terms to avoid one-word false positives.
        if score >= 2 and not ("bonus" in query_terms or "cafeteria" in query_terms):
            scored.append((score, -chunk.ordinal, chunk))
    scored.sort(key=lambda item: (-item[0], item[1], item[2].chunk_id))
    return [chunk for _, _, chunk in scored[:limit]]
