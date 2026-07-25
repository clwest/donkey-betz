# SESSION 2967 — Slice 7 Tool-Gap Fixes: `workspace_tool.update` + `claude_code_tool` auto-resolve-repo

**HEAD:** `acfea6972` (PR #3576 merged)
**Branch shape:** feat/s2967-slice7-tool-gap-fixes → main
**PR count:** 1 code PR (#3576) + 1 close cascade PR (TBD)
**Ratified path deviation:** S2967 first-action was Path A (nightly beat + drift dashboard) per S2966 flow-test addendum. Chris ratified a mid-session re-slate to Slice 7 tool-gap sweep after S2967 open surfaced that Rigby had dispatched a Claude Code task that reported "no repo detected" and no-op'd. Path A moves to S2968 first-action.

---

## What shipped

**PR #3576** — `feat(s2967): Slice 7 tool-gap fixes — workspace_tool.update + claude_code_tool auto-resolve-repo` (+256/-33 across 5 files).

### Fix 1 — `workspace_tool.update` (Ledger #22 discharge)

New `update` action on `workspace_tool`:

| Field | Behavior |
|---|---|
| `workspace_id` | required — identifies the target row |
| `root_path` | validated for on-disk existence before persist (prevents the exact regression that triggered Ledger #22) |
| `new_name` | maps to `name` on the model (the payload's `name` key is reserved for lookup on other actions — pragmatic-awkward per Rigby T1 SIGN) |
| `description` | direct mutation |
| `workspace_type` | direct mutation |
| `business_status` | routes to related `WorkspaceConfig.status` — echoes `config_update_applied: bool` in response |

Response envelope returns `{updates: {...}, old_values: {...}}` for audit trail. User-scoped filter matches other workspace actions (caller-owned workspaces only).

**A2 SIGN bug fix caught mid-flight:** Rigby's initial A2 dispatch cleared `business_status` from `'active'` to `''` because the PA function-calling layer serializes missing string keys as `""` (not `None`). My original guard `if business_status is not None` treated absent-in-payload as intentional-clear. Fixed to require truthy value; same defence-in-depth pattern already used on the main `updates` dict. Regression re-verified: `workspace_tool.update` with ONLY `description` payload left `business_status` untouched.

### Fix 2 — `claude_code_tool` auto-resolve-repo (S2967-open regression)

**Root cause:** `REPO_ROOT = '/app'` was hardcoded at `core/services/claude_code_engineer.py:294` for Railway containers. On local dev `/app` doesn't exist; `_ensure_git_repo()` falls back to that read-only nonexistent path when `GITHUB_TOKEN` env var is unset. Result: every local claude_code dispatch reports "no repo detected in environment" and no-op's.

**Fix design (three-hop explicit dependency injection — Rigby T1 SIGN REVISE #1 pushback against module-global mutation):**

1. `claude_code_tool` schema accepts optional `workspace_id`.
2. `_handle_claude_code` (`td_handlers_codejobs.py:330`) resolves `workspace_id → ProjectWorkspace.root_path` with a four-priority chain: **explicit** → **active_workspace** (is_active=True, tie-broken by most recent `last_operation_at`) → **fallback**. Response envelope echoes `workspace_id_resolved` + `workspace_root_path` + `resolved_from` per Rigby T1 SIGN REVISE #2 ("no magic defaults — annotate loudly").
3. `claude_code_engineer_task` accepts `workspace_root_path` kwarg, passes through.
4. `execute_engineering_task` resolves `repo_root` via new `_resolve_repo_root()` helper and threads `repo_root` into every `_execute_tool` call.

**Concurrency safety:** `_ensure_git_repo()` refactored to **return** the resolved path instead of mutating module-level `REPO_ROOT` global. `_execute_tool(tool_name, tool_input, repo_root)` accepts per-dispatch `repo_root` param. `REPO_ROOT` stays as an inert fallback constant. Under prefork pool concurrency (Railway), each `execute_engineering_task` run threads its own `repo_root` independently — no global-clobber race.

**Fallback preserved:** If `workspace_root_path` is None (Railway prod path where dispatcher didn't resolve), `_resolve_repo_root()` falls back to the existing `_ensure_git_repo()` /tmp-clone flow. Zero behavior change on Railway.

### Cut from this batch

Fix 3 (auto-bind conversation_id at framework level) was pre-considered and cut in Rigby T1 SIGN. The existing S2728 F-CC-3 `follow_up_will_fire` echo already tells callers when to poll `execution_history_tool` / call `schedule_followup`. Root-cause investigation of why `self._conversation_id` can be empty in fresh PA conversations = separate arc.

---

## Governance chain

**Chris D-verdict (mid-session re-slate to Slice 7):** ratified after joint Claude+Rigby recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`. Plain-English framing per `feedback_plain_english_decision_framing_for_chris` — "do we lose anything?" (no — Path A observation is nice-to-have, gap-fixes unblock actual work) + "is it more work later?" (no — both downstream arcs get cheaper with the tool gaps fixed).

**Rigby T1 pre-code SIGN:**
- Tool-verified via `repo_tool.read_file` × 4 (schema anchor + handler insertion point + REPO_ROOT hardcoding + auto-inject fallback) + `deliverable_tool.append` × 1 (Ledger #22).
- 2 REVISEs surfaced via mandatory open-ended zoom-out ask (per `feedback_zoom_out_ask_per_rigby_sign`) — both accepted pre-code:
  1. Global REPO_ROOT is a latent concurrency bomb → refactor to explicit DI.
  2. Magic-default to Donkey Betz UUID is too convenient → annotate loudly with `resolved_from` echo.
- Fix 3 cut agreement + `new_name` accepted as pragmatic-awkward.

**Rigby A2 post-code SIGN:**
- Tool-verified via `workspace_tool` × 2 + `claude_code_tool` × 1 + `agent_job_status` × 1.
- One real bug caught mid-verify (empty-string business_status regression). Patched + re-verified before AGREE.
- Full end-to-end round-trip: claude_code_tool dispatch with `workspace_id=b4503364-…` returned `resolved_from='explicit'` + `workspace_root_path=/Users/donkeyking/Donkey_Betz/unified-donkey-betz` + `follow_up_will_fire=true`. Task `46260f53-ffac-438f-9780-02cd257217ee` completed with the correct single filename from `/docs/governance/` (`SYSTEM_OWNER.md`) — proving the engineer ran against the real working tree, not the `/app` fallback that produces the "no repo detected" no-op.

**Post-merge:** `make recycle-all` executed per PLAYBOOK-7.4.4 (workers advanced to sha=`acfea6972cd9`).

---

## Rigby Tool Gap Ledger

- **Ledger #22 — `workspace_tool` no update action → DISCHARGED at S2967.** Ratified S2967 open (2026-07-25), fix shipped same session, tool-verified twice via Rigby A2 SIGN. Ledger entry appended to deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`).
- **Ledger #17 — Chat UI response-relay gap — no change** (Chris terminal path continues; 11 consecutive terminal ratifications S2957→S2967).
- **Ledger #19 — SIA allowlist — no change** (still discharged at S2964).
- **Ledger #20 — `ToolCallRecord.trace_id` NULL on 100% of rows — no change**.
- **Ledger #21 — PA→ToolCallRecord write silent regression — no change**.
- **New candidate:** `claude_code_tool` auto-bind conversation_id at framework level (Fix 3 cut from S2967) — deferred to future investigation; not urgent because `follow_up_will_fire` echo gives callers observability.

---

## Pre-existing state note

**4 ProjectWorkspace rows** had stale `/Users/donkeyking/development/unified-donkey-betz` prefix root_paths (Donkey Betz `b4503364-…`, System Autonomous `1f0d467e-…`, chris-personal `33aa1e08-…`, s2798_onboarding_test `61ae8e5d-…`) — Chris moved the working tree to `/Users/donkeyking/Donkey_Betz/unified-donkey-betz` without updating the ProjectWorkspace rows. Fixed via ORM at S2967 open (before shipping the tool-gap fix that would have enabled Rigby to self-serve the same repair). All 4 rows now on the correct prefix; verified via `workspace_tool.list`.

---

## S2968 first-action

**Path A — nightly beat + pass-rate drift dashboard.** Original S2967 first-action per S2966 flow-test addendum. Deferred one session by the Slice 7 mid-session re-slate; no re-scoping required.

Ship a Celery beat task that runs `run_golden_evals --execute` across all 8 slices on a schedule + a UI/API to surface pass-rate trends per-slice / per-prompt / per-substrate. Uses `GoldenEvalRun` rows already persisting (112 as of S2966 close + additions from S2967 A2 SIGN dispatches).

**Also carry forward as S2968 candidates:**
- Per-slice named predicate graduation (S2967 Path B candidate).
- Ledger #20 + #21 fix arc (S2967 Path C candidate).
- Rigby outbound-messaging gap (2 triggers observed S2965/S2966; log to ledger at S2968).

---

## Deferred queue (updated at S2967 close)

Additions:
- **Claude Code auto-bind conversation_id at framework level** — Fix 3 cut from S2967; separate arc.
- **Path B (per-slice predicate graduation)** — carried forward from S2966 deferred; still a valid S2968 candidate.
- **Path C (Ledger #20 + #21 fix arc)** — carried forward from S2966 deferred; unblocks Rigby fabrication predicates.

Carried unchanged (long-standing):
- Docs restructuring arc (Chris-ratified S2800).
- Slice 5-hardening executable invariants.
- Tier 2 lint promotion.
- Advanced paste-UUID fallback for cluster picker.
- Server-side search + pagination on `/eligible/`.
- Z1/Z2/Z4 signal-dispatch UI polish.
- Rank + cap + paginate follow-ups.
- Per-pattern-type diversity floors.
- Ledger candidates backlog.
- W2 #1 / #2b / #2c pending Chris re-slate.
- LLMCallLog field splits.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os follow-ons.

---

## Live verify checklist for S2968 open

1. `bash tools/pa_local.sh "workspace_tool action=list"` — confirm all 4 formerly-stale workspaces show `/Users/donkeyking/Donkey_Betz/unified-donkey-betz` prefix.
2. `bash tools/pa_local.sh "claude_code_tool task='ANSWER MODE: echo the current git HEAD SHA from the repo root' workspace_id=b4503364-2573-4401-9e28-61a739e0ce50 conversation_id=<S2968 pin>"` — smoke test auto-resolve-repo + follow-up wake.
3. `grep "^python tools/pa_chat.py" tools/pa_local.sh` — confirm the S2968 pin (retired at S2967 close cascade).

---

## Session close summary (three-part per feedback rule)

**1. What was done:**
Slice 7 tool-gap sweep: two workspace/Claude Code fixes shipped in one PR (#3576, HEAD `acfea6972`, +256/-33). New `workspace_tool.update` action + `claude_code_tool` now auto-resolves the working tree from an explicit `workspace_id` (or the active workspace) instead of hardcoded `/app`.

**2. How it improves the platform:**
- Before: any repo relocation or workspace attribute drift required raw ORM (as Chris just experienced with the `/Users/donkeyking/development/...` → `/Users/donkeyking/Donkey_Betz/...` move). Now Rigby can self-serve the correction via `workspace_tool action=update`.
- Before: every local-dev `claude_code_tool` dispatch reported "no repo detected" and no-op'd (as observed at S2967 open with Rigby's `3a381a71-…` dispatch). Now the engineer runs against the actual working tree — real files, real changes, real PRs.
- Both fixes are customer-facing product surface (A1 SaaS): every gap Rigby hits, a customer would hit.

**3. Exact next-session first action:**
S2968 opens with Path A — nightly beat task running `run_golden_evals --execute` across all 8 Golden Evals slices + a pass-rate drift dashboard. Per S2963 arc structure. Uses the harness shipped S2964→S2966. Original S2967 first-action, deferred one session by the mid-session gap-fix re-slate.
