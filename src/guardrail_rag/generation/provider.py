"""Provider interface for grounded answer generation."""

from dataclasses import dataclass
from typing import Protocol

from guardrail_rag.ingestion.models import Chunk


@dataclass(frozen=True)
class GenerationResult:
    answer: str
    refusal_reason: str | None = None


class AnswerProvider(Protocol):
    def answer(self, question: str, chunks: list[Chunk]) -> GenerationResult:
        """Generate an answer using only the supplied authorized chunks."""
