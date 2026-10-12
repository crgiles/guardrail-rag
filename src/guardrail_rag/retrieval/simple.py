"""Deterministic lexical retrieval over authorized chunks."""

import re

from guardrail_rag.authorization.policy import filter_authorized
from guardrail_rag.ingestion.models import Chunk

_STOP_WORDS = frozenset(
    {
        "a", "an", "and", "are", "for", "how", "in", "is", "of", "on", "the",
        "to", "what", "which", "who", "where", "with",
    }
)


def _normalize(term: str) -> str:
    """Apply minimal stemming so singular/plural forms match."""
    aliases = {"required": "require", "approved": "approve", "approvals": "approval"}
    if term in aliases:
        return aliases[term]
    if term.endswith("ies") and len(term) > 4:
        return term[:-3] + "y"
    if term.endswith("s") and len(term) > 3:
        return term[:-1]
    return term


def _terms(text: str) -> set[str]:
    """Normalize text into comparable terms while dropping common filler words."""
    return {
        _normalize(term)
        for term in re.findall(r"[a-z0-9]+", text.lower())
        if term not in _STOP_WORDS
    }


def retrieve(
    chunks: list[Chunk],
    query: str,
    caller_role: str,
    limit: int = 1,
    minimum_score: float = 0.5,
) -> list[Chunk]:
    """Return authorized chunks ranked by normalized query-term overlap.

    Authorization happens before scoring, and the explicit sort keys make
    results reproducible when several chunks have the same overlap score.
    """
    if not query.strip():
        raise ValueError("query cannot be empty")
    if limit < 1:
        raise ValueError("limit must be positive")
    if not 0 <= minimum_score <= 1:
        raise ValueError("minimum_score must be between zero and one")

    query_terms = _terms(query)
    if not query_terms:
        return []

    authorized_chunks = filter_authorized(chunks, caller_role)
    scored: list[tuple[float, int, str, Chunk]] = []
    for chunk in authorized_chunks:
        # Include the title because short policy documents often put the key
        # topic in metadata rather than repeating it in every paragraph.
        chunk_terms = _terms(f"{chunk.document.title} {chunk.text}")
        # Normalize by query length so a short query cannot win merely because
        # it has fewer terms; chunk size then provides a stable tie-breaker.
        score = len(query_terms & chunk_terms) / len(query_terms)
        # Negative wording should not make a handbook look authoritative.
        if "does not define" in chunk.text.lower():
            score -= 0.25
        if score >= minimum_score:
            scored.append((score, -len(chunk_terms), chunk.chunk_id, chunk))

    scored.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [chunk for _, _, _, chunk in scored[:limit]]
