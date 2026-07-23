# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2912 CLOSE → S2912 Slice 2 batch 6b shipped (1 tool; `universal_agent_tool` solo) + **SLICE 2 CLOSED at 25/25 tools**. **S2913 OPENS WITH SLICE 3 BATCH 1** (`td_handlers_core.py`, 22 tools) — D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2912 close).** Sixth accelerated PA-tools sweep batch in Slice 2 and its final tool. Batch 6b shipped `universal_agent_tool` as solo 1-tool batch per S2908 last-in-slice precedent. Contract-only ship rationale ratified by Chris (Option A) — handler always enqueues a real Celery task with no dry_run/noop fast-path, so post-merge verification is contract-level (schema/handler/metadata alignment) + worker recycle freshness per PLAYBOOK-7.4.4, NOT live dispatch.

**PRs shipped this session:**
- u-d-b PR [#3451](https://github.com/clwest/donkey-betz-platform/pull/3451) — S2912 Slice 2 batch 6b + Slice 2 close, merged at `71bf71a10`.
- u-d-b PR `<TBD>` — S2912 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Batch 6b outcomes:**

- **`universal_agent_tool`** (`td_handlers_agents.py:1771`, actionless schema) — TOOL_DEFAULTS entry `safety_class='MUTATION'`, `applicability='conditional'` + 141-line validation doc (sweep variant v1). §5a captures no-live-fire posture + `dry_run` add-flag pattern as future-mitigation note. Frontmatter reconciles intent (`validated_partial` per Chris Option A) vs classifier ceiling (`validated (full)` per actionless-tool rule at `pa_tools_gap_map.py:439-442`) explicitly.
- **All 3 Rigby T1 same-PR mitigations landed** — frontmatter reconciliation (line 10), methodology-framing softening (line 134 — "validated (contract-only close) with limit exposed"), queue-state framing softening (line 119 — "not planned under the current sweep" vs prior "no future batch is scheduled").

**Rigby joint SIGN (2 substantive cycles this session, zero rubber-stamp):**
- Batch 6b T0 SIGN AGREE-with-edits — Q1 solo-ship + Q2 TOOL_DEFAULTS MUTATION conditional (tightened applicability='conditional') + Q3 contract-only (rejected `task='noop'` as no handler-side noop path) + Q4(a) uniformity claim ratified with error-envelope caution + Q4(b) methodology-validation with limit exposed.
- Batch 6b T1 SIGN mixed — V1/V3/V4 AGREE + V2 AGREE-with-edits (frontmatter reconciliation) + Q5(a)/Q5(b) DISAGREE (methodology-framing + queue-state softening). **Operational note:** T1 initial dispatch errored on OpenAI Connection error mid-synthesis but tool_runs completed cleanly; retry produced verdicts. Transient failures do NOT invalidate captured tool_runs.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- `make recycle-all` clean (`logs/recycle_events.jsonl` entry `sha=71bf71a10ee0, surviving=none`).
- **No live dispatch attempted for `universal_agent_tool`** — contract-only ship per §5a. Live-fire testability requires the ~10-line `dry_run` add-flag mitigation documented in §5a; not opened as a substrate arc (see forbidden list).

**Sweep progress (post-S2912):**
- Slice 2 (`td_handlers_agents`): **25/25 shipped. CLOSED.**
- Total corpus untested: 70 → 69 (-1). Gap map: 32 full + 8 partial + 69 untested.
- Slice 3 (`td_handlers_core`, 22 tools) opens next session (S2913).

Full session context: `docs/handoffs/SESSION_2912_SLICE_2_CLOSE.md`.

---

## S2913 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 3 batch 1 (first batch of `td_handlers_core.py`)

**No blocking Chris D-verdict.** S2912 shipped 1 PR cleanly; Slice 2 closed; harness trustworthy post-S2909 arc + S2911 latent-bug reveal + S2912 clean-execution proof.

**Slice 3 inventory pre-check:** `td_handlers_core.py` has 25 `_handle_*` handlers (`grep -c "def _handle_" core/services/td_handlers_core.py` = 25); the "22 tools" count in the sweep tracker reflects schema-registered tools (some handlers are handler-only or register multiple names). Confirm exact tool-count via `PA_TOOL_AUDIT.md` cross-reference before committing batch composition.

**S2913 T0 SIGN questions to route to Rigby:**
- **Q1 Batch composition:** (a) 4-tool mixed-composition batch mirroring S2910 batch 5 shape; (b) actionless-only opener mirroring S2906 batch 2 shape; (c) grep for read-only-vs-mutation distribution across the 22-tool Slice 3 corpus before deciding.
- **Q2 Bridge dependency scan:** Slice 2 was pure-ORM (all batches). Slice 3 has bridge-suspects at first-glance: `_handle_active_repo` (:89), `_handle_fleet_health` (:159), `_handle_paid_interest_status` (:188), `_handle_db_health` (:1442), `_handle_http_smoke_test` (:1884), `_handle_workflow_run` (:3141). S2909 bridge preflight substrate should apply. Which of these need bridge preflight envelope handling before batching?
- **Q3 Shape recommendation:** TOOL_DEFAULTS vs per-action metadata mix based on Q1/Q2 outcomes. Follow S2905 metadata-pattern-selection lint counter cadence.
- **Q4 zoom-out ask (required per feedback_zoom_out_ask_per_rigby_sign):** Slice 3 opens fresh. What does Slice 2 close *fail* to teach us about Slice 3? What's the highest-risk assumption carried across the slice boundary that S2913 should invalidate or validate in T0?

### Alternative Step 1 candidates (unchanged from S2911/S2912 open)

- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.

### What's forbidden at S2913 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.** v2 is frozen at S2909 close.
- No new gate/lint proposals (S2910 FT-3/FT-4 stay logged, not built).
- No agent-substrate validation arc (peer to PA tools sweep). Requires explicit Chris directive.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.** FT-5 is a tracked candidate; opens only via Chris ratify.
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.** S2910 Ledger #33 candidate is logged, not built.
- **No "schema-drift-fix Fold promotion" without 2nd confirmed instance.** S2911 Ledger #36 is Candidate Fold — Trigger #1 only; forward-carry.
- **No `dry_run` infrastructure arc for mutation-class dispatchers without explicit Chris directive.** S2912 §5a documents the ~10-line same-shape mitigation; do not open it as a substrate arc.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — Chris pivoted to the sweep at S2892. If character-os side pings, stand by per pre-S2892 protocol.
- **Testing Discipline chapter candidacy** — Ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged.
- **2-tier evidence template promotion** — Ledger row 160. Triggers after 1-2 more large-surface sweeps adopt cleanly.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. **CLOSED (mitigated) 2026-07-22 S2904 arc close.** S2905→S2912 sustained accelerated pace through end-of-Slice-2.
- **Response-level introspection field creep** — Ledger row 162 (S2896). Same-PR mitigated.
- **S2905 metadata-pattern-selection lint** — substrate-arc-scope. Batch 6b used TOOL_DEFAULTS (actionless); no shadowing. Counter unchanged.
- **S2906/S2907/S2908 Ledger candidates** — unchanged.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load stalls harness ~5min without `SKIP_NLP_MODELS=1`** — unchanged.
- **S2908 doc-fix candidate: `obs_tool_validation.md` §6.1 conflates OBS_DISABLED vs BRIDGE_UNREACHABLE error envelopes** — unchanged.
- **S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action** — confirmation-flow ADR candidate. Design-arc-scope; deferred.
- **S2909 FT-1 through FT-5** — unchanged; FT-5 (`minimal_safe_args_v2`) still tracked as candidate arc, opens only via explicit Chris directive.
- **S2910 FT-1 (Ledger #33) — Entrypoint-side context-injection test coverage gap** — unchanged.
- **S2910 FT-2 (Ledger #34) — Doc-pointer-verification lint candidate** — no new instances S2912. Unchanged.
- **S2911 Ledger #35 — Envelope-shape inconsistency on `opportunity_manager.delete` + `task_manager.delete` unknown-id paths** — unchanged. Not urgent (both IRREVERSIBLE-skipped); track for future MUTATION-coverage batch.
- **S2911 Ledger #36 — Candidate Fold Trigger #1 (schema-drift-fix always exercise every action branch)** — unchanged. **NOT corroborated at S2912** (batch 6b not a drift-fix ship; no new independent instance). Promote on 2nd trigger.
- **S2911 Ledger #37 — HIDDEN MUTATION planner-safety pattern** — unchanged. Track for other tools with implicit-parent-row creation.
- **NEW S2912 §5a mitigation note — `dry_run` add-flag pattern for actionless mutation-class dispatchers** — ~10-line same-shape mitigation documented in `universal_agent_tool_validation.md` §5a. NOT opened as substrate arc; wait for Chris directive OR 2nd mutation-class dispatcher ship that would benefit before promoting.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — Unchanged.
- **Applicability metadata pattern (entry #28)** — Unchanged.
- **Baseline lookback cap (entry #29)** — MITIGATED at PR #3423 (S2899).
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — Unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
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

**Slice 2 — `td_handlers_agents` (25 tools):** **CLOSED.**
- **S2905 batch 1: 4 tools ✓** (gates_tool, pilots_tool, cost_telemetry_tool, revenue_tracker_tool). Mixed-pattern proof.
- **S2906 batch 2: 4 tools ✓** (get_body_vitals, check_resource_budget, get_system_alerts, web_search). Actionless-only proof.
- **S2907 batch 3: 3 tools ✓** (ml_analysis, voice_clone_tool, orm_inspect_tool). Small-actionful all-READ_ONLY proof.
- **S2908 batch 4: 4 tools ✓** (bpaas_tool, davinci_tool, obs_tool, media_tool). SHAPE-BREAK mixed-scoped-to-READ_ONLY-subset proof.
- **S2909:** substrate cleanup arc (T1+T2 shipped, arc closed). Zero sweep-batch contribution.
- **S2910 batch 5: 4 tools ✓** (brainstorm_tool, web_fetch_tool, schedule_followup, legal_doc_drafter_agent). Mixed-composition-across-batch proof.
- **S2911 batch 6a: 4 tools ✓** (opportunity_manager_tool, task_manager_tool, pipeline_orchestrator_tool, video_history_tool). Scoped-to-READ_ONLY-subset mixed-safety proof (all pure ORM, no bridges).
- **S2911 drift-fix ✓** (reasoning_engine_tool). Schema↔handler drift 1st confirmed instance CLOSED + latent handler bug fixed.
- **S2912 batch 6b: 1 tool ✓** (universal_agent_tool). Solo last-in-slice + contract-only mutation-class dispatcher proof.

**Slice 3 — `td_handlers_core` (22 tools):** **Opens S2913.**
**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix).

**Total remaining tools to close:** ~51. Post-substrate sweep pace at S2905-S2912 = 4/4/3/4/4/4/1 tools/batch + 1 drift-fix. Extrapolated remaining ~7-10 sessions at accelerated pace with trustworthy harness.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2912 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2912: zero A4 spend — pure sweep-batch engineering (batch 6b + Slice 2 close).** A1 shipping spend was batch 6b PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2912)

See:
- **S2912 handoff (current):** `docs/handoffs/SESSION_2912_SLICE_2_CLOSE.md`
- **S2911 handoff:** `docs/handoffs/SESSION_2911_SLICE_2_BATCH_6A_PLUS_DRIFT_FIX.md`
- **S2910 handoff:** `docs/handoffs/SESSION_2910_SLICE_2_BATCH_5_MIXED_COMPOSITION_SWEEP.md`
- **S2909 handoff:** `docs/handoffs/SESSION_2909_SUBSTRATE_CLEANUP_ARC_T1_T2_SHIPPED.md`
- **S2909 arc scoping doc:** `docs/audits/pa_tools/substrate/S2909_substrate_cleanup_arc_scoping.md`
- **S2908 handoff:** `docs/handoffs/SESSION_2908_SLICE_2_BATCH_4_SHAPE_BREAK_SWEEP.md`
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
- **S2912 per-tool validation doc (this session):** `universal_agent_tool_validation.md`
- **S2911 per-tool validation docs:** `opportunity_manager_tool_validation.md`, `task_manager_tool_validation.md`, `pipeline_orchestrator_tool_validation.md`, `video_history_tool_validation.md`, `reasoning_engine_tool_validation.md`
- **S2910 per-tool validation docs:** `brainstorm_tool_validation.md`, `web_fetch_tool_validation.md`, `schedule_followup_validation.md`, `legal_doc_drafter_agent_validation.md`
- **S2908 per-tool validation docs:** `bpaas_tool_validation.md`, `davinci_tool_validation.md`, `obs_tool_validation.md`, `media_tool_validation.md`
- **S2907 per-tool validation docs:** `ml_analysis_validation.md`, `voice_clone_tool_validation.md`, `orm_inspect_tool_validation.md`
- **S2906 per-tool validation docs:** `get_body_vitals_validation.md`, `check_resource_budget_validation.md`, `get_system_alerts_validation.md`, `web_search_validation.md`
- **S2905 per-tool validation docs:** `gates_tool_validation.md`, `pilots_tool_validation.md`, `cost_telemetry_tool_validation.md`, `revenue_tracker_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 43 non-substrate post-S2912)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (unchanged from S2911 — no new ledger candidates this session).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
