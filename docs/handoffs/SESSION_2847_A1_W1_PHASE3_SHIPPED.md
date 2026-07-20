# Session 2847 Handoff — A1 W1 Phase 3 shipped

**Session ID:** 2847
**Date:** 2026-07-20
**Session pin:** `pa-c944dd9ec7b94428` (label `s2846-close-mint-s2847`) — RETIRES at close
**Prior session pin:** `pa-5eec7b14a3a5482b` (retired at S2846 close)
**Next session:** S2848 will atomic-mint fresh pin per `feedback_session_open_atomic_mint_before_pa_dispatch`

**Merge commits in order:** `5ccd3ca26` (Phase 3) → `<this docs cascade PR>` (S2847 close)

---

## Executive summary

One code PR shipped: `workspace_budget_tool` — PA-manageable per-workspace budget cap + freeze management. Completes the A1 W1 SaaS substrate for the PA path (attribution → enforcement → operator surface). Only W1.5 downgrade-tier remains as A1 W1's ratified follow-on before this substrate is feature-complete for A1 W2 scope.

Pre-code Rigby SIGN cycle produced 5 zoom-out folds (tool-grounded verification, not a rubber-stamp) — all F-BLOCKING adopted before ship. Live E2E exercised all 5 tool actions + all 3 mutation audit paths; caught 2 bugs mid-cycle (UUID JSON serialization + `action_type` CharField overflow), fixed in-branch, re-verified.

Working loop stayed on shape: Claude proposes → Rigby SIGN pressure-tests with tools → joint recommendation to Chris → Chris ratifies → Claude ships → Rigby E2E-verifies → Claude ORM-cross-checks Rigby's tool_runs. Zero rubber-stamps this session; one F-BLOCKING pushback (`clear_cap` symmetric undo + auth + audit trail) adopted verbatim.

---

## What shipped

### PR #3309 — Phase 3 workspace_budget_tool (`5ccd3ca26`)

**New tool: `workspace_budget_tool`** (5 actions, all drift-lint CLEAN):

- `set_cap(workspace_id, daily_cap_usd)` — writes `SystemConfiguration key='workspace_daily_cap:<uuid>'`; idempotent; response warns when workspace is currently frozen and the new cap now exceeds 24h spend
- `get_status(workspace_id)` — cap + `daily_total`/`hourly_total`/calls + `is_frozen` + `enforcement_tier` + `window_note`, joined with `ProjectWorkspace.name`
- `clear_freeze(workspace_id)` — delegates to `BudgetController.clear_workspace_freeze` with `actor_user_id` for audit
- `list_caps()` — inventory joined with `ProjectWorkspace.name` for operator readability; enriches each row with current 24h spend + freeze status
- `clear_cap(workspace_id)` — deletes the cap; explicitly does NOT clear an existing freeze (two independently auditable operations)

**BudgetController extensions** (symmetric with the S2846 get/enforce/is/clear methods at `core/services/ops_autopilot/budget.py`):

- `set_workspace_daily_cap(workspace_id, daily_cap_usd, actor_user_id=None) -> dict` — idempotent; returns `{workspace_id, cap, previous_cap, changed}`; raises `ValueError` on cap ≤ 0
- `clear_workspace_daily_cap(workspace_id, actor_user_id=None) -> bool` — symmetric undo
- `list_workspace_caps() -> list` — raw rows for handler enrichment; skips non-float values with WARN log
- `clear_workspace_freeze` — added optional `actor_user_id` kwarg (backward-compat); records AutopilotAction on manual clear

**Handler:** `_handle_workspace_budget` on `OpsHandlersMixin` at `core/services/td_handlers_ops.py:3841`. Register line at `core/services/tool_dispatcher.py:522`. Handler count: 156 → 158.

**Schema:** `pa_tool_schemas.py:3316` — 79-line entry inserted before `governance_tool`. Description explicitly notes "daily = last 24h sliding window (not calendar day)" and that mutations require workspace owner OR staff.

**Hardening folds** (Rigby SIGN #1 zoom-out, ratified pre-code):

1. **Auth** — mutations validate workspace exists AND require `request.user.id == workspace.user_id` OR `is_staff`. Reads unrestricted beyond `is_authenticated`. Rationale: this tool surface IS the A1 SaaS product surface — pre-A1 hardening now saves later.

2. **Mutation audit** — set_cap / clear_cap / clear_freeze emit `AutopilotAction(policy='workspace_budget_tool')` rows with `actor_user_id` in evidence + `previous_cap` where relevant. Symmetric with existing `enforce_workspace_freeze` audit. Idempotent no-ops (changed=false) skip the row.

3. **enforcement_tier** — get_status + list_caps return `'freeze_only'` today; grows to `'freeze_and_downgrade'` when W1.5 lands without schema break.

4. **Timebox note** — every response includes `window_note` clarifying "daily = last 24h sliding window (not calendar day)".

5. **Set-under-freeze warning** — set_cap response warns when workspace is frozen and new cap now exceeds 24h spend (operator should call clear_freeze to resume).

**Bugs caught during E2E + fixed in-branch:**

- **UUID JSON serialization** — `evidence={'actor_user_id': user_id}` failed because Chris's user_id is a UUID (`AbstractUser` PK); Django JSONField can't serialize UUID natively. Fixed with `str(actor_user_id)` in all 3 audit dicts.
- **`action_type` length** — initial name `'workspace_freeze_cleared_manual'` was 31 chars; `AutopilotAction.action_type` is `CharField(max_length=30)`. Renamed to `'workspace_freeze_cleared'` (24 chars). Note: choice-list constraint not enforced by `.objects.create()` — same precedent used by S2846's `'workspace_budget_freeze'` action_type.

**Live E2E verified against real Donkey Betz workspace** (`b4503364-2573-4401-9e28-61a739e0ce50`):
- Empty state → set_cap $1.50 → verify persisted → get_status shape → set_cap $2.75 (changed=true, previous_cap=1.5) → clear_cap → list_caps empty
- Frozen path: manual cap=$0.10 + enforce → get_status shows `is_frozen=true` → set_cap $5.00 returns freeze warning → clear_freeze cleared=true + audit row written

**Post-merge sanity check:** `workspace_budget_tool action='list_caps'` dispatched via Rigby after `make recycle-all` — returns clean state, tool reachable at HEAD `5ccd3ca267cf`.

---

## Working loop artifacts

**Rigby SIGN cycle (pre-code):**
- Q1-Q5: AGREE on Claude's proposed design (separate tool, `clear_cap` 5th action, `daily_cap_usd` naming, keep set_cap/clear_freeze independent, minimal get_status shape)
- Q6: REFINE — add `workspace_name` via ProjectWorkspace join for operator usability
- Q7 zoom-out: 5 concerns (auth F-BLOCKING; mutation audit F-BLOCKING; enforcement_tier forward-compat; timebox semantics; bulk ops deferred)

Tool-grounded via 6 `repo_tool` reads (BudgetController API grep, budget.py extract of methods 470-720, OpsHandlersMixin location) before authoring the response. Not a rubber-stamp — one AGREE + one REFINE + five substantive zoom-out concerns.

**Chris D-verdict:** "proceed with phase 3" (session open) — treated as scope-yes; joint scope refinement (5 folds) presented to Chris post-SIGN; adopted implicitly by proceeding to code without veto.

---

## Not shipped at S2847 close (deferred to S2848)

- **W1.5 downgrade-tier** — soft-threshold routing to cheaper model before hard freeze. Mirrors Phase 2 pattern:
  - `BudgetController.enforce_workspace_downgrade(spend, now, workspace_id)` — sets `workspace_downgrade_active:<uuid>` flag when spend crosses soft threshold (proposed: 70% of cap, mirroring global `BUDGET_SOFT_LIMIT_PCT`)
  - `BudgetController.is_workspace_downgraded(workspace_id)` — hot-path check for `llm_enforcer`
  - `BudgetController.clear_workspace_downgrade(workspace_id, actor_user_id=None)` — symmetric with clear_workspace_freeze
  - `llm_enforcer._call_openai` extension — when workspace is downgraded, route to `AutopilotConfig.BUDGET_DOWNGRADE_MODEL` instead of the requested model
  - `workspace_budget_tool.get_status.enforcement_tier` — flips from `'freeze_only'` to `'freeze_and_downgrade'` when downgrade is enabled
  - Optionally: expose downgrade threshold via tool (new action or extend set_cap with `downgrade_pct` param)
  - Estimated ~half day; one PR; drift-lint should stay CLEAN

- **Drift-lint triage of 69 DRIFT entries** — Rigby's S2846 SIGN bucketed a handful (REAL_BUG / SUB_HANDLER_FP / ALIAS_TOLERANT) but only 4/10 sampled were tool-verified before her timebox. Tight ~2-3 day arc could fix top 10-15 REAL_BUG entries. Priority depends on Chris interest signal at S2848 open.

- **Bulk workspace_budget_tool operations** — Rigby Q7 fold #5. Not needed for single-workspace today; schema left extensible. Add to Rigby Tool Gap Ledger as future candidate for A1 W2+ when multi-workspace tenants exist.

- **`workspace_budget_tool` schema-value polish** — action_type constants (`'workspace_cap_set'`, `'workspace_cap_cleared'`, `'workspace_freeze_cleared'`) are not in `AutopilotAction.ACTION_TYPES` choices list. Same precedent as `'workspace_budget_freeze'` from S2846. Low-priority cleanup to add all 4 to the choices tuple in a docs+choices cascade PR; forensic-visibility not impacted (rows write fine, choices are only enforced at form-validation).

---

## D6 moratorium (still in force)

- No new strategic discovery arcs
- No new opportunity portfolio expansions
- No new evaluation frameworks
- No layer-boundary design arcs
- No re-opening the D4 wedge frame or picks

**A4 warm-up operating constraints from S2846 still in force** (6-line block — see `00-START-NEXT-SESSION.md` Step 3).

---

## Session-open pattern for S2848

Per `feedback_session_open_atomic_mint_before_pa_dispatch`:

```bash
python manage.py session_lifecycle close --label s2848-<first-action-context>
# e.g. s2848-a1-w15-downgrade-tier
grep "^python tools/pa_chat.py" tools/pa_local.sh   # verify wrapper points to new pin
```

Then dispatch to Rigby.

**Recommended lean:** W1.5 downgrade-tier (Option B from S2847 slate). Direct extension of the Phase 3 work I just shipped — enforcement_tier field is already forward-compat and will grow to `'freeze_and_downgrade'` automatically when the flag is honored.

---

## Memory (Claude-authored)

No new memory entries needed at S2847 close. Existing rules exercised:
- `feedback_session_open_with_orient` — orient auto-fired at open
- `feedback_session_open_atomic_mint_before_pa_dispatch` — atomic mint at open (Step 1)
- `feedback_cycle_1a_verify_before_build` — verify-before-build substrate mapping before writing code
- `feedback_claude_directs_rigby_then_verifies` — SIGN routed to Rigby before coding + ORM verification of tool_runs
- `feedback_verify_rigby_tool_runs_before_trusting_sign` — verified Rigby's 6 `repo_tool` reads before treating SIGN as substantive
- `feedback_zoom_out_ask_per_rigby_sign` — Q7 explicit zoom-out ask produced 5 substantive folds
- `feedback_claude_rigby_agree_first_chris_yes_no` — joint recommendation presented to Chris (not menu); implicit-adopt on proceed
- `feedback_local_truth_no_production` — local pass = shipped; `make celery-recycle` at every code change
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — `make recycle-all` after PR #3309 merge
- `feedback_gh_pr_merge_admin_until_billing_fixed` — `--admin` flag on merge
- `feedback_read_full_rigby_response_not_just_tail` — re-fetched Rigby's Q6-Q7 body when initial tail truncated it

---

## Runtime impact

- 158 tool handlers registered (up from 156 pre-Phase-3)
- 5 new AutopilotAction rows written during E2E (2× workspace_cap_set + 2× workspace_cap_cleared + 1× workspace_freeze_cleared) — all with `actor_user_id` in evidence
- SystemConfiguration `workspace_daily_cap:*` + `workspace_freeze_active:*` prefix key surface unchanged (existing S2846 shape); tool now manages these rows first-class
- Zero code migration required (only SystemConfiguration rows, which are runtime-managed)

---

## Files touched

| File | Δ | Purpose |
|---|---|---|
| `core/services/ops_autopilot/budget.py` | +151 | set/clear_workspace_daily_cap + list_workspace_caps + audit hook on clear_workspace_freeze |
| `core/services/pa_tool_schemas.py` | +79 | workspace_budget_tool schema |
| `core/services/td_handlers_ops.py` | +206 | _handle_workspace_budget on OpsHandlersMixin |
| `core/services/tool_dispatcher.py` | +3 | register("workspace_budget_tool", ...) |
| `tools/pa_local.sh` | +2/-1 | session pin rotation from S2847 open atomic mint |
