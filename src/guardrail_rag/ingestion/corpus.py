"""Load and select a validated synthetic document corpus."""

from collections.abc import Iterable
from pathlib import Path

from .markdown import chunk_document, parse_markdown
from .models import Chunk, Document


class CorpusError(ValueError):
    """Raised when the corpus is invalid or internally inconsistent."""


def _family_key(document: Document) -> str:
    """Return the version family key used by supersedes links."""
    return document.supersedes or document.document_id


def _select_current(documents: Iterable[Document]) -> list[Document]:
    grouped: dict[str, list[Document]] = {}
    for document in documents:
        grouped.setdefault(_family_key(document), []).append(document)

    selected: list[Document] = []
    for family, versions in grouped.items():
        approved = [document for document in versions if document.status == "approved"]
        if len(approved) > 1:
            raise CorpusError(f"multiple approved versions in document family: {family}")
        if approved:
            selected.append(approved[0])
    return sorted(selected, key=lambda document: document.document_id)


class DocumentStore:
    """Immutable in-memory store of the current approved document corpus."""

    def __init__(self, documents: Iterable[Document]):
        documents = list(documents)
        ids = [document.document_id for document in documents]
        if len(ids) != len(set(ids)):
            raise CorpusError("duplicate document_id")
        self._documents = tuple(_select_current(documents))
        self._chunks = tuple(
            chunk for document in self._documents for chunk in chunk_document(document)
        )

    @property
    def documents(self) -> tuple[Document, ...]:
        return self._documents

    @property
    def chunks(self) -> tuple[Chunk, ...]:
        return self._chunks

    def for_role(self, role: str) -> tuple[Chunk, ...]:
        """Return only chunks authorized for role; unknown roles fail closed."""
        return tuple(chunk for chunk in self._chunks if role in chunk.document.allowed_roles)


def load_corpus(directory: Path) -> DocumentStore:
    """Load all Markdown files beneath directory into a validated store."""
    if not directory.is_dir():
        raise CorpusError(f"corpus directory does not exist: {directory}")
    paths = sorted(directory.glob("*.md"))
    if not paths:
        raise CorpusError(f"corpus directory contains no Markdown files: {directory}")
    try:
        documents = [parse_markdown(path) for path in paths]
        return DocumentStore(documents)
    except (OSError, ValueError) as exc:
        if isinstance(exc, CorpusError):
            raise
        raise CorpusError(str(exc)) from exc
