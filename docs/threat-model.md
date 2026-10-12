# Guardrail RAG Threat Model

Status: Proposed baseline
Method: trust-boundary analysis for a local, role-aware RAG service.

## Assets

- A1: synthetic enterprise documents and classification metadata.
- A2: authorization policy and caller role.
- A3: prompts, retrieved chunks, citations, and generated answers.
- A4: provider credentials and configuration.
- A5: evaluation results, audit records, and operational metrics.
- A6: service availability and data integrity.

## Actors

- Authorized user with a declared role.
- Malicious user attempting unauthorized retrieval.
- Malicious document author or compromised ingestion source.
- Prompt-injection content in documents or questions.
- Compromised model/provider or provider outage.
- Local process or dependency with filesystem access.

## Trust boundaries

1. API client to FastAPI service: all request fields are untrusted.
2. Ingestion source to document store: metadata and content are untrusted.
3. Document store to authorization filter: policy enforcement boundary.
4. Retrieval pipeline to model provider: only authorized, bounded context may cross.
5. Provider response to API client: output is untrusted and must be validated.
6. Service to filesystem/database/logs: prevent secrets, traversal, and corruption.

## Threat register

| ID | Threat | Controls | Verification |
|---|---|---|---|
| T-01 | Unauthorized chunks enter context | Filter by role before ranking/prompt construction; fail closed | Cross-role retrieval tests |
| T-02 | Prompt injection changes policy | Treat content as data; model cannot authorize access or tools | Injection corpus |
| T-03 | Stale or draft policy is cited | Explicit status/version/effective-date ranking and validation | Stale/conflict cases |
| T-04 | Unsupported answer is fabricated | Minimum evidence threshold and refusal path | Insufficient-evidence cases |
| T-05 | Citation is fabricated or mismatched | Citations must reference retrieved chunk IDs | Citation integrity tests |
| T-06 | Sensitive data leaks through logs/errors | Structured allowlist, redaction, secret canaries | Log/response scans |
| T-07 | Oversized input causes resource exhaustion | Body, document, chunk, timeout, and concurrency limits | Abuse tests |
| T-08 | Malformed metadata bypasses policy | Schema validation and duplicate/version checks | Ingestion negative tests |
| T-09 | Provider compromise or failure | Minimal bounded context, no side effects, timeout and error mapping | Provider fake/failure tests |
| T-10 | Dependency or configuration compromise | Lock dependencies, secret scanning, safe defaults | CI checks |
| T-11 | State corruption | Atomic writes/transactions and recovery tests | Interrupt/restart tests |
| T-12 | Cross-request data leakage | Request-scoped context and no shared mutable authorization state | Parallel request tests |

## Security invariants

- Authorization is decided by server policy, never by the model.
- Unauthorized content is not retrieved, logged, or sent to a provider.
- Every citation maps to an actual retrieved chunk.
- A failed security check is an error or refusal, never a fallback.
- No real credentials or proprietary documents are required to run tests.

## Residual risk

A language model can still produce an incorrect answer from authorized context. The system reduces, measures, and exposes that risk; it does not eliminate it. Public deployment requires authentication, TLS, rate limiting, provider controls, and an explicit multi-user security review.
