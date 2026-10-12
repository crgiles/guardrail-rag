"""Markdown parsing, validation, and deterministic chunking."""

import re
from datetime import date
from pathlib import Path

import yaml

from .models import (
    VALID_CLASSIFICATIONS,
    VALID_ROLES,
    VALID_STATUSES,
    Chunk,
    Document,
)

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)


def parse_markdown(path: Path) -> Document:
    match = _FRONTMATTER.match(path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"{path.name}: YAML frontmatter is required")
    metadata = yaml.safe_load(match.group(1)) or {}
    content = match.group(2).strip()
    required = {
        "document_id", "title", "department", "classification", "allowed_roles",
        "status", "version", "effective_date",
    }
    missing = required - metadata.keys()
    if missing:
        raise ValueError(f"{path.name}: missing metadata: {sorted(missing)}")
    roles = frozenset(metadata["allowed_roles"])
    if not roles or not roles <= VALID_ROLES:
        raise ValueError(f"{path.name}: allowed_roles contains an unknown role")
    if metadata["classification"] not in VALID_CLASSIFICATIONS:
        raise ValueError(f"{path.name}: invalid classification")
    if metadata["status"] not in VALID_STATUSES:
        raise ValueError(f"{path.name}: invalid status")
    version = metadata["version"]
    if not isinstance(version, int) or version < 1:
        raise ValueError(f"{path.name}: version must be a positive integer")
    try:
        effective_date = date.fromisoformat(str(metadata["effective_date"]))
    except ValueError as exc:
        raise ValueError(f"{path.name}: effective_date must be ISO format") from exc
    if not content:
        raise ValueError(f"{path.name}: document content cannot be empty")
    return Document(
        document_id=str(metadata["document_id"]),
        title=str(metadata["title"]),
        department=str(metadata["department"]),
        classification=str(metadata["classification"]),
        allowed_roles=roles,
        status=str(metadata["status"]),
        version=version,
        effective_date=effective_date,
        content=content,
        supersedes=metadata.get("supersedes"),
    )


def chunk_document(document: Document, max_words: int = 120) -> list[Chunk]:
    if max_words < 1:
        raise ValueError("max_words must be positive")
    words = document.content.split()
    chunks: list[Chunk] = []
    for ordinal, start in enumerate(range(0, len(words), max_words)):
        text = " ".join(words[start:start + max_words])
        chunks.append(Chunk(
            chunk_id=f"{document.document_id}:{ordinal}",
            document_id=document.document_id,
            text=text,
            ordinal=ordinal,
            document=document,
        ))
    return chunks
