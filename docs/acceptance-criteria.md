# Acceptance Criteria

## First vertical slice

- AC-01: A clean checkout installs and runs locally with documented commands.
- AC-02: Synthetic Markdown documents validate, chunk, and persist with metadata.
- AC-03: A query accepts a caller role and returns a request ID.
- AC-04: Only role-authorized chunks are eligible for retrieval and generation.
- AC-05: An answer cites real retrieved document/chunk IDs.
- AC-06: Missing evidence produces a structured refusal, not a guessed answer.
- AC-07: Current approved content outranks superseded or draft content.
- AC-08: Prompt-injection text cannot change authorization or activate tools.
- AC-09: Malformed metadata, oversized inputs, and unsupported files fail safely.
- AC-10: Provider errors and timeouts produce stable non-secret error responses.

## Engineering quality

- AC-11: Tests run without network access or real credentials.
- AC-12: Provider access is replaceable through a documented interface.
- AC-13: Logs contain request ID and safe metrics but no prompts, secrets, or unauthorized content.
- AC-14: Parallel requests cannot share caller authorization state.
- AC-15: CI runs lint, tests, and secret scanning.
- AC-16: README explains architecture, threat model, evaluation, and limitations.

## Release evidence

- Exact install and test commands recorded.
- Test count and evaluation-set version recorded.
- Retrieval, citation, refusal, security, and latency metrics recorded.
- Known limitations are explicit.
- Requirements, threat model, ADR, and repository structure match shipped behavior.
