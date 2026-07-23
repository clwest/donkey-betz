# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2907 CLOSE → Small-actionful all-READ_ONLY batch ✓ shipped. Third post-substrate batch. **S2908 OPENS WITH REQUIRED SHAPE-BREAK — uniform READ_ONLY pattern must NOT repeat** (Rigby T0+T1 zoom-out E → Chris ratified) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-23 (S2907 close).** Third accelerated PA-tools sweep batch after Row 161 substrate arc close. PR [#3439](https://github.com/clwest/donkey-betz-platform/pull/3439) merged at `706e7d60a`. Three small-actionful all-READ_ONLY tools validated: `ml_analysis` (3 actions), `voice_clone_tool` (5 actions), `orm_inspect_tool` (5 actions). Zero same-PR handler fix required this batch (contrast S2906 which needed the `_handle_system_alerts` fix). Doc-only per S2796.

**Small-actionful stress-test claim validated (S2906 T0 SIGN Fold A commitment closed):**
- T1a auto-harness produced real evidence for all 3 tools with real action enumeration (13 total actions covered).
- 3 new pass verdicts in gap map (8 → 11 template compliance).
- `validated_full: 20 → 23 (+3)`, `untested: 86 → 83 (-3)`, `td_handlers_agents` untested slice `17 → 14 (-3)`.
- Rigby joint SIGN (T0 + T1): 15+ verification `tool_runs` between them; sharp T0 zoom-out E caught uniform-pattern-precedent-setting risk, folded to S2908 shape-break commitment. T1 zoom-out E identified drift-rate coupling risk (batch selection + minimal-safe-args harness profile could inflate the 87.5% drift narrative).
- Uniform-`TOOL_DEFAULTS`-only batch — zero per-action `TOOL_ACTION_METADATA` records added; mixed-pattern coexistence count stays 1/3 sweep sessions (distance to lint trigger: 2 more mixed sessions).

**Post-merge live-dispatch verified (per PLAYBOOK-7.4.4):**
- `orm_inspect_tool action=list_models` → clean allowlist. ✓
- `voice_clone_tool action=stats` → clean aggregate. ✓
- `ml_analysis action=status` → clean MLEngine health (8.5s latency on first post-recycle dispatch — DistilBERT load; caches thereafter). ✓

All 3 tools TOOL_DEFAULTS seed is live in worker.

**Rigby joint SIGN (S2907):** T0 SIGN AGREE-with-edits (batch composition + orm_inspect benchmark framing softened + Fold A zoom-out E precedent-setting risk folded to S2908 shape-break commitment). T1 SIGN AGREE-with-2-edits (voice_clone anonymous-user language + orm_inspect harness classification wording; both folded same-batch). Zero rubber-stamp SIGN across both rounds.

**PRs shipped this session:**
- u-d-b PR [#3439](https://github.com/clwest/donkey-betz-platform/pull/3439) — S2907 Slice 2 batch 3, merged at `706e7d60a`
- u-d-b PR `<TBD>` — S2907 close cascade (handoff + 00-START refresh + wrapper pin bump)

**Zoom-out folds captured (per PLAYBOOK-6.10.7):**
- **Fold A (T0 zoom-out E, `future_trigger` + Chris-ratified same-day):** Uniform READ_ONLY pattern accreting; three coupling risks named (Template v1 overfitting, drift-rate selection bias, hard governance muscle unexercised). **S2908 batch 4 MUST break uniform pattern.** Preferred shape (Rigby T1 ranking): mixed-tool scoped to READ_ONLY subset, documented in `## Covered actions`. Alternate: gated-write dry_run-only. Memory: `project_s2908_batch_4_shape_break_commitment.md`.
- **Fold B (T1 zoom-out E, `future_trigger`):** Drift-rate narrative (87.5% across S2906+S2907) could couple to batch selection + minimal-safe-args harness profile. Do NOT let S2908 batch pick optimize the story; keep shape-break as-ratified and let drift-rate land honestly.

Full session context: `docs/handoffs/SESSION_2907_SLICE_2_BATCH_3_SMALL_ACTIONFUL_SWEEP.md`.

---

## S2908 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 2 batch 4 (SHAPE-BREAK REQUIRED)

**S2908 REQUIRED open: Slice 2 batch 4 SHAPE-BREAK.** Do NOT open with another uniform-READ_ONLY multi-action batch. Chris directive (2026-07-23) folded per Fold A: *"if this is our Batch 3 let's go with 1 and knock it out but in our next session we need to change the shape."*

**Two acceptable shapes (per Rigby T0+T1 zoom-out E, ratified by Chris):**

**Shape A (Rigby-preferred, T1 zoom-out ranking):** Mixed-tool scoped to READ_ONLY subset only. Pick one tool with both READ_ONLY and WRITE actions from the S2907 rejected-mixed list; cover ONLY the READ_ONLY actions in the validation doc; document the scoping explicitly in `## Covered actions` (e.g., "Actions covered: X, Y, Z. Mutation actions W, V explicitly out of scope this ship — see §5a Mutation containment for deferral rationale + planned coverage slice"). Tests Template v1's mixed-pattern representation without taking write risk.

Concrete candidates from S2907 rejected-mixed inventory:
- `bpaas_tool` — cover `get_schema` + `get_example` only (skip `create_project` + `generate_close_pack` mutations).
- `davinci_tool` — cover `health` + `status` + `result` + `jobs` + `grades` only (skip `render` mutation).
- `obs_tool` — cover `health` + `status` + `last` only (skip `start` + `stop` + `upload_last` mutations).
- `media_tool` — cover `list` + `detail` + `stats` only (skip `delete` mutation).

**Shape B (Rigby-second-choice, Chris-ratified alternate):** Gated-write tool covering only the dry_run branch. Pick one tool with dry_run/confirm pattern; cover only the dry_run action. Tests schema/handler gating + metadata correctness without mutations. Candidates: `autopilot_tool` (Slice 1.5b if paired with mutation staged-enforcement), `security_containment_plan` (S1228 PR-A gate — dry_run branch alone).

**Concrete work:**
- Inspect 3-5 candidate tools from Shape A list (or 1-2 gated-write for Shape B). Confirm safety-class split via handler-trace evidence + downstream service inspection.
- Author T1b template v1 docs. `## Covered actions` MUST include explicit scoping note naming excluded mutation actions and deferral rationale.
- Watch drift-find rate on the MIXED-scoped batch specifically — this is data point #3 for S2906 Fold B trend candidate. Fold B says: "keep shape-break as-ratified so we test the real hypothesis (uniform-shape overfitting hides mixed-surface realities), not the meta-narrative." Do NOT let candidate pick optimize the drift-rate story.
- If drift-rate stays ≥50% across the mixed-scoped batch, that's data point #3 → hits 3-batch escalation floor → evaluate Playbook-amendment / cleanup-arc promotion.
- If drift-rate drops below 50%, that CONFIRMS Rigby's Fold B "batch-selection bias" hypothesis (mixed-surface batches surface less drift than uniform-safe-args batches).

**Session cap:** target 1 session for batch of 3-5.

### Alternative Step 1 candidates (unchanged from S2906/S2907 close)

- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid if Chris wants clean parity gate before more sweep sessions.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note (§ below, unchanged).

**Recommend Shape A mixed-tool-scoped-to-READ_ONLY-subset** — closes both Chris-ratified S2908 shape-break commitment AND advances Rigby's preferred zoom-out ranking. Phase 0 + Slice 1.5b can bundle into S2909+.

### What's forbidden at S2908 (D6 MORATORIUM still in force)

- **NO another uniform-READ_ONLY multi-action batch** (Fold A commitment — this is the load-bearing S2908 constraint).
- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- No v1 → v2 harness schema bump without substrate-arc-scoped SIGN. FT-2 (`soft_error` outcome) would need this; do NOT act on it without the SIGN cycle.
- No v1 → v2 template variant bump without substrate-arc-scoped SIGN. If a third template variant is proposed at any point, that's ZO-Q8's trigger — evaluate structured-parse migration, not just add another variant.
- No agent-substrate validation arc (peer to PA tools sweep). Requires explicit Chris directive.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — Chris pivoted to the sweep at S2892. If character-os side pings, stand by per pre-S2892 protocol.
- **Testing Discipline chapter candidacy** — ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — ledger row 159. Unchanged.
- **2-tier evidence template promotion** — ledger row 160. Triggers after 1-2 more large-surface sweeps adopt cleanly.
- **Sweep-arc pace sustainability substrate arc** — ledger row 161. **CLOSED (mitigated) 2026-07-22 S2904 arc close.** S2905 (4 tools) + S2906 (4 tools) + S2907 (3 tools) sustain the accelerated pace claim.
- **Response-level introspection field creep** — ledger row 162 (S2896). Same-PR mitigated; watch for pattern in other tools' response contracts.
- **Harness timestamp churn** — S2903 fold, `future_trigger`. Unchanged.
- **T1a FT-1 defaulted-tool action-set change lint** — S2903 substrate-arc-scope. Unchanged.
- **T1a FT-2 harness `soft_error` outcome value** — S2903 substrate-arc-scope. Unchanged.
- **T1b ZO-Q2 warn-noise escalation ladder** — S2904 substrate-arc-scope. Unchanged.
- **T1b ZO-Q7 automated corpus-counter helper** — S2904 substrate-arc-scope. Unchanged.
- **T1b ZO-Q8 structured-parse migration** — S2904 substrate-arc-scope. Unchanged.
- **S2905 metadata-pattern-selection lint** — substrate-arc-scope. Trigger: ≥3 sweep sessions mix `TOOL_DEFAULTS` + per-action `TOOL_ACTION_METADATA` without stated rule-based justification. **S2907 contribution: zero** (uniform-only batch). Distance to trigger: 2 more mixed sessions.
- **S2906 Ledger candidates (`get_body_vitals`, `web_search`, `get_system_alerts`)** — unchanged.
- **NEW — S2907 Ledger candidate: `ml_analysis` schema-declared `model_type` unused + handler-required `data` schema-missing** — silent-parameter-invisibility class (3rd tool with this pattern). Deferred (batch-scope discipline).
- **NEW — S2907 Ledger candidate: `voice_clone_tool` marketplace `limit` silent-clamp at 30 + `list`/`clone_requests` schema-declared-but-hard-capped at 20/10** — silent-truncation + schema-declared-but-handler-ignored classes. Deferred.
- **NEW — S2907 substrate finding: T1a harness `status_code`-only classification misclassifies inline `{ok:false}` envelopes as success** — 4/5 orm_inspect_tool dispatches this ship. Harness improvement candidate. Deferred to substrate-arc scope.
- **NEW — S2907 harness-substrate: MLEngine per-invocation NLP-model load stalls harness ~5min without `SKIP_NLP_MODELS=1`** — deferred to substrate-arc scope.
- **S2906/S2907 systemic drift trend candidate (Fold B)** — 7/8 tools across S2906+S2907 (87.5%). `future_trigger`: if drift rate sustains ≥50% across S2908 (3rd batch data point), promote to Playbook amendment (drift taxonomy + response rule) OR dedicated cleanup arc. Do NOT act off two data points. Also per Rigby T1 zoom-out E: watch for batch-selection + minimal-safe-args harness profile coupling — S2908 mixed-scoped batch either confirms drift is systemic OR reveals uniform-safe-args was inflating the rate.
- **S2905 Ledger candidates (`pilots_tool`, `cost_telemetry_tool`, `revenue_tracker_tool`)** — unchanged.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — Unchanged.
- **Applicability metadata pattern (entry #28)** — Unchanged.
- **Baseline lookback cap for HISTORICAL_BASELINE fields (entry #29)** — MITIGATED at PR #3423 (S2899). Substrate available; operator has not flipped default None yet.
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — Unchanged.
- **R1 fleet reject-mode flip** — deferred.
- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind sweep.
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits (`requested_model_id`, `was_policy_reroute`) — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (17 registered tools):**
- Batches 1-4 (S2892-S2895): 9 tools ✓
- **S2896-S2899:** 4 engineering ships (Rows A/B/C/#29 mitigated).
- **S2900-S2904:** Row 161 substrate arc — CLOSED. T1c ✓ S2901 + T1a ✓ S2902-S2903 + T1b ✓ S2904.
- **Remainder:** Slice 1.5b (autopilot_tool mutations, ~1 session; staged enforcement per pre-commit note) + `ops_tool` sweep slot (promoted from partial at T1c) + Phase 0 heading fixes for 8 close_with_short_note tools.

**Slice 2 — `td_handlers_agents` (25 tools):**
- **S2905 batch 1: 4 tools ✓** (gates_tool, pilots_tool, cost_telemetry_tool, revenue_tracker_tool). Mixed-pattern proof.
- **S2906 batch 2: 4 tools ✓** (get_body_vitals, check_resource_budget, get_system_alerts, web_search). Actionless-only proof.
- **S2907 batch 3: 3 tools ✓** (ml_analysis, voice_clone_tool, orm_inspect_tool). Small-actionful all-READ_ONLY proof.
- **S2908+ batches 4-5:** 14 tools remaining. S2908 REQUIRED shape-break (mixed-scoped-to-READ_ONLY-subset OR gated-write-dry_run-only). Target ~3-5 tools/batch → ~3 more batches.

**Slice 3 — `td_handlers_core` (22 tools):** queued behind Slice 2.
**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arc CLOSED (S2900-S2904):** T1c ✅ S2901 → T1a ✅ S2902+S2903 → T1b ✅ S2904.

**Total remaining tools to close:** 65 (or ~93 counting partials + doc-unknowns). Post-substrate sweep pace observed: S2905=4, S2906=4, S2907=3. Extrapolated remaining ~10-14 sessions at 4-5 tools/batch accelerated pace once mixed-shape coverage is exercised.

---

## Autopilot Slice 1.5b pre-commit note

When `autopilot_tool` mutations are eventually swept (Slice 1.5b), the shape MUST be:

1. **Staged-enforcement session** — many mutations require paired lifecycle scaffolding: `experiment_create` + `_start` (paired), `outreach_generate` + `_approve` + `_reject` (needs synthetic draft rows or A4 throttle waiver), `close_pack_generate` + `_approve` (needs synthetic opportunity_id), `meeting_create` + `_brief` + `_recap` (creates real calendar substrate), `governance_kill_switch` + `_deactivate_switch` (paired), `release_freeze` + `_unfreeze` (paired), `run` (evaluates all policies against real state — may create real blocks/downgrades).
2. **Canary containment per-action:** some are inherently global (`run`, `governance_set_mode global`, `release_freeze`) — need paired revert protocol. Others operate on single rows — canary to synthetic test data.
3. **A4 warm-up hard-throttle** (S2846) governs outreach mutations — max 3-5 total intros even in the mutation session.
4. **`backfill_impacts` + `backfill_failure_reasons`** — data-substrate writes; need idempotency verification post-write.
5. **`security_containment_plan dry_run=false, confirm=true`** — S1228 PR-A gate; explicit both-flag dispatch required.

Do NOT try to sweep both categories in one session.

---

## Two-Claude concurrency safety envelope (still active from S2889)

Rulebook: `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`.

- Each terminal uses its own Rigby conversation pin — no state collision.
- Different repos, different branches — no git collision.
- **Watch:** character-os Docker postgres previously captured u-d-b's `:5433` via IPv6 wildcard (S2885). `USE_PGBOUNCER=0` still in force in both `.env` files. If character-os side runs `docker compose up`, verify port ownership before restarting u-d-b.
- Shared u-d-b PA endpoint (`http://localhost:8000`) — both Claudes may drive it; surface handles concurrent conversations.

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2907 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2907: zero A4 spend — pure sweep-batch execution.** A1 shipping spend was the S2907 batch 3 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2907)

See:
- **S2907 handoff (current):** `docs/handoffs/SESSION_2907_SLICE_2_BATCH_3_SMALL_ACTIONFUL_SWEEP.md`
- **S2906 handoff:** `docs/handoffs/SESSION_2906_SLICE_2_BATCH_2_ACTIONLESS_SWEEP.md`
- **S2905 handoff:** `docs/handoffs/SESSION_2905_SLICE_2_BATCH_1_ACCELERATED_SWEEP.md`
- **S2904 handoff:** `docs/handoffs/SESSION_2904_T1B_TEMPLATE_EXTRACTION.md`
- **S2903 handoff:** `docs/handoffs/SESSION_2903_T1A_PHASE_2_METADATA_SEED.md`
- **S2902 handoff:** `docs/handoffs/SESSION_2902_T1A_AUTO_HARNESS_SCAFFOLD.md`
- **S2901 handoff:** `docs/handoffs/SESSION_2901_T1C_LOW_SIGNAL_AUDIT.md`
- **S2900 handoff:** `docs/handoffs/SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md`
- **S2900 substrate arc scoping (closed at S2904):** `docs/audits/pa_tools/substrate/S2900_substrate_arc_scoping.md` (parent) + `T1a_auto_harness.md` + `T1b_family_doc_templates.md` + `T1c_low_signal_audit.md` + `T1b_ship_shape_s2904.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2907 per-tool validation docs (new this session):**
  - `docs/research/tools/validation/ml_analysis_validation.md`
  - `docs/research/tools/validation/voice_clone_tool_validation.md`
  - `docs/research/tools/validation/orm_inspect_tool_validation.md`
- **S2906 per-tool validation docs:**
  - `docs/research/tools/validation/get_body_vitals_validation.md`
  - `docs/research/tools/validation/check_resource_budget_validation.md`
  - `docs/research/tools/validation/get_system_alerts_validation.md`
  - `docs/research/tools/validation/web_search_validation.md`
- **S2905 per-tool validation docs:**
  - `docs/research/tools/validation/gates_tool_validation.md`
  - `docs/research/tools/validation/pilots_tool_validation.md`
  - `docs/research/tools/validation/cost_telemetry_tool_validation.md`
  - `docs/research/tools/validation/revenue_tracker_tool_validation.md`
- **S2899 handoff:** `docs/handoffs/SESSION_2899_EMBEDDING_BASELINE_LOOKBACK_CAP.md`
- **S2898 handoff:** `docs/handoffs/SESSION_2898_INTEGRITY_NULL_SPIKE_APPLICABILITY.md`
- **S2897 handoff:** `docs/handoffs/SESSION_2897_PROSPECTING_QUEUE_TITLE_FIX.md`
- **S2896 handoff:** `docs/handoffs/SESSION_2896_AUTOPILOT_HISTORY_WIPE_DIAGNOSTIC.md`
- **S2895 handoff:** `docs/handoffs/SESSION_2895_PA_TOOLS_SWEEP_SLICE_1_5A_AUTOPILOT_READ_ONLY.md`
- **S2894 handoff:** `docs/handoffs/SESSION_2894_PA_TOOLS_SWEEP_SLICE_1_BATCH_3.md`
- **S2893 handoff:** `docs/handoffs/SESSION_2893_PA_TOOLS_SWEEP_SLICE_1_BATCH_2.md`
- **S2892 handoff:** `docs/handoffs/SESSION_2892_PA_TOOLS_SWEEP_SLICE_1_BATCH_1.md`
- **S2889 handoff:** `docs/handoffs/SESSION_2889_PLAYBOOK_V0_9_0_RATIFIED.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 33 non-substrate total post-S2907)
- **S2906 workspace mirrors** (authored by Rigby at S2907 open):
  - Content Mirror: `f9578144-0020-4cf9-b532-bbde2b892623`
  - Ratification Envelope: `deeca50b-9fa4-47a2-8d3a-fe0a974856e4`
  - Both in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`.
- **S2907 workspace mirrors:** Rigby to author at S2908 open (both into Donkey Betz workspace above) — content mirror + ratification envelope per `feedback_rigby_writes_workspace_deliverables`.
- **S2908 commitment memory:** `project_s2908_batch_4_shape_break_commitment.md`.
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace above).

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
