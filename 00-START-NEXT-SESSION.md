# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2949 CLOSED. A9 shipped: 4th signal-dispatch rule (`demand_spike` → `MarketMovementMonitorAgent`) + per-rule diagnostics. Chris ratified "Begin A9" at open; Rigby SIGN converged on MarketMovementMonitorAgent (22 execs / effectiveness 84 / best semantic fit) via 5 shortlist introspections. Rigby zoom-out fold flagged 4-rule starvation risk classified `same_session_mitigatable` → shipped per_rule_diagnostics counters same PR. Post-merge Rigby SIGN found second fold: `blocked_by_cap` incremented once then broke, under-reporting magnitude → classified `same_pr_mitigatable` → Chris ratified fix-now via plain-English decision routing → amendment PR #3539 shipped same session with magnitude fix. Live-verify PASSED — all 4 rules present in `per_rule_diagnostics`, real dedupe counts observed (trend_emergence=4 blocked_by_dedupe, opportunity_window=3, demand_spike + content_gap all zeros matching 0-active state). Post-merge Rigby SIGN used `repo_tool.read` on 3 file ranges (non-rubber-stamp evidence per `feedback_verify_rigby_tool_runs_before_trusting_sign`).

**Refreshed 2026-07-24 (S2949 close).** Gap-map headline: `100 validated_full / 0 untested` (unchanged — signal-dispatch net-new, not a PA-tools sweep change).

**PRs shipped this session:**
- u-d-b PR **#3538** — S2949 A9: 4th signal-dispatch rule + per-rule diagnostics (2 files, +121/-18, 58/58 tests pass).
- u-d-b PR **#3539** — S2949 A9 amendment: blocked_by_cap/daily_cap magnitude fix (2 files, +44/-3, 60/60 tests pass).

**Twin mirrors shipped this session:**
- Content mirror: `f6b386ab-19e6-4c33-990c-82773d6a96a3` (Architecture & Research workspace, category `initiative_phase_doc`; diagnostic flag cleared via ORM).
- Ratification envelope: `8dfb4644-e76b-49ab-aab4-4e07fa971cb0` (Architecture & Research workspace, `deliverable_type='ratification_record'`, category `governance`; diagnostic cleared via ORM).

**Files shipped this session:**
- **MODIFIED** `core/services/signal_dispatch_service.py` (net +64) — 4th `SignalDispatchRuleDef` (demand_spike__market_movement_monitor); `scan_and_dispatch()` returns `per_rule_diagnostics` (`eligible_count`, `blocked_by_cap`, `blocked_by_dedupe`, `blocked_by_daily_cap`); `_eligible_clusters_for_rule` returns `(clusters, dedupe_excluded_count)` tuple; magnitude semantics for cap counters.
- **MODIFIED** `core/tests/test_signal_dispatch_service.py` (net +83) — 7 new tests total across both PRs.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- Recycled after PR #3538 merge (`make celery-recycle`) — task `4858d440-b3f9-41a6-8a95-7fb145a4126a` returned expected shape.
- Recycled after PR #3539 amendment merge — workers matched HEAD at close.

**Governance:** none this session. D6 moratorium unchanged. One new pattern candidate observed (see below).

**Governance-worthy pattern candidate (first trigger only, S2949):** _"When a post-merge Rigby SIGN fold classifies `same_pr_mitigatable` after the PR is already closed, ship a same-session amendment PR as the operational equivalent."_ First trigger this session (PR #3539 shipped ~15 min after PR #3538). Watch for corroboration before proposing a Playbook rule. Do NOT codify yet. Combines with S2948 pattern candidate ("Shape MVP + same-session ergonomic upgrade") + S2947 pattern candidate ("spend-mutation endpoints must not be AllowAny") — three open pattern candidates in flight.

**Rigby Tool Gap Ledger:** no new formal entries. Known `deliverable_tool.create` diagnostic-flag bug re-hit twice (both mirrors) and re-worked-around via ORM as expected.

Full session context: `docs/handoffs/SESSION_2949_A9_4TH_DISPATCH_RULE.md`.

---

## S2950 open sequence

**S2950 first-action is Chris-directed.** No pre-ratified plan carries forward from S2949.

### Universal open sequence

1. **Live-verify signal-dispatch pipeline still healthy:** ORM checks:
   - `SignalCluster.objects.filter(status='active').count()` — expect ≥ 9 (S2946 baseline + ongoing lift)
   - `SignalDispatch.objects.filter(scan_run_id='manual').count()` — expect ≥ 5 (S2948 baseline + any Chris clicks)
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 0 untested`.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2950 pin (retired at S2949 close cascade).
4. **Chris directs first-action from the deferred queue below.**

### Deferred queue (updated at S2949 close — Chris picks)

Engineering-first candidates (per `feedback_engineering_bias_over_audit`), sorted by leverage adjacency to what just shipped:

- **(A10) 5th signal-dispatch rule — `skill_demand`** — pattern already ratified at S2949 for follow-up. 133 total clusters / 4 detecting. Agent shortlist to route through Rigby introspection: `TalentMarketAnalyst` (if exists) / `MarketIntelligenceAgent` / `OpportunityPipelineAgent`.
- **(NEW-1) Wire up A1 shipping** — engineering-net-new. Turn Rigby into a product a stranger can pay for.
- **(NEW-6) Fair-share round-robin scanning in `scan_and_dispatch()`** — S2949 amendment made starvation _visible_ but not _prevented_. Rule tuple order still determines dispatch priority under cap contention. Add round-robin or slot-based fairness. Needs regression tests on non-drift correctness. Trigger to open: observed non-zero `blocked_by_cap` on a rule for N consecutive scans.
- **(NEW-7) `per_rule_diagnostics` persisted per `scan_run_id`** — currently logged + returned but not written to any audit table. If operators start querying "which rule got starved most yesterday?" ledger growth matters. Deferred until real need surfaces.
- **(NEW-2) Rank + cap + paginate follow-ups on Rigby S2946 zoom-out fold** — reactive; only ship if a specific consumer bites at post-lift active-count levels.
- **(NEW-3) Option 2 revisit — per-pattern-type diversity floors** — if /3 across the board proves too noisy for `opportunity_window`, introduce `PER_PATTERN_DIVERSITY_FLOOR` dict.
- **(NEW-5) "Manual dispatch" cost estimate in modal (S2947 Z2 reactive follow-up)** — if operators start firing many manual dispatches and LLM spend spikes.
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(E) Tier 2 lint promotion** — envelope-JSON top-level-key parse. Ledger #5 sub-substrate.
- **(H) generate_newsletter dry_run default flip (record-only S2944)**.
- **(I) bulk_archive statuses autofill robustness (record-only S2944)** — 2nd trigger observed at S2945. ~5-line handler fix + regression test.
- **Envelope enhancement (record-only S2942)** — `verify_hint` + `would_write_count` for dry_run envelopes.
- **Close-ceremony ledger-flip checklist (meta-fix, record-only S2942)**.
- **Deliverable v1 template retrofit (record-only S2943)**.

---

## What's forbidden at S2950 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2949 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2949 additions to the deferred queue:**

- **Fair-share round-robin scanning** — see NEW-6 above.
- **Persist `per_rule_diagnostics` in audit table** — see NEW-7 above.

**Prior deferred entries carry forward from S2948:**

- **Advanced paste-UUID fallback** — the S2948 picker replaced paste-UUID entirely. If an operator ever needs to dispatch a cluster NOT in the eligible list, add a collapsed "Advanced: paste UUID" toggle.
- **Server-side search + pagination on `/eligible/`** — client-side filter fine at ~10-100 clusters.

**Prior deferred entries carry forward from S2947:**

- **Z1 — Manual+auto shared daily-cap UI hint** (Rigby S2947 zoom-out, reactive).
- **Z2 — Cost estimate / rate-limiting story for the modal** (Rigby S2947 zoom-out, reactive) — see NEW-5.
- **Z4 — Queue backlog handling / CSRF polish / "queued" success toast** (Rigby S2947 zoom-out, reactive).

**Prior deferred entries carry forward from S2946:**

- **Rank + cap + paginate follow-ups** (Rigby S2946 zoom-out fold, reactive).
- **Per-pattern-type diversity floors** (Option 2 alternate to S2946 shipped Option 1) — see NEW-3.

**Long-standing deferred entries:**

- **Ledger candidate — `bulk_archive` statuses autofill robustness** — HIGH priority per S2945.
- **`generate_newsletter` dry_run default flip (record-only S2944).**
- **Deliverable v1 template retrofit (record-only S2943).**
- **Envelope enhancement candidates (S2942, record-only).**
- **Close-ceremony ledger-flip checklist (S2942 meta-fix candidate, record-only).**
- **dry_run scope expansion to batch 2a/2b (S2942 deferred).**
- **Ledger #16b candidate** — needs 3+ triggers.
- **Ledger candidate — `code_job_tool.submit` silent-degrade on Celery dispatch fail.**
- **Ledger candidate — `employee_tool.run_now` double-dispatch hazard.**
- **Ledger candidate — `railway_tool` `restart`+`redeploy` functional equivalence.**
- **Ledger #5 Tier-2 candidate — bare invalid-action envelope pattern** — sixth-instance corroboration at S2940.
- **`_handle_railway` docstring under-lists actions** (5/7 named) — ~2-min doc fix at next `td_handlers_railway.py` touch.
- **Ledger #5 Tier 2 (envelope-JSON parse)** — deferred per Rigby S2938 ZO AGREE.
- **Ledger #5 Tier 3 (semantic distance between prose and field names)** — too fuzzy for MVP.
- **Ledger #36 (blog_tool Deliverable/SelfBlog approve-path fix)** — correctness bug candidate.
- **Ledger #37 (feedback_tool.update `.save()` → update_fields)** — ~1-line fix.
- **Ledger #39 (rigby_work_queue module docstring stale)** — ~5-min doc fix.
- **Ledger #40 candidate (newsletter_tool sources drift)** — record-only.
- **`execution_history_tool` `hours` schema declaration** — ~3 min follow-up PR.
- **Invalid-action non-gating consistency across Slice 6+7 handlers** — Ledger #5 consolidation candidate.
- **`zoom_out_tool include=aggregations` Rigby-wrapper investigation (S2937 §6.1a anomaly)** — PA-wrapper investigation.
- **CompetitorAnalysisAgent hardening candidate** — S2929 deferred.
- **Dedicated `agent_execution_query` PA tool** — S2931 Ledger #33 alternative path.
- **Shared `skip_in_test` decorator** — S2931 Ledger #34 alternative.
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A.
- **Bundled dev-env drift slate** — pre-existing pyright warnings on many files including `signal_aggregation_service.py` (S2946) + `signal_dispatch_service.py` (S2947+S2948+S2949) + `views_signal_dispatch.py` (S2947+S2948) + `test_s2934_signal_dispatch_harness.py` (S2947+S2948) + `test_signal_dispatch_service.py` (S2949).
- **Phase 0 heading fixes (8 tools)** — doc-only PR.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate + Ledger candidate: media_tool.delete IRREVERSIBLE** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged; S2949 hit twice and workaround-cleared via ORM.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **S2919 narrative_tool dev-env drift** — unchanged.
- **S2925 Ledger #34 (LOW, distinct from S2931's #34)** — broader stale-model latent bug.
- **S2926 Ledger candidate — AgentTaskExecution pre-existing pyright drift** — bundled dev-env drift.
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
**Slice 6 — `td_handlers_content` (6 tools):** CLOSED at S2936 (6/6). ✅
**Slice 7 — singleton bucket (9 tools across 8 handler files):** CLOSED at S2940 (9/9). ✅
**Ledger #16 twin-mirror enforcement substrate:** CLOSED at S2941 (PR #3517). ✅
**Ledger #38 dry_run MVP + Ledger #41 scoreboard promotion:** CLOSED at S2942. ✅
**Ledger #38 batch 2/3/4:** CLOSED at S2943/S2944/S2945.
**S2946 A6:** Signal-substrate topology fix (adjacent domain).
**S2947 A8:** Signal-dispatch button + POST/resolve endpoints (adjacent domain).
**S2948 NEW-4:** Cluster picker + eligible endpoint + postbuild template sync (adjacent domain).
**S2949 A9:** 4th signal-dispatch rule (demand_spike) + per-rule diagnostics + magnitude-fix amendment (adjacent domain).

**Total remaining sweep tools: 0.** All ratified sweep scope discharged.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2949: zero A4 spend** — pure engineering ship.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller context (S2846 → S2949)

See:
- **S2949 handoff (current):** `docs/handoffs/SESSION_2949_A9_4TH_DISPATCH_RULE.md`
- **S2949 shipped code:**
  - `core/services/signal_dispatch_service.py:82-108` — 4th `SignalDispatchRuleDef` (demand_spike__market_movement_monitor)
  - `core/services/signal_dispatch_service.py:130-200` — `scan_and_dispatch()` with per_rule_diagnostics + magnitude semantics
  - `core/services/signal_dispatch_service.py:210-241` — `_eligible_clusters_for_rule` returning `(clusters, dedupe_excluded_count)` tuple
- **S2948 handoff:** `docs/handoffs/SESSION_2948_NEW_4_CLUSTER_PICKER.md`
- **S2947 handoff:** `docs/handoffs/SESSION_2947_A8_MANUAL_DISPATCH_BUTTON.md`
- **S2946 handoff:** `docs/handoffs/SESSION_2946_A6_DIVERSITY_DENOMINATOR.md`
- **S2945 handoff:** `docs/handoffs/SESSION_2945_LEDGER_38_BATCH_4.md`
- **S2944 handoff:** `docs/handoffs/SESSION_2944_LEDGER_38_BATCH_3.md`
- **S2943 handoff:** `docs/handoffs/SESSION_2943_SLICE_6_LEDGER_38_BATCH_2.md`
- **S2942 handoff:** `docs/handoffs/SESSION_2942_S2942_CLOSURE_PLAN.md`
- **S2941 handoff:** `docs/handoffs/SESSION_2941_LEDGER_16_TWIN_MIRROR.md`
- **S2940 handoff:** `docs/handoffs/SESSION_2940_SLICE_7_CLOSE.md`
- **Signal-substrate anchor files:**
  - `core/models_signal_intelligence.py` — `SignalCluster` model + `is_actionable` property (line 249) + status enum (line 203)
  - `core/services/signal_aggregation_service.py` — `_calculate_strength` (line 839) + `_calculate_confidence` (line 866) + `MIN_CLUSTER_SIZE=3` (line 44)
  - `core/services/signal_dispatch_service.py` — `SignalDispatchService` + `SIGNAL_DISPATCH_RULES` (4 rules as of S2949, line 58) + `create_manual_dispatch` (S2947, line 308) + `execute_dispatch` (line 369) + `MANUAL_SCAN_RUN_ID='manual'` + `DEFAULT_MANUAL_GUARD_WINDOW_MINUTES=5`
  - `core/views_signal_dispatch.py` — 4 endpoints: list (S2934 A4) + manual POST (S2947 A8) + resolve (S2947 A8) + eligible (S2948 NEW-4)
  - `core/models_signal_dispatch.py` — SignalDispatch model
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
