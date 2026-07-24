# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2945 CLOSED. Ledger #38 batch 4 shipped (`content_tool.run_cleanup` dry_run alignment via shared `_gather_cleanup_preview` helper — closes content_tool 100%). Chris directed engineering-first at S2945 open (option G from the deferred queue). Claude+Rigby T1 SIGN converged on Option B (rich preview helper) over Option A (minimal stub); Rigby DISAGREE with Option A as final on future-drift + retrofit-cost grounds. Chris ratified Option B on plain-English framing (real preview + no future retrofit). Same-PR fold (PLAYBOOK-6.10.8): 2nd trigger of S2944 record-only statuses-autofill quirk mitigated at helper layer — Rigby's first live-verify returned invalid_params (GPT-5.2 autofilled `statuses:[]`); fix `if not statuses: statuses = ['ready','draft']` in `_gather_cleanup_preview` hardens BOTH the dry_run handler path AND the real Celery task path (single source of truth). Fourth mutation-tool-set to earn full S2942 envelope alignment; content_tool per-action alignment count 3 → 4 (100%; all category-scoped mutations pattern-aligned + async-dispatch mutation now aligned via helper).

**Refreshed 2026-07-24 (S2945 close).** Gap-map headline: `100 validated_full / 0 untested` (unchanged). Scoreboard baseline unchanged: `per_execution_mode: {unknown: 158, live: 3}` + `per_mutation_safety: {unknown: 158, dry_run_supported: 3}` — content_tool doc metric already promoted at S2943; S2945 grows PER-ACTION alignment inside content_tool, not doc count.

**PRs shipped this session:**
- u-d-b PR **#3529** — S2945 Ledger #38 batch 4: `content_tool.run_cleanup` dry_run S2942-envelope alignment via shared `_gather_cleanup_preview` helper; regression tests + doc §6.6 with real dispatch evidence + same-PR autofill 2nd-trigger fix.

**Twin mirrors shipped this session (per `feedback_twin_deliverable_at_every_ratification`):**
- Content mirror: `fe4b9b00-8e3f-44ee-8801-44e979acec9c` (Architecture & Research workspace, category `initiative_phase_doc`; diagnostic flag cleared via ORM per known bug).
- Ratification envelope: `b7ed980d-1561-4821-bfce-51f24e5917a7` (Architecture & Research workspace, `deliverable_type='ratification_record'`, category `governance`; no diagnostic flagged — S2942 pre-set workaround baked in).

**Files shipped this session:**
- **MODIFIED** `core/services/td_handlers_content.py` — `run_cleanup` dry_run branch (line 4670+) emits S2942 envelope: `dry_run:true` (default), `would_action:'dispatch_celery'`, `would_task:'cleanup_stale_content'`, `no_writes:true`, plus preview (`would_archive_count`, `total_found`, `safe_statuses`, `cap`, `top_by_type[:5]`, `top_by_category[:5]`).
- **MODIFIED** `core/tasks_misc.py` — NEW `_gather_cleanup_preview()` helper (line 34-102) as single source of truth for the archive queryset; `_impl_cleanup_stale_content` refactored to call the helper.
- **MODIFIED** `core/services/pa_tool_schemas.py:4190` — `dry_run` param description enumerates `run_cleanup`.
- **NEW** `core/tests/test_s2945_dry_run_batch_4.py` — 14 regression tests (10 handler + 4 helper).
- **MODIFIED** `docs/research/tools/validation/content_tool_validation.md` — header bumped S2944 → S2945; §Covered actions + §5a mutation containment + §6.4 updated for `run_cleanup`; §6.6 added with real Rigby dispatch evidence (§6.6.a envelope proof, §6.6.b same-PR autofill fold, §6.6.c regression coverage, §6.6.d single-source-of-truth guarantee).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- Recycled mid-session twice (once post-handler-edit before live-verify, once after autofill fix).
- Recycled after PR #3529 merge (workers matched HEAD `62ca81bea`).
- Live-verified `run_cleanup` dry_run in conversation `pa-2306c73855774b75` (post-merge 11ms, 4/4 sentinel fields, 4/4 preview fields, `safe_statuses` coerced to `['ready','draft']`).
- Gap-map regen confirms scoreboard unchanged (`per_mutation_safety.dry_run_supported=3`).

**Governance:** none. D6 moratorium unchanged. Same-PR fold exercised per PLAYBOOK-6.10.8; no new record-only zoom-out candidates.

**Rigby Tool Gap Ledger:** no new formal entries. Autofill 2nd-trigger was helper-side, mitigated in-PR.

Full session context: `docs/handoffs/SESSION_2945_LEDGER_38_BATCH_4.md`.

---

## S2946 open sequence

**S2946 first-action is Chris-directed.** No pre-ratified plan carries forward from S2945.

### Universal open sequence

1. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline still reads `100 validated_full / 0 untested`, and `per_execution_mode.live` ≥ 3 (regression witness for S2942/S2943/S2944/S2945 ship).
2. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2946 pin (retired at S2945 close cascade).
3. **Chris directs first-action from the deferred queue below.**

### Deferred queue (updated at S2945 close — Chris picks)

Engineering-first candidates (per `feedback_engineering_bias_over_audit`):

- **(NEW-1) Wire up A1 shipping** — engineering-net-new.
- **(A8) Signal Dispatches "Manual dispatch" button** — ~30 min UI, engineering.
- **(A9) Fourth signal-dispatch rule** — `demand_spike` (250 clusters) or `skill_demand` (131 clusters).
- **(A6) SignalCluster promotion audit** — only 0.58% of clusters are active.
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(E) Tier 2 lint promotion** — envelope-JSON top-level-key parse. Ledger #5 sub-substrate.
- **(H) generate_newsletter dry_run default flip (record-only S2944)** — schema says "DEFAULT: true" but handler defaults False. Would need per-caller regression review. Simple 1-line handler fix + wider blast-radius analysis.
- **(I) bulk_archive statuses autofill robustness (record-only S2944 — NOW 2nd trigger observed at S2945 run_cleanup path, fixed there via helper)** — port the `if not statuses` coercion pattern from `_gather_cleanup_preview` to `_handle_bulk_archive` (per-handler touch, not shared-helper reachable). ~5-line handler fix + regression test.
- **Envelope enhancement (record-only S2942)** — Rigby zoom-out fold suggested `verify_hint` + `would_write_count` for dry_run envelopes. Needs 2nd-trigger corroboration before promoting.
- **Close-ceremony ledger-flip checklist (meta-fix, record-only S2942)** — first trigger from S2942 reconciliation; watch for 2nd trigger.
- **Deliverable v1 template retrofit (record-only S2943)** — protocol-variant docs can't opt into `Template version: v1` without triggering sweep-variant section lints. Pattern gap, not defect.

---

## What's forbidden at S2946 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2945 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2945 additions to the deferred queue:**

- **Ledger candidate — `bulk_archive` statuses autofill robustness (2nd trigger corroborated at S2945 run_cleanup path):** the S2944 record-only observation is now confirmed as a real pattern. Fixed at `_gather_cleanup_preview` for the run_cleanup path; `_handle_bulk_archive` still vulnerable. ~5-line handler fix + regression test. **Deferred priority: HIGH — 2 triggers observed.**

**S2944 additions still deferred:**

- **Ledger #38 batch 4 candidate (`content_tool.run_cleanup` dry_run addition):** ✅ **SHIPPED S2945.** No longer deferred.
- **`generate_newsletter` dry_run default flip (record-only):** handler defaults False but schema says "DEFAULT: true". Needs per-caller regression review.

**S2943 additions still deferred:**

- **Deliverable v1 template retrofit (record-only):** protocol-variant docs can't opt into `Template version: v1` without triggering sweep-variant section lints. Pattern gap, not defect.

**S2942 additions still deferred:**

- **Envelope enhancement candidates (S2942 Rigby zoom-out fold, record-only):** `verify_hint` (model + id + field expectations block) + `would_write_count` (multi-row summary). Requires 2nd-trigger corroboration.
- **Close-ceremony ledger-flip checklist (S2942 meta-fix candidate, record-only):** first trigger from S2942 reconciliation of stale #33 + #34 rows. Requires 2nd trigger.
- **dry_run scope expansion to batch 2a/2b (mission_verdict, newsletter_tool, rigby_work_item, code_job_tool, employee_tool, railway_tool):** deferred per plan §8 — needs per-tool semantics + higher-stakes safety envelopes.

**All S2941 deferred entries carry forward (S2942/S2943/S2944/S2945 didn't touch them):**

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
- **Bundled dev-env drift slate** — pre-existing pyright warnings on `pa_tool_schemas.py` + `build_pa_tool_audit.py` + `pa_tools_gap_map.py` + `session_lifecycle.py` + `twin_mirror_enforcement.py` + `td_handlers_agents.py` + `td_handlers_content.py` + `tasks_misc.py` (all ORM attribute-access + partially-unknown-generic warnings — pre-existing pattern; S2945 added ~4 lines matching the same pattern on `_gather_cleanup_preview`).
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate + Ledger candidate: media_tool.delete IRREVERSIBLE** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged; S2945 hit and workaround-cleared via ORM as expected.
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
**Slice 6 — `td_handlers_content` (6 tools):** CLOSED at S2936 (6/6, batch 1 + 2). ✅ **S2943 + S2944 + S2945 addenda:** file-scope doc closure for `content_tool` + `deliverable_tool` heading; four consecutive content_tool mutations pattern-aligned to S2942 envelope (bulk_archive_published S2943; bulk_archive + generate_newsletter S2944; run_cleanup S2945 — content_tool per-action 100%).
**Slice 7 — singleton bucket (9 tools across 8 handler files):** CLOSED at S2940 (9/9). ✅
**Ledger #16 twin-mirror enforcement substrate:** CLOSED at S2941 (PR #3517). ✅
**Ledger #38 dry_run MVP + Ledger #41 scoreboard promotion:** CLOSED at S2942. ✅
**Ledger #38 batch 2 (bulk_archive_published):** CLOSED at S2943 (PR #3524). ✅
**Ledger #38 batch 3 (bulk_archive + generate_newsletter):** CLOSED at S2944 (PR #3527). ✅
**Ledger #38 batch 4 (run_cleanup — closes content_tool 100%):** CLOSED at S2945 (PR #3529). ✅

**Substrate arcs CLOSED:** Ledger #5 Tier 1 MVP (S2938) + Ledger #16 (S2941) + Ledger #38 dry_run MVP (S2942) + Ledger #41 scoreboard (S2942) + Ledger #38 batch 2 (S2943) + Ledger #38 batch 3 (S2944) + Ledger #38 batch 4 (S2945).

**Total remaining tools to close: 0.** All ratified sweep scope discharged. Content_tool mutations are 100% pattern-aligned; delegated content_tool actions inherit dry_run coverage from sibling tools (blog_tool, feedback_tool, deliverable_tool). No Ledger #38 batch 5+ candidate currently identified within content_tool.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2942 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2945: zero A4 spend** — pure substrate ship (~$0.001 LLM cost from test suite setup + Rigby dispatch cost).
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2945)

See:
- **S2945 handoff (current):** `docs/handoffs/SESSION_2945_LEDGER_38_BATCH_4.md`
- **S2944 handoff:** `docs/handoffs/SESSION_2944_LEDGER_38_BATCH_3.md`
- **S2943 handoff:** `docs/handoffs/SESSION_2943_SLICE_6_LEDGER_38_BATCH_2.md`
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
- **S2944 Ledger #38 batch 3 code:** `core/services/td_handlers_content.py` (generate_newsletter line 4707+, bulk_archive line 5044+) + `core/services/pa_tool_schemas.py:4190` + `core/tests/test_s2944_dry_run_batch_3.py` (7 tests)
- **S2945 Ledger #38 batch 4 code:** `core/services/td_handlers_content.py` (run_cleanup line 4670-4738) + `core/tasks_misc.py` (`_gather_cleanup_preview` helper line 34-102 + `_impl_cleanup_stale_content` refactor line 104-159) + `core/services/pa_tool_schemas.py:4190` + `core/tests/test_s2945_dry_run_batch_4.py` (14 tests: 10 handler + 4 helper)
- **S2940 Batch 2b validation docs:** `docs/research/tools/validation/{code_job_tool,employee_tool,railway_tool}_validation.md`
- **S2939 Batch 2a validation docs:** `docs/research/tools/validation/{mission_verdict,newsletter_tool,rigby_work_item}_tool_validation.md`
- **S2937 validation docs:** `docs/research/tools/validation/{rigby_shift_brief,spider_data_aggregation,zoom_out}_tool_validation.md`
- **S2936 validation docs (S2945 refreshed with §6.6 run_cleanup evidence):** `docs/research/tools/validation/content_tool_validation.md`
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
