# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2906 CLOSE → Actionless-shape batch ✓ shipped. Second post-substrate batch. S2907 opens with **small-actionful all-read-only stress test** (S2906 T0 SIGN zoom-out commitment) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-23 (S2906 close).** Second accelerated PA-tools sweep batch after Row 161 substrate arc close. PR [#3437](https://github.com/clwest/donkey-betz-platform/pull/3437) merged at `40378bdf0`. Four actionless read-only tools (`schema_action_count=0` — a shape not exercised in S2905) validated: `get_body_vitals`, `check_resource_budget`, `get_system_alerts`, `web_search`. Same-PR handler fix for `get_system_alerts` schema/handler param drift shipped per Rigby T0 SIGN §C + T1 SIGN B edit.

**Actionless-shape claim validated:**
- Zero manual dispatch — T1a auto-harness produced empty-actions artifacts (`schema_action_count=0`) for all 4; `## Covered actions` intentionally empty; §5 Findings + handler-trace evidence carry the load per T1b template v1 sweep variant.
- 4 new pass verdicts in gap map (4 → 8 template compliance).
- `validated_full: 16 → 20 (+4)`, `untested: 90 → 86 (-4)`, `td_handlers_agents` untested slice `21 → 17 (-4)`.
- Rigby joint SIGN (T0 + T1): 9 verification `tool_runs` between them; sharp T0 zoom-out pushback caught actionless-only under-stress-testing risk, folded into 3-part scope claim in all 4 docs + S2907 stress-test pointer. T1 zoom-out identified systemic drift trend candidate (3/4 tools drift).
- Uniform-TOOL_DEFAULTS-only batch — zero per-action `TOOL_ACTION_METADATA` records added; mixed-pattern coexistence count stays 1/2 sweep sessions (distance to lint trigger: 2 more mixed sessions).

**Same-PR handler fix (post-merge live-dispatch verified):**
- `_handle_system_alerts` now accepts both `severity` (schema, preferred) and `severity_threshold` (legacy). Class-level `_SEVERITY_SCHEMA_TO_INTERNAL` maps schema domain → internal domain.
- Rigby T1 SIGN B edit folded same-PR: legacy-domain unknown values normalize to `warning` (not `info` — prevents silent regression).
- 8-case simulation OK; 3-case live Rigby dispatch post-recycle OK.

**Rigby joint SIGN (S2906):** T0 SIGN AGREE-with-edits (batch composition + actionless-shape + drift-fix directive + zoom-out fold to add S2907 commitment). T1 SIGN AGREE-with-1-edit (severity_threshold unknown-value normalization folded same-PR). Zero rubber-stamp SIGN across both rounds.

**PRs shipped this session:**
- u-d-b PR [#3437](https://github.com/clwest/donkey-betz-platform/pull/3437) — S2906 Slice 2 batch 2, merged at `40378bdf0`
- u-d-b PR `<TBD>` — S2906 close cascade (handoff + 00-START refresh + wrapper pin bump)

**Zoom-out folds captured (per PLAYBOOK-6.10.7):**
- **Fold A (T0 zoom-out, `same_pr_mitigated`):** Actionless-only batch under-stress-tests the "handler-trace evidence required for `## Covered actions`" claim. Same-PR mitigation shipped: 3-part scope claim + S2907 stress-test pointer added to all 4 docs.
- **Fold B (T1 zoom-out, `future_trigger`):** Systemic schema/handler drift trend candidate — 3/4 tools this batch. NOT yet a substrate-arc trigger. Escalation trigger recorded: if 3-5 subsequent sweep batches sustain ≥50% drift-find rate, promote to Playbook amendment (drift taxonomy + response rule) or dedicated cleanup arc.

Full session context: `docs/handoffs/SESSION_2906_SLICE_2_BATCH_2_ACTIONLESS_SWEEP.md`.

---

## S2907 open sequence

### Step 1 (RECOMMENDED FIRST ACTION) — Slice 2 batch 3 (small-actionful all-read-only stress test)

**S2907 recommended open: Slice 2 batch 3.** Closes S2906 T0 SIGN Fold A commitment. Pick one small-actionful (2-3 actions) all-read-only tool from remaining 17 `td_handlers_agents` untested list; add 3-4 more actionless / small-actionful tools to sustain 5-tools-per-batch accelerated pace.

**Concrete work:**
- Inspect action-enum size + safety class of small-actionful candidates: `bpaas_tool`, `davinci_tool`, `reasoning_engine_tool`, others as surface. Look for 2-3 actions all uniformly READ_ONLY (no mutation branches; no `_record_*` writes in downstream services).
- Reject candidates that would mix safety classes (would recreate the S2905 mixed-pattern situation without stated justification — 2/2 mixed sessions → materially closer to the ≥3 sessions lint trigger).
- Pick 4-5 tools total for the batch. Author T1b canonical template v1 docs with real handler-trace evidence in `## Covered actions` per action.
- Watch drift-find rate carefully — this is the second data point for the S2906 Fold B trend candidate. If drift rate stays high, escalate the ledger row from `future_trigger` to substrate arc candidate.

**Session cap:** target 1 session for batch of 5. Accelerated pace holding at 4/session since S2905.

### Alternative Step 1 candidates

- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid if Chris wants clean parity gate before more sweep sessions.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note (§ below, unchanged).

**Recommend Slice 2 batch 3** — closes S2906 T0 SIGN Fold A commitment (the small-actionful stress test); Phase 0 heading fixes + Slice 1.5b can bundle into subsequent S2908+ sessions.

### What's forbidden at S2907 (D6 MORATORIUM still in force)

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
- **Sweep-arc pace sustainability substrate arc** — ledger row 161. **CLOSED (mitigated) 2026-07-22 S2904 arc close.** S2905 (4 tools) + S2906 (4 tools) sustain the accelerated pace claim.
- **Response-level introspection field creep** — ledger row 162 (S2896). Same-PR mitigated; watch for pattern in other tools' response contracts.
- **Harness timestamp churn** — S2903 fold, `future_trigger`. Unchanged.
- **T1a FT-1 defaulted-tool action-set change lint** — S2903 substrate-arc-scope. Unchanged.
- **T1a FT-2 harness `soft_error` outcome value** — S2903 substrate-arc-scope. Unchanged.
- **T1b ZO-Q2 warn-noise escalation ladder** — S2904 substrate-arc-scope. Unchanged.
- **T1b ZO-Q7 automated corpus-counter helper** — S2904 substrate-arc-scope. Unchanged.
- **T1b ZO-Q8 structured-parse migration** — S2904 substrate-arc-scope. Unchanged.
- **S2905 metadata-pattern-selection lint** — substrate-arc-scope. Trigger: ≥3 sweep sessions mix TOOL_DEFAULTS + per-action `TOOL_ACTION_METADATA` without stated rule-based justification. **S2906 contribution: zero** (uniform-only batch). Distance to trigger: 2 more mixed sessions.
- **NEW — S2906 Ledger candidate: `get_body_vitals` schema empty properties / handler reads undeclared `systems` + `include_details`** — silent-parameter-invisibility class. Deferred (batch-scope discipline).
- **NEW — S2906 Ledger candidate: `web_search` schema declares only `query` / handler reads undeclared `limit` + `num_results`** — silent-parameter-expansion class. Deferred.
- **NEW — S2906 Ledger candidate: `get_system_alerts` schema-declared `limit` handler-ignored** — schema-declared-but-handler-ignored class. Deferred.
- **NEW — S2906 systemic drift trend candidate (Fold B)** — 3/4 tools this batch. `future_trigger`: if 3-5 subsequent sweep batches sustain ≥50% drift-find rate, promote to Playbook amendment (drift taxonomy + response rule) OR dedicated cleanup arc. Do NOT act off single batch data point.
- **S2905 Ledger candidate: `pilots_tool` undeclared `action=running`** — Unchanged.
- **S2905 Ledger candidate: `cost_telemetry_tool` silent `limit` cap at 50** — Unchanged.
- **S2905 Ledger candidate: `revenue_tracker_tool` `status='confirmed'` default drift** — Unchanged.
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
- **S2907+ batches 3-5:** 17 tools remaining. Target ~5 tools/batch at accelerated pace → ~4 more batches.

**Slice 3 — `td_handlers_core` (22 tools):** queued behind Slice 2.
**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arc CLOSED (S2900-S2904):** T1c ✅ S2901 → T1a ✅ S2902+S2903 → T1b ✅ S2904.

**Total remaining tools to close:** 68 (or ~96 counting partials + doc-unknowns). Post-substrate sweep pace observed: S2905=4, S2906=4. Extrapolated remaining ~12-16 sessions at 5-tools/batch accelerated pace.

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2906 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2906: zero A4 spend — pure sweep-batch execution.** A1 shipping spend was the S2906 batch 2 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2906)

See:
- **S2906 handoff (current):** `docs/handoffs/SESSION_2906_SLICE_2_BATCH_2_ACTIONLESS_SWEEP.md`
- **S2905 handoff:** `docs/handoffs/SESSION_2905_SLICE_2_BATCH_1_ACCELERATED_SWEEP.md`
- **S2904 handoff:** `docs/handoffs/SESSION_2904_T1B_TEMPLATE_EXTRACTION.md`
- **S2903 handoff:** `docs/handoffs/SESSION_2903_T1A_PHASE_2_METADATA_SEED.md`
- **S2902 handoff:** `docs/handoffs/SESSION_2902_T1A_AUTO_HARNESS_SCAFFOLD.md`
- **S2901 handoff:** `docs/handoffs/SESSION_2901_T1C_LOW_SIGNAL_AUDIT.md`
- **S2900 handoff:** `docs/handoffs/SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md`
- **S2900 substrate arc scoping (closed at S2904):** `docs/audits/pa_tools/substrate/S2900_substrate_arc_scoping.md` (parent) + `T1a_auto_harness.md` + `T1b_family_doc_templates.md` + `T1c_low_signal_audit.md` + `T1b_ship_shape_s2904.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2906 per-tool validation docs (new this session):**
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
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 30 non-substrate total)
- **S2906 workspace mirrors:** Rigby to author at S2907 open (both into Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`) — content mirror + ratification envelope per `feedback_rigby_writes_workspace_deliverables`.
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace above).

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
