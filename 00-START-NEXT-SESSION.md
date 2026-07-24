# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2940 CLOSED SLICE 7 (9/9 tools). BATCH 2b shipped 3 validation docs (`code_job_tool` + `employee_tool` + `railway_tool`) as PR #3515 at SHA `260ec6508`. §6 LIVE-VERIFIED coverage DOUBLED vs S2939 (7 read actions across the 3 docs vs 4 at S2939 Batch 2a). Second live-in-force Ledger #5 lint consumer — 0 handler_drift hits across all 3 Batch 2b tools (substrate remained clean). Gap-map headline: **`98 validated_full / 0 untested`** (was `95 / 3` at S2939 close). **S2941 OPENS WITH LEDGER #16 TWIN-MIRROR ENFORCEMENT** — the S2940 T0 D-verdict deferred substrate ship.

**Refreshed 2026-07-24 (S2940 close).** Chris D-verdict at S2940 T0 RATIFIED Batch 2b = 3-tool ship (`code_job_tool` + `employee_tool` + `railway_tool`) closes Slice 7 in one final ship (no Batch 2c needed — the 00-START "6 remaining" claim at S2939 close reflected accounting drift; reality was 3 `untested`). Chris D-verdict at S2940 T1 RATIFIED ship. Rigby SIGN AGREE 4/4 twice (T0 + T1). One minor §6.3/§6.4 code_job_tool reword applied inline before commit.

**Gap-map headline (Chris D-verdict condition — quoted at close per S2940 T0 zoom-out AGREE):**
```
Total tool names: 161
Per-category:
  validated_full: 98
  validated_partial: 11
  validated_doc_exists_unknown: 7
  untested: 0
  agent_via_run_agent: 44
  meta_no_handler: 1
```

**PRs shipped this session:**
- u-d-b PR [#3515](https://github.com/clwest/donkey-betz-platform/pull/3515) — Slice 7 Batch 2b (3 validation docs, CLOSES Slice 7). Merge SHA `260ec6508`.
- u-d-b PR `<TBD>` — S2940 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Docs shipped this session:**
- **`docs/research/tools/validation/code_job_tool_validation.md`** (new, 302 lines) — 4-read/3-mut bifurcated. §5a: submit=external Celery, cancel=cascading, add_repo=contained. §5b Appendix A for submit async-fanout on `code_jobs` queue. §6.1+6.2 LIVE-VERIFIED (`list_repos` returns 1 repo — donkey-betz-platform; `list` returns empty state).
- **`docs/research/tools/validation/employee_tool_validation.md`** (new, 406 lines) — 3-read/1-mut bifurcated. §5a: run_now=external Celery. §5b Appendix A for 4-pair `_RUN_NOW_TASKS` registry (rigby/docs_manager, platform_auditor/platform_audit, chief_of_staff/morning_brief, bug_triage_specialist/triage_daily). §6.1+6.2+6.3 LIVE-VERIFIED (describe rigby + describe platform_auditor + status rigby docs_manager 7d — trust.ratio=1.0, streak=5 certified). Cross-links `mission_verdict` (shared handler file — Employee OS dispatch → observe → certify loop).
- **`docs/research/tools/validation/railway_tool_validation.md`** (new, 312 lines) — 5-read/2-mut bifurcated. §5a: restart+redeploy=external HTTP (both fire identical `serviceInstanceRedeploy` GraphQL mutation). §5b Appendix N (Network-Preflight) — hardcoded endpoint at line 21, bearer_token via `RAILWAY_API_TOKEN`, 20s per-call timeout. §6.1 LIVE-VERIFIED (`help` — no network). §6.2 LIVE-VERIFIED refusal path (`RAILWAY_API_TOKEN not configured`, `error_code=legacy_error` — same 2-field signature as S2939 rigby_work_item `_disabled_response`).
- **Auto-gen doc regen** (`--include-validation-xref`): `docs/PA_TOOL_AUDIT.md` + `docs/audits/PA_TOOLS_GAP_MAP.md` — all 3 tools flip `untested → validated_full`.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3515 recycled clean at `sha=260ec6508ec0` via `make recycle-all` (surviving=none).
- Rigby verified (3/3 PASS): (1) `code_job_tool action=list_repos` envelope matches §6.1; (2) `railway_tool action=help` envelope matches §6.1 (no error_code because token check bypassed); (3) `employee_tool action=describe employee=rigby` envelope matches §6.1.

**Governance:** none this session. D6 moratorium unchanged.

**Rigby Tool Gap Ledger:** no new formal entries. 4 new record-only Ledger candidates surfaced in-doc (all deferred):
1. `code_job_tool.submit` silent-degrade on Celery dispatch failure (line 148-149 warning-log-only).
2. `employee_tool.run_now` double-dispatch hazard (no idempotency check at handler layer).
3. `railway_tool` `restart`+`redeploy` functional equivalence (identical GraphQL mutation).
4. Sixth-instance invalid-action bare-envelope pattern (Ledger #5 Tier-2 candidate — 2+ more corroborations before promoting).

Full session context: `docs/handoffs/SESSION_2940_SLICE_7_CLOSE.md`.

---

## S2941 open sequence — LEDGER #16 TWIN-MIRROR ENFORCEMENT (S2940 T0 D-verdict deferred substrate ship)

**S2941 first-action is ratified from S2940 T0:** Ledger #16 twin-mirror enforcement substrate hardening. The 3-trigger corroboration was met at S2939 close (S2937 + S2938 + S2939 all shipped without content_mirror + ratification_envelope deliverables — twin-mirror pattern per `feedback_twin_deliverable_at_every_ratification` was skipped 3 sessions). Backfill option (A) was executed at S2939 close (6 mirrors via ORM). Chris D-verdict at S2940 T0 RATIFIED the substrate promotion for S2941.

### Scope for S2941 (Ledger #16 hardening)

Two shape options — decide at T0 SIGN with Rigby:

**Option A (hard-refuse):** Extend `session_lifecycle close` (`core/management/commands/session_lifecycle.py`) to **refuse close** when both mirror IDs (content_mirror + ratification_envelope) are not provided or discoverable. Requires new CLI flags OR ORM lookup + fail-loud disposition.

**Option B (soft-checklist):** Add an explicit close-checklist gate that lists "twin mirrors written?" alongside handoff / 00-START / wrapper-pin bump items and prompts before finalizing. Softer; still allows override.

Estimated: ~2 hr substrate session either shape. Chris directive at S2940 T0: "queued alongside Batch 2b" was deferred to standalone S2941 session per Rigby T0 SIGN Q4 recommendation ("avoid compounding close-cascade complexity").

### S2941 open sequence

1. **First-action lint pre-flight:** run `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` and confirm gap-map headline still reads `98 validated_full / 0 untested` — sanity that no drift between sessions.
2. **T0 SIGN with Rigby:** present Option A vs Option B for Ledger #16 substrate shape. Ask her preferred posture (hard-refuse vs soft-checklist). Include mutation-verb scan on `core/management/commands/session_lifecycle.py` — this is a real code substrate ship, not a doc ship.
3. **Chris D-verdict:** joint recommendation from Claude+Rigby with plain-English decision framing (what we lose / more work later).
4. **Implementation:** edit `session_lifecycle.py` per chosen shape. Add regression test at `core/tests/test_session_lifecycle_twin_mirror.py` (or extend existing test file).
5. **Rigby T1 SIGN** with tool-grounded verification asks.
6. **PR + admin-merge + recycle + post-merge verify.**
7. **Close cascade** (handoff + 00-START refresh + wrapper pin bump).

### Alternative next actions (not blocked — still available if Chris redirects)

- **(A8) Signal Dispatches "Manual dispatch" button** (Rigby S2934 zoom-out fold — ~30 min).
- **(A9) Fourth signal-dispatch rule** — `demand_spike` (250 clusters) or `skill_demand` (131 clusters).
- **(A6) SignalCluster promotion audit** — only 0.58% of clusters are active.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.
- **(E) Tier 2 lint promotion** — envelope-JSON top-level-key parse against schema description text. Ledger #5 sub-substrate. ~1 session.
- **(F) Dry-run substrate design (Ledger #38)** — enables live mutation verification of Slice 7 mutations retroactively (all 4 mut tools now have analyzed-only §6). ~1 session.
- **(G) Ledger #40 candidate promotion** — expand Ledger #5 Tier 1 lint to catch `newsletter_tool` sources-drift class. Threshold: 2+ more corroborations before promoting.
- **(H) Ledger #41 candidate** — teach gap-map classifier to distinguish live-verified vs analyzed-only actions (fine-grained `validated_partial` vs `validated_full` disposition).

---

## What's forbidden at S2941 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2941 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

All S2939 close deferred entries carry forward. **S2940 additions to the deferred queue:**

- **Ledger candidate — `code_job_tool.submit` silent-degrade on Celery dispatch fail** — line 148-149 warning-log-only path. Candidate for a first-class refusal envelope OR a `celery_dispatched: false` field.
- **Ledger candidate — `employee_tool.run_now` double-dispatch hazard** — no idempotency check at handler layer; concurrent re-dispatch creates concurrent OpsRun rows. Candidate for a refuse-if-non-terminal check.
- **Ledger candidate — `railway_tool` `restart`+`redeploy` functional equivalence** — both fire identical `serviceInstanceRedeploy` mutation.
- **Ledger #5 Tier-2 candidate — bare invalid-action envelope pattern** — sixth-instance corroboration surfaced at S2940 (`code_job_tool` + `railway_tool` both use bare `{error: ...}` shape). Threshold: 2+ more corroborations before promoting.
- **`_handle_railway` docstring under-lists actions** (5/7 named — omits `metrics` + `help`) — ~2-min doc fix at next `td_handlers_railway.py` touch.

All prior S2939 deferred entries unchanged:

- **Ledger #5 Tier 2 (envelope-JSON parse)** — deferred per Rigby S2938 ZO AGREE. Bring back when 2+ additional §5c.1 findings prove Tier 1 leaves detection gaps.
- **Ledger #5 Tier 3 (semantic distance between prose and field names)** — too fuzzy for MVP; needs curated corpus first.
- **Ledger #36 (blog_tool Deliverable/SelfBlog approve-path fix)** — correctness bug candidate.
- **Ledger #37 (feedback_tool.update `.save()` → update_fields)** — ~1-line fix.
- **Ledger #38 (dry_run affordance across batch-2 mutations)** — substrate design session. Would enable live verification of Slice 7 batch 2a/2b mutations retroactively.
- **Ledger #39 (rigby_work_queue module docstring stale)** — **AUTO-DETECTED by Ledger #5 lint.** ~5-min doc fix; natural fold-in at next `rigby_work_queue` touch.
- **Ledger #40 candidate (newsletter_tool sources drift)** — record-only.
- **Ledger #41 candidate (classifier live-vs-analyzed distinction)** — record-only.
- **`execution_history_tool` `hours` schema declaration** — ~3 min follow-up PR. Ledger #35 references.
- **Invalid-action non-gating consistency across Slice 6+7 handlers** — Ledger #5 consolidation candidate. Now at sixth-instance corroboration (S2940).
- **`zoom_out_tool include=aggregations` Rigby-wrapper investigation (S2937 §6.1a anomaly)** — PA-wrapper investigation. Bundle with any Rigby wrapper touch.
- **A8 — Signal Dispatches "Manual dispatch" UI button** — Rigby S2934 zoom-out fold.
- **A6 — SignalCluster promotion audit** — substrate investigation.
- **CompetitorAnalysisAgent hardening candidate** — S2929 deferred.
- **Dedicated `agent_execution_query` PA tool** — S2931 Ledger #33.
- **Shared `skip_in_test` decorator** — S2931 Ledger #34.
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A.
- **Bundled dev-env drift slate** — pyright warnings on `pa_tool_schemas.py` + `build_pa_tool_audit.py` + `pa_tools_gap_map.py` (pre-existing dev-env drift; unchanged this ship).
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate + Ledger candidate: media_tool.delete IRREVERSIBLE** — unchanged.
- **S2909-S2929 Ledger candidates** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **S2919 narrative_tool dev-env drift** — unchanged.
- **S2925 Ledger #34 (LOW, distinct from S2931's #34)** — broader stale-model latent bug.
- **S2926 Ledger candidate — AgentTaskExecution pre-existing pyright drift** — bundled dev-env drift candidate.
- **R1 fleet reject-mode flip** — deferred.
- **Docs restructuring arc** (`project_docs_restructuring_arc_queued`) — Chris-ratified S2800, still queued.
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.
- **S2933 A3 v1 admin surface** — deferred by design (Path B ratified).

---

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (17 registered tools):** UNCHANGED.
**Slice 2 — `td_handlers_agents` (25 tools):** CLOSED at S2912.
**Slice 3 — `td_handlers_core` (22 tools):** CLOSED at S2917 (22/22).
**Slice 4 — `td_handlers_gateway` (17 tools):** CLOSED at S2924 (17/17).
**Slice 5 — `tool_dispatcher` (14 tools):** CLOSED at S2928 (14/14). ✅
**Slice 6 — `td_handlers_content` (6 tools):** CLOSED at S2936 (6/6, batch 1 + 2). ✅
**Slice 7 — singleton bucket (9 tools across 8 handler files):** **CLOSED at S2940 (9/9).** ✅ Batches 1 (S2937, 3) + 2a (S2939, 3) + 2b (S2940, 3).

**Substrate arcs CLOSED:** Ledger #5 Tier 1 MVP (S2938 — schema-vs-handler consistency lint).

**Total remaining tools to close: 0.**

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2940 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2940: zero A4 spend** — pure substrate/docs progress (Batch 2b docs shipped; Slice 7 CLOSED).
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2940)

See:
- **S2940 handoff (current):** `docs/handoffs/SESSION_2940_SLICE_7_CLOSE.md`
- **S2939 handoff:** `docs/handoffs/SESSION_2939_SLICE_7_BATCH_2A.md`
- **S2938 handoff:** `docs/handoffs/SESSION_2938_LEDGER_5_LINT.md`
- **S2937 handoff:** `docs/handoffs/SESSION_2937_SLICE_7_BATCH_1.md`
- **S2936 handoff:** `docs/handoffs/SESSION_2936_SLICE_6_BATCH_2_CLOSE.md`
- **S2935 handoff:** `docs/handoffs/SESSION_2935_SLICE_6_BATCH_1.md`
- **S2934 handoff:** `docs/handoffs/SESSION_2934_SIGNAL_DISPATCH_OBSERVABILITY.md`
- **S2933 handoff:** `docs/handoffs/SESSION_2933_A3_SIGNAL_DISPATCH_V1.md`
- **S2932 handoff:** `docs/handoffs/SESSION_2932_A2_CONTENT_STRATEGY_CONSOLIDATION.md`
- **S2931 handoff:** `docs/handoffs/SESSION_2931_LEDGER_33_34_BUNDLE.md`
- **S2930 handoff:** `docs/handoffs/SESSION_2930_AGENT_RUNS_TAB.md`
- **S2929 handoff:** `docs/handoffs/SESSION_2929_A1_FOLD_REMEDIATION.md`
- **S2928 handoff:** `docs/handoffs/SESSION_2928_SLICE_5_CLOSE_BATCH_4.md`
- **S2927 handoff:** `docs/handoffs/SESSION_2927_SLICE_5_BATCH_3.md`
- **S2926 handoff:** `docs/handoffs/SESSION_2926_SLICE_5_BATCH_2.md`
- **S2925 handoff:** `docs/handoffs/SESSION_2925_SLICE_5_BATCH_1.md`
- **Slice 5 CLOSE artifact:** `docs/audits/pa_tools/substrate/slice_5_close_artifact.md`
- **T1b canonical template file (with §5c retro-fold):** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2938 Ledger #5 lint code:** `core/services/pa_tools_gap_map.py` (`lint_schema_vs_handler` line 431) + `core/tests/test_pa_tools_gap_map_ledger_5.py`
- **S2940 Batch 2b validation docs (CLOSES Slice 7):** `docs/research/tools/validation/{code_job_tool,employee_tool,railway_tool}_validation.md`
- **S2939 Batch 2a validation docs:** `docs/research/tools/validation/{mission_verdict,newsletter_tool,rigby_work_item}_tool_validation.md`
- **S2937 validation docs:** `docs/research/tools/validation/{rigby_shift_brief,spider_data_aggregation,zoom_out}_tool_validation.md`
- **S2936 validation docs:** `docs/research/tools/validation/{blog,feedback}_tool_validation.md`
- **S2935 validation docs:** `docs/research/tools/validation/{execution_history,learning_patterns,recent_activity,surgical_moves_status}_tool_validation.md`
- **S2929 regression test:** `core/tests/test_base_business_research_agent_synthesis_gate.py` (5 tests, all pass)
- **S2930 Agent Runs endpoint test:** `core/tests/test_agent_runs_list_endpoint.py` (7 tests, all pass)
- **S2931 Ledger #33 + #34 bundle test:** `core/tests/test_s2931_ledger_33_34_bundle.py` (8 tests, all pass)
- **S2932 A2 fail-loud gate test:** `core/tests/test_content_strategy_agent_fail_loud_gate.py` (4 tests, all pass)
- **S2933 A3 v1 signal-dispatch test:** `core/tests/test_signal_dispatch_service.py` (23 tests total)
- **S2933 A3 v1 model:** `core/models_signal_dispatch.py`
- **S2933 A3 v1 service (SIGNAL_DISPATCH_RULES — 3 rules after S2934):** `core/services/signal_dispatch_service.py`
- **S2933 A3 v1 retry lever:** `python manage.py resend_signal_dispatch --help`
- **S2934 A4 endpoint:** `core/views_signal_dispatch.py` + `GET /api/v1/agents/signal-dispatches/`
- **S2934 A7 on-demand harness:** `python manage.py dispatch_signal --help`
- **S2934 A4 tab component:** `frontend/src/pages/workspace/tabs/SignalDispatchesTab.tsx`
- **S2934 test file:** `core/tests/test_s2934_signal_dispatch_harness.py` (13 tests, all pass)
- **BaseBusinessResearchAgent content-shape FAIL Fold:** engineering item deliverable `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5`.
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (no new formal entries S2940; 4 record-only candidates deferred).
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated with `--include-validation-xref`) + `docs/research/tools/validation/*.md` (115 per-tool validation docs post-S2940).
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
