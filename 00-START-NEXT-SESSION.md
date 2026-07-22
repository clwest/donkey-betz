# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2877 CLOSE → PA-surface `error_code` smoke suite shipped (2026-07-21; picks up as S2878) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2877 close).** S2874 1st-trigger promoted at S2876 close (PA-surface-level smoke test) — Chris ratified at S2877 open; Claude+Rigby executed:

- **PR #3377** `52c6d550b` — S2877 slate (1 file, +307/-0)
  - New test file `core/tests/test_s2877_pa_surface_error_codes_smoke.py` — first suite that exercises the full `_execute_inner` path end-to-end via `ToolDispatcher.execute_sync`. Prior S2874/S2875/S2876 tests call `dispatcher._handle_<x>()` directly and bypass the S2876 dispatcher-layer backfill wrapper.
  - **3 classes covering all three PA error-envelope planes:**
    - `MigratedHandlerPASurfaceTests` (14 rows) — migrated handlers pass concrete `error_code` through unchanged (S2874 read_file + S2875 read-path envelope migration).
    - `LegacyBackfillPASurfaceTests` (3 rows) — legacy handlers get `error_code='legacy_error'` backfilled by S2876 wrapper. Class docstring marked ⚠️ DELETE AFTER S2876 SUNSET with sunset criteria referenced inline.
    - `DispatcherEnvelopeTests` (1 row) — dispatcher-level unknown-tool failure surfaces at outer `ToolResult.error_code=TOOL_NOT_FOUND` (ok=False).
  - **Design refinements (Rigby pre-code SIGN, 4 grounded `repo_tool` runs, not rubber-stamp):** F1 envelope shape verified against dispatcher L820-887 + L920-929; F2 3-class split; F3 F-BLOCKING added rows 16-17 (`newsletter_tool` + `ops_tool` unknown-action → `legacy_error`) after Rigby enumerated 39-file bare-`{'error':msg}` population; F4 no `assertLogs` on breadcrumb (rate-limit map global state = flaky).
  - **Zoom-out mitigations shipped same-PR:** deterministic bogus UUID `00000000-...` (row 8), assertions minimal (`error_code` value + `error` truthy — never full message text), sunset docstring guardrail.
  - Combined regression suite (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877): **135/135 pass**.
  - Post-code SIGN via Rigby: AGREE on all 5 file-read checks; live probes delegated to CTOAgent async (surfaced Rigby tool-surface gap → observation #22.4).

**New Rigby-observed finding from S2877 post-code SIGN (1st trigger — do NOT auto-promote):**
1. **#22.4 Rigby cannot dispatch arbitrary tool-name strings.** Her PA tool surface only exposes tools registered in `PA_TOOL_SCHEMAS`. Tests / smoke probes that exercise dispatcher-level branches (e.g., `TOOL_NOT_FOUND` on a name like `__nonexistent_tool_s2877__`) can't be executed by Rigby directly — she must delegate to CTOAgent (async, 180s+ round-trip). Candidate resolutions: (A) extend Rigby's schema with a `dispatcher_probe_tool` action for auth-gated dev-mode smoke probes, (B) accept CTOAgent-delegation pattern as norm, (C) codify Claude self-executes dispatcher-envelope live verification via Python shell. Watch for 2nd trigger before promoting.

## PRIOR SESSION — S2876 close (dispatcher-layer error_code backfill wrapper)

- **PR #3375** `1f0882d0a` — S2876 slate (2 files, +262/-0)
  - Adds temporary compatibility bridge in `ToolDispatcher._execute_inner` between PII scrub (L836-842) and `ToolResult` wrap (L875). Backfills `error_code='legacy_error'` on handler responses matching `{'error': msg}` without an `error_code`.
  - Idempotent on S2874/S2875 migrated handlers; truthy `.get('error')` guard; top-level only.
  - Rate-limited (60s per-tool) WARNING breadcrumb `legacy_handler_error_envelope_missing_error_code` for greppable visibility.
  - Inline sunset criteria: remove when all handlers emit error_code OR breadcrumb fires < 1% for 14d.

**Working loop observations at S2877:**
- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code SIGN Rigby ran 4 real tool_runs; post-code SIGN Rigby ran 2 real `repo_tool.read_file` runs on the shipped file. Not rubber-stamp.
- `feedback_zoom_out_ask_per_rigby_sign` fired 2× — pre-code fold yielded 4 shipped mitigations; post-code fold yielded "wrong kind of stability" observation.
- `feedback_claude_rigby_agree_first_chris_yes_no` — F3 F-BLOCKING resolved pre-code; shipped without Chris re-routing.
- `feedback_engineering_bias_over_audit` — net-new engineering ship (first-of-its-kind PA-surface contract enforcement).
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=52c6d550bbe1, surviving=none`).
- `feedback_read_full_rigby_response_not_just_tail` — pre-code SIGN response truncated at "you're 3"; fetched tail for concerns 3-9.
- `feedback_local_truth_no_production` — 135/135 local pass IS the deploy step.
- `feedback_rigby_writes_workspace_deliverables` — Rigby Tool Gap Ledger update via Rigby PA at close.
- `feedback_gh_pr_merge_admin_until_billing_fixed` — merged PR #3377 with `--admin` flag.

**Rigby Tool Gap Ledger updates (via Rigby PA per `feedback_rigby_writes_workspace_deliverables`):**
- Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **#22.4 (Rigby cannot dispatch arbitrary tool-name strings)** → new observation, 1st trigger, do NOT auto-promote
- **[carried from S2876]** #22.3 (orthogonal-contract-axes in handler error responses) → still 1st trigger, watch for 2nd

**Session pin `pa-d822f8e637c7449a` (labeled `s2877-cross-tool-error-envelope`) RETIRES at S2877 close.** Fresh mint required at S2878 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

**Prior pin:** `pa-f515aa3ca81545d3` (labeled `s2876-cross-tool-error-envelope`) retired at S2876 close.

---

## S2878 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

Wrapper pin will be rewritten at S2877 close (this PR's cascade). If needed at S2878 open:

```bash
python manage.py session_lifecycle close --label s2878-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2878

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2877 close — Legacy-handler migration wave driven by S2876 breadcrumb telemetry** (previously #3 at S2877 open, now higher signal). With S2876 backfill live + S2877 smoke suite proving the contract works end-to-end, grep production logs for `legacy_handler_error_envelope_missing_error_code` breadcrumb hits and prioritize migration of top-N legacy handlers to S2874-style `{error, error_code, ...}` envelope. Rigby enumerated 39 legacy files at S2877; concrete targets for first pass: `td_handlers_agents.py` (multiple sites), `td_handlers_content.py`, `td_handlers_governance.py`, `td_handlers_core.py`, `td_handlers_railway.py`. Est ~15-30 min per handler. Sunset criterion for S2876 backfill: all handlers migrated OR breadcrumb <1% for 14d.

2. **NEW at S2877 close — Schema-level dead-branch investigation** (previously #2 at S2877 open, still 1st trigger from S2875 post-code SIGN). Audit which handler branches (`unknown_action` most obviously) are unreachable via the PA tool schema layer due to enum constraints. Decide per handler: (a) keep dead-code for defense-in-depth, (b) loosen schema to allow discovery of new actions, (c) explicitly document reachability class. Est ~1 hr (audit-only, no code). **S2877 note:** the S2877 smoke test's `unknown_action` rows for `repo_tool`/`spider_status_tool`/`kb_tool` prove the branches are reachable via `execute_sync` even if schema blocks the PA route — data point for the audit.

3. **NEW at S2877 close — Extend S2877 smoke suite with schema-layer PA route** (extension of just-shipped work). Currently smoke tests dispatch via `ToolDispatcher.execute_sync` which bypasses the PA schema validation layer. A parallel test class could dispatch via the PA endpoint (or `pa_local.sh` wrapper) to catch cases where the schema layer rejects a payload the dispatcher would happily handle (the S2875 `kb_tool.unknown_action` schema-block observation). Est ~1.5 hr.

4. **Carried from S2876 close — #22.3 orthogonal-contract-axes resolution** (1st trigger from S2876 post-code SIGN). NOT ready to slate; needs 2nd independent trigger. When it surfaces, candidate resolutions: (A) standardize handler errors on `{error, error_code, ...}` and drop `success:false` convention entirely; (B) explicitly document `success` as legacy/noise.

5. **NEW at S2877 close — #22.4 Rigby dispatcher-probe extension** (1st trigger from S2877 post-code SIGN F5 delegation). If pattern surfaces again (2nd trigger), evaluate (A) `dispatcher_probe_tool` extension of Rigby's schema for auth-gated dev-mode arbitrary-tool-name dispatch, (B) codify CTOAgent-delegation pattern for dispatcher-envelope work.

6. **Carried from S2874/S2875 — Cross-tool structured-error-envelope migration EXTENSION** to write-path handlers. Now that read-path is done + S2876 dispatcher backfill provides safety net for any legacy handler + S2877 smoke suite proves the contract works end-to-end. Est ~2 hr if explicit.

7. **Carried from S2874/S2875 — Extract `td_error.py` gateway-layer helper.** Still gated on Rigby confirming shapes are empirically stable. If write-path migration proceeds (#6), that may be the extraction trigger.

8. **Carried from S2874 — `feedback_recycle_after_merge` extension for multi-checkout setups** (still 1st trigger). Watch for 2nd trigger before formalizing as a feedback rule.

9. **Carried from S2873 — `orm_inspect_tool` JSONField type predicate** (S2872 Rigby-observed gap #1, still 1st trigger). Would enable direct queries like "count LegacySpiderData rows where raw_data is not a dict" via a `jsonb_typeof`-style predicate.

10. **Carried from S2873 — kalshi-only distribution on canonical SpiderData** (Rigby zoom-out 1st trigger). 117K rows all attributed to `kalshi` spider — data-shape investigation candidate.

11. **Carried from S2873 — "post-allowlist smoke checklist" UX pattern** (Rigby zoom-out 1st trigger).

12. **Ledger #5 — schema/handler drift detection lint / CI wiring** (~2 hr). Command exists at `core/management/commands/check_pa_tool_drift.py` (S2846-authored, 403 lines) but never wired to CI enforcement.

13. **Carried from S2872 — Category B cosmetic `raw_data_dict` migration** (~30 min).

14. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863).

15. **Carried — Exemption-list telemetry** (Rigby zoom-out from S2868 slate #1, 1st trigger).

16. **Carried — Stale-cleared row GC** (Rigby zoom-out from S2868 slate #1).

17. **Carried — `group_key_note` UX hint on `count_by`** (S2867 Q2 fold, 1st trigger).

18. **Carried — High-cardinality guardrail on `count_by`** (S2867 Q5 fold, 1st trigger).

19. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, 1st trigger).

20. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Still 2 independent triggers, not promoted.

21. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate, 1st trigger only).

22. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

23. **Carried — `simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold).

24. **Carried — `enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

25. **Carried — `actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required).

26. **Carried — `EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

27. **Carried — `list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

28. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859+S2868 cycle observed).

29. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

30. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

31. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

32. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

33. **Carried — Middleware `log_injected_params` spec candidate** (S2870 Q6 zoom-out fold, 1st trigger).

34. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

35. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2875, further extended at S2876. See A4 Constraints below.

36. **Carried — Character-os Rigby integration (5-gap analysis from S2872 mid-session, D6 moratorium hold)** — DBZ's `/api/pa/chat/` endpoint doesn't recognize `source='character-os-consult-engine'` / `spokesperson_id` / `workspace_id`. Parked under D6 moratorium; unlock requires Chris directive.

### What's forbidden at S2878 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2877 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2877: PA-surface error_code smoke suite now live — enforces the S2874/S2875/S2876 contract end-to-end so future regressions (accidental removal of backfill, contract shape drift, dispatcher refactors) are caught before shipping. A4 outreach substrate has stronger guarantees around error-envelope contract stability.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(jj) as ratified at S2876 close. **(kk) The PA-tool-surface `error_code` contract is now regression-tested at the `execute_sync` boundary — 18 fixtures across 3 envelope planes (migrated handlers pass-through, S2876 backfill, dispatcher-level unknown-tool). Any future PA-tool-surface work can rely on the smoke suite as a shield against contract drift.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2877 close — what shipped (one PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3377** `52c6d550b` — S2877 slate: PA-surface `error_code` smoke suite (1 file, +307/-0)
- **PR `<this docs cascade>`** — S2877 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2878 open

**Workspace canonical:** Rigby Tool Gap Ledger updated via Rigby PA per `feedback_rigby_writes_workspace_deliverables` (#22.4 new 1st-trigger observation logged).

**Runtime impact:**
- First test suite that exercises the S2876 dispatcher-layer backfill wrapper end-to-end via `ToolDispatcher.execute_sync`. Prior S2874/S2875/S2876 tests all bypass `_execute_inner`.
- Contract enforcement across all three PA error-envelope planes: migrated handlers pass-through (14 rows) + S2876 backfill (3 rows) + dispatcher-level unknown-tool (1 row).
- Sunset guardrail: `LegacyBackfillPASurfaceTests` class explicitly marked DELETE AFTER S2876 SUNSET with criteria referenced inline — removal is mechanical, not a class-level rewrite.
- Combined regression suite (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877): **135/135 pass**.

**Not shipped at S2877 close (deferred to S2878 or later):**
- Legacy-handler migration wave driven by S2876 breadcrumb telemetry (now higher priority given S2877 smoke coverage)
- Schema-level dead-branch investigation (still 1st trigger from S2875 post-code SIGN — S2877 smoke provides data)
- Schema-layer PA route smoke extension (new candidate — dispatch via PA endpoint to catch schema-blocked payloads)
- #22.3 orthogonal-contract-axes resolution (still 1st trigger)
- #22.4 Rigby dispatcher-probe extension (new 1st trigger)
- Write-path handler envelope migration
- Extract `td_error.py` gateway helper
- All prior deferred items from S2874/S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc still carried

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2877)

See:
- **S2877 handoff (current):** `docs/handoffs/SESSION_2877_PA_SURFACE_ERROR_CODES_SMOKE.md`
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
