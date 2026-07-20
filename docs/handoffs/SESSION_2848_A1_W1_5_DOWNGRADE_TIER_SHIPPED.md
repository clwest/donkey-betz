# Session 2848 Handoff — A1 W1.5 downgrade-tier shipped

**Session ID:** 2848
**Date:** 2026-07-20
**Session pin:** `pa-1a4d45c9a947423d` (label `s2848-a1-w15-downgrade-tier`) — RETIRES at close
**Prior session pin:** `pa-c944dd9ec7b94428` (retired at S2847 close)
**Next session:** S2849 will atomic-mint fresh pin per `feedback_session_open_atomic_mint_before_pa_dispatch`

**Merge commits in order:** `b5e7b3e98` (Phase W1.5) → `<this docs cascade PR>` (S2848 close)

---

## Executive summary

**A1 W1 SaaS substrate is now feature-complete for the PA path.** One code PR shipped (`#3311`) completing the W1.5 soft downgrade tier that S2847 Phase 3 left as forward-compat, AND back-wiring Phase 2's `enforce_workspace_freeze` (which the S2848 EIA found had no automatic caller — required Django shell to trigger since S2846).

Pre-code Rigby SIGN #1 (task `984fe4c2`) executed 4 tool-grounded verifications (`repo_tool.search` + `repo_tool.read_file` × 3) and independently confirmed the Phase 2 auto-wire gap. Delivered 5 substantive zoom-out folds; F-BLOCKING adopted verbatim before code (dropped per-workspace `downgrade_pct` override; added hysteresis; added fail-soft per-workspace loop).

Live E2E via Rigby (task `1400c384`) exercised the full new W1.5 surface end-to-end and caught one Phase 3 designed-behavior observation (set_cap is config-only; enforcement fires from periodic cycle) worth noting as a small UX friction candidate.

Working loop stayed on shape: Claude EIA → Rigby SIGN pressure-tests with tools → joint recommendation to Chris → Chris ratifies → Claude ships → Rigby E2E-verifies → Claude ORM-cross-checks. Zero rubber-stamps this session; one F-BLOCKING pushback (`downgrade_pct` disagreement) adopted verbatim; one anomaly-pause during E2E (Rigby correctly paused at STEP 2 with a design-question observation before continuing).

---

## What shipped

### PR #3311 — Phase W1.5 workspace downgrade-tier + Phase 2 back-wire (`b5e7b3e98`)

**BudgetController additions (`core/services/ops_autopilot/budget.py`):**

| Method | Purpose |
|---|---|
| `enforce_workspace_downgrade(spend, now, workspace_id)` | Set at 70% of cap, auto-clear at 60% (hysteresis). Idempotent. Writes `workspace_downgrade_set` / `workspace_downgrade_cleared` AutopilotAction rows. |
| `is_workspace_downgraded(workspace_id) → bool` | Hot-path SystemConfiguration read for llm_enforcer. |
| `clear_workspace_downgrade(workspace_id, actor_user_id=None) → bool` | Symmetric with `clear_workspace_freeze`. Writes audit row when `actor_user_id` passed (operator override). |

**SystemConfiguration key:** `workspace_downgrade_active:<uuid>`
**Hysteresis constant:** `_WORKSPACE_DOWNGRADE_CLEAR_PCT = 0.60` (Fold F2 from Rigby zoom-out)

**Periodic cycle back-wire (`_policy_budget_controller` in `core/services/ops_autopilot/core.py`):**

After the existing global tier decisions, iterates `list_workspace_caps()`:
- Zombie-safe: skips caps whose ProjectWorkspace row is missing (Fold NB2)
- Fail-soft per workspace: try/except so one bad row doesn't abort the cycle (Fold F3)
- Calls `enforce_workspace_freeze` (Phase 2 auto-wire — this is the fix for the gap) AND `enforce_workspace_downgrade` per workspace
- Result includes `{evaluated, skipped_zombie, freeze_actions, downgrade_actions, errors}`

**llm_enforcer hot-path (`core/llm_enforcer.py:242-303`):**

Adds workspace-downgrade block after workspace-freeze block. Precedence: workspace-freeze wins (freeze return-blocks before downgrade check runs). Global freeze + global downgrade retain existing precedence upstream. On active downgrade + `not use_claude`: sets `self._budget_downgrade_model = BUDGET_DOWNGRADE_MODEL` — `_call_openai` at line ~503 already swaps to it.

**workspace_budget_tool (`core/services/td_handlers_ops.py` + `core/services/pa_tool_schemas.py`):**

- **New action** `clear_downgrade` — symmetric with `clear_freeze`
- `get_status` returns `is_downgraded` + `enforcement_tier` flips from `'freeze_only'` → `'downgrade_and_freeze'`
- `list_caps` per-row `is_downgraded` field
- `set_cap` schema **unchanged** (Fold F1 — no per-workspace `downgrade_pct`)
- Schema description updated for W1.5 semantics

**AutopilotAction.ACTION_TYPES (`core/models_diagnostic_pipeline.py` + migration `0390`):**

Adds 6 workspace-scoped values (2 W1.5 + 4 Phase 2/3 backfill that were being written without registration):
- `workspace_budget_freeze` (Phase 2 auto)
- `workspace_freeze_cleared` (Phase 3 manual)
- `workspace_cap_set` (Phase 3 tool)
- `workspace_cap_cleared` (Phase 3 tool)
- `workspace_downgrade_set` (W1.5 auto)
- `workspace_downgrade_cleared` (W1.5 auto-hysteresis or manual)

Migration `0390` is choices-only (max_length unchanged at 30). Auto-generated migration was rewritten by hand to strip ~695 lines of unrelated pre-existing schema drift (Narrative models, HAI dispatch alterations, index renames) that would have accidentally shipped in this PR.

---

## Rigby SIGN cycle — working loop evidence

### SIGN #1 (pre-code, task `984fe4c2`)

**Tool-grounded verification (4 repo_tool calls executed):**
- T1: confirmed `enforce_workspace_freeze` has NO CALLERS in `core/**/*.py` (my EIA finding correct)
- T2: confirmed `_policy_budget_controller` at `core.py:1347` only uses global `compute_spend`, no `compute_workspace_spend` reference
- T3: confirmed `AutopilotAction.action_type` = CharField(max_length=30) with 12 existing choices (none workspace-scoped)
- T4: confirmed `BUDGET_SOFT_LIMIT_PCT=0.7`, `BUDGET_DOWNGRADE_MODEL='gpt-5-mini'`, `BUDGET_CRITICAL_PURPOSES` set

**Verdicts:**
- Q1: AGREE (no caller)
- Q2: AGREE Shape B lean (fix + ship together over accreting more dead-code substrate)
- Q3: AGREE precedence (workspace-freeze → workspace-downgrade → global-freeze → global-downgrade)
- **Q4: DISAGREE** (F-BLOCKING) — drop per-workspace `downgrade_pct`; global constant only. Reasoning: schema surface + test matrix + doesn't add W1.5 core value. Chris ratified.
- Q5: AGREE add `clear_downgrade` action + auto-clear via cycle (both needed)
- Q6 (non-blocking): two explicit action_types (`_set` + `_cleared`)
- Q7 (non-blocking): defensive zombie-workspace skip in loop
- Q8 zoom-out (5 concerns):
  - #1 structural alt considered + rejected (compute-inline in llm_enforcer too expensive for hot path)
  - **#2 F-adjacent: fail-soft per workspace** — adopted
  - **#3 F-adjacent: hysteresis** — adopted (set at 70%, clear at 60%)
  - #4 idempotent per-workspace enforcement — already true by design
  - #5 smallest-change validation — matches proposal

**Zero rubber-stamps.** All verdicts tool-grounded; F-BLOCKING pushback caught + adopted before Chris routing.

### E2E (post-merge, task `1400c384`)

Exercised the full W1.5 surface on Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`):

- **STEP 2 pause + observation:** Rigby correctly paused when `set_cap` didn't immediately freeze the over-cap workspace. Correct behavior — `set_cap` is Phase 3 config-only; enforcement fires from periodic cycle. Recorded as candidate UX friction (see §Deferred).
- STEP 4-6: `clear_downgrade` clears the shell-triggered downgrade flag; `is_downgraded` correctly flips T→F
- STEP 7: `list_caps` returns per-row `is_downgraded` field
- STEP 8: `clear_cap` correctly notes freeze not auto-cleared (Phase 3 designed)
- STEP 9: 6 `AutopilotAction` rows verified with correct provenance — auto (`BudgetController` / `workspace_budget_controller`) vs manual (`workspace_budget_tool` / `workspace_budget_tool`)

**Shell E2E (pre-push, Claude-executed):**
Baseline → set cap $0.10 with spend $0.80 → downgrade set (`gpt-5-mini` selected) → idempotent second call (None) → simulated spend 40% → auto-hysteresis clear → re-trigger → manual clear with `actor_user_id=1` → 4 audit rows with correct auto/manual differentiation.

---

## Memory hits + adherence

- `feedback_session_open_atomic_mint_before_pa_dispatch` — retired `pa-c944dd9ec7b94428` (12 rows updated), minted `pa-1a4d45c9a947423d`, verified wrapper before first PA dispatch
- `feedback_cycle_1a_verify_before_build` — full EIA before design draft (found the Phase 2 wiring gap that would have shipped unnoticed)
- `feedback_verify_rigby_tool_runs_before_trusting_sign` — dispatch specified T1–T4 explicit tool-grounded directives; Rigby delivered non-empty tool_runs; both AGREE and DISAGREE verdicts landed on tool evidence
- `feedback_zoom_out_ask_per_rigby_sign` — Q8 delivered 5 substantive concerns; 3 folded
- `feedback_claude_rigby_agree_first_chris_yes_no` — Q4 F-BLOCKING resolved between Claude+Rigby before Chris routing; Chris got single-recommendation yes/no
- `feedback_read_full_rigby_response_not_just_tail` — pulled full SIGN body via ORM after `tail -300` truncated Q6-Q8
- `feedback_gh_pr_merge_admin_until_billing_fixed` — used `--admin` on merge (billing still blocked)
- `feedback_recycle_after_merge` — `make recycle-all` post-merge (sha=b5e7b3e98544)
- `feedback_local_truth_no_production` — recycle + Rigby exercise IS the deploy step; no production observation window

## What's NOT shipped at S2848 close

- Live E2E of the llm_enforcer hot-path model swap (i.e. dispatch a non-critical LLM call in a downgraded workspace and observe `gpt-5.2 → gpt-5-mini` route) — the hot-path code is verified by inspection + Phase 2 test coverage; live routing swap deferred as it requires either (a) waiting for autopilot cycle to fire naturally on real spend or (b) additional shell orchestration. **The tier is live** (flag writes, hot-path reads, `_call_openai` swaps) — just not observed end-to-end in a single Rigby session.
- **Drift-lint triage** of the 69 baseline DRIFT entries beyond Phase 2's original 4 (S2848 slate item #1) — awaits explicit Chris direction
- **set_cap immediate enforcement** (candidate follow-up from Rigby E2E STEP 2 observation) — currently config-only; operator setting a tight cap on an already-over-spend workspace has to wait ~10 min for autopilot cycle to fire the flag. Small UX friction; not shipped unless Chris directs
- **Bulk workspace_budget_tool operations** (Rigby Tool Gap Ledger candidate from S2847)

---

## Twin-pointer card (repo + workspace)

**Repo:**
- `docs/handoffs/SESSION_2848_A1_W1_5_DOWNGRADE_TIER_SHIPPED.md` — this file
- `00-START-NEXT-SESSION.md` — S2849 open sequence (updated at this close)
- `core/services/ops_autopilot/budget.py:459-750` — BudgetController per-workspace freeze + downgrade (Phase 2 + W1.5)
- `core/services/ops_autopilot/core.py:1420-1510` — `_policy_budget_controller` workspace iteration back-wire
- `core/llm_enforcer.py:242-303` — workspace freeze + downgrade hot-path
- `core/services/td_handlers_ops.py:3841-4080` — workspace_budget_tool 6 actions
- `core/services/pa_tool_schemas.py:3315-3405` — workspace_budget_tool schema
- `core/models_diagnostic_pipeline.py:519-538` — AutopilotAction.ACTION_TYPES with 6 workspace values
- `core/migrations/0390_s2848_autopilotaction_workspace_action_types.py` — choices-only migration

**Workspace UI:**
- Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` — same workspace exercised at S2846–S2848
- Rigby Tool Gap Ledger deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` — no new entries this session

**Grafana / observability:** none touched at S2848.

---

## Session-close ceremony

- Merged: `#3311` (b5e7b3e98) → `<this docs cascade PR>`
- Recycled: post-merge `make recycle-all` (clean recycle, sha=b5e7b3e98544). Final recycle after docs cascade PR merge at close.
- Docs cascade: 4-step (build_docs_index → build_rag_corpus → sync_docs_index_to_documents → --embed) + build_docs_provenance run at close
- Twin workspace mirror: Rigby writes content mirror + ratification envelope via PA tool per `feedback_rigby_writes_workspace_deliverables`
- Session pin `pa-1a4d45c9a947423d` retires; S2849 atomic-mints fresh
