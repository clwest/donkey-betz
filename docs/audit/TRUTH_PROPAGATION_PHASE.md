# Truth Propagation Phase

Date: 2026-05-04

## Purpose

This phase cleaned up the repo's highest-risk silent-success and ambiguous-failure paths so degraded state is visible instead of being mistaken for success.

- eliminate silent success
- eliminate ambiguous `None` / fallback behavior
- expose degraded and fallback states in returned results or status metadata

## Context-Kit Verification Snapshot

### verify

- `total`: 6
- `VERIFIED`: 2
- `DOC_ONLY`: 4
- `CONFLICT`: 0
- `UNKNOWN`: 0

### behavior scans

| scope | total files scanned | files with signals | entrypoint files | risk categories |
| --- | ---: | ---: | ---: | ---: |
| `celery` | 21 | 20 | 8 | 12 |
| `agents` | 211 | 150 | 23 | 12 |
| `spiders` | 177 | 172 | 11 | 12 |

Top behavioral surfaces from the latest scans:

- `celery`: `core/tasks.py`, `core/tasks_agents.py`, `core/tasks_media.py`
- `agents`: `core/agents/base_agent.py`, `core/agents/code_review_agent.py`, `agents/executors/base_executor.py`
- `spiders`: `ai_core/spiders/spider_orchestrator.py`, `ai_core/spiders/api_manager.py`, `ai_core/spiders/consciousness.py`, `ai_core/spiders/spider_data_router.py`

### coverage snapshots

| scope | total files | covered files | skipped files | unknown files | coverage files % | coverage bytes % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `core` | 1387 | 1386 | 1 | 0 | 99.9 | 54.5 |
| `agents` | 211 | 209 | 0 | 2 | 99.1 | 98.5 |
| `spiders` | 177 | 177 | 0 | 0 | 100.0 | 100.0 |

## Layers Audited

- Celery
- Agents / `base_agent`
- Router / registry
- Code review agent
- Spiders

## P0 / P1 Fixes Completed

- Fail-open governance in spider network now fails closed.
- CourtListener fake-ready fallback now returns degraded output instead of pretending success.
- PA TTS failure signaling now returns explicit failure metadata.
- Pilot metric collectors now expose query failures instead of silently converting them to healthy-looking zero values.
- Auto-research now surfaces partial-failure metadata.
- Celery sync / repair commands now log tracebacks and fail non-zero on critical sync errors.
- Delegation and autopilot malformed results now fail closed instead of counting as success.
- Router and registry fallback paths now expose resolution metadata.
- Code review agent no longer returns clean success when no real review completed.
- Spider orchestrator mock fallback now surfaces fallback metadata.
- Scheduled spider batches now summarize failures at the top level.
- Spider consciousness health now exposes fallback and degraded-state metadata.
- Spider data router now surfaces route outcomes and delivery failures.
- Spider API manager now exposes request and fallback failure metadata while preserving legacy return values.

## Tests Added / Updated

- `core/tests/test_spider_network_governance.py`
- `core/tests/test_spider_orchestrator_mock_fallback.py`
- `core/tests/test_consciousness_health_visibility.py`
- `core/tests/test_agent_result_success_defaults.py`
- `core/tests/test_code_review_agent_fake_success.py`
- `core/tests/test_pilot_metrics.py`
- `core/tests/test_pa_tts_task.py`
- `core/tests/test_auto_research_metadata.py`
- `core/tests/test_celery_sync_commands.py`
- `core/tests/test_base_agent_workspace_write_visibility.py`
- `core/tests/test_base_agent_doc_write_failure_visibility.py`
- `core/tests/test_spider_data_router_observability.py`
- `core/tests/test_api_manager_failure_metadata.py`

## Current Verification State

- Focused test suites passed in the latest checkpoint.
- `context-kit verify --json` reported `0 CONFLICT` and `0 UNKNOWN`.
- The spider, agents, and celery behavior scans all completed successfully.

## Definition of Truth Propagation

For this repository, truth propagation means:

- failures are surfaced as failures, not as clean success
- fallback behavior is explicitly labeled when it is used
- partial failures are summarized at the top level, not only buried in nested records
- health and readiness outputs expose degraded state when they are based on fallback data
- legacy caller compatibility is preserved when possible, but metadata is added so ambiguity is removed

## Remaining Deferred P2s

- `ai_core/spiders/spider_orchestrator.py` metrics broadcast and count-detail visibility
- `ai_core/spiders/api_manager.py` lower-level quota and health reason codes
- `ai_core/spiders/consciousness.py` fallback metadata in non-health helper paths
- `core/agents/registry.py` lookup helper observability
- `ai_core/spiders/spider_data_router.py` deeper per-consumer delivery diagnostics if desired
- `core/agents/base_agent.py` best-effort enrichment and knowledge-share observability

## Recommended Next Audit Layer

`ai_core/spiders/spider_orchestrator.py`

Reason: it is still the highest behavioral risk surface in the spider scan, even after the mock-fallback visibility patch. The remaining work there is mostly observability rather than silent-success correction.
