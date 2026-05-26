---
originating_session: 969
provenance_confidence: HIGH
provenance_note: Hand-authored handoff. Cited by Session 1158 narrative G (Frontend) milestone 2 as the related handoff to the workspace 9-tab structure era.
---

# Session 969b — PA Live Telemetry Tools

**Date:** February 8, 2026
**PRs:** #974 (PA live telemetry tools)
**Status:** COMPLETE — Deployed to Railway, verified on production

---

## What Was Done

### Problem: PA Self-Awareness Gap (Discovered Session 968)

When asked "what's been going on?" or "any errors recently?", the PA hallucinated stats because it had zero tools to query live system telemetry. The existing `execution_history_tool` only covered `AgentExecution` records, and `get_body_vitals` only covered body system health. Neither gave a holistic "what happened recently" snapshot.

### Solution: 3 New PA Telemetry Tools

Added 3 tools that give the PA real-time awareness of system activity, health, and errors. Two files modified — no new files, no migrations.

#### Tool 1: `recent_activity_tool`

**Purpose:** "What's been going on?" — comprehensive activity snapshot across all subsystems.

**Queries (within configurable hours window, default 2h):**
- Celery tasks — count by status from `django_celery_results.TaskResult`
- Spider data — total items, distinct spiders, top spiders from `SpiderData`
- Conversations — count by status, latest questions from `HiveMindSession`
- Blogs — total, published vs draft, latest titles from `SelfBlog`
- Initiative changes — recently updated active initiatives from `Initiative`
- Signal clusters — active clusters by strength from `SignalCluster`

**Actions:** `summary` (default, 5 items per section) or `detailed` (15 items)

#### Tool 2: `system_health_tool`

**Purpose:** "How's the system?" — aggregate health snapshot.

**Queries:**
- Latest heartbeat — status, health score, age from `HeartBeat`
- Component statuses — healthy/unhealthy counts from `ComponentStatus`
- Celery health — last 1h task count + success rate from `TaskResult`
- Tool call health — today's totals + success rate from `ToolCallAggregate`
- Spider freshness — last 2h count + latest timestamp from `SpiderData`

**Computed `overall_assessment`:** healthy / degraded / critical based on heartbeat age, celery success rate, and component health.

**Actions:** `overview` (default) or `components` (includes per-component details)

#### Tool 3: `error_summary_tool`

**Purpose:** "Any errors?" — recent failures and patterns.

**Queries (within configurable hours window, default 4h):**
- Active failure signatures from `FailureSignature`
- Failure detections grouped by source type from `FailureDetection`
- Failed tool calls grouped by agent+tool from `ToolCallRecord`
- Failed Celery tasks grouped by task name from `TaskResult`

**Computed `severity`:** none / low / moderate / high based on total error count.

**Actions:** `summary` (default, 5 items) or `detailed` (20 items)

### Entrypoint Routing Changes

**Enrichment map:** 3 new entries with empty lists (pure telemetry, no enrichment needed)

**Intent aliases:** 5 new — `activity`, `whats_happening`, `errors`, `failures`, `platform_health`

**Intent routing keywords:**
- Recent activity: "what's been going on", "catch me up", "what did I miss", "update me", etc.
- System health: "how's the system", "is everything working", "anything down", etc.
- Error summary: "any errors", "what failed", "what broke", "any problems", etc.

**Routing order:** New blocks placed BEFORE existing `system_health` block to avoid "system" keyword overlap.

**Payload builders:** Extract `action` (summary/detailed) and `hours` from natural language (e.g., "last 6 hours" → `hours=6`).

---

## Files Modified

| File | Change |
|------|--------|
| `core/services/tool_dispatcher.py` | 3 tool registrations + 3 handler methods (~450 lines) |
| `core/services/unified_pa_entrypoint.py` | 3 enrichment map entries, 5 aliases, 3 intent routing blocks, 3 payload builders (~55 lines) |

## Key Decisions

- **No new files, no migrations** — tools are handler methods on existing ToolDispatcher class
- **Empty enrichment lists** — telemetry tools return pure data, no LLM enrichment overlay needed
- **`import re` inside elif branches** — matches existing pattern in `_build_tool_payload` to avoid UnboundLocalError from Python's function-level scoping with inline imports
- **Graceful degradation** — each data source wrapped in try/except so one query failure doesn't block others
- **Computed assessments** — `overall_assessment` and `severity` give the PA language-ready verdicts to communicate to users

## Testing

### Local
- Both files import cleanly
- 8/8 intent routing tests pass
- Payload builders correctly extract hours from "last 6 hours" → `hours=6`, "past 12h" → `hours=12`
- All 3 tools execute against live DB in <150ms each

### Railway Production
- 47 tool handlers registered (up from 44)
- `recent_activity_tool` — OK, 1442ms, found 21 spider items, 17 blogs, 10 initiatives
- `system_health_tool` — OK, 359ms, assessment=degraded (heartbeat stale — correctly detected Celery beat gap)
- `error_summary_tool` — OK, 284ms, severity=none, 0 errors
- 6/6 intent routing tests pass on production

---

## What Could Come Next

1. **PA Response Formatting for Telemetry** — The PA's LLM prompt builder could use intent-specific directives for telemetry tools (e.g., "Summarize the activity concisely, highlight anything unusual")
2. **Celery Beat Schedule Monitoring** — Add Celery Beat schedule metadata to `system_health_tool` (which tasks are scheduled, last run times)
3. **Trend Comparison** — Compare current period vs previous period (e.g., "50% more spider data than yesterday")
4. **Alert Thresholds** — Auto-surface telemetry warnings in the PA greeting when errors or degraded health detected
