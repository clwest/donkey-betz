# SESSION 2949 — A9: 4th Signal-Dispatch Rule (demand_spike → MarketMovementMonitorAgent) + per-rule diagnostics

**Date:** 2026-07-24
**Status:** CLOSED — PR #3538 + amendment PR #3539 merged, workers recycled twice
**HEAD at close:** `<filled at close cascade>`
**Merge commits:** squash `522a7026c` (PR #3538) + squash `47eb12bfe` (PR #3539)
**Twin mirrors (Architecture & Research workspace):**
- Content: `f6b386ab-19e6-4c33-990c-82773d6a96a3` (`initiative_phase_doc`)
- Ratification: `8dfb4644-e76b-49ab-aab4-4e07fa971cb0` (`ratification_record`, `category='governance'`)
- Both diagnostic-flag-cleared via ORM per known `deliverable_tool.create` bug.

---

## What shipped

**S2949 A9** — adds the **4th signal-dispatch rule** (`demand_spike` → `MarketMovementMonitorAgent`) per the S2948 deferred queue's A9 slot. Chris ratified opening A9 at session open with "Begin A9".

The rule ships alongside **per-rule diagnostics counters** in `scan_and_dispatch()` — Rigby's SIGN-cycle zoom-out fold flagged 4-rule fan-out starvation risk under the shared per-scan cap, classified `same_session_mitigatable`. The counters make starvation observable without changing drain-in-order semantics.

**Post-merge Rigby SIGN found a follow-on fold** classified `same_pr_mitigatable` — the `blocked_by_cap` counter incremented once then broke, under-reporting actual blocked magnitude. Chris ratified fix-now → amendment PR #3539 shipped in the same session.

## Files shipped

**PR #3538 (`522a7026c`):**
- **MODIFIED** `core/services/signal_dispatch_service.py` (+58) — 4th `SignalDispatchRuleDef`; `scan_and_dispatch()` now populates + returns `per_rule_diagnostics` alongside legacy `per_rule`; `_eligible_clusters_for_rule` refactored to return `(clusters, dedupe_excluded_count)` tuple.
- **MODIFIED** `core/tests/test_signal_dispatch_service.py` (+45) — 5 new tests: rule registry mapping, S2949 rule-count bump (3→4), demand_spike scanner fan-out, per_rule_diagnostics shape assertion, dedupe counter increment.

**PR #3539 (`47eb12bfe`) — amendment:**
- **MODIFIED** `core/services/signal_dispatch_service.py` (+6/-3) — `enumerate(eligible)` in scan loop; `blocked_by_cap += (len(eligible) - i)` and `blocked_by_daily_cap += (len(eligible) - i)` on break instead of +1.
- **MODIFIED** `core/tests/test_signal_dispatch_service.py` (+38) — 2 new tests asserting magnitude semantics (5-eligible + cap=2 → blocked_by_cap==3; daily-cap-exhausted + 4-fresh → blocked_by_daily_cap==4).

## Test evidence

- **60/60 tests pass** (`test_signal_dispatch_service` + `test_s2934_signal_dispatch_harness`) after amendment.
- Live-verify observed at `scan_signal_dispatch_rules.delay()` post-#3538 recycle (task_id `4858d440-b3f9-41a6-8a95-7fb145a4126a`):
  - `enqueued=0`, all 4 rules present in `per_rule_diagnostics`
  - `trend_emergence`: `blocked_by_dedupe=4`
  - `opportunity_window`: `blocked_by_dedupe=3`
  - `demand_spike` + `content_gap`: all zeros (matches ORM state — 0 active for both)

## Rigby SIGN — non-rubber-stamp evidence

**Pre-ship SIGN (agent-pick + spec):**
- `agent_introspection_tool` on 5 shortlisted agents (`MarketMovementMonitorAgent`, `MarketAnomalyDetectorAgent`, `OpportunityPipelineAgent`, `MarketIntelligenceAgent`, `TrendBreakDetectorAgent`)
- `ops_tool.execution_search` for 7d evidence on each
- Pick: **MarketMovementMonitorAgent** (22 execs / effectiveness 84 / best semantic fit for "spike/momentum" framing)
- Pattern-choice AGREE demand_spike over skill_demand (volume-amplification lens)
- Zoom-out fold: **starvation-by-ordering + shared-cap contention** with 4 rules → `same_session_mitigatable` → discharged via per_rule_diagnostics counters in same PR

**Post-merge SIGN (repo_tool.read evidence):**
- `core/services/signal_dispatch_service.py:82-107` — 4th rule shape verified
- `core/services/signal_dispatch_service.py:130-190` — counter wiring verified at correct points
- `core/tests/test_signal_dispatch_service.py:65-90` — new test presence verified
- Verdict: **AGREE**
- New zoom-out fold: **`blocked_by_cap` under-reports magnitude** — increments once then breaks → classified `same_pr_mitigatable` → Chris ratified fix-now → amendment PR #3539

## Chris ratifications

1. **A9 open** — "Begin A9" (session-open universal sequence step 4).
2. **Fix-now amendment** — plain-English A/B routing, Chris chose A ("fix it now") with implementation intent: "compute `remaining = len(eligible) - idx` and add that to `blocked_by_cap` before breaking; add one test that sets up eligible>cap and asserts `blocked_by_cap == remaining`."

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

1. **PR #3538 merged** → `make celery-recycle` → live-verify via `scan_signal_dispatch_rules.delay()` → all 4 rules present in diagnostics.
2. **PR #3539 (amendment) merged** → `make celery-recycle` → workers matched HEAD at close.

## Governance / pattern candidates

**Pattern candidate — same_pr_mitigatable fold shipped as same-session amendment PR** (first trigger this session): Rigby's `blocked_by_cap` fold was classified `same_pr_mitigatable` but the PR was already merged. Chris ratified same-session amendment PR (#3539) as the operational equivalent — "fix now" preserves the spirit of the fold classification even when the original PR is closed. Watch for corroboration; not codified.

**S2948 pattern candidate** ("Shape MVP + same-session ergonomic upgrade") — no new trigger this session; A9 was net-new engineering, not an MVP-then-upgrade loop.

**S2947 pattern candidate** ("spend-mutation endpoints must not be AllowAny") — unchanged; still one trigger.

## Rigby Tool Gap Ledger

No new formal entries. Known `deliverable_tool.create` diagnostic-flag bug re-hit twice (both S2949 mirrors) and re-worked-around via ORM as expected.

## Deferred queue additions from S2949

- **Fair-share round-robin scanning** — the counters make starvation _visible_ but don't _prevent_ it. Rule order in `SIGNAL_DISPATCH_RULES` tuple determines dispatch priority under cap contention. Fair-share (round-robin or slot-based) would need its own regression tests to prove no correctness drift. Ledger with trigger = observed non-zero `blocked_by_cap` on a rule after multiple scans.
- **`per_rule_diagnostics` in `SignalDispatch` audit rows** — currently the counters are logged + returned; not persisted per scan_run_id. If operators start querying "which rule got starved most yesterday?" ledger table growth would matter.

## Reference

- **S2949 shipped code:**
  - `core/services/signal_dispatch_service.py:82-108` — 4th `SignalDispatchRuleDef` (demand_spike__market_movement_monitor)
  - `core/services/signal_dispatch_service.py:130-200` — `scan_and_dispatch()` with per_rule_diagnostics
  - `core/services/signal_dispatch_service.py:210-241` — `_eligible_clusters_for_rule` returning tuple
- **S2948 upstream:** `docs/handoffs/SESSION_2948_NEW_4_CLUSTER_PICKER.md`
- **PR #3538** — feat: 4th rule + per-rule diagnostics
- **PR #3539** — fix: magnitude semantics for blocked_by_cap / blocked_by_daily_cap
