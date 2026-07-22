# Session 2878 — `bpaas_tool` structured error-envelope migration (breadcrumb-driven, Ledger #22 followup)

**Date:** 2026-07-21
**Session pin (retired at close):** `pa-e869c051b9fd4c0d` (labeled `s2878-legacy-handler-envelope-migration`; minted at S2878 open via `session_lifecycle close`)
**Prior pin retired at S2878 open:** `pa-f45f81cb7ef34005` (mint drift observation — see §Drift Notes)
**Slate label:** S2878 — bpaas_tool structured error-envelope migration
**PRs:** #3379 (`ac1854f6d`) + `<docs cascade>` at close
**Combined regression:** 139/139 (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877 + S2878)

---

## Shipped

**PR #3379 `ac1854f6d` — S2878 slate (4 files, +178/-18)**

- **`core/services/td_handlers_agents.py`** — `_handle_bpaas` (L6234-6303) migrated from bare `{'success': False, 'error': msg}` returns to S2874 canonical shape `{success, error_code, error, action}`. 5 error-return sites → 3 canonical codes.
- **`core/tests/test_s2877_pa_surface_error_codes_smoke.py`** — deleted `test_bpaas_generate_close_pack_empty_packet_backfilled` from `LegacyBackfillPASurfaceTests`; updated class docstring (removed bpaas from "representative handlers" list; added S2878 pointer).
- **`core/tests/test_s2878_bpaas_error_envelope.py`** (NEW) — `BpaasToolMigratedEnvelopeTests` class, 5 rows, full `ToolDispatcher.execute_sync` end-to-end path. `handler_exception` row uses `unittest.mock.patch` on the packet_service module-level symbol.
- **`.gitignore`** — housekeeping rule `docs/audits/SESSION_*_SYSTEM_AUDIT_*.md` (19 untracked auto-generated snapshots from the Session 819 System Audit API cleaned at S2878 open). Force-add fallback documented in-comment.

### Migration diff — 5 sites × 3 canonical codes

| Site | Prior return shape | New `error_code` |
|---|---|---|
| L6237 (`action` missing) | `{'success': False, 'error': 'action is required'}` | `missing_required_params` |
| L6249 (`create_project` missing workspace_id/packet) | `{'success': False, 'error': 'workspace_id and packet are required'}` | `missing_required_params` |
| L6261 (`generate_close_pack` missing packet) | `{'success': False, 'error': 'packet is required'}` | `missing_required_params` |
| L6273 (unknown action) | `{'success': False, 'error': f"Unknown action: ..."}` | `unknown_action` |
| L6277 (exception fallback) | `{'success': False, 'error': str(e)}` | `handler_exception` |

All 5 new envelopes include `'action': action` per Rigby's F3 guardrail (context consistency across success/error planes).

### Why bpaas + only bpaas — breadcrumb telemetry driver

Grep of the S2876 `legacy_handler_error_envelope_missing_error_code` breadcrumb in `django_debug.log`: 24 total hits, of which the ONLY real (non-test-fixture) handler is `bpaas_tool.generate_close_pack` — 3 hits. All other hits are `_s2876_fake_tool` (S2876 test suite fixture) or `newsletter_tool`/`ops_tool` `__bogus_action_s2877__` (S2877 unknown-action test rows).

Narrow scope preserves the S2874/S2875/S2876/S2877 one-thing-per-PR arc discipline.

### Pre-code SIGN via Rigby (2026-07-21, 3 grounded `repo_tool.read_file` runs)

Not rubber-stamp per `feedback_verify_rigby_tool_runs_before_trusting_sign`. Folds:

| Question | Verdict | Resolution |
|---|---|---|
| F1: 5 error-return sites + shape claims | AGREE + tool-verified | Read `td_handlers_agents.py:6200-6420`, confirmed 5 sites + envelope claims |
| F2: S2876 breadcrumb text + sunset criteria | AGREE + tool-verified | Read `tool_dispatcher.py:40-120`, confirmed sunset criteria wording (all handlers emit `error_code` OR `<1%` for 14d) |
| F3: naming taxonomy | AGREE-with-refinement | Consolidated 5 proposed codes → 3: collapse three "required-param-absent" sites to single `missing_required_params` (human-readable specificity preserved in `error` string). Keep `unknown_action` + `handler_exception` |
| F4: S2877 test-file scope | AGREE | Re-home (not duplicate) the 1 bpaas row currently in `LegacyBackfillPASurfaceTests`. S2877 file edit is part of S2878 PR scope, not a separate PR |
| F5 (zoom-out, mandatory) | RAISED-CONCERN | See §Zoom-out fold below — forward-carried to S2879 |

### Zoom-out fold — F5 substantive concern (per `feedback_zoom_out_ask_per_rigby_sign`)

Rigby: "The dispatcher backfill makes the platform *appear* contract-stable (everything has an `error_code`), which can mask how many handlers are still legacy. If we only migrate breadcrumb-hit handlers, we risk a long tail where most failures still come through as `error_code='legacy_error'`."

Two concrete costs Rigby named:

1. **Product/UX cost:** clients start depending on meaningful `error_code` taxonomy (targeted UI copy, suggested fixes, retry semantics), but `legacy_error` is non-actionable — the contract becomes "formally present but semantically useless" for most tools.
2. **Migration cost:** Sunset criterion #1 (all handlers emit `error_code`) stays out of reach. Even if criterion #2 (<1% for 14d) passes because legacy paths are *rare*, the surface is still uneven.

**Coupling/risk from staying breadcrumb-driven:** optimizes for *observed runtime frequency*, not *criticality / blast radius*. Rare-but-critical handlers (publishing moments, ops/admin workflows) may starve — exactly the paths where structured envelopes matter most at incident time.

**Not altering S2878 scope (arc discipline preserved).** Forward-carried to S2879 as the criticality-first slate selector — S2879 opens on a criticality-driven pick (candidate: `td_handlers_content.py` 19 sites, or `td_handlers_ops.py` 26 sites), not another breadcrumb-driven one.

### Post-code SIGN via Rigby (2026-07-21, 3 grounded `repo_tool.read_file` runs on shipped files)

**AGREE on V1/V2/V3 file verification:**

- **V1** (bpaas migration): 5 sites verified emit `{success, error_code, error, action}` shape with promised codes; `action` in scope at exception-fallback L6277.
- **V2** (S2877 file edit): `LegacyBackfillPASurfaceTests` now has ONLY 2 methods (newsletter + ops); docstring updated per plan.
- **V3** (S2878 new file): 5 tests map 1:1 to 5 handler sites; all use `execute_sync` end-to-end; assertions never test full error-message text.

**V4 zoom-out — 2 risk-flagged concerns (not F-BLOCK):**

| Concern | Rigby's ask | Claude's resolution |
|---|---|---|
| V4a: patch target for function-scoped import | Consider patching in `td_handlers_agents` module namespace | Empirically correct as-shipped: `from X import Y` inside function body re-fetches `X.Y` from sys.modules on each call, so patching `X.Y` intercepts. Rigby's alternative (`td_handlers_agents.generate_close_pack`) would fail — the name isn't bound at module scope. Local test passes; standard Python mock idiom. **No change.** |
| V4b: `.gitignore` glob breadth | Consider narrowing or negation-allowlist for canonical retention | Kept the broad glob but added in-comment fallback: `git add -f docs/audits/SESSION_<n>_SYSTEM_AUDIT_<ts>.md` for canonical retention. **1-line comment added.** |

## D-verdict (Rigby-ratified per `feedback_claude_rigby_agree_first_chris_yes_no`)

Chris routed the S2878 slate D-verdict via Rigby: **YES ship as scoped**, with guardrails:

- Use only 3 codes: `missing_required_params`, `unknown_action`, `handler_exception` ✓
- Include `action` in envelope for all 5 sites ✓
- Test move is in-scope: remove single BPaaS legacy-backfill assertion + reassert under migrated coverage ✓
- `.gitignore` housekeeping rides along ✓
- Forward-carry: S2879 locked to **criticality-first** slate, not breadcrumb-first ✓

## Working-loop observations at S2878

- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code SIGN Rigby ran 3 real `repo_tool.read_file` runs; post-code SIGN ran 3 more on shipped files. Not rubber-stamp.
- `feedback_zoom_out_ask_per_rigby_sign` — fired 2×: pre-code (F5 → S2879 forward-carry), post-code (V4a/V4b → 1 comment edit + defense of patch idiom).
- `feedback_claude_rigby_agree_first_chris_yes_no` — F3 taxonomy + F4 test scope resolved between Claude+Rigby before Chris D-verdict. Chris got 1 recommendation, not a menu.
- `feedback_engineering_bias_over_audit` — net-new engineering ship (handler migration + regression coverage, not audit-of-what-exists).
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=ac1854f6d09a, surviving=none`).
- `feedback_read_full_rigby_response_not_just_tail` — pre-code SIGN response truncated at F5; re-fetched cleanly to get full zoom-out concern.
- `feedback_claude_stdout_truncation_vs_ui_truncation` — the F5 re-fetch was for Claude's execution context (mine); Chris likely saw the full response in Chat UI.
- `feedback_local_truth_no_production` — 139/139 local pass IS the deploy step.
- `feedback_rigby_writes_workspace_deliverables` — Rigby Tool Gap Ledger update via Rigby PA at close.
- `feedback_gh_pr_merge_admin_until_billing_fixed` — merged PR #3379 with `--admin` flag.

## Rigby Tool Gap Ledger updates (via Rigby PA per `feedback_rigby_writes_workspace_deliverables`)

- Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **#22 (S2876 dispatcher backfill sunset progress)** → 1 handler migrated (`_handle_bpaas`). Legacy population enumerated at S2877 was 39 files; now 38 (bpaas removed from the count).
- **[carried from S2877]** #22.4 (Rigby cannot dispatch arbitrary tool-name strings) → still 1st trigger from S2877 post-code SIGN F5 delegation; NOT observed again at S2878 (no F-VERIFIED post-code live probe needed — post-code was file-read verification only). Watch for 2nd trigger.
- **[carried from S2876]** #22.3 (orthogonal-contract-axes in handler error responses) → S2878 migration produces a datapoint but does NOT resolve the underlying question of `success:False` vs `error_code`-only convention. Still 1st trigger. Watch for 2nd trigger before promoting.

## Drift Notes

- **Pin retirement mismatch:** 00-START-NEXT-SESSION at S2877 close listed `pa-d822f8e637c7449a` as the pin to retire at S2878 open. Actual retire at `session_lifecycle close --label s2878-...` retired `pa-f45f81cb7ef34005` (which came into existence between S2877 close's `session_lifecycle` run and S2878 open, likely from the S2877 docs cascade PR #3378 wrapper rewrite). Minor observation — not blocking. Current active S2878 pin is `pa-e869c051b9fd4c0d`.
- **`_s2876_fake_tool` breadcrumb noise:** the S2876 test suite creates a fake tool and dispatches through it to prove backfill fires; the breadcrumb logs these dispatches even though they're test fixtures. Not actionable (test fixtures are supposed to fire the breadcrumb by design), but a future observability refinement could add a "fixture-marker" to distinguish test dispatches from real handler hits. NOT slated — 1st noise observation only.

## S2879 forward-carry — criticality-first slate selector

Rigby's F5 zoom-out folds into S2879 slate selection:

- **Do not open S2879 on another breadcrumb-hit handler** (there aren't real hits anyway — bpaas was the only one).
- **Open S2879 on a criticality-driven pick.** Candidate first-look targets:
  - `td_handlers_content.py` (19 `{'error': ...}` sites, PA content pipeline — high blast radius at publishing/deliverable moments)
  - `td_handlers_ops.py` (26 sites, ops-tool = admin/operator surface — high blast radius at incident/triage moments)
  - `td_handlers_governance.py` (1 site — small, but governance = ratification/decision surface, high semantic weight per row)

Suggest S2879 opens with a Rigby pre-code SIGN that ranks these three by (a) call frequency in prod-adjacent code, (b) failure blast radius, (c) migration complexity.
