# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2937 OPENED SLICE 7 (final sweep bucket) WITH BATCH 1: 3 pure-read validation docs (Chris "yes proceed" ratification). Template §5c "Contract ↔ Implementation Consistency" retro-fold shipped BEFORE Batch 1 + Ledger #39 (rigby_work_queue docstring drift). **S2938 OPENS WITH BATCH 2a (3 local-DB-write mutation tools — mission_verdict + newsletter_tool + rigby_work_item)**.

**Refreshed 2026-07-24 (S2937 close).** Chris ratified 4-batch plan at S2937 T1 ("yes proceed") after Claude+Rigby joint AGREE with 3-way batch 2 sub-split edit (Rigby's F-BLOCKING isolating railway_tool as own Batch 2c) + template §5c retro-fold BEFORE Batch 1 ships. Rigby executed Ledger #39 append (record-only per Chris T1 verdict) in one atomic tool call. Shipped as PR #3510 (merge SHA `0b07da219`).

**PRs shipped this session:**
- u-d-b PR [#3510](https://github.com/clwest/donkey-betz-platform/pull/3510) — S2937 Slice 7 batch 1 (3 pure-read validation docs + template §5c retro-fold + Ledger #39). Merge SHA `0b07da219`.
- u-d-b PR `<TBD>` — S2937 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Code shipped this session:**
- **Template amendment (T1b canonical template v1):**
  - `_TEMPLATE_per_tool_validation.md` §5c "Contract ↔ Implementation Consistency" mandatory checklist added between §5b and §6. 3 items: (5c.1) handler/module header claims match action reality; (5c.2) gating truth matches runtime behavior; (5c.3) shared handler-file coupling noted. +57 lines.
- **3 new validation docs (T1b sweep template v1, all `pass`):**
  - `rigby_shift_brief_tool_validation.md` (1 action: generate, LIVE-VERIFIED 4083ms; §5c.1 PARTIAL DRIFT — schema description says "suggested next action" but JSON key is `next_action`; undocumented top-level `traffic_light`+`summary_text`+`metadata.*` response fields).
  - `spider_data_aggregation_tool_validation.md` (1 action: aggregate, LIVE-VERIFIED 144ms; 9 by_data_type buckets — news 1408 / financial 1189 / tech 619 top-3).
  - `zoom_out_tool_validation.md` (1 action: list, LIVE-VERIFIED 5ms; 162 total_rows / 56+59+47 classification split; §6.1a anomaly — `include=aggregations` param not propagated by Rigby wrapper, deferred as wrapper-investigation candidate).
- **Blast-radius classification:** All 3 tools pure-read — no §5a needed.
- **Rigby Tool Gap Ledger entry #39** — `td_handlers_rigby_work_queue.py` module docstring stale (says "four actions" + "No agent dispatch" but 5th action `delegate` DOES async-dispatch via `rigby_mission_delegation`). Record-only per Chris T1; ~5-min fix bundled with future rigby_work_queue touch.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3510 recycled clean at `sha=0b07da219a6b` via `make recycle-all` (surviving=none).
- Rigby verified 3 tools post-recycle: `spider_data_aggregation` + `zoom_out` show EXACT envelope shape match (same top spiders, same total_rows/counts); `rigby_shift_brief` exercised (tool_runs confirms dispatch; full envelope shape stable per handler contract).

**Gap-map ratchet:** validated_full 89 → 92 (+3); untested 9 → 6 (-3); template pass 86 → 89 (+3). Total per-tool docs 106 → 109. No regressions.

**Governance:** none this session. D6 moratorium unchanged. Zero new forbidden-entry candidates.

**Rigby Tool Gap Ledger:** 1 entry appended (#39). **Ledger #5 systemic detection lint is at or past its promotion threshold** (schema-under-describes-handler observed 3+ cycles: S2935 + S2936 + S2937). Recommend promoting to substrate work in a dedicated session before continuing sweep close.

Full session context: `docs/handoffs/SESSION_2937_SLICE_7_BATCH_1.md`.

---

## S2938 open sequence — SLICE 7 BATCH 2a (3 local-DB-write mutation tools)

**Natural next action:** open Batch 2a — 3 mutation-bearing tools with local-DB writes:
- **mission_verdict** — 3 mutation actions (certify/reject/defer); writes OpsRunEvent + flips OpsRun.status; **spreading** (OpsRunEvent has 2 post_save receivers: `broadcast_mission_verdict` + `escalate_mission_verdict_to_hai`); Rigby-gated auth.
- **newsletter_tool** — 4 mutation actions (prepare/outline/metrics/config) + 3 read actions (validate/list_issues/sources); **spreading** (Deliverable post_save → deliverable_mirror_signals); prepare fans out to 4 Deliverable writes.
- **rigby_work_item** — 4 mutation actions (acknowledge/resolve/ignore/delegate) + 1 read (list); flag-gated by `RIGBY_WORK_QUEUE_REVIEW_ENABLED` (default OFF); **spreading** (same OpsRunEvent receivers as mission_verdict when flag ON); `delegate` also async-dispatches via `rigby_mission_delegation` service (per Ledger #39).

### Batch 2a inventory

| Tool | Handler file | Mutation posture | §5c pre-flight |
|---|---|---|---|
| mission_verdict | `td_handlers_employee.py:434` (shared module — cross-link to employee_tool which ships in Batch 2b) | 3 mutations (all `spreading`) | 5c.3 = shared-module cross-link |
| newsletter_tool | `td_handlers_newsletter.py:27` | 4 mutations (all `spreading` via Deliverable receivers) | 5c.3 = dedicated |
| rigby_work_item | `td_handlers_rigby_work_queue.py:141` | 4 mutations (all `spreading`); flag-gated | 5c.2 = flag-gated, §6 LIVE-VERIFIES disabled_response; 5c.1 = drift already known (Ledger #39) — call out in-doc |

### First action — Batch 2a T0 SIGN routing

**S2938 first action:** author 3 validation docs under bifurcated Option C shape (§6 LIVE-VERIFIED for read actions + §5a ANALYZED-NOT-EXECUTED for mutations). Route T0 SIGN to Rigby for AGREE on:
1. Does `mission_verdict` require any special handling since ALL 3 actions are mutations (no §6 LIVE reads to bifurcate)? Options: (a) §6 ANALYZED-only per-action with signal-grep evidence; (b) exercise `describe`/`status` via sibling `employee_tool` in Batch 2b to prove OpsRun/OpsRunEvent shape.
2. rigby_work_item §6 with flag=OFF — verify all 4 mutation actions return `_disabled_response`; separately note in §5a what the actions WOULD do if flag=ON.
3. Ledger #39 cross-link in rigby_work_item validation doc — flag known docstring drift up-front so readers don't mistrust the doc's §5c.1 disposition.

Then execute the batch (3 docs + §5a tables) + append any additional Ledger entries surfaced.

**Recommended shape:** Option C bifurcated (matches Slice 6 batch 2 precedent). Rigby AGREE at T0 SIGN.

### S2938 open sequence

1. Read the 3 handler entrypoints (already read at S2937 T0 — just refresh line numbers if changed).
2. Grep signal receivers for OpsRun / OpsRunEvent / Deliverable / RigbyWorkItem (already grepped at S2937 T0 — confirm no drift).
3. Route bifurcated shape + all-mutation-tool handling to Rigby at S2938 T0 SIGN.
4. Execute batch (3 docs + §5a tables + §5c dispositions per doc).
5. Live-verify read actions (newsletter validate/list_issues/sources; rigby_work_item list with flag OFF returning disabled_response).
6. Ledger appends if any drift surfaces.
7. PR + admin-merge + recycle + post-merge verify + close cascade.

### Alternative next actions (not blocked — still available if Chris redirects)

- **(P) Promote Ledger #5 systemic detection lint to substrate** — 3+ cycle threshold met. Design a schema-vs-handler param-set consistency lint in `pa_tools_gap_map.py` before continuing sweep. Estimate: 1-2 sessions. Would unblock cleaner §5c.1 dispositions for remaining 6 tools.
- **(A8) Signal Dispatches "Manual dispatch" button** (Rigby S2934 zoom-out fold — ~30 min).
- **(A9) Fourth signal-dispatch rule** — `demand_spike` (250 clusters) or `skill_demand` (131 clusters).
- **(A6) SignalCluster promotion audit** — only 0.58% of clusters are active.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.
- **(E) Dry-run substrate design for the 5 batch-2 mutations (Ledger #38)** — enables live mutation verification of `blog_tool.approve/reject/generate` + `feedback_tool.submit/update`.

---

## What's forbidden at S2937 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2937 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

- **Ledger #5 systemic detection lint promotion** — 3-cycle threshold met (S2935 + S2936 + S2937). Recommend dedicated session; substrate scope. Blocks cleaner §5c.1 dispositions for the remaining 6 Slice 7 tools.
- **Ledger #36 (blog_tool Deliverable/SelfBlog approve-path fix)** — extend `_handle_content_review` publish/archive branches to fall back to SelfBlog. Correctness bug candidate.
- **Ledger #37 (feedback_tool.update `.save()` → update_fields)** — ~1-line fix.
- **Ledger #38 (dry_run affordance across 5 batch-2 mutations)** — substrate design session. Blocks live mutation verification of Slice 6 batch 2 mutations AND Slice 7 batch 2a/2b/2c mutations.
- **Ledger #39 (rigby_work_queue module docstring stale)** — ~5-min doc fix. Bundle with any future rigby_work_queue touch.
- **`execution_history_tool` `hours` schema declaration** — ~3 min follow-up PR. Ledger entry #35 references.
- **Invalid-action non-gating consistency across Slice 6+7 handlers** — `recent_activity_tool` + `surgical_moves_status_tool` + `rigby_shift_brief_tool` + `spider_data_aggregation_tool` + `zoom_out_tool` all use in-envelope error returns (not `raise ValueError`) unlike the execution_history_tool / learning_patterns_tool pattern. Ledger #5 candidate for consolidation.
- **`zoom_out_tool include=aggregations` Rigby-wrapper investigation (S2937 §6.1a anomaly)** — the `include` param may not have propagated through Rigby's dispatch surface at S2937 T0 verify. Not a tool bug; PA-wrapper investigation. Bundle with any Rigby wrapper touch.
- **A8 — Signal Dispatches "Manual dispatch" UI button** — Rigby S2934 zoom-out fold.
- **A6 — SignalCluster promotion audit** — substrate investigation.
- **CompetitorAnalysisAgent hardening candidate** — S2929 deferred.
- **Dedicated `agent_execution_query` PA tool** — S2931 Ledger #33.
- **Shared `skip_in_test` decorator** — S2931 Ledger #34.
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A.
- **Bundled dev-env drift slate** — pyright warnings on `pa_tool_schemas.py` (pre-existing dev-env drift; unchanged this ship).
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
**Slice 7 — singleton bucket (9 tools across 8 handler files):** **BATCH 1 CLOSED at S2937 (3/9).** Batches 2a/2b/2c queued.

**Total remaining tools to close:** **6 across 5 handler files** (down from 9 at S2937 open).

**Substrate arcs CLOSED at S2937:** none (template §5c retro-fold shipped inline with Batch 1). S2937 shipped 1 sweep-progress PR + 1 template amendment PR (bundled) + 1 Ledger entry.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2937 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2937: zero A4 spend** — pure substrate progress (Slice 7 batch 1 ship + template retro-fold).
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2937)

See:
- **S2937 handoff (current):** `docs/handoffs/SESSION_2937_SLICE_7_BATCH_1.md`
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
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entry #39 added S2937 — rigby_work_queue module docstring stale).
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (109 per-tool validation docs post-S2937).
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
