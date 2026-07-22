# Session 2880 — `ops_tool` remainder critical-slice structured error-envelope migration

**Date:** 2026-07-21
**Session pin (retired at close):** `pa-73d2689f9e8c4e7c` (labeled `s2879-governance-ops-critical-slice`; carried into S2880 open — no fresh mint at open per steady-cadence session shape)
**Prior pin retired at S2879 open:** `pa-3c31ea25818f48f6` (minted during S2878 docs cascade PR #3380)
**Slate label:** S2880 — ops_tool remainder critical-slice error-envelope migration
**PRs:** #3383 (`e6ae8a1b3a59`) + `<docs cascade>` at close
**Combined regression:** 174/174 (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877 + S2878 + S2879 + S2880 + test_zoom_out_tool_2780)

---

## Shipped

**PR #3383 `e6ae8a1b3a59` — S2880 slate (2 files, +209/-7)**

- **`core/services/td_handlers_ops.py`** (+35/-7) — 7 sites migrated across 3 subsets. Reused the S2879 `_handler_error` helper at L48 (no new helper introduced). 4-code S2879 taxonomy honored (5 × `invalid_params` + 1 × `not_found` + 1 × `unknown_action` this slate; `dependency_missing` unused).
- **`core/tests/test_s2880_ops_remainder_error_envelope.py`** (NEW, 174 lines) — 7 test rows exercising full `ToolDispatcher.execute_sync` path. Reuses the S2879 `_assert_migrated_envelope` module-level helper (single-source contract, forces a compile-time break if the S2879 helper signature drifts).

### Migration diff — 7 sites × 3 canonical codes × 3 subsets

| Subset | Site | Prior return shape | New `error_code` | Dispatched tool |
|---|---|---|---|---|
| kill-switch | `governance_set_mode` missing mode (L3567) | `{'error': 'mode is required (...)'}` | `invalid_params` | `autopilot_tool` |
| kill-switch | `governance_kill_switch` missing target (L3585) | `{'error': 'target is required (...)'}` | `invalid_params` | `autopilot_tool` |
| kill-switch | `governance_deactivate_switch` missing switch_id (L3602) | `{'error': 'switch_id is required'}` | `invalid_params` | `autopilot_tool` |
| scheduled-task | `_handle_scheduled_tasks` enable/disable missing task_id (L6002) | `{'error': 'task_id or name required for enable/disable'}` | `invalid_params` | `scheduled_tasks_tool` |
| scheduled-task | `_handle_scheduled_tasks` disable task not found (L6009) | `{'error': f'Scheduled task not found: ...'}` | `not_found` | `scheduled_tasks_tool` |
| ops-digest | `_handle_ops_digest` post missing conversation_id (L5279) | `{'error': 'conversation_id required for post action'}` | `invalid_params` | `ops_digest_tool` |
| ops-digest | `_handle_ops_digest` local unknown-action fallback (L5308) | `{'error': f'Unknown action: ...'}` | `unknown_action` | `ops_digest_tool` |

Rigby condition #4 (no partial migration inside any single action) verified PASS for all 6 unique actions in post-code SIGN.

### Slate framing correction — governance actions dispatch via `autopilot_tool`, not `ops_tool`

Pre-code assumption in 00-START-NEXT-SESSION.md Step 2 slated the 3 governance kill-switch actions as `ops_tool` sites. Runtime routing check during test authoring corrected: `governance_set_mode` / `governance_kill_switch` / `governance_deactivate_switch` live inside `_handle_autopilot` (registered as `autopilot_tool` at `tool_dispatcher.py:538`), not `_handle_ops`. Test dispatch fixed pre-merge; slate still valid because the migration edits remained in `td_handlers_ops.py` regardless of the dispatching tool name.

Recorded as Fold D at post-code SIGN (2nd trigger — see below).

### Why ops remainder critical-slice — criticality-first cadence continued (from S2879)

Per Rigby's S2879 F5 forward-carry (breadcrumb-driven migration lets the platform appear contract-stable while most real failures still fall through `error_code='legacy_error'`), S2880 stayed criticality-first, ranking against ops-incident-loop blast radius:

- **Kill-switch / mode-change** — the knobs you reach for while the platform is on fire; envelope consistency here reduces "can't tell what failed" risk during containment.
- **Scheduled-task enable/disable** — beat mutations; failures during operational adjustment (unusual but not rare) benefit from explicit `not_found` vs `invalid_params` distinction.
- **Ops-digest post + local unknown-action** — operator-facing surface; digest-post failures (bad conversation_id) are actionable messages, unknown-action fallback stops the "why did nothing happen?" mystery.

Excluded from S2880 slate (deferred to S2881+):
- **Subset 2 (write-path, 11 sites)** — `draft_*` / `close_pack_*` / `meeting_*` / `event_reply` at L3312-3533. Mutation-risk containment.
- **Subset 3 (agent-diag, 8+ sites)** — `agent_memory` / `heartbeat_history` / `infra_health` / `pa_diag`. PR-size containment.

### Pre-code SIGN via Rigby (2026-07-21, tool-grounded)

Not rubber-stamp per `feedback_verify_rigby_tool_runs_before_trusting_sign`.

**Turn 1 (initial ranking):** Rigby returned §1 site counts for subsets 1-3 (kill-switch=3 / write-path=11 / agent-diag=8+) with tool-grounded evidence; §4/§5 unverified. She flagged this as an F-BLOCKING gap in §1 ("If you want the table fully complete per your ask, I need one more tool pass over the enable/disable handler section and the conversation-post + dispatcher-default section.") — but Claude did not initially route the follow-up. Chris caught the missed offer.

**Turn 2 (complete verification):** Rigby completed subset 4 (2 sites at L6002 + L6009) and subset 5 (2 sites at L5279 + L5308; dispatcher default already migrated at L429-434, 0 sites). Ranking updated: recommendation shifted from Subset-1-only to Subset 1 + 4 + 5 combined (7 sites in one PR), still meeting small-PR + no-partial-migration constraints.

**§4 zoom-out folds (pre-code):**
1. **Fold 1 (1st):** Criticality-first optimizes for operator panic-time at expense of systematic surface reduction.
2. **Fold 2 (2nd):** 4-code taxonomy risks becoming "the ops-tool contract" not "the platform contract" if migration stays ops-scoped.
3. **Fold 3 (2nd trigger for V4):** Normalization utility V4 or `td_error.py` extraction might dominate criticality-first cadence on total risk/effort. 1st trigger at S2879 post-code; 2nd trigger here.

**Chris D-verdict:** Approve S2880 = 7-site kill-switch + scheduled-task + conversation-post slate. Ratified pre-code.

### Post-code SIGN via Rigby (2026-07-21, 7 grounded `repo_tool` runs at HEAD `e6ae8a1b3a59`)

**§1 per-site verification:** All 7 sites AGREE with quoted evidence. Confirmed:
- All 3 kill-switch sites emit correct `_handler_error` shape with matching action names.
- Both scheduled-task sites correctly pass the runtime `action` variable (works for both `enable` and `disable`).
- Both ops-digest sites emit correct action + code.

**§2 taxonomy code count:** invalid_params=5, not_found=1, unknown_action=1, dependency_missing=0 — matches slate spec exactly.

**§3 no-partial-migration audit:** All 6 unique actions PASS. Rigby noted correctly that other `return {'error':}` sites exist elsewhere in the file (L1576, L1581, L3312, L3324, L3364, and ~25 others) but NOT inside migrated actions — those are the S2881+ backlog.

**§4 helper-reuse:** PASS. `_handler_error` defined once at L48, no duplicate added.

**§5 zoom-out folds (post-code):**
1. **Fold A (2nd trigger — criticality-first pacing):** Cadence stays valid *if* remaining slates stay clusterable + bounded. If next remainder is diffuse (many unrelated actions, scattered sites), criticality-first becomes a pacing trap: lots of tiny PRs, repeated review overhead, rising inconsistency risk.
2. **Fold B (3rd trigger — V4 normalization utility).** Prior triggers: S2879 post-code (1st) + S2880 pre-code (2nd) + S2880 post-code (3rd). Rigby recommends: don't do N more 5-10 site PRs if ~30 bare-return remainder is diffuse; a safe mechanical normalizer with guardrails/tests likely dominates on total risk/effort. NOT the same axis as the 6-adopter `_tool_error → td_error.py` extraction gate.
3. **Fold C (2nd trigger — two-helper coexistence coupling):** If `_handler_error` keeps spreading only in ops surfaces while other tools stay on `_tool_error`, taxonomy discipline becomes "ops-only correctness" and cross-tool consistency drifts (harder for operators to build a single mental model of errors).
4. **Fold D (2nd trigger — governance routing/ownership boundary drift):** Governance actions are effectively `ops_autopilot` engine calls inside `ops_tool` (well, `autopilot_tool` per S2880 correction). For S2881, explicitly track whether we're modifying (a) handler surface, (b) autopilot engine internals, or (c) both.

**§6 F-BLOCKING:** NONE.

### Working loop observations at S2880

- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code SIGN turn 1 = tool-grounded (3 real `repo_tool` runs, subsets 1-3 counts); turn 2 = tool-grounded (4 more reads, subsets 4-5). Post-code SIGN = 7 real `repo_tool` runs at HEAD. Not rubber-stamp.
- `feedback_zoom_out_ask_per_rigby_sign` fired 2× — pre-code (Fold 3 V4 = 2nd trigger); post-code (Fold B V4 = 3rd trigger). V4 accreting real trigger count.
- `feedback_read_full_rigby_response_not_just_tail` — pre-code SIGN turn 1 was persisted to `bo6d5g9x5.txt` because output exceeded 40KB; Claude read partial via `preview` field, missed Rigby's explicit tool-run offer at the §1 tail. **Chris caught the gap and directed the follow-up.** Post-code SIGN also truncated mid-Fold-A; Claude re-routed for §5 tail + §6 without asking Rigby to re-run tool checks (per Chris's improved pattern — "use your own tools to read persisted stdout instead of round-tripping Rigby").
- `feedback_claude_stdout_truncation_vs_ui_truncation` — recognized both times that Chris's UI likely has the full response; Claude re-fetched for its own execution context, not because Chris was missing content.
- `feedback_claude_directs_rigby_then_verifies` — Claude directed narrow tool-grounded verification (per-site with line numbers + specific taxonomy checks + no-partial-migration audit per action); Rigby executed with quoted evidence; Claude verified via git log HEAD sha match.
- `feedback_claude_rigby_agree_first_chris_yes_no` — pre-code SIGN F-BLOCKING gap (subsets 4-5 unverified) resolved between Claude+Rigby BEFORE Chris D-verdict. Chris got 1 recommendation (subsets 1+4+5), not a menu.
- `feedback_engineering_bias_over_audit` — net-new engineering ship (7-site migration + 7-row regression + Ledger update).
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=e6ae8a1b3a59, surviving=none`).
- `feedback_local_truth_no_production` — 174/174 local pass IS the deploy step.
- `feedback_rigby_writes_workspace_deliverables` — Ledger #22 update via Rigby PA at close (+2,730 chars appended to `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`; total now 37,978 chars).
- `feedback_gh_pr_merge_admin_until_billing_fixed` — merged PR #3383 with `--admin` flag.
- `feedback_per_pr_summary_signals_close_readiness` — mid-flight per-PR summary to Chris with "still open before close" checklist (Rigby SIGN + Ledger + handoff + 00-START + wrapper bump + docs cascade + final recycle).

### Rigby Tool Gap Ledger updates (via Rigby PA)

Deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (status `ready`, +2,730 chars → total 37,978 chars):

- **#22 progress:** 7 sites migrated. Legacy-file population S2879=37 → **S2880=30**. Ops file down 7. Governance file still fully clean (from S2879).
- **NEW Fold A** — criticality-first cadence pacing trap watch. 2nd trigger.
- **NEW Fold B** — V4 normalization utility lever. 3rd trigger. Threshold event.
- **NEW Fold C** — two-helper coexistence coupling. 2nd trigger.
- **NEW Fold D** — governance-in-ops routing boundary drift. 2nd trigger.

Session pin `pa-73d2689f9e8c4e7c` (labeled `s2879-governance-ops-critical-slice`; carried across S2880 in-place) **RETIRES at S2880 close**. Fresh mint required at S2881 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## For S2881 open

See `00-START-NEXT-SESSION.md` (refreshed at S2880 close). Key open questions:
- Is Fold B (V4 normalization utility) ready to promote to a 4th trigger and become the S2881 slate driver, or does criticality-first cadence continue into Subset 2 (write-path) or Subset 3 (agent-diag)?
- Does S2881 explicitly label handler-surface vs autopilot-engine-internal work (Fold D)?
- Does taxonomy discipline get widened beyond ops surfaces (Fold C)?
