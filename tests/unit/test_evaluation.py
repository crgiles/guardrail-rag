import json
from pathlib import Path

from guardrail_rag.evaluation.runner import evaluate

ROOT = Path(__file__).parents[2]


def test_evaluation_report_passes_initial_corpus():
    report = evaluate(ROOT / "data" / "synthetic", ROOT / "data" / "evals" / "v1.json")

    assert report["total_cases"] == 15
    assert report["failed_cases"] == 0
    assert report["passed_cases"] == 15
    assert report["unauthorized_retrieval_count"] == 0
    assert report["correct_refusal_rate"] == 1.0


def test_evaluation_report_is_json_serializable():
    report = evaluate(ROOT / "data" / "synthetic", ROOT / "data" / "evals" / "v1.json")
    json.dumps(report)
