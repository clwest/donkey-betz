# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2876 CLOSE → dispatcher-layer error_code backfill wrapper shipped (2026-07-21; picks up as S2877) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2876 close).** Rigby Tool Gap Ledger #22.2 (1st trigger promoted at S2875 close from Rigby zoom-out fold) — Chris ratified at S2876 open; Claude+Rigby executed:

- **PR #3375** `1f0882d0a` — S2876 slate (2 files, +262/-0)
  - Adds temporary compatibility bridge in `ToolDispatcher._execute_inner` between PII scrub (L836-842) and `ToolResult` wrap (L875). Backfills `error_code='legacy_error'` on handler responses matching `{'error': msg}` without an `error_code`.
  - Idempotent on S2874/S2875 migrated handlers; truthy `.get('error')` guard skips success dicts with nullable `error`; top-level only (nested errors are handler-domain).
  - **Design refinements (Rigby pre-code SIGN, 5 real repo_tool runs, not rubber-stamp):** F1 → `'legacy_error'` (not `'unknown_error'` — distinct from future "truly unknown in migrated taxonomy"); F2 → truthy guard (safer default); F3/F4/F5 F-VERIFIED.
  - **Zoom-out mitigations shipped same-PR (anti-compat-blanket):** (1+2) rate-limited (60s per-tool) WARNING breadcrumb `legacy_handler_error_envelope_missing_error_code` with structured tool/action/trace fields — greppable visibility counter; (3) inline sunset criteria (remove when all handlers emit error_code OR breadcrumb fires < 1% for 14d).
  - New test file `core/tests/test_s2876_dispatcher_error_code_backfill.py` — 13 tests across 4 test classes (core 5 + scope 2 + isolation 1 + breadcrumb 5).
  - Combined regression suite (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876): **117/117 pass**.
  - Post-code live SIGN via Rigby: **F-VERIFIED** on live PA surface — `bpaas_tool.generate_close_pack {packet:{}}` returned `{success:false, error:'packet is required', error_code:'legacy_error'}`, backfill wrapper firing as designed.

**New Rigby-observed finding from S2876 post-code live SIGN (1st trigger — do NOT auto-promote):**
1. **#22.3 Orthogonal contract axes in handler error responses.** Some handlers return `{success:false, error:msg}` — post-S2876 the `error_code` is now backfilled, but `success:false` was already there. Three orthogonal axes now live (outer `ToolResult.ok` / inner `result.success` / inner `result.error_code`). Consumers may key on one and ignore others. Candidate resolutions: (A) standardize handler errors on `{error, error_code, ...}` and drop `success:false` convention, OR (B) explicitly document `success` as legacy/noise while outer envelope + inner error fields are authoritative. Watch for 2nd independent trigger before promoting to slate candidate.

## PRIOR SESSION — S2875 close (cross-tool structured-error-envelope migration)

- **PR #3372** `a89dc0a001e4` — S2875 slate (4 files, +405/-17)
  - Extended S2874's `{error, error_code, ...optional_fields}` envelope shape from `repo_tool.read_file` to 3 sibling read-path handlers: `repo_tool` (5 sites in `td_handlers_gateway.py`) + `spider_status_tool` (6 sites in `td_handlers_ops.py`) + `kb_tool` (6 sites in `td_handlers_ops.py`) — 17 sites total.
  - Helper design (Q3=A DEFER): local module-level `_tool_error(code, message, **fields)` per file — S2876 dispatcher backfill wrapper is candidate replacement / natural extraction trigger for future `td_error.py` gateway helper.
  - Post-code SIGN: 3/4 F-VERIFIED live; 1 F-BLOCKED at PA-schema layer (`kb_tool unknown_action` — enum-constrained action param rejects invalid strings at schema validation before reaching handler → still-1st-trigger observation for schema-level dead branches).

## PRIOR SESSION — S2874 close (repo_tool.read_file large-file paging)

- **PR #3369** `cc889af1f` — S2874 slate (3 files, +295/-15)
  - `repo_tool.read_file` gained `allow_large: bool = False` opt-in that lifts the 500KB soft cap for paged reads.

**Working loop observations at S2876:**
- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code SIGN Rigby ran 5 real `repo_tool.read_file` + `repo_tool.search` runs (all grounded); post-code SIGN Rigby ran 1 real live PA dispatch (F-VERIFIED end-to-end); ledger update Rigby ran 3 real `deliverable_tool.detail` + 1 real `deliverable_tool.append` + 1 real `deliverable_tool.detail` (write verified via tail slice).
- `feedback_zoom_out_ask_per_rigby_sign` fired 2× — pre-code fold yielded 3 shipped mitigations (rate-limited warning, sunset criteria, structured log fields); post-code fold surfaced #22.3 orthogonal-contract-axes as new 1st-trigger observation.
- `feedback_claude_rigby_agree_first_chris_yes_no` — reached agreement pre-code with 2 F-BLOCKING fold-ins (F1 `legacy_error`, F2 truthy guard); shipped without Chris re-routing.
- `feedback_engineering_bias_over_audit` — net-new engineering ship, not audit.
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=1f0882d0a49a, surviving=none`).
- `feedback_read_full_rigby_response_not_just_tail` — pre-code SIGN response was 36.7KB; targeted continuation to fetch truncated zoom-out fold tail.
- `feedback_local_truth_no_production` — 117/117 local pass IS the deploy step per Chris directive.
- `feedback_rigby_writes_workspace_deliverables` — routed ledger #22.2 SHIPPED update + #22.3 candidate to Rigby PA; she refused destructive `update` (large content + truncated prior read), proposed `deliverable_tool.append` as safer path (2861 chars appended, total 27,999 chars, verified via detail tail).
- `feedback_gh_pr_merge_admin_until_billing_fixed` — merged PR #3375 with `--admin` flag.
- **Candidate feedback rule (2nd trigger candidate — 1st was S2875):** Rigby refuses destructive `deliverable_tool.update` operations on large-content deliverables when prior read was truncated; she asks `Use append` or `Force update` explicitly. Watch for 3rd trigger before promoting as a Rigby-tool-surface UX pattern.

**Rigby Tool Gap Ledger updates (via Rigby PA per `feedback_rigby_writes_workspace_deliverables`):**
- Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **#22.2 (dispatcher-layer error_code backfill wrapper)** → `shipped_in_pr_S2876` (2 files / +262 lines / 13 new tests / 117/117 combined regression / live F-VERIFIED via `bpaas_tool.generate_close_pack`)
- **#22.3 (orthogonal-contract-axes in handler error responses)** → new observation, 1st trigger, do NOT auto-promote

**Session pin `pa-f515aa3ca81545d3` (labeled `s2876-cross-tool-error-envelope`) RETIRES at S2876 close.** Fresh mint required at S2877 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

**Prior pin:** `pa-158b00decda0491d` (labeled `s2875-cross-tool-error-envelope`) retired at S2875 close.

---

## S2877 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

Wrapper pin rewritten at S2876 close. If needed at S2877 open:

```bash
python manage.py session_lifecycle close --label s2877-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2877

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2876 close — PA-surface-level smoke test** (still 1st trigger from S2874, high signal, promoted to top slot now that S2876 dispatcher backfill is live). Would catch stale-worker false negatives immediately + verify migrated envelopes end-to-end (including newly-backfilled `legacy_error` from S2876). Lightweight suite dispatching through the PA tool surface (not just handler unit tests) against known-error fixtures asserting `error_code='<expected>'`. Est ~1–1.5 hr.

2. **NEW at S2876 close — Schema-level dead-branch investigation** (1st trigger from S2875 post-code SIGN). Audit which handler branches (`unknown_action` most obviously) are unreachable via the PA tool schema layer due to enum constraints. Decide per handler whether to (a) keep dead-code for defense-in-depth, (b) loosen schema to allow discovery of new actions, (c) explicitly document reachability class. Est ~1 hr (audit-only, no code).

3. **NEW at S2876 close — Legacy-handler migration wave, driven by breadcrumb telemetry.** Now that S2876 backfill fires + emits rate-limited WARNING per legacy tool, grep logs after ~1 hour of platform activity to enumerate which handlers still return bare `{error: msg}`. Prioritize handlers that fired the breadcrumb most, migrate to S2874-style `{error, error_code, ...}` envelope. Sunset criterion for backfill: all handlers migrated OR breadcrumb fire-rate <1% for 14d. Est varies (~15 min per handler once cataloged).

4. **NEW at S2876 close — #22.3 orthogonal-contract-axes resolution** (1st trigger from S2876 post-code SIGN live PA finding). NOT ready to slate; needs 2nd independent trigger. When it surfaces, candidate resolutions: (A) standardize handler errors on `{error, error_code, ...}` and drop `success:false` convention entirely; (B) explicitly document `success` as legacy/noise. Watch for.

5. **Carried from S2874/S2875 — Cross-tool structured-error-envelope migration EXTENSION** to write-path handlers. Now that read-path is done + S2876 dispatcher backfill provides safety net for any legacy handler, evaluate whether explicit write-path (create/update/delete) migration is warranted or whether backfill + gradual migration wave (#3 above) suffices. Est ~2 hr if explicit.

6. **Carried from S2874/S2875 — Extract `td_error.py` gateway-layer helper.** S2876 didn't force this; dispatcher backfill provides different lever. Still gated on Rigby confirming shapes are empirically stable. If write-path migration proceeds (#5), that may be the extraction trigger.

6. **Carried from S2874 — `feedback_recycle_after_merge` extension for multi-checkout setups** (still 1st trigger). Watch for 2nd trigger before formalizing as a feedback rule.

7. **Carried from S2873 — `orm_inspect_tool` JSONField type predicate** (S2872 Rigby-observed gap #1, still 1st trigger). Would enable direct queries like "count LegacySpiderData rows where raw_data is not a dict" via a `jsonb_typeof`-style predicate.

8. **Carried from S2873 — kalshi-only distribution on canonical SpiderData** (Rigby zoom-out 1st trigger). 117K rows all attributed to `kalshi` spider — data-shape investigation candidate.

9. **Carried from S2873 — "post-allowlist smoke checklist" UX pattern** (Rigby zoom-out 1st trigger).

10. **Ledger #5 — schema/handler drift detection lint / CI wiring** (~2 hr). Command exists at `core/management/commands/check_pa_tool_drift.py` (S2846-authored, 403 lines) but never wired to CI enforcement.

11. **Carried from S2872 — Category B cosmetic `raw_data_dict` migration** (~30 min).

12. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863).

13. **Carried — Exemption-list telemetry** (Rigby zoom-out from S2868 slate #1, 1st trigger).

14. **Carried — Stale-cleared row GC** (Rigby zoom-out from S2868 slate #1).

15. **Carried — `group_key_note` UX hint on `count_by`** (S2867 Q2 fold, 1st trigger).

16. **Carried — High-cardinality guardrail on `count_by`** (S2867 Q5 fold, 1st trigger).

17. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, 1st trigger).

18. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Still 2 independent triggers, not promoted.

19. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate, 1st trigger only).

20. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

21. **Carried — `simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold).

22. **Carried — `enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

23. **Carried — `actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required).

24. **Carried — `EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

25. **Carried — `list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

26. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859+S2868 cycle observed).

27. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

28. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

29. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

30. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

31. **Carried — Middleware `log_injected_params` spec candidate** (S2870 Q6 zoom-out fold, 1st trigger).

32. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

33. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2875: see A4 Constraints below.

34. **Carried — Character-os Rigby integration (5-gap analysis from S2872 mid-session, D6 moratorium hold)** — DBZ's `/api/pa/chat/` endpoint doesn't recognize `source='character-os-consult-engine'` / `spokesperson_id` / `workspace_id`. Parked under D6 moratorium; unlock requires Chris directive.

### What's forbidden at S2877 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2876 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2876: dispatcher-layer error_code backfill wrapper now landed — Rigby (and every future caller including A4 outreach substrate) can program against `error_code` uniformly across the WHOLE PA tool surface (not just S2874/S2875 migrated 17 sites). Legacy handlers returning `{error: msg}` get automatic `error_code='legacy_error'` backfill; migrated handlers pass through with their concrete codes. Rate-limited breadcrumb log signals when a legacy handler fires so migration priority can be data-driven.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(ii) as ratified at S2875 close. **(jj) Every PA tool response with a top-level error now carries an `error_code` field — either the handler's own migrated code (S2874/S2875 style) or the dispatcher-backfilled `'legacy_error'` (S2876 wrapper). A4 outreach substrate can rely on `error_code` presence as a stable contract without conditional substring-matching on `error` text. Sunset criterion for backfill: all handlers migrated OR breadcrumb fire-rate <1% for 14d.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2876 close — what shipped (one PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3375** `1f0882d0a` — S2876 slate: dispatcher-layer error_code backfill wrapper (2 files, +262/-0)
- **PR `<this docs cascade>`** — S2876 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2877 open

**Workspace canonical:** Rigby Tool Gap Ledger updated via Rigby PA per `feedback_rigby_writes_workspace_deliverables` (#22.2 promoted from S2875 close 1st-trigger observation → `shipped_in_pr_S2876`, +1 new 1st-trigger observation #22.3 orthogonal-contract-axes logged).

**Runtime impact:**
- Every PA tool response with a top-level `error` now carries an `error_code` field — either the handler's own migrated code (S2874/S2875 style) or the dispatcher-backfilled `'legacy_error'` (S2876 wrapper). Rigby (and every future PA-tool caller including A4 outreach substrate) can rely on `error_code` presence as a stable contract without conditional substring-matching on `error` text.
- Rate-limited (60s per-tool) `logger.warning('legacy_handler_error_envelope_missing_error_code ...')` breadcrumb provides greppable visibility into which handlers are still pre-migration + how often they're invoked in real traffic — data-driven migration prioritization.
- Live post-code verification (Rigby on live PA tool surface after `make recycle-all` to `sha 1f0882d0a`): **F-VERIFIED** via `bpaas_tool.generate_close_pack {packet:{}}` → returned `{success:false, error:'packet is required', error_code:'legacy_error'}`.
- Combined regression suite (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876): **117/117 pass**.

**Not shipped at S2876 close (deferred to S2877 or later):**
- PA-surface-level smoke test (still 1st trigger from S2874, now promoted to top S2877 candidate)
- Schema-level dead-branch investigation (1st trigger from S2875 post-code SIGN)
- Legacy-handler migration wave driven by breadcrumb telemetry (NEW candidate — enabled by S2876 breadcrumb)
- #22.3 orthogonal-contract-axes resolution (NEW 1st trigger from S2876 post-code SIGN — needs 2nd trigger before slating)
- Write-path handler envelope migration (candidate for after backfill traffic data available)
- Extract `td_error.py` gateway helper (still gated on shapes empirically settling; write-path migration may be extraction trigger)
- All prior deferred items from S2874/S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc still carried

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2876)

See:
- **S2876 handoff (current):** `docs/handoffs/SESSION_2876_DISPATCHER_ERROR_CODE_BACKFILL.md`
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
