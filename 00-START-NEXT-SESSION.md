# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2901 CLOSE → T1c low-signal audit SHIPPED (Row 161 substrate arc thread 1/3) + S2902 opens with T1a (auto-harness scaffold) as FIRST action (2026-07-22; picks up as S2902) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2901 close).** T1c executed as first thread of the Row 161 substrate arc. PR #3427 merged at `e92bd807c` — populated triage table (54 unique rows: 10 Group A + 44 Group B), Action Metadata Map location decision (Candidate A confirmed), T1a MVP surface input, four zoom-out folds captured. Rigby wrote twin workspace mirror (content mirror `c9c0d8e2-41c3-4be5-8a44-8d55e78f6ca1` + ratification envelope `40373e35-d063-4033-920e-e7d02b82aa7b`, both in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`).

**T1c bucket totals:**
- `close_with_short_note`: 8 (7 doc-unknown tools + `autopilot_tool` — Slice 1.5b already queued)
- `promote_to_sweep`: 2 (`ops_tool` 18/20 unverified; `workspace_tool` false-positive validated_partial)
- `defer_indefinitely`: 0
- `out_of_class_agent`: 44 (all agent-via-run_agent tools)

**T1a MVP surface post-T1c:** 96 in-class tools for harness (94 untested + 2 T1c-promoted); 45 out-of-harness (44 agent_via_run_agent + 1 run_agent meta).

**PRs shipped this session:**
- u-d-b PR [#3427](https://github.com/clwest/donkey-betz-platform/pull/3427) — S2901 T1c low-signal audit, merged at `e92bd807c`
- u-d-b PR `<TBD>` — S2901 close cascade (handoff + 00-START refresh + wrapper pin bump)

**Ledger status:** Row 161 → OPENED as substrate arc (S2900); thread 1/3 (T1c) shipped this session. Row A `mitigated` (PR #3419 S2897). Row B `mitigated` (PR #3421 S2898). Row C `mitigated` (PR #3417 S2896). Row #29 `mitigated` (PR #3423 S2899). Deferred rows 27/28/30 unchanged.

**Zoom-out folds captured (per PLAYBOOK-6.10.7):**
- Fold A — `run_agent` rewrite exclusion at harness boundary → `future_trigger`, T1a Phase 1
- Fold B — schema↔doc parity check required for close_with_short_note tools → `future_trigger`, T1a Phase 0
- Fold C — gap-map snapshot pinning → `same_pr_mitigatable`, closed inline at T1c §7.0 (HEAD `7891ee9c` pinned)
- Fold D — `validated (full)` doc-status ≠ runtime confidence → `future_trigger`, T1a §2 anti-goals

Full session context: `docs/handoffs/SESSION_2901_T1C_LOW_SIGNAL_AUDIT.md`.

---

## S2902 open sequence

### Step 1 (MANDATORY FIRST ACTION — no menu, no defer) — T1a auto-harness scaffold phase

**S2902 opens with T1a as thread 2/3 of the Row 161 substrate arc.** This is not a decision point — sequencing is locked by S2900 Chris D-verdict Option A ratification. T1c completed at S2901 unblocks T1a per the arc shape. Do NOT present alternative engineering candidates until T1a scaffold ships.

**T1a scope** (see `docs/audits/pa_tools/substrate/T1a_auto_harness.md` for full detail + T1c-inherited scope inputs):

**MVP boundaries (locked at parent §5 + T1a §2 anti-goals):**
- Django mgmt command `pa_tool_validate_harness`
- In-process dispatch (not HTTP)
- READ_ONLY auto-executes only; per-action safety classifier
- Action Metadata Map micro-thread: create `core/services/tool_action_metadata.py` with `TOOL_ACTION_METADATA` dict keyed by `(tool_name, action)`, fields `safety_class` / `applicability` / `notes`
- Session cap: **≤2** (scaffold + harden)

**T1c-inherited scope inputs (fold carry-forward):**
- **96 in-class tools** for harness (94 untested + 2 T1c-promoted: `ops_tool` + `workspace_tool`)
- **Fold A** — exclude `run_agent`-rewritten calls from harness surface; add Phase 1 regression test verifying rewrite doesn't enter validation queue
- **Fold B** — Phase 0 doc-heading-fix pass must include `--check-doc-schema-parity` gate; auto-escalate mismatches to sweep
- **Fold D** — harness verifies all in-class tools regardless of doc-status; add to T1a §2 anti-goals at scaffold time
- **Fold C already closed** at T1c §7.0 (gap-map HEAD `7891ee9c` pinned as coverage-math baseline)

**Anti-scope-creep watchlist (parent §5):** async / pagination / golden-files / multi-auth / rate-limit / orchestration. If any surface, defer as substrate-follow-on ledger rows; **substrate-arc-scoped SIGN required** for output-schema changes.

**T1a close criteria:**
1. `pa_tool_validate_harness` mgmt command runnable end-to-end against the 96 in-class tools' READ_ONLY actions.
2. `core/services/tool_action_metadata.py` exists with `TOOL_ACTION_METADATA` dict populated for at least the READ_ONLY action surface.
3. Phase 0 doc-heading-fix for the 8 close_with_short_note tools shipped OR explicitly deferred to a separate PR (Rigby's preference at T1a open).
4. Fold A regression test + Fold B parity check gate landed.

### Step 2 — T1b (family-doc template), ONLY after T1a completes

Do NOT open T1b until T1a scaffold ships AND at least one harden pass has surfaced whether the auto-harness produces per-tool docs cleanly. T1b scope depends on T1a's actual output shape.

### What's forbidden at S2902 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- No re-negotiating substrate arc scope during T1a/T1b execution. Scope changes require substrate-arc-scoped SIGN.
- No opening T1b before T1a completes. Sequencing locked at S2900 ratification.
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
- **Sweep-arc pace sustainability substrate arc** — ledger row 161. **OPENED at S2900 as substrate arc (Chris D-verdict Option A ratified 2026-07-22).** Scoping: `docs/audits/pa_tools/substrate/S2900_substrate_arc_scoping.md`. Three threads: T1a auto-harness / T1b family-doc template / T1c low-signal audit. Execution order: **T1c ✅ shipped S2901 PR #3427** (54-row triage + Candidate A metadata location + 4 folds captured) → T1a (S2902 next; ≤2 sessions; MVP-strict; 96 in-class tools) → T1b (after T1a; 1-2 sessions). Total substrate-arc estimate: ~4–5 sessions; remaining ~3-4 sessions. Expected sweep acceleration ~50 sessions → ~10–15 sessions for remaining ~76 tools.
- **Response-level introspection field creep** — ledger row 162 (S2896). Same-PR mitigated; watch for pattern in other tools' response contracts.
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
- **S2901 (this session):** T1c triage complete. `ops_tool` promoted to sweep queue; `agent_introspection_tool` + `kb_tool` + `search_docs` bucketed close_with_short_note (heading fix at T1a Phase 0); `autopilot_tool` remains queued for Slice 1.5b post-T1a.
- **Remainder:** Slice 1.5b (autopilot_tool mutations, ~1 session; timing depends on T1a WRITE_GATED classifier stability) + `ops_tool` sweep slot (promoted from partial to full sweep at T1c) + Phase 0 heading fixes for 3 ops tools (`agent_introspection_tool` / `kb_tool` / `search_docs`).

**Slice 2 — `td_handlers_agents` (25 tools):** queued behind substrate arc. Plus `workspace_tool` (T1c-promoted from false-positive validated_partial).
**Slice 3 — `td_handlers_core` (22 tools):** queued behind substrate arc.
**Slice 4 — `td_handlers_gateway` (17 tools):** queued behind substrate arc.
**Slice 5 — `tool_dispatcher` (14 tools):** queued behind substrate arc.

**Substrate arc in flight (S2900-):** T1c ✅ shipped S2901 → T1a (S2902 next; ~≤2 sessions) → T1b (~1-2 sessions). Total: ~4-5 substrate sessions; ~3-4 remaining. Post-substrate sweep pace target: **~10-15 sessions** for remaining ~76 tools (vs ~50 at current-shape pace).

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2901 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2901: zero A4 spend — pure substrate arc thread 1/3 execution.** A1 shipping spend was the T1c triage PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2901)

See:
- **S2901 handoff (current):** `docs/handoffs/SESSION_2901_T1C_LOW_SIGNAL_AUDIT.md`
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
