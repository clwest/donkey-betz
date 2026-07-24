# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2933 SHIPPED A3 v1 SIGNAL-TRIGGERED AGENT AUTO-DISPATCH (Chris "Proceed with Path 2" ratification). Clean ~90-min diff. **S2934 OPENS CLEAN** — no forced first action.

**Refreshed 2026-07-24 (S2933 close).** Chris ratified A3 at open ("proceed with A3"), then re-ratified after Rigby zoom-out on rule-metastasis risk ("Proceed with Path 2" — code-defined mapping dict over DB config table). Shipped as PR #3501 (merge SHA `68705a69e`).

**PRs shipped this session:**
- u-d-b PR [#3501](https://github.com/clwest/donkey-betz-platform/pull/3501) — S2933 A3 v1, merged at `68705a69e`.
- u-d-b PR `<TBD>` — S2933 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Code shipped this session (net-new, 1,061-line insert-only diff):**
- **New reactive-orchestration primitive** — Celery beat `scan-signal-dispatch-rules` fires every 5 min, walks code-defined `(SignalCluster.pattern_type → AGENT_MAP agent)` rules, enqueues per-cluster dispatch tasks, records outcome in new `SignalDispatch` audit table.
- **v1 rules (Rigby-verified via `agent_introspection_tool`):** `trend_emergence` → `TrendAnalysisAgent` (110 executions / 100% 7d success), `content_gap` → `ContentStrategyAgent` (post-S2932 fail-loud gate).
- **Safety nets:** global `SIGNAL_DISPATCH_MAX_PER_SCAN=10` cap + per-rule `max_per_day=10` cap + `is_actionable` gate + `SIGNAL_DISPATCH_ENABLED` kill switch.
- **Fire-once with retry lever:** `SignalDispatch.outcome` + `error_summary` populated at dispatch-time; failed dispatch does NOT block scanner retry; manual retry via `manage.py resend_signal_dispatch --dispatch-id X`.
- **20 tests, all pass.** S2932 gate tests still pass (5/5). Django check clean.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3501 recycled clean at `sha=68705a69e4f6` via `make recycle-all`.
- Rigby verification: `db_health_tool verify_table core_signaldispatch` — 12 expected columns present; `scheduled_tasks_tool` — `scan-signal-dispatch-rules` enabled + `total_runs=1` at 15:50:00 (beat scheduler already picking it up 5 min after merge); `delegate_to_agent TrendAnalysisAgent` smoke returned `task_id` cleanly (confirms `AgentRouter.route(agent_name='TrendAnalysisAgent')` path works — same path `SignalDispatchService.execute_dispatch` uses).
- **0 SignalDispatch rows yet** — expected. 862 SignalClusters exist but none currently `status='active'` matching v1 pattern_types. Pipeline is live; rows will accumulate as SignalAggregationService promotes matching clusters.

**Governance:** none this session. D6 moratorium unchanged. Zero new forbidden-entry candidates.

**Rigby Tool Gap Ledger:** one LOW observation (S2933 `orm_inspect_tool` doesn't allowlist `SignalDispatch` + `PeriodicTask`; workaround via `db_health_tool` was clean, not opening as formal entry unless second trigger surfaces). #33+#34 remain RESOLVED at S2931 PR #3497.

Full session context: `docs/handoffs/SESSION_2933_A3_SIGNAL_DISPATCH_V1.md`.

---

## S2934 open sequence — CLEAN, no governance decision blocking

No R-verdict pending. Fresh arc-scope surface:

- **(A) NET-NEW ENGINEERING** — several candidate leans:
  - **(A4) Signal-dispatch v1.1 — real observability path:** if any `SignalDispatch` rows have accumulated between S2933 close and S2934 open, produce a "signal-dispatch triage" surface (either Rigby's inbox — 5 min doc-add — or a lightweight Workspace tab). Trigger: check `SignalDispatch.objects.count()` at S2934 open; if > 0, this is the natural follow-on.
  - **(A5) Add a 3rd/4th signal-dispatch rule:** if Chris wants to expand coverage — e.g., `opportunity_window` → some scoring agent, `demand_spike` → market_research/research pathway. One-line addition to `SIGNAL_DISPATCH_RULES` + a smoke test each.
  - **(A6) SignalCluster `status='active'` promotion audit:** the S2933 pipeline is gated on `is_actionable` (status='active' AND strength ≥ 0.5 AND confidence ≥ 0.5). Fresh sample shows 862 clusters, most in `detecting`. Worth verifying `SignalAggregationService` is actually promoting clusters at reasonable cadence — if not, S2933's dispatcher will fire rarely.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(C) Slice 6 sweep continuation** — `td_handlers_content.py` (6 tools).
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.

**Recommend:** open S2934 by counting `SignalDispatch.objects.all().count()` first. If > 0, natural continuation is A4 (observability); if 0, either A5 (rule expansion) or A6 (upstream audit) are lean net-new picks.

---

## What's forbidden at S2933 (D6 MORATORIUM still in force)

All S2925/S2926/S2927/S2928/S2929/S2931/S2932 forbidden entries carry forward.

**S2929 first-instance entries (still awaiting 2nd corroborating trigger):**
- No "handoff shape misclassification" Fold promotion without 2nd instance.
- No "tool-to-class routing anomaly" Fold promotion without 2nd instance.
- No "Fold ratification over-count via unverified handoff description" Fold promotion without 2nd instance.

**S2933 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

- **CompetitorAnalysisAgent hardening candidate** — S2929 Chris D-verdict deferred; S2930 R2 explicitly excluded from Fold scope.
- **Dedicated `agent_execution_query` PA tool** — S2931 Ledger #33 chose the ~30 min quick-win over the ~1-2 hr dedicated tool.
- **Shared `skip_in_test` decorator** — S2931 Ledger #34 chose per-receiver gate over shared decorator.
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A.
- **Bundled dev-env drift slate** — S2919 narrative + S2925 Ledger legacy + AgentTaskExecution pre-existing pyright drift + S2927-observed `td_handlers_agents.py` pyright drift + S2931-observed `agent_execution_bridge.py` pyright drift + S2933-observed `tasks.py` pre-existing arg-type drift + `celery.py` pre-existing property-assign drift.
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

## Sweep progress tracker (Path B ratified S2892) — UNCHANGED at S2933

**Slice 1 — `td_handlers_ops` (17 registered tools):** UNCHANGED.
**Slice 2 — `td_handlers_agents` (25 tools):** CLOSED at S2912.
**Slice 3 — `td_handlers_core` (22 tools):** CLOSED at S2917 (22/22).
**Slice 4 — `td_handlers_gateway` (17 tools):** CLOSED at S2924 (17/17).
**Slice 5 — `tool_dispatcher` (14 tools):** CLOSED at S2928 (14/14). ✅

**Total remaining tools to close:** **15 across 8 handler files** (unchanged — S2933 shipped engineering primitive, no PA-tools sweep work).

**Substrate arcs CLOSED at S2933:** none. S2933 shipped 1 engineering PR (new reactive-orchestration primitive).

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2933 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2933: zero A4 spend** — pure engineering (signal-triggered agent auto-dispatch v1).
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2933)

See:
- **S2933 handoff (current):** `docs/handoffs/SESSION_2933_A3_SIGNAL_DISPATCH_V1.md`
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
- **S2933 A3 v1 signal-dispatch test:** `core/tests/test_signal_dispatch_service.py` (20 tests, all pass)
- **S2933 A3 v1 model:** `core/models_signal_dispatch.py`
- **S2933 A3 v1 service (SIGNAL_DISPATCH_RULES lives here):** `core/services/signal_dispatch_service.py`
- **S2933 A3 v1 retry lever:** `python manage.py resend_signal_dispatch --help`
- **BaseBusinessResearchAgent content-shape FAIL Fold (RATIFIED S2928, REMEDIATED S2929, NARROW-SCOPED + CLOSED S2930):** engineering item in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` — deliverable `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5`.
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (S2930 entries #33 + #34 both RESOLVED at S2931 PR #3497).
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (100 per-tool validation docs post-S2928)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
