# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2948 CLOSED. NEW-4 Cluster Picker (Shape B upgrade) shipped + postbuild template auto-sync bundled. Chris hit the paste-UUID ergonomic gap Shape C left within minutes of the S2947 A8 ship ("I don't have a UUID to search for…") and pre-ratified the Shape B upgrade in the same session ("if you have the context and everything ship it now"). ManualDispatchModal rewritten as 2-column layout: searchable cluster list (left) + preview+rule+submit (right). New `GET /api/v1/agents/signal-dispatches/eligible/` endpoint returns active clusters with matching rules + guard-block flags. Default hides clusters whose only matching rule is guard-blocked (avoids 409s from the picker); `include_blocked=1` surfaces them with `guard_blocked_rules` populated. **Bonus fix bundled:** `frontend/scripts/generate-manifest.mjs` now auto-syncs `core/templates/index.html` bundle hashes from `dist/index.html` on every `npm run build` — permanently removes the stale-template bug that broke Chris's UI mid-S2947 close (that manual fix went out as PR #3535). Post-merge Rigby SIGN used `repo_tool` reads on views + postbuild script (non-rubber-stamp evidence per `feedback_verify_rigby_tool_runs_before_trusting_sign`). 32/32 signal-dispatch tests pass (25 pre-existing + 7 new for eligible endpoint). Live-verify pending Chris's first click on the new picker.

**Refreshed 2026-07-24 (S2948 close).** Gap-map headline: `100 validated_full / 0 untested` (unchanged — signal-dispatch UI upgrade, not a PA-tools sweep change).

**PRs shipped this session:**
- u-d-b PR **#3536** — S2948 NEW-4: cluster picker (Shape B) + postbuild template auto-sync (7 files, +431/-147, 32/32 tests pass).

**Twin mirrors shipped this session:**
- Content mirror: `2bfac487-5869-4f26-90d0-8146a0ce0cf3` (Architecture & Research workspace, category `initiative_phase_doc`; diagnostic flag cleared via ORM).
- Ratification envelope: `242deb77-e58c-41ce-a19f-765fb9d41ad0` (Architecture & Research workspace, `deliverable_type='ratification_record'`, category `governance`; diagnostic cleared via ORM).

**Files shipped this session:**
- **NEW** `signal_dispatches_eligible` view in `core/views_signal_dispatch.py` (+118) — GET `/api/v1/agents/signal-dispatches/eligible/`.
- **MODIFIED** `core/urls.py` (+2) — new route.
- **NEW** 7 regression tests in `core/tests/test_s2934_signal_dispatch_harness.py` (+79) — `TestSignalDispatchesEligibleEndpoint`.
- **REWRITE** `ManualDispatchModal` in `frontend/src/pages/workspace/tabs/SignalDispatchesTab.tsx` (~130 net delta) — 2-column picker layout.
- **MODIFIED** `frontend/src/lib/api.ts` (+3) — `agentsApi.signalDispatchesEligible()`.
- **MODIFIED** `frontend/scripts/generate-manifest.mjs` (+38) — postbuild template auto-sync.
- **MODIFIED** `core/templates/index.html` — first auto-synced write (S2948 bundle hashes).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- Recycled after PR #3536 merge (`make celery-recycle` + `make stop && make start`).
- Frontend rebuilt (`npm run build`) — auto-sync log line confirmed: `[generate-manifest] Synced core/templates/index.html to current dist hashes.`
- Live-verify pending Chris's first click.

**Governance:** none this session. D6 moratorium unchanged. Governance pattern candidate observed (see below).

**Governance-worthy pattern candidate (first trigger only, S2948 addition):** _"When Shape MVP will inevitably surface an ergonomic gap on first-use, ship the ergonomic upgrade in the same session (or explicitly commit to a follow-up before merging the MVP)."_ S2947 A8 Shape C → S2948 NEW-4 Shape B loop took ~30 min from "I don't have a UUID" to shipped/merged/recycled — good outcome, but validates Shape C under-scoped the ergonomic requirement. Watch for corroboration on another Shape MVP → same-session upgrade before proposing a playbook rule. Do NOT codify yet. Combines with S2947 first-trigger candidate ("spend-mutation endpoints must not be AllowAny") — two open pattern candidates in flight.

**Rigby Tool Gap Ledger:** no new formal entries. Known `deliverable_tool.create` diagnostic-flag bug re-hit twice (both mirrors) and re-worked-around via ORM as expected.

Full session context: `docs/handoffs/SESSION_2948_NEW_4_CLUSTER_PICKER.md`.

---

## S2949 open sequence

**S2949 first-action is Chris-directed.** No pre-ratified plan carries forward from S2948.

### Universal open sequence

1. **Live-verify signal-dispatch pipeline still healthy:** ORM checks:
   - `SignalCluster.objects.filter(status='active').count()` — expect ≥ 9 (S2946 baseline + ongoing lift)
   - `SignalDispatch.objects.filter(scan_run_id='manual').count()` — expect ≥ 2 (S2947 baseline + any Chris clicks)
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 0 untested`.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2949 pin (retired at S2948 close cascade).
4. **Chris directs first-action from the deferred queue below.**

### Deferred queue (updated at S2948 close — Chris picks)

Engineering-first candidates (per `feedback_engineering_bias_over_audit`), sorted by leverage adjacency to what just shipped:

- **(A9) 4th signal-dispatch rule** — `demand_spike` (250 clusters) or `skill_demand` (131 clusters). **Directly amplified by S2946 + S2947 + S2948 combined** — more clusters + easy-to-use picker = more useful rule-firing surface.
- **(NEW-1) Wire up A1 shipping** — engineering-net-new. Turn Rigby into a product a stranger can pay for.
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

## What's forbidden at S2949 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2948 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2948 additions to the deferred queue:**

- **Advanced paste-UUID fallback** — the S2948 picker replaced paste-UUID entirely. If an operator ever needs to dispatch a cluster NOT in the eligible list (e.g., `include_blocked=1` case or a non-actionable cluster), add a collapsed "Advanced: paste UUID" toggle. Only ship if the need surfaces.
- **Server-side search + pagination on `/eligible/`** — client-side filter is fine at ~10-100 clusters. If active count grows past ~500 (unlikely at current post-S2946 levels), promote to server-side.

**Prior deferred entries carry forward from S2947:**

- **Z1 — Manual+auto shared daily-cap UI hint** (Rigby S2947 zoom-out, reactive).
- **Z2 — Cost estimate / rate-limiting story for the modal** (Rigby S2947 zoom-out, reactive) — see NEW-5 above.
- **Z4 — Queue backlog handling / CSRF polish / "queued" success toast** (Rigby S2947 zoom-out, reactive).

**Prior deferred entries carry forward from S2946:**

- **Rank + cap + paginate follow-ups** (Rigby S2946 zoom-out fold, reactive).
- **Per-pattern-type diversity floors** (Option 2 alternate to S2946 shipped Option 1) — see NEW-3 above.

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
- **Bundled dev-env drift slate** — pre-existing pyright warnings on many files including `signal_aggregation_service.py` (S2946) + `signal_dispatch_service.py` (S2947) + `views_signal_dispatch.py` (S2947+S2948) + `test_s2934_signal_dispatch_harness.py` (S2947+S2948).
- **Phase 0 heading fixes (8 tools)** — doc-only PR.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate + Ledger candidate: media_tool.delete IRREVERSIBLE** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged; S2948 hit twice and workaround-cleared via ORM.
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

**Total remaining sweep tools: 0.** All ratified sweep scope discharged.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2948: zero A4 spend** — pure engineering ship.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller context (S2846 → S2948)

See:
- **S2948 handoff (current):** `docs/handoffs/SESSION_2948_NEW_4_CLUSTER_PICKER.md`
- **S2948 shipped code:**
  - `core/views_signal_dispatch.py:141-238` — `signal_dispatches_eligible` view
  - `frontend/src/pages/workspace/tabs/SignalDispatchesTab.tsx:117-317` — ManualDispatchModal v2
  - `frontend/scripts/generate-manifest.mjs:104-139` — postbuild template auto-sync
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
  - `core/services/signal_dispatch_service.py` — `SignalDispatchService` + `SIGNAL_DISPATCH_RULES` (line 58) + `create_manual_dispatch` (S2947, line 308) + `execute_dispatch` (line 369) + `MANUAL_SCAN_RUN_ID='manual'` + `DEFAULT_MANUAL_GUARD_WINDOW_MINUTES=5`
  - `core/views_signal_dispatch.py` — 3 endpoints: list (S2934 A4) + manual POST (S2947 A8) + resolve (S2947 A8) + eligible (S2948 NEW-4)
  - `core/models_signal_dispatch.py` — SignalDispatch model
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
