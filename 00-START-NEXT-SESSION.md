# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2939 SHIPPED SLICE 7 BATCH 2a: 3 mutation-tool validation docs (mission_verdict + newsletter_tool + rigby_work_item) as PR #3514, bifurcated Option C shape with Chris D-verdict guardrails (§6 read-only scope + §5a mutation proof bar). First live-in-force consumer of the S2938 Ledger #5 lint substrate — 2 handler_drift hits on `rigby_work_item` (both Ledger #39 case) auto-rendered inline; zero false positives across other 115 wired tools. Sweep: Slice 7 Batch 2a CLOSED (3/9 → 6 remaining). **S2940 OPENS WITH SLICE 7 BATCH 2b — likely pure-read trio (`employee_tool` + 2 more singletons).**

**Refreshed 2026-07-24 (S2939 close).** Chris D-verdict at S2939 T0 RATIFIED joint plan with two guardrails baked into all 3 docs. Rigby S2939 T0 SIGN AGREE-WITH-EDITS 4/4 (Q1/Q2/Q3 + ZO; tool-grounded — 8 tool_runs). Q3 edit caught a "hard-claim without code-cite" risk on mission_verdict's post_save receivers — verified at `mission_verdict_signals.py:57` + `mission_verdict_attention_signals.py:68` before writing the assertion. PR merged as SHA `edaa3f16e`.

**PRs shipped this session:**
- u-d-b PR [#3514](https://github.com/clwest/donkey-betz-platform/pull/3514) — Slice 7 Batch 2a (3 mutation-tool validation docs, bifurcated Option C). Merge SHA `edaa3f16e`.
- u-d-b PR `<TBD>` — S2939 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Docs shipped this session:**
- **`docs/research/tools/validation/mission_verdict_tool_validation.md`** (new, 161 lines) — all-mutation shape (certify/reject/defer). No §6 LIVE-VERIFY (no read actions); §5a covers 3 actions with `cascading` blast-radius + code-cited post_save receivers (broadcast + HAI) + idempotency proof bar.
- **`docs/research/tools/validation/newsletter_tool_validation.md`** (new, 326 lines) — 4-mut/3-read bifurcated. §6.1–6.4 cover 4 read-path envelopes (validate/list_issues/sources/config) captured LIVE at S2939 T0; §5a covers 4 mutations with `spreading`/`contained` tier + Deliverable post_save receiver chain.
- **`docs/research/tools/validation/rigby_work_item_tool_validation.md`** (new, 259 lines) — 5-action flag-gated. §6.1 LIVE-VERIFIES the `disabled_response` path (flag defaults OFF, revealed `error_code: "legacy_error"` field appended by dispatcher normalizer — patched inline before commit); §5a covers 4 mutations with `spreading`/`external` tier + Appendix A async-fanout for `delegate`.
- **Auto-gen doc regen** (`--include-validation-xref`): `docs/PA_TOOL_AUDIT.md` (+10 lines) + `docs/audits/PA_TOOLS_GAP_MAP.md` (+20 lines) — all 3 tools flip `untested → validated_full`.

**Live backfill (Ledger #5 lint pre-flight at S2939 open):** 117 tools scanned → 2 hits (both on `rigby_work_item`, both Ledger #39 case surfaced at S2937 manual scan) → 0 false positives across 115 remaining wired tools. Auto-flag disposition rendered inline in `rigby_work_item` §5c.1 with pointer to Ledger #39 as pre-existing known cause — **first auto-detected-drift precedent in the sweep**.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3514 recycled clean at `sha=edaa3f16e9d0` via `make recycle-all` (surviving=none).
- Rigby verified (3/3 PASS): (1) `newsletter_tool action=list_issues limit=3` envelope matches §6.2; (2) `rigby_work_item action=list` disabled_response matches §6.1 incl. `error_code`; (3) all 3 tools show `validated_full` in `PA_TOOL_AUDIT.md`; `rigby_work_item` row still carries 2 lint tags.

**Governance:** none this session. D6 moratorium unchanged.

**Rigby Tool Gap Ledger:** no new entries. Ledger #39 auto-detected by Ledger #5 lint (natural fold-in at next `rigby_work_queue` touch, ~5-min docstring refresh).

Full session context: `docs/handoffs/SESSION_2939_SLICE_7_BATCH_2A.md`.

---

## S2940 open sequence — SLICE 7 BATCH 2b + LEDGER #16 TWIN-MIRROR ENFORCEMENT

**S2940 has TWO ratified first-actions** (Chris D-verdict at S2939 close 2026-07-24):

### (1) SLICE 7 BATCH 2b (sweep continuation — likely pure-read trio)

**Natural next action:** open Batch 2b — 3 tools from the remaining 6:
- **employee_tool** — 4 read actions (describe / run_now / status / evidence_for_mission). **run_now is Rigby-gated dispatch** — actually a MUTATION in the broader sense (fires MissionRunner). Requires shape-decision at T0 SIGN: is run_now analyzed-only (like mission_verdict) or is describe/status/evidence_for_mission the "safe read subset" for LIVE-VERIFY? **Shared handler file with `mission_verdict` (Batch 2a) — cross-link in-doc.**
- 2 more singletons TBD — Chris/Rigby to select at T0 SIGN from the remaining 5 handler files. Likely candidates: any tools where dominant surface is pure-read (avoids re-forcing bifurcated Option C or Ledger #38 pressure).

### Batch 2b inventory (from remaining pool)

Remaining 6 tools across 5 handler files (per S2939 close):
- `employee_tool` (`td_handlers_employee.py:100`) — shared module with mission_verdict (Batch 2a).
- Plus 5 more singletons in 4 other handler files (Chris/Rigby select at T0 SIGN based on read-vs-mutation posture scan).

### S2940 open sequence

1. **First-action lint pre-flight:** run `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` and grep for `handler_drift_*` on the 3 Batch 2b tools. Verify hits against expected count. Any new hits = pre-existing drift; disposition inline in §5c.1.
2. **T0 SIGN mutation-verb scan (per S2921 mutation-scan-swap pattern):** classify each Batch 2b tool as pure-read vs mutation-capable BEFORE finalizing the batch shape. If any tool surfaces as mutation-capable when frame assumed pure-read, swap per S2921 discipline.
3. Route Batch 2b shape decision + `employee_tool run_now` handling to Rigby at S2940 T0 SIGN. Ask: pure-read trio possible, or does employee_tool force another bifurcation?
4. Execute batch (3 docs + §5a tables + §5c dispositions per doc, including employee_tool ↔ mission_verdict cross-link).
5. Live-verify read actions.
6. Ledger appends if any drift surfaces.
7. PR + admin-merge + recycle + post-merge verify + close cascade.

### (2) LEDGER #16 TWIN-MIRROR ENFORCEMENT — substrate hardening (queued alongside Batch 2b)

**3-trigger corroboration met at S2939 close** (Chris flagged 2026-07-24 that S2937 + S2938 + S2939 all shipped without content_mirror + ratification_envelope deliverables — twin-mirror pattern per `feedback_twin_deliverable_at_every_ratification` was skipped 3 sessions in a row). Backfill option (A) executed at S2939 close (6 mirrors created via ORM — bypassed diagnostic-flag bug per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`). Ledger #16 promotion to substrate ratified as S2940 second first-action.

**Scope for S2940 (Ledger #16 hardening):**
- Extend `session_lifecycle close` to **refuse close** when both mirror IDs (content + ratification) are not provided or discoverable.
- Alternative shape (softer): add an explicit close-checklist gate that lists "twin mirrors written?" and prompts before finalizing.
- Estimated: ~2 hr substrate session.

**Ordering:** Batch 2b can ship first (mirror discipline is now caught up); Ledger #16 substrate can be an afternoon follow-on OR a full separate ship — Chris/Rigby to decide at T0 SIGN based on Batch 2b scope shape.

**S2939 close mirror backfill IDs (for reference):**
- S2937: content `27da3b4d-7b43-4fc8-84ae-92d30c7c40e8` + ratification `3da8db2f-3f3c-4e40-aa23-7a57c210f832`
- S2938: content `94f04fcd-6ef3-44e6-aa19-315589146358` + ratification `422d8e72-ff8e-4087-9488-88e60b7435fc`
- S2939: content `23dcfe23-3b6a-474e-b882-af6e4d919f2b` + ratification `fbc9f386-17d0-46f0-ab09-362c10102858`

### Alternative next actions (not blocked — still available if Chris redirects)

- **(A8) Signal Dispatches "Manual dispatch" button** (Rigby S2934 zoom-out fold — ~30 min).
- **(A9) Fourth signal-dispatch rule** — `demand_spike` (250 clusters) or `skill_demand` (131 clusters).
- **(A6) SignalCluster promotion audit** — only 0.58% of clusters are active.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.
- **(E) Tier 2 lint promotion** — envelope-JSON top-level-key parse against schema description text. Ledger #5 sub-substrate. ~1 session.
- **(F) Dry-run substrate design (Ledger #38)** — enables live mutation verification of remaining Slice 7 batch 2b/2c mutations AND retroactively for Batch 2a. ~1 session.
- **(G) Ledger #40 candidate promotion** — expand Ledger #5 Tier 1 lint to catch `newsletter_tool` sources-drift class. Threshold: 2+ more corroborations before promoting.
- **(H) Ledger #41 candidate** — teach gap-map classifier to distinguish live-verified vs analyzed-only actions (fine-grained `validated_partial` vs `validated_full` disposition).

---

## What's forbidden at S2940 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2940 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

- **Ledger #5 Tier 2 (envelope-JSON parse)** — deferred per Rigby S2938 ZO AGREE. Would catch `rigby_shift_brief` PARTIAL DRIFT + `newsletter_tool` `sources` drift (Ledger #40 candidate). Bring back when 2+ additional §5c.1 findings prove Tier 1 leaves detection gaps.
- **Ledger #5 Tier 3 (semantic distance between prose and field names)** — too fuzzy for MVP; needs curated corpus first.
- **Ledger #36 (blog_tool Deliverable/SelfBlog approve-path fix)** — extend `_handle_content_review` publish/archive branches to fall back to SelfBlog. Correctness bug candidate.
- **Ledger #37 (feedback_tool.update `.save()` → update_fields)** — ~1-line fix.
- **Ledger #38 (dry_run affordance across batch-2 mutations)** — substrate design session. Blocks live mutation verification of Slice 6 batch 2 mutations AND Slice 7 batch 2a/2b/2c mutations.
- **Ledger #39 (rigby_work_queue module docstring stale)** — **AUTO-DETECTED by Ledger #5 lint.** ~5-min doc fix; natural fold-in at next `rigby_work_queue` touch.
- **Ledger #40 candidate (newsletter_tool sources drift)** — record-only; did NOT trip current Tier 1 MVP heuristic. Promote to Tier 1 lint expansion if pattern surfaces in 2+ more docs.
- **Ledger #41 candidate (classifier live-vs-analyzed distinction)** — gap-map classifier refinement. Record-only.
- **`execution_history_tool` `hours` schema declaration** — ~3 min follow-up PR. Ledger #35 references.
- **Invalid-action non-gating consistency across Slice 6+7 handlers** — Ledger #5 consolidation candidate. Fourth-instance corroboration observed at S2939 (rigby_work_item + earlier mission_verdict + newsletter_tool `_handler_error` variant + prior in-envelope pattern).
- **`zoom_out_tool include=aggregations` Rigby-wrapper investigation (S2937 §6.1a anomaly)** — PA-wrapper investigation. Bundle with any Rigby wrapper touch.
- **A8 — Signal Dispatches "Manual dispatch" UI button** — Rigby S2934 zoom-out fold.
- **A6 — SignalCluster promotion audit** — substrate investigation.
- **CompetitorAnalysisAgent hardening candidate** — S2929 deferred.
- **Dedicated `agent_execution_query` PA tool** — S2931 Ledger #33.
- **Shared `skip_in_test` decorator** — S2931 Ledger #34.
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A.
- **Bundled dev-env drift slate** — pyright warnings on `pa_tool_schemas.py` + `build_pa_tool_audit.py` + `pa_tools_gap_map.py` (pre-existing dev-env drift; unchanged this ship — same class, deferred).
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
**Slice 7 — singleton bucket (9 tools across 8 handler files):** **BATCH 1 CLOSED at S2937 (3/9). BATCH 2a CLOSED at S2939 (3/9).** Batches 2b + 2c queued for S2940+ (6 tools remaining across 5 handler files).

**Substrate arcs CLOSED at S2938:** Ledger #5 (Tier 1 MVP — schema-vs-handler consistency lint). Tier 2 + Tier 3 deferred to future ships.

**Total remaining tools to close:** **6 across 5 handler files** (down from 9 at S2937 open).

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2939 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2939: zero A4 spend** — pure substrate/docs progress (Batch 2a docs shipped).
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2939)

See:
- **S2939 handoff (current):** `docs/handoffs/SESSION_2939_SLICE_7_BATCH_2A.md`
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
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (no new entries S2939; Ledger #39 auto-detected by Ledger #5 lint substrate).
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated with `--include-validation-xref`) + `docs/research/tools/validation/*.md` (112 per-tool validation docs post-S2939).
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
