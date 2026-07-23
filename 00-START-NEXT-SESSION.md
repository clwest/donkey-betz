# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2903 CLOSE → T1a fully DONE (Phase 1 S2902 + Phase 2 S2903) + S2904 opens with T1b template extraction (recommended) OR Phase 0 heading fixes (2026-07-22; picks up as S2904) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2903 close).** T1a Phase 2 metadata seed shipped in a single session. PR #3431 merged at `6237df49c` — 4 TOOL_DEFAULTS entries (ops_tool + kb_tool + agent_introspection_tool + repo_tool, all READ_ONLY) + 8 new TOOL_ACTION_METADATA records (ops_tool.focus_mode_update WRITE_GATED override + session_tool mixed-safety fan-out of 3 READ_ONLY / 4 MUTATION) + 12 new regression tests including the Rigby-Q3 `MutationVerbDefaultLeakTests` heuristic guard. Rigby wrote twin workspace mirror (content mirror `a9cbb5cd-af20-4660-8fd8-1ab1f79696cb` + ratification envelope `c5579bda-aa8c-414e-8deb-cfd16fe79541`, both in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`).

**T1a Phase 2 live results:**
- Harness READ_ONLY dispatch: **2 → 39** (up +37 from Phase 1 baseline)
- skipped_metadata_missing: **567 → 525** (down −42)
- Zero exceptions, zero error_captured outcomes at the ToolResult.ok level
- Parity gate: **8 mismatches unchanged from Phase 1** (Phase 0 doc-fix backlog — 8 close_with_short_note tools that need `## Covered actions` heading fixes)

**Rigby joint SIGN (S2903):** 4/4 AGREE after two Q1-Q4 mitigation rounds. Same-PR edits: (Q1) softened `ops_tool.focus_mode_update` note — auth enforcement location NOT verified at seed time; (Q3) added mutation-verb leak regression guard. Future triggers recorded: FT-1 defaulted-tool action-set change lint; FT-2 harness `soft_error` outcome for `ok=True` + `error_code` responses.

**PRs shipped this session:**
- u-d-b PR [#3431](https://github.com/clwest/donkey-betz-platform/pull/3431) — S2903 T1a Phase 2 metadata seed, merged at `6237df49c`
- u-d-b PR `<TBD>` — S2903 close cascade (handoff + 00-START refresh + wrapper pin bump)

**Ledger status:** Row 161 → T1c ✓ shipped S2901; T1a Phase 1 ✓ shipped S2902; **T1a Phase 2 ✓ shipped S2903 (this session — T1a fully DONE)**; T1b queued for S2904+. Row A `mitigated` (PR #3419 S2897). Row B `mitigated` (PR #3421 S2898). Row C `mitigated` (PR #3417 S2896). Row #29 `mitigated` (PR #3423 S2899). Deferred rows 27/28/30 unchanged.

**Zoom-out folds captured (per PLAYBOOK-6.10.7):**
- Fold — harness timestamp churn → `future_trigger`, NOT MITIGATED (110 of 116 per-tool JSONs diff only on `run_metadata.generated_at` per run). Trigger to act: harness becomes CI-invoked OR a PR needs to isolate content-change signal. Candidate fix: compare content excluding `generated_at` before writing; if unchanged, preserve prior timestamp.

Full session context: `docs/handoffs/SESSION_2903_T1A_PHASE_2_METADATA_SEED.md`.

---

## S2904 open sequence

### Step 1 (RECOMMENDED FIRST ACTION) — T1b template extraction

**S2904 recommended open: T1b template extraction (Row 161 substrate arc thread 3/3, arc close).** T1a is fully done — Phase 1 shipped the harness scaffold, Phase 2 authored real metadata producing 39 READ_ONLY dispatches. The v1 artifact schema is frozen (contract in `pa_tool_validate_harness.py` module docstring). T1b canonicalizes the per-tool validation-doc section structure with the real harness output to model on.

**T1b concrete work per parent §3:**
- Canonicalize per-tool validation-doc section structure (extract from S2796 6-section template + observed variation across the 22 shipped validation docs)
- Add ratchet-and-warn gap-map lint
- Ratchet fires on new-doc-authoring OR when a tool's covered-actions set changes
- Consumes the Phase 2 v1 output schema (frozen — safe to bind against)

**Session cap:** ~1-2 sessions per T1b scoping.

### Alternative Step 1 candidate — Phase 0 heading fixes

Defensible if Chris judges the parity gate should be clean before T1b template work. The 8 close_with_short_note tools (agent_introspection_tool / autopilot_tool / deliverable_tool / kb_tool / ops_tool / repo_tool / search_docs / session_tool) all need `## Covered actions` heading additions to their validation docs. Doc-only PR, would clear all 8 parity mismatches.

**Recommend T1b first** — the parity mismatches are informational (the harness records them but doesn't block). T1b template extraction is the arc-close work; heading fixes can bundle into the S2904+ sweep sessions as each tool gets picked up.

### What's forbidden at S2904 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- No re-negotiating substrate arc scope during T1b execution. Scope changes require substrate-arc-scoped SIGN.
- No v1 → v2 harness schema bump without substrate-arc-scoped SIGN. FT-2 (`soft_error` outcome) would need this; do NOT act on it without the SIGN cycle.
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
- **Sweep-arc pace sustainability substrate arc** — ledger row 161. **T1c ✓ shipped S2901 PR #3427 → T1a Phase 1 ✓ shipped S2902 PR #3429 → T1a Phase 2 ✓ shipped S2903 PR #3431. T1b queued for S2904+ (~1-2 sessions).** Total substrate-arc actual so far: **~2.5 sessions** (T1c 1 + T1a 1.5) vs ~4-5 initial estimate. Expected sweep acceleration ~50 sessions → ~10–15 sessions for remaining ~76 tools.
- **Response-level introspection field creep** — ledger row 162 (S2896). Same-PR mitigated; watch for pattern in other tools' response contracts.
- **Harness timestamp churn** — S2903 fold, `future_trigger`. Trigger to act: harness becomes CI-invoked OR a PR needs to isolate content-change signal.
- **T1a FT-1 defaulted-tool action-set change lint** — S2903 substrate-arc-scope. Trigger: pre-commit or CI shape becomes concrete.
- **T1a FT-2 harness `soft_error` outcome value** — S2903 substrate-arc-scope. Trigger: v1 → v2 schema bump signed off.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — deferred; trigger = operator/customer signals batched-lead triage ambiguity.
- **Applicability metadata pattern (entry #28)** — deferred; trigger = next integrity detector added.
- **Baseline lookback cap for HISTORICAL_BASELINE fields (entry #29)** — **MITIGATED at PR #3423 (S2899). Substrate available; operator has not flipped default None yet.**
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — deferred; trigger = embedding-pipeline lag becomes chronic (>3 sessions of persistent 100%-null embedding spikes).
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
- **S2896:** engineering ship (Row C mitigated).
- **S2897:** engineering ship (Row A mitigated).
- **S2898:** engineering ship (Row B mitigated).
- **S2899:** engineering ship (Row #29 Phase 2 lookback cap mitigated).
- **S2900:** Row 161 substrate arc OPENED (Chris D-verdict Option A). Engineering-first streak ends.
- **S2901:** T1c triage complete. `ops_tool` promoted to sweep queue; `agent_introspection_tool` + `kb_tool` + `search_docs` bucketed close_with_short_note (heading fix queued); `autopilot_tool` remains queued for Slice 1.5b post-T1a.
- **S2902:** T1a auto-harness scaffold shipped PR #3429. Harness enumerates 116 in-class tools. 2 READ_ONLY dispatched via seeded metadata. 567 skipped for missing metadata. 8 parity mismatches surfaced.
- **S2903 (this session):** T1a Phase 2 metadata seed shipped PR #3431. Harness dispatches jump 2 → 39 READ_ONLY. Rigby SIGN 4/4 AGREE after Q1/Q3 same-PR mitigations. T1a fully DONE.
- **Remainder:** Slice 1.5b (autopilot_tool mutations, ~1 session; timing depends on T1a WRITE_GATED classifier stability) + `ops_tool` sweep slot (promoted from partial to full sweep at T1c) + Phase 0 heading fixes for 8 close_with_short_note tools (agent_introspection_tool / autopilot_tool / deliverable_tool / kb_tool / ops_tool / repo_tool / search_docs / session_tool).

**Slice 2 — `td_handlers_agents` (25 tools):** queued behind T1b. Plus `workspace_tool` (T1c-promoted from false-positive validated_partial).
**Slice 3 — `td_handlers_core` (22 tools):** queued behind T1b.
**Slice 4 — `td_handlers_gateway` (17 tools):** queued behind T1b.
**Slice 5 — `tool_dispatcher` (14 tools):** queued behind T1b.

**Substrate arc in flight (S2900-):** T1c ✅ shipped S2901 → T1a ✅ shipped S2902+S2903 → T1b (queued for S2904+; ~1-2 sessions). Total actual so far: **~2.5 substrate sessions** (T1c 1 + T1a 1.5) vs ~4-5 initial estimate. Post-substrate sweep pace target: **~10-15 sessions** for remaining ~76 tools (vs ~50 at current-shape pace).

**Total remaining tools to close:** 76 (or ~104 counting partials + doc-unknowns).

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2903 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2903: zero A4 spend — pure substrate arc thread 2/3 execution (T1a Phase 2).** A1 shipping spend was the T1a Phase 2 metadata seed PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2903)

See:
- **S2903 handoff (current):** `docs/handoffs/SESSION_2903_T1A_PHASE_2_METADATA_SEED.md`
- **S2902 handoff:** `docs/handoffs/SESSION_2902_T1A_AUTO_HARNESS_SCAFFOLD.md`
- **S2901 handoff:** `docs/handoffs/SESSION_2901_T1C_LOW_SIGNAL_AUDIT.md`
- **S2900 handoff:** `docs/handoffs/SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md`
- **S2900 substrate arc scoping:** `docs/audits/pa_tools/substrate/S2900_substrate_arc_scoping.md` (parent) + `T1a_auto_harness.md` + `T1b_family_doc_templates.md` + `T1c_low_signal_audit.md` (populated at S2901)
- **S2899 handoff:** `docs/handoffs/SESSION_2899_EMBEDDING_BASELINE_LOOKBACK_CAP.md`
- **S2898 handoff:** `docs/handoffs/SESSION_2898_INTEGRITY_NULL_SPIKE_APPLICABILITY.md`
- **S2897 handoff:** `docs/handoffs/SESSION_2897_PROSPECTING_QUEUE_TITLE_FIX.md`
- **S2896 handoff:** `docs/handoffs/SESSION_2896_AUTOPILOT_HISTORY_WIPE_DIAGNOSTIC.md`
- **S2895 handoff:** `docs/handoffs/SESSION_2895_PA_TOOLS_SWEEP_SLICE_1_5A_AUTOPILOT_READ_ONLY.md`
- **S2894 handoff:** `docs/handoffs/SESSION_2894_PA_TOOLS_SWEEP_SLICE_1_BATCH_3.md`
- **S2893 handoff:** `docs/handoffs/SESSION_2893_PA_TOOLS_SWEEP_SLICE_1_BATCH_2.md`
- **S2892 handoff:** `docs/handoffs/SESSION_2892_PA_TOOLS_SWEEP_SLICE_1_BATCH_1.md`
- **S2891 handoff:** `docs/handoffs/SESSION_2891_BRIDGE_ACTIVITY_DIGEST.md`
- **S2890 handoff:** `docs/handoffs/SESSION_2890_OPS_TOOL_RECENT_BRIDGE_CALLS.md`
- **S2889 handoff:** `docs/handoffs/SESSION_2889_PLAYBOOK_V0_9_0_RATIFIED.md`
- **S2888 handoff:** `docs/handoffs/SESSION_2888_TD_ERROR_EXTRACTION.md`
- **S2887 handoff + audit:** `docs/handoffs/SESSION_2887_S2887_SIDE_STEP_GTM_AUDIT.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **Character-os UI → u-d-b reference sheet:** `/Users/donkeyking/Donkey_Betz/docs/2026-07-22_CHARACTER_OS_UI_TO_UDB_REFERENCE_SHEET.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 22 total after S2895)
- **Autopilot tool validation doc:** `docs/research/tools/validation/autopilot_tool_validation.md` (S2895; §3 + §5 + §7.1 reference the Row A/C shapes; S2896 + S2897 + S2898 + S2899 mitigations live in the handler + revenue.py + intelligence.py, not this doc)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
