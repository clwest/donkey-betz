# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2941 CLOSED LEDGER #16 TWIN-MIRROR ENFORCEMENT. Substrate ship: `session_lifecycle close` now REFUSES to proceed without twin-mirror IDs (`--content-mirror-id` + `--ratification-envelope-id`) OR explicit `--allow-no-mirror` acknowledgment. Enforcement runs pre-`transaction.atomic()` — refuse produces clean rollback (no retire, no mint, no wrapper rewrite). Ship PR #3517 at SHA `c250b49b6`. 35 tests pass (20 new + 15 pre-existing). First live-in-force use: THIS session's own close ceremony (dogfooding). Rigby T0 SIGN AGREE + T1 SIGN AGREE with 1 F-BLOCKING resolved before commit (same-UUID-both-IDs escape → gated). Chris D-verdict RATIFY at T0 + T1. **S2942 OPENS WITH DEFERRED QUEUE PICKS** — see §S2942 open sequence below.

**Refreshed 2026-07-24 (S2941 close).** Ledger #16 3-trigger corroboration (S2937/S2938/S2939) discharged. Gap-map headline unchanged: `98 validated_full / 0 untested`.

**PRs shipped this session:**
- u-d-b PR [#3517](https://github.com/clwest/donkey-betz-platform/pull/3517) — Ledger #16 twin-mirror enforcement (substrate). Merge SHA `c250b49b6`.
- u-d-b PR `<TBD>` — S2941 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Twin mirrors shipped this session (dogfooding):**
- Content mirror: `0fbbe1aa-44f5-425c-8788-936971cfbf41` (Architecture & Research workspace, category `initiative_phase_doc`).
- Ratification envelope: `be7265d9-6e44-4d75-a268-e81ff15a927e` (Architecture & Research workspace, `deliverable_type='ratification_record'`).

**Files shipped this session:**
- **NEW** `core/services/twin_mirror_enforcement.py` (~180 LOC) — public API `assert_twin_mirror_at_close(...)`.
- **MODIFIED** `core/management/commands/session_lifecycle.py` — 3 new CLI flags + pre-tx enforcement call + stdout audit line.
- **NEW** `core/tests/test_session_lifecycle_twin_mirror.py` (420 lines, 20 tests) — direct-service + CLI-integration coverage including clean-rollback proof.
- **MODIFIED** `core/tests/test_session_lifecycle_command.py` — 2 pre-existing tests updated to pass `--allow-no-mirror`.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3517 recycled clean at `sha=c250b49b62a3` via `make recycle-all` (surviving=none).
- Live-verified refuse-path: `python manage.py session_lifecycle close --dry-run` (no mirror flags) → correct `CommandError` with actionable message.
- Live-verified allow-path: `python manage.py session_lifecycle close --dry-run --allow-no-mirror --label smoke-s2941` → clean dry-run.
- **Third live-verification:** THIS session's own close cascade (first end-to-end use of the new gate on a real ratification ceremony).

**Governance:** none this session. D6 moratorium unchanged. Zoom-out fold-candidate recorded (see below §Ledger #16b watch).

**Rigby Tool Gap Ledger:** no new formal entries. No candidates surfaced this session.

Full session context: `docs/handoffs/SESSION_2941_LEDGER_16_TWIN_MIRROR.md`.

---

## S2942 open sequence

**No pre-ratified first-action carried forward from S2941.** Ledger #16 discharged the 3-trigger corroboration cleanly; no follow-up substrate shipped.

Chris directs at S2942 open. Suggested first-action candidates (all deferred from S2940/S2941 queues):

- **(A8) Signal Dispatches "Manual dispatch" button** (Rigby S2934 zoom-out fold — ~30 min UI, engineering).
- **(A9) Fourth signal-dispatch rule** — `demand_spike` (250 clusters) or `skill_demand` (131 clusters). Engineering + observability.
- **(A6) SignalCluster promotion audit** — only 0.58% of clusters are active. Audit-then-build; likely surfaces gaps.
- **(F) Dry-run substrate design (Ledger #38)** — enables live mutation verification of Slice 7 batch 2a/2b mutations retroactively. ~1 session substrate.
- **(H) Ledger #41 candidate** — teach gap-map classifier to distinguish live-verified vs analyzed-only actions. ~1 session substrate.
- **(D) Docs restructuring arc** — unblocked at S2800, still queued. Large arc.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A. ~1 session substrate.
- **(E) Tier 2 lint promotion** — envelope-JSON top-level-key parse against schema description text. Ledger #5 sub-substrate. ~1 session.
- **(NEW-1) Wire up A1 shipping** — engineering-net-new: build something user-facing. Per `feedback_engineering_bias_over_audit`, actively surface 1-3 net-new candidates.
- **(NEW-2) Ledger #16b if triggered** — see watch below.

### Ledger #16b watch (fold-candidate from S2941 T1 SIGN)

**Trigger:** if `--allow-no-mirror` becomes routine across ~3+ closes without cascade-only justification, tighten the gate via:
- Option A: reason-string requirement (e.g., `--allow-no-mirror --reason "S2XXX cascade-only wrapper-pin bump"`).
- Option B: label-pattern restriction (auto-block `--allow-no-mirror` for labels matching `/ratif|playbook|governance/i`).

**Current status:** 0 in-force uses of `--allow-no-mirror` at the time of S2941 close (only the smoke-test dry-run + the 2 pre-existing test invocations count, and neither is a real close). Watch during S2942+.

### S2942 open sequence steps (universal)

1. **First-action lint pre-flight:** run `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` and confirm gap-map headline still reads `98 validated_full / 0 untested`.
2. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2942 pin (retired at this session's close cascade).
3. Chris directs first-action from the deferred queue above; joint T0 SIGN with Rigby follows normal shape.

---

## What's forbidden at S2942 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2942 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

All S2940 close deferred entries carry forward. **S2941 additions to the deferred queue:**

- **Ledger #16b candidate** — see Ledger #16b watch above (needs 3+ triggers).

All prior S2940 deferred entries unchanged:

- **Ledger candidate — `code_job_tool.submit` silent-degrade on Celery dispatch fail** — line 148-149 warning-log-only path.
- **Ledger candidate — `employee_tool.run_now` double-dispatch hazard** — no idempotency check at handler layer.
- **Ledger candidate — `railway_tool` `restart`+`redeploy` functional equivalence** — both fire identical `serviceInstanceRedeploy` mutation.
- **Ledger #5 Tier-2 candidate — bare invalid-action envelope pattern** — sixth-instance corroboration at S2940.
- **`_handle_railway` docstring under-lists actions** (5/7 named) — ~2-min doc fix at next `td_handlers_railway.py` touch.
- **Ledger #5 Tier 2 (envelope-JSON parse)** — deferred per Rigby S2938 ZO AGREE.
- **Ledger #5 Tier 3 (semantic distance between prose and field names)** — too fuzzy for MVP.
- **Ledger #36 (blog_tool Deliverable/SelfBlog approve-path fix)** — correctness bug candidate.
- **Ledger #37 (feedback_tool.update `.save()` → update_fields)** — ~1-line fix.
- **Ledger #38 (dry_run affordance across batch-2 mutations)** — substrate design session.
- **Ledger #39 (rigby_work_queue module docstring stale)** — **AUTO-DETECTED by Ledger #5 lint.** ~5-min doc fix.
- **Ledger #40 candidate (newsletter_tool sources drift)** — record-only.
- **Ledger #41 candidate (classifier live-vs-analyzed distinction)** — record-only.
- **`execution_history_tool` `hours` schema declaration** — ~3 min follow-up PR.
- **Invalid-action non-gating consistency across Slice 6+7 handlers** — Ledger #5 consolidation candidate.
- **`zoom_out_tool include=aggregations` Rigby-wrapper investigation (S2937 §6.1a anomaly)** — PA-wrapper investigation.
- **A8 — Signal Dispatches "Manual dispatch" UI button** — Rigby S2934 zoom-out fold.
- **A6 — SignalCluster promotion audit** — substrate investigation.
- **CompetitorAnalysisAgent hardening candidate** — S2929 deferred.
- **Dedicated `agent_execution_query` PA tool** — S2931 Ledger #33.
- **Shared `skip_in_test` decorator** — S2931 Ledger #34.
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A.
- **Bundled dev-env drift slate** — pyright warnings on `pa_tool_schemas.py` + `build_pa_tool_audit.py` + `pa_tools_gap_map.py` + now `session_lifecycle.py` + `twin_mirror_enforcement.py` (ORM attribute-access warnings — pre-existing pattern).
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
**Slice 7 — singleton bucket (9 tools across 8 handler files):** CLOSED at S2940 (9/9). ✅
**Ledger #16 twin-mirror enforcement substrate:** CLOSED at S2941 (PR #3517). ✅

**Substrate arcs CLOSED:** Ledger #5 Tier 1 MVP (S2938) + Ledger #16 (S2941).

**Total remaining tools to close: 0.**

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2941 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2941: zero A4 spend** — pure substrate ship.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2941)

See:
- **S2941 handoff (current):** `docs/handoffs/SESSION_2941_LEDGER_16_TWIN_MIRROR.md`
- **S2940 handoff:** `docs/handoffs/SESSION_2940_SLICE_7_CLOSE.md`
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
- **Slice 5 CLOSE artifact:** `docs/audits/pa_tools/substrate/slice_5_close_artifact.md`
- **T1b canonical template file (with §5c retro-fold):** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2938 Ledger #5 lint code:** `core/services/pa_tools_gap_map.py` (`lint_schema_vs_handler` line 431) + `core/tests/test_pa_tools_gap_map_ledger_5.py`
- **S2941 Ledger #16 enforcement code:** `core/services/twin_mirror_enforcement.py` + `core/management/commands/session_lifecycle.py` (`_handle_close` line 582+) + `core/tests/test_session_lifecycle_twin_mirror.py`
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
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (no new formal entries S2941).
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated with `--include-validation-xref`) + `docs/research/tools/validation/*.md` (115 per-tool validation docs post-S2940).
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
