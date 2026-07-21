# Session 2857 — `workspace_budget_tool.simulate_enforcement` Shipped

**Date:** 2026-07-20
**HEAD at close:** `52cf41287`
**PR:** [#3331](https://github.com/clwest/donkey-betz-platform/pull/3331)
**Prior session:** [SESSION_2856](SESSION_2856_AUTOPILOT_HISTORY_EVIDENCE_AND_ENFORCEMENT_SPLIT_SHIPPED.md)
**Session pin retired at close:** `pa-cda874e3ee284874`

---

## TL;DR

Shipped one net-new PA-tool action per S2857 open recommendation: **`workspace_budget_tool.simulate_enforcement`**. Operators and customer demos can now fire the workspace freeze + downgrade enforcer against a synthetic daily-spend value without dropping to Django shell (the prior workaround because Rigby's `PersonalAssistant` calling agent bypasses freeze at `core/llm_enforcer.py:271` `_critical_agents`).

Also expanded during this session per Rigby SIGN mods:
- `enforcement_report` gains `include_simulated` opt-in (default `false`) so demo/verification traffic stays out of `operator_events_count` / `auto_events_count`.
- `enforce_workspace_freeze` + `enforce_workspace_downgrade` gain additive `simulated=False` kwarg. Kwarg default preserves prior behavior — all 43 pre-existing S2856 + pricing_catalog tests pass unchanged.

**26 new pytest cases across 5 classes** + 43 pre-existing = **69 total green**. Post-recycle Rigby E2E confirmed all 3 decision tiers on `chris-personal` workspace (below cap → no_op; at soft limit → would_set_downgrade; above cap → would_freeze + would_set_downgrade).

---

## What shipped

### PR #3331 `52cf41287`

Files (752 insertions, 7 deletions):

| File | Δ | Change |
|---|---|---|
| `core/services/ops_autopilot/budget.py` | +20 | `simulated=False` kwarg on both enforce_ methods; threads `evidence['simulated']=True` when set |
| `core/services/td_handlers_ops.py` | +220 | `enforcement_report.include_simulated` filter + new `simulate_enforcement` action handler (~170 lines) |
| `core/services/pa_tool_schemas.py` | +73 | `simulate_enforcement` in action enum; extended description; new `simulated_daily_spend_usd` + `include_simulated` params; extended `dry_run` and `workspace_id` descriptions |
| `core/tests/test_s2857_simulate_enforcement.py` | +446 (new) | 26 tests: dry-run decision math (7), live enforce (5), auth (4), validation incl. nan/inf (6), enforcement_report simulated filter (3) |

### API shape

```python
# workspace_budget_tool.simulate_enforcement
payload = {
    "action": "simulate_enforcement",
    "workspace_id": "<UUID>",
    "simulated_daily_spend_usd": 5.50,   # required, finite float ≥ 0
    "dry_run": True,                     # default true
}

# Dry-run response (no state written):
{
    "action": "simulate_enforcement",
    "workspace_id": "...",
    "workspace_name": "chris-personal",
    "simulated_daily_spend_usd": 5.5,
    "dry_run": True,
    "thresholds": {
        "cap_usd": 5.0,
        "downgrade_set_threshold_usd": 3.5,   # cap * soft_pct (70%)
        "downgrade_clear_threshold_usd": 3.0, # cap * clear_pct (60%)
        "soft_limit_pct": 0.7,
        "clear_pct": 0.6,
        "currently_frozen": False,
        "currently_downgraded": False,
    },
    "freeze_decision": "would_freeze",
    "downgrade_decision": "would_set_downgrade",
    "freeze_action": None,       # dry-run, no action taken
    "downgrade_action": None,
    "note": "dry_run=true — no state written and no AutopilotAction rows "
            "created. Pass dry_run=false to fire the enforcer (WARNING: "
            "real workspace freeze/downgrade flags WILL be written and "
            "llm_enforcer will block or downgrade real calls for this "
            "workspace until clear_freeze / clear_downgrade is called).",
}
```

### Decision math

| Simulated spend | freeze_decision | downgrade_decision |
|---|---|---|
| `< downgrade_clear_threshold` while currently downgraded | `no_op_below_cap` | `would_clear_downgrade` |
| `< downgrade_set_threshold` (70% of cap) | `no_op_below_cap` | `no_op_below_soft_limit` |
| `>= downgrade_set_threshold` and `< cap` | `no_op_below_cap` | `would_set_downgrade` (or `no_op_already_downgraded`) |
| `>= cap` | `would_freeze` (or `no_op_already_frozen`) | `would_set_downgrade` (or `no_op_already_downgraded`) |

### Attribution

Live-path (`dry_run=false`) writes to SystemConfiguration flags AND creates AutopilotAction audit rows with:
- `agent_name = 'workspace_budget_tool'`
- `policy = 'workspace_budget_tool'`
- `evidence.actor_user_id = str(user_id)`
- `evidence.trigger = 'simulate_enforcement'`
- `evidence.simulated = True` ← S2857 marker

`enforcement_report` filters `evidence.simulated=True` rows out of `operator_events_count` and `auto_events_count` by default; opt in via `include_simulated=true`. Response `note` field records which mode applied.

---

## Working loop validated at S2857

- **1 Rigby pre-code design SIGN cycle** (1 turn): AGREE-TO-BUILD on Q1/Q2/Q4, DISAGREE-with-mods on Q3 (adopted `evidence.simulated=True` + `include_simulated` opt-in on report). 9 tool_runs across `repo_tool` grounding checks — verified enforce_ signatures, `_critical_agents` bypass, `_authorize_mutation` shape, S2856 split rule.
- **1 Rigby post-code diff SIGN cycle** (1 turn): 6 independent `repo_tool.read_file` verifications on the actual staged hunks. AGREE on Q2/Q4, mild-DISAGREE on Q1 (kwarg placement description) and Q3 (missing `math.isfinite()` guard for nan/inf). Fix applied inline before ship + 2 test cases added.
- **Post-recycle Rigby E2E** on `52cf41287`: 3 dry-run decisions across spend tiers verified live on `chris-personal` workspace (`33aa1e08-…`). Validation error correctly returned for `-1.0`. Response shape matches spec.

Chris ratified the S2857 slate at session open ("go ahead with simulate_enforcement") per `feedback_claude_rigby_agree_first_chris_yes_no` — Rigby's mods to Q3 (evidence.simulated + report filter + nan/inf guard) are scope-preserving refinements that landed in the same PR.

---

## Rigby zoom-out folds (S2857 open)

Per `feedback_zoom_out_ask_per_rigby_sign`, the pre-code SIGN Q5 included the mandatory open-ended zoom-out. Rigby raised two coupling/risk items — both **shipped same-PR** (not deferred):

1. **Q5(a) — Report pollution risk**: Simulated events flowing through `enforcement_report.operator_events_count` could skew operator "did enforcement fire this week" reads. **Applied same-PR**: `include_simulated=false` default filter + `evidence.simulated=True` marker.
2. **Q5(b) — Real hot-path side-effect**: `dry_run=false` actually writes to `SystemConfiguration:workspace_freeze_active:<uuid>`, meaning `llm_enforcer` WILL block real calls until operator calls `clear_freeze`. **Applied same-PR**: response `note` field carries explicit warning naming the follow-up `clear_freeze` / `clear_downgrade` calls in BOTH dry-run and live paths.

Post-code SIGN Q3 raised a THIRD item (not from zoom-out but from independent diff verification):

3. **`math.isfinite()` guard** — `float('nan')` and `float('inf')` passed the `< 0` check silently. **Applied same-PR**: 3-line guard + `test_nan_spend_rejected` + `test_inf_spend_rejected` cases.

**First trigger observed on pre-code Q5(c) — EnforcementContext dataclass**: Post-code Q5 raised the question of consolidating `actor_user_id` + `trigger` + `simulated` (and growing) into an `EnforcementContext` dataclass rather than continuing to pipe kwargs. **Deferred** — first trigger only; awaits second trigger before Playbook amendment per PLAYBOOK precedent (2-trigger threshold; 4-trigger for stricter arcs).

---

## What did NOT ship at S2857 (S2858 candidates)

Same list as S2857 open with one row promoted:

1. **`clear_freeze`/`clear_downgrade` post-clear spend context** (carried) — currently `clear_freeze` just deletes the flag; inline the spend + re-flag likelihood in the response so operator doesn't have to re-call `get_status`. ~30 min.
2. **N+1 in `list_caps include_defaults=False` path** (S2852 Rigby Q4 pre-existing finding) — `ProjectWorkspace.objects.get(id=wid)` inside loop at `td_handlers_ops.py:4013`. Batch with `filter(id__in=[…]).in_bulk(field_name='id')` prefetch. ~30 min.
3. **`selected_fields` param for `autopilot_tool.history include_evidence`** (S2856 Rigby Q5c zoom-out fold, first trigger). Blocked until second consumer complains about payload size.
4. **`enforcement_action_types` shared constant** (S2856 pre-code Q5b, first trigger). Not urgent until fifth action_type added.
5. **`actor_user_id` as first-class column on `AutopilotAction`** (S2856 pre-code Q5a, first trigger — MIGRATION required). Deferred until schema-migration budget opens.
6. **`EnforcementContext` dataclass consolidation** (S2857 post-code Q5, first trigger). Awaits second independent trigger.
7. **Phase 2B pricing arc** (only if reconciliation trigger surfaces).
8. **A4 warm-up under ratified constraints** — S2846 6-line block still in force.

---

## A4 Warm-up Operating Constraints — refreshed at S2857 close

Same as S2856 — no substrate changes to A4 lane at S2857. Added capability claim:

> **(l)** Operators + demo audiences can now trigger the freeze + downgrade enforcer against a synthetic spend value without needing shell access — via `workspace_budget_tool.simulate_enforcement`. Dry-run reveals decisions + thresholds; live path writes real flags with `evidence.simulated=True` marker (excluded from fleet report by default).

---

## Twin canonical representations (per `feedback_twin_deliverable_at_every_ratification`)

- **Repo canonical (Claude-authored):**
  - PR #3331 `52cf41287` — S2857 code
  - PR `<this docs cascade>` — S2857 handoff + 00-START-NEXT refresh + docs cascade
- **Workspace canonical:** Content mirror + ratification envelope to be written by Rigby via PA tool per `feedback_rigby_writes_workspace_deliverables` at S2857 close-cascade.

---

## Session close checklist

- [x] Rigby pre-code SIGN (AGREE-TO-BUILD + Q3 mods adopted)
- [x] Code + tests (26 new + 43 pre-existing green)
- [x] Rigby post-code SIGN (Q3 nan/inf guard applied inline)
- [x] PR #3331 merged via `gh pr merge --admin` (billing gate per `feedback_gh_pr_merge_admin_until_billing_fixed`)
- [x] `make celery-recycle` post-merge (PLAYBOOK-7.4.4)
- [x] Rigby post-recycle E2E confirmed live on `52cf41287`
- [ ] Docs cascade (4-step: `build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `sync_docs_index_to_documents --embed`)
- [ ] Handoff doc (this file)
- [ ] `00-START-NEXT-SESSION.md` refresh for S2858
- [ ] Rigby writes workspace deliverables (twin: content + ratification envelope)
- [ ] Three-part Chris close summary
