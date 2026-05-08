# Truth Propagation Principles

This system is designed to ensure that execution state always reflects reality.

## Core Principles

1. No silent success
   - A failure must never appear as a success.

2. No ambiguous None
   - Null/None values must not mask failure conditions.

3. Explicit fallback visibility
   - All fallback paths must expose:
     - `fallback_used`
     - `fallback_type`
     - `reason`

4. Partial failure must be surfaced
   - Systems must expose:
     - `partial_failure`
     - `failure_count`
     - failure context

5. External failures must be classified
   - API, DB, and system failures must include:
     - `failure_type`
     - `error_type`
     - context

6. Observability over assumptions
   - Logs are not enough.
   - Critical state must be returned as structured data.

7. System state must reflect system truth
   - Health, readiness, and outputs must not rely on hidden fallback values.

---

## Definition: Truth Propagation

Truth propagation means that every layer of the system:

- detects failure
- classifies failure
- surfaces failure
- preserves failure context

so that no part of the system can silently degrade without being visible.

---

## Scope

These principles apply to:

- Celery task orchestration
- Agent delegation and execution
- Router and registry resolution
- External API interactions
- Spider ingestion and routing
- System health and monitoring

---

## Enforcement

These principles are enforced through:

- structured return payloads
- fallback metadata
- partial failure flags
- targeted tests
- context-kit verification and behavior scans
