"""Offline evaluation runner for retrieval, citations, and refusal behavior."""

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from guardrail_rag.generation.fake import FakeProvider
from guardrail_rag.ingestion.corpus import load_corpus
from guardrail_rag.retrieval.simple import retrieve


@dataclass(frozen=True)
class EvaluationCase:
    """One expected retrieval and generation behavior case."""
    id: str
    question: str
    role: str
    expected: str
    source_ids: list[str]


@dataclass(frozen=True)
class CaseResult:
    """Observed outcome for one evaluation case."""
    id: str
    passed: bool
    expected: str
    actual: str
    citations_valid: bool
    retrieved_count: int
    elapsed_ms: float


def load_cases(path: Path) -> list[EvaluationCase]:
    """Load evaluation cases from a JSON file."""
    records = json.loads(path.read_text(encoding="utf-8"))
    return [EvaluationCase(**record) for record in records]


def evaluate(corpus_path: Path, cases_path: Path) -> dict:  # pylint: disable=too-many-locals
    """Evaluate retrieval and refusal behavior against a corpus and cases."""
    store = load_corpus(corpus_path)
    provider = FakeProvider()
    cases = load_cases(cases_path)
    results: list[CaseResult] = []

    for case in cases:
        started = time.perf_counter()
        chunks = retrieve(list(store.chunks), case.question, case.role)
        generation = provider.answer(case.question, chunks)
        actual = "refusal" if generation.refusal_reason else "answer"
        actual_ids = {chunk.document_id for chunk in chunks}
        # Refusals must not emit citations, even if lexical retrieval found noise.
        citations_valid = (
            actual == "refusal"
            or actual_ids <= set(case.source_ids)
            if case.source_ids
            else actual == "refusal" and not generation.answer.startswith("Based on")
        )
        passed = actual == case.expected and citations_valid
        results.append(CaseResult(
            id=case.id,
            passed=passed,
            expected=case.expected,
            actual=actual,
            citations_valid=citations_valid,
            retrieved_count=len(chunks),
            elapsed_ms=round((time.perf_counter() - started) * 1000, 3),
        ))

    passed = sum(result.passed for result in results)
    answer_cases = [result for result in results if result.expected == "answer"]
    refusal_cases = [result for result in results if result.expected == "refusal"]
    unauthorized = [
        result for result in results
        if result.id.startswith("unauthorized-") and result.retrieved_count > 0
    ]
    return {
        "evaluation_version": cases_path.stem,
        "total_cases": len(results),
        "passed_cases": passed,
        "failed_cases": len(results) - passed,
        "retrieval_hit_rate": round(
            sum(result.retrieved_count > 0 for result in answer_cases) / len(answer_cases), 3
        ) if answer_cases else 0.0,
        "citation_validity_rate": round(
            sum(result.citations_valid for result in results) / len(results), 3
        ) if results else 0.0,
        "correct_refusal_rate": round(
            sum(result.passed for result in refusal_cases) / len(refusal_cases), 3
        ) if refusal_cases else 0.0,
        "unauthorized_retrieval_count": len(unauthorized),
        "elapsed_ms": round(sum(result.elapsed_ms for result in results), 3),
        "results": [asdict(result) for result in results],
    }


def main() -> None:
    """Run the selected offline evaluation version and print JSON."""
    parser = argparse.ArgumentParser(description="Run offline Guardrail RAG evaluation")
    parser.add_argument("--version", default="v1", choices=("v1", "v2"))
    args = parser.parse_args()
    root = Path(__file__).parents[3]
    report = evaluate(
        root / "data" / "synthetic",
        root / "data" / "evals" / f"{args.version}.json",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
