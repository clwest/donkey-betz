# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2935 SHIPPED SLICE 6 BATCH 1 (Chris "yes proceed" ratification). 4 pure-read validation docs + schema-realignment fix for 2 tools + Ledger entry #35 for the schema-under-describes-handler drift class. Clean substrate progress diff. **S2936 OPENS WITH A NATURAL NEXT MOVE: Slice 6 batch 2 (mutation-heavy pair `blog_tool` + `feedback_tool`)**.

**Refreshed 2026-07-24 (S2935 close).** Chris ratified 4-tool pure-read batch + schema-fix-in-PR + Ledger entry at S2935 T1 ("yes proceed") after Claude+Rigby joint AGREE. Rigby's Q4(c) zoom-out surfaced the schema-under-describes-handler drift as bundle-into-PR (preferred over Ledger-only or future-carry). Shipped as PR #3506 (merge SHA `628f7bde1`).

**PRs shipped this session:**
- u-d-b PR [#3506](https://github.com/clwest/donkey-betz-platform/pull/3506) — S2935 Slice 6 batch 1 pure-read quartet + schema-realignment, merged at `628f7bde1`.
- u-d-b PR `<TBD>` — S2935 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Code shipped this session:**
- **4 new validation docs (T1b sweep template v1, all `pass`):** `execution_history_tool` (§6 primary anchor — 5 actions exercised live) + `learning_patterns_tool` (3 actions) + `recent_activity_tool` + `surgical_moves_status_tool`.
- **Schema realignment fixes (3 tools in `pa_tool_schemas.py`):**
  - `recent_activity_tool`: added `action` (summary/detailed) + `hours`; deprecated `limit`+`minutes`.
  - `surgical_moves_status_tool`: added `action` + `hours` + `session_id`; deprecated `verbose`.
  - `learning_patterns_tool`: expanded description to enumerate actions (cleared lint).
- **Rigby Tool Gap Ledger entry #35** — schema-under-describes-handler drift class, 2/3 instances resolved this ship.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3506 recycled clean at `sha=628f7bde1917` via `make recycle-all`.
- Rigby verified all 3 tools post-recycle:
  1. `execution_history_tool action=stats` — envelope stable, `avg_time` nullability confirmed as documented.
  2. `recent_activity_tool action=detailed hours=24` — **NEW schema-declared params work end-to-end**; `sections.spider_data.top_spiders` returned 15 entries (confirms `item_limit=15` behavior visible in the wire).
  3. `surgical_moves_status_tool action=detailed hours=168` — NEW schema-declared params work; `total_sessions=6, decision_verdict=null` for all (data condition, documented).

**Gap-map ratchet:** validated_full 83 → 87 (+4); untested 15 → 11 (-4); template pass 80 → 84 (+4). No regressions.

**Governance:** none this session. D6 moratorium unchanged. Zero new forbidden-entry candidates.

**Rigby Tool Gap Ledger:** entry #35 added (schema-under-describes-handler drift, 2 resolved + 1 deferred + 1 sibling divergence future work). Reinforces Ledger #5 (systemic detection lint) as approaching third-instance promotion threshold.

Full session context: `docs/handoffs/SESSION_2935_SLICE_6_BATCH_1.md`.

---

## S2936 open sequence — SLICE 6 BATCH 2 (mutation-heavy pair)

**Natural next action per S2935 close:** Slice 6 batch 2 covers the 2 mutation-heavy tools deferred at batch 1 per S2921 process hygiene (don't mix mutation-shape design with pure-read validate-under-substrate in one session).

### First action — Slice 6 batch 2: `blog_tool` + `feedback_tool`

**Batch inventory:**

| Tool | Actions | Mutation posture | Handler file |
|---|---|---|---|
| `blog_tool` | 8 (stats/list/detail/search/recent/approve/reject/generate) | MUTATION-HEAVY: `approve` (publish) + `reject` (archive) + `generate` (LLM+deliberation dispatch) | `core/services/td_handlers_content.py:213` (routes through `_handle_blog_direct` + `_handle_blog_query` + `_handle_content_review`) |
| `feedback_tool` | 4 (list/stats/submit/update) | MUTATION: `submit` (INSERT UserFeedback) + `update` (UPDATE UserFeedback) | `core/services/td_handlers_content.py:3587` (`_handle_feedback`) |

**Methodology anchors:**

- **T1b template §5a 4-tier blast-radius taxonomy (added S2921)** — mandatory for tools with mutation actions declared as in-scope OR ship-deferred. Both tools need §5a tables classifying each mutation action (contained/spreading/cascading/external).
- **Grep discipline for `contained` claims:** signal-chain grep (`post_save.connect` / `@receiver`) + FK-cascade check. First mis-classification post-merge = Ledger candidate.
- **Batch shape decision at S2936 T0 SIGN:** three canonical shapes per S2907 Fold E — gated-write dry_run-only is likely the right fit for this batch (both tools cross into DB write + LLM dispatch). Rigby picks at T0.
- **Prior Slice 5 batch 4 close artifact for pattern:** `docs/audits/pa_tools/substrate/slice_5_close_artifact.md` — Slice 5 was agent-forwarding single-shared-handler shape; Slice 6 batch 2 is per-tool multi-action + mutation containment. Different but the §5a authoring guidance still applies.

**S2936 open sequence:**

1. Read the two mutation handlers in full — `_handle_blog_direct` at `td_handlers_content.py:213` (routes to `_handle_blog_query` + `_handle_content_review`) + `_handle_feedback` at `:3587`.
2. Grep-verify `post_save` / `@receiver` on `UserFeedback` + `SelfBlog` / `Deliverable` (blog_tool downstream) to classify mutation blast radius correctly.
3. Route batch composition + shape decision (uniform gated-write / mixed / other) to Rigby at S2936 T0 SIGN — joint AGREE, then Chris yes/no per `feedback_claude_rigby_agree_first_chris_yes_no`.
4. Execute the batch (2 docs + §5a tables for each mutation action + §5b Appendix A if async fan-out surfaces).
5. Slice 6 CLOSE at end of S2936 (batch 2 = final 2 tools). Slice 6 close-artifact optional depending on structural pattern surfaced.

### Alternative next actions (not blocked — still available if Chris redirects)

- **Slice 7 (singleton bucket)** — 7 tools across 7 handler files: `code_job_tool` / `employee_tool` + `mission_verdict` / `newsletter_tool` / `railway_tool` / `rigby_shift_brief_tool` / `rigby_work_item` / `spider_data_aggregation_tool` / `zoom_out_tool`. Bundle after Slice 6 batch 2 closes.
- **(A8) Signal Dispatches "Manual dispatch" button** (Rigby S2934 zoom-out fold — ~30 min).
- **(A9) Fourth signal-dispatch rule** — `demand_spike` (250 clusters) or `skill_demand` (131 clusters). One-line rule + agent verification.
- **(A6) SignalCluster promotion audit** — only 0.58% of clusters are active; investigate `SignalAggregationService`.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.

---

## What's forbidden at S2935 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2935 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

- **`execution_history_tool` `hours` schema declaration** — ~3 min follow-up PR. Ledger entry #35 references. Bundle with Slice 6 batch 2 close if convenient.
- **Invalid-action non-gating consistency across Slice 6 handlers** — `recent_activity_tool` + `surgical_moves_status_tool` don't `raise ValueError` on unknown actions (unlike siblings). Ledger #35 references.
- **Schema-vs-handler param-set consistency lint in `pa_tools_gap_map.py`** — Ledger #5 systemic detection lint (S2845) + reinforced by S2935 ship. Third-instance promotion threshold approaching.
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
**Slice 6 — `td_handlers_content` (6 tools):** **batch 1 CLOSED at S2935 (4/6)** — batch 2 open with `blog_tool` + `feedback_tool`.

**Total remaining tools to close:** **11 across 8 handler files** (down from 15 at S2934 close).

**Substrate arcs CLOSED at S2935:** none. S2935 shipped 1 sweep-progress PR (validation quartet + schema-realignment) + Ledger entry #35.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2935 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2935: zero A4 spend** — pure substrate progress (Slice 6 batch 1 validation ship).
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2935)

See:
- **S2935 handoff (current):** `docs/handoffs/SESSION_2935_SLICE_6_BATCH_1.md`
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
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entry #35 added S2935 — schema-under-describes-handler drift class).
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (104 per-tool validation docs post-S2935).
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
