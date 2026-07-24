# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2943 CLOSED. Slice 6 doc closure + Ledger #38 batch 2 shipped. Chris directed engineering-first at S2943 open (option B from 3-option kickoff menu): resume PA-tools sweep per `project_s2935_resume_pa_tools_sweep`. Post-S2942 reconciliation (Rigby T1 SIGN AGREE via 4 tool_runs) surfaced that only 2 tools in `td_handlers_content.py` needed doc work (not the pre-S2942 "6 untested" claim from S2934 memory): `content_tool` (no dedicated doc) + `deliverable_tool` (missing `## Covered actions` heading). Rigby zoom-out (Q3) pushed for a 2-PR split to avoid bundling docs-only wins with code churn; adopted. PR-A shipped docs-only; PR-B shipped `bulk_archive_published` dry_run alignment per `project_s2908_batch_4_shape_break_commitment` (chose bulk/maintenance sibling of already-supported `bulk_archive` over `set_status` per Rigby verdict on semantic coupling). Third mutation tool to earn `live` + `dry_run_supported`.

**Refreshed 2026-07-24 (S2943 close).** Gap-map headline: `100 validated_full / 0 untested` (+2 from S2942). New scoreboard baseline: `per_execution_mode: {unknown: 158, live: 3}` + `per_mutation_safety: {unknown: 158, dry_run_supported: 3}`.

**PRs shipped this session:**
- u-d-b PR **#3523** — S2943 Slice 6 PR-A (docs-only): new `content_tool_validation.md` + `## Covered actions` heading on `deliverable_tool_validation.md`.
- u-d-b PR **#3524** — S2943 Slice 6 PR-B (code + live-verify): `bulk_archive_published` dry_run pattern-alignment; scoreboard 2 → 3.

**Twin mirrors shipped this session (per `feedback_twin_deliverable_at_every_ratification`):**
- Content mirror: `a3cb246d-48bf-4825-bbac-5c3547136bf9` (Architecture & Research workspace, category `initiative_phase_doc`; missing_initiative_id diagnostic cleared post-create).
- Ratification envelope: `7b1eeaa7-18b5-45f8-9b1d-5e3e898a8a08` (Architecture & Research workspace, `deliverable_type='ratification_record'`, category `governance`; no diagnostic flagged — S2942 pre-set workaround baked in).

**Files shipped this session:**
- **NEW** `docs/research/tools/validation/content_tool_validation.md` — S2796 sweep shape v1; 27 actions enumerated flat; blast-radius per §5a; Appendix A Celery fan-out; §6.1 live-verify evidence; frontmatter gains `Execution mode: live` + `Mutation safety: dry_run_supported`.
- **MODIFIED** `docs/research/tools/validation/deliverable_tool_validation.md` — flat `## Covered actions` heading between §3 and §4; enumerates all 18 current actions (S2728 covered 16; `delete` + `clear_diagnostic` added S2860/S2868).
- **MODIFIED** `core/services/td_handlers_content.py` — `_handle_bulk_archive_published` dry_run branch (line 5171-5181) emits S2942-aligned envelope: `would_action='archive_published'` + `would_change_to='archived'` + `would_archive_count=N` + `no_writes=true`.
- **MODIFIED** `core/services/pa_tool_schemas.py` — `dry_run` param description (line 4190) now enumerates all 3 supporting actions.
- **NEW** `core/tests/test_s2943_bulk_archive_published_dry_run.py` (6 regression tests).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- Recycled once mid-session (post-PR-B handler edit, before live-verify).
- Recycled again after PR-B merge.
- Live-verified `bulk_archive_published` under dry_run in conversation `pa-5e0a153475dd44f7` (21ms, 5/5 S2942 envelope fields present, 0 writes).
- Gap-map regen confirms scoreboard Metric B 2 → 3.

**Governance:** none. D6 moratorium unchanged. Two zoom-out ledger candidates recorded record-only (newsletter dry_run alignment + deliverable v1 template retrofit — see handoff §Ledger candidates).

**Rigby Tool Gap Ledger:** no new formal entries. Ledger #38 gained a batch-2 mitigation reference in-doc (S2943 handoff pointer).

Full session context: `docs/handoffs/SESSION_2943_SLICE_6_LEDGER_38_BATCH_2.md`.

---

## S2944 open sequence

**S2944 first-action is Chris-directed.** No pre-ratified plan carries forward from S2943.

### Universal open sequence

1. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline still reads `100 validated_full / 0 untested`, and `per_execution_mode.live` ≥ 3 (regression witness for S2943 ship).
2. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2944 pin (retired at S2943 close cascade).
3. **Chris directs first-action from the deferred queue below.**

### Deferred queue (updated at S2943 close — Chris picks)

Engineering-first candidates (per `feedback_engineering_bias_over_audit`):

- **(NEW-1) Wire up A1 shipping** — engineering-net-new.
- **(A8) Signal Dispatches "Manual dispatch" button** — ~30 min UI, engineering.
- **(A9) Fourth signal-dispatch rule** — `demand_spike` (250 clusters) or `skill_demand` (131 clusters).
- **(A6) SignalCluster promotion audit** — only 0.58% of clusters are active.
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(E) Tier 2 lint promotion** — envelope-JSON top-level-key parse. Ledger #5 sub-substrate.
- **(F) Ledger #38 batch 3 — `content_tool.generate_newsletter` dry_run alignment** — NEW at S2943 close. Native `dry_run=true` short-circuit already exists (td_handlers_content.py:4707-4721) but predates S2942 envelope contract. Adding `no_writes:true` + `would_action` + `would_dispatch_target` would make it the 4th action to earn `dry_run_supported`. ~30 min + live-verify + doc.
- **Envelope enhancement (record-only S2942)** — Rigby zoom-out fold suggested `verify_hint` + `would_write_count` for dry_run envelopes. Needs 2nd-trigger corroboration before promoting.
- **Close-ceremony ledger-flip checklist (meta-fix, record-only S2942)** — first trigger from S2942 reconciliation; watch for 2nd trigger.
- **Deliverable v1 template retrofit (record-only S2943)** — protocol-variant docs (like `deliverable_tool_validation.md`) can't opt into `Template version: v1` without triggering sweep-variant section lints. Either extend lint to know protocol shape, or leave protocol docs as `warn`-flagged. Pattern gap, not defect.

---

## What's forbidden at S2944 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2943 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

S2943 additions to the deferred queue:

- **Ledger #38 batch 3 candidate (`content_tool.generate_newsletter` dry_run alignment):** native `dry_run=true` short-circuit already exists (td_handlers_content.py:4707-4721) but envelope predates S2942 contract. Adding `no_writes:true` + `would_action` + `would_dispatch_target` = 4th `dry_run_supported` tool. ~30 min + live-verify + doc.
- **Deliverable v1 template retrofit (record-only):** protocol-variant docs can't opt into `Template version: v1` without triggering sweep-variant section lints. Pattern gap, not defect.

S2942 additions still deferred:

- **Envelope enhancement candidates (S2942 Rigby zoom-out fold, record-only):** `verify_hint` (model + id + field expectations block) + `would_write_count` (multi-row summary). Requires 2nd-trigger corroboration.
- **Close-ceremony ledger-flip checklist (S2942 meta-fix candidate, record-only):** first trigger from S2942 reconciliation of stale #33 + #34 rows. Requires 2nd trigger.
- **dry_run scope expansion to batch 2a/2b (mission_verdict, newsletter_tool, rigby_work_item, code_job_tool, employee_tool, railway_tool):** deferred per plan §8 — needs per-tool semantics + higher-stakes safety envelopes.

All S2941 deferred entries carry forward (S2942 didn't touch them):

- **Ledger #16b candidate** — needs 3+ triggers.
- **Ledger candidate — `code_job_tool.submit` silent-degrade on Celery dispatch fail** — line 148-149 warning-log-only path.
- **Ledger candidate — `employee_tool.run_now` double-dispatch hazard** — no idempotency check at handler layer.
- **Ledger candidate — `railway_tool` `restart`+`redeploy` functional equivalence** — both fire identical `serviceInstanceRedeploy` mutation.
- **Ledger #5 Tier-2 candidate — bare invalid-action envelope pattern** — sixth-instance corroboration at S2940.
- **`_handle_railway` docstring under-lists actions** (5/7 named) — ~2-min doc fix at next `td_handlers_railway.py` touch.
- **Ledger #5 Tier 2 (envelope-JSON parse)** — deferred per Rigby S2938 ZO AGREE.
- **Ledger #5 Tier 3 (semantic distance between prose and field names)** — too fuzzy for MVP.
- **Ledger #36 (blog_tool Deliverable/SelfBlog approve-path fix)** — correctness bug candidate.
- **Ledger #37 (feedback_tool.update `.save()` → update_fields)** — ~1-line fix.
- **Ledger #39 (rigby_work_queue module docstring stale)** — auto-detected by Ledger #5 lint. ~5-min doc fix.
- **Ledger #40 candidate (newsletter_tool sources drift)** — record-only.
- **`execution_history_tool` `hours` schema declaration** — ~3 min follow-up PR.
- **Invalid-action non-gating consistency across Slice 6+7 handlers** — Ledger #5 consolidation candidate.
- **`zoom_out_tool include=aggregations` Rigby-wrapper investigation (S2937 §6.1a anomaly)** — PA-wrapper investigation.
- **CompetitorAnalysisAgent hardening candidate** — S2929 deferred.
- **Dedicated `agent_execution_query` PA tool** — S2931 Ledger #33 alternative path (superseded by allowlist expansion but still tracked).
- **Shared `skip_in_test` decorator** — S2931 Ledger #34 alternative (superseded by explicit guard but still tracked).
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A.
- **Bundled dev-env drift slate** — pre-existing pyright warnings on `pa_tool_schemas.py` + `build_pa_tool_audit.py` + `pa_tools_gap_map.py` + `session_lifecycle.py` + `twin_mirror_enforcement.py` + `td_handlers_agents.py` + `td_handlers_content.py` (all ORM attribute-access + partially-unknown-generic warnings — pre-existing pattern).
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate + Ledger candidate: media_tool.delete IRREVERSIBLE** — unchanged.
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
**Slice 6 — `td_handlers_content` (6 tools):** CLOSED at S2936 (6/6, batch 1 + 2). ✅ **S2943 addendum:** file-scope doc closure for `content_tool` + `deliverable_tool` heading + `bulk_archive_published` dry_run alignment.
**Slice 7 — singleton bucket (9 tools across 8 handler files):** CLOSED at S2940 (9/9). ✅
**Ledger #16 twin-mirror enforcement substrate:** CLOSED at S2941 (PR #3517). ✅
**Ledger #38 dry_run MVP + Ledger #41 scoreboard promotion:** CLOSED at S2942. ✅
**Ledger #38 batch 2 (bulk_archive_published):** CLOSED at S2943 (PR #3524). ✅

**Substrate arcs CLOSED:** Ledger #5 Tier 1 MVP (S2938) + Ledger #16 (S2941) + Ledger #38 dry_run MVP (S2942) + Ledger #41 scoreboard (S2942) + Ledger #38 batch 2 (S2943).

**Total remaining tools to close: 0.** All ratified sweep scope discharged. Batch 2 mutation-dry_run expansion beyond blog_tool + feedback_tool remains deferred (needs per-tool semantics).

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2942 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2942: zero A4 spend** — pure substrate ship (~$0.001 LLM cost from test suite setup only).
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2942)

See:
- **S2943 handoff (current):** `docs/handoffs/SESSION_2943_SLICE_6_LEDGER_38_BATCH_2.md`
- **S2942 handoff:** `docs/handoffs/SESSION_2942_S2942_CLOSURE_PLAN.md`
- **S2941 handoff:** `docs/handoffs/SESSION_2941_LEDGER_16_TWIN_MIRROR.md`
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
- **T1b canonical template file (S2942 refreshed with two-metric scoreboard):** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2938 Ledger #5 lint code:** `core/services/pa_tools_gap_map.py` (`lint_schema_vs_handler` line 431) + `core/tests/test_pa_tools_gap_map_ledger_5.py`
- **S2941 Ledger #16 enforcement code:** `core/services/twin_mirror_enforcement.py` + `core/management/commands/session_lifecycle.py` (`_handle_close` line 582+) + `core/tests/test_session_lifecycle_twin_mirror.py`
- **S2942 Ledger #38 dry_run code:** `core/services/td_handlers_content.py` (5 branches) + `core/services/pa_tool_schemas.py` (2 schemas) + `core/tests/test_s2942_dry_run_mvp.py`
- **S2942 Ledger #41 scoreboard code:** `core/services/pa_tools_gap_map.py` (`EXECUTION_MODES` / `MUTATION_SAFETY_VALUES` / `UNKNOWN_LABEL`) + `core/tests/test_s2942_ledger_41_scoreboard.py`
- **S2940 Batch 2b validation docs:** `docs/research/tools/validation/{code_job_tool,employee_tool,railway_tool}_validation.md`
- **S2939 Batch 2a validation docs:** `docs/research/tools/validation/{mission_verdict,newsletter_tool,rigby_work_item}_tool_validation.md`
- **S2937 validation docs:** `docs/research/tools/validation/{rigby_shift_brief,spider_data_aggregation,zoom_out}_tool_validation.md`
- **S2936 validation docs (S2942 refreshed with dry_run evidence + Metric A+B frontmatter):** `docs/research/tools/validation/{blog,feedback}_tool_validation.md`
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
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (S2942 reconciliation banner + #33/#34/#38 mitigated stanzas added).
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated with `--include-validation-xref`) + `docs/research/tools/validation/*.md` (115 per-tool validation docs post-S2940).
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
