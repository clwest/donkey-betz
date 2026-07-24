# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2938 PROMOTED LEDGER #5 TO SUBSTRATE: schema-vs-handler consistency lint (Tier 1 MVP) shipped as PR #3512 after Chris ratified Path B (pause Slice 7 Batch 2a for one session). Live backfill: 2 flags land on `rigby_work_item` (Ledger #39 case), zero false positives across 115 remaining wired tools. **S2939 OPENS WITH SLICE 7 BATCH 2a (deferred one session) — 3 mutation tools (mission_verdict + newsletter_tool + rigby_work_item) with lint now in-force at pre-flight.**

**Refreshed 2026-07-24 (S2938 close).** Chris D-verdict at S2938 T0: Path B ratified against Path A (charge Batch 2a as-planned). Rigby S2938 T0 SIGN AGREE (Q1/Q2/Q3 with Q3 F-BLOCKING refinement broadening negative-claim patterns + service-layer dispatch detection; ZO AGREE Tier 2 defer). All 4 refinements incorporated. PR merged as SHA `6ce7c0501`.

**PRs shipped this session:**
- u-d-b PR [#3512](https://github.com/clwest/donkey-betz-platform/pull/3512) — Ledger #5 schema-vs-handler consistency lint (Tier 1 MVP). Merge SHA `6ce7c0501`.
- u-d-b PR `<TBD>` — S2938 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Code shipped this session:**
- **`core/services/pa_tools_gap_map.py`** (+132 lines):
  - `_NUMBER_WORD_TO_INT` map + `_DOCSTRING_ACTION_COUNT_RE` regex.
  - `_NEGATIVE_CLAIM_PATTERNS` (3 domains: dispatch / mutation / feature_flag; Q3 refined with "does not dispatch" / "doesn't dispatch" / "side-effect free").
  - `_EVIDENCE_SIGNATURES` (celery primitives + curated service-layer async-dispatch functions like `rigby_mission_delegation.delegate_work_item` per Q3).
  - `lint_schema_vs_handler(schema, handler_source, handler_docstring) -> List[str]` — parse-based, no LLM, precision-first.
  - `build_gap_map()` wired to merge `lint_schema` + `lint_schema_vs_handler` output into `row['lints']`.
- **`core/management/commands/build_pa_tool_audit.py`** (+40 lines):
  - `_load_handler_module(handler_file_rel) -> (source, docstring)` helper with per-file cache keyed by absolute path. Silent-fail on OSError/SyntaxError. Multi-tool handler files (e.g. `td_handlers_content.py` hosting 6 tools) read once.
  - `_inspect()` extended to capture `handler_source` + `handler_docstring` per row.
- **`core/tests/test_pa_tools_gap_map_ledger_5.py`** (new, 181 lines): 11 contracts across 3 classes (`ActionCountDriftTests`, `NegativeClaimDriftTests`, `BuildGapMapIntegrationTests`). All pass in 0.001s.
- **Auto-gen doc regen** (`--include-validation-xref` shape preserved): `docs/PA_TOOL_AUDIT.md` + `docs/audits/PA_TOOLS_GAP_MAP.md` render 2 new lint tags on `rigby_work_item` row under existing "Schema quality lints" section (Q2 AGREE shape).

**Live backfill:** 117 tools scanned → 2 hits (both on `rigby_work_item`, both are the Ledger #39 case surfaced manually at S2937) → 0 false positives across 115 remaining wired tools.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3512 recycled clean at `sha=6ce7c0501964` via `make recycle-all` (surviving=none).
- Rigby verified: (1) both `handler_drift_*` tags render in PA_TOOL_AUDIT.md:158 + PA_TOOLS_GAP_MAP.md:165 + summary blocks; (2) `rigby_work_item action=list` returns clean `disabled_response` post-recycle (flag OFF).

**Governance:** none this session. D6 moratorium unchanged.

**Rigby Tool Gap Ledger:** no new entries. Ledger #5 promoted to substrate this ship.

Full session context: `docs/handoffs/SESSION_2938_LEDGER_5_LINT.md`.

---

## S2939 open sequence — SLICE 7 BATCH 2a (resumes after 1-session lint substrate)

**Natural next action:** open Batch 2a — 3 mutation-bearing tools with local-DB writes:
- **mission_verdict** — 3 mutation actions (certify/reject/defer); writes OpsRunEvent + flips OpsRun.status; **spreading** (OpsRunEvent has 2 post_save receivers: `broadcast_mission_verdict` + `escalate_mission_verdict_to_hai`); Rigby-gated auth.
- **newsletter_tool** — 4 mutation actions (prepare/outline/metrics/config) + 3 read actions (validate/list_issues/sources); **spreading** (Deliverable post_save → deliverable_mirror_signals); prepare fans out to 4 Deliverable writes.
- **rigby_work_item** — 4 mutation actions (acknowledge/resolve/ignore/delegate) + 1 read (list); flag-gated by `RIGBY_WORK_QUEUE_REVIEW_ENABLED` (default OFF); **spreading** (same OpsRunEvent receivers as mission_verdict when flag ON); `delegate` also async-dispatches via `rigby_mission_delegation` service (per Ledger #39).

### Batch 2a inventory (unchanged from S2937)

| Tool | Handler file | Mutation posture | §5c pre-flight |
|---|---|---|---|
| mission_verdict | `td_handlers_employee.py:434` (shared module — cross-link to employee_tool which ships in Batch 2b) | 3 mutations (all `spreading`) | 5c.3 = shared-module cross-link |
| newsletter_tool | `td_handlers_newsletter.py:27` | 4 mutations (all `spreading` via Deliverable receivers) | 5c.3 = dedicated |
| rigby_work_item | `td_handlers_rigby_work_queue.py:141` | 4 mutations (all `spreading`); flag-gated | 5c.2 = flag-gated, §6 LIVE-VERIFIES disabled_response; 5c.1 = **AUTO-FLAGGED by Ledger #5 lint (`handler_drift_action_count` + `handler_drift_negative_claim_dispatch`)** — call out in-doc, treat as auto-detected drift precedent |

### S2939 open sequence

1. **First-action lint pre-flight:** run `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` and grep for `handler_drift_*` on the 3 Batch 2a tools. Any hits become in-doc drift disposition in §5c.1 automatically (not manual scan). Verify:
   - mission_verdict + newsletter_tool: expected 0 handler_drift hits.
   - rigby_work_item: expected 2 hits (both known, both = Ledger #39 case).
2. Route bifurcated shape (Option C — LIVE-VERIFIED reads + ANALYZED mutations) + all-mutation-tool handling for mission_verdict to Rigby at S2939 T0 SIGN. Recycle the Q1/Q2/Q3 shape from S2937 (T1 already Chris-ratified).
3. Execute batch (3 docs + §5a tables + §5c dispositions per doc).
4. Live-verify read actions (newsletter validate/list_issues/sources; rigby_work_item list with flag OFF returning disabled_response).
5. Ledger appends if any drift surfaces.
6. PR + admin-merge + recycle + post-merge verify + close cascade.

### Alternative next actions (not blocked — still available if Chris redirects)

- **(A8) Signal Dispatches "Manual dispatch" button** (Rigby S2934 zoom-out fold — ~30 min).
- **(A9) Fourth signal-dispatch rule** — `demand_spike` (250 clusters) or `skill_demand` (131 clusters).
- **(A6) SignalCluster promotion audit** — only 0.58% of clusters are active.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.
- **(E) Tier 2 lint promotion** — envelope-JSON top-level-key parse against schema description text. Would catch `rigby_shift_brief` PARTIAL DRIFT (schema names 6 subsections; envelope has 4 undocumented top-level fields). Ledger #5 sub-substrate. ~1 session.
- **(F) Dry-run substrate design for the 5 batch-2 mutations (Ledger #38)** — enables live mutation verification of `blog_tool.approve/reject/generate` + `feedback_tool.submit/update`.

---

## What's forbidden at S2938 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2938 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

- **Ledger #5 Tier 2 (envelope-JSON parse)** — deferred per Rigby S2938 ZO AGREE. Would catch schema-description-vs-envelope-shape drift. Bring back when 2+ additional §5c.1 findings prove Tier 1 leaves detection gaps.
- **Ledger #5 Tier 3 (semantic distance between prose and field names)** — too fuzzy for MVP; needs curated corpus first.
- **Ledger #36 (blog_tool Deliverable/SelfBlog approve-path fix)** — extend `_handle_content_review` publish/archive branches to fall back to SelfBlog. Correctness bug candidate.
- **Ledger #37 (feedback_tool.update `.save()` → update_fields)** — ~1-line fix.
- **Ledger #38 (dry_run affordance across 5 batch-2 mutations)** — substrate design session. Blocks live mutation verification of Slice 6 batch 2 mutations AND Slice 7 batch 2a/2b/2c mutations.
- **Ledger #39 (rigby_work_queue module docstring stale)** — **NOW AUTO-DETECTED by Ledger #5 lint shipped this session.** ~5-min doc fix; bundle with any future rigby_work_queue touch (natural fold-in during Batch 2a next session).
- **`execution_history_tool` `hours` schema declaration** — ~3 min follow-up PR. Ledger entry #35 references.
- **Invalid-action non-gating consistency across Slice 6+7 handlers** — Ledger #5 consolidation candidate.
- **`zoom_out_tool include=aggregations` Rigby-wrapper investigation (S2937 §6.1a anomaly)** — PA-wrapper investigation. Bundle with any Rigby wrapper touch.
- **A8 — Signal Dispatches "Manual dispatch" UI button** — Rigby S2934 zoom-out fold.
- **A6 — SignalCluster promotion audit** — substrate investigation.
- **CompetitorAnalysisAgent hardening candidate** — S2929 deferred.
- **Dedicated `agent_execution_query` PA tool** — S2931 Ledger #33.
- **Shared `skip_in_test` decorator** — S2931 Ledger #34.
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A.
- **Bundled dev-env drift slate** — pyright warnings on `pa_tool_schemas.py` + now `build_pa_tool_audit.py` + `pa_tools_gap_map.py` (pre-existing dev-env drift; unchanged this ship — same class, deferred).
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
**Slice 7 — singleton bucket (9 tools across 8 handler files):** **BATCH 1 CLOSED at S2937 (3/9).** **Batch 2a deferred one session at S2938 for Ledger #5 substrate ship.** Batches 2a/2b/2c queued for S2939+.

**Substrate arcs CLOSED at S2938:** Ledger #5 (Tier 1 MVP — schema-vs-handler consistency lint). Tier 2 + Tier 3 deferred to future ships.

**Total remaining tools to close:** **6 across 5 handler files** (unchanged from S2937 close — Batch 2a re-queues clean).

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2938 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2938: zero A4 spend** — pure substrate progress (Ledger #5 lint promotion).
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2938)

See:
- **S2938 handoff (current):** `docs/handoffs/SESSION_2938_LEDGER_5_LINT.md`
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
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (no new entries S2938; Ledger #5 promoted to substrate).
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated with `--include-validation-xref`) + `docs/research/tools/validation/*.md` (109 per-tool validation docs post-S2937).
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
