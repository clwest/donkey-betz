# Session 2846 Handoff — A1 W1 Phase 1 + Phase 2 shipped

**Session ID:** 2846
**Date:** 2026-07-20
**Session pin:** `pa-5eec7b14a3a5482b` (label `s2846-drift-lint`) — RETIRES at close
**Prior session pin:** `pa-e0053042f1ad40ca` (retired at S2845 close)
**Next session:** S2847 will atomic-mint fresh pin per `feedback_session_open_atomic_mint_before_pa_dispatch`

**Merge commits in order:** `81cde1d37` → `6c350a19b` → `7ee53e206` → `d6bdfe6cb` → `d8ccd56d4`

---

## Executive summary

Five PRs shipped in a single working session. A4↔A1 sequencing ratified (Chris D-verdict option (a)); A1 Week 1 SaaS product substrate now demonstrably ships end-to-end for the PA path with workspace attribution + per-workspace cap enforcement.

Working loop validated across four Rigby SIGN cycles — two rubber-stamps caught + re-fired with tool-grounded directives, one lint blind spot caught by Rigby's counter-verification, one Rigby counter-claim refuted by Claude's own source verification. This is the working shape of `feedback_verify_rigby_tool_runs_before_trusting_sign` + `feedback_claude_directs_rigby_then_verifies` operating together.

---

## What shipped

### PR #3303 — Drift-lint (`81cde1d37`)

`python manage.py check_pa_tool_drift` — static AST analysis of every `PA_TOOL_SCHEMAS` entry against its registered `ToolDispatcher` handler. Reports:
- `HANDLER_ONLY_PARAM` — handler reads payload key schema hides (S2844 class of bug)
- `SCHEMA_ONLY_PARAM` — schema declares param no handler reads
- `HANDLER_ONLY_ACTION` — handler branches on action not in enum
- `SCHEMA_ONLY_ACTION` — enum lists action no handler branch handles
- `MISSING_HANDLER` — schema present, no handler registered
- `SOURCE_UNAVAILABLE` — handler source not readable

First-run scan: **114 tools · 69 DRIFT · 43 CLEAN · 1 MISSING_HANDLER (`run_agent`) · 1 SOURCE_UNAVAILABLE (`research_and_create_tool`)**.

Proof-of-concept: `intelligence_tool` no longer flags `source_spider` after S2845's fix — the class of bug that caused S2844 misdiagnosis is now caught by this lint before ship.

**Lint self-improvement:** Rigby's tool-grounded verification caught a real blind spot on `active_repo_tool` — handler reads `repo` via `(payload or {}).get("repo")` at `td_handlers_core.py:126`, which the initial visitor missed. Fixed in-branch by adding `_unwrap` for `BoolOp`/`IfExp` defensive idioms.

### PR #3304 — A4↔A1 sequencing RATIFIED (`6c350a19b`)

Chris D-verdict = **option (a)** — accept all 4 zoom-out folds from Rigby's SIGN #1 AND codify her 6-line "A4 Warm-up Operating Constraints" block as slate discipline (no renegotiation midstream).

Sequential A1-first + A4 pipeline warm-up parallel; full A4 engagement packaging BLOCKED until A1 W1 substrate demonstrably ships.

**Constraints block (Rigby-authored, S2846-ratified):**

1. Spend lane — separate budget lane; no contention with A1 shipping spend
2. Evidence tag — A4 artifacts "discovery-quality, not truth" until drift-lint (✓ shipped) + A1 workspace attribution exist (✓ shipped)
3. No capability claims — zero claims about per-workspace caps/reporting/invoicing/audit trails until A1 W1 ships (✓ enforcement in place; no PA tool exposure yet)
4. Pilot framing only — pilot/early-access/concierge language; no "productized offering" during parallel period
5. Hard throttle — fixed timebox + fixed send count (3–5 total intros)
6. No bespoke follow-ups — one standard reply + optional meeting link only

### PR #3305 — Docs cascade (`7ee53e206`)

Regenerated `docs/INDEX.md` against post-#3304 state. 40,256 chunks / 3,282 files; 2 docs updated in DB; 0 unembedded.

### PR #3306 — A1 W1 Phase 1 (`d6bdfe6cb`)

**Model + migration:**
- `LLMCallLog.workspace = FK(ProjectWorkspace, SET_NULL, nullable, related_name='llm_calls')` at `core/models_llm_routing.py:302`
- Composite index `(workspace, -created_at)` — BudgetController hot path
- Migration `0389_llmcalllog_workspace_fk_s2846.py` — targeted single `AddField + AddIndex` (deliberately excludes unrelated pending changes `makemigrations` flagged for Narrative*/HaiDispatchLog)

**Threading (write sites):**
- `core/llm_enforcer.py:709` — `_save_cost_tracking` gains `user: Optional[Any] = None` kwarg; resolves workspace via `workspace_resolver.get_active_workspace` when user provided
- `core/llm_enforcer.py:151` — `enforce_real_ai` gains `user` kwarg, threads to `_save_cost_tracking`
- `core/services/agent_llm_router.py:467` — `_log_call` adds workspace resolution + passes workspace to `LLMCallLog.objects.create`
- `core/services/unified_pa_entrypoint.py:844` — `_pa_wrapped_enforce_real_ai` auto-injects `self.user` via `setdefault` — covers 8 PA-path call sites without individual updates
- `core/services/embedding_service.py` — intentionally unchanged; embedding jobs are system-level; workspace stays NULL for W1 scope

**Fold 1 guardrail (multi-workspace ambiguity):**
- `core/services/workspace_resolver.py:56` — `get_active_workspace` now WARN-logs when `is_active=True` filter misses and "first workspace" fallback is used

**E2E verified live (post-recycle):**
```
Latest LLMCallLog row:
  agent_name: PersonalAssistant
  provider/model: openai/gpt-5.2
  user: chris
  workspace: Donkey Betz [ACTIVE] (b4503364-2573-4401-9e28-61a739e0ce50)
  cost: $0.084810

Recent 5 rows attribution:
  PersonalAssistant       workspace=Donkey Betz    (PA path)
  SpiderSemanticSearch    workspace=NULL           (system task)
  InterviewAssistant      workspace=NULL × 3       (system tasks)
```

### PR #3307 — A1 W1 Phase 2 (`d8ccd56d4`)

**BudgetController additions (`core/services/ops_autopilot/budget.py:521-616`):**

| Method | Purpose |
|---|---|
| `compute_workspace_spend(now, workspace_id=None)` | Per-workspace OR null-bucket spend from LLMCallLog |
| `get_workspace_daily_cap(workspace_id) -> Optional[float]` | Lookup at key `workspace_daily_cap:<uuid>` |
| `enforce_workspace_freeze(spend, now, workspace_id)` | Freeze when daily spend crosses cap; idempotent; records `AutopilotAction` |
| `is_workspace_frozen(workspace_id) -> bool` | Hot-path SystemConfiguration read |
| `clear_workspace_freeze(workspace_id) -> bool` | Removes freeze flag |

**Fold 2 (cap-keying policy):** documented inline in `budget.py` module-level comment — caps keyed by `workspace_id`, NOT owner. Decouples billing from user identity.

**Fold 3 (null-bucket handling):** `compute_workspace_spend(workspace_id=None)` reports system-task bucket separately; `enforce_workspace_freeze` returns None for null bucket (global freeze is the mechanism).

**Fold 4 (no caching in W1):** every `is_workspace_frozen` hits SystemConfiguration. Revisit at scale.

**llm_enforcer freeze hook (`core/llm_enforcer.py:242-283`):**
Mirrors the existing global freeze block. When `user` provided to `enforce_real_ai`, resolves active workspace, checks `is_workspace_frozen`. Non-critical calls return `{success: False, error: 'Workspace budget freeze active', blocked_by_workspace_budget: True, workspace_id: <uuid>, response: '[BLOCKED: Workspace <name> budget freeze active — non-critical calls paused]'}`. Critical purposes (`governance`/`auth`/`incident_response`/`pa_chat`) + agents (`PersonalAssistant`) bypass, same allowlist as global.

**E2E verified live:**
```
BudgetController shell test:
  compute_workspace_spend(Donkey Betz): $0.0848 / 1 call
  compute_workspace_spend(None):        $12.6594 / 1735 calls (null bucket = system tasks)
  get_workspace_daily_cap: None → $0.01 after test cap set
  enforce_workspace_freeze: {type: workspace_budget_freeze, cap: 0.01, spend: 0.0848}
  is_workspace_frozen: True → False after clear
  Re-enforce returns None (idempotent)

llm_enforcer runtime hook test:
  TestAgent/general + frozen workspace:
    success=False, error='Workspace budget freeze active',
    blocked_by_workspace_budget=True, workspace_id=<uuid>
  PersonalAssistant/pa_chat + frozen workspace:
    success=True — critical bypass, real LLM call fired ($0.003293)
```

---

## Rigby SIGN cycles — working loop evidence

### SIGN #1 (A4↔A1 sequencing, task `cc8892a0`)
Tool-grounded verification via `LLMCallLog.workspace` FK absence check + `BudgetController.compute_spend` signature read. AGREE with sequential A1-first + refined constraint. Zoom-out delivered 4 substantive folds. Non-trivial.

### SIGN #2 (drift-lint triage, task `5093658f`)
**Empty tool_runs — rubber-stamp.** Bucketing framework A/B/C1/C2/D/E/F useful as rubric but at least one specific claim (`content_tool` mismapping) refuted by Claude source verification.

### SIGN #3 (drift-lint triage re-fire with tool-grounded directive, task `4f5fb9b0`)
`repo_tool.search` × 3 executed. AGREE on F-BLOCKING (a)/(b)/(c). Verified 4 of 10 sample tools; UNVERIFIED 6/10 (Rigby's `repo_tool` timebox couldn't locate `_handle_<tool>` bodies for deliverable/governor/mission_verdict/rigby_shift_brief/messaging/claude_code within her budget).

**Rigby's counter-claims (Claude re-verified against source):**
- `active_repo_tool sp:["repo"]`: Rigby said handler DOES read `repo`. Claude source-checked `td_handlers_core.py:126` — `repo = (payload or {}).get("repo")`. **Rigby was right; lint had a real blind spot.** Fixed in-branch.
- `autopilot_tool hp:[6 params]`: Rigby said handler "only reads action, limit, dry_run." Claude grep-verified `_handle_autopilot` at `td_handlers_ops.py:2036-3840` (1800 lines) reads all 6 flagged params (channel/hours/offers/outcome/summary/title). **Rigby was wrong; lint was correct.** She read only the function head, not the dispatch body.

### SIGN #4 (A1 W1 EIA, task `347c09f0`)
Tool-grounded verification via 3 `repo_tool.search` calls. AGREE on F-BLOCKING (a)/(b)/(c) — write-site count exhaustive (exactly 3 non-test), `workspace_resolver` circular-import safe, `BudgetController.compute_spend` has no existing workspace filter. AGREE on D1-D6 with 2 tactical tweaks (D5 pass object not id string; D6 freeze-only for W1). Zoom-out delivered 4 new failure-mode folds (multi-workspace ambiguity / workspace reassignment / workspace deletion / cache-across-scopes).

### SIGN #5 (constraints block authoring, task `09f74e7f`)
Authoring, not verification. Empty tool_runs acceptable per Claude's dispatch instruction. Delivered the 6-line block verbatim.

---

## What's NOT shipped at S2846 close

- **Phase 3: PA tool exposure for workspace budget management.** Cap set/clear/status is Django-shell-only today. First S2847 candidate.
- **W1.5 downgrade-tier for workspaces.** Phase 2 shipped freeze-tier only per Rigby's D6 tweak.
- **Drift-lint triage beyond the 4 Rigby sampled.** 65 DRIFT entries un-bucketed; scope for a separate arc if Chris directs.

---

## Twin-pointer card (repo + workspace)

**Repo:**
- `00-START-NEXT-SESSION.md` — S2847 open sequence + A4 constraints (still in force) + candidate slate
- `docs/handoffs/SESSION_2846_A1_W1_PHASE1_PHASE2_SHIPPED.md` — this file
- `core/services/ops_autopilot/budget.py:521-616` — BudgetController per-workspace methods + module-level cap-keying policy
- `core/llm_enforcer.py:242-283` — workspace freeze runtime hook
- `core/models_llm_routing.py:302` — LLMCallLog.workspace FK
- `core/management/commands/check_pa_tool_drift.py` — drift-lint

**Workspace UI:**
- Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` — the workspace that now has attribution + potentially cap-managed (no cap set at close; can be set via `SystemConfiguration workspace_daily_cap:<uuid>` key)
- Rigby Tool Gap Ledger deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` — updated at S2845; new S2846 candidate: `repo_tool` handler-body-locate timebox limitation

**Grafana / observability (if applicable):** none touched at S2846.

---

## Session-close ceremony

- Merged: `#3303` → `#3304` → `#3305` → `#3306` → `#3307`
- Recycled: 3 times (after `#3303`, after `#3305`, after `#3306` — final recycle after `#3307` at close)
- Docs cascade run once (post-#3304); needs one more run at close (embedded in this handoff commit)
- Session pin `pa-5eec7b14a3a5482b` retires; S2847 atomic-mints fresh
