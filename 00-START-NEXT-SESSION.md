# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2882 CLOSE → `ops_tool` EXECUTION + AUTH critical-slice + `permission_denied` 5th taxonomy code shipped (2026-07-21; picks up as S2883) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2882 close).** S2882 was the fourth CRITICALITY-FIRST handler migration slate. Two PRs shipped: Slate 2 (4 sites) + close follow-on (`permission_denied` 5th code + not-staff branch).

- **PR #3387** `6331c833e` — S2882 slate (2 files, +191/-8)
  - **EXECUTION cluster** (`_ops_execution_detail` L1574-1594, 2 sites): missing `execution_id` + DoesNotExist → `invalid_params` + `not_found` via `ops_tool`.
  - **AUTH cluster** (`_authorize_staff` L4439-4466, 2 sites): missing auth + actor-not-found → `invalid_params` + `not_found` via `workspace_budget_tool`. Helper signature extended with `action_name` arg; 2 call-sites updated.
  - **Fold D 4th-trigger THRESHOLD EVENT mid-slate:** Pre-code SIGN framed AUTH cluster as `ops_tool` surface; test dispatcher initially routed via `ops_tool` and got `unknown_action`. `_authorize_staff` actually lives inside `_handle_workspace_budget` (dispatched via `workspace_budget_tool` at `tool_dispatcher.py:542`). Same routing-boundary drift Rigby caught in S2880 (governance_tool) + S2881 (autopilot_tool). PLAYBOOK-6.10.10 amendment candidate now on 4 independent triggers.
  - **Reused S2879 `_handler_error` helper** at `td_handlers_ops.py:48` — no new helper introduced.
  - **New test file** `core/tests/test_s2882_ops_execution_auth_error_envelope.py` — 4 rows exercising full `ToolDispatcher.execute_sync` path via both `ops_tool` and `workspace_budget_tool`.

- **PR #3388** `377f39364` — S2882 close follow-on (2 files, +51/-8)
  - Chris ratified Rigby's post-code zoom-out (a): **added `permission_denied` as 5th taxonomy code** (scope strictly authz). `_handler_error` docstring at `td_handlers_ops.py:48` documents the 5th code with scope constraint.
  - `_authorize_staff` not-staff branch (L4457-4467) migrated from bare `{'error': ...}` to `_handler_error(action_name, 'permission_denied', ...)`.
  - 5th test row added; uses `unittest.mock.patch` on `User.objects.get` to bypass `TestCase`-transaction-invisibility to the dispatcher's async ORM connection.
  - Combined regression (S2869 → **S2882** + `test_zoom_out_tool_2780`): **190/190 pass** (185 baseline + 5 new).

### Why the slate split into two PRs

Pre-code SIGN (Rigby, 3 turns tool-grounded) evaluated 3 paths for shipping the remaining 14 sites: (a) bundle Slate 2+3 in one PR, (b) Slate 2 → Slate 3 sequential PRs, (c) Slate 2 only S2882. Rigby's V2 correctly flagged Slate 3 spans **4 different tool surfaces** (agent_memory_tool / heartbeat_history_tool / infra_health_tool / search_docs) — bundling would violate Fold D routing-certainty axis. Rigby DISAGREED (a), AGREED (b) and (c). Chris D-verdict: (b), Slate 2 as PR-1 at S2882.

Post-code SIGN raised (a) taxonomy-gap + (b) helper-enclosing-scope. Chris ratified both; (a) shipped as PR #3388 same session; (b) codified as SIGN discipline candidate for future PLAYBOOK amendment.

### 2 post-code zoom-out asks (both Chris-ratified) + 3 additional Fold observations

Recorded in Rigby Tool Gap Ledger #22 (to be updated by Rigby at S2882 close, next step in the close ceremony).

**Post-code SIGN (2 asks, both approved same-session):**
- (a) TAXONOMY: 5th code `permission_denied` added before Slate 3 (shipped PR #3388). Prevents deferring the not-staff branch or opening a longer taxonomy-refinement arc.
- (b) FOLD D FIX: Pre-code SIGN MUST grep for **helper enclosing scope** (containing `_handle_*` method) before labeling tool surface. Deferred to future PLAYBOOK amendment session — extension or sibling to PLAYBOOK-6.10.10.

**Additional post-code folds (recorded for PLAYBOOK-6.10.8 substrate, forward-carry):**
- **Fold X (1st trigger):** `TestCase` transactions not visible to `ToolDispatcher.execute_sync` async ORM connection. Not a same-slate fix — broader test-authoring concern.
- **Fold Y (1st trigger):** `_authorize_staff` broad `except Exception:` swallows SynchronousOnlyOperation and silently returns `not_found`. Not shipped — behavior change requires its own SIGN.
- **Fold Z (informative):** Post-S2882 population = 9 sites remaining, but Slate 3 was scoped as 10 sites. Need fresh grep + routing-map at S2883 open before committing to Slate 3 site list.

## PRIOR SESSIONS — S2881 close + S2880 close + S2879 close

- **PR #3385** `0c26d8564` — S2881 slate (2 files, +196/-11) — `autopilot_tool` write-path critical slice (outreach + close_pack + engagement + meeting, 11 sites). See `docs/handoffs/SESSION_2881_OPS_WRITE_PATH_CRITICAL_SLICE.md`.
- **PR #3383** `e6ae8a1b3a59` — S2880 slate (2 files, +209/-7) — ops_tool remainder critical-slice (kill-switch 3 + scheduled-task 2 + ops-digest 2). See `docs/handoffs/SESSION_2880_OPS_REMAINDER_CRITICAL_SLICE.md`.
- **PR #3381** `9a3039e22e69` — S2879 slate (4 files, +279/-32) — governance_tool + ops_tool critical-slice. See `docs/handoffs/SESSION_2879_GOVERNANCE_OPS_CRITICAL_SLICE.md`.

**Session pin `pa-aae31b596346411e` RETIRES at S2882 close.** Fresh mint required at S2883 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## S2883 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

Wrapper pin rewritten at S2882 close (this PR's cascade). If needed at S2883 open:

```bash
python manage.py session_lifecycle close --label s2883-<slate>
```

Verify:
```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
```

### Step 2 — S2883 primary slate DECISION POINT

Per Fold D routing-certainty axis + post-S2882 Fold Z, the remaining 9 sites need a **routing-map refresh** before slating. Recommended pre-code discipline:

**Pre-code SIGN Q1 (per zoom-out b):** Rigby: for each of the 4 handler methods below, grep `tool_dispatcher.py` for the registration line AND grep `td_handlers_ops.py` for the enclosing `def _handle_*` method containing each targeted site. Report a routing-map table before any code is written.

**Slate 3 candidate (agent-diag family, targeted ~9 sites, needs routing refresh):**
- `_handle_agent_memory` (L6749, L6766, L6840, L6844) — 4 sites; dispatched via `agent_memory_tool` at `tool_dispatcher.py:610`
- `_handle_heartbeat_history` (L6909, L6913) — 2 sites; dispatched via `heartbeat_history_tool` at L611
- `_handle_infra_health` (L7130, L7134) — 2 sites; dispatched via `infra_health_tool` at L612
- `_handle_search_docs` (L7582, L7729) — 2 sites; dispatched via `search_docs` (no `_tool` suffix) at L629

**Line numbers above are S2881 baseline** — post-S2882 edits may have shifted them. Verify via fresh grep at S2883 open.

**Options for Chris:**
- (i) Ship all 9-10 Slate 3 sites in one PR after routing-map verification
- (ii) Split Slate 3 by tool surface (4 mini-PRs), tightest Fold D discipline
- (iii) Grep-map first, then decide bundle vs split based on evidence

Recommended default: **(iii)** — matches Rigby's zoom-out (b) SIGN discipline.

### Step 3 — Net-new engineering candidates for S2883 (broader list)

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2882 close — S2883 primary slate driver: Slate 3 routing-map + migration** (per zoom-out b discipline). Post-map decision on bundle vs split.

2. **NEW at S2882 close — Fold Y follow-on candidate: narrow `_authorize_staff` broad `except Exception:` to `User.DoesNotExist`.** Surface-behavior change; requires its own Rigby SIGN before code.

3. **NEW at S2882 close — Fold X test-authoring workaround: standardize on either `TransactionTestCase` or ORM-boundary mocking for dispatcher-path tests requiring DB-visible state.** Not a code fix — a test-authoring convention documentation. Candidate for the S2882 handoff → future test-authoring standards doc.

4. **NEW at S2882 close — PLAYBOOK-6.10.10 amendment ratification** — 4 triggers on record + Rigby zoom-out (b) refinement (helper-enclosing-scope grep as SIGN discipline). May be opened at S2883 or later.

5. **NEW at S2882 close — Grep-based CI audit metric** (Fold 3 convergent from S2881, still deferred) — a lint or CI script that counts bare `return {'error':}` returns across `core/services/*.py` and fails if the count regresses. Would enforce Fold D routing discipline mechanically.

6. **Carried from S2881 close — Fold D PLAYBOOK amendment candidate (PLAYBOOK-6.10.10)** — future ratification session.

7. **Carried from S2880 close — Fold A/B/C** all at 2nd/3rd trigger from S2880 post-code. Fold B (V4 normalizer) still at 3rd trigger, deferred by S2881 Path A recommendation. Fold A (criticality-first pacing) + Fold C (two-helper coexistence coupling) still at 2nd trigger.

8. **Carried from S2878 close — `_s2876_fake_tool` breadcrumb noise refinement** (1st trigger). NOT ready to slate.

9. **Carried from S2877 close — Schema-level dead-branch investigation** (1st trigger from S2875). Audit which handler branches are unreachable via PA tool schema enum constraints.

10. **Carried from S2877 close — Schema-layer PA route smoke extension** — dispatch via PA endpoint to catch schema-blocked payloads.

11. **Carried from S2876 close — #22.3 orthogonal-contract-axes resolution** (still 1st trigger).

12. **Carried from S2877 close — #22.4 Rigby dispatcher-probe extension** (still 1st trigger).

13. **Carried from S2874/S2875 — Extract `td_error.py` gateway-layer helper.** Still gated on Rigby's 6-adopter empirical-stability signal for `_tool_error`. Distinct axis from Fold B (V4 normalizer).

14. **Carried from S2874 — `feedback_recycle_after_merge` extension for multi-checkout setups** (still 1st trigger).

15. **Carried from S2873 — `orm_inspect_tool` JSONField type predicate** (1st trigger).

16. **Carried from S2873 — kalshi-only distribution on canonical SpiderData** (1st trigger).

17. **Carried from S2873 — "post-allowlist smoke checklist" UX pattern** (1st trigger).

18. **Ledger #5 — schema/handler drift detection lint / CI wiring** (~2 hr). Command exists at `core/management/commands/check_pa_tool_drift.py` (S2846-authored, 403 lines) but never wired to CI enforcement.

19. **Carried from S2872 — Category B cosmetic `raw_data_dict` migration** (~30 min).

20. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863).

21. **Carried — Exemption-list telemetry** (Rigby zoom-out from S2868 slate #1, 1st trigger).

22. **Carried — Stale-cleared row GC** (Rigby zoom-out from S2868 slate #1).

23. **Carried — `group_key_note` UX hint on `count_by`** (S2867 Q2 fold, 1st trigger).

24. **Carried — High-cardinality guardrail on `count_by`** (S2867 Q5 fold, 1st trigger).

25. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, 1st trigger).

26. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Still 2 independent triggers, not promoted.

27. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate, 1st trigger only).

28. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

29. **Carried — `simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold).

30. **Carried — `enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

31. **Carried — `actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required).

32. **Carried — `EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

33. **Carried — `list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

34. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859+S2868 cycle observed).

35. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

36. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

37. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

38. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

39. **Carried — Middleware `log_injected_params` spec candidate** (S2870 Q6 zoom-out fold, 1st trigger).

40. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

41. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2875 → S2876 → S2877 → S2878 → S2879 → S2880 → S2881 → **S2882 (EXECUTION + AUTH + permission_denied 5th code)**. See A4 Constraints below.

42. **Carried — Character-os Rigby integration (5-gap analysis from S2872 mid-session, D6 moratorium hold)** — parked; unlock requires Chris directive.

### What's forbidden at S2883 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2882 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2882: EXECUTION + AUTH clusters (2 + 3 sites) now emit structured error codes (`invalid_params` / `not_found` / `permission_denied`). Fifth real-handler migration wave in the S2876 sunset arc, fourth criticality-first. A4 outreach substrate now has structured error semantics on execution-lookup and workspace-budget-authz mutation surfaces, extending prior S2881 write-path + S2880 kill-switch + S2879 governance + focus_mode/celery/tenant/staleness coverage. 5-code taxonomy now available: `invalid_params` / `not_found` / `unknown_action` / `dependency_missing` / `permission_denied`.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(oo) as ratified at S2881 close. **(pp) `ops_tool.execution_detail` + `workspace_budget_tool.{set_default_cap,backfill_defaults}` authz gate now emit concrete `error_code` from the 5-code taxonomy. Fifth wave in the S2876 sunset arc, fourth criticality-first. `permission_denied` code available for authz denial semantics. A4 messaging that references operator-facing execution lookup or workspace-budget authorization can rely on structured error semantics for downstream integrations.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2882 close — what shipped (two PRs + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3387** `6331c833e` — S2882 slate: `ops_tool` EXECUTION + AUTH critical-slice error-envelope migration (2 files, +191/-8)
- **PR #3388** `377f39364` — S2882 close follow-on: `permission_denied` 5th taxonomy code + not-staff branch migration (2 files, +51/-8)
- **PR `<this docs cascade>`** — S2882 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2883 open

**Workspace canonical:** Rigby Tool Gap Ledger updated via Rigby PA per `feedback_rigby_writes_workspace_deliverables` (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`, appended at S2882 close).

**Runtime impact:**
- Fifth wave of real handler migrations in the S2876 backfill sunset arc, fourth criticality-first. Legacy-file population S2881=~14 → **S2882=9**. Ops file remains IN the population with 9 bare returns in 4 clusters (agent-diag family).
- Regression suite grew from 185 → **190** (+5 S2882 rows).
- 5 sites (2 EXECUTION + 3 AUTH) no longer surface `error_code='legacy_error'`; consumers can key on 5-code taxonomy.
- **New `permission_denied` 5th taxonomy code** — scope strictly authz.
- No new helper introduced — S2879 `_handler_error` reused for all 5 sites.
- Fold D reached 4th trigger (routing surprise on `workspace_budget_tool`) → PLAYBOOK-6.10.10 amendment candidate strengthened + Rigby zoom-out (b) refinement (helper-enclosing-scope grep as SIGN discipline).

**Not shipped at S2882 close (deferred to S2883 or later):**
- Slate 3 (agent-diag family, ~9-10 sites, 4 tool surfaces) — needs routing-map refresh first
- PLAYBOOK-6.10.10 amendment ratification (4 triggers + Rigby (b) refinement)
- Fold X (async DB isolation) test-authoring convention
- Fold Y (narrow `_authorize_staff` broad except catch) — behavior change, own SIGN
- Grep-based CI audit metric (Fold 3 convergent from S2881)
- Fold A/C from S2880 (2nd trigger, awaiting 3rd)
- Fold B (V4 normalizer, 3rd trigger, deferred by Path A recommendation)
- All prior deferred items from S2881/S2880/S2879/S2878/S2877/S2876/S2874/S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc still carried

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2882)

See:
- **S2882 handoff (current):** `docs/handoffs/SESSION_2882_OPS_EXECUTION_AUTH_CRITICAL_SLICE.md`
- **S2881 handoff:** `docs/handoffs/SESSION_2881_OPS_WRITE_PATH_CRITICAL_SLICE.md`
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
