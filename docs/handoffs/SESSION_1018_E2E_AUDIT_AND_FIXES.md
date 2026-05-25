---
originating_session: 1018
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1018 — End-to-End Audit + Conversation Junk Fix + Initiative Fast-Track Fix

**Date:** February 16, 2026
**PRs:** #1239, #1240

---

## Problems

### 1. Conversation Topic Junk (PR #1239)
20% of agent conversations (61/310 in 24h) were circular meta-discussions. Agents were discussing their own instructions as topics — e.g., "Discussion: [Learned] Research: Research this topic using EXTERNAL sources (web_search, spid..."

**Root cause:** 751 `AgentKnowledgeSource` items with `[Learned]` prefix containing raw agent instructions were being selected as conversation topics by `run_agent_conversation` and `run_multi_agent_conversation`.

### 2. Initiative Fast-Track Stall (PR #1240)
100% of auto-created initiatives stalled at Stage 2. No initiative had ever reached Stage 3+.

**Root cause:** All 4 initiative creation paths hardcoded `execution_speed='fast'`, which is designed to stop at Stage 2 (`can_auto_progress` returns False for `fast` at `stage >= 2`).

---

## Changes

### PR #1239 — Conversation topic junk filter
- **File:** `core/tasks.py`
- `run_agent_conversation` (lines 7132-7179): Excluded `[Learned]` and `EXTERNAL sources` from knowledge source query; added instruction marker filter
- `run_multi_agent_conversation` (lines 8035-8082): Same filters
- `cleanup_boardroom_junk` (lines 465-482): Added cleanup of junk `AgentConversation` records

### PR #1240 — Initiative fast-track stall
- **File:** `core/services/conversation_initiative_pipeline.py` (line 469): `'fast'` → `'balanced'`
- **File:** `core/services/autonomous_action_executor.py` (line 1131): `'fast'` → `'balanced'`
- **File:** `core/services/hivemind_execution_pipeline.py` (line 503): `'fast'` → `'balanced'`
- **File:** `core/services/initiative_integration_service.py` (line 166): `'fast'` → `'balanced'`
- **Data fix:** Batch-updated 21 existing initiatives (10 ACTIVE + 11 TRIAGE) from `fast` → `balanced` on Railway

---

## End-to-End System Audit Results (24h)

| Subsystem | Volume | Success Rate | Issues Found |
|-----------|--------|-------------|--------------|
| Agent Executions | 437 | 83.5% | Timeouts: 0 post-fix, .metadata: 0 post-fix |
| Agent Conversations | 310 | 99.7% legitimate | Junk: 0 post-fix (was 19%) |
| Agent Dreams | 43 new | 96.6% promoted | Healthy |
| Initiatives | 38 total | 10 ACTIVE unblocked | Fixed (was 100% stalled) |
| Signal Clusters | 328 new | N/A | Healthy |
| Spider Data | 1,694 new | N/A | All types active |
| Celery Tasks | 49,676 | 99.94% | 0 failures |
| Content Pipeline | 97 blogs, 101 deliberations | N/A | 28 published |
| Body Systems | 1,431 heartbeats | 100% healthy | All 7 green |
| Code Artifacts | 35 total | N/A | All pending review |

## Verification

- Junk conversation topics: 0 post-fix (was 61)
- Active initiatives with `can_auto_progress=True`: 10/10
- All active initiatives at `balanced` speed
- Body systems: 100% healthy
- Celery: 99.94% success rate, 0 failures

## Field Name Discoveries (for future sessions)

| Model | Correct Field | Common Mistake |
|-------|--------------|----------------|
| `AgentDream` | `dreamed_at` | `created_at` |
| `AgentDream` | `dream_type` | `status`, `type` |
| `SignalCluster` | `pattern_type` | `cluster_type` |
| `SignalCluster` | `name` | `title` |
| `AgentConversation` | `started_at` | `created_at` |
| `ComponentStatus` | import from `core.models_heart` | `core.models` |
| `DeliberationSession` | import from `core.models_deliberation` | `core.models_unified_system` |
