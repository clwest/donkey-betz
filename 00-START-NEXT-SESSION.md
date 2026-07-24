# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2934 SHIPPED SIGNAL-DISPATCH OBSERVABILITY + THIRD RULE + ON-DEMAND HARNESS (Chris "Approved, ship it" ratification). Clean ~90-min diff. **S2935 OPENS CLEAN** — no forced first action.

**Refreshed 2026-07-24 (S2934 close).** Chris ratified bundled A4+A5+A7 at open ("Approved, ship it") after Claude+Rigby joint AGREE — Rigby zoom-out at joint sign-off argued the harness (A7) had to ship in the same PR as the dashboard (A4) because the observed 0.58% active-cluster rate meant A4 alone would read as a "dead dashboard" for hours/days waiting for a natural fire. Shipped as PR #3503 (merge SHA `242d6116c`).

**PRs shipped this session:**
- u-d-b PR [#3503](https://github.com/clwest/donkey-betz-platform/pull/3503) — S2934 A4+A5+A7 bundle, merged at `242d6116c`.
- u-d-b PR `<TBD>` — S2934 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Code shipped this session (net-new, 975-line insert-only diff):**
- **A4 — Signal Dispatches Workspace tab:** new endpoint `GET /api/v1/agents/signal-dispatches/` + `SignalDispatchesTab.tsx` mounted under System sub-tabs. 25/page table with pattern_type + outcome filters, detail panel with cluster metadata + agent execution UUID + input payload. Manual dispatches badged so they never blend with reactive-pipeline analytics.
- **A5 — third rule:** `opportunity_window → OpportunityScoringAgent` added to `SIGNAL_DISPATCH_RULES`. Verified: 33 total execs / 96 effectiveness / 100% recent success + 117 clusters exist (1 active at open).
- **A7 — on-demand harness:** `python manage.py dispatch_signal --cluster-id X [--rule-key K] [--force] [--sync]`. Rigby SIGN safety envelope: cluster-id required, idempotent guard (5-min window), scan_run_id='manual' labeling, no batch mode, rule auto-pick with 0/2+ error.
- **15 new tests, all pass.** 36/36 total for the signal-dispatch surface. Django check clean.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3503 recycled clean at `sha=242d6116c2bd` via `make recycle-all`.
- **Reactive path validated (unexpected bonus):** beat scheduler picked up the new A5 rule and fired `scan-signal-dispatch-rules` at 16:20:00 UTC — 90 seconds after merge. Scanner found active opportunity_window cluster `62bdb598…` ("Chatgpt, Openai opportunity window"), dispatched OpportunityScoringAgent, execution succeeded (`execution_id=37c66dd7-d1e5-49c6-b04c-2fea5efc442e`). Row `scan_run_id=b6d3b2b747fc44e8`. **A5 fires reactively for real, not just theoretically.**
- **Idempotent guard validated:** manual `dispatch_signal --sync` (no `--force`) correctly errored with `Idempotent guard: dispatch 798587a9-... exists within 5min window`.
- **Manual `--force` + labeling validated:** manual dispatch row created with `scan_run_id='manual'` (Rigby SIGN safety condition satisfied). Sync agent execution completed in-flight during close cascade — see handoff §Post-merge for outcome.
- **A4 endpoint verified via Rigby tool surface:** HTTP 200, correct row count.

**Governance:** none this session. D6 moratorium unchanged. Zero new forbidden-entry candidates.

**Rigby Tool Gap Ledger:** one LOW observation (S2934 A7 verification): Rigby has no `terminal_tool` in her PA surface, so she couldn't run the `dispatch_signal` mgmt command herself for post-merge verification. Same class as the S2933 `orm_inspect_tool` allowlist gap. Not opening as a formal Ledger entry yet; will promote if a third tool-surface gap of the "operator-critical CLI unreachable from PA" shape surfaces.

Full session context: `docs/handoffs/SESSION_2934_SIGNAL_DISPATCH_OBSERVABILITY.md`.

---

## S2935 open sequence — CHRIS DIRECTIVE S2934 CLOSE: RESUME THE PA TOOLS SWEEP

**Ratified at S2934 close (2026-07-24):** After Claude surfaced the honest sweep-completeness fraction (13 tools completely untested / 21 of 117 total lack full coverage / 18% remaining), Chris directed: **"resume the sweep next session."** S2935 first action is Slice 6.

### First action — Slice 6: `td_handlers_content.py` (6 untested tools)

**Batch candidates (all currently `untested` per `docs/audits/PA_TOOLS_GAP_MAP.md`):**

| Tool | File |
|---|---|
| `blog_tool` | `core/services/td_handlers_content.py` |
| `execution_history_tool` | `core/services/td_handlers_content.py` |
| `feedback_tool` | `core/services/td_handlers_content.py` |
| `learning_patterns_tool` | `core/services/td_handlers_content.py` |
| `recent_activity_tool` | `core/services/td_handlers_content.py` |
| `surgical_moves_status_tool` | `core/services/td_handlers_content.py` |

**Methodology anchors:**

- **Path B ratified S2892** (`project_pa_tools_sweep_path_b_open`) — engineering-first sweep, code-defined shape, not DB config.
- **Substrate arc thread order** (`project_row_161_substrate_arc_opened_s2900`) — T1c → T1a → T1b.
- **T1b canonical template:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`.
- **Prior slice close artifacts** for pattern reference: Slice 5 = `docs/audits/pa_tools/substrate/slice_5_close_artifact.md`; Slice 4 CLOSED S2924; Slice 3 CLOSED S2917; Slice 2 CLOSED S2912.
- **Batch shape:** S2907 T0 Fold E ratified 2026-07-23 (`project_s2908_batch_4_shape_break_commitment`) applied to Slice 5; for Slice 6, Rigby's zoom-out should pick the batch shape at S2935 T0 SIGN. Uniform READ_ONLY, mixed-scoped-to-READ_ONLY-subset, and gated-write-dry_run-only remain the three canonical shapes.

**S2935 open sequence:**

1. Read `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` + the Slice 5 close artifact for shape reference.
2. Route batch composition to Rigby (which 3-4 of the 6 tools to include in batch 1, batch shape decision per Fold E) — joint AGREE, then Chris yes/no per `feedback_claude_rigby_agree_first_chris_yes_no`.
3. Execute the batch. Docs land in `docs/research/tools/validation/<tool_name>.md`; auto-generated summary updates in `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md`.

### Remaining untested tools beyond Slice 6 (7 tools across 7 handler files, for future slices)

Singleton-per-file bucket — pick up as a bundled Slice 7 after Slice 6 closes:

- `code_job_tool` (`td_handlers_codejobs.py`)
- `employee_tool` + `mission_verdict` (`td_handlers_employee.py`)
- `newsletter_tool` (`td_handlers_newsletter.py`)
- `railway_tool` (`td_handlers_railway.py`)
- `rigby_shift_brief_tool` (`td_handlers_rigby_shift_brief.py`)
- `rigby_work_item` (`td_handlers_rigby_work_queue.py`)
- `spider_data_aggregation_tool` (`spider_data_aggregation_tool.py`)
- `zoom_out_tool` (`td_handlers_governance.py`)

### Not blocked — still available if Chris redirects mid-open

- **(A8) Signal Dispatches "Manual dispatch" button** (Rigby S2934 zoom-out fold — ~30 min).
- **(A9) Fourth signal-dispatch rule** — `demand_spike` (250 clusters) or `skill_demand` (131 clusters). One-line rule + agent verification.
- **(A6) SignalCluster promotion audit** — only 0.58% of clusters are active; investigate `SignalAggregationService`.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.

---

## What's forbidden at S2934 (D6 MORATORIUM still in force)

All S2925/S2926/S2927/S2928/S2929/S2931/S2932/S2933 forbidden entries carry forward.

**S2929 first-instance entries (still awaiting 2nd corroborating trigger):**
- No "handoff shape misclassification" Fold promotion without 2nd instance.
- No "tool-to-class routing anomaly" Fold promotion without 2nd instance.
- No "Fold ratification over-count via unverified handoff description" Fold promotion without 2nd instance.

**S2934 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

- **A8 — Signal Dispatches "Manual dispatch" UI button** — Rigby S2934 zoom-out fold. Explicitly deferred at close per Chris's engineering-bias-over-audit directive; promote to next slate if Chris signals interest.
- **A6 — SignalCluster promotion audit** — 5/862 active rate observed at S2934 open. Substrate investigation, not net-new build.
- **CompetitorAnalysisAgent hardening candidate** — S2929 Chris D-verdict deferred; S2930 R2 explicitly excluded from Fold scope.
- **Dedicated `agent_execution_query` PA tool** — S2931 Ledger #33 chose the ~30 min quick-win over the ~1-2 hr dedicated tool.
- **Shared `skip_in_test` decorator** — S2931 Ledger #34 chose per-receiver gate over shared decorator.
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A.
- **Bundled dev-env drift slate** — S2919 narrative + S2925 Ledger legacy + AgentTaskExecution pre-existing pyright drift + S2927-observed `td_handlers_agents.py` pyright drift + S2931-observed `agent_execution_bridge.py` pyright drift + S2933-observed `tasks.py` pre-existing arg-type drift + `celery.py` pre-existing property-assign drift + S2934-observed `signal_dispatch_service.py:226` `dispatch_agent_for_signal_cluster.delay` pyright inference drift + `views_signal_dispatch.py` ambient `request.GET` unknown-type drift.
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate + Ledger candidate: media_tool.delete IRREVERSIBLE** — unchanged.
- **S2909-S2929 Ledger candidates** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **S2919 narrative_tool dev-env drift** — unchanged.
- **S2925 Ledger #34 (LOW, distinct from S2931's #34)** — broader stale-model latent bug; multi-hour cleanup deferred.
- **S2926 Ledger candidate — AgentTaskExecution pre-existing pyright drift** — bundled dev-env drift candidate.
- **R1 fleet reject-mode flip** — deferred.
- **Docs restructuring arc** (`project_docs_restructuring_arc_queued`) — Chris-ratified S2800, still queued.
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.
- **S2933 A3 v1 admin surface** — deferred by design (Path B ratified). Migrate to DB config table if runtime editability becomes valuable.

---

## Sweep progress tracker (Path B ratified S2892) — UNCHANGED at S2934

**Slice 1 — `td_handlers_ops` (17 registered tools):** UNCHANGED.
**Slice 2 — `td_handlers_agents` (25 tools):** CLOSED at S2912.
**Slice 3 — `td_handlers_core` (22 tools):** CLOSED at S2917 (22/22).
**Slice 4 — `td_handlers_gateway` (17 tools):** CLOSED at S2924 (17/17).
**Slice 5 — `tool_dispatcher` (14 tools):** CLOSED at S2928 (14/14). ✅

**Total remaining tools to close:** **15 across 8 handler files** (unchanged — S2934 shipped engineering primitive, no PA-tools sweep work).

**Substrate arcs CLOSED at S2934:** none. S2934 shipped 1 engineering PR (signal-dispatch observability bundle).

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2934 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2934: zero A4 spend** — pure engineering (signal-dispatch observability bundle).
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2934)

See:
- **S2934 handoff (current):** `docs/handoffs/SESSION_2934_SIGNAL_DISPATCH_OBSERVABILITY.md`
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
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2929 regression test:** `core/tests/test_base_business_research_agent_synthesis_gate.py` (5 tests, all pass)
- **S2930 Agent Runs endpoint test:** `core/tests/test_agent_runs_list_endpoint.py` (7 tests, all pass)
- **S2930 Agent Runs tab file:** `frontend/src/pages/workspace/tabs/AgentRunsTab.tsx`
- **S2931 Ledger #33 + #34 bundle test:** `core/tests/test_s2931_ledger_33_34_bundle.py` (8 tests, all pass)
- **S2932 A2 fail-loud gate test:** `core/tests/test_content_strategy_agent_fail_loud_gate.py` (4 tests, all pass)
- **S2933 A3 v1 signal-dispatch test:** `core/tests/test_signal_dispatch_service.py` (23 tests total after S2934 — 20 from S2933 + 3 new)
- **S2933 A3 v1 model:** `core/models_signal_dispatch.py`
- **S2933 A3 v1 service (SIGNAL_DISPATCH_RULES — 3 rules after S2934):** `core/services/signal_dispatch_service.py`
- **S2933 A3 v1 retry lever:** `python manage.py resend_signal_dispatch --help`
- **S2934 A4 endpoint:** `core/views_signal_dispatch.py` + `GET /api/v1/agents/signal-dispatches/`
- **S2934 A7 on-demand harness:** `python manage.py dispatch_signal --help`
- **S2934 A4 tab component:** `frontend/src/pages/workspace/tabs/SignalDispatchesTab.tsx`
- **S2934 test file:** `core/tests/test_s2934_signal_dispatch_harness.py` (13 tests, all pass)
- **BaseBusinessResearchAgent content-shape FAIL Fold (RATIFIED S2928, REMEDIATED S2929, NARROW-SCOPED + CLOSED S2930):** engineering item in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` — deliverable `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5`.
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (S2930 entries #33 + #34 both RESOLVED at S2931 PR #3497).
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (100 per-tool validation docs post-S2928)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
