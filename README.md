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

Run the API locally with the deterministic fake provider:

```bash
uvicorn guardrail_rag.api.app:app --reload
```

For live generation through OpenRouter, set `GUARDRAIL_RAG_PROVIDER=openrouter`,
`OPENROUTER_API_KEY`, and optionally `OPENROUTER_MODEL` in your environment.
Tests never require an API key.

Then query it:

```bash
curl -s http://127.0.0.1:8000/query \\
  -H 'content-type: application/json' \\
  -d '{"question":"What approvals are required for a production network change?","role":"network_engineer"}'
```

See `docs/` for requirements, architecture, threat model, evaluation, and acceptance criteria.
