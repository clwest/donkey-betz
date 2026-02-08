# Phase 2 Applied Notes — Strategic Memory Service

**Session:** 962
**Date:** February 7, 2026
**Branch:** `session-962/phase2-strategic-memory`

## Summary

Phase 2 turns passive memory and logs into an active strategic layer. The StrategicMemoryService answers "Have we tried this before?", "What tends to fail here?", and "What strategy has worked historically?" by searching across 7 data sources with weighted ranking and recency bonuses.

## New Files

| File | Purpose |
|------|---------|
| `core/services/strategic_memory_service.py` | StrategicMemoryService with 3 public methods + 7 private search methods |
| `core/views_strategic_memory.py` | 3 read-only API endpoints |
| `core/tests/test_phase2_strategic_memory.py` | 37 tests covering service, API, and PA integration |

## Modified Files

| File | Change |
|------|--------|
| `core/urls.py` | Import + 3 URL patterns for `/api/memory/` |
| `core/services/unified_pa_entrypoint.py` | Replaced Phase 0 stub with real StrategicMemoryService for `strategic_memory` enrichment |

## Service API

### `query_precedents(query, top_k=10, scope=None) -> dict`
Searches 7 sources with weighted ranking:

| Source | Weight | Search Method |
|--------|--------|---------------|
| AgentMemory | 1.00 | Embedding similarity (pgvector) with text fallback |
| LearningPattern | 0.85 | Text search on description/pattern_type |
| DecisionRecord | 0.75 | Text search on reasoning/action/task_summary |
| AgentDecisionSummary | 0.75 | Text search on topic/recommended_stance/rationale |
| DeliberationSession | 0.65 | Text search on objective |
| ContractRecord | 0.55 | Python-side filtering on contract_data JSON |
| DeliberationTurn | 0.45 | Text search on content (capped at 5 results) |

Recency bonus: +0.10 (last 30d), +0.05 (30-180d), +0.00 (older).

### `get_failure_signatures(domain=None, top_k=10) -> dict`
Aggregates LearningPattern failure types into grouped signatures with failure rates.

### `recommend_strategy(objective, top_k=5) -> dict`
Returns precedents, success patterns, avoid patterns, and do/don't bullets.

### `format_for_pa(query, top_k=7) -> str`
Compact output for PA enrichment injection (token-budget aware).

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/memory/precedents/?q=...&top_k=10` | Precedent search |
| GET | `/api/memory/failures/?domain=...&top_k=10` | Failure signatures |
| GET | `/api/memory/strategy/?objective=...&top_k=5` | Strategy recommendations |

All require authentication (same middleware as deliberation endpoints).

## PA Enrichment

The `strategic_memory` enrichment key (already mapped to `reasoning` intent) now uses `StrategicMemoryService.format_for_pa()` instead of the Phase 0 LearningPatternEngine stub. This injects precedents and failure patterns into the PA's reasoning context.

## Tests

37 tests total, all passing:
- 9 helper function tests (tokenization, text relevance, recency bonus)
- 8 precedent search tests (mixed sources, sorting, schema, scope, text fallback)
- 4 failure signature tests (grouping, failure rate computation, domain filter)
- 2 strategy recommendation tests
- 9 API endpoint tests (200s, 400s, auth required)
- 3 PA enrichment integration tests
- 1 singleton test

## No Migrations Required

Phase 2 is purely additive service + views — no schema changes.

## Known Limits

- AgentMemory embedding search loads up to 200 records into memory for Python-side cosine similarity (adequate for current scale)
- ContractRecord search is Python-side filtering on recent 100 records (JSONField doesn't support icontains)
- No full-text search (tsvector) — deferred to Phase 3
- No new embedding backfills — uses existing pgvector infrastructure

## Verification

```bash
# Hit endpoints on Railway
curl -H "Cookie: sessionid=..." https://<railway-url>/api/memory/precedents/?q=initiative%20cleanup
curl -H "Cookie: sessionid=..." https://<railway-url>/api/memory/failures/
curl -H "Cookie: sessionid=..." https://<railway-url>/api/memory/strategy/?objective=fix%20initiative%20duplication
```
