# SESSION 2853 — W2 #3.2 downgrade-savings section shipped

**Date:** 2026-07-20
**Predecessor:** SESSION_2852_LIST_CAPS_AUTH_TIGHTENED.md
**Branch:** main
**PR shipped:** #3322 → merged as `fcffd2dd9`
**Session pin:** `pa-99ad8aeca6e7477e` (retires at S2853 close)

---

## TL;DR

Extends `workspace_budget_tool.enforcement_report` with an opt-in
`include_downgrade_savings` flag that surfaces per-workspace + top-level
downgrade-model usage plus an estimated savings dollar figure vs
pre-downgrade `gpt-5.2` rates. Answers "did the S2850 policy-triggered
downgrade actually save money?" — the visible payoff leg of the
S2850 enforcement-correctness arc.

Ships a **scoped** pricing table (`core/services/ops_autopilot/pricing.py`)
that surfaces (and explicitly does NOT resolve) the pre-existing 3-way
price-site divergence across `llm_enforcer.py:606-627`,
`llm_enforcer.py:697-701`, and `base_agent.py:2592-2593`. Whole-repo
single-source refactor deferred as a separate arc.

Zero migration; zero enforcement-behavior change; response shape is
backward-compatible when the new flag is not set.

---

## What shipped

| Artifact | Detail |
|---|---|
| **PR #3322** `fcffd2dd9` | 4 files, +224 -1 |
| **NEW `core/services/ops_autopilot/pricing.py`** | 67 lines — `MODEL_PRICES` (Decimal) + `estimate_uncached_cost()` helper. Docstring explicitly bounds: "Do NOT use for billing; LLMCallLog.cost is authoritative." Names the 3 divergent price sites in the repo. |
| **`core/services/td_handlers_ops.py` (+128)** | `enforcement_report` handler gains `include_downgrade_savings=false` payload flag; extra batch aggregate on `LLMCallLog` filtered by `model_id=BUDGET_DOWNGRADE_MODEL`; per-workspace `downgrade_model_calls_count / _actual_cost_usd / _would_have_cost_usd / _estimated_savings_usd`; top-level `downgrade_model_totals` + `downgrade_savings_note`. Decimal-throughout. |
| **`core/services/pa_tool_schemas.py` (+27)** | New `include_downgrade_savings` boolean schema field + over-estimate caveat prose for LLM callers. `enforcement_report` action description updated. |
| **`tools/pa_local.sh`** | Session-open pin rotation to `pa-99ad8aeca6e7477e` |

---

## Working loop (S2853)

- **1 Rigby pre-code design ping** (task `ce7f8eb5…`) — 4 questions including the load-bearing price-site decision (`llm_enforcer.py:697-701` vs `base_agent.py:2592`). Rigby returned conditional-YES with 5 concrete refinements (Decimal contract, `downgrade_model_*` naming for forward-carry semantic stability, top-level totals block, `Coalesce` NULL safety, docstring anti-misuse line). All 5 adopted verbatim.
- **1 Rigby SIGN cycle on the diff** (task `cd585bdb…`) — tool-grounded via `repo_tool` (7+ reads including whole-file, targeted line ranges, and cross-file greps). **Caught a BLOCKING KeyError bug**: dict build used `actual_cost/would_have_cost/savings` keys, downstream reads used `actual/would_have/savings` — would have exploded on first PA call with the flag set. Fixed at `td_handlers_ops.py:4457-4460` before second-turn AGREE-TO-SHIP.
- **1 pre-merge E2E direct handler invocation** — verified new keys present, values numerically correct, backward-compat rows still intact.
- **1 post-merge PA E2E** via Rigby dispatch (task `489e9fe8…`) — workers on SHA `fcffd2dd9` serving new code; Donkey Betz workspace row confirmed with all 4 new fields; top-level `downgrade_model_totals` = `{model_id:'gpt-5-mini', calls:1, actual_cost_usd:0.000399, would_have_cost_usd:0.00301175, estimated_savings_usd:0.00261275}`.
- **Zero rubber-stamps** — Rigby's `tool_runs` verified non-empty on all 3 dispatches per `feedback_verify_rigby_tool_runs_before_trusting_sign`.
- **No Chris ratification needed** — additive, opt-in, backward-compat feature extension.

---

## Verification

Post-merge `make recycle-all` at `fcffd2dd9`:

```
workspace_budget_tool.enforcement_report (Rigby PA dispatch, staff scope)
  window=30d, include_downgrade_savings=true
  → top-level: downgrade_model_totals {model_id:'gpt-5-mini', calls:1,
    actual_cost_usd:0.000399, would_have_cost_usd:0.00301175,
    estimated_savings_usd:0.00261275}
  → 16 rows returned; Donkey Betz row has all 4 new fields populated,
    zero-activity workspaces have all 4 at 0.0
  → backward-compat fields (attributed_spend_usd, calls,
    enforcement_events_count) all still present
  → new downgrade_savings_note explains over-estimate + uncached caveat
```

Query drives real data via `(workspace, -created_at)` index on `LLMCallLog`.

---

## Pre-existing surfacings

The single real-data gpt-5-mini row we have shows `actual_cost=$0.000399`
for 1721 input tokens + 0 completion tokens. My pricing.py entry
(from `llm_enforcer.py:697-701`, $0.50/1M input) would compute
$0.000861 — and `base_agent.py:2592` ($3.00/1M input) would compute
$0.005163. **Three different numbers, none matches.** The
`LLMCallLog.cost` for that row was written by yet a fourth estimator.

Rigby predicted this in the pre-code design ping (Q4.5). The
`downgrade_savings_note` handler prose explicitly frames it: "actual_cost
may include caching discounts or provider variance… Diagnostic estimate
only; as-of query time, not a reconciled billing ledger." Load-bearing
that whole-repo pricing-canonicalization refactor stays a separate arc.

---

## Deferred to S2854 or later

- **Whole-repo pricing-canonicalization refactor** (surfaced anew by this ship) — reconcile `base_agent.py:2592` divergent gpt-5-mini price + any other estimator sites into a single MODEL_PRICES source. Blocks whole-fleet cost-accuracy claims.
- **Auto-vs-operator event split for `enforcement_report`** (S2851 Q4b) — still needs `evidence.trigger` completeness audit first
- **PA-surface E2E path for `llm_enforcer` hot-path swap** (S2850 Ledger #2)
- **`autopilot_tool.history` evidence surface** (S2850 Ledger #1)
- **`clear_freeze` / `clear_downgrade` post-clear spend context**
- **N+1 in `list_caps` include_defaults=False path** (S2852 Rigby Q4 finding — pre-existing)
- **`was_downgraded` flag on `LLMCallLog`** — would let downgrade-savings distinguish enforcer-forced from natively-mini calls (removes the OVER-estimate caveat). Migration required.

---

## Substrate story (updated)

After S2846→S2853:
- per-workspace enforcement fires immediately on cap change ✓
- audit trail is correct (both cycle-triggered and operator-triggered attributed) ✓
- tracking is accurate (effective model recorded, not requested) ✓
- fleet auditability visible via `enforcement_report` ✓
- read surfaces auth-scoped: staff / owner / unauth ✓
- **downgrade savings estimate visible per-workspace + fleet-total** ✓ (NEW at S2853)

---

## D6 moratorium

Still in force. No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

---

## For A1 W1 + W2 arc context

See:
- **S2852:** `docs/handoffs/SESSION_2852_LIST_CAPS_AUTH_TIGHTENED.md`
- **S2851:** `docs/handoffs/SESSION_2851_A1_W2_3_1_ENFORCEMENT_REPORT_SHIPPED.md`
- **S2850:** `docs/handoffs/SESSION_2850_A1_W2_ENFORCEMENT_CORRECTNESS_LEG.md`
- **S2849:** `docs/handoffs/SESSION_2849_A1_W2_DEFAULTS_BACKFILL_SHIPPED.md`
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`
