import json
from pathlib import Path

import pytest

from guardrail_rag.evaluation.runner import evaluate

ROOT = Path(__file__).parents[2]


@pytest.mark.parametrize("version, expected_cases", [("v1", 15), ("v2", 15)])
def test_evaluation_report_passes_corpus(version, expected_cases):
    report = evaluate(ROOT / "data" / "synthetic", ROOT / "data" / "evals" / f"{version}.json")

    assert report["total_cases"] == expected_cases
    assert report["failed_cases"] == 0
    assert report["passed_cases"] == expected_cases
    assert report["unauthorized_retrieval_count"] == 0
    assert report["correct_refusal_rate"] == 1.0


def test_evaluation_report_is_json_serializable():
    report = evaluate(ROOT / "data" / "synthetic", ROOT / "data" / "evals" / "v1.json")
    json.dumps(report)
