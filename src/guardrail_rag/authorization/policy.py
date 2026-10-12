"""Fail-closed authorization policy for document access."""

from guardrail_rag.ingestion.models import Chunk


def is_authorized(chunk: Chunk, caller_role: str) -> bool:
    """Return whether a caller role may access a chunk's document."""
    return caller_role in chunk.document.allowed_roles


def filter_authorized(chunks: list[Chunk], caller_role: str) -> list[Chunk]:
    """Return only chunks authorized for the caller role."""
    # Keep this filter separate from scoring: unauthorized text must never
    # influence ranking or reach a provider, even as a high-scoring distractor.
    return [chunk for chunk in chunks if is_authorized(chunk, caller_role)]
