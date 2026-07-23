# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2909 CLOSE → S2909 substrate cleanup arc T1+T2 shipped, arc CLOSED ✓. Fold B systemic drift crushed 87.5% → 13.3%. **S2910 OPENS WITH SWEEP RESUMPTION — Slice 2 batch 5 (harness now trustworthy)** — D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2909 close).** Substrate cleanup arc opened Chris-ratified Option A + shipped T1 (PR [#3443](https://github.com/clwest/donkey-betz-platform/pull/3443) at `dbea312541c7`) + shipped T2 (PR [#3444](https://github.com/clwest/donkey-betz-platform/pull/3444) at `589b0792df90`) + closed without T3 (joint Claude+Rigby AGREE + Chris D-verdict). Total: 1 session, beat the ≤3-session estimate.

**Arc thread outcomes:**

- **T1 — harness soft_error classifier.** `pa_tool_validate_harness._run_single_action` now reclassifies transport-success + inline error envelope (`ok:false` or `error_code` present) as new stable `expected_outcome='soft_error'`. `HARNESS_VERSION 'v1' → 'v2'`. 117 artifacts backfilled. 8 regression tests. Docstring Migration notes block documents Fold Q4 (per-tool validation docs are hand-authored, NOT auto-regenerated).
- **T2 — bridge availability precheck.** `ToolActionMetadata.bridge: Optional[str]` field + `resolve_bridge` helper + `_probe_bridge` method (cached per-run, uses SAME client tool uses per Rigby T2 Q4 fold #1 critical catch — RESOLVE_NODE_URL vs DAVINCI_BRIDGE_URL sprawl). New stable `expected_outcome='skipped_bridge_unreachable'`. 7 external_bridge READ_ONLY entries wired. 9 regression tests.
- **T3 — deferred as unnecessary.** Joint Claude+Rigby SIGN AGREE + Chris D-verdict: T1+T2 evidence answers "did drift drop below 50% post-remediation?" decisively (87.5% → 13.3%). T3 would only add secondary epistemic value (selection-bias quantification).

**Sweep-15 drift trend (Fold B measurement scope):**
- Pre-fix: 87.5% × 2 + 75% (S2906/S2907/S2908 batches)
- Post-T1 (v2 classifier): 24.3% (9/37)
- **Post-T2 (bridge preflight): 13.3% (4/30)** — below the 50% Fold B floor that opened the arc

Post-T2 residual soft_errors (4/30): all `orm_inspect_tool` required-arg cases (`describe_model`/`get`/`filter`/`count_by` need `model` param). Different substrate class — logged as FT-5 candidate.

**Rigby joint SIGN (3 grounded cycles this session):**
- T0 arc-scope SIGN (before code) — Q1-Q3 AGREE, Q4 named DOC-AUTOGEN coupling risk → §4 Fold Q4 + T1 docstring migration note
- T1 post-implementation SIGN — SHIP-READY, flagged stale docstring polish, Q4 named FT-1/FT-2/FT-3
- T2 shape + post-implementation SIGN — Q1/Q3 AGREE, Q2 REVISE (5s/3s timeouts), **Q4 caught critical env-var-sprawl bug (RESOLVE_NODE_URL:5001 vs DAVINCI_BRIDGE_URL:9090) that would have false-positive-skipped healthy tools**, Q4 named FT-4 + FT-5

**PRs shipped this session:**
- u-d-b PR [#3443](https://github.com/clwest/donkey-betz-platform/pull/3443) — S2909 T1 harness soft_error classifier, merged at `dbea312541c7`
- u-d-b PR [#3444](https://github.com/clwest/donkey-betz-platform/pull/3444) — S2909 T2 bridge availability precheck, merged at `589b0792df90`
- u-d-b PR `<TBD>` — S2909 close cascade (handoff + 00-START refresh + wrapper pin bump)

**Post-merge live-dispatch verified (per PLAYBOOK-7.4.4):**
- Post-T1: `obs_tool.json` v2 shows 3 READ_ONLY as `soft_error` with inline_error_code notes ✓
- Post-T2: `obs_tool.json` v2 shows 3 READ_ONLY as `skipped_bridge_unreachable` (`bridge=obs; OBS_ENABLED env not set`) ✓; `davinci_tool.json` shows 4 READ_ONLY as `skipped_bridge_unreachable` with resolve_node URL in notes (proves probe uses ResolveNodeClient's URL — Rigby's Q4 fold #1 catch validated) ✓

Full session context: `docs/handoffs/SESSION_2909_SUBSTRATE_CLEANUP_ARC_T1_T2_SHIPPED.md`.

---

## S2910 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Resume Slice 2 sweep, pick batch 5

**No blocking Chris D-verdict.** S2909 arc closed cleanly; harness now trustworthy. Advance to sweep-batch cadence.

**Slice 2 remaining: 10 tools** across `td_handlers_agents`. Suggested batch 5 composition (Rigby to propose specifics at S2910 T0 SIGN):
- Continue accelerated pace (S2905/S2906/S2907/S2908 shipped 4/4/3/4 tools respectively)
- Target ~3-5 tools per batch
- Shape: mixed-safety-scoped-to-READ_ONLY-subset OR uniform-READ_ONLY-multi-action — Rigby to recommend based on remaining-10 composition

**Post-arc harness gain:** future sweep batches measure real drift against the fixed v2 classifier + bridge preflight. Prior Fold B rates (87.5%) were artifacts of the classifier bug — S2910+ drift measurements will reflect actual tool health.

### Alternative Step 1 candidates (unchanged from S2908 open)

- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note (§ below, unchanged).

### What's forbidden at S2910 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.** v2 is now frozen at S2909 close. Any additional classifier or outcome-value changes require a fresh substrate-arc SIGN cycle.
- No new gate/lint proposals (FT-3/FT-4 stay logged, not built).
- No agent-substrate validation arc (peer to PA tools sweep). Requires explicit Chris directive.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.** FT-5 is a tracked candidate; the arc opens only when Chris ratifies.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — Chris pivoted to the sweep at S2892. If character-os side pings, stand by per pre-S2892 protocol.
- **Testing Discipline chapter candidacy** — Ledger row 154 `future_trigger`. Unchanged; FT-3 (`soft_error_count` gate) may fold in.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged.
- **2-tier evidence template promotion** — Ledger row 160. Triggers after 1-2 more large-surface sweeps adopt cleanly.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. **CLOSED (mitigated) 2026-07-22 S2904 arc close.** S2905+S2906+S2907+S2908 sustained the accelerated pace; S2909 substrate cleanup arc confirmed the harness underpinning.
- **Response-level introspection field creep** — Ledger row 162 (S2896). Same-PR mitigated.
- **S2905 metadata-pattern-selection lint** — substrate-arc-scope. Distance to trigger: 2 more mixed sessions (S2909 was zero-contribution since T1+T2 are harness/metadata not tool-sweep).
- **S2906/S2907/S2908 Ledger candidates** — unchanged.
- **S2907 substrate finding: T1a harness `status_code`-only misclassification** — **CLOSED-BY-ARC-T1 at `dbea312541c7`.**
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load stalls harness ~5min without `SKIP_NLP_MODELS=1`** — unchanged.
- **S2908 substrate finding: Bridge-unreachable-during-harness detection gap** — **CLOSED-BY-ARC-T2 at `589b0792df90`.**
- **S2908 doc-fix candidate: `obs_tool_validation.md` §6.1 conflates OBS_DISABLED vs BRIDGE_UNREACHABLE error envelopes** — Small-doc-touch scope; deferred. Note: T2 backfill now correctly bucket OBS_DISABLED as `skipped_bridge_unreachable` in harness output; validation doc still needs its own touch-up.
- **S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action** — confirmation-flow ADR candidate. Design-arc-scope; deferred.
- **S2906/S2907/S2908 systemic drift trend (Fold B, 3 data points)** — **CLOSED at S2909 arc close.** Drift measurement approach validated + fix shipped.
- **S2905 Ledger candidates (`pilots_tool`, `cost_telemetry_tool`, `revenue_tracker_tool`)** — unchanged.
- **NEW S2909 FT-1 — `artifact_sha256` cache-invalidation ripple** — operational-ripple future_trigger. If a downstream watcher of artifact hashes surfaces, evaluate.
- **NEW S2909 FT-2 — `error_code`-key false-positive constraint** — tools must not emit `error_code` on success. Enforcement TBD.
- **NEW S2909 FT-3 — `soft_error_count` new-gate-temptation** — new CI/merge gate proposals ratify separately (likely under Testing Discipline chapter candidacy).
- **NEW S2909 FT-4 — bridge-metadata consistency lint** — external_bridge in notes → bridge field required.
- **NEW S2909 FT-5 — `minimal_safe_args_v2` substrate arc candidate** — orm_inspect_tool-style residual drift is input-synthesis concern. Opens only via explicit Chris directive; do NOT open under S2910.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — Unchanged.
- **Applicability metadata pattern (entry #28)** — Unchanged.
- **Baseline lookback cap (entry #29)** — MITIGATED at PR #3423 (S2899).
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — Unchanged.
- **NEW S2909 Ledger entry #31 — content-mirror auto-flagged as diagnostic** — 2 instances this session; substrate fix candidate.
- **NEW S2909 Ledger entry #32 — FT-5 minimal_safe_args_v2 tracker.**
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
- **S2910+ batches 5+:** 10 tools remaining. Target ~3-5 tools/batch → ~2-3 more batches to close Slice 2 at accelerated pace with trustworthy harness.

**Slice 3 — `td_handlers_core` (22 tools):** queued behind Slice 2.
**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight).

**Total remaining tools to close:** ~57 (or ~85 counting partials + doc-unknowns). Post-substrate sweep pace at S2905-S2908 = 4/4/3/4 tools/batch. Extrapolated remaining ~10-13 sessions at accelerated pace with trustworthy harness.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2909 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2909: zero A4 spend — pure substrate-arc engineering.** A1 shipping spend was T1 PR + T2 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2909)

See:
- **S2909 handoff (current):** `docs/handoffs/SESSION_2909_SUBSTRATE_CLEANUP_ARC_T1_T2_SHIPPED.md`
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
- **S2908 per-tool validation docs:** `bpaas_tool_validation.md`, `davinci_tool_validation.md`, `obs_tool_validation.md`, `media_tool_validation.md`
- **S2907 per-tool validation docs:** `ml_analysis_validation.md`, `voice_clone_tool_validation.md`, `orm_inspect_tool_validation.md`
- **S2906 per-tool validation docs:** `get_body_vitals_validation.md`, `check_resource_budget_validation.md`, `get_system_alerts_validation.md`, `web_search_validation.md`
- **S2905 per-tool validation docs:** `gates_tool_validation.md`, `pilots_tool_validation.md`, `cost_telemetry_tool_validation.md`, `revenue_tracker_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 37 non-substrate)
- **S2909 workspace mirrors** (all in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`):
  - Arc scoping content mirror `8795f629-737d-4709-8782-3f3e7ee5d3d7`
  - T1 ratification envelope `84dadc95-e68c-47a1-bb3a-74f7a160ed29`
  - T2 ratification envelope `cb91603b-cb83-4b25-8f80-1c5ae901e9ec`
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entries #31 + #32 appended this session).

For older session history (S1-S2848), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
