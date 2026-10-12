"""Validated document and chunk models."""

from dataclasses import dataclass
from datetime import date

VALID_ROLES = frozenset({"employee", "network_engineer", "security_admin"})
VALID_CLASSIFICATIONS = frozenset({"public", "internal", "confidential", "restricted"})
VALID_STATUSES = frozenset({"approved", "draft", "superseded"})


@dataclass(frozen=True)
class Document:  # pylint: disable=too-many-instance-attributes
    """Validated document and its authorization metadata."""
    document_id: str
    title: str
    department: str
    classification: str
    allowed_roles: frozenset[str]
    status: str
    version: int
    effective_date: date
    content: str
    supersedes: str | None = None


@dataclass(frozen=True)
class Chunk:
    """A deterministic, authorized-retrieval unit from a document."""
    chunk_id: str
    document_id: str
    text: str
    ordinal: int
    document: Document
