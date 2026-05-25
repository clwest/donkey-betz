---
originating_session: 1034
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1034 — RAG Wiring, Legal Agent, and Production Stability

**Date:** February 18, 2026
**PRs:** #1314–#1323 (10 PRs)
**Focus:** Wire user-uploaded documents into all 92 agents via RAG, legal agent integration, COO-recommended schedule throttling, Railway error fixes, frontend 404 cleanup

## Summary

Three major themes:
1. **RAG Document Integration** — User-uploaded PDFs/URLs now flow into all 92 agents via a new context layer in AgentRouter
2. **Legal Agent Pipeline** — LegalDocDrafterAgent fully wired into PA with intent routing, JDF form context, and document fallback
3. **Production Stability** — Fixed 4 Railway log error categories, workspace path auto-correction, media task guards, schedule throttling, frontend 404s

## Change 1: RAG Document Wiring (PR #1319)

**Problem:** Users could upload documents (PDFs, URLs, YouTube) via content app, but no agent ever retrieved them. The RAG system was fully built but disconnected from the agent pipeline.

**Solution:** New context layer `_get_user_documents_context()` in AgentRouter:
- Embeds the task text via `EmbeddingService.get_embedding_sync()`
- Queries `DocumentEmbedding` with pgvector `CosineDistance` (threshold 0.45)
- Filters by `document__owner=self.user` and `document__status='processed'`
- Returns top 5 most relevant chunks with similarity scores

**Wiring:**
- `gather_context()` and `route()` both call the new method
- `BaseAgent._build_intelligent_prompt()` injects results as "YOUR UPLOADED DOCUMENTS" section
- All 92 agents that use `_build_intelligent_prompt()` automatically get user documents
- Legal agent gets additional direct RAG fallback with stricter threshold (0.40)

**Files:** `core/agent_router.py`, `core/agents/base_agent.py`, `core/agents/legal/legal_doc_drafter_agent.py`, `core/services/unified_pa_entrypoint.py`, `core/services/tool_dispatcher.py`

## Change 2: Legal Agent Pipeline (PRs #1315–#1318)

**Problem:** LegalDocDrafterAgent existed but wasn't reachable from PA. No intent routing, broken document queries, wrong router dispatch.

**Fixes:**
- PR #1315: Added `legal_assistance` PA intent → routes to `universal_agent_tool` with LegalDocDrafterAgent
- PR #1316: Changed from registry stub to `AgentRouter.route()` for proper context injection
- PR #1317: Injected JDF (Judicial Department Form) reference into legal agent prompt context
- PR #1318: Moved `legal_assistance` intent before `user_feedback` to prevent "court order" misrouting to complaint handler
- Fixed broken `document_type__in=['court_order']` filter (not a valid choice) → valid types

**Files:** `core/services/unified_pa_entrypoint.py`, `core/services/tool_dispatcher.py`, `core/agents/legal/legal_doc_drafter_agent.py`

## Change 3: COO Agent Recommendations (PR #1320)

**Problem:** COO agent audit identified three cost/stability concerns: aggressive schedules, PA timeout too short, unbounded trend analysis.

**Fixes:**
- Throttled 4 beat schedules: spider warm-up 4h→6h, clean stale 24h→48h, refresh AI opps 30m→2h, dream execution 2h→4h
- Raised PA `universal_agent_tool` timeout from 30s → 90s (agents averaging 35-45s)
- Broadened trend bounding regex to catch more runaway patterns

**Files:** `core/settings.py`, `core/services/tool_dispatcher.py`, `core/tasks.py`

## Change 4: Workspace Path + Media Guard (PR #1321)

**Problem:** ImageAgent wasted $0.03 on non-generative task ("List recent images"). Workspace path stored as local macOS path in DB, fails on Railway.

**Fixes:**
- Auto-correct workspace path: detect invalid `root_path`, recompute from `__file__`, update DB
- Two-layer media task guard: regex whitelist for generation verbs in both `execute_agent_task()` and `ConversationActionDispatcher`
- `_MEDIA_AGENTS` frozenset + `_MEDIA_GENERATION_PATTERN` regex

**Files:** `core/tasks.py`, `core/services/conversation_action_dispatcher.py`

## Change 5: Railway Log Error Fixes (PR #1322)

Four distinct error categories eliminated:

| Error | Count | Fix |
|-------|-------|-----|
| `AgentResult has no attribute 'result'` | 4x | Changed `.result` → `.message` in narrative_drift_coordinator |
| `UUID is not JSON serializable` | ~10x | Wrapped `gate.id` with `str()` in gate_progression_pipeline |
| `Invalid field name(s) for ActionPlan` | 3x | Switched `OpportunityActionPlan` → `ActionPlan` in ai_core tasks + spider_validator |
| `cannot import SpiderPriority` | 1x | Removed nonexistent import in trigger_project_research |

**Files:** `core/agents/narrative/narrative_drift_coordinator.py`, `core/services/gate_progression_pipeline.py`, `ai_core/tasks.py`, `ai_core/spiders/spider_validator.py`, `core/tasks.py`

## Change 6: Frontend 404 Stubs (PR #1323)

**Problem:** AgentsPage tabs (Channels, Tools, Templates) called `/api/v1/agents/{channels,tools,templates}/` but no backend routes existed.

**Fix:** Added 3 stub endpoints in `core/urls.py` returning `{results: [], count: 0}`. Tabs now show clean empty states instead of console 404 spam.

**File:** `core/urls.py`

## Other Fixes

- PR #1314: Cleaner deliverable titles for research-and-create workflow

## Files Changed (All PRs)

| File | Changes |
|------|---------|
| `core/agent_router.py` | New `_get_user_documents_context()`, wired into `gather_context()` and `route()` |
| `core/agents/base_agent.py` | Inject user docs into `_build_intelligent_prompt()` |
| `core/agents/legal/legal_doc_drafter_agent.py` | Fixed document query, added content app RAG fallback, JDF context |
| `core/agents/narrative/narrative_drift_coordinator.py` | `.result` → `.message` (3 locations) |
| `core/services/unified_pa_entrypoint.py` | Legal intent routing, upload hint, intent priority fix |
| `core/services/tool_dispatcher.py` | Legal handler, `had_user_documents` flag, PA timeout 30s→90s |
| `core/services/gate_progression_pipeline.py` | UUID str() wrapping |
| `core/services/conversation_action_dispatcher.py` | Media task pre-dispatch filter |
| `core/tasks.py` | Media task guard, workspace path auto-correct, schedule throttling, SpiderPriority removal |
| `core/settings.py` | Beat schedule throttling |
| `core/urls.py` | 3 stub endpoints for AgentsPage tabs |
| `ai_core/tasks.py` | OpportunityActionPlan → ActionPlan |
| `ai_core/spiders/spider_validator.py` | OpportunityActionPlan → ActionPlan (2 methods) |

## Key Patterns Established

- **RAG context layer:** `_get_user_documents_context()` in AgentRouter — one embedding call per agent execution (~$0.00002), only when `self.user` is set
- **Media task guard:** `_MEDIA_AGENTS` frozenset + `_MEDIA_GENERATION_PATTERN` regex — two layers (pre-dispatch + execute_agent_task)
- **Workspace path self-healing:** Auto-detect stale local paths, recompute from `__file__`, update DB record
- **Legal agent routing:** Intent `legal_assistance` → `universal_agent_tool` → `AgentRouter.route()` → `LegalDocDrafterAgent` with JDF context + RAG documents

## Post-Session Metrics

| Metric | Value |
|--------|-------|
| Railway log errors | **0** (was 18+) |
| Frontend console 404s | **0** (was 6+) |
| Agents with RAG document access | **92** (was 0) |
| PA intents | **39** (added legal_assistance) |
| Media task guard | LIVE (two-layer) |
| PA timeout | 90s (was 30s) |
| Beat schedule savings | ~40% fewer runs for 4 tasks |
