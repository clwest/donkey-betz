# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2910 CLOSE → S2910 Slice 2 batch 5 shipped (4 tools; mixed-composition). **S2911 OPENS WITH SWEEP RESUMPTION — Slice 2 batch 6 (6 tools remaining)** — D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2910 close).** Fourth accelerated PA-tools sweep batch in Slice 2 after S2909 substrate cleanup arc closed the harness classifier + bridge preflight gaps. First mixed-composition batch: one 7-action mixed READ_ONLY+MUTATION tool (`brainstorm_tool` per-action records) + three actionless tools (`web_fetch_tool` READ_ONLY, `schedule_followup` WRITE_GATED, `legal_doc_drafter_agent` MUTATION) via `TOOL_DEFAULTS`.

**Batch outcomes:**

- **`brainstorm_tool`** — 6 R covered + 1 M excluded. 3 R clean success (`list`/`recent`/`stats`) + 3 R clean `error_captured` on ValueError-fail-loud paths (`search`/`details`/`by_category` require args beyond `action`). No `soft_error` drift — clean exception-path shape (contrast S2907 `orm_inspect_tool` FT-5 candidate).
- **`web_fetch_tool`** — actionless, TOOL_DEFAULTS READ_ONLY. Post-merge live GET `https://httpbin.org/status/200` returned expected 200 + full envelope shape.
- **`schedule_followup`** — actionless, TOOL_DEFAULTS WRITE_GATED conditional. **New regression test class** (`ScheduleFollowupPAContextInvariantTests`) added to honor Rigby T0 SIGN Q4 ask — 3 tests pin the PA-context invariant (missing-context error marker + nested-context promotion + root-vs-nested equivalence).
- **`legal_doc_drafter_agent`** — actionless, TOOL_DEFAULTS MUTATION conditional. Confirmed registered post-merge.

**Sweep progress (post-S2910):**
- Slice 2 (`td_handlers_agents`): 4 batches × 4/4/3/4 tools = 15 shipped + this batch's 4 = **19/25 shipped**; 6 remaining.
- Total corpus untested: 79 → 75 (-4). `validated_partial` 7 → 8 (+1 brainstorm); `validated_full` 27 → 26 (net -1 because brainstorm went partial).

**Rigby joint SIGN (2 substantive cycles this session, zero rubber-stamp):**
- T0 SIGN AGREE-with-edits — 4-tool composition ratified; Q4 flagged heterogeneous risk surfaces + `schedule_followup` context coupling; ask for PA-context invariant test honored this ship.
- T1 SIGN AGREE-with-edits — all Q1-Q3 substantive with handler/schema/test tool_runs cross-checks. **Q2 caught real drift**: `schedule_followup_validation.md` §Related pointed to `core/tests/test_schedule_followup_pa_context.py` (nonexistent); fixed pre-commit to reference the correct file + new class. Q3 flagged coverage limit: handler-side pinned, entrypoint-side injection at `unified_pa_entrypoint.py:2262-2264` uncovered — noted as follow-up in the doc.

**PRs shipped this session:**
- u-d-b PR [#3446](https://github.com/clwest/donkey-betz-platform/pull/3446) — S2910 Slice 2 batch 5 mixed-composition sweep, merged at `e84d69343`.
- u-d-b PR `<TBD>` — S2910 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Post-merge live-dispatch verified (per PLAYBOOK-7.4.4):**
- Post-merge: `make celery-recycle` → Rigby dispatched `brainstorm_tool action=stats` (matches doc §6.1 shape) + `web_fetch_tool` (matches doc §4/§5) + `schedule_followup` fake-execution-id (11-key contract + fail-loud) + `legal_doc_drafter_agent` registry visibility ✓.

Full session context: `docs/handoffs/SESSION_2910_SLICE_2_BATCH_5_MIXED_COMPOSITION_SWEEP.md`.

---

## S2911 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Resume Slice 2 sweep, pick batch 6

**No blocking Chris D-verdict.** S2910 shipped cleanly; harness continues trustworthy post-S2909 arc close.

**Slice 2 remaining: 6 tools** across `td_handlers_agents`:
- `opportunity_manager_tool`
- `pipeline_orchestrator_tool`
- `reasoning_engine_tool`
- `task_manager_tool`
- `universal_agent_tool`
- `video_history_tool`

**S2911 T0 SIGN questions to route to Rigby:**
- Batch 6 composition (which 3-5 of the 6 remaining tools). Suggest composition ties tools by dispatch-shape / handler-primitive coherence per S2910 T0 SIGN Q4 zoom-out ("coherent batches by side-effect class").
- Shape recommendation: uniform-READ_ONLY-multi-action OR mixed-scoped-to-READ_ONLY-subset. `opportunity_manager_tool` and `task_manager_tool` likely have MUTATION actions (`create`/`update_status`/`delete`); scoped-to-READ_ONLY-subset shape may fit.
- Bridge dependencies (per S2909 T2 metadata pattern) — likely none for this remaining set but confirm.
- Q4 zoom-out ask (per feedback_zoom_out_ask_per_rigby_sign) — required.

### Alternative Step 1 candidates (unchanged from S2910 open)

- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note (§ below, unchanged).

### What's forbidden at S2911 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.** v2 is frozen at S2909 close.
- No new gate/lint proposals (S2910 FT-3/FT-4 stay logged, not built).
- No agent-substrate validation arc (peer to PA tools sweep). Requires explicit Chris directive.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.** FT-5 is a tracked candidate; opens only via Chris ratify.
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.** S2910 Ledger #33 candidate is logged, not built.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — Chris pivoted to the sweep at S2892. If character-os side pings, stand by per pre-S2892 protocol.
- **Testing Discipline chapter candidacy** — Ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged.
- **2-tier evidence template promotion** — Ledger row 160. Triggers after 1-2 more large-surface sweeps adopt cleanly.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. **CLOSED (mitigated) 2026-07-22 S2904 arc close.** S2905→S2910 sustained accelerated pace; S2909 substrate cleanup confirmed harness underpinning.
- **Response-level introspection field creep** — Ledger row 162 (S2896). Same-PR mitigated.
- **S2905 metadata-pattern-selection lint** — substrate-arc-scope. Distance to trigger: 2 more mixed sessions (S2910 was mixed-composition-across-batch — different class than mixed-pattern-shadowing; may or may not increment counter, defer to next SIGN cycle for pattern-boundary judgment).
- **S2906/S2907/S2908 Ledger candidates** — unchanged.
- **S2907 substrate finding: T1a harness `status_code`-only misclassification** — **CLOSED-BY-ARC-T1 at `dbea312541c7`.**
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load stalls harness ~5min without `SKIP_NLP_MODELS=1`** — unchanged.
- **S2908 substrate finding: Bridge-unreachable-during-harness detection gap** — **CLOSED-BY-ARC-T2 at `589b0792df90`.**
- **S2908 doc-fix candidate: `obs_tool_validation.md` §6.1 conflates OBS_DISABLED vs BRIDGE_UNREACHABLE error envelopes** — unchanged.
- **S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action** — confirmation-flow ADR candidate. Design-arc-scope; deferred.
- **S2906/S2907/S2908 systemic drift trend (Fold B, 3 data points)** — **CLOSED at S2909 arc close.**
- **S2909 FT-1 through FT-5** — unchanged; FT-5 (`minimal_safe_args_v2`) still tracked as candidate arc, opens only via explicit Chris directive.
- **NEW S2910 FT-1 (Ledger #33) — Entrypoint-side context-injection test coverage gap.** `unified_pa_entrypoint.py:2262-2264` (`arguments.setdefault('conversation_id', self.conversation_id)`) is not asserted anywhere. Handler-side pinned this ship; entrypoint side uncovered. Substrate-arc scope; deferred.
- **NEW S2910 FT-2 (Ledger #34) — Doc-pointer-verification lint candidate.** 1 instance caught this session (schedule_followup doc → nonexistent test file). If recurs, propose a lint that grep-verifies test file paths cited in validation docs exist.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — Unchanged.
- **Applicability metadata pattern (entry #28)** — Unchanged.
- **Baseline lookback cap (entry #29)** — MITIGATED at PR #3423 (S2899).
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — Unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — 2 instances S2909; substrate fix candidate; unchanged.
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

**Slice 2 — `td_handlers_agents` (25 tools):**
- **S2905 batch 1: 4 tools ✓** (gates_tool, pilots_tool, cost_telemetry_tool, revenue_tracker_tool). Mixed-pattern proof.
- **S2906 batch 2: 4 tools ✓** (get_body_vitals, check_resource_budget, get_system_alerts, web_search). Actionless-only proof.
- **S2907 batch 3: 3 tools ✓** (ml_analysis, voice_clone_tool, orm_inspect_tool). Small-actionful all-READ_ONLY proof.
- **S2908 batch 4: 4 tools ✓** (bpaas_tool, davinci_tool, obs_tool, media_tool). SHAPE-BREAK mixed-scoped-to-READ_ONLY-subset proof.
- **S2909:** substrate cleanup arc (T1+T2 shipped, arc closed). Zero sweep-batch contribution.
- **S2910 batch 5: 4 tools ✓** (brainstorm_tool, web_fetch_tool, schedule_followup, legal_doc_drafter_agent). Mixed-composition-across-batch proof (per-action for multi-action + TOOL_DEFAULTS for actionless).
- **S2911+ batches 6+:** 6 tools remaining. Target ~3-5 tools/batch → ~1-2 more batches to close Slice 2 at accelerated pace.

**Slice 3 — `td_handlers_core` (22 tools):** queued behind Slice 2.
**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight).

**Total remaining tools to close:** ~53 (or ~81 counting partials + doc-unknowns). Post-substrate sweep pace at S2905-S2908 + S2910 = 4/4/3/4/4 tools/batch. Extrapolated remaining ~9-12 sessions at accelerated pace with trustworthy harness.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2910 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2910: zero A4 spend — pure sweep-batch engineering.** A1 shipping spend was batch 5 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2910)

See:
- **S2910 handoff (current):** `docs/handoffs/SESSION_2910_SLICE_2_BATCH_5_MIXED_COMPOSITION_SWEEP.md`
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
- **S2910 per-tool validation docs (this session):** `brainstorm_tool_validation.md`, `web_fetch_tool_validation.md`, `schedule_followup_validation.md`, `legal_doc_drafter_agent_validation.md`
- **S2908 per-tool validation docs:** `bpaas_tool_validation.md`, `davinci_tool_validation.md`, `obs_tool_validation.md`, `media_tool_validation.md`
- **S2907 per-tool validation docs:** `ml_analysis_validation.md`, `voice_clone_tool_validation.md`, `orm_inspect_tool_validation.md`
- **S2906 per-tool validation docs:** `get_body_vitals_validation.md`, `check_resource_budget_validation.md`, `get_system_alerts_validation.md`, `web_search_validation.md`
- **S2905 per-tool validation docs:** `gates_tool_validation.md`, `pilots_tool_validation.md`, `cost_telemetry_tool_validation.md`, `revenue_tracker_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 41 non-substrate post-S2910)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entries #33 + #34 candidates surfaced this session; workspace mirror TBD via Rigby dispatch).

For older session history (S1-S2848), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
