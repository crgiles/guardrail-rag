"""Deterministic provider used by tests and local development."""

from guardrail_rag.ingestion.models import Chunk

from .provider import GenerationResult


class FakeProvider:
    """Return an auditable answer assembled only from retrieved chunks."""

    def answer(self, question: str, chunks: list[Chunk]) -> GenerationResult:
        if not chunks:
            return GenerationResult(
                answer="I don't have enough authorized evidence to answer that.",
                refusal_reason="insufficient_evidence",
            )
        evidence = " ".join(chunk.text for chunk in chunks)
        return GenerationResult(
            answer=f"Based on the available evidence: {evidence}",
        )
