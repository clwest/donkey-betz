# Session 2879 — `governance_tool` + `ops_tool` critical-slice structured error-envelope migration

**Date:** 2026-07-21
**Session pin (retired at close):** `pa-7f847367d41a4d10` (labeled `s2879-governance-ops-critical-slice`; minted at S2879 open via `session_lifecycle close`)
**Prior pin retired at S2879 open:** `pa-3c31ea25818f48f6` (minted during S2878 docs cascade PR #3380)
**Slate label:** S2879 — governance + ops critical-slice error-envelope migration
**PRs:** #3381 (`9a3039e22e69`) + `<docs cascade>` at close
**Combined regression:** 167/167 (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877 + S2878 + S2879 + test_zoom_out_tool_2780)

---

## Shipped

**PR #3381 `9a3039e22e69` — S2879 slate (4 files, +279/-32)**

- **`core/services/td_handlers_governance.py`** (+29/-4) — new `_handler_error(action, code, message, **fields)` at top of file emitting the S2874 canonical 4-key envelope `{success: False, error_code, error, action, **fields}`. Migrated the single `_handle_zoom_out` unknown-action default at L63 to use it. Docstring explicitly calls out intentional split from the S2875 3-key `_tool_error`.
- **`core/services/td_handlers_ops.py`** (+66/-13) — new `_handler_error` helper at L48 (right after the S2875 `_tool_error`). Docstring locks the 4-code S2879 taxonomy per Rigby's condition #3: `invalid_params` / `not_found` / `unknown_action` / `dependency_missing`. 7 sites migrated (see table below).
- **`core/tests/test_s2879_governance_ops_error_envelope.py`** (NEW, 176 lines) — 8 test rows exercising full `ToolDispatcher.execute_sync` path. ImportError paths simulated via `patch.dict(sys.modules, {'core.models_...': None})` (documented pattern for the `except ImportError` guards).
- **`core/tests/test_s2877_pa_surface_error_codes_smoke.py`** (+11/-17) — deleted `test_ops_tool_unknown_action_backfilled` from `LegacyBackfillPASurfaceTests` (site now migrated). Class docstring updated with re-home pointer, matching the S2878 F4 pattern.

### Migration diff — 8 sites × 3 canonical codes

| File | Site | Prior return shape | New `error_code` |
|---|---|---|---|
| governance | L40 `_handle_zoom_out` unknown action | `{'error': f'Unknown zoom_out_tool action: ...'}` | `unknown_action` |
| ops | L317 `focus_mode_update` no `config_updates` | `{'error': 'config_updates dict required'}` | `invalid_params` |
| ops | L397 `_handle_ops` dispatcher default | `{'error': f'Unknown ops_tool action: ...'}` | `unknown_action` |
| ops | L1100 `_ops_celery_task_history` ImportError | `{'error': 'CeleryTaskEvent model not available'}` | `dependency_missing` |
| ops | L1169 `_ops_tenant_boundary_violations` ImportError | `{'error': 'OpsRunEvent model not available'}` | `dependency_missing` |
| ops | L1178 `_ops_tenant_boundary_violations` invalid failure_kind | `{'error': f'invalid failure_kind ...'}` | `invalid_params` |
| ops | L1298 `_ops_staleness_warnings` ImportError | `{'error': 'OpsRunEvent model not available'}` | `dependency_missing` |
| ops | L1306 `_ops_staleness_warnings` invalid verdict | `{'error': f'invalid verdict ...'}` | `invalid_params` |

The two multi-error-path helpers (`_ops_tenant_boundary_violations` + `_ops_staleness_warnings`) had BOTH error exits migrated together per Rigby's condition #4 (no partial migration inside any single action).

All 8 new envelopes include `'action': action` per Rigby's S2878 F3 guardrail.

### Why governance + ops critical slice — criticality-first pick (Rigby F5 forward-carry from S2878)

Per Rigby's S2878 pre-code SIGN F5 zoom-out, S2879 was locked to criticality-first, NOT breadcrumb-first, to avoid the platform appearing contract-stable while most real failures still fall through `error_code='legacy_error'`. Rigby's rationale ratified at S2879 pre-code SIGN:

- **Ops failures compound during incident/debug loops.** When an operator hits an error in `ops_tool`, they're already diagnosing something; opaque errors turn debugging into recursive debugging.
- **Governance is "free momentum" with low risk** — 1 site, 5-minute ship, adds coverage in the same PR without stealing cycles from the ops slice.
- **Content deferred to S2881+** — publishing errors painful but generally retriable and less incident-critical than ops observability/config surfaces.

### Pre-code SIGN via Rigby (2026-07-21, 8 grounded `repo_tool` runs)

Not rubber-stamp per `feedback_verify_rigby_tool_runs_before_trusting_sign`. Folds:

| Question | Verdict | Resolution |
|---|---|---|
| 1: Verify 19/26/1 site counts | F-BLOCKING correction | Actual populations: **13** content / **37** ops / **1** governance — 00-START-claimed 19/26 numbers unverified. Not a scope blocker; corrects the doc |
| 2: Sample site characterization | AGREE + tool-grounded | Read sample sites in each file; confirmed action-scope mapping |
| 3: Ranking — blast radius | AGREE | Ops > content > governance |
| 3: Ranking — complexity | AGREE | Governance lowest, content moderate, ops higher (mix of validation + import guards) |
| 4: S2879 slate recommendation | AGREE-with-refinement | Governance 1 site + ops critical slice (4-5 highest-blast-radius actions); ops remainder → S2880; content → S2881+ |
| 5 (mandatory conditions): 4-code taxonomy + F3 rigor + no-partial-migration + critical-slice must include ImportError guards | AGREE ratified | All 4 conditions applied in shipped code |
| Zoom-out fold | RAISED-CONCERN | See §Zoom-out folds below — forward-carried to S2880+ |

Rigby's proposed mitigation for the two-shape coexistence (given D6 moratorium blocks a full helper-extraction arc): enforce a **local micro-template** inside the PR — a small helper function in-file so all migrated envelopes are byte-identical shape. **Implemented as `_handler_error` in each of the two files.**

### Mid-implementation SIGN — helper-shape narrow AGREE (Rigby)

At implementation time, the existing `_tool_error(code, message, **fields)` in `td_handlers_ops.py:28` (Rigby's S2875 helper) was found to output the 3-key `{error, error_code, **fields}` shape — NOT the 4-key S2878 canonical shape. Twelve existing adopters in ops use it.

Claude proposed: add NEW local `_handler_error` helper in each file (governance + ops) matching the S2878 4-key shape, and do NOT modify `_tool_error` (would silently break the 12 existing call sites' contract). Rigby AGREE with the reasoning; docstring on both new helpers explicitly documents the intentional split and points at Rigby's 6-adopter helper-extraction gate as the reconciliation trigger.

### Post-code SIGN via Rigby (2026-07-21, 8 grounded `repo_tool` runs on shipped files)

**AGREE — READY TO SHIP.**

- **Condition #1** (helper identity): both `_handler_error` helpers produce byte-identical 4-key envelope shape ✓
- **Condition #2** (correct action scope): all 7 ops sites pass the correct `action=` string (dispatcher-scope for the fallthrough, explicit string for the helper-scoped sites) ✓
- **Condition #3** (no partial migration): `_ops_tenant_boundary_violations` and `_ops_staleness_warnings` have zero remaining bare `{'error': ...}` returns in their action-scope bodies ✓

## Zoom-out folds — post-code (per `feedback_zoom_out_ask_per_rigby_sign`)

Rigby raised 4 forward-carry concerns, all logged in Rigby Tool Gap Ledger #22 as 1st-trigger observations:

- **V1 — Two-layer error-contract accretion.** 3-key `_tool_error` + 4-key `_handler_error` now coexist. Stable if consumers never assume a single universal schema; watch for third trigger before promoting to a helper-extraction ADR.
- **V2 — Consumer ambiguity on `success`/`error` key semantics.** Callers keying on `success is False` will miss legacy errors; callers keying on `if 'error' in result` will false-positive on success payloads that legitimately have an `error` key.
- **V3 — Inconsistent `action` presence.** Handler envelope has it, legacy doesn't. UI/logging keyed on `action` degrades silently.
- **V4 — Normalization utility candidate.** A local helper at ToolDispatcher post-processing that converts either shape to a common internal representation for PA surfaces. Would prevent shape-leak into every new consumer. Still endorsed to defer to Rigby's 6-adopter gate.

Rigby's summary: "You're accreting a two-layer error-contract system. That's stable short-term only if consumers never assume a single universal schema."

## D-verdict

Chris approved S2879 slate + Rigby's 4 conditions at pre-code SIGN. Post-code SIGN AGREE from Rigby → shipped PR #3381 with `--admin` merge per `feedback_gh_pr_merge_admin_until_billing_fixed`.

## Working-loop observations at S2879

- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code SIGN Rigby ran 8 real `repo_tool` runs; post-code SIGN ran 8 more on shipped files. Not rubber-stamp.
- `feedback_zoom_out_ask_per_rigby_sign` — fired 2×: pre-code (F5 → 4 forward-carries) and post-code (V1-V4 → all forward-carried as 1st-trigger observations).
- `feedback_claude_directs_rigby_then_verifies` — Claude directed helper-shape verification with concrete evidence (site line numbers, 3-key vs 4-key concrete grep); Rigby AGREE with grounded tool runs.
- `feedback_claude_rigby_agree_first_chris_yes_no` — F1 F-BLOCKING (site count correction) + helper-shape narrow SIGN both resolved between Claude+Rigby BEFORE Chris D-verdict. Chris got 1 recommendation on the slate, not a menu.
- `feedback_engineering_bias_over_audit` — net-new engineering ship (helper + 8-site migration + regression coverage).
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=9a3039e22e69, surviving=none`).
- `feedback_read_full_rigby_response_not_just_tail` — pre-code SIGN response truncated at the AGREE rationale mid-sentence; Rigby re-emitted the tail cleanly on follow-up dispatch.
- `feedback_claude_stdout_truncation_vs_ui_truncation` — the AGREE-rationale truncation actually appeared in Chris's Chat UI too (not just Claude's stdout), so it was a genuine response truncation; re-fetch was necessary.
- `feedback_local_truth_no_production` — 167/167 local pass IS the deploy step.
- `feedback_rigby_writes_workspace_deliverables` — Rigby Tool Gap Ledger update via Rigby PA at close (not Claude ORM-direct).
- `feedback_gh_pr_merge_admin_until_billing_fixed` — merged PR #3381 with `--admin` flag.

## Sunset arc progress (Ledger #22)

- Legacy-file population enumerated at S2877: **39 files**
- Post-S2878: **38 files** (bpaas_tool fully migrated)
- Post-S2879: governance file fully migrated (0 remaining bare returns) → **37 files**. Ops file partially migrated (7 sites down; ~30 single-line + 2 multi-line still legacy) → stays IN population.

Two of 39 legacy files now fully clean. Content file (~13 sites) untouched. Full sunset still gated on migrating the ~30 remaining ops sites (S2880 candidate) + content file (S2881+) + the remaining ~35 files.

## Not shipped at S2879 close (deferred to S2880+)

- Ops remainder (~30 sites across ~10-12 actions) — S2880 primary slate driver
- `td_handlers_content.py` (13 sites) — S2881+
- The 4 new zoom-out folds (V1-V4) — all 1st-trigger; watch for second trigger before promotion
- All prior carried items from S2878/S2877/S2876/S2875/S2874 still deferred
