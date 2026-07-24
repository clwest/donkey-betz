# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2936 SHIPPED SLICE 6 BATCH 2 → SLICE 6 CLOSED (Chris "yes proceed" ratification). 2 validation docs (blog_tool + feedback_tool) under bifurcated Option C shape + 3 Ledger entries + clean substrate progress. **S2937 OPENS WITH SLICE 7 (singleton bucket — 9 tools across 8 handler files)**.

**Refreshed 2026-07-24 (S2936 close).** Chris ratified Option C at S2936 T1 ("yes proceed") after Claude+Rigby joint AGREE with 2 F-BLOCKINGs (bifurcated §6 LIVE vs §5a ANALYZED labeling + Deliverable/SelfBlog approve-path correctness trap Ledger). Rigby executed the Ledger append (3 entries: #36/#37/#38) in one atomic tool call. Shipped as PR #3508 (merge SHA `a681b7ec0`).

**PRs shipped this session:**
- u-d-b PR [#3508](https://github.com/clwest/donkey-betz-platform/pull/3508) — S2936 Slice 6 batch 2 CLOSE (blog_tool + feedback_tool validation docs, Option C bifurcated shape), merged at `a681b7ec0`.
- u-d-b PR `<TBD>` — S2936 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Code shipped this session:**
- **2 new validation docs (T1b sweep template v1, both `pass`):**
  - `blog_tool_validation.md` (8 actions: 5 read LIVE-VERIFIED + 3 mutation ANALYZED-NOT-EXECUTED, §5b Appendix A for `generate` async-fanout).
  - `feedback_tool_validation.md` (4 actions: 2 read LIVE-VERIFIED + 2 mutation ANALYZED-NOT-EXECUTED, both `contained` per zero-receiver grep).
- **Blast-radius classification (§5a 4-tier per Rigby taxonomy S2921):**
  - `blog_tool.approve/reject`: **spreading** (or contained if `RIGBY_EVENT_INTAKE_ENABLED=False` — current default).
  - `blog_tool.generate`: **external + cascading** — Celery `apply_async` + LLM invocation.
  - `feedback_tool.submit/update`: **contained** — zero post_save receivers on UserFeedback.
- **Rigby Tool Gap Ledger entries #36 + #37 + #38** — blog_tool Deliverable/SelfBlog approve-path gap + feedback_tool `.save()` write-scope drift + missing `dry_run` affordance across 5 batch-2 mutations.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3508 recycled clean at `sha=a681b7ec09a1` via `make recycle-all` (surviving=none).
- Rigby verified 4 tools post-recycle: `blog_tool action=stats` + `blog_tool action=recent days=7` + `feedback_tool action=stats` + `feedback_tool action=list limit=5`. Envelope shapes stable across all 4; `blog_tool.recent` shows data-condition drift (count 10→0, same total=204, envelope shape stable — documented behavior per validation doc §5).

**Gap-map ratchet:** validated_full 87 → 89 (+2); untested 11 → 9 (-2); template pass 84 → 86 (+2). No regressions.

**Governance:** none this session. D6 moratorium unchanged. Zero new forbidden-entry candidates.

**Rigby Tool Gap Ledger:** 3 entries appended (#36/#37/#38). Ledger #5 systemic detection lint approaches third-instance promotion threshold — S2935 (schema-under-describes-handler drift) + S2936 (5 sub-drifts noted) reinforce.

Full session context: `docs/handoffs/SESSION_2936_SLICE_6_BATCH_2_CLOSE.md`.

---

## S2937 open sequence — SLICE 7 (singleton bucket)

**Natural next action:** open Slice 7 — 9 tools across 8 handler files, no shared handler-file coupling. This is the final sweep bucket before the sweep closes.

### Slice 7 inventory (9 tools across 8 handler files)

| Tool | Handler file | Mutation posture (from schema) |
|---|---|---|
| `code_job_tool` | `core/services/td_handlers_code_jobs.py` (or similar) | TBD — read at T0 |
| `employee_tool` | `core/services/td_handlers_employees.py` (or similar) | Likely has update/create actions |
| `mission_verdict` | (same handler as employee_tool per S2934 A7 harness) | Mutation-heavy (records verdicts) |
| `newsletter_tool` | `core/services/td_handlers_newsletter.py` | Likely mutation-bearing (create/publish) |
| `railway_tool` | `core/services/td_handlers_railway.py` | External (Railway API) — probably risky |
| `rigby_shift_brief_tool` | `core/services/td_handlers_rigby_shift_brief.py` | TBD — read at T0 |
| `rigby_work_item` | `core/services/td_handlers_rigby_work_queue.py` | Mutation (queue ops) |
| `spider_data_aggregation_tool` | `core/services/spider_data_aggregation_tool.py` | Read-only probable |
| `zoom_out_tool` | `core/services/td_handlers_governance.py` | Read-only probable |

### First action — Slice 7 batch composition at T0 SIGN

**S2937 first action:** read all 8 handler files (or first 3-4 by hazard classification) + surface batch composition options to Rigby.

Three canonical shapes per S2907 Fold E:
1. **Split by handler file** — 8 batches over ~4 sessions (each session covers 2-3 tools).
2. **Split by mutation posture** — 2 batches: pure-read subset (spider_data_aggregation + zoom_out + rigby_shift_brief likely) then mutation subset (railway + employee + mission_verdict + newsletter + rigby_work_item + code_job).
3. **Split by risk posture** — touch railway (external Railway API) + employee/mission_verdict (governance-adjacent) last; ship the safe read-only tools first.

**Recommended: Option 2 (mutation-posture split)** — matches Slice 6 batch-1/batch-2 pattern (pure-read first, mutation second). Rigby picks at T0 SIGN.

### S2937 open sequence

1. Read all 8 handler files (or first 3-4 by hazard classification).
2. Grep signal receivers for the models each tool touches (mission_verdict → OpsRun/OpsRunEvent, railway → Railway API state, etc.).
3. Route batch composition + shape decision to Rigby at S2937 T0 SIGN — joint AGREE, then Chris yes/no per `feedback_claude_rigby_agree_first_chris_yes_no`.
4. Execute the batch (2-4 docs + §5a tables where mutations declared).
5. Slice 7 may close in 1-2 sessions depending on batch shape.

### Alternative next actions (not blocked — still available if Chris redirects)

- **(A8) Signal Dispatches "Manual dispatch" button** (Rigby S2934 zoom-out fold — ~30 min).
- **(A9) Fourth signal-dispatch rule** — `demand_spike` (250 clusters) or `skill_demand` (131 clusters). One-line rule + agent verification.
- **(A6) SignalCluster promotion audit** — only 0.58% of clusters are active; investigate `SignalAggregationService`.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.
- **(E) Dry-run substrate design for the 5 batch-2 mutations (Ledger #38)** — enables live mutation verification of `blog_tool.approve/reject/generate` + `feedback_tool.submit/update`.

---

## What's forbidden at S2936 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2936 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

- **Ledger #36 (blog_tool Deliverable/SelfBlog approve-path fix)** — extend `_handle_content_review` publish/archive branches to fall back to SelfBlog. Correctness bug candidate. Bundle with future blog_tool follow-up.
- **Ledger #37 (feedback_tool.update `.save()` → update_fields)** — ~1-line fix. Bundle with any future feedback_tool follow-up or dry_run substrate work.
- **Ledger #38 (dry_run affordance across 5 batch-2 mutations)** — substrate design session. Blocks live mutation verification of Slice 6 batch 2 mutations.
- **`execution_history_tool` `hours` schema declaration** — ~3 min follow-up PR. Ledger entry #35 references. Bundle with next content_tool touch.
- **Invalid-action non-gating consistency across Slice 6 handlers** — `recent_activity_tool` + `surgical_moves_status_tool` don't `raise ValueError` on unknown actions (unlike siblings). Ledger #35 references.
- **Schema-vs-handler param-set consistency lint in `pa_tools_gap_map.py`** — Ledger #5 systemic detection lint (S2845) + reinforced by S2935 + S2936 ships. **Third-instance promotion threshold approached** — multiple drifts documented in S2936: `blog_tool.recent` days default, invalid-action message drift, `feedback_tool` unused `target_id`+`rating`, silent `target_type` coercion, non-validated `new_status`.
- **A8 — Signal Dispatches "Manual dispatch" UI button** — Rigby S2934 zoom-out fold.
- **A6 — SignalCluster promotion audit** — substrate investigation.
- **CompetitorAnalysisAgent hardening candidate** — S2929 deferred.
- **Dedicated `agent_execution_query` PA tool** — S2931 Ledger #33.
- **Shared `skip_in_test` decorator** — S2931 Ledger #34.
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A.
- **Bundled dev-env drift slate** — pyright warnings on `pa_tool_schemas.py` line 5915/6167+ (pre-existing dev-env drift; unchanged this ship).
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
**Slice 6 — `td_handlers_content` (6 tools):** **CLOSED at S2936 (6/6, batch 1 + 2).** ✅
**Slice 7 — singleton bucket (9 tools across 8 handler files):** **OPEN at S2937.**

**Total remaining tools to close:** **9 across 8 handler files** (down from 11 at S2935 close).

**Substrate arcs CLOSED at S2936:** Slice 6 (via batch 2 shipping the final 2/6 tools). S2936 shipped 1 sweep-progress PR + 3 Ledger entries.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2936 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2936: zero A4 spend** — pure substrate progress (Slice 6 batch 2 CLOSE ship).
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2936)

See:
- **S2936 handoff (current):** `docs/handoffs/SESSION_2936_SLICE_6_BATCH_2_CLOSE.md`
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
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
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
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entries #36 + #37 + #38 added S2936 — blog_tool Deliverable/SelfBlog approve-path gap + feedback_tool `.save()` write-scope drift + no `dry_run` affordance across 5 mutations).
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (106 per-tool validation docs post-S2936).
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
