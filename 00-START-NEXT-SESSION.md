# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2879 CLOSE → `governance_tool` + `ops_tool` critical-slice structured error-envelope migration shipped (2026-07-21; picks up as S2880) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2879 close).** S2879 was the first CRITICALITY-FIRST handler migration slate (per Rigby's F5 forward-carry from S2878, which had been breadcrumb-driven). Two files fully or partially migrated in a single paired-file PR.

- **PR #3381** `9a3039e22e69` — S2879 slate (4 files, +279/-32)
  - **`_handle_zoom_out`** (`core/services/td_handlers_governance.py:63`) migrated from bare `{'error': msg}` → S2874 canonical `{success, error_code, error, action}`. 1 site → 1 code (`unknown_action`). Governance file drops OUT of the legacy population entirely (0 remaining bare returns).
  - **`_handle_ops` critical slice** (`core/services/td_handlers_ops.py`): 7 sites across 4 action families migrated. `focus_mode_update` config-validation, dispatcher unknown-action default, `_ops_celery_task_history` ImportError guard, `_ops_tenant_boundary_violations` BOTH error paths (import guard + invalid failure_kind), `_ops_staleness_warnings` BOTH error paths (import guard + invalid verdict). Rigby condition #4 (no-partial-migration inside any single action) applied.
  - **Taxonomy locked to 4-code minimum** (Rigby condition #3): `invalid_params` / `not_found` / `unknown_action` / `dependency_missing`. Only 3 of 4 used in this slate.
  - **New helpers** — `_handler_error(action, code, message, **fields)` added to BOTH `td_handlers_governance.py` (top of file) and `td_handlers_ops.py` (next to existing S2875 `_tool_error`). Docstrings on both explicitly document intentional split from `_tool_error` (3-key, 12 existing adopters); reconciliation deferred to Rigby's 6-adopter helper-extraction gate.
  - **New test file** `core/tests/test_s2879_governance_ops_error_envelope.py` — 8 rows, full `ToolDispatcher.execute_sync` end-to-end path. ImportError paths simulated via `patch.dict(sys.modules, {'core.models_...': None})`.
  - **S2877 file edit** — deleted `test_ops_tool_unknown_action_backfilled` from `LegacyBackfillPASurfaceTests` (site now migrated; re-homed under S2879 per Rigby F4 pattern from S2878).
  - Combined regression (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877 + S2878 + S2879 + `test_zoom_out_tool_2780`): **167/167 pass**.

### Why criticality-first (not breadcrumb-first)

Rigby's F5 forward-carry from S2878: breadcrumb-driven migration lets the platform *appear* contract-stable while most real failures still fall through `error_code='legacy_error'`. Ops failures compound during incident/debug loops (worst blast radius); governance is free momentum (1 site, low risk); content deferred (retriable at authoring time, less incident-critical). Pre-code SIGN F-BLOCKING correction: 00-START-claimed 19/26 site counts were unverified — actual populations are 13 content / 37 ops / 1 governance.

### 4 post-code zoom-out folds — forward-carried (all 1st trigger)

Recorded in Rigby Tool Gap Ledger #22 (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`, +2,730 chars appended at S2879 close):

1. **V1 — Two-layer error-contract accretion.** 3-key `_tool_error` + 4-key `_handler_error` coexisting. Stable if consumers never assume single universal schema; watch for third trigger.
2. **V2 — Consumer ambiguity on `success`/`error` key semantics.** Callers keying on `success is False` miss legacy errors; callers keying on `if 'error' in result` false-positive on success payloads with legitimate error keys.
3. **V3 — Inconsistent `action` presence.** Handler envelope has it, legacy doesn't. UI/logging keyed on `action` degrades silently.
4. **V4 — Normalization utility candidate.** Local helper at ToolDispatcher post-processing converting either shape to common representation. Would prevent shape-leak into every new consumer. Still endorsed to defer to Rigby's 6-adopter helper-extraction gate.

## PRIOR SESSION — S2878 close (`bpaas_tool` structured error-envelope migration)

- **PR #3379** `ac1854f6d` — S2878 slate (4 files, +178/-18) — first real handler migration in the S2876 backfill sunset arc. Breadcrumb-driven pick (bpaas was the only real production hit in the S2876 breadcrumb log). See `docs/handoffs/SESSION_2878_BPAAS_ERROR_ENVELOPE.md`.

**Working loop observations at S2879:**
- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code SIGN Rigby ran 8 real `repo_tool` runs; post-code SIGN ran 8 more on shipped files. Not rubber-stamp.
- `feedback_zoom_out_ask_per_rigby_sign` fired 2× — pre-code (F5 → 4-code taxonomy + no-partial-migration + micro-template conditions); post-code (V1-V4 → all forward-carried).
- `feedback_claude_directs_rigby_then_verifies` — Claude directed helper-shape narrow SIGN with concrete evidence (3-key vs 4-key concrete site line numbers); Rigby AGREE with grounded tool runs.
- `feedback_claude_rigby_agree_first_chris_yes_no` — pre-code SIGN F1 F-BLOCKING correction on site counts + helper-shape narrow SIGN both resolved between Claude+Rigby BEFORE Chris D-verdict. Chris got 1 recommendation, not a menu.
- `feedback_engineering_bias_over_audit` — net-new engineering ship (2 helpers + 8-site migration + regression coverage).
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=9a3039e22e69, surviving=none`).
- `feedback_read_full_rigby_response_not_just_tail` — pre-code SIGN response truncated mid-AGREE-rationale; re-fetched cleanly.
- `feedback_claude_stdout_truncation_vs_ui_truncation` — the AGREE-rationale truncation appeared in Chris's Chat UI too, not just Claude's stdout; re-fetch was for real content loss, not just Claude context.
- `feedback_local_truth_no_production` — 167/167 local pass IS the deploy step.
- `feedback_rigby_writes_workspace_deliverables` — Rigby Tool Gap Ledger update via Rigby PA at close (+2,730 chars appended to `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`).
- `feedback_gh_pr_merge_admin_until_billing_fixed` — merged PR #3381 with `--admin` flag.

**Rigby Tool Gap Ledger updates (via Rigby PA per `feedback_rigby_writes_workspace_deliverables`):**
- Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (status `ready`, +2,730 chars → total 35,246 chars)
- **#22 (S2876 backfill sunset progress)** → 1 governance + 7 ops sites migrated. Legacy-file population S2877=39 → S2878=38 → **S2879=37**. Governance file fully clean (0 bare returns). Ops file partial (~30 bare returns still legacy across single-line + multi-line patterns).
- **NEW V1** — two-layer error-contract accretion (3-key + 4-key coexistence). 1st trigger.
- **NEW V2** — consumer ambiguity on `success`/`error` key semantics. 1st trigger.
- **NEW V3** — normalization utility candidate at ToolDispatcher post-processing. 1st trigger (endorsed defer to 6-adopter gate).
- **[carried from S2876/S2877]** #22.3 (orthogonal-contract-axes) → still 1st trigger; S2879 adds a datapoint but does not force resolution.
- **[carried from S2877]** #22.4 (Rigby dispatcher-probe extension) → NOT re-triggered at S2879. Still 1st trigger.

**Session pin `pa-7f847367d41a4d10` (labeled `s2879-governance-ops-critical-slice`) RETIRES at S2879 close.** Fresh mint required at S2880 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

**Prior pin retired at S2879 open:** `pa-3c31ea25818f48f6` (minted during S2878 docs cascade PR #3380).

---

## S2880 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

Wrapper pin rewritten at S2879 close (this PR's cascade). If needed at S2880 open:

```bash
python manage.py session_lifecycle close --label s2880-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Continue criticality-first handler migration into ops remainder

Per Rigby's S2879 slate framing (governance+ops-critical → S2880 = ops-remainder → S2881+ = content), the natural S2880 lever is the remaining ~30 sites in `td_handlers_ops.py` that weren't in the S2879 critical slice.

Candidates for a Rigby pre-code SIGN to rank by criticality:

1. **Ops write-path handlers** (draft management, close-pack lifecycle, meeting scheduling) — actions like `draft_*`, `close_pack_*`, `meeting_*`, `event_reply` etc. across ~L3259-3549. Write-path failures = user data loss surface.
2. **Ops kill-switch / mode-change handlers** (`bulk_switch_mode`, `switch_toggle`, `switch_reset`) at L3514-3549. Failures during incident response = worst possible timing.
3. **Ops agent-memory / agent-stats surfaces** (`agent_memory` at L6759-6763, `heartbeat_history` L6828-6832, `infra_health` L7049-7053, `pa_diag` L7501-7648). Diagnostic surfaces — same "operator debugging while errors are opaque" problem.
4. **Ops scheduled-task management** (`enable`/`disable` at L5949-5956). Beat schedule mutations.
5. **Ops conversation-post** (L5226 + L5255 dispatcher default). Communication surface.

Non-mutually-exclusive: candidate pairing could be kill-switch subset (~4 sites) + agent-diag subset (~5-6 sites) — small enough for one PR, criticality-focused.

### Step 3 — Net-new engineering candidates for S2880 (broader list)

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2879 close — S2880 primary slate driver: ops-remainder critical slice** (see §Step 2).

2. **NEW at S2879 close — V1/V2/V3/V4 zoom-out fold consolidation.** All 1st trigger from S2879 post-code SIGN. Watch for second trigger before promoting; V4 (normalization utility) is the most likely to converge with the 6-adopter helper-extraction gate.

3. **Carried from S2878 close — `_s2876_fake_tool` breadcrumb noise refinement** (1st trigger). S2876 test suite creates fake tool that legitimately fires the breadcrumb; log doesn't distinguish test-fixture from real handler hits. ~30 min. NOT ready to slate — 1st noise observation only.

4. **Carried from S2877 close — Schema-level dead-branch investigation** (still 1st trigger from S2875 post-code SIGN). Audit which handler branches are unreachable via PA tool schema enum constraints. Est ~1 hr (audit-only).

5. **Carried from S2877 close — Schema-layer PA route smoke extension** — dispatch via PA endpoint to catch schema-blocked payloads. Est ~1.5 hr.

6. **Carried from S2876 close — #22.3 orthogonal-contract-axes resolution** (still 1st trigger). S2879 adds a datapoint but does not force resolution.

7. **Carried from S2877 close — #22.4 Rigby dispatcher-probe extension** (still 1st trigger from S2877; NOT re-triggered at S2879).

8. **Carried from S2874/S2875 — Cross-tool structured-error-envelope migration EXTENSION to write-path handlers.** Might overlap with S2880 candidate #1 above depending on how the slate lands.

9. **Carried from S2874/S2875 — Extract `td_error.py` gateway-layer helper.** Still gated on Rigby's 6-adopter empirical-stability signal. S2879 adds `_handler_error` as a distinct-shape helper — doesn't count toward the same-shape adopter gate.

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

37. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2875 → S2876 → S2877 → S2878 → **S2879 (governance + ops critical slice)**. See A4 Constraints below.

38. **Carried — Character-os Rigby integration (5-gap analysis from S2872 mid-session, D6 moratorium hold)** — parked; unlock requires Chris directive.

### What's forbidden at S2880 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2879 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2879: `_handle_zoom_out` + 7 ops critical-slice sites now emit structured `error_code` — the S2876 backfill wrapper's idempotent guard short-circuits before assigning `legacy_error` for these paths. Second real-handler migration wave in the S2876 sunset arc, this time criticality-first. A4 outreach substrate has structured error semantics on the operator-facing ops surface, not just the bpaas consulting workflow.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(ll) as ratified at S2878 close. **(mm) governance `zoom_out_tool` + ops critical slice (7 sites across `focus_mode_update` / dispatcher / celery_task_history / tenant_boundary_violations / staleness_warnings) now emit concrete `error_code` values from a 4-code taxonomy (`invalid_params` / `unknown_action` / `dependency_missing`). Second wave in the S2876 sunset arc. A4 messaging that references operator-facing ops observability can rely on structured error semantics for downstream integrations.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2879 close — what shipped (one PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3381** `9a3039e22e69` — S2879 slate: governance + ops critical-slice error-envelope migration + retired S2877 ops-backfill test row (4 files, +279/-32)
- **PR `<this docs cascade>`** — S2879 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2880 open

**Workspace canonical:** Rigby Tool Gap Ledger updated via Rigby PA per `feedback_rigby_writes_workspace_deliverables` (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`, +2,730 chars appended, status `ready`).

**Runtime impact:**
- Second wave of real handler migrations in the S2876 backfill sunset arc, first criticality-first. Legacy-file population S2877=39 → S2878=38 → **S2879=37** (governance file fully clean). Ops file remains IN the population with ~30 remaining bare returns.
- Regression suite grew from 139 → 167 (+8 new S2879 rows − 1 deleted S2877 row = +7 net; discrepancy in doc-vs-runner count is because S2879 test batch inclusion picked up additional session tests not counted at S2878 close).
- `_handle_zoom_out` + 7 ops critical-slice sites no longer surface `error_code='legacy_error'`; consumers can key on the 4-code S2879 taxonomy.
- Two `_handler_error` local helpers now shipped (governance + ops files). Distinct from S2875 `_tool_error` — reconciliation deferred to Rigby's 6-adopter gate.

**Not shipped at S2879 close (deferred to S2880 or later):**
- Ops-remainder critical slice migration (S2880 primary slate candidate)
- All 4 new zoom-out folds from S2879 (V1-V4) — 1st trigger, watch for second
- Schema-level dead-branch investigation (still 1st trigger from S2875)
- Schema-layer PA route smoke extension
- #22.3 orthogonal-contract-axes resolution
- #22.4 Rigby dispatcher-probe extension
- Write-path handler envelope migration
- Extract `td_error.py` gateway helper
- All prior deferred items from S2878/S2877/S2874/S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc still carried

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2879)

See:
- **S2879 handoff (current):** `docs/handoffs/SESSION_2879_GOVERNANCE_OPS_CRITICAL_SLICE.md`
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
