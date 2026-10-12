# Guardrail RAG Requirements

Status: Proposed baseline
Scope: local API that answers questions over synthetic enterprise documents.

## Goals

1. Ingest versioned Markdown documents with explicit classification and role metadata.
2. Retrieve only documents the requesting role is authorized to see.
3. Return grounded answers with source citations.
4. Refuse unsupported, ambiguous, stale, or unauthorized questions safely.
5. Provide deterministic evaluation, security tests, and observable request metrics.
6. Keep the first release local-first, inexpensive, and easy to run from a clean checkout.

## Non-goals

- Model training or fine-tuning.
- Production multi-tenant hosting.
- Kubernetes or distributed deployment.
- Real company data, credentials, or proprietary documents.
- Autonomous side effects or unrestricted agents.
- Treating model output as an authorization decision.

## Functional requirements

### FR-1 Documents

- Accept Markdown documents from the synthetic corpus.
- Store stable document ID, title, department, classification, allowed roles, status, version, effective date, and superseded document ID.
- Reject malformed metadata and duplicate active versions.

### FR-2 Retrieval

- Chunk documents deterministically.
- Support metadata filtering before generation.
- Prefer approved, current documents over superseded or draft documents.
- Preserve document and chunk provenance.

### FR-3 Answers

- Accept a question and caller role.
- Return answer, citations, retrieval metadata, refusal reason when applicable, and request ID.
- Cite only retrieved chunks supplied to the model.
- Refuse when evidence is insufficient or the caller lacks authorization.

### FR-4 Security

- Authorization filtering occurs before prompt construction.
- Content, citations, and model output cannot grant permissions.
- Prompt-injection text is treated as untrusted document content.
- Secrets never enter fixtures, logs, responses, or the repository.
- Enforce request, document, and response size limits.

### FR-5 Evaluation and operations

- Provide an offline evaluation command with answerable, insufficient-evidence, authorization, stale-document, and injection cases.
- Record latency, retrieval count, refusal category, token/cost fields when available, and model/provider identifier without secrets.
- Expose health and configuration-safe diagnostics.

## Quality requirements

- Python 3.11+.
- Reproducible local setup with documented commands.
- Unit and integration tests run without network access or real credentials.
- Provider access is isolated behind an interface and replaceable with a deterministic fake.
- CI must run lint, tests, and secret scanning.
- Default behavior is fail-closed for authorization and evidence checks.

## Initial scale target

- 20–50 synthetic documents.
- Three roles: `employee`, `network_engineer`, `security_admin`.
- At least 50 evaluation cases.
- Local SQLite persistence initially; PostgreSQL/pgvector is a later adapter.
