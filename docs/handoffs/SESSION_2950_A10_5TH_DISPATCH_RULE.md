# SESSION 2950 — A10: 5th Signal-Dispatch Rule (skill_demand → TrendAnalysisAgent, intentional reuse)

**Date:** 2026-07-24
**Status:** CLOSED — PR #3541 merged, workers recycled
**HEAD at close:** `<filled at close cascade>`
**Merge commit:** squash `4850c8e26` (PR #3541)
**Twin mirrors (Architecture & Research workspace):**
- Content: `67c20981-6d5d-42e3-aa59-63b0ff94e420` (`initiative_phase_doc`, diagnostic cleared)
- Ratification: `11406369-48d7-4add-810e-fd66a08b6381` (`ratification_record`, `category='governance'`, diagnostic already null)

---

## What shipped

**S2950 A10** — adds the **5th signal-dispatch rule** (`skill_demand` → `TrendAnalysisAgent`) per the S2949 deferred queue's A10 slot. Chris ratified "Begin A10" at session open.

**Design decision — intentional agent reuse:** TrendAnalysisAgent already handles `trend_emergence` (rule #1). Claude push-back on reuse coupling triggered a Rigby two-philosophy framing:
- **(a) Reuse TrendAnalysisAgent** — proven "signal → brief" reliability (15 completed executions past 30d), skill_demand framed as labor-market/skills subtype.
- **(b) MarketIntelligenceAgent** — cleaner per-pattern attribution but only 5 lifetime execs / no recent activity.

Converged on (a) with rationale: for a net-new rule the primary risk is "will output be useful?", so proven brief-format reliability outweighs untested distinctness. Attribution concern (mixed metrics under one agent) ledgered for when per-pattern dashboards land.

## Files shipped

**PR #3541 (`4850c8e26`):**
- **MODIFIED** `core/services/signal_dispatch_service.py` (+22) — 5th `SignalDispatchRuleDef` with intentional-reuse framing comment.
- **MODIFIED** `core/tests/test_signal_dispatch_service.py` (+44) — 4 new tests: mapping, rule-count bump (4→5), reuse lock-in (TrendAnalysisAgent serves 2 rules), scanner fan-out for skill_demand; +1 line update to the diagnostics-shape test to iterate 5 rule keys.

## Test evidence

- **63/63 tests pass** (`test_signal_dispatch_service` + `test_s2934_signal_dispatch_harness`).
- Live-verify observed at `scan_signal_dispatch_rules.delay()` post-recycle (task_id `631d3c89-9784-4370-81b3-f8fbf2585c77`):
  - `enqueued=0`, all 5 rules present in both `per_rule` + `per_rule_diagnostics`
  - `skill_demand__trend_analysis` diagnostics all-zeros (matches 0-active baseline)

## Rigby SIGN — non-rubber-stamp evidence

**Pre-ship SIGN (agent-pick):**
- `agent_introspection_tool` on MarketIntelligenceAgent, MarketingStrategyAgent, OpportunityPipelineAgent, TrendAnalysisAgent
- `ops_tool.execution_search` (30d) for each
- Initial pick: TrendAnalysisAgent (15 execs 30d, best "signal → brief" reliability)
- **Claude push-back** on reuse coupling → Rigby laid out the two philosophies with pros/cons
- **Converged pick: TrendAnalysisAgent** with explicit reuse-framing rule comment
- Zoom-out fold: **future_trigger** — promote NEW-6 fair-share round-robin when ≥2 patterns are concurrently active + hitting caps

**Post-merge SIGN (repo_tool.read evidence):**
- `core/services/signal_dispatch_service.py` (rule region) — verified 5th rule + reuse comment present
- `core/tests/test_signal_dispatch_service.py` lines 90-125 — verified 3 new tests
- Verdict: **AGREE**
- Zoom-out fold: **future_trigger** — cross-rule allocation bias / cap contention risk over ~7d

## Chris ratifications

1. **A10 open** — "Begin A10 please" (session-open directive).

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

1. **PR #3541 merged** → `make celery-recycle` → live-verify via `scan_signal_dispatch_rules.delay()` → all 5 rules present in diagnostics.

## Governance / pattern candidates

**No new pattern candidates this session.** Prior candidates unchanged:
- S2948: "Shape MVP + same-session ergonomic upgrade" (1 trigger)
- S2947: "spend-mutation endpoints must not be AllowAny" (1 trigger)
- S2949: "same_pr_mitigatable fold shipped as same-session amendment PR" (1 trigger)

## Rigby Tool Gap Ledger

No new formal entries. Known `deliverable_tool.create` diagnostic-flag bug re-hit on content mirror only (ratification mirror was created with null diagnostic_status — inconsistent behavior worth noting but not a new gap).

## Deferred queue additions from S2950

- **Per-pattern effectiveness attribution work** — when per-pattern dashboards land, TrendAnalysisAgent's mixed workload (trend_emergence + skill_demand) needs disambiguation. Options: (1) add `pattern_type` header to agent brief output; (2) tag `AgentTaskExecution` rows with `signal_pattern_type` for downstream aggregation. Trigger: first request for "which pattern is TrendAnalysisAgent most effective on?" or first pattern-scoped effectiveness dashboard.
- **Fair-share round-robin scanning (NEW-6)** — still deferred; promotion trigger from S2950 Rigby zoom-out: ≥2 patterns concurrently active + hitting caps, observed over ~7d in `blocked_by_cap` diagnostics.

## Reference

- **S2950 shipped code:**
  - `core/services/signal_dispatch_service.py:105-125` — 5th `SignalDispatchRuleDef` (skill_demand__trend_analysis)
- **S2949 upstream:** `docs/handoffs/SESSION_2949_A9_4TH_DISPATCH_RULE.md`
- **PR #3541** — feat: 5th signal-dispatch rule with intentional TrendAnalysisAgent reuse
