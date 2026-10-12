# Evaluation Strategy

## Principles

Measure retrieval, authorization, grounding, refusal behavior, and operational quality separately. A fluent answer is not evidence of a correct system.

## Test layers

1. Static: formatting, lint, type checks, dependency and secret scans.
2. Unit: metadata validation, chunking, role policy, version selection, citation validation, refusal logic, redaction.
3. Integration: ingestion-to-query flow using SQLite and a deterministic fake provider.
4. Security: unauthorized roles, prompt injection, stale documents, malformed metadata, oversized input, secret canaries, parallel request isolation.
5. Provider contract: timeout, malformed response, refusal, and retry mapping without real credentials.
6. Evaluation set: answerable, insufficient-evidence, authorization, stale/conflict, and injection cases.
7. Manual: clean-checkout setup, API walkthrough, README accuracy, and architecture review.

## Initial evaluation corpus

- 25 answerable questions with expected source IDs.
- 10 insufficient-evidence questions.
- 10 unauthorized questions.
- 5 stale/current conflict questions.
- 5 prompt-injection cases.

## Metrics

- Retrieval hit rate for expected source chunks.
- Unauthorized retrieval count; target: zero.
- Citation validity and source-match rate.
- Correct refusal rate.
- Grounded-answer rate on answerable cases.
- p50/p95 query latency.
- Provider error and timeout rate.
- Input, retrieved-chunk, and response size distributions.

## Release gates

- All tests pass offline.
- Zero unauthorized chunks reach generation.
- Zero fabricated citations in the evaluation set.
- Refusal behavior passes all negative cases.
- No high-severity secret or dependency findings.
- Evaluation command produces a versioned JSON result.
- Any skipped test names its prerequisite and is covered elsewhere.

## Evidence

Each release records commit, Python version, commands, test count, evaluation-set version, metrics, known limitations, and any approved waiver. Real provider credentials are prohibited in CI.
