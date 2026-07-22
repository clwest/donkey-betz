# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2880 CLOSE → `ops_tool` remainder critical-slice structured error-envelope migration shipped (2026-07-21; picks up as S2881) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2880 close).** S2880 was the second CRITICALITY-FIRST handler migration slate. Continued S2879 cadence into 3 additional bounded ops subsets in a single PR.

- **PR #3383** `e6ae8a1b3a59` — S2880 slate (2 files, +209/-7)
  - **`_handle_autopilot` governance kill-switch cluster** (`core/services/td_handlers_ops.py:3562-3618`): 3 sites migrated (`governance_set_mode` / `governance_kill_switch` / `governance_deactivate_switch`). All `invalid_params`. **Slate-open framing correction:** these actions dispatch via `autopilot_tool`, not `ops_tool` — verified during test authoring, re-recorded as post-code Fold D (2nd trigger, routing boundary drift).
  - **`_handle_scheduled_tasks` enable/disable cluster** (`core/services/td_handlers_ops.py:5999-6018`): 2 sites migrated. Missing task_id → `invalid_params` (action=runtime variable). Task not found → `not_found` (action=runtime variable). Rigby condition #4 satisfied (both error paths in enable/disable action migrated together).
  - **`_handle_ops_digest` post + local fallback** (`core/services/td_handlers_ops.py:5276-5324`): 2 sites migrated. Missing conversation_id in `post` branch → `invalid_params`. Unknown-action fallback → `unknown_action` (action=runtime variable).
  - **Reused S2879 `_handler_error` helper** at `td_handlers_ops.py:48` — no new helper added. Fold B (V4 normalization utility) reached 3rd trigger at post-code SIGN.
  - **New test file** `core/tests/test_s2880_ops_remainder_error_envelope.py` — 7 rows exercising full `ToolDispatcher.execute_sync` path across 3 tools (`autopilot_tool` / `scheduled_tasks_tool` / `ops_digest_tool`). Reuses the S2879 module-level `_assert_migrated_envelope` helper (single-source contract).
  - No S2877 backfill-suite deletions needed — verified none of the S2880 migrated actions were covered in `LegacyBackfillPASurfaceTests`.
  - Combined regression (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877 + S2878 + S2879 + **S2880** + `test_zoom_out_tool_2780`): **174/174 pass**.

### Why criticality-first continued at S2880

Rigby pre-code SIGN ranked the 5 candidate subsets by (i) incident-loop blast radius, (ii) operator-debugging frequency, (iii) PR size / mutation risk. Winners for a single small PR: kill-switch (worst blast radius under incident pressure) + scheduled-task (bounded beat mutations) + ops-digest post (operator-facing, actionable errors). Deferred: write-path (11 mutation-risk sites), agent-diag (8+ sites, larger diff). Tool-grounded site counts corrected pre-code priors (kill-switch: 3 vs assumed ~4; scheduled-task: 2 vs unverified; ops-digest: 2 vs unverified).

### 4 post-code zoom-out folds (Fold B is 3rd-trigger threshold event)

Recorded in Rigby Tool Gap Ledger #22 (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`, +2,730 chars appended at S2880 close, total 37,978 chars):

1. **Fold A (2nd trigger)** — Criticality-first cadence stays valid *if* remaining slates stay clusterable + bounded. If next remainder is diffuse (many unrelated actions, scattered sites), criticality-first becomes a pacing trap.
2. **Fold B (3rd trigger)** — V4 normalization utility / mechanical normalizer becomes a real accumulating lever. Prior triggers: S2879 post-code + S2880 pre-code + S2880 post-code. Rigby recommends: don't do N more 5-10 site PRs if the ~30 bare-return remainder is diffuse; a safe mechanical normalizer with guardrails/tests likely dominates on total risk/effort. **NOT the same axis as the 6-adopter `_tool_error → td_error.py` extraction gate** (that stays deferred).
3. **Fold C (2nd trigger)** — Two-helper coexistence (`_tool_error` 3-key + `_handler_error` 4-key) is stable but coupling risk rising if `_handler_error` keeps spreading only in ops surfaces.
4. **Fold D (2nd trigger)** — Governance actions dispatch via `autopilot_tool` (correction from `ops_tool` pre-code assumption); S2881 slates should explicitly label handler-surface vs autopilot-engine-internal work.

## PRIOR SESSION — S2879 close (`governance_tool` + `ops_tool` critical-slice)

- **PR #3381** `9a3039e22e69` — S2879 slate (4 files, +279/-32) — first criticality-first handler migration slate in the S2876 backfill sunset arc. Governance file dropped OUT of legacy population entirely (0 remaining bare returns). Ops file 7 sites in critical slice migrated. See `docs/handoffs/SESSION_2879_GOVERNANCE_OPS_CRITICAL_SLICE.md`.

**Working loop observations at S2880:**
- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code SIGN 2 grounded turns; post-code SIGN 7 real `repo_tool` runs at HEAD. Not rubber-stamp.
- `feedback_zoom_out_ask_per_rigby_sign` fired 2× — pre-code (Fold 3 V4 = 2nd trigger) + post-code (Fold B V4 = 3rd trigger). V4 threshold event.
- `feedback_read_full_rigby_response_not_just_tail` — pre-code SIGN turn 1 stdout persisted to `bo6d5g9x5.txt`; Claude missed Rigby's tool-run offer at §1 tail. **Chris caught the gap and directed follow-up.** Post-code SIGN also truncated mid-Fold-A; Claude recovered via narrow re-emit ask (§5 tail + §6 only, no tool_runs needed).
- `feedback_claude_stdout_truncation_vs_ui_truncation` — both truncations were Claude-stdout only; Chris's UI likely had full content.
- Chris pattern improvement (S2880 mid-session): "use your own tools to read persisted stdout files instead of round-tripping Rigby for truncated content." Adopted.
- `feedback_claude_directs_rigby_then_verifies` — Claude directed per-site + taxonomy + no-partial-migration + helper-reuse checks with concrete line numbers; Rigby executed with quoted evidence; Claude verified HEAD sha.
- `feedback_claude_rigby_agree_first_chris_yes_no` — pre-code F-BLOCKING gap resolved between Claude+Rigby before Chris D-verdict.
- `feedback_engineering_bias_over_audit` — net-new engineering ship.
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=e6ae8a1b3a59, surviving=none`).
- `feedback_local_truth_no_production` — 174/174 local pass IS the deploy step.
- `feedback_rigby_writes_workspace_deliverables` — Ledger update via Rigby PA at close.
- `feedback_gh_pr_merge_admin_until_billing_fixed` — merged PR #3383 with `--admin` flag.
- `feedback_per_pr_summary_signals_close_readiness` — mid-flight per-PR summary with "still open before close" checklist delivered.

**Rigby Tool Gap Ledger updates (via Rigby PA per `feedback_rigby_writes_workspace_deliverables`):**
- Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (status `ready`, +2,730 chars → total 37,978 chars)
- **#22 (S2876 backfill sunset progress)** → 7 sites migrated across 3 subsets. Legacy-file population S2879=37 → **S2880=30** (ops file down 7). Governance file still fully clean (0 bare returns from S2879).
- **NEW Fold A** — criticality-first cadence pacing trap watch. 2nd trigger.
- **NEW Fold B** — V4 normalization utility. **3rd trigger threshold event.**
- **NEW Fold C** — two-helper coexistence coupling. 2nd trigger.
- **NEW Fold D** — governance-in-ops routing boundary drift. 2nd trigger.

**Session pin `pa-73d2689f9e8c4e7c` RETIRES at S2880 close.** Fresh mint required at S2881 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2881 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

Wrapper pin rewritten at S2880 close (this PR's cascade). If needed at S2881 open:

```bash
python manage.py session_lifecycle close --label s2881-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — S2881 primary lever DECISION POINT — Fold B is at 3rd trigger

Two paths to route through Rigby pre-code SIGN + Chris D-verdict:

**Path A — Continue criticality-first cadence.** Next slate would be either:
- **Subset 2 (write-path, 11 sites)** — `draft_*` / `close_pack_*` / `meeting_*` / `event_reply` at L3312-3533. Mutation-risk surface. Rigby ranked #3 at S2880 pre-code (behind kill-switch + agent-diag) due to size + mutation risk. Would require careful no-partial-migration verification per action.
- **Subset 3 (agent-diag, 8+ sites)** — `agent_memory` / `heartbeat_history` / `infra_health` / `pa_diag`. Read-only diagnostic surfaces. Rigby ranked #2 at S2880 pre-code. Larger diff than S2880 but low behavioral risk.

**Path B — Pivot to V4 normalization utility.** Fold B reached 3rd trigger at S2880 post-code (S2879 post + S2880 pre + S2880 post). Rigby recommends: "don't do N more 5-10 site PRs if the ~30 bare-return remainder is diffuse; a safe mechanical normalizer with guardrails/tests likely dominates on total risk/effort." Would look like:
- A ToolDispatcher post-processing shim that detects bare `{'error': ...}` returns from unmigrated handlers and normalizes them to the S2874 envelope shape (`success=False`, `error_code='legacy_error'` or a more specific default, `action` from dispatch context).
- Would NOT touch the source sites (unlike direct migration); would provide contract-compliant output at the dispatcher boundary while source sites drift naturally over time.
- Distinct axis from the 6-adopter `_tool_error → td_error.py` extraction gate — that's about consolidating existing helpers; this is about wrapping unmigrated returns.

**Recommended pre-code SIGN questions:**
- Rigby: audit the remaining ~30 bare-return sites for cluster vs diffuse pattern. If clusterable → Path A viable. If diffuse → Path B may dominate.
- Rigby: for Path B, sketch the normalizer shim shape (single function at `ToolDispatcher.execute_sync` output? Middleware layer?). Confirm it wouldn't collide with `_tool_error` or `_handler_error` shapes already in use.
- Chris: D-verdict between Path A and Path B (or a Path A+B hybrid where the normalizer is authored but criticality-first migration continues in parallel).

### Step 3 — Net-new engineering candidates for S2881 (broader list)

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2880 close — S2881 primary slate driver: DECISION between Path A (criticality-first cadence continuation) and Path B (V4 normalization utility pivot)** (see §Step 2).

2. **NEW at S2880 close — Fold D driven S2881 preflight: label whether next slate touches (a) handler surface, (b) autopilot/engine internals, or (c) both.** Reduces routing-boundary drift risk.

3. **Carried from S2879 close — 4 zoom-out folds (V1-V4) — some now upgraded via S2880 post-code re-observation.** V4 is now Fold B 3rd trigger (see Path B). V1/V2/V3 remain 1st trigger from S2879.

4. **Carried from S2878 close — `_s2876_fake_tool` breadcrumb noise refinement** (1st trigger). NOT ready to slate.

5. **Carried from S2877 close — Schema-level dead-branch investigation** (1st trigger from S2875). Audit which handler branches are unreachable via PA tool schema enum constraints.

6. **Carried from S2877 close — Schema-layer PA route smoke extension** — dispatch via PA endpoint to catch schema-blocked payloads.

7. **Carried from S2876 close — #22.3 orthogonal-contract-axes resolution** (still 1st trigger).

8. **Carried from S2877 close — #22.4 Rigby dispatcher-probe extension** (still 1st trigger).

9. **Carried from S2874/S2875 — Extract `td_error.py` gateway-layer helper.** Still gated on Rigby's 6-adopter empirical-stability signal for `_tool_error`. Distinct axis from Fold B (V4 normalizer).

10. **Carried from S2874 — `feedback_recycle_after_merge` extension for multi-checkout setups** (still 1st trigger).

11. **Carried from S2873 — `orm_inspect_tool` JSONField type predicate** (1st trigger).

12. **Carried from S2873 — kalshi-only distribution on canonical SpiderData** (1st trigger).

13. **Carried from S2873 — "post-allowlist smoke checklist" UX pattern** (1st trigger).

14. **Ledger #5 — schema/handler drift detection lint / CI wiring** (~2 hr). Command exists at `core/management/commands/check_pa_tool_drift.py` (S2846-authored, 403 lines) but never wired to CI enforcement.

15. **Carried from S2872 — Category B cosmetic `raw_data_dict` migration** (~30 min).

16. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863).

17. **Carried — Exemption-list telemetry** (Rigby zoom-out from S2868 slate #1, 1st trigger).

18. **Carried — Stale-cleared row GC** (Rigby zoom-out from S2868 slate #1).

19. **Carried — `group_key_note` UX hint on `count_by`** (S2867 Q2 fold, 1st trigger).

20. **Carried — High-cardinality guardrail on `count_by`** (S2867 Q5 fold, 1st trigger).

21. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, 1st trigger).

22. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Still 2 independent triggers, not promoted.

23. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate, 1st trigger only).

24. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

25. **Carried — `simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold).

26. **Carried — `enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

27. **Carried — `actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required).

28. **Carried — `EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

29. **Carried — `list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

30. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859+S2868 cycle observed).

31. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

32. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

33. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

34. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

35. **Carried — Middleware `log_injected_params` spec candidate** (S2870 Q6 zoom-out fold, 1st trigger).

36. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

37. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2875 → S2876 → S2877 → S2878 → S2879 → **S2880 (ops-remainder critical slice)**. See A4 Constraints below.

38. **Carried — Character-os Rigby integration (5-gap analysis from S2872 mid-session, D6 moratorium hold)** — parked; unlock requires Chris directive.

### What's forbidden at S2881 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2880 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2880: kill-switch (3 sites) + scheduled-task (2 sites) + ops-digest (2 sites) now emit structured `error_code` values. Third real-handler migration wave in the S2876 sunset arc, second criticality-first. A4 outreach substrate now has structured error semantics on the operator-facing incident-response surfaces (governance safe-mode + beat mutation + digest posting), extending prior S2879 coverage of governance zoom-out + ops focus_mode/celery/tenant/staleness.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(mm) as ratified at S2879 close. **(nn) autopilot `governance_set_mode` / `governance_kill_switch` / `governance_deactivate_switch` + `scheduled_tasks_tool` enable/disable + `ops_digest_tool` post + local unknown-action now emit concrete `error_code` values from the 4-code taxonomy (`invalid_params` / `not_found` / `unknown_action`). Third wave in the S2876 sunset arc, second criticality-first. A4 messaging that references operator-facing incident-response observability (safe-mode toggles, kill-switch activation, beat schedule enable/disable) can rely on structured error semantics for downstream integrations.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2880 close — what shipped (one PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3383** `e6ae8a1b3a59` — S2880 slate: ops_tool remainder critical-slice error-envelope migration (2 files, +209/-7)
- **PR `<this docs cascade>`** — S2880 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2881 open

**Workspace canonical:** Rigby Tool Gap Ledger updated via Rigby PA per `feedback_rigby_writes_workspace_deliverables` (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`, +2,730 chars appended, total 37,978 chars).

**Runtime impact:**
- Third wave of real handler migrations in the S2876 backfill sunset arc, second criticality-first. Legacy-file population S2879=37 → **S2880=30**. Ops file remains IN the population with ~30 bare returns.
- Regression suite grew from 167 → 174 (+7 S2880 rows).
- 3 governance kill-switch + 2 scheduled-task + 2 ops-digest sites no longer surface `error_code='legacy_error'`; consumers can key on the 4-code S2879 taxonomy.
- No new helper introduced — S2879 `_handler_error` reused for all 7 sites.

**Not shipped at S2880 close (deferred to S2881 or later):**
- S2881 primary slate decision (Path A criticality-first vs Path B V4 normalizer pivot)
- Fold A/C/D from S2880 post-code — all 2nd trigger, watch for third
- All prior deferred items from S2879/S2878/S2877/S2876/S2874/S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc still carried

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2880)

See:
- **S2880 handoff (current):** `docs/handoffs/SESSION_2880_OPS_REMAINDER_CRITICAL_SLICE.md`
- **S2879 handoff:** `docs/handoffs/SESSION_2879_GOVERNANCE_OPS_CRITICAL_SLICE.md`
- **S2878 handoff:** `docs/handoffs/SESSION_2878_BPAAS_ERROR_ENVELOPE.md`
- **S2877 handoff:** `docs/handoffs/SESSION_2877_PA_SURFACE_ERROR_CODES_SMOKE.md`
- **S2876 handoff:** `docs/handoffs/SESSION_2876_DISPATCHER_ERROR_CODE_BACKFILL.md`
- **S2875 handoff:** `docs/handoffs/SESSION_2875_CROSS_TOOL_ERROR_ENVELOPE.md`
- **S2874 handoff:** `docs/handoffs/SESSION_2874_REPO_TOOL_READ_FILE_PAGING.md`
- **S2873 handoff:** `docs/handoffs/SESSION_2873_ORM_INSPECT_SPIDER_DATA_OPPORTUNITY.md`
- **S2872 handoff:** `docs/handoffs/SESSION_2872_RAW_DATA_DICT_SWEEP_LEDGER_22B_TELEMETRY.md`
- **S2871 handoff:** `docs/handoffs/SESSION_2871_RAW_DATA_DICT_PROPERTY_ORM_INSPECT_LEGACY_SPIDER_DATA_CONDITIONAL_TIMEOUT.md`
- **S2870 handoff:** `docs/handoffs/SESSION_2870_INJECTION_HARDENING_AND_RAW_DATA_GUARD.md`
- **S2869 handoff:** `docs/handoffs/SESSION_2869_SPIDER_SEARCH_PREVIEW_AND_SIGNAL_CLUSTERS_MULTISOURCE.md`
- **S2868 handoff:** `docs/handoffs/SESSION_2868_DELIVERABLE_DIAGNOSTIC_AND_SPIDER_STATUS_PAGINATION.md`
- **S2867 handoff:** `docs/handoffs/SESSION_2867_ORM_COUNT_BY.md`
- **S2866 handoff:** `docs/handoffs/SESSION_2866_ORM_INSPECT_TOOL.md`
- **S2865 handoff:** `docs/handoffs/SESSION_2865_WEB_FETCH_TOOL.md`
- **S2864 handoff:** `docs/handoffs/SESSION_2864_HF_BACKFILL_VIEW_CLEANUP.md`
- **S2863 handoff:** `docs/handoffs/SESSION_2863_HF_HUB_API_SORT_DOWNLOADS.md`
- **S2862 handoff:** `docs/handoffs/SESSION_2862_HUGGINGFACE_SIGNAL_EXTRACTION_FIX.md`
- **S2861 handoff:** `docs/handoffs/SESSION_2861_AUTOPILOT_SELECTED_FIELDS_SHIPPED.md`
- **S2860 handoff:** `docs/handoffs/SESSION_2860_DELIVERABLE_TOOL_DELETE_SHIPPED.md`
- **S2859 handoff:** `docs/handoffs/SESSION_2859_DELIVERABLE_TOOL_GOTCHAS_LEDGER_8_9_SHIPPED.md`
- **S2858 handoff:** `docs/handoffs/SESSION_2858_CLEAR_STATUS_CONTEXT_AND_LIST_CAPS_N1_SHIPPED.md`
- **S2857 handoff:** `docs/handoffs/SESSION_2857_SIMULATE_ENFORCEMENT_SHIPPED.md`
- **S2856 handoff:** `docs/handoffs/SESSION_2856_AUTOPILOT_HISTORY_EVIDENCE_AND_ENFORCEMENT_SPLIT_SHIPPED.md`
- **S2855 handoff:** `docs/handoffs/SESSION_2855_PRICING_CANON_PHASE_2A_SHIPPED.md`
- **S2854 handoff:** `docs/handoffs/SESSION_2854_PRICING_CANON_PHASE_1_SHIPPED.md`
- **S2853 handoff:** `docs/handoffs/SESSION_2853_W2_3_2_DOWNGRADE_SAVINGS_SHIPPED.md`
- **S2852 handoff:** `docs/handoffs/SESSION_2852_LIST_CAPS_AUTH_TIGHTENED.md`
- **S2851 handoff:** `docs/handoffs/SESSION_2851_A1_W2_3_1_ENFORCEMENT_REPORT_SHIPPED.md`
- **S2850 handoff:** `docs/handoffs/SESSION_2850_A1_W2_ENFORCEMENT_CORRECTNESS_LEG.md`
- **S2849 handoff:** `docs/handoffs/SESSION_2849_A1_W2_DEFAULTS_BACKFILL_SHIPPED.md`
- **S2848 handoff:** `docs/handoffs/SESSION_2848_A1_W1_5_DOWNGRADE_TIER_SHIPPED.md`
- **S2847 handoff:** `docs/handoffs/SESSION_2847_A1_W1_PHASE3_SHIPPED.md`
- **S2846 handoff:** `docs/handoffs/SESSION_2846_A1_W1_PHASE1_PHASE2_SHIPPED.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
