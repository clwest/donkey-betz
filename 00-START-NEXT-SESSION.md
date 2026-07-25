# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2946 CLOSED. A6 SignalCluster promotion diversity denominator shipped (`_calculate_strength` diversity_factor denominator `source_count/5` → `/3` in `signal_aggregation_service.py:855` — aligns with `MIN_CLUSTER_SIZE=3`). Chris picked A6 as engineering-first first-action after plain-English framing of the 5 deferred-queue candidates. Claude directed investigation; raw-ORM verified root cause (838/870 = 96% of SignalClusters decay/archive without promotion; no decayed cluster ever hit ≥4 sources; naturally-narrow signal types like skill_demand from job spiders capped at ~3 sources, so `diversity_factor` capped at 0.6 and strength never cleared 0.5 bar). Rigby T1 SIGN converged on Option 1 (denominator /3) over Option 2 (per-pattern floors) on simplicity + reversibility grounds; AGREE non-blocking. Chris D0 ratified on plain-English framing (1-line change, reversible, precision protected by unchanged confidence floor). Zoom-out fold (per `feedback_zoom_out_ask_per_rigby_sign`): 4 downstream breakpoint categories at 10× active-cluster count (agent dispatch loops, curated snapshots, UI/API pagination, dashboards) — reactive rank+cap+paginate follow-ups if any bite. **Retrospective lift:** 153 of 527 historical decayed rows would have promoted under new formula (145 3-source cohort). Projected steady-state active count: 9 → ~80–100 (~10×).

**Refreshed 2026-07-24 (S2946 close).** Gap-map headline: `100 validated_full / 0 untested` (unchanged). Scoreboard baseline unchanged. Signal-substrate topology change; not a PA-tools sweep change.

**PRs shipped this session:**
- u-d-b PR **#3531** — S2946 A6: SignalCluster promotion diversity denominator 5→3 (`signal_aggregation_service.py:855` + 7 regression tests + validation doc); ~10× projected active-cluster lift; precision guardrail (confidence floor) unchanged.

**Twin mirrors shipped this session (per `feedback_twin_deliverable_at_every_ratification`):**
- Content mirror: `3374ffce-3925-4bcc-a527-e2a9a38f052a` (Architecture & Research workspace, category `initiative_phase_doc`; diagnostic flag cleared via ORM per known bug).
- Ratification envelope: `a01ea4f1-5536-49a7-beea-a1a99c2e2107` (Architecture & Research workspace, `deliverable_type='ratification_record'`, category `governance`; diagnostic cleared via ORM per known bug).

**Files shipped this session:**
- **MODIFIED** `core/services/signal_aggregation_service.py:855` — `diversity_factor = min(1.0, source_count / 3)` (was `/ 5`) + 6-line rationale comment.
- **NEW** `core/tests/test_s2946_diversity_denominator.py` — 7 regression tests locking new formula + precision invariants.
- **NEW** `docs/research/platform/S2946_A6_diversity_denominator.md` — validation doc with root cause, quantified lift, SIGN cycle, limitations.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- Recycled after PR #3531 merge (workers matched HEAD `7be5ee9af`).
- Live-verified via Rigby prose-only check: `SignalCluster.status='active'` count = 9 (baseline, as expected — lift is going-forward only), workers loaded post-merge = yes, no unexpected activity in 15 min post-recycle.
- Gap-map regen not required (signal substrate topology change, not PA-tools sweep).

**Governance:** none. D6 moratorium unchanged. Zoom-out fold shipped as reactive-follow-up deferred-queue additions (not same-PR).

**Rigby Tool Gap Ledger:** no new formal entries. Two known bugs re-hit and re-worked-around via ORM as expected (`deliverable_tool.create` diagnostic flag + empty `deliverable_type`).

Full session context: `docs/handoffs/SESSION_2946_A6_DIVERSITY_DENOMINATOR.md`.

---

## S2947 open sequence

**S2947 first-action is Chris-directed.** No pre-ratified plan carries forward from S2946.

### Universal open sequence

1. **Live-verify S2946 lift materializing:** run ORM check `SignalCluster.objects.filter(status='active').count()` — expect ≥ 9 and hopefully growing as new spider signals hit the /3 aggregator. If still exactly 9 after 24h, investigate whether spiders are pushing fresh signals.
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline still reads `100 validated_full / 0 untested`, and `per_execution_mode.live` ≥ 3.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2947 pin (retired at S2946 close cascade).
4. **Chris directs first-action from the deferred queue below.**

### Deferred queue (updated at S2946 close — Chris picks)

Engineering-first candidates (per `feedback_engineering_bias_over_audit`), sorted by leverage adjacency to S2946:

- **(A9) 4th signal-dispatch rule** — `demand_spike` (250 clusters) or `skill_demand` (131 clusters). **Directly amplified by S2946 lift** — more active clusters = more rule-firing surface.
- **(A8) Signal Dispatches "Manual dispatch" button** — ~30 min UI, engineering. **More useful post-S2946** because more active clusters means the button dispatches something interesting.
- **(NEW-1) Wire up A1 shipping** — engineering-net-new. Turn Rigby into a product a stranger can pay for.
- **(NEW-2) Rank + cap + paginate follow-ups on Rigby S2946 zoom-out fold** — reactive; only ship if a specific consumer bites at post-lift active-count levels. Watch signal_dispatch fire rate + curator snapshot sizes + UI response times + dashboard density over 24–48h.
- **(NEW-3) Option 2 revisit — per-pattern-type diversity floors** — if /3 across the board proves too noisy for `opportunity_window` (natively hits 5+ sources on mega-topics), introduce `PER_PATTERN_DIVERSITY_FLOOR` dict mirroring `PER_PATTERN_MIN_CLUSTER_SIZE`.
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(E) Tier 2 lint promotion** — envelope-JSON top-level-key parse. Ledger #5 sub-substrate.
- **(H) generate_newsletter dry_run default flip (record-only S2944)** — schema says "DEFAULT: true" but handler defaults False. Would need per-caller regression review. Simple 1-line handler fix + wider blast-radius analysis.
- **(I) bulk_archive statuses autofill robustness (record-only S2944 — 2nd trigger observed at S2945 run_cleanup path, fixed there via helper)** — port the `if not statuses` coercion pattern from `_gather_cleanup_preview` to `_handle_bulk_archive` (per-handler touch, not shared-helper reachable). ~5-line handler fix + regression test.
- **Envelope enhancement (record-only S2942)** — `verify_hint` + `would_write_count` for dry_run envelopes. Needs 2nd-trigger corroboration.
- **Close-ceremony ledger-flip checklist (meta-fix, record-only S2942)** — first trigger from S2942 reconciliation; watch for 2nd trigger.
- **Deliverable v1 template retrofit (record-only S2943)** — protocol-variant docs can't opt into `Template version: v1` without triggering sweep-variant section lints.

---

## What's forbidden at S2947 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2946 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2946 additions to the deferred queue:**

- **Rank + cap + paginate follow-ups** (Rigby S2946 zoom-out fold, reactive) — 4 downstream consumer categories at 10× active-cluster count. See NEW-2 above.
- **Per-pattern-type diversity floors** (Option 2 alternate to shipped Option 1) — see NEW-3 above.

**All prior deferred entries carry forward from S2945** (S2946 didn't touch them):

- **Ledger candidate — `bulk_archive` statuses autofill robustness (2nd trigger corroborated at S2945)** — HIGH priority per S2945.
- **Ledger #38 batch 4 candidate (`content_tool.run_cleanup` dry_run addition):** ✅ **SHIPPED S2945.** No longer deferred.
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
- **Dedicated `agent_execution_query` PA tool** — S2931 Ledger #33 alternative path (superseded by allowlist expansion but still tracked).
- **Shared `skip_in_test` decorator** — S2931 Ledger #34 alternative (superseded by explicit guard but still tracked).
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A.
- **Bundled dev-env drift slate** — pre-existing pyright warnings on `pa_tool_schemas.py` + `build_pa_tool_audit.py` + `pa_tools_gap_map.py` + `session_lifecycle.py` + `twin_mirror_enforcement.py` + `td_handlers_agents.py` + `td_handlers_content.py` + `tasks_misc.py` + **`signal_aggregation_service.py` (S2946 confirmed pre-existing)** + **`test_s2946_diversity_denominator.py` (matches same pattern).**
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate + Ledger candidate: media_tool.delete IRREVERSIBLE** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged; S2946 hit twice and workaround-cleared via ORM as expected.
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
**Slice 6 — `td_handlers_content` (6 tools):** CLOSED at S2936 (6/6). ✅ **S2943 + S2944 + S2945 addenda:** content_tool per-action 100% via S2942-envelope alignment (all 4 mutations).
**Slice 7 — singleton bucket (9 tools across 8 handler files):** CLOSED at S2940 (9/9). ✅
**Ledger #16 twin-mirror enforcement substrate:** CLOSED at S2941 (PR #3517). ✅
**Ledger #38 dry_run MVP + Ledger #41 scoreboard promotion:** CLOSED at S2942. ✅
**Ledger #38 batch 2/3/4:** CLOSED at S2943/S2944/S2945.
**S2946 A6:** **NOT PA-tools-sweep scope.** Signal-substrate topology fix; adjacent domain.

**Total remaining sweep tools: 0.** All ratified sweep scope discharged.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2946: zero A4 spend** — pure engineering ship.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2946)

See:
- **S2946 handoff (current):** `docs/handoffs/SESSION_2946_A6_DIVERSITY_DENOMINATOR.md`
- **S2946 validation doc:** `docs/research/platform/S2946_A6_diversity_denominator.md`
- **S2946 shipped code:** `core/services/signal_aggregation_service.py:855` (1 LOC + rationale comment) + `core/tests/test_s2946_diversity_denominator.py` (7 tests)
- **S2945 handoff:** `docs/handoffs/SESSION_2945_LEDGER_38_BATCH_4.md`
- **S2944 handoff:** `docs/handoffs/SESSION_2944_LEDGER_38_BATCH_3.md`
- **S2943 handoff:** `docs/handoffs/SESSION_2943_SLICE_6_LEDGER_38_BATCH_2.md`
- **S2942 handoff:** `docs/handoffs/SESSION_2942_S2942_CLOSURE_PLAN.md`
- **S2941 handoff:** `docs/handoffs/SESSION_2941_LEDGER_16_TWIN_MIRROR.md`
- **S2940 handoff:** `docs/handoffs/SESSION_2940_SLICE_7_CLOSE.md`
- **Signal-substrate anchor files:**
  - `core/models_signal_intelligence.py` — `SignalCluster` model + `is_actionable` property (line 249) + status enum (line 203)
  - `core/services/signal_aggregation_service.py` — `_calculate_strength` (line 839) + `_calculate_confidence` (line 866) + `MIN_CLUSTER_SIZE=3` (line 44)
  - `core/tasks_misc.py:4547` — decay path (`detecting > 2 days → decayed`)
  - `core/services/signal_dispatch_service.py` — downstream consumer (S2933)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
