# Phase 3 Applied Notes — Evidence Pack Assembly + Session Trace + Replay

**Session:** 963
**Date:** February 7, 2026
**Branch:** `session-963/phase3-evidence-trace`

## Summary

Phase 3 turns deliberation sessions into fully auditable, replayable records. Two builder services incrementally assemble structured JSON on DeliberationSession's `evidence_pack` and `trace` JSONFields as conversations progress. No migrations needed — uses existing schema from Phase 1.

## New Files

| File | Purpose |
|------|---------|
| `core/services/evidence_pack_builder.py` | EvidencePackBuilder — sources, claims, contradictions, internal refs, memory retrievals |
| `core/services/session_trace_builder.py` | SessionTraceBuilder — turn timeline, contract snapshots, tool calls, decisions, performance |
| `core/tests/test_phase3_evidence_trace.py` | 33 tests covering builders, API endpoints, auth, and error safety |

## Modified Files

| File | Change |
|------|--------|
| `core/conversation_orchestrator.py` | 4 hooks: init pack+trace after session creation, append turn+contradiction after each turn, attach contracts after mandate/synthesis, finalize+attach tool calls before completion |
| `core/views_deliberation.py` | 3 new endpoints: evidence, trace, replay |
| `core/urls.py` | Import + 3 URL patterns |

## Builder APIs

### EvidencePackBuilder (evidence-pack-v1 schema)

| Method | Purpose |
|--------|---------|
| `init_pack(session)` | Initialize empty pack on session |
| `append_source(session, source_dict)` | Add data source (deduped by source_id) |
| `append_claims(session, claims_list)` | Add claims (deduped by claim_id) |
| `append_contradiction(session, dict)` | Record tension between claims |
| `append_internal_refs(session, refs)` | Add doc references (deduped by path) |
| `append_memory_retrievals(session, list)` | Add memory hits (capped at 5) |
| `finalize(session)` | Set assembled_at timestamp |

### SessionTraceBuilder (session-trace-v1 schema)

| Method | Purpose |
|--------|---------|
| `init_trace(session)` | Initialize empty trace |
| `append_turn(session, ...)` | Record turn with content_hash, tension, grounding (deduped by turn_number) |
| `append_turn_from_model(session, turn)` | Convenience from DeliberationTurn instance |
| `attach_contract_snapshot(session, type, data)` | Record execution/synthesis/research contracts |
| `attach_tool_calls(session, trace_id)` | Link ToolCallRecord entries |
| `attach_decisions(session, trace_id)` | Link DecisionRecord entries |
| `finalize(session, state)` | Set performance metrics (tension_count, grounding_count, etc.) |

## Orchestrator Hooks

| Hook | Location | What it does |
|------|----------|-------------|
| 1 | After session creation | `init_pack()` + `init_trace()` |
| 2 | After each turn persisted | `append_turn()` with SHA-256 content hash + `append_contradiction()` on tension |
| 3 | After contracts saved | `attach_contract_snapshot()` for execution/synthesis + `append_source()` for user input |
| 4 | Before completion | `attach_tool_calls()` + `attach_decisions()` via trace_id + `finalize()` both builders |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/deliberation/sessions/<uuid>/evidence/` | Evidence pack JSON + stats |
| GET | `/api/deliberation/sessions/<uuid>/trace/` | Session trace JSON + stats |
| GET | `/api/deliberation/sessions/<uuid>/replay/` | Full replay: turns (content) + contracts + trace + evidence |

All require authentication (same middleware as other deliberation endpoints).

## Tests

33 tests total, all passing:
- 13 EvidencePackBuilder tests (init, append, dedupe, finalize, error safety)
- 10 SessionTraceBuilder tests (init, turns, contracts, finalize, error safety)
- 2 singleton tests
- 5 API endpoint tests (200s, 404s)
- 3 auth-required tests

## No Migrations Required

Phase 3 is purely additive — services + views + orchestrator hooks. Uses existing `evidence_pack` and `trace` JSONFields from Phase 1 migration 0232.

## Design Principles

- **Never blocks conversations**: All builder operations wrapped in try/except
- **Incremental assembly**: Each hook appends to existing JSON, no full rebuilds
- **Deduplication**: Sources by source_id, claims by claim_id, turns by turn_number, refs by doc_path
- **Content integrity**: SHA-256 hashes on turn content for tamper detection
- **Singleton pattern**: Both builders use `get_*()` factory functions

## Verification

```bash
# Hit endpoints on Railway
curl -H "Cookie: sessionid=..." https://<railway-url>/api/deliberation/sessions/<uuid>/evidence/
curl -H "Cookie: sessionid=..." https://<railway-url>/api/deliberation/sessions/<uuid>/trace/
curl -H "Cookie: sessionid=..." https://<railway-url>/api/deliberation/sessions/<uuid>/replay/
```
