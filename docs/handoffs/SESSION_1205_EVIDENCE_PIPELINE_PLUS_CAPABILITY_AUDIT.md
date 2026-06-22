# Session 1205 — Evidence pipeline fix + Tiered Capability Audit + first organic spider fire

**Status:** Closed clean. **4 PRs merged.** **10 audit deliverables filed on new Platform Capability Audit Initiative.** Platform end-to-end producer chain confirmed working for the first time in 48 hours.
**Date:** 2026-06-22
**Active conversation:** `pa-76aa5b61d0764d11` — Session 1205 evidence-card pipeline thread spawned mid-session via `session_tool create_fresh`. Prior thread `pa-1871b37227054254` (Session 1204) retired.
**Prior session:** [`SESSION_1204_PHASE_B2_DRIFT_QUALITY_FIX_CLOSE.md`](./SESSION_1204_PHASE_B2_DRIFT_QUALITY_FIX_CLOSE.md).
**Next session entry point:** Session 1206 — **Layer 1 telemetry blind-spot fix** (BaseAgent.execute creates AgentExecution row with idempotency guard). Single-PR, fixes Layer 1 + cascades to Layer 4.

## TL;DR

Session 1205 split into two arcs in one day:

**Arc A — Evidence pipeline fix (PR #2456).** Closed Session 1204's deepest finding: MLB Stage 1 brief had `[E1]-[E10] (no content)` cards. Traced ResearchAgent → `intelligence_tool` → `_handle_web_search` → `WebSearchTool` (Serper/DDGS). Found the bug at `research_agent.py:1209` — when search results had title but empty snippet, `_extract_best_evidence("")` returned the literal `(no content)`. Fix: `evidence_text = snippet or title`. Live-verified by re-dispatching MLB Stage 1 — new brief 6320 chars, zero "(no content)" markers, agent now reasons about parlay evidence cards.

**Arc B — Tiered Capability Audit + producer chain resurrection.** Operator initiated systematic audit across 4 layers (83 agents / 109 PA tool schemas + 174 handlers / 80 spiders / 8 learning bridges). Initiative `29154d73-…` created as the audit home. **Pass-1 inventory complete with 4 dashboard deliverables.** Critical finding: the platform has the same "wired but unscheduled producer" pattern at every layer. PRs #2457 + #2458 + #2459 + a one-time `PeriodicTask.enabled=True` flip restored producer fires. **First organic `run_spider_network` execution in 48+ hours completed at 18:00 local CDT** — 80 spiders, 1510 items, 0 errors, 199 downstream agent solutions auto-created via spider_agent_connector cascade.

The audit dashboards updated post-fire show Layer 3 (Spiders) jumping from **0 → 63 FRESH** in a single 4-min cycle. Layers 1, 2, 4 remained flat — but the audit ALSO surfaced WHY (telemetry blind spots — finding `65f1299f-…`). Session 1206 entry point is fixing those telemetry gaps so future audit runs are honest.

## Session Manifest

### PRs merged

| # | Title | Files | Lines | Verified |
|---|---|---|---|---|
| **#2456** | fix(session-1205): evidence cards fall back to title when snippet empty | `core/agents/research_agent.py` | +10 / -2 | ✅ live (MLB brief re-dispatched, 0 "(no content)") |
| **#2457** | feat(session-1205): beat schedule entries for 4 unscheduled producers (sports + market intel) | `core/celery.py` + `core/management/commands/add_critical_celery_tasks.py` | +43 (then +17/-12 fixup) | ✅ live (kalshi fired 200 markets at 17:15 + 18:15) |
| **#2458** | feat(session-1205): re-enable run-spider-network beat producer on local | `core/management/commands/add_critical_celery_tasks.py` | +11 / -1 | ✅ live (80 spiders / 1510 items at 18:00 local) |
| **#2459** | fix(session-1205): Makefile beat startup — tighten pgrep pattern + verify | `Makefile` | +27 / -8 | ✅ live (defensive verification block in place) |

### Initiative + deliverables on `29154d73-06a5-4630-abb4-3412cbdca5c5` Platform Capability Audit

Spawned as child of Reality Map (`0ecd1bc2-…`), workspace=DBZ, kind=investigation.

**Layer dashboards (one per layer):**
| ID | Title | Size | Headline |
|---|---|---|---|
| `7d221aa4-…` | Layer 1 Agent Capability Map (83 agents) | ~14.4KB | 31 active / 1 broken / 18 quiet / **56 UNTESTED**. ContentWriterAgent 64% sr (only BROKEN). |
| `bb1e0a98-…` | Layer 2 PA Tools Map (109 schemas + 174 handlers) | ~22.4KB | 28 active / **2 BROKEN** (intelligence_tool 60%, messaging_tool 69%) / 25 quiet / 120 UNTESTED |
| `6a200985-…` | Layer 3 Spider Network Map (80 spiders) | ~8.2KB post-fix | **63 FRESH** (post-fire) / 1 stale_recent / 8 stale_week / 6 stale_month / 2 UNTESTED |
| `dc970d99-…` | Layer 4 Learning Bridges Map (8 bridges) | ~6.3KB | 223 writes/30d but **per-bridge attribution heuristic broken** (10% accounted) |

**Deep-dive findings filed:**
| ID | Title | Severity |
|---|---|---|
| `6869fa55-…` | Sports Betting Agents Deep-Dive — wired but unscheduled | Resolved by PR #2457 |
| `65f1299f-…` | **Telemetry blind spot** — direct-constructor agent paths bypass AgentExecution | **Session 1206 P1** |
| `2de3d8d6-…` | theodds spider returns 0 events | Session 1206 investigation |
| `ed6a8f28-…` | SportsOddsAnalyst caller bug — None context at tasks_financial.py:2071 | Low priority cleanup |
| `ea561389-…` | First Producer→Data Win: Kalshi 200 markets + memory spike warning | Memory pattern → Session 1206 follow-up |
| `a4928480-…` | Makefile bug: make celery silently skips beat startup when tail -F running | Resolved by PR #2459 |

### Reframe: "Bucket semantics — platform-was-down"

Per operator clarification mid-audit: 30d activity windows reflect what the recently-recovering platform has happened to touch in debug/test sessions, NOT what's wireable. Renamed bucket `DEAD` → `UNTESTED` across Layers 1-3 with explicit context block. Each row in the dashboards is a checklist item; deep-dives become trust-trail stamps. Sports deep-dive (`6869fa55-…`) is the trust-trail template — "I checked. Here's what I found. Here's what's broken vs wireable."

### Producer chain state (end of session)

| Beat task | Enabled | Last run | Status |
|---|---|---|---|
| `run-spider-network` | ✅ True | 17:00 server (18:00 local CDT) | Fired clean — 80 spiders / 1510 items / 0 errors / 260s / 444MB memory spike |
| `collect-sports-odds-intelligence` | ✅ True | 17:00 server | Fired — events=0 (theodds dry; finding `2de3d8d6-…`) |
| `collect-kalshi-prediction-markets` | ✅ True | 17:15 server | Fired clean — 200 markets / 0 errors / 2.85s / 345MB memory spike |
| `market-intelligence-scan` | ✅ True | 17:00 server | Fired earlier; cascade hit telemetry blind spot (`65f1299f-…`) |
| `generate-daily-betting-brief` | ✅ True | (never) | Daily 7AM MT — first organic fire tomorrow morning |

Beat process state: PID 77436 (running as `nohup` without `--detach`; survives the `--detach` daemonization bug that caused the in-session 15-min beat outage). New Makefile (PR #2459) prevents the recurrence — `--detach` removed + defensive verification block exits 1 if beat fails to spawn.

## Behavioral invariants — what's now true post-merge

1. **Evidence cards extract from title when snippet empty** — ResearchAgent no longer emits `(no content)` cards. Card body becomes meaningful even when DDGS returns title-only results.
2. **5 producer beat tasks fire on schedule** — `run-spider-network` (every 30 min), `market-intelligence-scan` (every 2h), `collect-sports-odds-intelligence` (every 30 min), `collect-kalshi-prediction-markets` (every 1h), `generate-daily-betting-brief` (daily 7AM MT). All on local + prod per operator directive.
3. **Spider data flows end-to-end** — beat → run_spider_network → SpiderData rows → process_core_spider_data consumer → solutions created → agent assignment (via spider_agent_connector).
4. **Makefile pgrep tightened** — `pgrep -f "celery -A core beat"` only matches the actual beat process, not observability commands (`tail -F celery-beat.log`, etc.). All 4 sites updated.
5. **Beat startup verifies** — `make celery` exits 1 with remediation hint if beat fails to spawn. Silent degradation → loud failure.
6. **Capability Audit Initiative is the trust-trail home** — 4 layer dashboards + 6 deep-dives. Future audit runs refresh in place + append new findings.

## Rollback levers (per change)

| Lever | Action | Effect |
|---|---|---|
| Revert PR #2456 | Single-file revert (research_agent.py) | Evidence cards drop title fallback; "(no content)" comes back |
| Revert PR #2457 | Single-file revert + `PeriodicTask.filter(name__in=[4 names]).update(enabled=False)` | 4 sports/market producers stop firing |
| Revert PR #2458 + `PeriodicTask.objects.get(name='run-spider-network').update(enabled=False)` | Disable producer | Spider network goes silent again |
| Revert PR #2459 | Single-file revert (Makefile) | Beat startup back to loose pgrep + no verification |
| **Hot disable all producers** | `PeriodicTask.objects.filter(name__in=[5 names]).update(enabled=False)` | One-step pause; no code revert needed |
| **Hot disable specific producer** | `PeriodicTask.objects.filter(name='run-spider-network').update(enabled=False)` | Targeted pause if memory spike or cost becomes a concern |

## 24h watch checklist (run 2026-06-23)

```bash
# 1. Beat process still alive
pgrep -fa "celery -A core beat"
# expected: a single process; if 0, see finding a4928480 remediation

# 2. All 5 producer tasks have last_run < 2h ago (except daily brief)
USE_PGBOUNCER=1 python manage.py shell -c "
from django_celery_beat.models import PeriodicTask
from django.utils import timezone
from datetime import timedelta
since = timezone.now() - timedelta(hours=2)
for n in ['run-spider-network', 'collect-sports-odds-intelligence', 'collect-kalshi-prediction-markets', 'market-intelligence-scan']:
    t = PeriodicTask.objects.get(name=n)
    fresh = t.last_run_at and t.last_run_at >= since
    print(f'{n:35s} last_run={t.last_run_at} fresh<2h={fresh}')
"

# 3. Spider freshness — at least 60 spiders FRESH (<24h)
USE_PGBOUNCER=1 python manage.py shell -c "
from core.models_unified_system import SpiderData
from django.db.models import Max
from django.utils import timezone
from datetime import timedelta
yesterday = timezone.now() - timedelta(hours=24)
counts = SpiderData.objects.values('spider_name').annotate(m=Max('created_at'))
fresh = sum(1 for c in counts if c['m'] and c['m'] >= yesterday)
print(f'Spiders with last_emit < 24h: {fresh}')
# expected: >= 60 — was 0 pre-PR #2458
"

# 4. Memory spike pattern — does it persist or amplify?
grep "SPIKE.*run_spider_network\|SPIKE.*collect_kalshi" celery-long-running.log | tail -10
# expected: ~400-500MB spike per fire is the baseline; 800MB+ would be a real degradation
```

**Falsifying signals (any → flag):**
- Beat process disappears without operator action (the bug that caused 15-min in-session outage; PR #2459's defensive check should now prevent silent versions of this)
- Producer task `last_run_at` stays at pre-restart value (beat dispatching to dead queue)
- SpiderData stops growing (consumer chain hung or spider network task crashing)
- Memory spike exceeds 1GB per fire (real memory leak, not just buffering)

## Session 1206 entry point — Layer 1 telemetry blind-spot fix

**Single P1**: BaseAgent.execute() creates AgentExecution row with idempotency guard.

**Why this first**:
- Resolves the three "flat layer" findings (Layers 1, 4 directly; Layer 2 partially)
- Small scope: ~30 lines, one file (`core/agents/base_agent.py`)
- Idempotency contract: skip if `context.get('_execution_record_id')` is already set (router already creates a row; don't duplicate)
- High leverage: ALL audit dashboards become honest after this PR. Future Pass-2 deep-dives have accurate data.
- Direct fix to finding `65f1299f-…`

**Approach sketch**:
```python
# In BaseAgent.execute(), at the very start:
from core.models_unified_system import AgentExecution
if not context.get('_execution_record_id'):
    rec = AgentExecution.objects.create(
        agent=Agent.objects.filter(name=self.__class__.__name__).first(),
        task=task,
        status='in_progress',
        input_data={'context': context, ...},
    )
    context['_execution_record_id'] = str(rec.id)
# ... at end, update status='completed' or 'failed' with output_data
```

**Verification**: Re-run `_impl_market_intelligence_scan` after merge → 3 new AgentExecution rows for SportsOddsAnalyst + ArbitrageDetector + PredictionMarketAnalyst should land. Sports agents transition from UNTESTED → CONFIRMED WORKING in Layer 1 dashboard.

## Other Session 1206 candidates (queued, lower priority)

| Item | Priority | Source |
|---|---|---|
| Layer 1 telemetry fix (above) | **P1** | Finding `65f1299f-…` |
| Stage-1-only action-item gate relaxation | P2 | Session 1204 carryover (task #18) |
| Beat schedule entry for `process_initiative_auto_progression` | P2 | Session 1204 carryover (task #19) |
| Serper failure instrumentation | P2 | Session 1205 evidence-pipeline (task #20 close) |
| Memory spike pattern investigation | P2 | Finding `ea561389-…` (kalshi 345MB + run_spider_network 444MB) |
| ContentWriterAgent 64% success rate deep-dive | P2 | Layer 1 dashboard only BROKEN agent |
| `intelligence_tool` 60% success rate fix | P2 | Layer 2 dashboard + Spine 3 Tool Migration Hardening |
| `messaging_tool` 69% success rate (Discord/Slack) | P3 | Layer 2 dashboard |
| theodds spider 0-events investigation | P3 | Finding `2de3d8d6-…` |
| SportsOddsAnalyst None-context wiring | P3 (cleanup) | Finding `ed6a8f28-…` |
| Phase B.1 24h watch — fires ~14:48 UTC tomorrow | P1 (time-gated) | Session 1203 carryover |
| Daily inference accuracy watch Day-3 | P1 (daily) | Session 1198-1200 protocol |

## Memory rule confirmations / additions

- **`make celery` silently skips beat startup when tail -F celery-beat.log is running** — finding `a4928480-…`, fixed by PR #2459. Worth a memory rule: "When `pgrep -f` patterns are used to guard process startup, match the distinctive command invocation pattern (`celery -A core beat`), not generic substrings that could appear in observability commands." Filed as Session 1205 close-out.
- **`--detach` silently fails on macOS Celery beat** — Session 1205 lost 15 minutes to a runaway beat process started with `--detach` that consumed 100%+ CPU and never wrote logs. PR #2459 removes `--detach` from the Makefile; `nohup … &` is the correct backgrounding pattern. Worth a memory rule.
- **The Capability Audit deliverables are the trust trail** — operator's framing: each row in a dashboard is a checklist item; each deep-dive deliverable is a verification stamp. The audit Initiative `29154d73-…` is the canonical home.

## Active conversation

`pa-76aa5b61d0764d11` — Session 1205 evidence-card pipeline thread. Carries the full evidence-pipeline arc, audit setup, and producer-chain debugging. Probably worth a fresh Session 1206 thread on first ping (telemetry fix is a different arc).

**Donkey Betz workspace_id (pin):** `b4503364-2573-4401-9e28-61a739e0ce50`. **50 Initiatives total** (Session 1204 was 50, +1 from Capability Audit `29154d73-…`, -1 archived test Initiative = net +1 / total 50). **31 Initiatives still have NULL `target_workspace_id`** — backfill remains scheduled in roadmap §B.3.

## Standard FIRST THING checks (Session 1206)

1. Disk + swap (per Session 1158 memory).
2. Through Rigby (`tools/pa_local.sh` pinned to current thread): `platform_config_tool overview` → confirm `service_context: local`.
3. **Worker + beat freshness check (Session 1205 add)**: `ps -eo pid,lstart | grep celery` — verify beat is alive AND from a sane start time. If beat is missing or its CPU usage looks runaway, see finding `a4928480-…` remediation. Per PR #2459, `make celery` now exits 1 on beat startup failure.
4. `gh pr list --author @me --state open` — expected empty.
5. **Phase B.1 24h watch** (fires ~14:48 UTC 2026-06-23).
6. **Spider freshness check** (post-PR #2458): `SpiderData` rows with `created_at` in last hour should be ~60+. If 0, run-spider-network has stopped firing.

---

**Session 1205 verdict:** Audit complete; producer chain resurrected; 4 PRs landed; 10 audit deliverables filed; trust trail established. Layers 1/4 still flat in dashboard but root cause identified and Session 1206 P1 fix scoped. Memory spike pattern + Serper instrumentation + action-item gate all queued with concrete pointers. **The platform's spider→data→agent-solution pipeline ran end-to-end for the first time in 48+ hours.**
