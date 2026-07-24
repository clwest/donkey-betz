# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2920 CLOSE → S2920 SHIPPED Slice 4 batch 3 (mobile + calendar + conceptforge) via template-preservation swap after Q1 mutation-scan disqualified proactive + self_awareness, then Q2 swap-in scan disqualified profile. **11/17 shipped.** **S2921 OPENS WITH SLICE 4 BATCH 4 (mutation-shape decision)** — D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2920 close).** Batch 3 shipped 3 pure-read gateway tools (mobile 126 · calendar 84 · conceptforge 82 lines) via S2796 doc-only shape. Rigby T0 SIGN 2-turn cycle grounded in 10+ `repo_tool` receipts — zero rubber-stamp. Turn 1 DISAGREE on original quartet (proactive `.update`×3 + self_awareness `.create`×1 flagged mutation-capable); Turn 2 swap attempt partially blocked (profile `.save` + `get_or_create()`); escalated to split-batch → ship 3 clean read-only + defer 3 mutation-capable to S2921 mutation-shape SIGN cycle. Post-merge live verify: 3/3 clean at ≤11ms (mobile 4ms / calendar 10ms / conceptforge 11ms). No dev-env drift.

**PRs shipped this session:**
- u-d-b PR [#3470](https://github.com/clwest/donkey-betz-platform/pull/3470) — Slice 4 batch 3 (gateway medium-tier read-only trio), merged at `fd4c9d5b0`.
- u-d-b PR `<TBD>` — S2920 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Tools shipped (3 — Slice 4 batch 3):**
- `mobile_tool` (4 actions: project_status/screens/api_modules/dependencies — filesystem read + JSON/regex parse; 2nd Slice-4 instance of filesystem-read shape after discord_tool) · `calendar_tool` (4 actions: channels/episodes/upcoming/stats — pure ORM SELECT+Count) · `conceptforge_tool` (3 actions: runs/run_detail/stats — pure ORM SELECT+Avg/Count+FK JOIN). All at `td_handlers_gateway.py` (lines 814 / 1793 / 2210 respectively). No TOOL_DEFAULTS or TOOL_ACTION_METADATA entries (all pure READ_ONLY; auto-classifier upgrades to `validated_full`).

**Rigby joint SIGN (2-turn cycle + Q4 zoom-out, zero rubber-stamp):**
- T0 SIGN turn 1: 8 `repo_tool` runs (4 handler-anchor searches + 4 boundary reads on original quartet). Q1 DISAGREE — 2/4 mutation-capable (proactive .update×3 + self_awareness .create×1). Q3 DO NOT AGREE to doc-only shape for full batch.
- T0 SIGN turn 2: 2 more `repo_tool` runs (handler-anchor searches for swap-ins profile + conceptforge). Verb-scan flagged profile mutation-capable (`enhanced.save()` at line 2415 + `get_or_create()`). Escalated to split-batch: ship read-only trio (mobile + calendar + conceptforge), defer mutation-capable trio (proactive + self_awareness + profile) to S2921. Q1 revised AGREE-with-edits, Q2 AGREE per-tool (0/3 first-hop literals), Q3 AGREE doc-only shape holds for the 3 clean tools.
- Q4 zoom-out: (a) legacy-error semantic-nuance framing may need refresh; (b) codify mutation-scan-swap pattern (2 triggers now — S2919 + S2920); (c) template-drift risk if we don't formally split read-only vs mutation-capable templates; (d) cockpit dedicated batch still deferred until mutation-shape settled.
- Post-merge live verify: 3/3 clean at ≤11ms with full envelope shapes (mobile expo_version + eas_profiles populated; calendar + conceptforge stats zero as expected in empty dev env).

**Sweep progress (post-S2920):**
- **Slice 4 (`td_handlers_gateway`):** 11/17 shipped. Batch 3 CLOSED.
- Remaining 6: cockpit (431) · podcast (251) · profile (188 — mutation) · proactive (140 — mutation) · self_awareness (118 — mutation) · vip_invite (81 — mutation ×3).
- Total corpus untested: 39 → **36** (batch 3 flipped 3 untested → full via auto-classifier).
- Gap map: **63 full · 10 partial · 7 unknown · 36 untested** (validation-doc counts post-regen).
- Session cumulative pace: 3 tools / 1 batch / 1 session (with 2-turn SIGN + mutation-scan + swap attempt + escalation + post-merge verify).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3470 recycled clean at `sha=fd4c9d5b0ce8`: 5 fresh workers (default + pa + long_running + broadcast + code_jobs) + beat, zero surviving old PIDs.

Full session context: `docs/handoffs/SESSION_2920_SLICE_4_BATCH_3.md`.

---

## S2921 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 4 batch 4 — MUTATION-SHAPE DECISION SIGN cycle

**BLOCKING Chris D-verdict from S2920 close:** codification of mutation-scan-swap pattern (Playbook amendment OR sweep-doc update). 2 triggers now (S2919 + S2920). Rigby + Claude joint recommendation. Yes/no + framing (Playbook v0.10.0 minor amendment vs sweep-doc note).

**Batch 4 options — mutation-capable Slice 4 tools:**

4 mutation-capable tools known: vip_invite (81, .create + .save×2 — 3 verbs from S2919 scan) · proactive (140, .update×3) · self_awareness (118, .create×1) · profile (188, .save×1 + get_or_create).

Options:
- **(a) Mutation-shape template design first, ship-cycle second:** design the mutation-capable-tool doc template at S2921 (§5a fill-out expected, blast-radius classification, per-action deferral rationale, Slice-when-covered pointer). Ship 0 tools at S2921; batch 4 ships at S2922 using the new template. Cleanest; unblocks vip_invite too.
- **(b) Single-tool pilot with in-flight template design:** ship 1 mutation-capable tool at S2921 as the template pilot (recommend self_awareness — smallest at 118 lines + only 1 mutation verb). Template extracts from the ship shape. Faster to first mutation-shipped tool but conflates design + shipment.
- **(c) Full mutation quartet with pre-existing §5a template:** ship all 4 mutation-capable tools at S2921 using the existing §5a "Mutation containment" template as-is (S2914 mutation-heavy-single-tool precedent). Risky — template hasn't been exercised for cluster-of-4.

Recommend **(a)** — cleanest split; matches Rigby Q4(c) recommendation to "formally split read-only doc-only vs mutation-capable tool handling."

**Q1 (batch 4 composition):** Pick option (a) / (b) / (c). If (b), pick pilot tool.

**Q2 (Appendix N/A applicability):** Continue gateway-wide 0/17 first-hop literal watch. Per-tool grep for mutation batch candidates.

**Q3 (batch 4 shape):** Mutation-capable template shape TBD. §5a "Mutation containment" section from template needs concrete blast-radius classification schema. Options: `contained` (row-level, single-user) / `spreading` (row-level, multi-user reachable) / `cascading` (FK cascade or signal chain) / `external` (network or Celery fan-out).

**Q4 zoom-out (required per feedback_zoom_out_ask_per_rigby_sign):**
- 3rd consecutive session with pace acceleration + probe-first correction — sustainable? What risk is accreting?
- Codification vote: if Chris ratifies mutation-scan-swap codification, Playbook v0.10.0 or sweep-doc update? Which locks the pattern in more usefully?
- 00-START source-of-truth regen: 2 consecutive sessions with calendar-span burn suggests stale-copy. Regen from `repo_tool` receipts at close?
- Legacy-error envelope semantic-nuance refresh: Rigby Q4(a) flag from S2920 — refresh framing now (still Chris-gated) or wait until post-D6 evaluation?

### Alternative Step 1 candidates

- **Cockpit-only batch** — 431 lines, dedicated batch shape. Still deferred until mutation-shape settled per S2920 Q4(d).
- **narrative_tool dev-env drift fix** — Rigby Tool Gap Ledger entry `5c84e75a` from S2919; requires ~30 min migration replay + verification. Engineering task, not sweep.
- **Legacy-error envelope substrate arc** — 15× corroborated post-S2920. **NOT to be opened without explicit Chris directive** (post-D6 evaluation candidate); framing may need refresh per Rigby S2920 Q4(a).
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.

### What's forbidden at S2921 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.**
- No new gate/lint proposals.
- No agent-substrate validation arc.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.**
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.**
- **No "schema-drift-fix Fold promotion" without explicit Chris directive.** **3/3 TRIGGERED at S2919 batch 2 + 4th confirming.** No new instance this batch. Triggers evaluation — still requires Chris D-verdict.
- **No `dry_run` infrastructure arc for mutation-class dispatchers without explicit Chris directive.**
- **No Concern C schema↔doc drift substrate arc.** Framing (a) still recommended for future post-D6 ratification.
- **No `post_save signal cascade` substrate arc without explicit Chris directive.**
- **No harness-level soft_error accounting substrate arc without explicit Chris directive.**
- **No "metadata-classification-as-runtime-gate" substrate arc without explicit Chris directive.**
- **No "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd confirmed instance.** 2/3 (S2913 conversation_tool.search + S2914 intelligence_tool.search). Batch 1 analytics_tool.atr_dashboard `stage3_dashboard` reuse is *documented-not-verified* — would be 3rd if audit surfaces LLM/network. Watch continues into Slice 4 batch 4+.
- **No "cascade audit companion doc" pattern promotion without 2nd instance.** 1/2 (S2915 competitor_comparison_tool.delete).
- **No "IRREVERSIBLE dry_run flag harness lint" Fold promotion without 3rd instance.** 2/3 (S2908 media_tool.delete + S2915 competitor_comparison_tool.delete).
- **No `NEXT_HEADING_RE` parser fix without Chris directive or 3rd instance.** 2 instances (S2914 + S2915). Batch 6+7 workaround = keep `###` only under §5b/appendices (AFTER Covered actions).
- **No "observability-tracker as MUTATION vector" Fold promotion without 2nd instance.** 1st (S2916 http_smoke_test OpsRunTracker).
- **No "undocumented envelope field (`error_code: 'legacy_error'`)" substrate arc without explicit Chris directive.** **15 instances corroborated post-S2920** (12 at S2919 + batch-3's mobile/calendar/conceptforge). Semantic nuance from S2919 live-verify still applies: observed `error_code='legacy_error'` is a VALUE on a post-S2909 envelope field, not the ABSENCE of the field. Framing may need refresh — Rigby S2920 Q4(a) flagged sweep guidance should treat `error_code` values as first-class semantics. Different substrate arc scope than originally framed. Still gated on explicit Chris directive.
- **No "grep-before-claim" Fold promotion without 2nd instance.** 1st (S2916 fleet_health HMAC-claim).
- **No "dispatcher re-entry" Fold promotion without 2nd instance.** 1st observed (S2917 workflow_run_tool.start).
- **No "handler-forwarded param not in schema" Fold promotion without 2nd instance.** 1st (S2917 workflow_run_tool.start `focus_areas`).
- **No "contract asymmetry — single vs dual identifier in async envelopes" Fold promotion without 2nd instance.** 1st (S2917 studio single task_id vs workflow_run dual).
- **No "envelope-key asymmetry across actions" Fold promotion without explicit Chris directive.** 3/3 TRIGGERED at S2919 batch 2. No new distinct sub-pattern this batch. Still Chris-gated.
- **No "multi-tenant leak on detail/results action" Fold promotion without post-D6 evaluation.** **3 instances now** (S2918 campaign_tool.detail + experiment_tool.results + S2920 calendar_tool.upcoming); absorbed by single-user pre-prod context per `project_single_user_pre_prod_operating_context`.
- **No "template-preservation swap" Fold promotion without explicit Chris directive.** **2 batch-level triggers now** (S2919 vip_invite→narrative + S2920 proactive+self_awareness+profile→conceptforge). Rigby + Claude joint recommend codification at S2921. **BLOCKING Chris D-verdict at S2921 open.**
- **No "mixed user-scoping within single response" Fold promotion without 2nd instance.** 1st (S2920 calendar_tool.stats: `total_channels` user-scoped, `total_episodes` un-scoped). 2nd instance triggers evaluation.
- **No "filesystem-read handler shape (open + regex)" Fold promotion without 3rd instance.** 2/3 (S2919 discord_tool + S2920 mobile_tool). 3rd instance triggers evaluation.
- **No "limit does not gate nested lists" Fold promotion without 2nd instance.** 1st (S2920 conceptforge_tool.run_detail: `limit` applies to top-level `runs` only, not `stages`/`artifacts`). 2nd instance triggers evaluation.
- **No "00-START span-math source-of-truth regen" Fold promotion without explicit Chris directive.** **2 consecutive sessions** with calendar-span burn (S2919 + S2920). Suggests 00-START source is stale-copied. Not yet a Fold — process hygiene issue. Recommend regen at close.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — Ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged.
- **2-tier evidence template promotion** — Ledger row 160. Unchanged.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. CLOSED at S2904.
- **Response-level introspection field creep** — Ledger row 162. Unchanged.
- **S2905 metadata-pattern-selection lint** — batch 3 used no TOOL_DEFAULTS/TOOL_ACTION_METADATA (pure READ_ONLY trio). Not incrementing lint counter.
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
- **S2915 Ledger candidates (batch 5)** — unchanged; second IRREVERSIBLE action still at 2/3.
- **S2916 Ledger candidates (batch 6)** — legacy-error envelope 15× corroborated post-S2920; observability-tracker as MUTATION vector still 1/2; grep-before-claim still 1/2.
- **S2917 Ledger candidates (batch 7)** — contract asymmetry, undocumented handler-forwarded param, dispatcher re-entry — all still 1st instance.
- **S2918 batch 1 Ledger candidates** — envelope-key asymmetry 3/3 triggered at S2919; multi-tenant leak 3rd at S2920 (still single-user pre-prod absorbed); schema-drift-fix 3/3+4th; view-reuse `stage3_dashboard` still documented-not-verified.
- **S2919 batch 2 Ledger candidates** — divergent `limit` hard-cap (1st); N+1 query pattern (1st); envelope-shape intra-tool asymmetry (1st); `variations` truncation-to-3 (1st); `platform_account` stringified-UUID-not-name (1st) — all still 1st instances.
- **NEW S2920 batch 3 Ledger candidates:**
  - **Multi-tenant leak on `calendar_tool.upcoming`** — 3rd gateway instance overall; still absorbed by single-user pre-prod.
  - **Mixed user-scoping within single response (`calendar_tool.stats`)** — 1st instance. 2nd triggers evaluation.
  - **Filesystem-read handler shape (open + regex) — 2nd Slice-4 instance** (discord + mobile). 3rd triggers evaluation.
  - **`limit` does not gate nested lists (`conceptforge_tool.run_detail`)** — 1st instance. 2nd triggers evaluation.
  - **500-byte placeholder heuristic (mobile_tool.screens)** — usability sharp edge; not defect-worthy.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — unchanged.
- **Applicability metadata pattern (entry #28)** — unchanged.
- **Baseline lookback cap (entry #29)** — MITIGATED at PR #3423 (S2899).
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **S2919 narrative_tool dev-env drift (Rigby Tool Gap Ledger)** — unchanged; MEDIUM priority; ~30 min migration replay + verification.
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

**Slice 4 — `td_handlers_gateway` (17 tools):** **OPEN — 11/17 shipped.**
- S2918 batch 1: 4 tools ✓ (gateway small-tier quartet — analytics/audit/campaign/experiment)
- S2919 batch 2: 4 tools ✓ (gateway small-tier read-only quartet — discord/distribution/ats/narrative; template-preservation swap #1)
- S2920 batch 3: 3 tools ✓ (gateway medium-tier read-only trio — mobile/calendar/conceptforge; template-preservation swap #2 with split-batch escalation)

**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix).

**Total remaining tools to close:** ~36. Post-S2920 pace: 3 tools this session with 2-turn SIGN + probe-first correction + mutation-scan swap attempts + escalation to split-batch + post-merge verify + no dev-env drift. Slice 4 CLOSE at ~2-3 more sessions if mutation-shape template gets designed cleanly at S2921 batch 4 (6 remaining, 4 of which are mutation-capable).

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2920 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2920: zero A4 spend — pure sweep-batch engineering (1 batch of 3 tools + 2-turn SIGN + close cascade).** A1 shipping spend was 1 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2920)

See:
- **S2920 handoff (current):** `docs/handoffs/SESSION_2920_SLICE_4_BATCH_3.md`
- **S2919 handoff:** `docs/handoffs/SESSION_2919_SLICE_4_BATCH_2.md`
- **S2918 handoff:** `docs/handoffs/SESSION_2918_SLICE_4_BATCH_1.md`
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
- **S2920 per-tool validation docs (this session's 3):** at `docs/research/tools/validation/`
  - `mobile_tool_validation.md`, `calendar_tool_validation.md`, `conceptforge_tool_validation.md`
- **S2919 per-tool validation docs:** at `docs/research/tools/validation/`
  - `discord_tool_validation.md`, `distribution_tool_validation.md`, `ats_tool_validation.md`, `narrative_tool_validation.md`
- **S2918 per-tool validation docs:** at `docs/research/tools/validation/`
  - `analytics_tool_validation.md`, `audit_tool_validation.md`, `campaign_tool_validation.md`, `experiment_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 80 non-substrate post-S2920)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (S2919 narrative_tool dev-env drift entry still pending triage).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
