# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2883 CLOSE → agent-diag family critical-slice shipped + `td_handlers_ops.py` EXITS S2876 backfill sunset arc (2026-07-21; picks up as S2884) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2883 close).** S2883 was the sixth CRITICALITY-FIRST handler migration slate. **One PR shipped, no follow-on required.** `td_handlers_ops.py` bare-`{'error':...}`-return population dropped from 10 → 0. **The ops file EXITS the S2876 backfill sunset population.**

- **PR #3390** `ca61c7725` — S2883 slate (2 files, +396/-10)
  - **agent_memory_tool cluster** (`_handle_agent_memory` L6744, 4 sites): missing agent_name (L6782 `invalid_params`), agent not found (L6799 `not_found`), unknown action (L6873 `unknown_action`), broad except (L6877 `internal_error`).
  - **heartbeat_history_tool cluster** (`_handle_heartbeat_history` L6879, 2 sites): unknown action (L6942 `unknown_action`), broad except (L6946 `internal_error`).
  - **infra_health_tool cluster** (`_handle_infra_health` L6948, 2 sites): unknown action (L7163 `unknown_action`), broad except (L7167 `internal_error`).
  - **search_docs cluster** (`_handle_search_docs` L7604, 2 sites): missing query (L7615 `invalid_params`), broad except (L7762 `internal_error`).
  - **Helper-choice = Path 1 SPLIT** (Rigby+Claude joint verdict, Chris D-approved): 6 non-catch-all → `_handler_error` (5-code taxonomy); 4 broad-except → `_tool_error('internal_error', ...)` matching S2879 `_handle_spider_status` precedent at L6737. **No taxonomy expansion, no new helper.**
  - **Fold Z corrected mid-slate:** Rigby's Q1 routing-map found population = 10 (not 9 as documented in S2882 00-START). Caught BEFORE any code written — S2882 zoom-out (b) discipline validated on first use.
  - **New test file** `core/tests/test_s2883_agent_diag_error_envelope.py` — 10 rows exercising full `ToolDispatcher.execute_sync` path across all 4 tool surfaces. Broad-except paths exercised via `unittest.mock.patch` on downstream ORM/import calls (`Agent.objects.filter`, `HeartBeat.objects.order_by`, `redis.from_url`, `core.rag.top_k`).
  - **Combined regression:** S2869 → **S2883** + `test_zoom_out_tool_2780` = **200/200 pass** (190 baseline + 10 new).
  - **Live post-merge envelope verified via Rigby** on `agent_memory_tool` + `search_docs` — both return correct `_handler_error` shape `{success: False, error_code: 'invalid_params', ...}`.

### Why S2883 shipped as one PR (no split needed)

Pre-code SIGN evaluated the 10-site population across 4 tool surfaces. Fold D routing-certainty axis was satisfied via Q1 routing-map refresh (Rigby verified all 4 handlers live directly in `td_handlers_ops.py`, none nested inside another handler — no Fold D 5th trigger). Q2 helper-choice fork (Path 1 SPLIT vs Path 2 EXPAND taxonomy vs Path 3 NARROW to 6 sites) resolved to Path 1 with Rigby zoom-out first-principles pushback on the framing itself. Chris ratified after plain-English framing translation (jargon → "do we lose anything / more work later" answers).

### 2 new memory rules codified at S2883

- **`feedback_plain_english_decision_framing_for_chris`** (NEW at S2883): every mid-flight Chris-facing decision surface must answer "do we lose anything?" + "is it more work later?" BEFORE the yes/no ask. Jargon (Fold letters, Ledger numbers, trigger counts) stays in Rigby SIGN cycles + handoffs, not in Chris decision routings. Chris directive turn-3 after I surfaced Path 1/2/3 with "Fold C 3rd trigger" / "Ledger #13 6th adopter" jargon. Chris ratified Path 1 immediately after re-framing.
- **Fold X 2nd trigger** (async DB isolation): `_handle_agent_memory` unknown_action test required `Agent.objects.filter` mock because real agent lookup short-circuited to `not_found` before reaching L6873 fallthrough. Same wall as S2882 `_authorize_staff` non-staff test. Test-authoring convention doc candidate.
- **Fold C 3rd trigger** (2-helper coexistence in single slate): Ledger #13 (`td_error.py` unified extraction) now at 6th real adopter signal — matches Rigby's S2875 stability threshold. Ready for dedicated arc when scheduled.

## PRIOR SESSIONS — S2882 close + S2881 close + S2880 close + S2879 close

- **PR #3389** `de78ba609` — S2882 docs cascade + wrapper pin bump. See `docs/handoffs/SESSION_2882_OPS_EXECUTION_AUTH_CRITICAL_SLICE.md`.
- **PR #3388** `377f39364` — S2882 close follow-on: `permission_denied` 5th taxonomy code + not-staff branch migration (2 files, +51/-8).
- **PR #3387** `6331c833e` — S2882 slate: `ops_tool` EXECUTION + AUTH critical-slice (2 files, +191/-8).
- **PR #3385** `0c26d8564` — S2881 slate: `autopilot_tool` write-path critical slice (2 files, +196/-11).
- **PR #3383** `e6ae8a1b3a59` — S2880 slate: ops_tool remainder critical-slice (2 files, +209/-7).
- **PR #3381** `9a3039e22e69` — S2879 slate: governance_tool + ops_tool critical-slice (4 files, +279/-32).

**Session pin `pa-5b237166eeb34070` RETIRES at S2883 close.** Fresh mint required at S2884 open per `feedback_session_open_atomic_mint_before_pa_dispatch` — but wrapper already rewritten at S2883 close to point at `pa-261ad03bdd634e70` (labeled `s2884-slate-tbd`).

---

## S2884 open sequence

### Step 1 — Session-open atomic mint (per `feedback_session_open_atomic_mint_before_pa_dispatch`)

Wrapper pin rewritten at S2883 close to `pa-261ad03bdd634e70` (labeled `s2884-slate-tbd`). Verify:

```bash
grep "^python tools/pa_chat.py" tools/pa_local.sh
# Expected: python tools/pa_chat.py "$@" --tools --conversation pa-261ad03bdd634e70
```

If wrapper points at a different / stale pin, run:

```bash
python manage.py session_lifecycle close --label s2884-<slate>
```

### Step 2 — S2884 primary slate DECISION POINT

**`td_handlers_ops.py` is DONE** — 0 bare returns remain. The S2876 backfill sunset arc for ops handlers is closed. Slate 4+ requires either:

- **(A) Move to next legacy file** — audit other `core/services/td_handlers_*.py` files (governance, agents, gateway, etc.) for remaining bare `{'error':...}` returns. Continues the sunset arc across the tool_dispatcher handler surface.
- **(B) Open Ledger #13 unified extraction arc** — `td_error.py` extraction now has 6 adopters (S2875 threshold met). Consolidate `_handler_error` + `_tool_error` into single canonical envelope. Dedicated arc, likely 2-3 sessions (design SIGN + implementation + adopter migration).
- **(C) PLAYBOOK-6.10.10 amendment ratification** — 4 Fold D triggers on record + Rigby zoom-out (b) helper-enclosing-scope refinement. Constitutional session shape (Playbook amendment cadence per §14.2).
- **(D) Shift to net-new engineering** — per `feedback_engineering_bias_over_audit`, pause backfill arc; propose new spider / UI page / agent capability / dashboard candidate.

**Recommended default: (A)** — audit the next legacy handler file for bare returns while the migration cadence + test-authoring pattern is warm. Estimated 20-min grep + slate-scoping SIGN Q1 before code.

**S2884 pre-code SIGN Q1 (per zoom-out (b) discipline):** for each candidate handler file, grep for `return \{('error'|"error")` returns AND grep for enclosing `def _handle_*` scope BEFORE labeling tool surface. Report routing-map table.

### Step 3 — Net-new engineering candidates for S2884 (broader list)

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2883 close — Ledger #13 unified helper extraction (`td_error.py`)** — 6th adopter signal reached. Ready for dedicated arc.

2. **NEW at S2883 close — Fold X test-authoring convention documentation** — 2nd trigger this slate. Standardize on either `TransactionTestCase` or ORM-boundary mocking for dispatcher-path tests requiring DB-visible state. Not code; documentation candidate.

3. **Carried from S2882 — Fold Y `_authorize_staff` broad `except Exception:` narrowing** to `User.DoesNotExist` — behavior change, requires own SIGN.

4. **Carried from S2882 — PLAYBOOK-6.10.10 amendment ratification** — 4 Fold D triggers + Rigby zoom-out (b) refinement.

5. **Carried from S2881 — Grep-based CI audit metric** — count bare `return {'error':}` returns across `core/services/*.py`; fail CI on regression.

6. **Carried from S2880 — Fold A/B/C from S2880 post-code.** Fold C now at 3rd trigger from S2883 — ties into Ledger #13 extraction (candidate 1). Fold A (criticality-first pacing) + Fold B (V4 normalizer, 3rd trigger, deferred by S2881 Path A) still deferred.

7. **Carried from S2878 — `_s2876_fake_tool` breadcrumb noise refinement** (1st trigger).

8. **Carried from S2877 — Schema-level dead-branch investigation** (1st trigger from S2875).

9. **Carried from S2877 — Schema-layer PA route smoke extension**.

10. **Carried from S2876 — #22.3 orthogonal-contract-axes resolution** (1st trigger).

11. **Carried from S2877 — #22.4 Rigby dispatcher-probe extension** (1st trigger).

12. **Carried from S2874/S2875 — Extract `td_error.py` gateway-layer helper.** SUPERSEDED by candidate 1 above — same extraction, now with 6th adopter signal.

13. **Carried from S2874 — `feedback_recycle_after_merge` extension for multi-checkout setups** (1st trigger).

14. **Carried from S2873 — `orm_inspect_tool` JSONField type predicate** (1st trigger).

15. **Carried from S2873 — kalshi-only distribution on canonical SpiderData** (1st trigger).

16. **Carried from S2873 — "post-allowlist smoke checklist" UX pattern** (1st trigger).

17. **Ledger #5 — schema/handler drift detection lint / CI wiring** (~2 hr). Command exists at `core/management/commands/check_pa_tool_drift.py` (S2846-authored, 403 lines) but never wired to CI enforcement.

18. **Carried from S2872 — Category B cosmetic `raw_data_dict` migration** (~30 min).

19. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863).

20. **Carried — Exemption-list telemetry** (Rigby zoom-out from S2868 slate #1, 1st trigger).

21. **Carried — Stale-cleared row GC** (Rigby zoom-out from S2868 slate #1).

22. **Carried — `group_key_note` UX hint on `count_by`** (S2867 Q2 fold, 1st trigger).

23. **Carried — High-cardinality guardrail on `count_by`** (S2867 Q5 fold, 1st trigger).

24. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, 1st trigger).

25. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.** Still 2 independent triggers, not promoted.

26. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate, 1st trigger only).

27. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

28. **Carried — `simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold).

29. **Carried — `enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

30. **Carried — `actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required).

31. **Carried — `EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

32. **Carried — `list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

33. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859+S2868 cycle observed).

34. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

35. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

36. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

37. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

38. **Carried — Middleware `log_injected_params` spec candidate** (S2870 Q6 zoom-out fold, 1st trigger).

39. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

40. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2875 → S2876 → S2877 → S2878 → S2879 → S2880 → S2881 → S2882 → **S2883 (agent-diag family)**. See A4 Constraints below.

41. **Carried — Character-os Rigby integration (5-gap analysis from S2872 mid-session, D6 moratorium hold)** — parked; unlock requires Chris directive.

### What's forbidden at S2884 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2883 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2883: agent-diag family (agent memory + heartbeat history + infra health + doc search, 10 sites) now emits structured error codes (`invalid_params` / `not_found` / `unknown_action` / `internal_error`). Sixth real-handler migration wave in the S2876 sunset arc — `td_handlers_ops.py` EXITS the population (0 bare returns remain). A4 outreach substrate now has structured error semantics on agent-scoped memory inspection, heartbeat time-series, infra dependency matrix, and doc-corpus RAG search surfaces, extending prior S2882 EXECUTION+AUTH + S2881 write-path + S2880 kill-switch + S2879 governance + focus_mode/celery/tenant/staleness coverage.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(pp) as ratified at S2882 close. **(qq) `agent_memory_tool` + `heartbeat_history_tool` + `infra_health_tool` + `search_docs` now emit concrete `error_code` from the 5-code taxonomy + `internal_error`. Sixth wave in the S2876 sunset arc completes the ops handler file (0 legacy returns remain). A4 messaging that references agent memory / heartbeat / infra / doc-search surfaces can rely on structured error semantics for downstream integrations.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2883 close — what shipped (one PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3390** `ca61c7725` — S2883 slate: agent-diag family critical-slice structured error-envelope migration (2 files, +396/-10)
- **PR `<this docs cascade>`** — S2883 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2884 open

**Workspace canonical:** Rigby Tool Gap Ledger entry #23 appended via Rigby PA per `feedback_rigby_writes_workspace_deliverables` (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`, appended 1418 chars, total 47,946 chars).

**Runtime impact:**
- Sixth wave of real handler migrations in the S2876 backfill sunset arc.
- Legacy-file population S2882=9 → **S2883=0** — Fold Z under-count corrected mid-slate (population was 10, not 9).
- **`td_handlers_ops.py` EXITS the S2876 backfill sunset population.**
- Regression suite grew from 190 → **200** (+10 S2883 rows).
- 10 sites no longer surface `error_code='legacy_error'`; consumers can key on 5-code taxonomy + `internal_error`.
- No new helper introduced. No taxonomy expansion. No new PLAYBOOK amendment.
- Fold C reached 3rd trigger — Ledger #13 (`td_error.py` unified extraction) ready for dedicated arc scheduling.

**Not shipped at S2883 close (deferred to S2884 or later):**
- `td_error.py` unified helper extraction (Ledger #13, 6th adopter signal reached)
- PLAYBOOK-6.10.10 amendment ratification (4 Fold D triggers on record)
- Fold X (async DB isolation) test-authoring convention documentation
- Fold Y (narrow `_authorize_staff` broad except catch) — S2882 carry-over
- Grep-based CI audit metric (Fold 3 convergent from S2881)
- All prior deferred items from S2882/S2881/S2880/S2879/S2878/S2877/S2876/S2874/S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc still carried

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2883)

See:
- **S2883 handoff (current):** `docs/handoffs/SESSION_2883_AGENT_DIAG_CRITICAL_SLICE.md`
- **S2882 handoff:** `docs/handoffs/SESSION_2882_OPS_EXECUTION_AUTH_CRITICAL_SLICE.md`
- **S2881 handoff:** `docs/handoffs/SESSION_2881_OPS_WRITE_PATH_CRITICAL_SLICE.md`
- **S2880 handoff:** `docs/handoffs/SESSION_2880_OPS_REMAINDER_CRITICAL_SLICE.md`
- **S2879 handoff:** `docs/handoffs/SESSION_2879_GOVERNANCE_OPS_CRITICAL_SLICE.md`
- **S2878 handoff:** `docs/handoffs/SESSION_2878_BPAAS_ERROR_ENVELOPE.md`
- **S2877 handoff:** `docs/handoffs/SESSION_2877_PA_SURFACE_ERROR_CODES_SMOKE.md`
- **S2876 handoff:** `docs/handoffs/SESSION_2876_DISPATCHER_ERROR_CODE_BACKFILL.md`
- **S2875 handoff:** `docs/handoffs/SESSION_2875_CROSS_TOOL_ERROR_ENVELOPE.md`
- **S2874 handoff:** `docs/handoffs/SESSION_2874_REPO_TOOL_READ_FILE_PAGING.md`
- **S2873 handoff:** `docs/handoffs/SESSION_2873_ORM_INSPECT_SPIDER_DATA_OPPORTUNITY.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
