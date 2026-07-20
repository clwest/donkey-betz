# SESSION 2852 — list_caps cross-workspace auth tightened

**Date:** 2026-07-20
**Predecessor:** SESSION_2851_A1_W2_3_1_ENFORCEMENT_REPORT_SHIPPED.md
**Branch:** main
**PR shipped:** #3320 → merged as `f22f0c154`
**Session pin:** `pa-44c36fc1f144459f` (retires at S2852 close)

---

## TL;DR

Addresses S2851 Rigby SIGN Q3 latent-overexposure finding: `workspace_budget_tool.list_caps` previously exposed every workspace's name + spend to any PA tool caller regardless of ownership. Now applies the same three-way auth pattern ratified for `enforcement_report` at S2851 (#3.1):

- **staff** sees all workspaces
- **non-staff** auto-scoped to workspaces owned (`user_id == caller`)
- **unauthenticated** returns `[]` + `scope_note`

Zero migration; zero enforcement-behavior change; only visibility tightens for non-staff / unauth callers.

---

## What shipped

| Artifact | Detail |
|---|---|
| **PR #3320** `f22f0c154` | `list_caps` auth block + `scope_note` in response |
| **`core/services/td_handlers_ops.py`** | Auth scope block at L3949-L3978; scoping applied to both `include_defaults` branches |
| **`core/services/pa_tool_schemas.py`** | `list_caps` action description updated to note the new auto-scope behavior |
| **`tools/pa_local.sh`** | Session-open pin rotation to `pa-44c36fc1f144459f` |

---

## Working loop (S2852)

- **1 Rigby SIGN cycle** (Q1..Q4 including zoom-out ask), tool-grounded — 5 `repo_tool` calls with file+line evidence at HEAD
- **5 Rigby verdicts, all substantive:**
  - Q1a-c: is_staff resolution + three-way branching + both include_defaults paths — all functionally identical to enforcement_report
  - Q1 nit: UUID coercion — keep `scoped_ids` as native UUIDs (from `values_list('id', flat=True)`), don't `str()`-coerce early; include_defaults=False loop converts str `wid` → UUID at comparison site
  - Q2: low-risk shape drift — new `scope_note` field is backward-compatible for typical callers
  - Q3: correct empty-scope shape (`[]` + note vs 403)
  - Q4 zoom-out: (a) non-staff callers will see fewer rows — intended, no code callers coupling risk confirmed via grep; (b) UUID nit repeat (addressed); (c) pre-existing N+1 in include_defaults=False path — forward-carry, not introduced by this change
- **1 post-merge PA E2E** — `workspace_budget_tool.list_caps` confirmed `scope_note: "staff scope — all workspaces"` at top level
- **Zero rubber-stamps** — Rigby's tool_runs verified non-empty per `feedback_verify_rigby_tool_runs_before_trusting_sign`

---

## Verification

Post-merge, after `make recycle-all` at SHA `f22f0c154`:

```
workspace_budget_tool.list_caps (Rigby, staff scope)
→ scope_note: "staff scope — all workspaces"
→ 16 workspaces returned (Donkey Betz $4.02/$5.00, others $0.00)
→ enforcement_tier: "downgrade_and_freeze"
→ include_defaults: false
```

Behavior verified for staff path. Non-staff / unauth paths verified by code inspection (no non-staff test user set up locally — out of scope for this ship).

---

## Deferred to S2853 or later

- **W2 #3.2 downgrade-savings section** — extension of #3.1 report; blocked on canonical price-table wire
- **Auto-vs-operator event split for `enforcement_report`** (S2851 Q4b) — needs `evidence.trigger` completeness audit first
- **PA-surface E2E path for `llm_enforcer` hot-path swap** (S2850 Ledger #2) — Rigby's calling agent bypasses freeze/downgrade
- **`autopilot_tool.history` evidence surface** (S2850 Ledger #1) — expose evidence/result JSON
- **`clear_freeze` / `clear_downgrade` post-clear spend context** — inline spend + re-flag likelihood
- **N+1 in `list_caps` include_defaults=False path** — pre-existing, not introduced by this change; ledger candidate

---

## Substrate story (updated)

After S2846→S2852:
- per-workspace enforcement fires immediately on cap change ✓
- audit trail is correct (both cycle-triggered and operator-triggered attributed) ✓
- tracking is accurate (effective model recorded, not requested) ✓
- fleet auditability visible via `enforcement_report` ✓
- **read surfaces auth-scoped: staff / owner / unauth** ✓ (NEW at S2852)

---

## D6 moratorium

Still in force. No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

---

## For A1 W1 + W2 arc context

See:
- **S2851:** `docs/handoffs/SESSION_2851_A1_W2_3_1_ENFORCEMENT_REPORT_SHIPPED.md`
- **S2850:** `docs/handoffs/SESSION_2850_A1_W2_ENFORCEMENT_CORRECTNESS_LEG.md`
- **S2849:** `docs/handoffs/SESSION_2849_A1_W2_DEFAULTS_BACKFILL_SHIPPED.md`
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`
