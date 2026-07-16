# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2800 CLOSED — worker-startup orphan reap + CodeReviewAgent MISSING_INPUT (Option B done; BettingPage next per Chris sequencing)

**Refreshed 2026-07-16 (SESSION 2800 CLOSED — fourth consecutive same-day engineering ship (S2797 → S2798 → S2799 → S2800). Chris directive at open: `"let's do option B then stop"` — one session, one ship, clean termination. Verify-before-build reframed the ship from "5 broken agents" to "1 infra handler + 1 real agent-code fix" after finding 4 of 5 failures are worker-restart orphans (SESSION_1084 §197 corroborated). Ships: `_reap_orphan_agent_executions_on_startup` handler on `worker_process_init` in `core/celery.py` (bulk UPDATE stale in-progress rows to `cancelled`) + CodeReviewAgent MISSING_INPUT early-return with structured error_code (`core/agents/code_review_agent.py`) + smoke gate mgmt command. **Live proof at post-merge recycle**: `[CELERY_WORKER_STARTUP_REAP] transitioned 16 orphan AgentExecution row(s) to cancelled` on first worker startup — 16 rows that would have been silently reaped as `failed` at 60min are now honestly labeled as worker-restart interruptions. Rigby T1 SIGN with tool-run evidence (ops_tool failure signatures + recycle cross-ref); 5 folds persisted BEFORE Chris D-verdict (rows 85-89) per PLAYBOOK-6.10.8 — third consecutive session with correct fold-timing discipline. Novel: **first ship with a live-measurable capability-lift receipt** (16-row reap number is the load-bearing metric). FORTIETH close-cycle post-PLAYBOOK-7.4.4.)**

**S2800 ship:**

**PR #3213 · `4c339a6a6b2a`** — 4 files, +274 / -1. Worker-startup orphan reap handler in `core/celery.py` + CodeReviewAgent MISSING_INPUT structured error_code in `core/agents/code_review_agent.py` + `smoke_broken_agents_pre_fix` mgmt command (extends S2799 smoke pattern to agent level) + fresh session pin.

**Handoff:** `docs/handoffs/SESSION_2800_FIX_BROKEN_AGENTS.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (fortieth cycle). Reap handler fired on first worker startup, transitioned 16 orphan rows to `cancelled` — measurable evidence in `celery*.log`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **89 rows** (35 `same_pr_actionable` / 30 `same_pr_mitigatable` / 22 `future_trigger`); rows 85-89 are S2800 T1 folds.

**Live proof:** `grep CELERY_WORKER_STARTUP_REAP celery*.log` — every worker startup now emits the reap count, giving Chris a running metric of how many false-failures the ship prevents over time.

---

## SESSION-OPEN INFRA STORY (S2800)

**Fourth consecutive same-day engineering ship.** S2797 (public landing page) → S2798 (onboarding banner) → S2799 (Rigby tool signposts) → S2800 (broken-agent fixes). One conversation, four ships, 21 ledger folds (68 → 89). Chris scoped S2800 as terminal: `"let's do option B then stop"`.

**Root-cause reframe upstream of implementation.** Initial candidate framing was "fix 5 broken agents" per S2799 Thread 1 audit. Verify-before-build reading of `core/tasks_agents.py:2450-2523` (heartbeat thread) + SESSION_1084 §197 handoff surfaced: **4 of 5 failures are worker-restart orphans**, not real hangs. Heartbeat thread dies with worker on `make celery-recycle`, execution row's `last_heartbeat_at` freezes, cleanup watchdog reaps 60min later as `failed`. Every recycle manufactures 4-agent "failures" that inflate error stats. Ship reframed: 1 infra handler (fixes 4 of 5 at root) + 1 real agent-code fix (CodeReviewAgent MISSING_INPUT).

**Live-measurable capability-lift receipt.** Post-merge `make recycle-all`: `[CELERY_WORKER_STARTUP_REAP] transitioned 16 orphan AgentExecution row(s) to cancelled`. That's 16 rows that WOULD have been marked `failed` at 60min — instead honestly labeled `Worker restart — execution interrupted (S2800)` with machine-parseable reason. Second consecutive ship with quantitative post-ship evidence (S2799 signpost lift was measurable via `zoom_out_tool` routing; S2800 orphan reap is measurable via log grep).

**PLAYBOOK-6.10.8 discipline held (third session in a row).** 5 folds persisted between T1 SIGN and Chris "ship it." S2798 missed timing (persisted after D-verdict); S2799 corrected; S2800 held. Pattern stable.

**Rigby T1 verify-honesty explicit.** Fold row 89 admits worker-restart hypothesis is **strongly consistent but not fully proven** — she couldn't produce a definitive day-bucket histogram cross-referencing every "no heartbeat" failure with `recycle_events.jsonl`. Ship covers the 4-known-orphan pattern; signposted follow-up for non-recycle-day no-heartbeat failures (those are real hangs needing different treatment). Direct PLAYBOOK-6.10.9 compliance.

---

## S2801 CANDIDATES — BETTINGPAGE IS THE DEFAULT (Chris sequenced)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired (S2800 close); freshness should be FRESH · SHA-match at S2800 close SHA (`4c339a6a6b2a` or cascade PR SHA).
**Ledger baseline:** 89 rows expected (35/30/22). Any drift = investigate.
**Regression 17-suite:** 318 tests OK at S2798 open; unchanged (S2800 was reliability infra + agent fix; no test-covered surface).
**Reap monitor:** `grep CELERY_WORKER_STARTUP_REAP celery*.log` — running count of orphans caught since S2800 ship.

### ⭐ BETTINGPAGE (default per Chris sequencing) — first-user trace + top-1 fix

Per Chris directive at S2799 open (persisted): **C → B → BettingPage**. C shipped at S2799 (signposts). B shipped at S2800 (worker reap + CodeReviewAgent). BettingPage is next.

- **BettingPage first-user trace** — 9-tab, 3023-line surface. Unknown state for a first user. What breaks, what's empty, what looks half-connected? Trace + fix top-1. Same shape as S2798 onboarding routing (audit → verify-before-build → ship one concrete fix). ~1 session.

### Stock Intelligence — first non-betting revenue play (from S2799 Thread 3)

Deferred behind BettingPage per Chris sequencing but the strategic candidate:

- Add newsletter scheduler (send daily brief to Pro subscribers — 3 days work)
- Add Stripe subscription gate on premium briefs / SEC depth (2 days)
- Total: ~1-2 weeks to first non-betting revenue
- Genuinely differentiated vs ChatGPT (citation provenance + multi-agent debate)

### S2800 follow-ups (all deferred; not blocking)

- **Non-recycle-day no-heartbeat monitor** (fold row 89 future_trigger) — after 7 days, sweep `AgentExecution.error_message LIKE '%no heartbeat%'` and cross-reference against recycle_events.jsonl. Any orphan-day failures = real hang, different fix needed.
- **AudioAgent TTS payment wall** — separate config issue (ElevenLabs paid plan required). Not code; deferred until Chris decides on paid TTS provider.
- **CodeReviewAgent workspace file discovery** — deferred per Rigby T1 (fail-fast > implicit guessing). Revisit only if MISSING_INPUT rate is high for user experience.
- **`interrupted` status enum value** — deferred (existing `cancelled` + error_message string sufficient).

### S2799 follow-ups (all deferred; not blocking)

- **Per-signpost adoption telemetry** (S2799 F84) — fires 7 days post-ship (2026-07-23) if any of the 14 signposted tools has zero invocations
- **`ops_digest_tool` handler FieldError fix** — `Cannot resolve keyword 'pattern_hash'` at `core/services/td_handlers_ops.py` (5-line ORM fix)
- **`calendar_tool` rename/kill** — dead/misnamed
- **`mission_verdict` read-only variant** — so it can earn a signpost

### S2797/S2798 standing owed

- Onboarding banner in shared authed Layout (S2798 F3 future_trigger)
- Throttle on `POST /api/onboarding/complete/` (S2798 F4 future_trigger)
- Regression test for `complete_onboarding_view`
- Public deployment of LandingPage (hosting + DNS)
- Waitlist DB capture (Shape B)
- I-0303 scoping (RUR-C1 parent-close blocker)
- Regression tests for 4 S2796 tools
- 8 remaining per-tool docs need "Covered actions"
- 23 tools schema-lint fix
- Wire tenant boundary health → Celery beat
- `SESSION_819_SYSTEM_AUDIT_*` cleanup (19+ files)
- Doc-note gap-map classifier h3-truncation bug in S2795 F2 template spec

### Deferred (waiting on triggers)

- **NEW: S2800 F89** — non-recycle-day no-heartbeat failure monitor (concrete post-ship monitoring trigger)
- **S2799 F80** — SMOKE_FAIL cluster ≥4/14 = Option-B trigger (already resolved — Option-B shipped this session; downgraded to closed)
- **S2799 F83** — Dynamic signposts via PAToolLearningEnricher (v2) — fires when Chris wants to iterate signposts without a PR
- **S2799 F84** — Per-signpost adoption telemetry (7-day check post-2026-07-16)
- All S2797/S2798 triggers unchanged

---

## SESSION PIN — S2800 RETIRED (fresh mint required at S2801 open)

**Pin history (S2800):**

- `pa-5ca1a29ad6514475` (label `s2800-fix-broken-agents`) minted S2800 open; **retired at S2800 close (`force=true`, thirty-first consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-5ca1a29ad6514475` (retired)** — intended failure mode forces S2801 first-action fresh mint.

**S2801 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2800 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §7 (Chris directive queue)

# Freshness check. Should be FRESH · SHA-match at S2800 close SHA (or cascade PR SHA).
bash tools/pa_local.sh "S2801 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Ledger check: confirm 89-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==89, r
print('OK — 89 rows, counts:', r['counts_by_classification'])
"

# S2800 reap monitor — how many orphans did the handler catch since ship?
grep CELERY_WORKER_STARTUP_REAP celery*.log | tail -10
# For rolling total across all recycle events:
grep -c "CELERY_WORKER_STARTUP_REAP.*transitioned" celery*.log

# Regression 17-suite (unchanged; S2800 was reliability infra + agent fix)
python manage.py test \
  core.tests.test_ops_auth_regression_2772 \
  core.tests.test_ops_query_param_allowlist_2773 \
  core.tests.test_pa_wrapper_ownership_2776 \
  core.tests.test_zoom_out_classifications_2777 \
  core.tests.test_zoom_out_tool_2780 \
  core.tests.test_governance_auth_regression_2780 \
  core.tests.test_platform_auth_regression_2784 \
  core.tests.test_decision_approve_auth_regression_2785 \
  core.tests.test_csrf_enforcement_2787 \
  core.tests.test_platform_authz_sweep_2788 \
  core.tests.test_pilot_gates_authz_sweep_2789 \
  core.tests.test_time_travel_authz_sweep_2790 \
  core.tests.test_zoom_out_aggregations_2791 \
  core.tests.test_zoom_out_tool_aggregations_2792 \
  core.tests.test_zoom_out_time_window_2793 \
  core.tests.test_tenant_boundary_health_2794 \
  core.tests.test_pa_tools_gap_map_2795 \
  --noinput

# S2799 signpost lift check — count last-24h invocations on 14 signposted tools
python manage.py shell <<'PY'
from datetime import timedelta
from django.utils import timezone
from core.models_tool_calls import ToolCallRecord
from django.db.models import Count
SIGNPOSTED = [
    'rigby_shift_brief_tool', 'employee_tool', 'zoom_out_tool', 'learning_tool',
    'learning_patterns_tool', 'workflow_run_tool', 'gates_tool', 'pilots_tool',
    'revenue_tracker_tool', 'self_awareness_tool', 'brainstorm_tool',
    'ops_digest_tool', 'heartbeat_history_tool', 'surgical_moves_status_tool',
]
since = timezone.now() - timedelta(days=1)
counts = dict(ToolCallRecord.objects.filter(
    tool_name__in=SIGNPOSTED, created_at__gte=since
).values_list('tool_name').annotate(c=Count('id')).values_list('tool_name', 'c'))
for t in SIGNPOSTED:
    print(f'  {t}: {counts.get(t, 0)}')
print(f'Total signposted invocations in last 24h: {sum(counts.values())}')
PY

# Mint fresh pin scoped to BettingPage (or whichever candidate Chris picks).
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2801 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — zoom-out ask required; folds classify+persist BEFORE D-verdict; concrete code-state claims MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline.

**S2800 lessons to carry:**

1. **Verify-before-build reframes the ship.** Initial "fix 5 broken agents" framing was WRONG — root cause was 4-of-5 = worker orphans + 1-of-5 = real agent bug. Read SESSION_1084 §197 before touching any agent code; the finding likely applies to more agents than the 5 named.
2. **PLAYBOOK-6.10.8 discipline stable.** Three sessions in a row with folds persisted before D-verdict. Continue the pattern.
3. **Live-measurable receipts are the load-bearing verification.** The `[CELERY_WORKER_STARTUP_REAP] transitioned 16 rows` log line at post-merge recycle is quantitative evidence the fix works. Prefer receipts over "verified by inspection" wherever possible.
4. **Chris's "then stop" termination clause is cleaner than implicit one-ship-per-session.** Watch for reuse.

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2800 artifacts:**

- **Reap handler:** `core/celery.py` — `_reap_orphan_agent_executions_on_startup` (below shutdown handler)
- **CodeReviewAgent fix:** `core/agents/code_review_agent.py:341` — MISSING_INPUT early-return
- **Smoke gate:** `core/management/commands/smoke_broken_agents_pre_fix.py` (reusable — extension of S2799 pattern)
- **Handoff:** `docs/handoffs/SESSION_2800_FIX_BROKEN_AGENTS.md`
- **Live test:** `python manage.py smoke_broken_agents_pre_fix` (or `--as-json`)
- **Predecessors:** S2799 (signposts), S2798 (onboarding), S2797 (landing)

🖥️ **Workspace UI — `/workspaces` surface:**

- **No new Workspace tab** — reliability infra ship
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **89 rows** (35/30/22); rows 85-89 are S2800
  - `logs/recycle_events.jsonl` — +2 events during S2800 close
  - `celery*.log` — `[CELERY_WORKER_STARTUP_REAP]` log line on every worker startup (measurable)
  - `http://localhost:8000/welcome` — public LandingPage (unchanged since S2797)
  - `http://localhost:8000/workspace` — first-run banner (unchanged since S2798)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2800 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-5ca1a29ad6514475` (retired at S2800 close, force=true, thirty-first consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-5ca1a29ad6514475` (retired; forces fresh mint at S2801 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2800 open |
| Recycle log | `logs/recycle_events.jsonl` — +2 events during S2800 close |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **89 rows** (35 actionable / 30 mitigatable / 22 future_trigger) |
| Rigby signposts | 14 tools routed via `unified_pa_entrypoint.py:2799` (unchanged since S2799) |
| Broken agents queue | 4 of 5 fixed at root (worker-startup orphan reap); 1 of 5 fixed (CodeReviewAgent MISSING_INPUT). AudioAgent TTS payment wall = separate config, not code. |
| Worker reap metric | `[CELERY_WORKER_STARTUP_REAP] transitioned 16 orphan rows` (S2800 first post-merge recycle) |
| Non-betting revenue play | Stock Intelligence identified (TIER 1); deferred behind BettingPage per Chris sequencing |
| Test user for onboarding demo | `s2798_onboarding_test` / `test-onboard-s2798!` — state re-armed at S2798 close |
| Next move | Chris selects at S2801 open (BettingPage default per C→B→BettingPage sequencing) |

---

## Recommended session-open protocol (S2801)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2800 handoff §2 (novel-precedent moments) + §3 (T1 SIGN) + §7 (Chris directive queue)
4. **Freshness + regression 17-suite + ledger 89 verify** — see S2801 open sequence above
5. **S2800 reap monitor** — count `[CELERY_WORKER_STARTUP_REAP]` log lines since ship (proves fix keeps working)
6. **S2799 signpost lift check** — count last-24h invocations on 14 signposted tools
7. **Watch for** ledger 89-row baseline surviving cascade merge; freshness FRESH · SHA-match
8. If `staleness_verdict != FRESH` → escalate
9. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
10. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
11. **Default candidate: BettingPage first-user trace + top-1 fix** per Chris C→B→BettingPage sequencing
12. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
13. Chris directs S2801 P0 selection (BettingPage unless override)
14. Mint fresh pin with candidate-scoped label
15. Route work through Rigby joint agreement before coding
16. **PLAYBOOK-6.10.8 constitutional at v0.8.0 (S2799 + S2800 discipline held for third consecutive session):** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
17. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist
18. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2801:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/PLATFORM_WHAT_IT_IS.md`](docs/PLATFORM_WHAT_IT_IS.md) — **anchor for user-ready reasoning**
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
4. [`docs/handoffs/SESSION_2800_FIX_BROKEN_AGENTS.md`](docs/handoffs/SESSION_2800_FIX_BROKEN_AGENTS.md) — **S2800 handoff (current)**
5. [`docs/handoffs/SESSION_2799_RIGBY_TOOL_SIGNPOSTS.md`](docs/handoffs/SESSION_2799_RIGBY_TOOL_SIGNPOSTS.md) — S2799 predecessor
6. [`docs/handoffs/SESSION_1084_HANG_CONTAINMENT.md`](docs/handoffs/SESSION_1084_HANG_CONTAINMENT.md) — root-cause reference for S2800 orphan pattern
7. [`core/celery.py`](core/celery.py) — worker-lifecycle handlers (S2800 reap added)
8. [`core/agents/code_review_agent.py`](core/agents/code_review_agent.py) — MISSING_INPUT block at execute() top
9. [`core/management/commands/smoke_broken_agents_pre_fix.py`](core/management/commands/smoke_broken_agents_pre_fix.py) — smoke gate (agent-level extension of S2799 pattern)
10. [`core/services/unified_pa_entrypoint.py`](core/services/unified_pa_entrypoint.py) — TOOL SIGNPOSTS at line 2799 (S2799)
11. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 89 rows at S2800 close (rows 85-89 are S2800)
