# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2881 CLOSE → `autopilot_tool` write-path critical-slice structured error-envelope migration shipped (2026-07-21; picks up as S2882) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2881 close).** S2881 was the third CRITICALITY-FIRST handler migration slate. Continued S2879/S2880 cadence into the contiguous write-path block in a single PR.

- **PR #3385** `0c26d8564` — S2881 slate (2 files, +196/-11)
  - **Write-path contiguous block** (`core/services/td_handlers_ops.py:3312-3533`, all inside `_handle_autopilot`): **11 sites migrated across 4 action-families**:
    - `outreach_approve` / `outreach_reject` — `draft_id` guards (2 sites, `invalid_params`)
    - `close_pack_generate` / `close_pack_approve` — `price` / `pack_id` guards (2 sites, `invalid_params`)
    - `engagement_classify` / `engagement_draft_reply` / `engagement_approve_reply` / `engagement_disqualify` — `event_id` / composite guards (4 sites, `invalid_params`)
    - `meeting_create` / `meeting_brief` / `meeting_recap` — `scheduled_at` / `meeting_id` guards (3 sites, `invalid_params`)
  - **Fold D 3rd-trigger THRESHOLD EVENT mid-slate:** Pre-code framing labeled slate as `ops_tool` handler-surface; all 11 test rows initially failed with `unknown_action` because write-path actually lives inside `_handle_autopilot` (registered `autopilot_tool` at `tool_dispatcher.py:538`). Same routing-boundary drift Rigby caught in S2880 governance cluster. Test dispatcher corrected → 11/11 pass.
  - **Reused S2879 `_handler_error` helper** at `td_handlers_ops.py:48` — no new helper added.
  - **New test file** `core/tests/test_s2881_ops_write_path_error_envelope.py` — 11 rows exercising full `ToolDispatcher.execute_sync` path via `autopilot_tool`. Reuses S2879 `_assert_migrated_envelope` helper (single-source contract).
  - Combined regression (S2869 → **S2881** + `test_zoom_out_tool_2780`): **185/185 pass** (174 baseline + 11 new).

### Why criticality-first continued at S2881 (Path A over Path B)

Pre-code SIGN (Rigby, 3 turns) evaluated Path A (criticality-first cadence continuation) vs Path B (V4 normalization utility pivot from S2880 Fold B 3rd trigger). Claude independently Grep-verified the remainder: **25 total bare-return sites in `td_handlers_ops.py`, clustered into 7 bounded groups — ZERO diffuse.** Path B's premise ("normalizer dominates if remainder is diffuse") lost its evidence. Rigby AGREE → **Path A dominates**. Compress remaining work to ~2-3 slates. Chris D-verdict: approve Path A + WRITE-PATH as Slate 1.

### 3 post-code zoom-out folds + 4 pre-code folds

Recorded in Rigby Tool Gap Ledger #22 (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`, +5,454 chars appended at S2881 close, total 43,434 chars).

**Pre-code (4 folds, all 1st trigger):**
1. Real axis is contract governance, not shim location — two helpers coexist (`_tool_error` + `_handler_error`); Path B would create a 3rd quasi-contract.
2. "Zero bare returns" may be wrong terminal state — alternative: externally-visible tool results carry `error_code`; internal helpers stay minimal with dispatcher-boundary normalization.
3. ~30→25 site-count drift is measurement/narrative signal — need repeatable grep-based CI audit metric.
4. Helper coexistence without consolidation plan = accumulating coupling debt.

**Post-code (3 folds, all convergent):**
1. Real recurring cost = tool-surface misidentification. Until routing is explicit/inspectable at pre-code, more `unknown_action` cycles.
2. Criticality-first ranking should add **routing certainty** as a first-class axis alongside risk/impact.
3. Mechanical audit artifacts (counts + routing map) needed to keep SIGN stable — echoes pre-code Fold 3.

### Fold D — PLAYBOOK amendment candidate recorded (option C ratified)

Chris D-verdict (2026-07-21) at S2881 mid-close: 3-trigger threshold event → record as **PLAYBOOK amendment candidate**, not mid-slate substrate change. Candidate rule text (for future ratification session):

> **PLAYBOOK-6.10.10 (candidate) — Pre-code routing verification for handler-surface slates.** For any handler-surface migration slate, pre-code SIGN MUST verify tool routing (`ToolDispatcher.register` mapping) for every action in the slate BEFORE labeling the slate as belonging to a specific tool surface. Evidence admission required: file+line reference to the dispatcher registration matching each action's actual handler method. EXTENDS PLAYBOOK-6.10.8 (fold-classification SIGN discipline).

Not opened at S2881 close per Chris scope constraint. Deferred to a future ratification session per PLAYBOOK §14.2 (default two-trigger threshold already exceeded at 3).

## PRIOR SESSIONS — S2880 close + S2879 close

- **PR #3383** `e6ae8a1b3a59` — S2880 slate (2 files, +209/-7) — ops_tool remainder critical-slice (kill-switch 3 + scheduled-task 2 + ops-digest 2). See `docs/handoffs/SESSION_2880_OPS_REMAINDER_CRITICAL_SLICE.md`.
- **PR #3381** `9a3039e22e69` — S2879 slate (4 files, +279/-32) — governance_tool + ops_tool critical-slice. Governance file dropped OUT of legacy population entirely. See `docs/handoffs/SESSION_2879_GOVERNANCE_OPS_CRITICAL_SLICE.md`.

**Working loop observations at S2881:**
- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code SIGN 3 tool-grounded turns (6+several+0 runs); post-code SIGN 7 real `repo_tool` runs at HEAD. Not rubber-stamp.
- `feedback_zoom_out_ask_per_rigby_sign` fired 2× — pre-code (4 folds) + post-code (3 folds). Convergent 'mechanical audit artifacts' recommendation.
- `feedback_read_full_rigby_response_not_just_tail` — pre-code turn 2 stdout cut mid-§2b; Claude used narrow re-emit without new tool calls per Chris's improved pattern.
- `feedback_claude_stdout_truncation_vs_ui_truncation` — recognized truncations were Claude-stdout only.
- `feedback_claude_directs_rigby_then_verifies` — Claude directed narrow tool-grounded verification with concrete line numbers + specific taxonomy checks; Rigby executed with quoted evidence; Claude verified HEAD sha.
- `feedback_claude_rigby_agree_first_chris_yes_no` — pre-code + post-code SIGN both reached joint agreement BEFORE Chris D-verdict.
- `feedback_engineering_bias_over_audit` — net-new engineering ship.
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=0c26d8564bd6, surviving=none`).
- `feedback_local_truth_no_production` — 185/185 local pass IS the deploy step.
- `feedback_rigby_writes_workspace_deliverables` — Ledger update via Rigby PA at close (43,434 chars).
- `feedback_gh_pr_merge_admin_until_billing_fixed` — merged PR #3385 with `--admin` flag.
- `feedback_per_pr_summary_signals_close_readiness` — mid-flight per-PR summary + still-open checklist delivered.

**Session pin `pa-0d3de74e1f7749d5` RETIRES at S2881 close.** Fresh mint required at S2882 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2882 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

Wrapper pin rewritten at S2881 close (this PR's cascade). If needed at S2882 open:

```bash
python manage.py session_lifecycle close --label s2882-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — S2882 primary slate DECISION POINT

Per Rigby's S2881 post-code Q3 recommendation, the remaining 14 sites in 6 clusters split into two ordered slates:

**Slate 2 candidate (recommended first):** EXECUTION + AUTH — 4 sites total, both native `_handle_ops` (low routing confusion risk per Fold D discipline):
- `_ops_execution_detail` (L1576, L1581): missing `execution_id` + not-found (2 sites — likely `invalid_params` + `not_found`)
- `_authorize_staff` helper (L4433, L4438): missing auth + actor user not found (2 sites — likely `invalid_params` + `not_found`)

**Slate 3 candidate:** Agent-diag family — 10 sites in 4 distinct handler methods, each requires routing verification per method (Fold D discipline):
- `_handle_agent_memory` (L6749, L6766, L6840, L6844): agent_name/not-found + unknown-action + exception (4 sites)
- `_handle_heartbeat_history` (L6909, L6913): unknown-action + exception (2 sites)
- `_handle_infra_health` (L7130, L7134): unknown-action + exception (2 sites)
- `_handle_search_docs` (L7582, L7729): query required + exception (2 sites)

**Recommended pre-code SIGN questions for S2882:**
- Rigby: verify tool routing for each of Slate 2's 4 sites via `Grep` on `tool_dispatcher.py` — confirm `ops_tool` → `_handle_ops` for EXECUTION + AUTH (NOT `autopilot_tool`).
- Rigby: for Slate 3's 4 handler methods (agent_memory / heartbeat / infra / search_docs), Grep the tool_dispatcher registrations up front to lock routing before any migration.
- Chris: bundle Slate 2 + 3 in one PR (14 sites) OR ship as two sequential PRs?

### Step 3 — Net-new engineering candidates for S2882 (broader list)

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2881 close — S2882 primary slate driver: Slate 2 (EXECUTION + AUTH, 4 sites) recommended first per Fold D routing-certainty axis.** Slate 3 (agent-diag family, 10 sites) sequenced after.

2. **NEW at S2881 close — Fold D PLAYBOOK amendment candidate (PLAYBOOK-6.10.10)** — future ratification session. Not opened at S2881 close. May be opened at S2882 or later.

3. **NEW at S2881 close — Grep-based CI audit metric (pre-code Fold 3 + post-code Fold 3 convergent)** — small parallel ship candidate: a lint or CI script that counts bare `return {'error':}` returns across `core/services/*.py` and fails if the count regresses. Would prevent site-count drift like the S2881 30→25 miscount and enforce Fold D routing discipline.

4. **Carried from S2880 close — Fold A/B/C** all at 2nd/3rd trigger from S2880 post-code. Fold B (V4 normalizer) still at 3rd trigger, deferred by S2881 Path A recommendation. Fold A (criticality-first pacing) + Fold C (two-helper coexistence coupling) still at 2nd trigger.

5. **Carried from S2878 close — `_s2876_fake_tool` breadcrumb noise refinement** (1st trigger). NOT ready to slate.

6. **Carried from S2877 close — Schema-level dead-branch investigation** (1st trigger from S2875). Audit which handler branches are unreachable via PA tool schema enum constraints.

7. **Carried from S2877 close — Schema-layer PA route smoke extension** — dispatch via PA endpoint to catch schema-blocked payloads.

8. **Carried from S2876 close — #22.3 orthogonal-contract-axes resolution** (still 1st trigger).

9. **Carried from S2877 close — #22.4 Rigby dispatcher-probe extension** (still 1st trigger).

10. **Carried from S2874/S2875 — Extract `td_error.py` gateway-layer helper.** Still gated on Rigby's 6-adopter empirical-stability signal for `_tool_error`. Distinct axis from Fold B (V4 normalizer).

11. **Carried from S2874 — `feedback_recycle_after_merge` extension for multi-checkout setups** (still 1st trigger).

12. **Carried from S2873 — `orm_inspect_tool` JSONField type predicate** (1st trigger).

13. **Carried from S2873 — kalshi-only distribution on canonical SpiderData** (1st trigger).

14. **Carried from S2873 — "post-allowlist smoke checklist" UX pattern** (1st trigger).

15. **Ledger #5 — schema/handler drift detection lint / CI wiring** (~2 hr). Command exists at `core/management/commands/check_pa_tool_drift.py` (S2846-authored, 403 lines) but never wired to CI enforcement.

16. **Carried from S2872 — Category B cosmetic `raw_data_dict` migration** (~30 min).

17. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863).

18. **Carried — Exemption-list telemetry** (Rigby zoom-out from S2868 slate #1, 1st trigger).

19. **Carried — Stale-cleared row GC** (Rigby zoom-out from S2868 slate #1).

20. **Carried — `group_key_note` UX hint on `count_by`** (S2867 Q2 fold, 1st trigger).

21. **Carried — High-cardinality guardrail on `count_by`** (S2867 Q5 fold, 1st trigger).

22. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, 1st trigger).

23. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Still 2 independent triggers, not promoted.

24. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate, 1st trigger only).

25. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

26. **Carried — `simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold).

27. **Carried — `enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

28. **Carried — `actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required).

29. **Carried — `EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

30. **Carried — `list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

31. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859+S2868 cycle observed).

32. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

33. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

34. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

35. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

36. **Carried — Middleware `log_injected_params` spec candidate** (S2870 Q6 zoom-out fold, 1st trigger).

37. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

38. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2875 → S2876 → S2877 → S2878 → S2879 → S2880 → **S2881 (write-path critical slice)**. See A4 Constraints below.

39. **Carried — Character-os Rigby integration (5-gap analysis from S2872 mid-session, D6 moratorium hold)** — parked; unlock requires Chris directive.

### What's forbidden at S2882 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2881 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2881: write-path 11 sites (outreach + close_pack + engagement + meeting param-guards) now emit structured `error_code='invalid_params'`. Fourth real-handler migration wave in the S2876 sunset arc, third criticality-first. A4 outreach substrate now has structured error semantics on the write-path mutation surfaces (outreach approval, deal close-pack, engagement classification/reply/disqualify, meeting create/brief/recap), extending prior S2880 kill-switch + S2879 governance + focus_mode/celery/tenant/staleness coverage.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(nn) as ratified at S2880 close. **(oo) `autopilot_tool` outreach/close_pack/engagement/meeting write-path param-guards now emit concrete `error_code='invalid_params'` from the 4-code taxonomy. Fourth wave in the S2876 sunset arc, third criticality-first. A4 messaging that references operator-facing write-path observability (draft approvals, deal close-packs, engagement replies, meeting mutations) can rely on structured error semantics for downstream integrations.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2881 close — what shipped (one PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3385** `0c26d8564` — S2881 slate: `autopilot_tool` write-path critical-slice error-envelope migration (2 files, +196/-11)
- **PR `<this docs cascade>`** — S2881 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2882 open

**Workspace canonical:** Rigby Tool Gap Ledger updated via Rigby PA per `feedback_rigby_writes_workspace_deliverables` (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`, +5,454 chars appended, total 43,434 chars).

**Runtime impact:**
- Fourth wave of real handler migrations in the S2876 backfill sunset arc, third criticality-first. Legacy-file population S2880=~25 → **S2881=14**. Ops file remains IN the population with 14 bare returns in 6 bounded clusters.
- Regression suite grew from 174 → 185 (+11 S2881 rows).
- 11 write-path action-family sites (outreach + close_pack + engagement + meeting) no longer surface `error_code='legacy_error'`; consumers can key on `error_code='invalid_params'` from the S2879 taxonomy.
- No new helper introduced — S2879 `_handler_error` reused for all 11 sites.
- Fold D reached 3rd trigger (threshold event) → recorded as PLAYBOOK-6.10.10 amendment candidate for future ratification session.

**Not shipped at S2881 close (deferred to S2882 or later):**
- PLAYBOOK-6.10.10 amendment ratification (candidate note only)
- Slate 2 (EXECUTION + AUTH, 4 sites)
- Slate 3 (agent-diag family, 10 sites)
- Grep-based CI audit metric (Fold 3 convergent recommendation)
- Fold A/C from S2880 (2nd trigger, awaiting 3rd)
- Fold B (V4 normalizer, 3rd trigger, deferred by Path A recommendation)
- All prior deferred items from S2880/S2879/S2878/S2877/S2876/S2874/S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc still carried

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2881)

See:
- **S2881 handoff (current):** `docs/handoffs/SESSION_2881_OPS_WRITE_PATH_CRITICAL_SLICE.md`
- **S2880 handoff:** `docs/handoffs/SESSION_2880_OPS_REMAINDER_CRITICAL_SLICE.md`
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
