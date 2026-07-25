# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2950 CLOSED. A10 shipped: 5th signal-dispatch rule (`skill_demand` → `TrendAnalysisAgent`, intentional reuse). Chris ratified "Begin A10 please" at open; Rigby SIGN initially recommended TrendAnalysisAgent via introspection evidence (15 execs 30d, proven "signal → brief" reliability). Claude push-back on reuse coupling (same agent now serves trend_emergence + skill_demand) triggered a Rigby two-philosophy framing: (a) reuse for proven reliability vs (b) MarketIntelligenceAgent for cleaner attribution but only 5 lifetime execs. Converged on (a) — for net-new rules the primary risk is "will output be useful?", so proven brief-format reliability outweighs untested distinctness. Attribution concern (mixed metrics under one agent) ledgered for when per-pattern dashboards land. Live-verify PASSED — all 5 rules present in per_rule_diagnostics. Post-merge Rigby SIGN: AGREE (repo_tool.read grounded). Zoom-out fold: `future_trigger` — promote NEW-6 fair-share round-robin when ≥2 patterns concurrently hitting caps over ~7d.

**Refreshed 2026-07-24 (S2950 close).** Gap-map headline: `100 validated_full / 0 untested` (unchanged — signal-dispatch net-new, not a PA-tools sweep change).

**PRs shipped this session:**
- u-d-b PR **#3541** — S2950 A10: 5th signal-dispatch rule (skill_demand → TrendAnalysisAgent, intentional reuse) (2 files, +63/-3, 63/63 tests pass).

**Twin mirrors shipped this session:**
- Content mirror: `67c20981-6d5d-42e3-aa59-63b0ff94e420` (Architecture & Research workspace, category `initiative_phase_doc`; diagnostic flag cleared via ORM).
- Ratification envelope: `11406369-48d7-4add-810e-fd66a08b6381` (Architecture & Research workspace, `deliverable_type='ratification_record'`, category `governance`; diagnostic already null — no clear needed).

**Files shipped this session:**
- **MODIFIED** `core/services/signal_dispatch_service.py` (+22) — 5th `SignalDispatchRuleDef` (skill_demand__trend_analysis) with intentional-reuse framing comment.
- **MODIFIED** `core/tests/test_signal_dispatch_service.py` (+44/-3) — 4 new tests: mapping, count bump (4→5), reuse lock-in, scanner fan-out; diagnostics-shape test bumped to 5 rules.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- Recycled after PR #3541 merge (`make celery-recycle`) — task `631d3c89-9784-4370-81b3-f8fbf2585c77` returned all 5 rules in per_rule_diagnostics, skill_demand all-zeros matching 0-active baseline.

**Governance:** none this session. D6 moratorium unchanged. No new pattern candidates.

**Rigby Tool Gap Ledger:** no new formal entries. Known `deliverable_tool.create` diagnostic-flag bug re-hit on content mirror only — ratification mirror was created with `diagnostic_status=null` this session (inconsistent behavior worth noting).

Full session context: `docs/handoffs/SESSION_2950_A10_5TH_DISPATCH_RULE.md`.

---

## S2951 open sequence

**S2951 first-action is Chris-directed.** No pre-ratified plan carries forward from S2950.

### Universal open sequence

1. **Live-verify signal-dispatch pipeline still healthy:** ORM checks:
   - `SignalCluster.objects.filter(status='active').count()` — expect ≥ 9 (S2946 baseline + ongoing lift)
   - `SignalDispatch.objects.filter(scan_run_id='manual').count()` — expect ≥ 5 (S2948 baseline + any Chris clicks)
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 0 untested`.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2951 pin (retired at S2950 close cascade).
4. **Chris directs first-action from the deferred queue below.**

### Deferred queue (updated at S2950 close — Chris picks)

Engineering-first candidates (per `feedback_engineering_bias_over_audit`), sorted by leverage adjacency to what just shipped:

- **(A11 candidate) 6th signal-dispatch rule — `sentiment_shift` or `market_movement`** — no volume evidence gathered yet; would need Rigby ORM baseline first. Signal-dispatch registry now at 5 rules × 4 patterns represented (trend_emergence used twice). Only propose if Chris directs continued signal-dispatch expansion.
- **(NEW-1) Wire up A1 shipping** — engineering-net-new. Turn Rigby into a product a stranger can pay for.
- **(NEW-6) Fair-share round-robin scanning in `scan_and_dispatch()`** — Rigby S2949 + S2950 zoom-out both flag this as `future_trigger`. Promote when ≥2 patterns are concurrently active + hitting caps observed in `blocked_by_cap` diagnostics over ~7 days.
- **(NEW-7) `per_rule_diagnostics` persisted per `scan_run_id`** — currently logged + returned but not written to any audit table. Trigger: first request for time-series starvation analysis.
- **(NEW-8) Per-pattern effectiveness attribution for reused agents** — TrendAnalysisAgent now serves 2 rules (trend_emergence + skill_demand); mixed metrics muddy per-pattern effectiveness reasoning. Options: (1) add pattern_type header to agent brief output; (2) tag AgentTaskExecution rows with signal_pattern_type. Trigger: first pattern-scoped effectiveness dashboard or "which pattern is agent X best at?" question.
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

## What's forbidden at S2951 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2950 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2950 additions to the deferred queue:**

- **Per-pattern effectiveness attribution for reused agents** — see NEW-8 above.

**Prior deferred entries carry forward from S2949:**

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
**S2950 A10:** 5th signal-dispatch rule (skill_demand → TrendAnalysisAgent intentional reuse) (adjacent domain).

**Total remaining sweep tools: 0.** All ratified sweep scope discharged.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2950: zero A4 spend** — pure engineering ship.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller context (S2846 → S2950)

See:
- **S2950 handoff (current):** `docs/handoffs/SESSION_2950_A10_5TH_DISPATCH_RULE.md`
- **S2950 shipped code:**
  - `core/services/signal_dispatch_service.py:105-125` — 5th `SignalDispatchRuleDef` (skill_demand__trend_analysis, intentional reuse)
- **S2949 handoff:** `docs/handoffs/SESSION_2949_A9_4TH_DISPATCH_RULE.md`
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
  - `core/services/signal_dispatch_service.py` — `SignalDispatchService` + `SIGNAL_DISPATCH_RULES` (5 rules as of S2950, line 58) + `create_manual_dispatch` (S2947) + `execute_dispatch` + `MANUAL_SCAN_RUN_ID='manual'` + `DEFAULT_MANUAL_GUARD_WINDOW_MINUTES=5`
  - `core/views_signal_dispatch.py` — 4 endpoints: list (S2934 A4) + manual POST (S2947 A8) + resolve (S2947 A8) + eligible (S2948 NEW-4)
  - `core/models_signal_dispatch.py` — SignalDispatch model
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
