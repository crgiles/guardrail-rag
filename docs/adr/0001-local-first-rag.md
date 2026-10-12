# ADR-0001: Local-First, Provider-Agnostic RAG Architecture

Status: Accepted for initial implementation

## Context

The portfolio project must demonstrate enterprise AI engineering without requiring proprietary data, expensive infrastructure, or a specific model vendor. The first milestone must be testable offline and understandable to reviewers.

## Decision

Build a Python FastAPI service with these boundaries:

- ingestion validates documents and metadata;
- storage persists document/chunk records;
- authorization filters records before retrieval results enter generation;
- retrieval ranks authorized chunks;
- generation uses a provider interface with a deterministic fake for tests;
- evaluation runs offline against a versioned test set;
- observability records safe request metrics only.

Use SQLite for the first implementation. Keep repository interfaces database-neutral so PostgreSQL/pgvector can be added later. Use Docker only after the local vertical slice works.

## Consequences

Positive:

- Fast local iteration and deterministic CI.
- No real provider credentials needed for tests.
- Clear security boundary and replaceable provider.
- Easy public demonstration.

Tradeoffs:

- SQLite is not the final scale target.
- Initial retrieval may be simpler than production hybrid search.
- Provider-specific performance and cost behavior require later integration tests.

## Rejected alternatives

- Starting with Kubernetes: operational complexity before product behavior.
- Embedding the application inside Hermes: couples the portfolio artifact to one agent runtime.
- Starting with an autonomous agent: introduces side effects before retrieval and authorization are proven.
