# Phase 1 Applied Notes — Deliberation Persistence Layer

**Session:** 962
**Date:** February 7, 2026
**Branch:** `session-962/phase1-persistence-layer`

## Summary

Phase 1 makes deliberation sessions, turns, contracts, and document versions durable and queryable. DeliberationSession wraps HiveMindSession/ConceptForgeRun/AgentSession as a unifying envelope without replacing them.

## New Files

| File | Purpose |
|------|---------|
| `core/models_deliberation.py` | 4 models: DeliberationSession, DeliberationTurn, ContractRecord, DocVersion |
| `core/views_deliberation.py` | 6 read-only API endpoints |
| `core/migrations/0232_phase1_deliberation_persistence.py` | Migration for all 4 models + 3 FK additions |
| `core/tests/test_deliberation_persistence.py` | 12 model tests (session, turn, contract, cascade) |
| `core/tests/test_doc_versioning.py` | 6 DocVersion model tests |
| `core/tests/test_api_deliberation_endpoints.py` | 17 API endpoint tests with auth |

## Modified Files

| File | Change |
|------|--------|
| `core/models/__init__.py` | Import + `__all__` for 4 new models |
| `core/models_unified_system.py` | `deliberation_session` FK on HiveMindSession + AgentSession |
| `core/models_conceptforge.py` | `deliberation_session` FK on ConceptForgeRun |
| `core/conversation_orchestrator.py` | 4 persistence hooks: session creation, turn save, contract save, completion |
| `core/agents/base_agent.py` | DocVersion creation in `_write_doc()` before overwrite |
| `core/urls.py` | Import + 6 URL patterns for deliberation/doc-version API |

## Models

### DeliberationSession
- UUID PK, session_type (hivemind/conceptforge/agent/composite), status (pending/active/completed/failed)
- objective (text), participants (JSON), evidence_pack (JSON), trace (JSON)
- parent_session (self-FK for sub-sessions), trace_id
- Indexes: created_at, status, trace_id

### DeliberationTurn
- FK to session (CASCADE), turn_number + unique constraint per session
- agent_name, role, content, content_hash (auto-computed SHA-256)
- contract_state (JSON), trace_id

### ContractRecord
- FK to session (CASCADE), contract_type (research/synthesis/execution)
- contract_data (JSON holding the full contract dict), trace_id

### DocVersion
- doc_path + version_number with unique constraint
- content_hash (SHA-256), content_snapshot (full text), author_agent
- FK to DeliberationSession (SET_NULL), change_reason, trace_id

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/deliberation/sessions/` | List sessions (filter: status, session_type, q, limit) |
| GET | `/api/deliberation/sessions/<uuid>/` | Session detail |
| GET | `/api/deliberation/sessions/<uuid>/turns/` | List turns (?full=1 for full content) |
| GET | `/api/deliberation/sessions/<uuid>/contracts/` | List contracts |
| GET | `/api/docs/versions/` | List doc versions (?doc_path= filter) |
| GET | `/api/docs/versions/<id>/` | Doc version detail with content snapshot |

## Orchestrator Wiring

The `ConversationOrchestrator.orchestrate_conversation()` method now:
1. Creates a `DeliberationSession` at conversation start (status='active')
2. Persists each agent turn as a `DeliberationTurn` with auto-hashed content
3. Saves execution mandates and synthesis contracts as `ContractRecord`s
4. Sets trace_id = conversation_id after generation
5. Marks session completed with timestamp on conversation end

All persistence is wrapped in try/except — failures log warnings but never break conversations.

## Doc Versioning

`BaseAgent._write_doc()` now creates a `DocVersion` before overwriting any file:
- Compares SHA-256 hashes; only versions if content actually changed
- Stores the OLD content as the snapshot (so you can see what was replaced)
- Version numbers auto-increment per doc_path

## Tests

35 tests total, all passing:
- 12 model persistence tests (create, constraints, cascade delete, ordering)
- 6 doc versioning tests (creation, increment, unique constraint, FK, repr)
- 17 API tests (list, filter, search, limit, detail, 404, counts, auth)

## Nullable FK Design

All 3 existing session models gained `deliberation_session = FK(SET_NULL, null=True)`:
- `HiveMindSession.deliberation_session`
- `ConceptForgeRun.deliberation_session`
- `AgentSession.deliberation_session`

These are purely additive — no existing behavior changes.
