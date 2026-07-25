# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2947 CLOSED. A8 Manual Dispatch Button shipped (Shape C — paste UUID + inline resolve preview + rule auto-pick). Chris picked A8 as engineering-first first-action after plain-English framing of the S2946-carryforward deferred queue. Claude directed investigation; verify-before-build found the full backend surface already existed (`SignalDispatchService.execute_dispatch`, `dispatch_signal` CLI, `dispatch_agent_for_signal_cluster` Celery task, `SignalDispatch(scan_run_id='manual')` model column, list endpoint + tab UI with amber Zap badge already coded) — only missing = one POST endpoint + one modal + button. Joint Claude+Rigby framing offered Shape A (~40 min debug MVP) / Shape B (~2 hrs full dropdown) / Shape C (~60-90 min paste+resolve+auto-rule). Chris ratified Shape C, no force. Rigby T1 SIGN used `repo_tool` reads + grep (non-rubber-stamp per `feedback_verify_rigby_tool_runs_before_trusting_sign`) — 5/5 design invariants PASS, both VERIFY checks PASS, F-BLOCKING zoom-out Z3 (AllowAny on mutation POST) → fixed same-PR at commit `d53054ff8` (changed to `IsAuthenticated`). Chris D0 ratified after plain-English summary. Post-merge live-verified end-to-end: cluster `0cd4f30d-...` → RESOLVE returned 1 matching rule → dispatch `8d548726-...` ran on long_running worker in ~20s (outcome=succeeded, no error) → guard correctly blocked immediate re-fire (409 `guard_blocked`) → CLI `--force` bypass path still works. Frontend `npm run build` produced fresh bundle (`sha=5fb5db1a4` in `__manifest.json`); Chris hard-refreshed browser to see button.

**Refreshed 2026-07-24 (S2947 close).** Gap-map headline: `100 validated_full / 0 untested` (unchanged — signal-dispatch surface change, not a PA-tools sweep change).

**PRs shipped this session:**
- u-d-b PR **#3533** — S2947 A8: manual dispatch button + Shape C modal + service extraction + Rigby F-BLOCKING Z3 fix (7 files, +705/-94, 25/25 tests pass).

**Twin mirrors shipped this session (per `feedback_twin_deliverable_at_every_ratification`):**
- Content mirror: `07dd725f-7404-4cc1-b474-9bb638da42db` (Architecture & Research workspace, category `initiative_phase_doc`; diagnostic flag cleared via ORM per known bug).
- Ratification envelope: `5e69fdb5-ad4f-4e6b-b9e3-b1124cc53f4d` (Architecture & Research workspace, `deliverable_type='ratification_record'`, category `governance`; diagnostic cleared via ORM per known bug).

**Files shipped this session:**
- **MODIFIED** `core/services/signal_dispatch_service.py` — added `create_manual_dispatch` service method (+126) with structured `error_code` catalog; added `MANUAL_SCAN_RUN_ID` + `DEFAULT_MANUAL_GUARD_WINDOW_MINUTES` module constants.
- **REWRITE** `core/management/commands/dispatch_signal.py` — thin wrapper over new service method (-80 net, behavior-identical).
- **MODIFIED** `core/views_signal_dispatch.py` — added `signal_dispatches_manual` (POST, `IsAuthenticated`) + `signal_dispatch_resolve_cluster` (GET, `AllowAny` matching list endpoint precedent) (+129).
- **MODIFIED** `core/urls.py` — 2 new paths under `api/v1/agents/signal-dispatches/`.
- **NEW** 11 regression tests in `core/tests/test_s2934_signal_dispatch_harness.py` — covers auto-pick, all error codes, guard 409 with `existing_dispatch_id`, and invariant that API never honors `force` param.
- **MODIFIED** `frontend/src/lib/api.ts` — 2 new API methods.
- **MODIFIED** `frontend/src/pages/workspace/tabs/SignalDispatchesTab.tsx` — `ManualDispatchModal` component + "Dispatch now" header button + query invalidation on success.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- Recycled after PR #3533 merge (`make celery-recycle` + `make stop && make start` for daphne to pick up new URL routes).
- Frontend rebuild required — Django serves static `frontend/dist/` bundle, not vite dev; ran `npm run build` at close and Chris hard-refreshed browser.
- Live-verified via Django shell probe on real active cluster `0cd4f30d-f8a2-4ca1-81d0-945e44442b9d` — dispatch succeeded, guard blocked re-fire, force bypass works.
- Gap-map regen not required.

**Governance:** none. D6 moratorium unchanged. One first-trigger pattern candidate observed (see below).

**Governance-worthy pattern candidate (first trigger only):** _"Any endpoint that can trigger spend (LLM fan-out / Celery dispatch) must tighten mutation permissions same-PR; `AllowAny` is never acceptable on spend mutations."_ S2947 A8 Z3 is trigger #1. Watch for corroboration in another PR before proposing playbook amendment. Do NOT codify yet.

**Rigby Tool Gap Ledger:** no new formal entries. Known `deliverable_tool.create` diagnostic-flag bug re-hit twice (both mirrors) and re-worked-around via ORM as expected.

Full session context: `docs/handoffs/SESSION_2947_A8_MANUAL_DISPATCH_BUTTON.md`.

---

## S2948 open sequence

**S2948 first-action is Chris-directed.** No pre-ratified plan carries forward from S2947.

### Universal open sequence

1. **Live-verify S2946 + S2947 lift still healthy:** run ORM check `SignalCluster.objects.filter(status='active').count()` — expect ≥ 9 and hopefully growing. Also `SignalDispatch.objects.filter(scan_run_id='manual').count()` — should be ≥ 2 (baseline from S2947 verify).
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline still reads `100 validated_full / 0 untested`, and `per_execution_mode.live` ≥ 3.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2948 pin (retired at S2947 close cascade).
4. **Chris directs first-action from the deferred queue below.**

### Deferred queue (updated at S2947 close — Chris picks)

Engineering-first candidates (per `feedback_engineering_bias_over_audit`), sorted by leverage adjacency to what just shipped:

- **(A9) 4th signal-dispatch rule** — `demand_spike` (250 clusters) or `skill_demand` (131 clusters). **Directly amplified by S2946 + S2947 combined** — more active clusters + a manual dispatch surface = more rule-firing paths.
- **(NEW-4) Cluster picker on Signal Dispatches tab (Shape B upgrade path)** — replace paste-UUID with a searchable dropdown of active clusters. Now that the POST endpoint + modal exists, this is a pure UX upgrade (~90 min). Would need a new `/eligible/` endpoint that returns active clusters + their matching rules.
- **(NEW-5) "Manual dispatch" cost estimate in modal (Z2 reactive follow-up)** — if operators start firing many manual dispatches and LLM spend spikes.
- **(NEW-1) Wire up A1 shipping** — engineering-net-new. Turn Rigby into a product a stranger can pay for.
- **(NEW-2) Rank + cap + paginate follow-ups on Rigby S2946 zoom-out fold** — reactive; only ship if a specific consumer bites at post-lift active-count levels. Watch signal_dispatch fire rate + curator snapshot sizes + UI response times + dashboard density over 24–48h.
- **(NEW-3) Option 2 revisit — per-pattern-type diversity floors** — if /3 across the board proves too noisy for `opportunity_window` (natively hits 5+ sources on mega-topics), introduce `PER_PATTERN_DIVERSITY_FLOOR` dict.
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(E) Tier 2 lint promotion** — envelope-JSON top-level-key parse. Ledger #5 sub-substrate.
- **(H) generate_newsletter dry_run default flip (record-only S2944)** — schema says "DEFAULT: true" but handler defaults False.
- **(I) bulk_archive statuses autofill robustness (record-only S2944)** — 2nd trigger observed at S2945. Port the coercion pattern to `_handle_bulk_archive`. ~5-line handler fix + regression test.
- **Envelope enhancement (record-only S2942)** — `verify_hint` + `would_write_count` for dry_run envelopes. Needs 2nd-trigger corroboration.
- **Close-ceremony ledger-flip checklist (meta-fix, record-only S2942)** — first trigger from S2942 reconciliation; watch for 2nd trigger.
- **Deliverable v1 template retrofit (record-only S2943)**.

---

## What's forbidden at S2948 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2947 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2947 additions to the deferred queue:**

- **Z1 — Manual+auto shared daily-cap UI hint** (Rigby S2947 zoom-out, reactive). Only ship if operators hit surprising cap blocks.
- **Z2 — Cost estimate / rate-limiting story for the modal** (Rigby S2947 zoom-out, reactive).
- **Z4 — Queue backlog handling / CSRF polish / "queued" success toast** (Rigby S2947 zoom-out, reactive).
- **Shape B cluster-picker upgrade** — see NEW-4 above.

**All prior deferred entries carry forward from S2946:**

- **Rank + cap + paginate follow-ups** (Rigby S2946 zoom-out fold, reactive) — 4 downstream consumer categories at 10× active-cluster count.
- **Per-pattern-type diversity floors** (Option 2 alternate to S2946 shipped Option 1) — see NEW-3 above.
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
- **Ledger #39 (rigby_work_queue module docstring stale)** — auto-detected by Ledger #5 lint. ~5-min doc fix.
- **Ledger #40 candidate (newsletter_tool sources drift)** — record-only.
- **`execution_history_tool` `hours` schema declaration** — ~3 min follow-up PR.
- **Invalid-action non-gating consistency across Slice 6+7 handlers** — Ledger #5 consolidation candidate.
- **`zoom_out_tool include=aggregations` Rigby-wrapper investigation (S2937 §6.1a anomaly)** — PA-wrapper investigation.
- **CompetitorAnalysisAgent hardening candidate** — S2929 deferred.
- **Dedicated `agent_execution_query` PA tool** — S2931 Ledger #33 alternative path.
- **Shared `skip_in_test` decorator** — S2931 Ledger #34 alternative.
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A.
- **Bundled dev-env drift slate** — pre-existing pyright warnings on `pa_tool_schemas.py` + `build_pa_tool_audit.py` + `pa_tools_gap_map.py` + `session_lifecycle.py` + `twin_mirror_enforcement.py` + `td_handlers_agents.py` + `td_handlers_content.py` + `tasks_misc.py` + `signal_aggregation_service.py` + `test_s2946_diversity_denominator.py` + **`signal_dispatch_service.py` (S2947 confirmed pre-existing: `.delay()` typing quirk on lines 228 + 363)** + **`views_signal_dispatch.py` (S2947 confirmed pre-existing: `request.GET/data` typing pattern)** + **`test_s2934_signal_dispatch_harness.py` (S2947 confirmed pre-existing: `create_user` on Manager)**.
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate + Ledger candidate: media_tool.delete IRREVERSIBLE** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged; S2947 hit twice and workaround-cleared via ORM as expected.
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
**Slice 6 — `td_handlers_content` (6 tools):** CLOSED at S2936 (6/6). ✅
**Slice 7 — singleton bucket (9 tools across 8 handler files):** CLOSED at S2940 (9/9). ✅
**Ledger #16 twin-mirror enforcement substrate:** CLOSED at S2941 (PR #3517). ✅
**Ledger #38 dry_run MVP + Ledger #41 scoreboard promotion:** CLOSED at S2942. ✅
**Ledger #38 batch 2/3/4:** CLOSED at S2943/S2944/S2945.
**S2946 A6:** Signal-substrate topology fix (adjacent domain).
**S2947 A8:** Signal-dispatch UI + API surface (adjacent domain).

**Total remaining sweep tools: 0.** All ratified sweep scope discharged.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2947: zero A4 spend** — pure engineering ship.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2947)

See:
- **S2947 handoff (current):** `docs/handoffs/SESSION_2947_A8_MANUAL_DISPATCH_BUTTON.md`
- **S2947 shipped code:**
  - `core/services/signal_dispatch_service.py:308-434` — `create_manual_dispatch` method
  - `core/views_signal_dispatch.py:88-193` — POST + resolve views
  - `frontend/src/pages/workspace/tabs/SignalDispatchesTab.tsx:117-322` — ManualDispatchModal
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
  - `core/models_signal_dispatch.py` — SignalDispatch model (audit row)
  - `core/tasks_misc.py:4547` — decay path (`detecting > 2 days → decayed`)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
