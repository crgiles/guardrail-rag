# Guardrail RAG

A local, evaluation-driven reference implementation for secure enterprise retrieval-augmented generation.

## Status

Planning and project skeleton. The first milestone is a role-aware RAG API over synthetic Northstar Communications documents.

## Goals

- authorization-aware retrieval
- cited answers grounded in retrieved chunks
- safe refusal when evidence is missing
- prompt-injection and stale-document tests
- provider-independent, offline-testable architecture

## Development

Requirements: Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
```

See `docs/` for requirements, architecture, threat model, evaluation strategy, and acceptance criteria.
