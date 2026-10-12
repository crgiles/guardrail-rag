"""Fail-closed authorization policy for document access."""

from guardrail_rag.ingestion.models import Chunk


def is_authorized(chunk: Chunk, caller_role: str) -> bool:
    """Return whether a caller role may access a chunk's document."""
    return caller_role in chunk.document.allowed_roles


def filter_authorized(chunks: list[Chunk], caller_role: str) -> list[Chunk]:
    """Return only chunks authorized for the caller role."""
    return [chunk for chunk in chunks if is_authorized(chunk, caller_role)]
