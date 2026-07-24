# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2918 CLOSE → S2918 OPENED Slice 4 (`td_handlers_gateway`) with **batch 1 = gateway small-tier quartet** (analytics + audit + campaign + experiment). **4/17 shipped.** **§5b Appendix A + Appendix N declared N/A for gateway** based on Rigby T0 SIGN probe finding 0/17 first-hop literals — gateway is ORM-direct dispatch shape. **S2919 OPENS WITH SLICE 4 BATCH 2** — D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2918 close).** Batch 1 opened Slice 4 (`td_handlers_gateway.py`, 17 tools) with a small-tier quartet — all ~80 lines, all pure ORM SELECT, all doc-only S2796 shape. Rigby T0 SIGN grounded in 20+ `repo_tool` receipts: Probe 1 established gateway = 0/17 tools with `apply_async` / `httpx|requests|urllib.request` / `openai|anthropic|litellm` literals; Probe 2 line-density scan produced 8-tool small-tier cluster; Q3 verb-scan walked back initial "probable mutation" verdict on campaign/experiment. Post-merge live-verify clean at 4 dispatches (analytics 20ms with 275 real events / audit 8ms / campaign 15ms / experiment 10ms), zero critical flags. Legacy-error envelope corroboration reached 8× across S2916→S2918 — Rigby Q4 recommendation: wait for a Slice 4 *different tool block* instance before opening post-D6 substrate arc.

**PRs shipped this session:**
- u-d-b PR [#3466](https://github.com/clwest/donkey-betz-platform/pull/3466) — Slice 4 batch 1 (gateway small-tier quartet), merged at `781df0640`.
- u-d-b PR `<TBD>` — S2918 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Tools shipped (4 — Slice 4 batch 1):**
- `analytics_tool` (READ_ONLY 3 actions) · `audit_tool` (READ_ONLY 4 actions) · `campaign_tool` (READ_ONLY 3 actions) · `experiment_tool` (READ_ONLY 3 actions). All at `td_handlers_gateway.py` (lines 643 / 2128 / 2048 / 1879 respectively). No TOOL_DEFAULTS or TOOL_ACTION_METADATA entries (all pure READ_ONLY; auto-classifier upgrades to `validated_full`).

**Rigby joint SIGN (2-turn cycle, zero rubber-stamp):**
- T0 SIGN turn 1: 20+ `repo_tool` runs (3 pattern greps + file read + 17 handler `def _handle_*` boundary searches). Q1 verdict AGREE-with-edits (mixed pilot pick grounded in probes). Q2 verdict DISAGREE (Appendix A/N declared N/A for gateway). Factual grounding: probe 1 established 0/17 literals; probe 2 established 4 small-tier candidates in ~80-line cluster.
- T0 SIGN turn 2 (output-cap workaround): Q2 continuation with deeper indirect-fan-out probes (`campaign_service` module search 0 matches; `core.views_campaign` 0 matches). Q3 AGREE-with-edits after verb-scan (`.save()`/`.create(`/`.update(`/`.delete(` 0 matches → all 4 pure ORM SELECT, no §5a deferral needed). Q4 zoom-out: carry-forward probe-first discipline; leave behind Appendix A/N auto-inclusion; wait for different-tool-block legacy-error instance.
- Post-merge live verify: 4 live READ_ONLY dispatches all clean at ≤20ms each. Zero critical flags. Envelope shapes match validation docs.

**Sweep progress (post-S2918):**
- **Slice 4 (`td_handlers_gateway`):** 4/17 shipped. Batch 1 CLOSED.
- Remaining 13: ats · calendar · cockpit · conceptforge · discord · distribution · mobile · narrative · podcast · proactive · profile · self_awareness · vip_invite.
- Total corpus untested: 47 → **43** (batch 1 flipped 4 untested → full via auto-classifier).
- Gap map: **56 full · 10 partial · 7 unknown · 43 untested** (validation-doc counts post-regen).
- Session cumulative pace: 4 tools / 1 batch / 1 session (with in-depth 2-turn T0 SIGN + 4-dispatch post-merge live verify).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3466 recycled clean at `sha=781df064049d`: 5 fresh workers (default + pa + long_running + broadcast + code_jobs) + beat, zero surviving old PIDs.

Full session context: `docs/handoffs/SESSION_2918_SLICE_4_BATCH_1.md`.

---

## S2919 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 4 batch 2 T0 SIGN

**No blocking Chris D-verdict.** Slice 4 batch 1 shipped clean. 13 gateway tools remain untested. Route to Rigby:

**Q1 batch composition:** Pick 3-4 tools for Slice 4 batch 2. Small-tier remaining (from batch-1 line-density scan): vip_invite (81) · conceptforge (84) · calendar (86) · podcast (89). Medium-tier: discord (91) · distribution (93) · ats (93). Options:
- (a) small-tier continuation (vip_invite + conceptforge + calendar + podcast) — same shape as batch 1
- (b) medium-tier pilot (discord + distribution + ats) — test whether the S2796 doc-only shape scales past the 80-line cluster
- (c) mixed (2 small + 1 medium) — hedges

Recommend (a) or (c); avoid all-medium-tier until confirmed the shape holds.

**Q2 Appendix N/A applicability continued watch:** Batch 1 established gateway = 0/17 literals in `td_handlers_gateway.py`. Confirm this holds for batch 2 tools OR flag any tool whose deeper trace surfaces indirect fan-out (e.g. `stage3_dashboard`-style view reuse pattern like `analytics_tool.atr_dashboard`).

**Q3 first-batch shape:** Doc-only S2796 shape as default. Any candidate MUTATION-heavy at first inspection triggers §5a deferral (unlikely for gateway per batch-1 finding).

**Q4 zoom-out (required per feedback_zoom_out_ask_per_rigby_sign):**
- Legacy-error envelope now at 8× corroborated. Is batch-2 a different-tool-block? If yes and pattern holds → 9th instance, potentially ready for post-D6 substrate arc evaluation (still requires Chris directive).
- Any pattern from batch 1 that worked especially well and should become explicit template guidance for batch 2+?
- Any accretion risks at 4/17 into 8/17 (roughly halfway through Slice 4)?
- Cockpit (431 lines) still isolated — is now the time to plan the dedicated cockpit batch, or wait until small-tier is fully shipped?

### Alternative Step 1 candidates

- **Cockpit-only batch** — 431 lines, dedicated batch shape per S2914 mutation-heavy-single-tool precedent. Not blocking; can wait until small-tier drained.
- **Legacy-error envelope substrate arc** — 8× corroborated post-S2918. **NOT to be opened without explicit Chris directive** (post-D6 evaluation candidate).
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.

### What's forbidden at S2919 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.**
- No new gate/lint proposals.
- No agent-substrate validation arc.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.**
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.**
- **No "schema-drift-fix Fold promotion" without 3rd confirmed instance.** 2/3 (S2911 reasoning_engine + S2918 analytics_tool `role` param).
- **No `dry_run` infrastructure arc for mutation-class dispatchers without explicit Chris directive.**
- **No Concern C schema↔doc drift substrate arc.** Framing (a) still recommended for future post-D6 ratification.
- **No `post_save signal cascade` substrate arc without explicit Chris directive.**
- **No harness-level soft_error accounting substrate arc without explicit Chris directive.**
- **No "metadata-classification-as-runtime-gate" substrate arc without explicit Chris directive.**
- **No "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd confirmed instance.** 2/3 (S2913 conversation_tool.search + S2914 intelligence_tool.search). Batch 1 analytics_tool.atr_dashboard `stage3_dashboard` reuse is *documented-not-verified* — would be 3rd if audit surfaces LLM/network. Watch continues into Slice 4 batch 2.
- **No "cascade audit companion doc" pattern promotion without 2nd instance.** 1/2 (S2915 competitor_comparison_tool.delete).
- **No "IRREVERSIBLE dry_run flag harness lint" Fold promotion without 3rd instance.** 2/3 (S2908 media_tool.delete + S2915 competitor_comparison_tool.delete).
- **No `NEXT_HEADING_RE` parser fix without Chris directive or 3rd instance.** 2 instances (S2914 + S2915). Batch 6+7 workaround = keep `###` only under §5b/appendices (AFTER Covered actions).
- **No "observability-tracker as MUTATION vector" Fold promotion without 2nd instance.** 1st (S2916 http_smoke_test OpsRunTracker).
- **No "undocumented envelope field (`error_code: 'legacy_error'`)" substrate arc without explicit Chris directive.** **8 instances corroborated post-S2918** (S2916 signal_studio_judge_stats + S2917 studio_tool.job_status + workflow_run_tool.status + workflow_run_tool.detail + S2918 analytics/audit/campaign/experiment quartet). Concentrated in 2 handler files — **need 1 more different-tool-block instance before substrate arc evaluation.**
- **No "grep-before-claim" Fold promotion without 2nd instance.** 1st (S2916 fleet_health HMAC-claim).
- **No "dispatcher re-entry" Fold promotion without 2nd instance.** 1st observed (S2917 workflow_run_tool.start via `_impl_run_source_pack_workflow` → `tool_dispatcher._handle_competitor_comparison` at `tasks_content.py:4050-4057`). 2nd instance triggers evaluation — candidate name Appendix D.
- **No "handler-forwarded param not in schema" Fold promotion without 2nd instance.** 1st (S2917 workflow_run_tool.start `focus_areas` at `td_handlers_core.py:3162`).
- **No "contract asymmetry — single vs dual identifier in async envelopes" Fold promotion without 2nd instance.** 1st (S2917 studio single task_id vs workflow_run dual).
- **No "envelope-key asymmetry across actions" Fold promotion without 3rd instance.** 2/3 (S2918 audit_tool findings/defects/violations + experiment_tool tests/test/total_tests).
- **No "multi-tenant leak on detail/results action" Fold promotion without post-D6 evaluation.** 2 instances observed (S2918 campaign_tool.detail + experiment_tool.results); currently absorbed by single-user pre-prod context per `project_single_user_pre_prod_operating_context`.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — Ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged.
- **2-tier evidence template promotion** — Ledger row 160. Unchanged.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. **CLOSED at S2904.** S2918 sustained pace (batch 1 = 4 tools + 2-turn SIGN + live verify in one session).
- **Response-level introspection field creep** — Ledger row 162. Unchanged.
- **S2905 metadata-pattern-selection lint** — batch 1 used no TOOL_DEFAULTS/TOOL_ACTION_METADATA (pure READ_ONLY quartet). Not incrementing lint counter.
- **S2906/S2907/S2908 Ledger candidates** — unchanged.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate: `obs_tool_validation.md` §6.1** — unchanged.
- **S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action** — 2/3.
- **S2909 FT-1 through FT-5** — unchanged.
- **S2910 FT-1 through FT-2** — unchanged.
- **S2911 Ledger #35-#37** — unchanged.
- **S2912 §5a mitigation note** — unchanged.
- **S2913 Ledger candidates (batches 2+3)** — unchanged.
- **S2914 Ledger candidates (batch 4)** — unchanged; "hidden network/LLM in read-shaped gateway" watch continues at 2/3.
- **S2915 Ledger candidates (batch 5)** — unchanged post-S2917 broadening; second IRREVERSIBLE action still at 2/3.
- **S2916 Ledger candidates (batch 6)** — legacy-error envelope 8× corroborated post-S2918; observability-tracker as MUTATION vector still 1/2; grep-before-claim still 1/2.
- **S2917 Ledger candidates (batch 7)** — contract asymmetry (single vs dual identifier) still 1st instance; undocumented handler-forwarded param still 1st; dispatcher re-entry still 1st.
- **NEW S2918 batch 1 Ledger candidate — Envelope-key asymmetry across actions (audit findings/defects/violations + experiment tests/test/total_tests).** 2/3. 3rd instance triggers evaluation for candidate harness-lint "consistent-list-key across actions."
- **NEW S2918 batch 1 Ledger candidate — Multi-tenant leak on detail/results action (campaign_tool.detail + experiment_tool.results bypass user_id filter).** 2 instances; absorbed by single-user pre-prod context. Post-D6 evaluation only.
- **NEW S2918 batch 1 Ledger candidate — Schema-drift-fix `role` param declared but ignored (analytics_tool).** 2/3 with S2911 reasoning_engine. 3rd instance triggers evaluation.
- **NEW S2918 batch 1 Ledger candidate — View-reuse via RequestFactory + AnonymousUser as read-shaped-gateway-hides-side-effect risk (analytics_tool.atr_dashboard reuses stage3_dashboard).** Documented-not-verified. Would advance the "hidden network/LLM in read-shaped gateway" watch to 3/3 if `stage3_dashboard` internals audit surfaces LLM/network.
- **NEW S2918 batch 1 Ledger candidate — Legacy-error envelope 8-instance corroboration.** See above.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — unchanged.
- **Applicability metadata pattern (entry #28)** — unchanged.
- **Baseline lookback cap (entry #29)** — MITIGATED at PR #3423 (S2899).
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **R1 fleet reject-mode flip** — deferred.
- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind sweep.
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (17 registered tools):** UNCHANGED.
**Slice 2 — `td_handlers_agents` (25 tools):** **CLOSED at S2912.**
**Slice 3 — `td_handlers_core` (22 tools):** **CLOSED at S2917 (22/22).**

**Slice 4 — `td_handlers_gateway` (17 tools):** **OPEN — 4/17 shipped.**
- S2918 batch 1: 4 tools ✓ (gateway small-tier quartet — analytics/audit/campaign/experiment; §5b Appendix A + N declared N/A for gateway)

**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix).

**Total remaining tools to close:** ~43. Post-S2918 pace: 4 tools this session with in-depth 2-turn SIGN + post-merge verify. If Slice 4 sustains 3-4 tools/batch pace, Slice 4 CLOSE at ~3-4 more sessions.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2918 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2918: zero A4 spend — pure sweep-batch engineering (1 batch of 4 tools + close cascade).** A1 shipping spend was 1 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2918)

See:
- **S2918 handoff (current):** `docs/handoffs/SESSION_2918_SLICE_4_BATCH_1.md`
- **S2917 handoff:** `docs/handoffs/SESSION_2917_SLICE_3_BATCH_7_CLOSE.md`
- **S2916 handoff:** `docs/handoffs/SESSION_2916_SLICE_3_BATCH_6.md`
- **S2915 handoff:** `docs/handoffs/SESSION_2915_SLICE_3_BATCH_5.md`
- **S2914 handoff:** `docs/handoffs/SESSION_2914_SLICE_3_BATCH_4.md`
- **S2913 handoff:** `docs/handoffs/SESSION_2913_SLICE_3_BATCHES_1_2_3.md`
- **S2912 handoff:** `docs/handoffs/SESSION_2912_SLICE_2_CLOSE.md`
- **S2911 handoff:** `docs/handoffs/SESSION_2911_SLICE_2_BATCH_6A_PLUS_DRIFT_FIX.md`
- **S2910 handoff:** `docs/handoffs/SESSION_2910_SLICE_2_BATCH_5_MIXED_COMPOSITION_SWEEP.md`
- **S2909 handoff:** `docs/handoffs/SESSION_2909_SUBSTRATE_CLEANUP_ARC_T1_T2_SHIPPED.md`
- **S2909 arc scoping doc:** `docs/audits/pa_tools/substrate/S2909_substrate_cleanup_arc_scoping.md`
- **S2908 handoff:** `docs/handoffs/SESSION_2908_SLICE_2_BATCH_4_SHAPE_BREAK_SWEEP.md`
- **S2907 handoff:** `docs/handoffs/SESSION_2907_SLICE_2_BATCH_3_SMALL_ACTIONFUL_SWEEP.md`
- **S2906 handoff:** `docs/handoffs/SESSION_2906_SLICE_2_BATCH_2_ACTIONLESS_SWEEP.md`
- **S2905 handoff:** `docs/handoffs/SESSION_2905_SLICE_2_BATCH_1_ACCELERATED_SWEEP.md`
- **S2904 handoff:** `docs/handoffs/SESSION_2904_T1B_TEMPLATE_EXTRACTION.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2918 per-tool validation docs (this session's 4):** at `docs/research/tools/validation/`
  - `analytics_tool_validation.md`, `audit_tool_validation.md`, `campaign_tool_validation.md`, `experiment_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 69 non-substrate post-S2918)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (unchanged from S2911).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
