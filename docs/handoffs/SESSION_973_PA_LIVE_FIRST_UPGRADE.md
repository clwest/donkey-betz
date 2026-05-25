---
originating_session: 973
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 973 — PA Live-First Upgrade

**Date:** February 9, 2026
**Previous Session:** 972 (Learning Loop Stats)
**Branch:** `session-973/pa-live-first-upgrade`
**PRs:** #1004, #1005, #1006, #1007

---

## Problem

When users asked broad system questions like "What updates have been made?" or "How is everything?", the PA's keyword-based intent routing fell through to `general` intent (no match), which called `_generate_direct_response()`. That method builds a prompt from static CLAUDE.md docs and user profile — no live data queried. The result read like a reformatted README, not an analytical advisor with live system access.

## Solution

Added a `system_overview` intent with a `status_snapshot_tool` that queries 9 models for cheap count-based metrics, cached for 60 seconds. Also hardened the `general` intent fallback to stop narrating documentation.

---

## Changes

### Files Modified

| File | Changes |
|------|---------|
| `core/services/tool_dispatcher.py` | Added `status_snapshot_tool` registration + `_handle_status_snapshot` handler |
| `core/services/unified_pa_entrypoint.py` | 6 surgical edits: intent routing, enrichment map, aliases, payload builder, formatter, analytical directive, direct response role |

No new files, no migrations, no new URLs.

### 1. `status_snapshot_tool` (tool_dispatcher.py)

New handler queries 9 models with `.count()` calls, each in its own `try/except`:

| Section | Model | Query |
|---------|-------|-------|
| initiatives | `Initiative` | active count + updated-last-24h |
| tool_calls_24h | `ToolCallRecord` | total + failed (24h) |
| health | `HeartBeat` | latest overall_status, score, age via recorded_at |
| spiders_24h | `SpiderData` | items + distinct spiders (24h) |
| conversations_24h | `HiveMindSession` | count (24h) |
| signal_clusters_active | `SignalCluster` | active count |
| celery_24h | `TaskResult` | total + failed (24h) |
| errors_24h | `FailureDetection` | count (24h) |
| blogs_24h | `SelfBlog` | total + published (24h) |

Django cache key: `pa:status_snapshot`, TTL 60s.

### 2. `system_overview` Intent (unified_pa_entrypoint.py)

- **INTENT_ENRICHMENT_MAP:** `'system_overview': ['intelligence_enricher']`
- **INTENT_ALIASES:** `'overview'` and `'executive_summary'` → `system_overview`
- **17 trigger phrases:** "how is everything", "overall system", "platform overview", "what updates", "executive summary", "big picture", etc.
- **Ordering:** Placed AFTER error_summary (line 616), BEFORE system_health body vitals (line 618) — existing Session 969 tools (recent_activity, system_health_check, error_summary) still win for their exact phrases.

### 3. Payload Builder

`system_overview` → `payload['action'] = 'snapshot'`

### 4. Formatter

Formats snapshot as compact bullet list: Health, Initiatives, Tool calls, Spiders, Conversations, Signals, Celery, Errors, Blogs. Ends with "*Want me to drill into any of these?*"

### 5. Analytical Directive

COO-level pulse check: max 3-5 bullet points, lead with most important observation, compare to expectations, separate OBSERVED vs EXPECTED, don't restate every number.

### 6. Direct Response Role Hardening

Changed `_generate_direct_response` role from "Personal Assistant" to "operational advisor". Added: "You are NOT a documentation narrator. Do NOT recite system capabilities from design documents." Suggests targeted questions for broad system queries.

---

## Bugs Fixed During Railway Testing

| Bug | Root Cause | Fix | PR |
|-----|-----------|-----|-----|
| `takes 4 positional arguments but 5 were given` | Handler was `async def` missing `tool_name` param | Changed to sync `def` with correct 5-param signature | #1005 |
| `cannot import name 'HeartBeat' from 'core.models'` | Models not re-exported from `__init__.py` | Direct imports: `core.models_heart`, `core.models_unified_system`, `core.models_diagnostic_pipeline` | #1006 |
| Formatter not rendering (raw dict shown) | `elif` placed outside `isinstance(dict)` block | Moved inside the block at correct indentation | #1006 |
| `Cannot resolve keyword 'created_at'` on HeartBeat | HeartBeat uses `recorded_at` and `overall_status` | Fixed field names | #1007 |

---

## Gotchas for Future Sessions

- **ToolDispatcher handler signature:** Must be `def handler(self, tool_name: str, payload: Dict, user_id: Optional[int], trace_id: str)` — sync, not async, and `tool_name` is the first param after `self`.
- **Model import paths on Railway:** HeartBeat is in `core.models_heart`, SpiderData in `core.models_unified_system`, FailureDetection in `core.models_diagnostic_pipeline`. Don't assume `core.models` re-exports everything.
- **HeartBeat fields:** Uses `recorded_at` (not `created_at`) and `overall_status` (not `status`).
- **Formatter nesting:** New intent cases in `_format_tool_result` must go inside the `if isinstance(tool_result, dict):` block, not at the top level.

---

## Railway Test Results (All Passing)

| Test | Phrase | Expected Intent | Result |
|------|--------|----------------|--------|
| 1 | "What updates have been made?" | system_overview | system_overview with live data |
| 2 | "How's everything?" | system_overview | system_overview with live data |
| 3 | "What's been going on?" | recent_activity | recent_activity (unchanged) |
| 4 | "How's the system?" | system_health_check | system_health_check (unchanged) |
| 5 | "Any errors?" | error_summary | error_summary (unchanged) |
| 6 | "Tell me about agents" | general | Concise response, no doc dump |

Live snapshot data: Health=healthy (100.0), 73 initiatives (73 updated 24h), 3,213 tool calls (4 failed), 641 spider items from 65 spiders, 176 blogs.
