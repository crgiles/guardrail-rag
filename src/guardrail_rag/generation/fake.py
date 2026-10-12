"""Deterministic provider used by tests and local development."""

import re

from guardrail_rag.ingestion.models import Chunk

from .provider import GenerationResult

_INJECTION_PATTERNS = (
    r"ignore\s+(all|any|previous)\s+(instructions|policies)",
    r"disregard\s+(authorization|security|all)",
    r"reveal\s+(restricted|secret|hidden)",
)


def _looks_like_injection(question: str) -> bool:
    return any(re.search(pattern, question, re.IGNORECASE) for pattern in _INJECTION_PATTERNS)


class FakeProvider:
    """Return an auditable answer assembled only from retrieved chunks."""

    def answer(self, question: str, chunks: list[Chunk]) -> GenerationResult:
        if _looks_like_injection(question):
            return GenerationResult(
                answer="I can't comply with an instruction to bypass safeguards.",
                refusal_reason="unsafe_instruction",
            )
        if not chunks:
            return GenerationResult(
                answer="I don't have enough authorized evidence to answer that.",
                refusal_reason="insufficient_evidence",
            )
        evidence = " ".join(chunk.text for chunk in chunks)
        return GenerationResult(
            answer=f"Based on the available evidence: {evidence}",
        )
