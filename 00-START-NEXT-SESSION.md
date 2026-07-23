# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2908 CLOSE → SHAPE-BREAK batch (mixed-scoped-to-READ_ONLY-subset) ✓ shipped. Fold B drift-rate data point #3 lands at 75% (down from 87.5% but still >50%). **S2909 OPENS WITH CHRIS D-VERDICT ON SYSTEMIC-DRIFT CLEANUP ARC (joint Claude+Rigby recommendation)** — D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2908 close).** First shape-break sweep batch after S2907 Fold A commitment. PR [#3441](https://github.com/clwest/donkey-betz-platform/pull/3441) merged at `a17aa0ba6`. Four mixed-safety tools validated (READ_ONLY subset only; mutations excluded via §5a Mutation containment):

- `bpaas_tool` (2 R covered / 2 M excluded)
- `davinci_tool` (5 R covered / 1 M excluded)
- `obs_tool` (3 R covered / 3 M excluded)
- `media_tool` (3 R covered / 1 IRREVERSIBLE excluded — **first IRREVERSIBLE in sweep corpus**)

Doc-only per S2796; metadata seed at `core/services/tool_action_metadata.py` uses Pattern C (per-action records for all 20 actions; no `TOOL_DEFAULTS` additions — keeps S2905 mixed-pattern lint counter at 1/3 sweep sessions).

**Shape-break commitment validated (S2907 T0 SIGN Fold A closed):**
- 13 READ_ONLY actions covered, 7 mutation actions correctly excluded from doc scope + harness dispatch.
- 4 new pass verdicts in gap map (23 full stays; +4 partial: 3 → 7 total). Untested 83 → 79.
- `td_handlers_agents` untested slice `14 → 10 (-4)`.
- Rigby joint SIGN (T0 + T1): 17 verification `tool_runs` between them; T0 caught count-ambiguity in initial dispatch and blocked AGREE until clarified. T1 verified 4 tools' `validated_partial` classification post-backtick-fix.
- Pattern C uniform this session — mixed-pattern coexistence count stays 1/3 sweep sessions (distance to lint trigger: 2 more mixed sessions).

**Post-merge live-dispatch verified (per PLAYBOOK-7.4.4):**
- `bpaas_tool action=get_schema` → clean `{success, action, schema}` (BUILD_PACKET_SCHEMA). ✓
- `davinci_tool action=grades` → clean `{action, count: 11, grades}` (COLOR_GRADE_PRESETS). ✓
- `obs_tool action=health` → error envelope `{ok: false, action, error: {code: OBS_DISABLED}}` — no crash. ✓ (`_obs_enabled()` false in local env; expected short-circuit.)
- `media_tool action=stats` → clean `{action, images: 10, videos: 0, audio: 4, total: 14}`. ✓

All 4 tools `TOOL_ACTION_METADATA` seed is live in worker.

**Rigby joint SIGN (S2908):** T0 SIGN AGREE-with-edits (validated_partial adoption + §5a conditional-mandatory rule + dependency_surface doc note + keep 4-tool batch). T1 SIGN AGREE (5 tool_runs verified 2 docs end-to-end + metadata seed + gap map rows for all 4 tools). Zero rubber-stamp SIGN across both rounds.

**PRs shipped this session:**
- u-d-b PR [#3441](https://github.com/clwest/donkey-betz-platform/pull/3441) — S2908 Slice 2 batch 4, merged at `a17aa0ba6`
- u-d-b PR `<TBD>` — S2908 close cascade (handoff + 00-START refresh + wrapper pin bump)

**Zoom-out folds captured (per PLAYBOOK-6.10.7):**
- **Fold Q6 (T0 zoom-out, mostly `same_pr_mitigatable`):** three coupling risks named — category ambiguity debt (solved by adopting `validated_partial`), doc-section ratchet creep (solved by conditional-mandatory §5a rule), harness semantics drift (long-term direction: move safety classification to `tool_action_metadata.py` code-truth, keep docs as evidence narrative).
- **Fold Q4 (T1 zoom-out, `future_trigger` + joint recommendation for Chris):** Fold B drift-rate data point #3 lands at **75%** — DOWN from 87.5% (S2906+S2907) but still >50% sustained. Rigby's batch-selection-bias hypothesis PARTIALLY confirmed (uniform-safe-args inflated the rate; drift IS systemic across shape variants). **Joint recommendation for S2909:** open systemic-drift cleanup arc scoped to (1) harness outcome classifier fix + (2) bridge availability precheck. Chris D-verdict required.

Full session context: `docs/handoffs/SESSION_2908_SLICE_2_BATCH_4_SHAPE_BREAK_SWEEP.md`.

---

## S2909 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Chris D-verdict on systemic-drift cleanup arc

**Chris directive required** — joint Claude+Rigby recommendation from S2908 T1 zoom-out Fold Q4: given 3 data points at >50% drift (87.5% × 2 + 75%), the Fold B systemic-drift hypothesis has crossed the "3-data-point 50% floor" trigger. Options:

**Option A (RECOMMENDED — joint Claude+Rigby):** Open systemic-drift cleanup arc as S2909 primary work. Scope:
1. **Harness outcome classifier fix** — `pa_tool_validate_harness` should treat inline `{error, error_code}` envelopes at HTTP 200 as `soft_error` outcome (not `success`). This alone would collapse most of the "classification drift" findings (9 instances across 4 tools cumulative).
2. **Bridge availability precheck** — preflight for `external_bridge` dependency surfaces (OBS bridge, resolve_node) so harness distinguishes "bridge down" (env config) vs "tool bug" (real drift).
3. **Optional post-fix experiment:** one reverse-control uniform-READ_ONLY sweep batch AFTER the harness fix to quantify whether drift-rate drops below 50% post-remediation. If it does, confirms Rigby's batch-selection-bias hypothesis fully. If it doesn't, drift is more systemic than the harness's classifier can explain — Playbook-amendment territory.

Advance to remediation before continuing sweep-batch work.

**Option B (Rigby-secondary):** Continue sweep — one more sweep batch (Shape A or Shape B per S2907 zoom-out E), THEN evaluate cleanup arc. Delays the substrate fix but gives one more clean data point. Rigby T1 flagged as "mostly re-proves the same systemic issue."

**Option C (defer):** Neither — pick a different S2909 track entirely (Testing Discipline chapter candidacy from ledger row 154; Bridge call observability rename-risk from row 155; or unrelated engineering work).

### Alternative Step 1 candidates (unchanged)

- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid but Fold Q4 recommendation supersedes at S2909 open.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note (§ below, unchanged).

**Recommend Option A** — closes the 3-data-point Fold B trigger with concrete substrate work rather than another sweep-batch data point.

### What's forbidden at S2909 (D6 MORATORIUM still in force)

- **NO another mixed-scoped sweep batch** unless Chris explicitly picks Option B — Fold Q4 says continuing without the harness fix mostly re-proves the same finding.
- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- No v1 → v2 harness schema bump WITHOUT substrate-arc-scoped SIGN. **FT-2 (`soft_error` outcome) is the exact remediation Fold Q4 recommends** — if Chris picks Option A, this bump happens under a substrate-arc SIGN cycle, not ad-hoc.
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
- **Sweep-arc pace sustainability substrate arc** — ledger row 161. **CLOSED (mitigated) 2026-07-22 S2904 arc close.** S2905 (4) + S2906 (4) + S2907 (3) + S2908 (4) sustain the accelerated pace claim.
- **Response-level introspection field creep** — ledger row 162 (S2896). Same-PR mitigated; watch for pattern in other tools' response contracts.
- **Harness timestamp churn** — S2903 fold, `future_trigger`. Unchanged.
- **T1a FT-1 defaulted-tool action-set change lint** — S2903 substrate-arc-scope. Unchanged.
- **T1a FT-2 harness `soft_error` outcome value** — S2903 substrate-arc-scope. **NOW LOAD-BEARING for S2909 Option A cleanup arc.**
- **T1b ZO-Q2 warn-noise escalation ladder** — S2904 substrate-arc-scope. Unchanged.
- **T1b ZO-Q7 automated corpus-counter helper** — S2904 substrate-arc-scope. Unchanged.
- **T1b ZO-Q8 structured-parse migration** — S2904 substrate-arc-scope. Unchanged.
- **S2905 metadata-pattern-selection lint** — substrate-arc-scope. Trigger: ≥3 sweep sessions mix `TOOL_DEFAULTS` + per-action `TOOL_ACTION_METADATA` without stated rule-based justification. **S2908 contribution: zero** (Pattern C uniform-only). Distance to trigger: 2 more mixed sessions.
- **S2906 Ledger candidates (`get_body_vitals`, `web_search`, `get_system_alerts`)** — unchanged.
- **S2907 Ledger candidate: `ml_analysis` schema-declared `model_type` unused + handler-required `data` schema-missing** — unchanged.
- **S2907 Ledger candidate: `voice_clone_tool` marketplace `limit` silent-clamp at 30 + `list`/`clone_requests` schema-declared-but-hard-capped at 20/10** — unchanged.
- **S2907 substrate finding: T1a harness `status_code`-only classification misclassifies inline `{ok:false}` envelopes as success** — **NOW LOAD-BEARING for S2909 Option A cleanup arc.**
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load stalls harness ~5min without `SKIP_NLP_MODELS=1`** — unchanged.
- **NEW — S2908 substrate finding: T1a harness classification-drift pattern extended, 5 more instances (davinci health+jobs, obs health+status+last) → 9 total across 4 tools** — merged into the S2907 substrate finding above.
- **NEW — S2908 substrate finding: Bridge-unreachable-during-harness detection gap** — external_bridge tools (davinci_tool + obs_tool) surface bridge-unreachable envelopes at harness time without any preflight distinguishing "bridge down" vs "tool bug". **LOAD-BEARING for S2909 Option A cleanup arc scope (2).**
- **NEW — S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action in sweep corpus — no confirm flag, no soft-delete** — confirmation-flow ADR candidate. Design-arc-scope; deferred.
- **NEW — S2908 doc-fix candidate: `obs_tool_validation.md` §6.1 conflates OBS_DISABLED vs BRIDGE_UNREACHABLE error envelopes** — post-merge dispatch surfaced OBS_DISABLED envelope specifically (`_obs_enabled()` false short-circuit); doc annotation is directionally correct but should distinguish. Small-doc-touch scope; deferred.
- **S2906/S2907/S2908 systemic drift trend (Fold B, 3 data points, 75% latest)** — **AT CROSS-OVER — joint recommendation for Chris to open cleanup arc at S2909 (see Option A above).**
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
- **S2900-S2904:** Row 161 substrate arc — CLOSED.
- **Remainder:** Slice 1.5b (autopilot_tool mutations, ~1 session) + `ops_tool` sweep slot (promoted from partial at T1c) + Phase 0 heading fixes for 8 close_with_short_note tools.

**Slice 2 — `td_handlers_agents` (25 tools):**
- **S2905 batch 1: 4 tools ✓** (gates_tool, pilots_tool, cost_telemetry_tool, revenue_tracker_tool). Mixed-pattern proof.
- **S2906 batch 2: 4 tools ✓** (get_body_vitals, check_resource_budget, get_system_alerts, web_search). Actionless-only proof.
- **S2907 batch 3: 3 tools ✓** (ml_analysis, voice_clone_tool, orm_inspect_tool). Small-actionful all-READ_ONLY proof.
- **S2908 batch 4: 4 tools ✓** (bpaas_tool, davinci_tool, obs_tool, media_tool). **SHAPE-BREAK — mixed-scoped-to-READ_ONLY-subset proof.**
- **S2909+ batches 5+:** 10 tools remaining. Recommend HOLDING sweep until cleanup arc lands (Option A). If Chris picks Option B, target ~3-5 tools/batch → ~2-3 more batches to close Slice 2.

**Slice 3 — `td_handlers_core` (22 tools):** queued behind Slice 2.
**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arc CLOSED (S2900-S2904):** T1c ✅ S2901 → T1a ✅ S2902+S2903 → T1b ✅ S2904.

**Total remaining tools to close:** ~61 (or ~89 counting partials + doc-unknowns). Post-substrate sweep pace observed: S2905=4, S2906=4, S2907=3, S2908=4. Extrapolated remaining ~10-13 sessions at 4-5 tools/batch accelerated pace once mixed-shape coverage is exercised — but Fold Q4 recommendation is to pause sweep and open cleanup arc first.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2908 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2908: zero A4 spend — pure sweep-batch execution.** A1 shipping spend was the S2908 batch 4 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2908)

See:
- **S2908 handoff (current):** `docs/handoffs/SESSION_2908_SLICE_2_BATCH_4_SHAPE_BREAK_SWEEP.md`
- **S2907 handoff:** `docs/handoffs/SESSION_2907_SLICE_2_BATCH_3_SMALL_ACTIONFUL_SWEEP.md`
- **S2906 handoff:** `docs/handoffs/SESSION_2906_SLICE_2_BATCH_2_ACTIONLESS_SWEEP.md`
- **S2905 handoff:** `docs/handoffs/SESSION_2905_SLICE_2_BATCH_1_ACCELERATED_SWEEP.md`
- **S2904 handoff:** `docs/handoffs/SESSION_2904_T1B_TEMPLATE_EXTRACTION.md`
- **S2903 handoff:** `docs/handoffs/SESSION_2903_T1A_PHASE_2_METADATA_SEED.md`
- **S2902 handoff:** `docs/handoffs/SESSION_2902_T1A_AUTO_HARNESS_SCAFFOLD.md`
- **S2901 handoff:** `docs/handoffs/SESSION_2901_T1C_LOW_SIGNAL_AUDIT.md`
- **S2900 handoff:** `docs/handoffs/SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md`
- **S2900 substrate arc scoping (closed at S2904):** `docs/audits/pa_tools/substrate/S2900_substrate_arc_scoping.md` (parent) + T1a/T1b/T1c child docs
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2908 per-tool validation docs (new this session):**
  - `docs/research/tools/validation/bpaas_tool_validation.md`
  - `docs/research/tools/validation/davinci_tool_validation.md`
  - `docs/research/tools/validation/obs_tool_validation.md`
  - `docs/research/tools/validation/media_tool_validation.md`
- **S2907 per-tool validation docs:**
  - `docs/research/tools/validation/ml_analysis_validation.md`
  - `docs/research/tools/validation/voice_clone_tool_validation.md`
  - `docs/research/tools/validation/orm_inspect_tool_validation.md`
- **S2906 per-tool validation docs:** `get_body_vitals_validation.md`, `check_resource_budget_validation.md`, `get_system_alerts_validation.md`, `web_search_validation.md`
- **S2905 per-tool validation docs:** `gates_tool_validation.md`, `pilots_tool_validation.md`, `cost_telemetry_tool_validation.md`, `revenue_tracker_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 37 non-substrate total post-S2908)
- **S2907 workspace mirrors** (Rigby to author at S2909 open — outstanding from S2908 open per `feedback_rigby_writes_workspace_deliverables`):
  - Both in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`.
- **S2908 workspace mirrors:** Rigby to author at S2909 open (both into Donkey Betz workspace above) — content mirror + ratification envelope per `feedback_rigby_writes_workspace_deliverables`.
- **S2908 commitment memory:** `project_s2908_batch_4_shape_break_commitment.md` — **CLOSED (mitigated).**
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace above).

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
