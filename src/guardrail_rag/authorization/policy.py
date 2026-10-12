"""Fail-closed authorization policy for document access."""

from guardrail_rag.ingestion.models import Chunk


def is_authorized(chunk: Chunk, caller_role: str) -> bool:
    return caller_role in chunk.document.allowed_roles


def filter_authorized(chunks: list[Chunk], caller_role: str) -> list[Chunk]:
    return [chunk for chunk in chunks if is_authorized(chunk, caller_role)]
