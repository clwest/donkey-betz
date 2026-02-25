# ADR-0001: Per-Run Ephemeral Container Execution

**Status**: Accepted
**Date**: 2026-02-25

## Context

The platform needs an internal executor to run commands and edit the repo in
managed containers. This enables the three-way collaboration loop (User + PA +
Claude Code) to produce durable artifacts — code changes, test results, diffs —
without relying on a transient CLI session that can crash or time out.

## Decision

Use **per-run ephemeral containers** (or subprocess sandboxes for MVP). Each
execution run:

1. Clones/fetches the repo at `main`
2. Creates a working branch `executor/<run_id>-<slug>`
3. Executes plan steps sequentially
4. Captures artifacts: diff patch, changed files list, command logs
5. Marks run as succeeded/failed
6. Working directory is destroyed after artifact capture

For MVP, the executor runs as a subprocess behind a clean interface so Docker
can replace it later without changing the API.

## Alternatives Considered

- **Persistent workspaces**: Simpler but leaks state between runs. Debugging
  failures is harder when prior state contaminates the environment.
- **Local execution (no isolation)**: Dangerous — commands run as the server
  process with full filesystem access.
- **SSH into host**: Operational complexity, poor auditability.

## Consequences

- **Stronger isolation**: Each run starts clean, no cross-contamination.
- **Auditability**: Every run produces a captured diff + log artifact.
- **Slightly slower cold start**: Must clone/fetch before each run.
- **Requires artifact capture**: Diff and logs must be persisted before the
  working directory is destroyed.
- **Docker upgrade path**: The subprocess interface is designed so Docker can
  be swapped in later (volume mounts, network control, resource limits).
