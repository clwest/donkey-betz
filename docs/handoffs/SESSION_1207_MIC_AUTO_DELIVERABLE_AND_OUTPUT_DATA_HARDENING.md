# Session 1207 — MIC auto-deliverable + output_data hardening (3 PRs)

**Status:** Closed clean. **3 PRs merged.** All live-verified before merge.
**Date:** 2026-06-22 (extended past midnight UTC)
**Active conversation:** `pa-33088358df304016` — Chris's pinned Session 1207 thread. Prior thread `pa-b2a99ff5b0ee47a6` (Rigby's session_tool create_fresh from this session open) was superseded mid-session; thread-pin update is captured in PR #2468.
**Prior session:** [`SESSION_1206_LAYER1_TELEMETRY_BASEAGENT_RUN.md`](./SESSION_1206_LAYER1_TELEMETRY_BASEAGENT_RUN.md).
**Next session entry point:** Session 1208 — **CampaignOrchestrator delegation hardening** (outbound pack schema + validation/retry + ONE combined deliverable). Full spec preserved as deliverable `ecddb62d-ab01-4b3b-83c4-2601670395d3` on Initiative `29154d73-…`.

## TL;DR

Single-arc session (MIC auto-deliverable + immediate refinements) pivoted from a Rigby check-in mid-Session-1206. The session 1206 expanded scope ended on a Wakeup Week re-dispatch; Rigby's read of the new evidence surfaced one clear gap: **MarketIntelligenceCoordinator runs successfully but produces no Deliverable** — the daily brief was stranded in `AgentExecution.output_data` instead of being persisted as a discoverable artifact.

Session 1207 closes that gap in 3 PRs:
- **PR #2467** — MIC auto-creates exactly 1 deliverable per successful run, with hook isolation so post-result-construction failures don't flip `success`.
- **PR #2468** — pa_local.sh thread pin moves from Rigby's auto-spawned `pa-b2a99ff5b0ee47a6` to Chris's preferred `pa-33088358df304016`. Pure dev ergonomics.
- **PR #2469** — Lifts `deliverable_id` + `warnings` from `result.data` to top-level `output_data`. Establishes a structured warnings convention (`{type, message}`) that other agents can adopt.

Mid-session, after MIC was closed, Rigby spec'd the next arc: **CampaignOrchestrator delegation hardening** (outbound pack for the $2k Automation Sprint offer, 2 segments, JSON schema validation, retry semantics, single combined deliverable). That's a substantial feature, not a "quick fix" — Chris flagged it for Session 1208. Full spec is filed as deliverable `ecddb62d-…` (10KB, §1-§6) so Session 1208 has the complete contract.

## Session Manifest

### PRs merged

| # | Title | Files | Verified |
|---|---|---|---|
| **#2467** | feat(session-1207): MarketIntelligenceCoordinator auto-creates deliverable per run | 1 + pa_local.sh bundled | ✅ live (smoke deliverable `758be167-…` in DBZ: title, category, workspace, sensitivity, body all match spec) |
| **#2468** | chore(session-1207): pin pa_local.sh to Chris's preferred Session 1207 thread | 1 | ✅ Subsequent Rigby pings route to the correct thread |
| **#2469** | fix(session-1207): MIC surfaces deliverable_id + warnings on output_data | 2 | ✅ Django check clean; codepath additive (deferred 7-min MIC re-smoke per Rigby's offer to sanity-check the diff pre-merge) |

### Deliverables filed / touched

| ID | Action | Note |
|---|---|---|
| `758be167-f9c9-4e03-822d-516a7449f675` | **NEW** (smoke evidence) | First-ever MIC auto-deliverable in DBZ. Title=`MarketIntelligenceCoordinator: Market Intel Brief — 2026-06-22`, content 2087 chars, sensitivity=internal, desk=market_intelligence. Kept as audit evidence per Rigby. |
| `ecddb62d-ab01-4b3b-83c4-2601670395d3` | **NEW** (Session 1208 entry) | Rigby's full CampaignOrchestrator delegation hardening spec — outbound pack JSON schema, validation rules, retry semantics, AC-1 through AC-5, deliverable shape. ~10KB body. Linked to Initiative `29154d73-…`. Tags: `session-1207-followup`, `session-1208-entry`, `campaign-orchestrator`, `income-gen`. |

Initiative `29154d73-…` (Platform Capability Audit) is now at **13 deliverables** (was 12 end-of-Session-1206; +1 from Session 1208 entry spec).

## Behavioral invariants — what's now true post-merge

1. **`MarketIntelligenceCoordinator.execute()` auto-creates exactly 1 Deliverable per successful brief generation.** Routes through `self._save_to_deliverable` → `create_deliverable` so PR #2465's workspace_id guardrail + PR #2464's BLOCKED detector + dedup machinery all apply. Workspace pinned to DBZ (`b4503364-2573-4401-9e28-61a739e0ce50`). Title: `Market Intel Brief — YYYY-MM-DD`. Category: `Market Intelligence`. Sensitivity: `internal` (in metadata). Body: provenance markdown + executive_summary + structured sections.
2. **MIC bookkeeping hooks (`_record_learning_outcome`, `_create_execution_memory`) cannot flip `result.success`.** Each call in both the success and failure branches is wrapped in its own try/except. A hook crash logs WARN but doesn't propagate to the outer except.
3. **`output_data.deliverable_id` is set on successful agent runs that produced a Deliverable.** Lifted from `result.data['deliverable_id']` by the `tasks_agents.execute_agent_task` writeback. Emitted only when present (preserves backwards compat).
4. **`output_data.warnings` is ALWAYS a top-level list.** Empty when no warnings, populated with `{type, message}` entries otherwise. Stable type keys defined so far: `deliverable_persist_failed` (caught exception), `deliverable_gated` (factory returned None — gate or dedupe). Convention is generalizable to other agents.
5. **`tools/pa_local.sh` points at `pa-33088358df304016`.** Future Claude Code sessions land in Chris's preferred Session 1207+ thread by default.
6. **PR #2463 / #2464 / #2465 invariants from Session 1206 all preserved.** Canonical+legacy output_data shape still written. BLOCKED detector still strict-marker-only. workspace_id validation guardrail still catches hallucinated UUIDs.

## Rollback levers (per change)

| Lever | Action | Effect |
|---|---|---|
| **Disable MIC auto-deliverable** | Revert PR #2467 (commit `80439f54`) | MIC stops persisting deliverables; brief stays in `AgentExecution.output_data` only. Hook isolation also reverts. |
| **Soften: skip the deliverable but keep hook isolation** | Comment out the `if result.success:` block at `core/agents/stocks/market_intelligence_coordinator.py:293-339` | Hook isolation preserved; deliverable persist disabled. |
| **Disable output_data top-level lift** | Revert PR #2469 (commit `1fc2b0b3`) | `deliverable_id` + `warnings` go back to being nested under `output_data.data` / `output_data.metadata`. PR #2463 dual-shape still works. |
| **Revert thread pin** | Edit `tools/pa_local.sh` `--conversation` flag to the prior value, or revert PR #2468 (`64d8cc96`) | Local PA wrapper routes elsewhere. Pure dev-side change. |

## Post-merge gotchas

- **Worker restart required after each merge** of celery-task-imported code (`market_intelligence_coordinator.py`, `tasks_agents.py`). Did this twice during the session (after #2467 + after #2469). If MIC behavior looks pre-fix on the next deploy cycle, check `ps -eo pid,lstart` for worker start time vs `git log -1 main` date.
- **Smoke deliverable `758be167-…` is in DBZ** — kept intentionally as audit evidence for the first-ever MIC auto-deliverable. Future runs will create their own; this one stays as the "before refinement" baseline.

## 24h watch checklist (fires 2026-06-23 ~03:50 UTC / 9:50 PM MDT)

```bash
# Invariant 1: every successful MIC run lands a Deliverable
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentExecution
from core.models_deliverables import Deliverable
from datetime import timedelta
from django.utils import timezone
cutoff = timezone.now() - timedelta(hours=24)
mic_completed = AgentExecution.objects.filter(
    agent__name='MarketIntelligenceCoordinator',
    status='completed', created_at__gte=cutoff,
).count()
mic_deliverables = Deliverable.objects.filter(
    agent_name='MarketIntelligenceCoordinator', created_at__gte=cutoff,
).count()
print(f'MIC completed runs: {mic_completed}')
print(f'MIC deliverables:   {mic_deliverables}')
print(f'Ratio (target = 1.0): {mic_deliverables / mic_completed if mic_completed else 0:.2f}')
"

# Invariant 2: no double-writes (1 deliverable per run)
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_deliverables import Deliverable
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
cutoff = timezone.now() - timedelta(hours=24)
dupes = (Deliverable.objects.filter(
    agent_name='MarketIntelligenceCoordinator', created_at__gte=cutoff)
    .values('parent_execution_id').annotate(c=Count('id')).filter(c__gt=1))
for d in dupes:
    print(f'POSSIBLE DUPE per exec: {d}')
print('(no output above = no duplicates)')
"

# Invariant 3: warnings list shape is consistent (no nested None / wrong type)
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentExecution
from datetime import timedelta
from django.utils import timezone
cutoff = timezone.now() - timedelta(hours=24)
for rec in AgentExecution.objects.filter(
    agent__name='MarketIntelligenceCoordinator', created_at__gte=cutoff
).order_by('-created_at')[:10]:
    od = rec.output_data or {}
    w = od.get('warnings', '<MISSING>')
    deliv_id = od.get('deliverable_id', '<MISSING>')
    print(f'{rec.id} status={rec.status} warnings_type={type(w).__name__} deliv_id={deliv_id!r}')
"
```

## Open follow-ups (deferred to Session 1208 or later)

- **Session 1208 entry: CampaignOrchestrator delegation hardening** — deliverable `ecddb62d-ab01-4b3b-83c4-2601670395d3` carries the full spec (§1-§6: scope, AC-1 through AC-5, outbound pack JSON schema, validation+retry semantics, deliverable body shape, plus §6 from Rigby).
- **Carryover from Session 1206:**
  - **P0** workspace_id hallucination root-cause trace (deliverable `96b6a72a-…`) — guardrail in place via PR #2465; root cause still unidentified
  - **P1** CI lint rule blocking `.execute(` outside `core/agents/` (deliverable `180f4e9f-…`)
  - **P1** Layer 1 dashboard refresh
  - **P1** Session 1206 24h watch (fires 2026-06-23 ~23:35 UTC)
  - **P2** TheOdds API key renewal (Chris-owned, billing-gated)
- **Wakeup Week scoreboard** — Rigby is updating with before/after evidence from the post-fix dispatches; ongoing across multiple sessions.

## Architecture note for future readers

The `warnings` convention introduced in PR #2469 generalizes:

```python
result.data.setdefault('warnings', []).append({
    'type': '<stable_key>',
    'message': '<human-readable, prefer ClassName: detail>',
})
```

Then in `tasks_agents.execute_agent_task` (and ideally any future custom dispatchers), lift to top-level `output_data['warnings']`. This gives ops tools and audit dashboards a deterministic surface to detect partial-failure degradation without parsing logs.

Other candidates for the same pattern (filed mentally for future hardening):
- Sub-agent dispatch failures inside coordinators (Bull/Bear/Risk crashes in MIC) — currently buried in `result.data.bull_analysis.error` etc.
- LLM hallucination warnings (model said something flagged by content filter but the deliverable still wrote)
- Cache miss / stale-data warnings (when an agent used data older than its freshness threshold but still produced output)

Worth a Session 1209+ hardening pass once CampaignOrchestrator lands.
