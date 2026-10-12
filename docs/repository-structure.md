# Repository Structure

```text
guardrail-rag/
├── src/guardrail_rag/
│   ├── api/             FastAPI routes, schemas, and dependency wiring
│   ├── authorization/   role and classification policy enforcement
│   ├── ingestion/       document parsing, validation, chunking
│   ├── retrieval/       indexing, filtering, ranking, provenance
│   ├── generation/      provider interface, prompts, refusal handling
│   ├── evaluation/      offline evaluation runner and result models
│   ├── observability/   safe metrics, request IDs, structured events
│   └── settings.py      environment-backed configuration
├── tests/
│   ├── unit/
│   ├── integration/
│   └── security/
├── data/
│   ├── synthetic/       fictional Northstar Communications documents
│   └── evals/            versioned questions and expected behaviors
├── scripts/             setup, corpus, evaluation, and release helpers
├── docs/                requirements, ADRs, threat model, evaluation
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## Dependency direction

- `api` wires components but owns no retrieval or policy logic.
- `authorization` is independent of model/provider code.
- `retrieval` receives already-validated policy inputs and returns provenance.
- `generation` receives only authorized chunks.
- `evaluation` uses public interfaces and deterministic fakes.
- Tests may exercise public boundaries; production code never imports tests.

## Placement rules

- New security behavior requires a negative test and threat-model update.
- New provider behavior belongs behind `generation` interfaces.
- New persisted fields require backward-read or migration behavior.
- New dependencies require justification, pinning, and a threat review.
