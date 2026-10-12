# ADR-0001: Localhost-first vanilla web UI over the existing Hermes runtime

- Status: Accepted
- Date: 2026-10-12
- Decision owners: Hermes WebUI maintainers

## Context

Hermes already owns agent execution, provider integration, memory, skills, scheduling, profiles, and runtime state. The WebUI needs to expose that capability without creating a second agent implementation or a heavy frontend build system. The principal deployment is a self-hosted operator console, often reached through an SSH tunnel or an equivalent private access layer.

Alternatives considered:

1. Build a separate service and duplicate agent/runtime state: high drift and security risk.
2. Adopt a SPA framework and bundler: richer component ecosystem, but adds build/runtime complexity to a lightweight self-hosted tool.
3. Use the existing Python HTTP server and static vanilla JavaScript: minimal deployment, direct integration, easy inspection, and no build step.

## Decision

Use the existing Python server as a thin routing and security boundary, delegate domain behavior to `api/`, and serve a framework-free static frontend from `static/`. The WebUI calls the existing Hermes runtime rather than reimplementing agent behavior. Bind to `127.0.0.1` by default; operators who need remote access must use an authenticated tunnel or explicitly configure a protected access layer.

SSE remains the streaming transport for chat/activity, with durable session/turn state and server-side ownership checks. Filesystem access is constrained to configured workspace roots. Security controls are implemented server-side and are not delegated to frontend behavior.

## Consequences

Positive:

- Small install and simple source-checkout operation.
- One source of truth for agent behavior and credentials.
- Easy terminal/agent modification and browser smoke testing.
- Localhost default reduces accidental exposure.

Negative:

- Vanilla JS requires discipline around module boundaries and DOM safety.
- SSE reconnect and race handling are application responsibilities.
- The Python HTTP surface is not a general-purpose public production server.
- Multi-user tenancy, broad public exposure, and richer client composition require new design work.

## Rejected alternatives

- Duplicating the agent: rejected because it creates state divergence and expands the trust boundary.
- Public-by-default binding: rejected because a local operator console is not safe to expose without an access layer.
- Client-only authorization: rejected because browsers and model output are untrusted.

## Follow-up constraints

Any proposal that changes the runtime authority, exposes a new network boundary, adds a parser/tool/plugin, or introduces multi-user access must update this ADR or add a superseding ADR and update the threat model.
