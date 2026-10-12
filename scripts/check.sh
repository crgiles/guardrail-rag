#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON="${PYTHON:-python}"

"$PYTHON" -m ruff check src tests
"$PYTHON" -m pylint src tests --score=y
"$PYTHON" -m pytest -q
"$PYTHON" -m guardrail_rag.evaluation.runner --version v2

echo "All quality checks passed."
