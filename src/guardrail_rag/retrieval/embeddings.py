"""Optional semantic retrieval with a deterministic local embedding backend.

# pylint: disable=duplicate-code
"""

import hashlib
import math
import re

from guardrail_rag.authorization.policy import filter_authorized
from guardrail_rag.ingestion.models import Chunk


class HashEmbeddingModel:  # pylint: disable=too-few-public-methods
    """Create reproducible token vectors without network calls or model weights."""

    def __init__(self, dimensions: int = 256) -> None:
        if dimensions < 8:
            raise ValueError("dimensions must be at least eight")
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        """Map normalized tokens into a signed, L2-normalized vector."""
        vector = [0.0] * self.dimensions
        for token in re.findall(r"[a-z0-9]+", text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[index] += 1.0 if digest[4] & 1 else -1.0
        magnitude = math.sqrt(sum(value * value for value in vector))
        return [value / magnitude for value in vector] if magnitude else vector


def _cosine(left: list[float], right: list[float]) -> float:
    """Return cosine similarity for already normalized or zero vectors."""
    return sum(a * b for a, b in zip(left, right))


# pylint: disable=duplicate-code
def retrieve_semantic(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    chunks: list[Chunk],
    query: str,
    caller_role: str,
    limit: int = 1,
    minimum_score: float = 0.15,
    model: HashEmbeddingModel | None = None,
) -> list[Chunk]:
    """Rank authorized chunks by local semantic similarity."""
    if not query.strip():
        raise ValueError("query cannot be empty")
    if limit < 1:
        raise ValueError("limit must be positive")
    if not 0 <= minimum_score <= 1:
        raise ValueError("minimum_score must be between zero and one")

    model = model or HashEmbeddingModel()
    query_vector = model.embed(query)
    scored = []
    for chunk in filter_authorized(chunks, caller_role):
        score = _cosine(query_vector, model.embed(f"{chunk.document.title} {chunk.text}"))
        if score >= minimum_score:
            scored.append((score, chunk.chunk_id, chunk))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [chunk for _, _, chunk in scored[:limit]]
