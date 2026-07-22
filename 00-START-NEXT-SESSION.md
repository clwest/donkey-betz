# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2875 CLOSE → cross-tool structured-error-envelope migration shipped (2026-07-21; picks up as S2876) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2875 close).** Rigby Tool Gap Ledger #2 (2nd trigger promoted at S2874 close) — Chris ratified at S2875 open; Claude+Rigby executed:

- **PR #3372** `a89dc0a001e4` — S2875 slate (4 files, +405/-17)
  - Extends S2874's structured-error-envelope shape (`{error, error_code, ...optional_fields}`) from `repo_tool.read_file` to 3 sibling read-path handlers.
  - **17 migration sites** across `repo_tool` (5 sites in `td_handlers_gateway.py`) + `spider_status_tool` (6 sites in `td_handlers_ops.py`) + `kb_tool` (6 sites in `td_handlers_ops.py`).
  - **Scope expansion:** Rigby's Q1 initial pass identified 11 sites; full-coverage sweep found 5 within-handler sites she missed (kb.chunks / kb.search_embeddings / kb.semantic_search, spider_status.history). Migrated all 17 for internal consistency across sibling actions.
  - **Envelope shape corrected mid-flight (Q2 fold):** S2874 uses `{error, error_code, ...}` — NO `success: false` key. Original proposal dropped that key.
  - **Helper design (Q3=A DEFER):** local module-level `_tool_error(code, message, **fields)` per file. Do NOT extract `td_error.py` gateway helper until 6+ adopters stable + shapes empirically settle. S2874's local `_read_file_error` untouched (zero retrofit).
  - **Q4 folds applied inline:** preserve exact error message text (no rephrasing → no substring-match regressions); `error_code` documented as optional during mixed-mode migration; partial-success `warnings:[]`/`errors:[]` convention deferred.
  - New test file `core/tests/test_s2875_cross_tool_error_envelope.py` — 18 tests across 4 test classes (repo_tool 5 + spider_status_tool 6 + kb_tool 4 + cross-tool parity 3).
  - Combined regression suite (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875): **104/104 pass**.
  - Post-code SIGN via Rigby (live PA surface): 3/4 F-VERIFIED (`repo_tool.tree`, `spider_status_tool.detail`, `repo_tool.search`); 1 F-BLOCKED at PA-schema layer (`kb_tool unknown_action` — enum-constrained action param rejects invalid strings at schema validation before reaching handler — see new-finding #1 below).

## PRIOR SESSION — S2874 close (repo_tool.read_file large-file paging)

- **PR #3369** `cc889af1f` — S2874 slate (3 files, +295/-15)
  - `repo_tool.read_file` gained `allow_large: bool = False` opt-in that lifts the 500KB soft cap for paged reads. Default over-cap responses ship a structured `error_code='file_too_large'` envelope with `path` / `file_size_bytes` / `size_hard_max` / `narrowing_hint`. `allow_large=true` path skips the `total_lines` second-pass over the soft max (`total_lines_known=false`) — no double I/O for metadata even in opt-in mode. `start_line` past EOF → soft `warning_code='start_line_past_eof_or_empty_file'` (not a hard error).
  - New test file `core/tests/test_s2874_repo_tool_read_file_paging.py` — 13 tests across 4 test classes.

## PRIOR SESSION — S2873 close (orm_inspect_tool allowlist +2)

- **PR #3367** `8423e946b` — S2873 slate (2 files, +253/-0)
  - `orm_inspect_tool` `_MODEL_POLICIES` extended from 9 → 11 models (`persistence.SpiderData` 116K rows + `core.Opportunity` 2.6K rows).

**Working loop observations at S2875:**
- `feedback_verify_rigby_tool_runs_before_trusting_sign` fired 3× (12 tool_runs total, all grounded — never rubber-stamping).
- `feedback_zoom_out_ask_per_rigby_sign` yielded 2 usable folds — 1 applied inline (Q4b contract test class), 1 promoted to ledger candidate (dispatcher backfill wrapper).
- `feedback_claude_rigby_agree_first_chris_yes_no` — presented Chris one recommendation with envelope-shape correction.
- `feedback_engineering_bias_over_audit` — net-new engineering ship, not audit.
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge in `development/` checkout (`sha=a89dc0a001e4, surviving=none`).
- `feedback_read_full_rigby_response_not_just_tail` — stdout truncated TWICE mid-Rigby-response; re-fetched via targeted continuation asks. No `### Important note` prose was hidden.
- `feedback_local_truth_no_production` — 104/104 local pass IS the deploy step per Chris directive.
- **Candidate feedback rule (1st trigger):** stdout-truncation-forces-continuation is a Claude execution-context tax that inflates SIGN cycle count. Watch for 2nd trigger before formalizing.

**New Rigby-observed tool-surface gaps (candidates for future ledger entries, NOT logged yet — watch for second-trigger):**
1. **Schema-level dead branches** (1st trigger). Handlers with enum-constrained `action` params in PA tool schema (`kb_tool`, `repo_tool`, `spider_status_tool`) cannot have their `unknown_action` branches exercised via the PA tool surface — GPT-5.2 rejects invalid actions at schema validation before dispatch reaches the handler. Migration is correct per unit tests; branch is unreachable in the live PA-surface path (still reachable via direct handler invocation / batch callers / buggy code).
2. **Dispatcher-layer `error_code` backfill wrapper** (1st trigger, Rigby zoom-out). A lightweight dispatcher wrapper backfilling `error_code='unknown_error'` on tool responses that have `error` but no `error_code` would give consumers a stable contract during mid-migration — eliminates the "hit sibling tool with old shape, crash on assumed key" failure mode.

**Rigby Tool Gap Ledger updates (via Rigby PA per `feedback_rigby_writes_workspace_deliverables`):**
- Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **#2 (structured-error envelope migration)** → `shipped_in_pr_S2875` (17 sites / 3 files / 18 tests / 104/104 combined regression)

**Session pin `pa-158b00decda0491d` (labeled `s2875-cross-tool-error-envelope`) RETIRES at S2875 close.** Fresh mint required at S2876 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

**Prior pin:** `pa-54eed7894ce845ed` (labeled `s2874-repo-tool-read-file-paging`) retired at S2874 close.

---

## S2876 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

Wrapper pin rewritten at S2875 close. If needed at S2876 open:

```bash
python manage.py session_lifecycle close --label s2876-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — Net-new engineering candidates for S2876

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2875 close — Dispatcher-layer `error_code` backfill wrapper** (Rigby zoom-out 1st trigger, highest signal). Wrap the dispatcher output path to backfill `error_code='unknown_error'` on any tool response that has `error` but no `error_code`. Solves the mixed-mode migration friction from S2875 without forcing every legacy tool to migrate first. Est ~45 min (small wrapper + unit tests + verify no double-wrap). Consider whether this becomes the promoted `td_error.py` extraction trigger.

2. **NEW at S2875 close — PA-surface-level smoke test** (still 1st trigger from S2874, high signal). Would catch stale-worker false negatives immediately + verify migrated envelopes end-to-end. Lightweight suite dispatching through the PA tool surface (not just handler unit tests) against known-error fixtures asserting `error_code='<expected>'`. Est ~1–1.5 hr.

3. **NEW at S2875 close — Schema-level dead-branch investigation** (1st trigger from S2875 post-code SIGN). Audit which handler branches (`unknown_action` most obviously) are unreachable via the PA tool schema layer due to enum constraints. Decide per handler whether to (a) keep dead-code for defense-in-depth, (b) loosen schema to allow discovery of new actions, (c) explicitly document reachability class. Est ~1 hr (audit-only, no code).

4. **Carried from S2874 — Cross-tool structured-error-envelope migration EXTENSION** to write-path handlers. Now that read-path is done + we've observed 6+ adopters, evaluate whether write-path (create/update/delete) migration is warranted. Est ~2 hr.

5. **Carried from S2874 — Extract `td_error.py` gateway-layer helper** (blocks on Rigby confirming shapes are empirically stable). S2875 shipped 6+ adopters but Q3=A said wait until "one weird envelope need in the wild." Not yet promoted — dispatcher backfill (candidate #1) may become the extraction trigger instead.

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

### What's forbidden at S2876 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2875 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2875: `repo_tool` + `spider_status_tool` + `kb_tool` error paths now return structured `{error, error_code, ...optional_fields}` envelopes matching the S2874 shape — Rigby (and every future caller including A4 outreach substrate) can program against `error_code` for reliable failure classification across 17 sibling sites in read-path handlers, not just `repo_tool.read_file`.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(hh) as ratified at S2874 close. **(ii) All 17 sibling error paths in `repo_tool` (tree / search / shared catchers) + `spider_status_tool` (history / detail / search / shared catchers) + `kb_tool` (chunks / search_embeddings / semantic_search / shared catchers) now return `{error, error_code, ...optional_fields}` envelopes with machine-actionable `error_code` values (`not_a_directory` / `query_required` / `unknown_action` / `value_error` / `internal_error` / `spider_name_required` / `item_id_required` / `item_not_found` / `filters_required` / `document_id_required`); message text preserved verbatim from pre-migration (no downstream substring-match regressions); `error_code` documented as optional during mixed-mode migration.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2875 close — what shipped (one PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3372** `a89dc0a001e4` — S2875 slate: cross-tool structured-error-envelope migration (4 files, +405/-17)
- **PR `<this docs cascade>`** — S2875 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2876 open

**Workspace canonical:** Rigby Tool Gap Ledger update planned at close per `feedback_rigby_writes_workspace_deliverables` (#2 promoted from wish-list → `shipped_in_pr_S2875`, 2 new zoom-out observations logged).

**Runtime impact:**
- Rigby (and every future PA-tool caller) can now program against `error_code` for failure classification across `repo_tool` / `spider_status_tool` / `kb_tool` — 17 sibling sites, not just S2874's `repo_tool.read_file`.
- Live post-code verification (Rigby on live PA tool surface after `make recycle-all` in `development/`): 3/4 F-VERIFIED (`repo_tool.tree`, `spider_status_tool.detail`, `repo_tool.search`); 1 F-BLOCKED at PA-schema layer (`kb_tool unknown_action` — enum-constrained schema rejects invalid strings before handler dispatch — new finding, see #1 in gaps section).
- Combined regression suite (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875): **104/104 pass**.

**Not shipped at S2875 close (deferred to S2876 or later):**
- Dispatcher-layer `error_code` backfill wrapper (Rigby zoom-out 1st trigger from S2875 — top S2876 candidate)
- PA-surface-level smoke test (still 1st trigger from S2874)
- Schema-level dead-branch investigation (1st trigger from S2875 post-code SIGN)
- Write-path handler envelope migration (candidate for after 6+ read-path adopters proven stable)
- Extract `td_error.py` gateway helper (still gated on "shapes empirically settle")
- `feedback_recycle_after_merge` multi-checkout extension (1st trigger from S2874)
- All prior deferred items from S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc still carried

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2875)

See:
- **S2875 handoff (current):** `docs/handoffs/SESSION_2875_CROSS_TOOL_ERROR_ENVELOPE.md`
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

For older session history (S1-S2846), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
