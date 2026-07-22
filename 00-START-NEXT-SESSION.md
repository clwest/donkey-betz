# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2878 CLOSE → `bpaas_tool` structured error-envelope migration shipped (2026-07-21; picks up as S2879) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2878 close).** S2878 was the first breadcrumb-driven handler migration since the S2876 wrapper + S2877 smoke suite went live. Rigby's F5 zoom-out folded into the S2879 slate selector — see §S2879 open sequence.

- **PR #3379** `ac1854f6d` — S2878 slate (4 files, +178/-18)
  - **`_handle_bpaas`** (`core/services/td_handlers_agents.py:6234`) migrated from bare `{'success': False, 'error': msg}` returns → S2874 canonical `{success, error_code, error, action}`. 5 sites → 3 canonical codes.
  - **Codes:** `missing_required_params` (3 sites, taxonomy consolidated per Rigby F3), `unknown_action`, `handler_exception`. All 5 envelopes include `'action': action` per F3 guardrail.
  - **New test file** `core/tests/test_s2878_bpaas_error_envelope.py` — 5 rows, full `ToolDispatcher.execute_sync` end-to-end path; `handler_exception` row uses `unittest.mock.patch` on the packet_service module-level symbol.
  - **S2877 file edit** — deleted `test_bpaas_generate_close_pack_empty_packet_backfilled` from `LegacyBackfillPASurfaceTests` (re-homed under S2878 migrated coverage per Rigby F4); class docstring updated (removed bpaas from "representative handlers", added S2878 pointer).
  - **Bundled `.gitignore` housekeeping** — rule `docs/audits/SESSION_*_SYSTEM_AUDIT_*.md` for auto-generated Session 819 System Audit API snapshots. 19 untracked instances cleaned at S2878 open. Force-add fallback documented in-comment.
  - Combined regression (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877 + S2878): **139/139 pass**.

### Why bpaas + only bpaas (breadcrumb-driven pick)

Grep of `django_debug.log` for the S2876 `legacy_handler_error_envelope_missing_error_code` breadcrumb: 24 total hits, only real (non-test-fixture) handler is `bpaas_tool.generate_close_pack` (3 hits). All other hits are `_s2876_fake_tool` (S2876 test suite) or S2877 `__bogus_action_s2877__` rows.

### F5 zoom-out — Rigby-raised concern (forward-carried, NOT altering S2878)

Rigby: *"The dispatcher backfill makes the platform *appear* contract-stable (everything has an `error_code`), which can mask how many handlers are still legacy. If we only migrate breadcrumb-hit handlers, we risk a long tail where most failures still come through as `error_code='legacy_error'`."*

Two costs Rigby named:
1. **Product/UX cost** — clients depending on meaningful `error_code` taxonomy get "formally present but semantically useless" contracts.
2. **Migration cost** — sunset criterion #1 (all handlers emit `error_code`) stays out of reach; criterion #2 (<1% for 14d) may pass because paths are *rare*, not because the surface is *clean*.

**S2879 is locked to criticality-first**, not breadcrumb-first. See §S2879 open sequence for candidate targets.

## PRIOR SESSION — S2877 close (PA-surface `error_code` smoke suite)

- **PR #3377** `52c6d550b` — S2877 slate (1 file, +307/-0) — first suite that exercises the full `_execute_inner` path end-to-end via `ToolDispatcher.execute_sync`. 3 classes × 3 envelope planes (migrated pass-through / legacy backfill / dispatcher-level).

**Working loop observations at S2878:**
- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code SIGN Rigby ran 3 real `repo_tool.read_file` runs; post-code SIGN ran 3 more on shipped files. Not rubber-stamp.
- `feedback_zoom_out_ask_per_rigby_sign` fired 2× — pre-code F5 → S2879 slate selector forward-carry; post-code V4a/V4b → 1 comment tightening + defense of patch idiom.
- `feedback_claude_rigby_agree_first_chris_yes_no` — F3 taxonomy + F4 test scope resolved between Claude+Rigby BEFORE Chris D-verdict. Chris got 1 recommendation, not a menu.
- `feedback_engineering_bias_over_audit` — net-new engineering ship (handler migration + regression coverage).
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=ac1854f6d09a, surviving=none`).
- `feedback_read_full_rigby_response_not_just_tail` — pre-code SIGN F5 truncated in Claude's stdout; re-fetched cleanly.
- `feedback_claude_stdout_truncation_vs_ui_truncation` — F5 re-fetch was for Claude's execution context; Chris likely saw full response in Chat UI.
- `feedback_local_truth_no_production` — 139/139 local pass IS the deploy step.
- `feedback_rigby_writes_workspace_deliverables` — Rigby Tool Gap Ledger update via Rigby PA at close.
- `feedback_gh_pr_merge_admin_until_billing_fixed` — merged PR #3379 with `--admin` flag.

**Rigby Tool Gap Ledger updates (via Rigby PA per `feedback_rigby_writes_workspace_deliverables`):**
- Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **#22 (S2876 backfill sunset progress)** → 1 handler migrated (`_handle_bpaas`). Legacy population enumerated at S2877 was 39 files → now 38.
- **[carried from S2877]** #22.4 (Rigby cannot dispatch arbitrary tool-name strings) → still 1st trigger; NOT observed again at S2878 (post-code was file-read only, no live dispatch delegation).
- **[carried from S2876]** #22.3 (orthogonal-contract-axes in handler error responses) → S2878 migration produces a datapoint but does NOT resolve the underlying `success:False` vs `error_code`-only convention. Still 1st trigger.

**Session pin `pa-e869c051b9fd4c0d` (labeled `s2878-legacy-handler-envelope-migration`) RETIRES at S2878 close.** Fresh mint required at S2879 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

**Prior pin retired at S2878 open:** `pa-f45f81cb7ef34005` (minted during S2877 docs cascade PR #3378).

---

## S2879 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

Wrapper pin will be rewritten at S2878 close (this PR's cascade). If needed at S2879 open:

```bash
python manage.py session_lifecycle close --label s2879-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — S2879 slate is CRITICALITY-FIRST, not breadcrumb-first (Rigby F5 forward-carry)

Per Rigby's F5 zoom-out at S2878 pre-code SIGN, the next legacy-handler migration slate MUST be picked by failure blast radius, not breadcrumb frequency. Suggest S2879 opens with a Rigby pre-code SIGN that ranks candidates by (a) call frequency in production-adjacent code, (b) failure blast radius, (c) migration complexity.

**Candidate first-look targets (all zero-breadcrumb, all high blast radius):**

1. **`td_handlers_content.py`** (19 `{'error': ...}` sites) — PA content pipeline, high blast radius at publishing/deliverable moments. Content-tool errors surface at operator-facing content authoring / bulk-archive / status-flip points.
2. **`td_handlers_ops.py`** (26 sites) — ops-tool = admin/operator surface, high blast radius at incident/triage moments. Ops-tool errors surface exactly when operators are trying to understand or fix things.
3. **`td_handlers_governance.py`** (1 site — small but semantically weighted) — ratification/decision surface, single-site migration = fastest ship if paired with another target.

Not mutually exclusive — a natural pairing might be `td_handlers_governance.py` (1 site, trivial) + `td_handlers_content.py` bulk_archive guards subset (~4 sites, ~L4821-5046) for a single-PR criticality-first pilot.

### Step 3 — Net-new engineering candidates for S2879 (broader list)

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2878 close — Criticality-first handler migration (S2879 primary slate driver)** — see §Step 2 above.

2. **NEW at S2878 close — `_s2876_fake_tool` breadcrumb noise refinement** (1st trigger observation). S2876 test suite creates a fake tool that legitimately fires the breadcrumb by design; the breadcrumb log doesn't distinguish test-fixture dispatches from real handler hits. Candidate: add a `fixture_marker` to the breadcrumb metadata (e.g., `_s2876_fake_tool` naming convention gets a `test_fixture=True` flag). Est ~30 min. NOT ready to slate — 1st noise observation only, needs 2nd trigger.

3. **Carried from S2877 close — Schema-level dead-branch investigation** (still 1st trigger from S2875 post-code SIGN). Audit which handler branches (`unknown_action` most obviously) are unreachable via the PA tool schema layer due to enum constraints. Est ~1 hr (audit-only, no code).

4. **Carried from S2877 close — Schema-layer PA route smoke extension** — dispatch via PA endpoint to catch schema-blocked payloads. Est ~1.5 hr.

5. **Carried from S2876 close — #22.3 orthogonal-contract-axes resolution** (1st trigger, still). S2878 migration produced 1 datapoint but did not force resolution. Watch for 2nd trigger.

6. **Carried from S2877 close — #22.4 Rigby dispatcher-probe extension** (1st trigger from S2877; NOT re-triggered at S2878). If pattern surfaces again, evaluate (A) `dispatcher_probe_tool` extension, (B) codify CTOAgent-delegation.

7. **Carried from S2874/S2875 — Cross-tool structured-error-envelope migration EXTENSION to write-path handlers.** After a few more criticality-first migrations land (S2879+), write-path could be the next arc. Est ~2 hr if explicit.

8. **Carried from S2874/S2875 — Extract `td_error.py` gateway-layer helper.** Gated on Rigby confirming shapes are empirically stable across migrated handlers. Likely trigger: when S2879+ migrations start creating the same envelope-construction boilerplate in a 4th handler.

9. **Carried from S2874 — `feedback_recycle_after_merge` extension for multi-checkout setups** (still 1st trigger). Watch for 2nd trigger.

10. **Carried from S2873 — `orm_inspect_tool` JSONField type predicate** (1st trigger). Would enable direct queries like "count LegacySpiderData rows where raw_data is not a dict" via a `jsonb_typeof`-style predicate.

11. **Carried from S2873 — kalshi-only distribution on canonical SpiderData** (1st trigger). 117K rows all attributed to `kalshi` spider — data-shape investigation candidate.

12. **Carried from S2873 — "post-allowlist smoke checklist" UX pattern** (1st trigger).

13. **Ledger #5 — schema/handler drift detection lint / CI wiring** (~2 hr). Command exists at `core/management/commands/check_pa_tool_drift.py` (S2846-authored, 403 lines) but never wired to CI enforcement.

14. **Carried from S2872 — Category B cosmetic `raw_data_dict` migration** (~30 min).

15. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863).

16. **Carried — Exemption-list telemetry** (Rigby zoom-out from S2868 slate #1, 1st trigger).

17. **Carried — Stale-cleared row GC** (Rigby zoom-out from S2868 slate #1).

18. **Carried — `group_key_note` UX hint on `count_by`** (S2867 Q2 fold, 1st trigger).

19. **Carried — High-cardinality guardrail on `count_by`** (S2867 Q5 fold, 1st trigger).

20. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, 1st trigger).

21. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Still 2 independent triggers, not promoted.

22. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate, 1st trigger only).

23. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

24. **Carried — `simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold).

25. **Carried — `enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

26. **Carried — `actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required).

27. **Carried — `EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

28. **Carried — `list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

29. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859+S2868 cycle observed).

30. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

31. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

32. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

33. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

34. **Carried — Middleware `log_injected_params` spec candidate** (S2870 Q6 zoom-out fold, 1st trigger).

35. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

36. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2875, further extended at S2876, further extended at S2877. See A4 Constraints below.

37. **Carried — Character-os Rigby integration (5-gap analysis from S2872 mid-session, D6 moratorium hold)** — parked; unlock requires Chris directive.

### What's forbidden at S2879 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2878 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2878: `_handle_bpaas` now emits structured `error_code` — the S2876 backfill wrapper's idempotent guard short-circuits before assigning `legacy_error` for this handler. First real-handler migration of the S2876 sunset arc. A4 outreach substrate has slightly stronger guarantees around error-envelope contract stability at handler-level, not just dispatcher-level.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(kk) as ratified at S2877 close. **(ll) `bpaas_tool` handler now emits 3 concrete `error_code` values (`missing_required_params`, `unknown_action`, `handler_exception`) — first real handler-side migration to the S2874 canonical shape. Any A4 messaging that references bpaas-driven consulting deliverables can rely on structured error semantics for downstream integrations.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2878 close — what shipped (one PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3379** `ac1854f6d` — S2878 slate: `_handle_bpaas` structured error-envelope migration + S2877 test re-home + `.gitignore` audit housekeeping (4 files, +178/-18)
- **PR `<this docs cascade>`** — S2878 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2879 open

**Workspace canonical:** Rigby Tool Gap Ledger updated via Rigby PA per `feedback_rigby_writes_workspace_deliverables` (#22 sunset progress: 39→38 legacy population; #22.3 still 1st trigger; #22.4 still 1st trigger).

**Runtime impact:**
- First real handler migrated in the S2876 backfill sunset arc. Legacy population enumerated at S2877: 39 files. Post-S2878: 38 files.
- Regression suite grew from 135 → 139 (+5 new S2878 rows − 1 deleted S2877 row = +4 net). All still pass end-to-end via `execute_sync`.
- `_handle_bpaas` (`bpaas_tool` — sole real breadcrumb hitter in local logs) will no longer surface `error_code='legacy_error'`; consumers can key on the concrete codes.

**Not shipped at S2878 close (deferred to S2879 or later):**
- Criticality-first handler migration (S2879 primary slate driver — Rigby F5 forward-carry)
- `_s2876_fake_tool` breadcrumb noise refinement (1st trigger only)
- Schema-level dead-branch investigation (still 1st trigger from S2875)
- Schema-layer PA route smoke extension
- #22.3 orthogonal-contract-axes resolution
- #22.4 Rigby dispatcher-probe extension
- Write-path handler envelope migration
- Extract `td_error.py` gateway helper
- All prior deferred items from S2877/S2874/S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc still carried

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2878)

See:
- **S2878 handoff (current):** `docs/handoffs/SESSION_2878_BPAAS_ERROR_ENVELOPE.md`
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
