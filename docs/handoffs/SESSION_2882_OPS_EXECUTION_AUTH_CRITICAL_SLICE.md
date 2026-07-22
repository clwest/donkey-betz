# Session 2882 — `ops_tool` EXECUTION + AUTH critical-slice structured error-envelope migration + `permission_denied` taxonomy expansion

**Date:** 2026-07-21
**Session pin (retired at close):** `pa-aae31b596346411e` (labeled `s2881-ops-write-path-critical-slice`; minted during S2881 docs cascade PR #3386, carried into S2882 open per steady-cadence shape)
**Prior pin retired at S2881 open:** `pa-0d3de74e1f7749d5`
**Slate label:** S2882 — `ops_tool` EXECUTION + AUTH critical-slice error-envelope migration + `permission_denied` follow-on
**PRs:** #3387 (`6331c833e`) + #3388 (`377f39364`) + `<docs cascade>` at close
**Combined regression:** 190/190 (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877 + S2878 + S2879 + S2880 + S2881 + **S2882** + `test_zoom_out_tool_2780`)

---

## Shipped

### PR #3387 `6331c833e` — S2882 slate (2 files, +191/-8)

- **`core/services/td_handlers_ops.py`** (+33/-8) — 4 sites migrated across two clusters. Reused the S2879 `_handler_error` helper at L48. `_authorize_staff` helper signature extended with `action_name` arg; 2 call-sites updated.
- **`core/tests/test_s2882_ops_execution_auth_error_envelope.py`** (NEW, 158 lines) — 4 test rows exercising full `ToolDispatcher.execute_sync` path via `ops_tool` (EXECUTION) and `workspace_budget_tool` (AUTH). Reuses the S2879 `_assert_migrated_envelope` helper.

### PR #3388 `377f39364` — S2882 close follow-on (2 files, +51/-8)

- **`core/services/td_handlers_ops.py`** (+16/-8) — `_handler_error` docstring expanded to 5-code taxonomy; `_authorize_staff` not-staff branch migrated to `permission_denied`.
- **`core/tests/test_s2882_ops_execution_auth_error_envelope.py`** (+35 lines) — 5th test row `test_set_default_cap_non_staff_returns_permission_denied` added. Uses `unittest.mock.patch` on `User.objects.get` to bypass `TestCase`-transaction-invisibility to the dispatcher's async ORM connection.

### Migration diff — 5 sites × 3 codes × 2 clusters × 2 dispatched tools

| Cluster | Site | Prior return shape | New `error_code` | Dispatched tool |
|---|---|---|---|---|
| EXECUTION | `_ops_execution_detail` missing execution_id (L1574) | `{'error': 'execution_id required'}` | `invalid_params` | `ops_tool` |
| EXECUTION | `_ops_execution_detail` DoesNotExist (L1583) | `{'error': f'Execution {id} not found'}` | `not_found` | `ops_tool` |
| AUTH | `_authorize_staff` no user (L4448) | `{'error': 'authentication required'}` | `invalid_params` | `workspace_budget_tool` |
| AUTH | `_authorize_staff` unknown actor (L4454) | `{'error': f'actor user_id=X not found'}` | `not_found` | `workspace_budget_tool` |
| AUTH | `_authorize_staff` not-staff (L4463, PR #3388) | `{'error': f'user_id=X is not staff...'}` | `permission_denied` (NEW code) | `workspace_budget_tool` |

Legacy-file population S2881=14 → **S2882=9** (5 sites cleared). Ops file remains IN the population with 9 bare returns in 4 clusters (agent-diag family).

---

## Rigby SIGN cycles

### Pre-code SIGN (3 turns, tool-grounded)

- **V1 (Slate 2 routing):** Rigby's Grep on `tool_dispatcher.py` for `ops_execution_detail` / `_ops_execution_detail` / `_authorize_staff` returned 0 matches (correct — those helpers live in `td_handlers_ops.py`, not the dispatcher). She verified the tool-surface registration: `ops_tool → _handle_ops` at `tool_dispatcher.py:519`, `autopilot_tool → _handle_autopilot` at L538. Correctly concluded EXECUTION cluster is native `ops_tool`. **Missed** the AUTH cluster's actual containing scope.
- **V2 (Slate 3 routing):** Rigby correctly Flag D-flagged that Slate 3 methods route through 4 DIFFERENT tool surfaces (`agent_memory_tool` L610, `heartbeat_history_tool` L611, `infra_health_tool` L612, `search_docs` L629 — no `_tool` suffix). Search-docs registration unverified in her session; Claude verified via direct Grep.
- **V3 (helper reuse):** Rigby explicitly flagged as PENDING — she hadn't read `td_handlers_ops.py:48` in her session. Claude verified directly.
- **Recommendation:** Rigby AGREED (b) sequential PRs, DISAGREED (a) bundle. Chris ratified (b) → Slate 2 as PR-1 at S2882.

### Post-code SIGN (1 turn, tool-grounded)

- **V1 CONFIRMED:** All 4 migrated sites quoted at HEAD via `repo_tool.read_file` and `repo_tool.search` with exact line numbers and code excerpts.
- **V2 CONFIRMED:** Both helpers (`_tool_error` L28, `_handler_error` L48) unchanged; no new helper introduced.
- **V3:** Rigby flagged pending (test file not opened); Claude verified via 189/189 regression pass.
- **Verdict:** AGREE conditional on V3 (Claude-verified).
- **Zoom-out (a) — TAXONOMY GAP:** Rigby recommended adding `permission_denied` 5th code before Slate 3 opens. Narrow, stable, prevents longer taxonomy-refinement arc.
- **Zoom-out (b) — FOLD D REPEATS:** Rigby recommended pre-code SIGN MUST grep for helper enclosing scope before labeling surface. Smallest procedural fix.

### Chris D-verdict (S2882 mid-close, 2026-07-21)

- **APPROVE** merge PR #3387 as-is (Slate 2, 4 sites).
- **APPROVE (a):** ship `permission_denied` 5th code as follow-on PR #3388 at S2882 close (not deferred to S2883).
- **APPROVE (b):** codify helper-enclosing-scope grep as SIGN discipline. Deferred to future PLAYBOOK amendment session (candidate: PLAYBOOK-6.10.10 extension or 6.10.11 sibling rule).

---

## Fold D 4th trigger — routing-boundary drift (mid-slate correction)

Pre-code SIGN framed both clusters as `ops_tool → _handle_ops` surface. Test dispatcher initially routed AUTH via `ops_tool` and got `unknown_action`. Root cause: `_authorize_staff` lives inside `_handle_workspace_budget` (dispatched via `workspace_budget_tool` at `tool_dispatcher.py:542`), NOT `_handle_ops`.

Same routing-boundary drift Rigby caught in prior slates:
1. **S2879** — governance surface migration (established the pattern was needed)
2. **S2880** — governance cluster: framed as `ops_tool`, actually `governance_tool`
3. **S2881** — write-path: framed as `ops_tool`, actually `autopilot_tool`
4. **S2882** — AUTH cluster: framed as `ops_tool`, actually `workspace_budget_tool`

**Amendment candidate (Chris-ratified deferral):** PLAYBOOK-6.10.10 (from S2881 close) already targets pre-code routing verification. Rigby's zoom-out (b) refines the rule text: pre-code SIGN MUST grep for the **enclosing handler method** of each targeted site (not just the action-key registration) before labeling the tool surface. The failure mode is consistent: "helper lives in `td_handlers_ops.py`, so surface = `ops_tool`" is the wrong inference — the containing `_handle_*` method determines the surface.

**Trigger count: 4** (well past PLAYBOOK §14.2 default 2-trigger threshold; well past S2881 informal 3-trigger threshold).

---

## Additional post-code folds (recorded for PLAYBOOK-6.10.8 substrate)

**Fold X — Async DB connection isolation surfaced during test authoring (1st trigger):** `TestCase` transactions are not visible to `ToolDispatcher.execute_sync`'s async ORM connection. Real actor creation short-circuited the not-staff test to `not_found` (User.objects.get raised in async connection → caught by broad `except Exception:`). Workaround shipped: `unittest.mock.patch` on `User.objects.get`. **Broader risk:** any future dispatcher-path test that requires DB-visible ORM state will hit the same wall — either use `TransactionTestCase`, mock the ORM boundary, or refactor the dispatcher to accept an injected DB session. Not a same-slate fix; forward-carry.

**Fold Y — `_authorize_staff` broad `except Exception:` swallows SynchronousOnlyOperation (1st trigger):** Related to Fold X. The current helper catches every exception and treats it as "actor not found." This is why `_handler_error(action_name, 'not_found', ...)` fires even when the underlying failure is a connection-mode error, not a real DoesNotExist. **Broader risk:** production dispatcher paths that hit sync-in-async issues would silently return `not_found` envelopes. Fix candidate: narrow the except to `User.DoesNotExist`. Not shipped at S2882 close — surface-behavior change, requires its own SIGN.

**Fold Z — Legacy population count math (informative):** 14 remaining sites (S2881 close) − 4 Slate 2 sites − 1 permission_denied follow-on site = 9 sites in `td_handlers_ops.py`. Verifiable via `grep -n "return {'error':" core/services/td_handlers_ops.py`. Slate 3 (agent-diag family, 10 sites) actually LOOKS wrong on this math — 9 total remaining but Slate 3 was scoped as 10. Need routing-map + fresh grep at S2883 open before committing to Slate 3 site list.

---

## Not shipped at S2882 close (deferred to S2883 or later)

- **Slate 3 (agent-diag family, ~9-10 sites)** — 4 handler methods each on a separate tool surface. Requires per-method routing verification per Fold D discipline. Chris deferred from S2882 bundle.
- **PLAYBOOK-6.10.10 amendment ratification** — 4 triggers on record; still awaiting ratification session.
- **Rigby zoom-out (b) helper-enclosing-scope SIGN discipline** — candidate PLAYBOOK amendment extension.
- **Fold X (async DB isolation)** — forward-carry, 1st trigger.
- **Fold Y (broad except catch in `_authorize_staff`)** — forward-carry, 1st trigger.
- **Grep-based CI audit metric** (Fold 3 convergent from S2881) — small parallel ship candidate, still deferred.
- All prior deferred items from S2880/S2879/S2878/S2877/S2876/S2874/S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc still carried.

---

## Runtime impact

- Fifth wave of real handler migrations in the S2876 backfill sunset arc, fourth criticality-first slate.
- Legacy-file population: S2881=14 → **S2882=9** (5 sites cleared).
- Regression suite grew from 185 → 190 (+5 S2882 rows).
- 5 sites (2 EXECUTION + 3 AUTH) no longer surface `error_code='legacy_error'`; consumers can key on structured taxonomy codes.
- **New 5th taxonomy code `permission_denied`** — expanded from the S2879 4-code minimal set. Scope strictly authz.
- No new helper introduced — S2879 `_handler_error` reused for all 5 sites.
- Fold D reached 4th trigger — PLAYBOOK-6.10.10 amendment candidate strengthened.

---

## Working loop observations at S2882

- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code SIGN with 8+ real `repo_tool` runs; post-code SIGN with 10+ real `repo_tool` runs at HEAD. Not rubber-stamp — Rigby's V2 correctly flagged Slate 3 as multi-surface risk and DISAGREED with the bundle path.
- `feedback_zoom_out_ask_per_rigby_sign` — post-code zoom-out delivered two actionable recommendations (a) + (b), both Chris-ratified. (a) shipped in-session as PR #3388.
- `feedback_read_full_rigby_response_not_just_tail` — Rigby's pre-code + post-code responses had informative bodies above the `Tool Runs (verbose)` separator; Claude filtered via grep/sed.
- `feedback_claude_stdout_truncation_vs_ui_truncation` — recognized truncations were Claude-stdout only; Chris saw the full responses.
- `feedback_claude_directs_rigby_then_verifies` — Claude directed narrow tool-grounded verification with concrete line numbers + specific taxonomy checks; Rigby executed with quoted evidence; Claude verified HEAD via direct file reads.
- `feedback_claude_rigby_agree_first_chris_yes_no` — pre-code + post-code SIGN both reached joint agreement BEFORE Chris D-verdict. Chris ratified all 3 asks in one turn.
- `feedback_engineering_bias_over_audit` — net-new engineering ship (5 sites, +1 taxonomy code).
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge on both PRs (`sha=6331c833e13d` then `sha=377f393647d4`, both `surviving=none`).
- `feedback_local_truth_no_production` — 190/190 local pass IS the deploy step.
- `feedback_rigby_writes_workspace_deliverables` — Ledger update via Rigby PA at close (see close-out step).
- `feedback_gh_pr_merge_admin_until_billing_fixed` — merged PR #3387 + #3388 with `--admin` flag.
- `feedback_per_pr_summary_signals_close_readiness` — mid-flight per-PR summary + still-open checklist delivered between #3387 and #3388.

---

## For fuller S2876 sunset arc context (spans S2876 → S2882)

See:
- **S2881 handoff:** `docs/handoffs/SESSION_2881_OPS_WRITE_PATH_CRITICAL_SLICE.md`
- **S2880 handoff:** `docs/handoffs/SESSION_2880_OPS_REMAINDER_CRITICAL_SLICE.md`
- **S2879 handoff:** `docs/handoffs/SESSION_2879_GOVERNANCE_OPS_CRITICAL_SLICE.md`
- **S2878 handoff:** `docs/handoffs/SESSION_2878_BPAAS_ERROR_ENVELOPE.md`
- **S2877 handoff:** `docs/handoffs/SESSION_2877_PA_SURFACE_ERROR_CODES_SMOKE.md`
- **S2876 handoff:** `docs/handoffs/SESSION_2876_DISPATCHER_ERROR_CODE_BACKFILL.md`
