# Session 1239 — PA tools audit (clean) + morning_brief local dogfood enabled

**Session window:** 2026-06-26 (Friday, after Session 1238 morning brief read).

**Theme:** Audit-then-act sweep. Verify the PA tools surface against reality, fold the one real cleanup into a PR, and flip the morning_brief beat task from prod-only to local-dogfood per Chris's directive.

---

## TL;DR

- **Audit #5 (PA tools — Δ=43 from PLATFORM_INVENTORY):** ran clean. 109 schemas / 152 handlers / 108 matched — inventory totals are correct. The 1 schema orphan (`run_agent`) + 44 handler orphans are all by-design (umbrella schema + agent-name dispatches via `_handle_agent_tool`). Rigby's `ops_tool action=tool_migration_report` confirmed all 14 entries in `REMOVED_TOOL_ALIASES` silent in 24h.
- **PR-1 #2660** — fix the lone real inconsistency surfaced by the audit: `web_search` was dual-exposed (live schema + handler + entry in REMOVED_TOOL_ALIASES). Also caught a regression where `intelligence_tool action=search source=web` dropped the caller's `limit` param.
- **PR-2 #2661** — drop `generate-morning-brief-daily` from `LOCAL_DENY_TASKS` so it fires on local for Chris's Sub-step E dogfood loop. Bonus: unstuck 6 pre-existing test failures from Session 1205's `run-spider-network` removal that the lock-in tests never tracked.

**Net stats:**
- 2 PRs, both admin-merged
- 7 files modified across both PRs (+108 / -31)
- 36 tests added/touched, all green
- 0 production regressions (audit confirmed)

---

## Audit #5: PA tools schemas vs handlers

### What Rigby + I cross-verified

The deferred audit candidate from previous sessions: PLATFORM_INVENTORY reports 109 PA tool schemas and 152 registered handlers (Δ=43). Need to classify the gap.

**Rigby's leg:** `ops_tool action=tool_migration_report` — 14 removed tools, all silent in 24h (matches `REMOVED_TOOL_ALIASES` dict length exactly).

**Claude's leg:** direct dispatcher introspection after Django setup:

```python
from core.services.tool_dispatcher import ToolDispatcher
from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS

disp = ToolDispatcher()
handlers = set(disp._tool_handlers.keys())  # 152
schemas = set(s.get('name', '') for s in PA_TOOL_SCHEMAS if isinstance(s, dict) and s.get('name'))  # 109

matched = schemas & handlers              # 108
schema_orphans = schemas - handlers       # 1 (run_agent)
handler_orphans = handlers - schemas      # 44 (individual agent names)
```

### Classification of the gap

| Category | Count | Status | Why |
|---|---:|---|---|
| Schema with matching handler | 108 | ✅ Healthy | Normal LLM-callable tool |
| Schema orphan: `run_agent` | 1 | ✅ By design | Umbrella schema; routes via `_handle_agent_tool` based on `agent_name` param |
| Handler orphans: 44 agent-name entries | 44 | ✅ By design | Each registered so `dispatch('research_agent', ...)` works; all share `_handle_agent_tool` |
| **REAL FINDING:** `web_search` dual-exposed | 1 | ❌ Inconsistency | Live schema + handler AND entry in REMOVED_TOOL_ALIASES (the only one of the 14 still wired) |

### `web_search` decision: Option B (kept as standalone primitive)

Rigby's initial lean was Option A (full migration — remove schema + handler, keep alias). Inspection of `_handle_web_search` at `core/services/td_handlers_agents.py:339-379` flipped the call:

1. **Same handler already serves both routes.** `intelligence_tool action=search source=web` at `td_handlers_core.py:3165` invokes `_handle_web_search` directly. Rigby's 4 pre-flight items (query shaping, rate limit, return shape, telemetry) are N/A because it's the same code path.

2. **Existing test guard explicitly documents the keep.** `test_gateway_smoke.py:171` comment: `# web_search is excluded — it's a standalone primitive kept intentionally`. The `REMOVED_TOOLS` frozenset at lines 191-197 omits `web_search` by name.

3. **Real bug surfaced.** `td_handlers_core.py:3165` was passing only `{'query': query}` to `_handle_web_search`, dropping `limit`. So `intelligence_tool action=search source=web limit=10` silently capped at 5 results (handler default).

So the cleanup was removing the stale REMOVED_TOOL_ALIASES entry — not removing the schema/handler.

---

## PR-1: web_search alias cleanup + intelligence_tool.search limit passthrough

**#2660** — admin-merged.

### Changes (+57 / -3 across 3 files)

1. **`core/services/tool_dispatcher.py:221`** — dropped `'web_search': ('intelligence_tool', 'search')` from `REMOVED_TOOL_ALIASES`.
2. **`core/services/td_handlers_core.py:3165`** — `intelligence_tool action=search source=web` now passes `limit` through:
   ```python
   result = self._handle_web_search(
       'web_search', {'query': query, 'limit': limit}, user_id, trace_id,
   )
   ```
3. **`core/tests/test_gateway_smoke.py`** — updated `expected_legacy` set + added `TestIntelligenceToolSearchWebLimitPassthrough` with 3 regression tests.

### Tests: 16/16 green in 178s

- `TestLegacyToGatewayMapping` (4) — alias map invariants
- `TestRemovedToolGuard` (3) — CI guard against tool re-introduction
- `TestWebSearchHandlerLimitPassthrough` (6) — pre-existing handler edge cases
- `TestIntelligenceToolSearchWebLimitPassthrough` (**3 NEW**) — `limit` honored, default-10 when omitted, oversized clamped to 10

---

## PR-2: generate-morning-brief-daily local dogfood + Session-1205 stale-test unblock

**#2661** — admin-merged.

### Part 1: local dogfood flip

Chris's 06-26 directive — _"it sounds like it's a good thing that its running so let's use it"_ — after Sub-step D (Sessions 1235-1238, PRs #2636-#2659) shipped the content-quality polish (Lane 1 self-check, Lane 3 no-signal fallback, Lane 4 odds-missing fallback, MUSCULAR plain-English humanizer, workspace_resolver factor, Decision Card validator + truncation + dynamic Denver TZ).

Original Session 1233 Sub-step C reasoning (prod-only on Railway to dodge 5+ LLM-call cost) superseded by the explicit-trade calculus: LLM cost is known + accepted as the price of tight iteration on a daily product.

**Effect after merge + `make celery` restart:** `generate-morning-brief-daily` registers as enabled `PeriodicTask`. Fires daily at 07:00 Denver (13:00 UTC MDT). The `_enforce_disabled_local` step (Session 1169) will NOT re-disable it.

### Part 2: 6 stale tests unblocked

Running `test_morning_brief_sub_step_c.py` surfaced 6 pre-existing test failures (verified pre-existing via `git stash` round-trip — fail identically on main without my edit). All referenced `run-spider-network` — Session 1205 removed it from `LOCAL_DENY_TASKS` to let the 80-spider producer fire on local, but three tests bypassed their own "explicit touch + Rigby sign-off required" lock-in:

| Test | Issue | Fix |
|---|---|---|
| `test_deny_list_has_expected_v1_entries` | Hardcoded v1 set with `run-spider-network` IN, morning-brief OUT | Updated to current 5-entry deny list |
| `_canonical()` + 3 derived tests in `test_local_safe_beat_filter.py` | Used `'run-spider-network'` as synthetic "denied" task | Swapped → `'backfill-spider-embeddings'` (currently denied) |
| 3 tests in `test_enforce_disabled_local.py` | Same drift | Same swap |

Spirit preserved exactly — CSV-parsing edge cases, dry-run preview, ENABLE_BEAT_TASKS override semantics all still tested. Just the specific tool names referenced got brought current. The "explicit touch + Rigby sign-off" gate now functions again.

### Tests: 20/20 green (was 14/20 on main before merge)

- `test_morning_brief_sub_step_c.py::MorningBriefBeatScheduleRegistrationTests` (2)
- `test_local_safe_beat_filter.py` (10) — was 7 pass / 3 fail
- `test_enforce_disabled_local.py` (7) — was 4 pass / 3 fail

---

## Operational invariants added

| Invariant | Source | Impact |
|---|---|---|
| `intelligence_tool action=search source=web limit=N` honors N | PR-1 `td_handlers_core.py:3165` | Callers can request 1-10 results instead of silent default-5 |
| `REMOVED_TOOL_ALIASES` and `web_search` schema/handler no longer contradict | PR-1 `tool_dispatcher.py:221` | LLM has one canonical web search entry point; cleanup audits won't flag this again |
| `generate-morning-brief-daily` enabled on local | PR-2 `add_critical_celery_tasks.py:66-70` | 07:00 Denver daily fire on Chris's laptop; Sub-step E dogfood loop active |
| Beat-filter lock-in tests track current denylist | PR-2 4 test files | Future denylist additions/removals require explicit test touch (gate restored) |

---

## Active conversation health

`pa-a2443db2e43a42dc` — added ~6 turns this session (audit-only, narrow scope). Should still be 90-100. Per S1237/S1238 close notes, Rigby's standing recommendation is "rotate before next substantial design+execution arc." Session 1240 begins Sub-step E which IS a new design+execution arc (Mon-Fri qualitative-verdict loop). **Rotation should be considered at S1240 open.**

---

## Carryover into Session 1240

### FIRST THING (Saturday morning 2026-06-27)

The 06-27 cumulative verification window:

```python
# 1. Did the brief fire? (LOCAL)
from core.models import CeleryTaskEvent
from datetime import date
ev = CeleryTaskEvent.objects.filter(
    task_name='core.tasks.generate_morning_brief_daily',
    started_at__date=date(2026, 6, 27),
).order_by('-started_at').first()
assert ev and ev.status == 'SUCCESS', f"Brief did not fire or failed: {ev}"

# 2. Did the deliverable land in the right workspace?
from core.models_deliverables import Deliverable
d = Deliverable.objects.filter(
    user__username='chris',
    category='Morning Brief',
    created_at__date=date(2026, 6, 27),
).first()
assert d, "No morning brief deliverable for 2026-06-27"
assert str(d.workspace_id) != 'cf708a2e-...', \
    "Brief landed in pre-PR-A leak workspace — PR #2653 regressed"

# 3. Sub-step D invariants in the content
content = d.content
assert 'MDT' in content and 'MST' not in content, "Dynamic TZ broken (PR #2655)"
# Lane 1 self-check, Lane 3/4 fallbacks per Session 1238 spec
```

### Priority 1 — Sub-step E kickoff

Per Session 1238 close: Mon-Fri dogfood loop. Chris reads daily, captures qualitative verdict, each newly-surfaced polish item becomes a focused PR. Same rhythm that produced Session 1238's 6 polish PRs but now driven by real cumulative content quality, not Rigby's one-time audit.

### Priority 2 — Whatever Rigby flags from the 06-27 brief

If overall score now lands in the 80s (up from Sub-step D pre-fire 66/100), declare Sub-step D verified-shipped. If still in the 70s, iterate.

### Priority 3+ — Remaining audit candidates

Sessions 1235-1239 closed PA tools audit (Δ=43). Still untouched:

- **80 spiders** — last full audit was Session 1205 Capability Audit Layer 3. Likely fresh drift since `run-spider-network` was re-enabled.
- **30 advisors** — last audit Session 1208 (`docs/ADVISOR_AUDIT.md`).
- **9 body systems** — `BodyCoordinator` autonomic reflex layer, last touched Sub-step D.
- **144 Discord commands** — `docs/DISCORD_AUDIT.md`, 25 Cog classes.
- **61 frontend routes** — last sanity-check pre-Workspace tab redesign.
- **7 fleet sibling apps** at localhost:8002-8008 — Session 1233 carryover.

### Worker state

No new `@shared_task` Session 1239. PR-2 adds an enabled `PeriodicTask` row (`generate-morning-brief-daily`) which requires a `make celery` restart on local for the beat scheduler to pick it up. Chris should run that before going to bed tonight if he wants the 07:00 Denver fire tomorrow.

### Still Chris-side carryover

- Anthropic credit refill at https://console.anthropic.com/billing
- CI billing still failing — both Session 1239 PRs admin-merged via `--admin`

---

## Session 1239 PR ledger

| PR | Subject | Net | Tests | Merged |
|---|---|---|---|---|
| [#2660](https://github.com/clwest/donkey-betz-platform/pull/2660) (PR-1) | web_search alias cleanup + intelligence_tool.search limit passthrough | +57 / -3 | 3 new (16 total green) | ✅ |
| [#2661](https://github.com/clwest/donkey-betz-platform/pull/2661) (PR-2) | generate-morning-brief-daily local dogfood + unstuck Session-1205 stale beat-filter tests | +51 / -28 | 1 flipped + 6 unstuck (20 total green) | ✅ |

---

**Last updated:** 2026-06-26 by Claude Code at Session 1239 close.
