# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2900 CLOSE → Row 161 substrate arc OPENED (Chris D-verdict Option A) + engineering-first streak ends + S2901 opens with T1c (fast-pass low-signal audit) as FIRST action (2026-07-22; picks up as S2901) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2900 close).** S2900 opened the PA tools sweep substrate arc after four consecutive engineering-first ships (S2896–S2899). Chris ratified Option A at S2900 turn 1. PR #3425 merged at `45f544970` — four new docs at `docs/audits/pa_tools/substrate/`: parent scoping + T1a auto-harness + T1b family-doc template + T1c low-signal audit. Rigby wrote twin workspace mirror (content mirror `cc7bd2c5-ef83-4c71-b2a3-76dee6f3ad97` + ratification envelope `3e9011cf-6780-4dbb-b413-6a96611d20f2`, both in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`; neither diagnostic-flagged).

**Arc shape (per Rigby SIGN + Chris "Ship it!" ratification):**

- **Thread order:** T1c first (fast pass, ~1 session; carves in-class boundary) → T1a (≤2 sessions, MVP-strict; Django mgmt command `pa_tool_validate_harness` + Action Metadata Map micro-thread) → T1b (1–2 sessions; ratchet-and-warn template posture).
- **Total substrate arc:** ~4–5 sessions. Expected sweep acceleration: **~50 sessions → ~10–15 sessions** for remaining ~76 tools if MVP discipline holds.
- **Anti-scope-creep:** if T1a grows to full HTTP/auth/async/pagination/golden-files, payoff is lost. Substrate-arc-scoped SIGN required for output-schema changes.

**PRs shipped this session:**
- u-d-b PR [#3425](https://github.com/clwest/donkey-betz-platform/pull/3425) — S2900 Row 161 substrate arc opened, merged at `45f544970`
- u-d-b PR `<TBD>` — S2900 close cascade (handoff + 00-START refresh + wrapper pin bump)

**Ledger status:** Row 161 → **OPENED as substrate arc.** Row A `mitigated` (PR #3419 S2897). Row B `mitigated` (PR #3421 S2898). Row C `mitigated` (PR #3417 S2896). Row #29 `mitigated` (PR #3423 S2899). Deferred rows 27/28/30 unchanged.

**Zoom-out folds:** None new this session. Rigby's five zoom-out concerns from the T1 SIGN (safety semantics / applicability metadata / fragmentation risk / metadata micro-thread / session-estimate blowup) were all folded into the arc shape pre-ship.

Full session context: `docs/handoffs/SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md`.

---

## S2901 open sequence

### Step 1 (MANDATORY FIRST ACTION — no menu, no defer) — T1c low-signal audit fast pass

**S2901 opens with T1c as the first thread of the substrate arc.** This is not a decision point — the sequencing is locked by Rigby SIGN B tweak (T1c first) + Chris "Ship it!" ratification at S2900 close. Do NOT present alternative engineering candidates until T1c ships.

**T1c scope** (see `docs/audits/pa_tools/substrate/T1c_low_signal_audit.md` for full detail):

- Fast triage of the ~14 low-signal tools (7 doc-unknown + 3 partial + 4 doc-only ops) plus explicit decision on the 44 `agent (via run_agent)` tools.
- Bucket each: `defer_indefinitely` / `promote_to_sweep` / `close_with_short_note` / `out_of_class_agent`.
- Fast-pass posture: ≤5 min per tool. If a tool needs more, default to `defer_indefinitely` with a `revisit_trigger` note.
- Action Metadata Map location decision: Candidate A (in-code, adjacent to `ToolDispatcher`, Rigby's lean) vs Candidate B (per-tool doc frontmatter). Default = Candidate A unless pivot-with-reason.

**T1c close criteria:**
1. Triage table populated for all 58 tools (14 low-signal + 44 agent-via-run_agent).
2. Action Metadata Map location decision recorded with rationale.
3. Bucket counts fed to T1a as scoping input.

**Session estimate:** ~1 session. May fit within a session that also opens T1a (auto-harness) if T1c completes cleanly in the first half.

### Step 2 — T1a (auto-harness build), ONLY after T1c ships

Do NOT open T1a until T1c triage table is populated + Action Metadata Map location decided. T1a MVP scope depends on knowing which tools remain in-class for the harness.

**T1a MVP boundaries (per parent §5 + T1a §2 anti-goals):** Django mgmt command `pa_tool_validate_harness`; in-process dispatch (not HTTP); READ_ONLY auto-executes only; per-action safety classifier; Action Metadata Map micro-thread. Session cap: ≤2 (scaffold + harden). If any of the anti-scope-creep watchlist items (async/pagination/golden-files/multi-auth/rate-limit/orchestration) come up, defer as substrate-follow-on rows.

### What's forbidden at S2901 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- No re-negotiating substrate arc scope during T1c/T1a/T1b execution. Scope changes require substrate-arc-scoped SIGN.
- No opening T1a before T1c completes. Sequencing locked at S2900 ratification.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — Chris pivoted to the sweep at S2892. If character-os side pings, stand by per pre-S2892 protocol.
- **Testing Discipline chapter candidacy** — ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — ledger row 159. Unchanged.
- **2-tier evidence template promotion** — ledger row 160. Triggers after 1-2 more large-surface sweeps adopt cleanly.
- **Sweep-arc pace sustainability substrate arc** — ledger row 161. **OPENED at S2900 as substrate arc (Chris D-verdict Option A ratified 2026-07-22).** Scoping: `docs/audits/pa_tools/substrate/S2900_substrate_arc_scoping.md`. Three threads: T1a auto-harness / T1b family-doc template / T1c low-signal audit. Execution order: T1c first (fast pass) → T1a (≤2 sessions, MVP-strict) → T1b (1–2 sessions). Total substrate-arc estimate: ~4–5 sessions; expected sweep acceleration ~50 sessions → ~10–15 sessions for remaining ~76 tools.
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
- **S2900 (this session):** **Row 161 substrate arc OPENED (Chris D-verdict Option A).** Engineering-first streak ends.
- **All 3 S2895-surfaced Ledger rows + one deferred zoom-out row + Row 161 now closed or opened.**
- **Remainder:** Slice 1.5b (autopilot_tool mutations, ~1 session) + 4 doc/unknown/partial ops tools (`agent_introspection_tool`, `kb_tool`, `search_docs`, `ops_tool`, ~1-2 sessions). Slice 1.5b timing depends on T1a WRITE_GATED classifier stability.

**Slice 2 — `td_handlers_agents` (25 tools):** queued behind substrate arc.
**Slice 3 — `td_handlers_core` (22 tools):** queued behind substrate arc.
**Slice 4 — `td_handlers_gateway` (17 tools):** queued behind substrate arc.
**Slice 5 — `tool_dispatcher` (14 tools):** queued behind substrate arc.

**Substrate arc in flight (S2900-):** T1c (S2901, ~1 session) → T1a (~2 sessions) → T1b (~1-2 sessions). Total: ~4-5 substrate sessions. Post-substrate sweep pace target: **~10-15 sessions** for remaining ~76 tools (vs ~50 at current-shape pace).

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2900 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2900: zero A4 spend — pure substrate arc opening.** A1 shipping spend was the substrate arc scoping PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2900)

See:
- **S2900 handoff (current):** `docs/handoffs/SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md`
- **S2900 substrate arc scoping:** `docs/audits/pa_tools/substrate/S2900_substrate_arc_scoping.md` (parent) + `T1a_auto_harness.md` + `T1b_family_doc_templates.md` + `T1c_low_signal_audit.md`
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
