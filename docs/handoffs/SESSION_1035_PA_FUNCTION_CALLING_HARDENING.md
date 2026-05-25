---
originating_session: 1035
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1035 — PA Function Calling Hardening & Operator Report

**Date:** February 19, 2026
**Commits:** ea2de879, 3d0725f3, cca9aac2, f5366d8a, 450be9a2, 53aaf07b, 3e777844
**Focus:** Harden the PA function calling system (shipped in Session 1036), fix operator report tool accuracy, add DB timeout resilience, clean up deprecated models

## Summary

Session 1036 shipped the PA redesign (keyword router → GPT-5.2 function calling). This session hardened it through iterative testing on Railway:
1. **Pyright cleanup** — 0 errors across all 4 PA function calling files
2. **Operator report accuracy** — Fixed 3 tool handlers returning wrong/missing data
3. **Agent taxonomy** — Disjoint categories (blocked/rerouted/fully_enabled) with reconciliation math
4. **Tool call metadata** — GPT function call names now captured (was `name: unknown`)
5. **DB timeout resilience** — _build_context capped at 5s per step (was unbounded, 134s observed)
6. **Model deduplication** — Removed deprecated UserAgentLearning (242 lines)

## Change 1: Pyright Cleanup (ea2de879)

**Problem:** 65+ Pyright errors across pa_tool_schemas.py, llm_enforcer.py, tool_dispatcher.py, unified_pa_entrypoint.py from the function calling implementation.

**Fix:** Added ~30 `type: ignore` comments for Django dynamic model attributes (_UserModel.id/.username), Celery .delay(), Anthropic ContentBlock union types, and dict type narrowing. All pre-existing patterns — no actual type bugs.

**Result:** 0 errors, ~920 warnings (all pre-existing) across all 4 files.

## Change 2: Operator Report Tool Fixes (3d0725f3)

Three issues found via live Railway testing:

1. **agent_introspection_tool schema** — `action='stats'` not in enum, so GPT-5.2 never called it. Added `'stats'` to the schema enum.
2. **Routable agent count** — `get_available_agents()` returned 0 because it accessed `agent_class.system_prompt` which threw on some classes. Replaced with `len(AgentRouter.AGENT_MAP)` → returns 82.
3. **Pipeline by_status** — `initiatives_active: 0` was confusing without context. Added `by_status` breakdown showing `{TRIAGE: 20, COMPLETED: 3}` which explains why active=0.

**Files:** core/services/pa_tool_schemas.py, core/services/tool_dispatcher.py

## Change 3: Deprecated UserAgentLearning Removal (cca9aac2)

**Problem:** `UserAgentLearning` existed in both `core/models.py:2664` (deprecated) and `core/models_unified_system.py:3355` (canonical). The `core/models/__init__.py` package already re-exports the canonical version via `from ..models_unified_system import *`.

**Fix:**
- Removed 242 lines of deprecated class from core/models.py
- Fixed broken import in core/models/jobs/models.py (was importing from non-existent `ai_learning.models`, now imports from `core.models_unified_system` and `..users.models`)

**Note:** Profile consolidation (UserProfile + ExtendedUserProfile + EnhancedUserProfile → UnifiedUserProfile) identified but deferred as Phase 4 of model deduplication audit.

## Change 4: Disjoint Agent Taxonomy (f5366d8a, 450be9a2)

**Problem:** `non_specialist_agents` list overlapped with `blocked_agents` (AudioAgent and CodeGeneratorAgent appeared in both). ChatGPT review caught this.

**Fix:** Three disjoint categories that sum to total:
- `blocked_agents`: 2 (AudioAgent, CodeGeneratorAgent) — hard-blocked, tasks rejected
- `rerouted_agents`: 8 (COOAgent, CTOAgent, etc.) — tasks redirected to specialists, excludes blocked
- `fully_enabled_count`: 72 — everything else
- `reconciliation`: "2 blocked + 8 rerouted + 72 fully_enabled = 82 total"

Also split `stats` and `list` actions — stats returns aggregates only, list includes top-50 agent preview.

**Files:** core/services/tool_dispatcher.py (agent_introspection handler)

## Change 5: Tool Call Metadata Fix (53aaf07b)

**Problem:** `tool_call_metadata` only stored `{'tool': ..., 'ok': ...}` from ToolResult. Missing the GPT-5.2 function call name, arguments, and call_id needed for multi-turn context reconstruction.

**Fix:** `_run_agentic_loop` now returns a 4-tuple `(content, tool_runs, fc_metadata, response_id)` where `fc_metadata` captures:
```python
{'name': tool_name, 'arguments': arguments, 'call_id': call_id, 'ok': tool_result.ok}
```

This flows through to `tool_call_metadata` in PAResponse and gets persisted in ChatConversation.metadata for history reconstruction.

**Files:** core/services/unified_pa_entrypoint.py

## Change 6: DB Timeout Resilience (3e777844)

**Problem:** Railway Postgres connection timeout (134s observed) blocked the entire PA request during `_build_context`. The profile load alone took 134s, causing repeated "Sorry, there was an error" on the frontend.

**Fix:** Added `asyncio.wait_for` timeouts to all DB-touching steps in `_build_context`:

| Step | Timeout | Degradation |
|------|---------|-------------|
| Profile load | 5s | PA works without profile context |
| Knowledge injection | 3s | PA works without system knowledge |
| System stats | 5s | PA uses hardcoded defaults |
| Docs context | 5s | PA works without document context |
| Conversation history (sync) | 5s | `SET LOCAL statement_timeout` |

**Result:** Worst-case `_build_context` capped at ~18s (all timeouts sequential) instead of 134s+. Each step gracefully degrades. Observed latency after fix: 15.6s for full operator report (5 tool calls + LLM synthesis).

## Verification

Tested on Railway production with PA function calling enabled:

```
Run a full operator report: system health, agent stats, pipeline status, and resource budget. Show raw numbers.
```

Result: 4 tools called in one turn, all data accurate, 15.6s total latency. Follow-up question ("How many agents are fully enabled vs blocked vs rerouted? Verify the math adds up.") correctly hit single tool and verified reconciliation.

## Known Issues / Next Session

1. **20 initiatives stuck in TRIAGE** — All initiatives are TRIAGE (20) or COMPLETED (3), none ACTIVE. The pipeline isn't promoting anything. May need investigation.
2. **Profile consolidation** — Three user profile models need merging (Phase 4 of model dedup audit).
3. **Railway web service instability** — Web service hung during deploy (Postgres connection timeout in release command). Required force redeploy. The timeout fix protects the PA but the release command (`migrate + sync_celery_beat + setup_codebase_workspace`) may also need timeouts.
