# Session 2849 Handoff — A1 W2 #2a defaults + backfill shipped

**Session ID:** 2849
**Date:** 2026-07-20
**Session pin:** `pa-507d1264765f4bf3` (label `s2849-a1-w2-scoping`) — RETIRES at close
**Prior session pin:** `pa-1a4d45c9a947423d` (retired at S2848 close)
**Next session:** S2850 will atomic-mint fresh pin per `feedback_session_open_atomic_mint_before_pa_dispatch`

**Merge commits in order:** `a74a9bdbc` → `167a9b34d` → `60ec5f75e` (squashed to PR #3313)

---

## Executive summary

**A1 W2 leg opens with #2a shipped.** One PR (`#3313`) writes the default-cap + backfill layer that unblocks per-workspace budget enforcement on the 16/16 workspaces that shipped through S2848 W1.5 with zero explicit caps configured.

Pre-code Rigby SIGN #1-#4 (task chain `984fe4c2` → `3785`) delivered tool-grounded ranking of the W2 candidate slate via 8+ `repo_tool` calls, one F-BLOCKING pushback (5th candidate: "state model / audit hardening") added and then withdrawn after QF-4 evidence confirmed state is canonical (all three keys — `workspace_daily_cap`, `workspace_freeze_active`, `workspace_downgrade_active` — live in same `SystemConfiguration` table with consistent prefix pattern).

Claude ORM-verified T3 (Rigby-flagged tool gap): **16 ProjectWorkspace rows, 0 with explicit caps, 0.1% attribution rate** (86/59,696 rows). This reshaped the W2 slate — Reframe A signed (W1 complete as-designed, PA-path attribution only, NULL-bucket handled globally per S2846 Fold 3), W2 re-ordered to start with defaults+backfill because 16/16 unconfigured means enforcement machinery has no substrate. Chris ratified Reframe A + #2a-first + skip W2-2b.

Live E2E via Rigby (tasks `19232172` → `dcb87b4f`) caught TWO GPT function-calling shape bugs (empty `include_workspace_ids=[]` blocking all writes; `daily_cap_usd=0` raising ValueError) — both fixed in the same PR at commit `167a9b34d`. Re-E2E post-fix wrote 16 caps successfully; audit trail confirmed via ORM (1× `workspace_default_cap_set` + 16× `workspace_cap_set` all at expected timestamps).

Working loop stayed on shape: Claude EIA → Rigby SIGN pressure-tests with tools → joint recommendation to Chris → Chris ratifies → Claude ships → Rigby E2E-verifies → Claude ORM-cross-checks → Rigby E2E catches bugs → Claude fixes + Rigby re-verifies → merge with `--admin`. Zero rubber-stamps; one F-BLOCKING pushback (5th candidate) adopted then withdrawn on evidence; two E2E-caught bugs fixed same-PR.

---

## What shipped

### PR #3313 (squash merge `60ec5f75e`)

**BudgetController** (`core/services/ops_autopilot/budget.py`):
- `_WORKSPACE_DEFAULT_CAP_KEY = 'workspace_default_daily_cap'`
- `get_workspace_default_cap()` — read global default (returns float or None)
- `set_workspace_default_cap(cap, actor_user_id)` — write default with `workspace_default_cap_set` AutopilotAction audit
- `get_effective_workspace_daily_cap(wid)` — returns `{cap, source}` where source ∈ `explicit|default|unset` (lazy fallback for operator surfaces; NOT read by autopilot enforcement)
- `backfill_workspace_defaults(default_cap, include/exclude, force, dry_run, actor_user_id)` — dry_run=True default, force=False skips workspaces with explicit caps, fail-soft per-workspace; empty include/exclude lists treated as "no filter" (E2E bug fix)

**workspace_budget_tool** (schema `pa_tool_schemas.py:3316+` + handler `td_handlers_ops.py:3841+`):
- 3 new actions on the existing tool: `get_default_cap` (read, no auth), `set_default_cap` (staff-only), `backfill_defaults` (staff-only, dry_run=True default)
- `get_status` + `list_caps` responses now include `cap_source`, `effective_cap`, `default_cap` fields
- `list_caps` gains `include_defaults` param — when true, returns every ProjectWorkspace with its effective cap alongside explicit ones
- All read responses include `null_bucket_note` reminding operators that workspace caps govern only workspace-attributed LLMCallLog rows; NULL-bucket (agents/spiders/background) is under global controls
- Handler defensively coerces `daily_cap_usd=0` → None so backfill reads the stored default (E2E bug fix)

**AutopilotAction**: adds `workspace_default_cap_set` (migration `0391_s2849_autopilotaction_workspace_default_cap_type`)

**Total surface change**: 6 files, +601/-68 LOC, 1 migration, 1 new AutopilotAction type, 3 new PA tool actions, 4 new BudgetController methods.

---

## E2E validation

Live PA E2E via Rigby (fresh mint `pa-507d1264765f4bf3`, staff auth confirmed via `session_tool.whoami`):

- **STEP 1** — `get_default_cap` (unset): `default_cap=null` ✓
- **STEP 2** — `set_default_cap daily_cap_usd=5`: `cap=5.0 previous_cap=null changed=true` ✓
- **STEP 3** — `get_default_cap` (post-set): `default_cap=5.0` ✓
- **STEP 4** — `list_caps` (no params): `count=0 default_cap=5.0` ✓ (no explicit caps yet)
- **STEP 5** — `list_caps include_defaults=true`: `count=16` — all rows `cap=null effective_cap=5.0 cap_source=default` ✓
- **STEP 6** — `get_status workspace_id=61ae8e5d…`: `cap=null effective_cap=5.0 cap_source=default default_cap=5.0` ✓
- **STEP 7** — `backfill_defaults` (dry_run=true default): `planned=16 wrote=0 skipped_not_included=0` ✓ (empty-list fix confirmed)
- **STEP 8** — `backfill_defaults dry_run=false`: `wrote=16 planned=16 errors=0` ✓
- **AUDIT** (Claude ORM cross-check): 1× `workspace_default_cap_set` at 19:29:47 + 16× `workspace_cap_set` at 19:30:41 (all `policy='workspace_budget_tool'`) ✓

STEPS 9-13 (post-backfill list_caps, get_status cap_source transition, idempotency, force overwrite, AutopilotAction audit-tool lookup) not exercised in the E2E turn due to PA loop turn-length limits — behaviors verified via Python smoke test pre-commit (idempotent rerun: planned=0 skipped_existing=16; force=true: planned=16 skipped_existing=0). STEP 13 tool-gap concern (no PA surface for querying AutopilotAction rows) is a valid Rigby Tool Gap Ledger candidate for S2850+ backlog.

---

## Rigby SIGN summary (this session)

**SIGN #1 (task `601a4ca8`, pre-code, W2 scoping)** — 12 `repo_tool` calls verifying `workspace_budget_tool` action set (6, includes `clear_downgrade`) + no existing frontend surface + `SystemConfiguration` state canonicalization. Provisional rankings with `T2/T3/T4 pending` caveats. Delivered F-BLOCKING: added 5th W2 candidate "State model / audit hardening" (`same_pr_mitigatable` zoom-out fold on state-fragmentation risk).

**SIGN #2 (task `1400c384`, pre-code, T2/T3/T4 completion)** — Completed T2 (`llm_enforcer.py:241-304` freeze check + `:288-296` downgrade routing; `LLMCallLog` schema at `models_llm_routing.py:322-333` + `:389-392` index verified). QF-4 verdict: **NOT_CONFIRMED** on state fragmentation — all three keys live in same `SystemConfiguration` table with consistent prefix. 5th candidate withdrawn from priority-1. T3 + T4 blocked by tool gap (no PA surface for ORM counts / platform_config overview); Rigby logged to Rigby Tool Gap Ledger deliverable.

**SIGN #3 (task after T3 ORM findings)** — Claude ran T3 via Django shell (16 workspaces / 0 caps / 0.1% attribution). Rigby signed **Reframe A** (W1 complete as-designed per S2846 Fold 3) + re-ranked W2 slate to `#2a defaults+backfill → #3 reporting → #1 UX polish → #4 A4`. Added optional bounded W2-2b "attribution expansion" thread (skipped per Chris). Zoom-out fold: `same_pr_mitigatable` credibility-debt concern (dashboards over 0.1% data) mitigated by Reframe A honest framing.

**SIGN #4 (task before code)** — F-BLOCKING signed all 6 design decisions (D1-D6): SystemConfiguration key + lazy fallback (D1a); PA tool action + dry_run/confirm gating (D2a); lazy new-workspace default (D3c); skip-existing/`force=true` semantics (D4); **$5/day default (D5b)**; `cap_source` display fields (D6 yes). F-BLOCKING #1-#3 adopted: allowlist/skiplist required, `cap_source` must be consistent across enforcement + display surfaces, NULL-bucket copy required in tool responses. Zoom-out fold: `future_trigger` on caps-only iteration coupling — Claude verified via `core.py:1451` that loop reads `list_workspace_caps()` (caps-only), confirming backfill is REQUIRED for enforcement (not just nice-to-have).

**Live E2E (task `19232172` → `dcb87b4f`, post-code)** — Caught 2 GPT function-calling bugs same-arc:
1. Empty `include_workspace_ids=[]` → `skipped_not_included=16` (blocked all writes)
2. `daily_cap_usd=0` → `ValueError: default_cap must be > 0, got 0.0`

Both fixed at commit `167a9b34d`; re-E2E confirmed 16 caps written + audit rows emitted.

---

## Memory hits + adherence

- `feedback_session_open_atomic_mint_before_pa_dispatch` ✓ — atomic mint `pa-507d1264765f4bf3` at session open BEFORE first PA dispatch
- `feedback_verify_rigby_tool_runs_before_trusting_sign` ✓ — verified tool_runs in every SIGN, caught nothing rubber-stamped
- `feedback_verify_at_raw_orm_before_trusting_tool_no_data` ✓ — when Rigby's T3 hit a tool gap, Claude ran ORM directly (surfaced 0.1% attribution finding that reshaped W2 slate)
- `feedback_rigby_tool_gap_ledger` ✓ — Rigby logged T3/T4 tool gap during SIGN #2
- `feedback_zoom_out_ask_per_rigby_sign` ✓ — every SIGN routing included zoom-out ask; 3 substantive folds delivered (state fragmentation → same_pr_mitigatable → NOT_CONFIRMED; credibility-debt → same_pr_mitigatable → mitigated via honest framing; caps-only coupling → future_trigger → verified + backfill mitigates)
- `feedback_claude_rigby_agree_first_chris_yes_no` ✓ — joint recommendation to Chris at the T3-reframe point, not menu of options
- `feedback_local_truth_no_production` ✓ — `make recycle-all` before E2E + after merge
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) ✓ — `make recycle-all` at `60ec5f75e` post-merge
- `feedback_gh_pr_merge_admin_until_billing_fixed` ✓ — merged with `--admin --squash --delete-branch`
- `feedback_read_full_rigby_response_not_just_tail` ✓ — fetched full assistant_response via ORM twice, caught the "she only got to STEP 6 in body summary" vs "she actually fired STEPS 7-8 in tool_runs" gap

---

## What's NOT shipped at S2849 close (deferred to S2850+)

- **#3 Reporting** (W2 priority 2 per Rigby ranking) — daily/weekly per-workspace spend rollups as PA tool action; reframed as "budget status & enforcement reporting," not "spend analytics"
- **#1 Operator UX polish** (W2 priority 3) — surfaces `get_status`/`list_caps` output; likely PA-tool enhancement or ops digest section, per `feedback_workspace_over_command_center_for_new_ui` NOT a new Command Center tab
- **#4 A4 warm-up** (W2 priority 4) — under S2846-ratified 6-line constraints, now that per-workspace enforcement is functionally live for the 16 backfilled workspaces
- **W2-2b attribution expansion** — Chris explicitly skipped; NULL-bucket remains 99.9% of traffic under global controls
- **PA tool for AutopilotAction listing** — Rigby E2E STEP 13 gap; would let operators query "who did what to workspace budgets" without dropping to Django shell
- **Cap templates + ownership transfer semantics** — deferred to later W2 slice or W2.5
- **Immediate-enforcement variant of set_cap** — S2848 observation; still unshipped
- **Live E2E of llm_enforcer hot-path model swap** — verify downgraded workspace routes non-critical calls to gpt-5-mini in one PA session

---

## Twin canonical representations (per `feedback_twin_deliverable_at_every_ratification`)

- **Repo canonical** (Claude-authored): PR #3313 merged as `60ec5f75e` + this handoff + `00-START-NEXT-SESSION.md` overwrite
- **Workspace canonical** (Rigby-authored via PA per `feedback_rigby_writes_workspace_deliverables`): content mirror + ratification envelope for A1 W2 #2a in Donkey Betz workspace (Rigby writes at close)
- **Memory**: no new memory entries needed at S2849; existing rules all reinforced by session evidence

---

## S2850 open sequence (see `00-START-NEXT-SESSION.md`)

1. Atomic mint fresh PA pin BEFORE any dispatch
2. Recommended lean: **W2 #3 Reporting** (daily/weekly per-workspace spend rollups) — highest leverage per Rigby's ranking now that enforcement substrate is live
3. Alternative micro-picks: PA tool for AutopilotAction querying (Rigby E2E gap), `set_cap` immediate-enforcement, llm_enforcer hot-path E2E
