# Tool Consolidation — Legacy Tool Removal Checklist

**Session 1079 | Phase 3 Prep**

## Overview

40+ PA tools consolidated into 6 gateways. This checklist tracks each legacy tool's deprecation readiness.

**Rollback (all tools):** Set `TOOLS_EXPOSE_LEGACY=true` on Railway celery-pa and restart.

---

## Gateway: `governance_tool` (absorbs 2 tools)

### 1. `boardroom_tool`
- **Gateway action mapping:**
  - `stats` → `governance_tool.inbox`
  - `list_attention` → `governance_tool.attention_list`
  - `approve_attention` → `governance_tool.attention_approve`
  - `ignore_attention` → `governance_tool.attention_ignore`
  - `lookup` → `governance_tool.attention_lookup`
  - `list_decisions` → `governance_tool.decision_list`
  - `promote_decision` → `governance_tool.decision_promote`
  - `reject_decision` → `governance_tool.decision_reject`
  - `get_triage_batch` → `governance_tool.triage_batch`
- **Known callers outside PA schema:**
  - `unified_pa_entrypoint.py` L6269-6397: triage mode calls — **MIGRATED** (commit 33a7e257)
  - `unified_pa_entrypoint.py` intent router — **MIGRATED**
  - `frontend/dist/__manifest.json` L243-361: UI surface mappings — **MIGRATED** (Session 1079)
  - `core/services/pa_tool_schemas.py`: enrichment + intent maps — keep (backward compat)
- **Safe-to-deprecate criteria:** 0 calls in 72h window via `tool_migration_report`
- **Risk:** LOW — all direct callers migrated

### 2. `human_decisions_tool`
- **Gateway action mapping:**
  - `list` → `governance_tool.decisions_list`
  - `stats` → `governance_tool.decisions_stats`
  - `create` → `governance_tool.decision_create`
  - `decide` → `governance_tool.decision_decide`
- **Known callers outside PA schema:**
  - `core/prompts/registry.py` L191: system prompt — **MIGRATED** (commit 33a7e257)
  - `core/services/learning_loop_orchestrator.py` L169: SuccessSignal — kept for continuity, gateway signal added
  - `personal_ai_assistant_enhanced.py` L1474, L13234-13540: old PA handler — deferred (fallback path only)
  - `core/assistant/tool_definitions.py` L1540: old assistant definition — deferred
  - `core/assistant/tool_category_router.py` L103: old routing — deferred
- **Safe-to-deprecate criteria:** 0 calls in 72h
- **Risk:** LOW — primary path migrated, old PA is fallback only

---

## Gateway: `work_tool` (absorbs 1 tool)

### 3. `initiative_tool`
- **Gateway action mapping:**
  - `list` → `work_tool.initiative_list`
  - `detail` → `work_tool.initiative_detail`
  - `create` → `work_tool.initiative_create`
  - `promote` → `work_tool.initiative_promote`
  - `stage_detail` → `work_tool.stage_detail`
  - `stage_approve` → `work_tool.stage_approve`
  - `action_item_list` → `work_tool.action_item_list`
  - `action_item_update` → `work_tool.action_item_update`
- **Known callers outside PA schema:**
  - `unified_pa_entrypoint.py` intent router — **MIGRATED**
  - `frontend/dist/__manifest.json` L451-748: UI surface mappings — **MIGRATED** (Session 1079)
  - `core/tasks.py` L35341: comment only
- **Safe-to-deprecate criteria:** 0 calls in 72h
- **Risk:** LOW

---

## Gateway: `content_tool` (absorbs 3 tools)

### 4. `content_review_tool`
- **Gateway action mapping:**
  - `stats` → `content_tool.content_stats`
  - `list` → `content_tool.content_list`
  - `details` → `content_tool.content_detail`
  - `search` → `content_tool.content_search`
  - `recent` → `content_tool.content_recent`
  - `approve` → `content_tool.content_approve`
  - `reject` → `content_tool.content_reject`
- **Known callers outside PA schema:**
  - `unified_pa_entrypoint.py` intent router — **MIGRATED**
  - `core/tools/http_smoke_test.py` L639: comment only
  - `test_pa_mutation_tools.py` L20: test case
- **Safe-to-deprecate criteria:** 0 calls in 72h
- **Risk:** LOW

### 5. `generate_blog_tool`
- **Gateway action mapping:**
  - (direct) → `content_tool.generate_blog`
- **Known callers outside PA schema:**
  - `unified_pa_entrypoint.py` intent router — **MIGRATED**
  - `core/tasks.py` L21536: comment only (references Celery task, not tool)
- **Safe-to-deprecate criteria:** 0 calls in 72h
- **Risk:** LOW

### 6. `deliverables_tool`
- **Gateway action mapping:**
  - `list` → `content_tool.deliverable_list`
  - `detail` → `content_tool.deliverable_detail`
  - `search` → `content_tool.deliverable_search`
  - `save` → `content_tool.deliverable_save`
  - `create` → `content_tool.deliverable_create`
  - `stats` → `content_tool.deliverable_stats`
- **Known callers outside PA schema:**
  - `unified_pa_entrypoint.py` intent router — **MIGRATED**
  - `test_pa_mutation_tools.py` L23, L30: test cases
- **Safe-to-deprecate criteria:** 0 calls in 72h
- **Risk:** LOW

---

## Gateway: `intelligence_tool` (absorbs 6 tools)

### 7. `stock_intelligence_tool`
- **Gateway action mapping:**
  - `alerts` → `intelligence_tool.stocks_alerts`
  - `predictions` → `intelligence_tool.stocks_predictions`
  - `sec_filings` → `intelligence_tool.stocks_sec_filings`
  - `overview` → `intelligence_tool.overview` (composite, stocks desk)
  - `briefs` → `intelligence_tool.briefs` (composite, stocks desk)
- **Known callers outside PA schema:**
  - `unified_pa_entrypoint.py` intent router — **MIGRATED**
- **Safe-to-deprecate criteria:** 0 calls in 72h
- **Risk:** LOW

### 8. `sports_betting_tool`
- **Gateway action mapping:**
  - `predictions` → `intelligence_tool.sports_predictions`
  - `arbs`/`arbitrage` → `intelligence_tool.sports_arbs`
  - `wagers` → `intelligence_tool.sports_wagers`
  - `record_wager` → `intelligence_tool.sports_record_wager`
- **Known callers outside PA schema:**
  - `unified_pa_entrypoint.py` intent router — **MIGRATED**
- **Safe-to-deprecate criteria:** 0 calls in 72h
- **Risk:** LOW

### 9. `legislation_tool`
- **Gateway action mapping:**
  - `search` → `intelligence_tool.legislation_search`
  - `summary` → `intelligence_tool.legislation_summary`
  - `trending` → `intelligence_tool.briefs` (legislation desk)
  - `overview` → `intelligence_tool.overview` (legislation desk)
- **Known callers outside PA schema:**
  - `unified_pa_entrypoint.py` intent router — **MIGRATED**
  - `core/prompts/tool_descriptions.py` L1006: description text — keep for now
  - `core/assistant/tool_definitions.py` L1660: old assistant — deferred
  - `test_pa_mutation_tools.py` L21: test case
- **Safe-to-deprecate criteria:** 0 calls in 72h
- **Risk:** LOW

### 10. `rag_query_tool`
- **Gateway action mapping:**
  - `search` → `intelligence_tool.search` (source=kb)
  - `ingest` → `intelligence_tool.kb_ingest`
- **Known callers outside PA schema:**
  - `unified_pa_entrypoint.py` intent router — **MIGRATED** (research → intelligence_tool)
- **Safe-to-deprecate criteria:** 0 calls in 72h
- **Risk:** LOW

### 11. `spider_data_tool`
- **Gateway action mapping:**
  - `search` → `intelligence_tool.search` (source=spider)
- **Known callers outside PA schema:**
  - `unified_pa_entrypoint.py` intent router — **MIGRATED** (crypto_price, spider_data)
  - `core/tasks.py` L26364: comment only
- **Safe-to-deprecate criteria:** 0 calls in 72h
- **Risk:** LOW

### 12. `web_search` (standalone primitive — NOT in _LEGACY_TOOL_NAMES)
- **Note:** `web_search` is kept as a standalone primitive, not deprecated.
  The intent router now routes research → `intelligence_tool`, but `web_search`
  remains available for direct LLM selection and old PA fallback.
- **Known callers:**
  - `core/assistant/base.py` L227, L510: old assistant handler
  - `personal_ai_assistant_enhanced.py` L1388, L3382: old PA handler
  - `config/tool_config.json`: config
  - Multiple agents use WebSearchTool directly (not via PA)

---

## Gateway: `ops_tool` (absorbs 2 tools)

### 13. `system_health_tool`
- **Gateway action mapping:**
  - (default) → `ops_tool.slo_status`
- **Known callers outside PA schema:**
  - `unified_pa_entrypoint.py` intent router — **MIGRATED**
- **Safe-to-deprecate criteria:** 0 calls in 72h
- **Risk:** LOW

### 14. `error_summary_tool`
- **Gateway action mapping:**
  - (default) → `ops_tool.failure_signatures`
- **Known callers outside PA schema:**
  - `unified_pa_entrypoint.py` intent router — **MIGRATED**
  - `core/middleware_error_capture.py` L4: comment only
- **Safe-to-deprecate criteria:** 0 calls in 72h
- **Risk:** LOW

---

## Phase 3 Activation Checklist

1. [ ] Run `ops_tool tool_migration_report window=72h` — confirm 0 legacy calls
2. [ ] Run gateway smoke test suite — all pass
3. [ ] Set `TOOLS_EXPOSE_LEGACY=false` on Railway celery-pa
4. [ ] Restart celery-pa (`railway redeploy` on celery-pa service)
5. [ ] Wait 30 min, run `ops_tool tool_migration_report window=1h` — confirm gateways only
6. [ ] Run `ops_tool slo_status window=6h` — no new breaches
7. [ ] Monitor for 24h — no user-facing regressions
8. [ ] If issues: set `TOOLS_EXPOSE_LEGACY=true` and redeploy (instant rollback)
