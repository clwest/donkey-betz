# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2899 CLOSE → embedding_text baseline lookback cap shipped (Ledger Row #29 → `mitigated`) + FOURTH consecutive engineering-first ship + explicit trigger recorded: S2900 opens with Row 161 substrate-arc gate as FIRST action regardless of queued candidates (2026-07-22; picks up as S2900) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2899 close).** S2899 was the FOURTH consecutive engineering-first ship. PR #3423 merged at `1fd68a49b` — `autopilot_tool.integrity_null_spike_scan` now has an optional per-field lookback cap for `HISTORICAL_BASELINE` fields. Default `None` preserves S2898 Phase 1 all-time semantics (zero behavior change at ship); operators can flip `HISTORICAL_BASELINE_LOOKBACK_DAYS['embedding_text']` to `30`/`90` when a pipeline lag becomes chronic and stale historical populates start dominating the baseline. Closes Ledger Row #29 (sticky-semantics risk Rigby surfaced in S2898 Q4 zoom-out).

**Design shape (per Rigby SIGN D-verdict: AGREE):**

```python
HISTORICAL_BASELINE_LOOKBACK_DAYS = {
    'embedding_text': None,   # None = all-time (S2898 Phase 1 default)
                              # int N = last N days rolling window
}
```

Query invariant preserved: chained `.filter(created_at__gte=cutoff)` before `.values(...).distinct()` when lookback is set. Still O(1) queries per HISTORICAL_BASELINE field (locked by `test_query_count_is_bounded` via `assertNumQueries=2`). Return dict adds `baseline_lookback_days` scoped to HISTORICAL_BASELINE fields only.

**PRs shipped this session:**
- u-d-b PR [#3423](https://github.com/clwest/donkey-betz-platform/pull/3423) — S2899 embedding_text baseline lookback cap (Ledger Row #29), merged at `1fd68a49b`
- u-d-b PR `<TBD>` — S2899 close cascade (handoff + 00-START refresh + wrapper pin bump)

**Gap-map ratchet:** unchanged (no sweep batch this session).

**Ledger status:** Row A `mitigated` (PR #3419 S2897). Row B `mitigated` (PR #3421 S2898). Row C `mitigated` (PR #3417 S2896). **Row #29 MITIGATED at PR #3423 (S2899).** All S2895 rows + one deferred zoom-out row closed. Deferred rows 27/28/30 unchanged — trigger criteria unchanged.

**Zoom-out folds:** None new this session. Rigby's Q4 concerns (knob proliferation, decay-vs-truth semantics) already mitigated in the shipped design.

Full session context: `docs/handoffs/SESSION_2899_EMBEDDING_BASELINE_LOOKBACK_CAP.md`.

---

## S2900 open sequence

### Step 1 (MANDATORY FIRST ACTION — no menu, no defer) — Row 161 substrate-arc gate DECISION

**Chris's explicit trigger recorded at S2899 ratification:** at S2900 open, Row 161 is the FIRST decision regardless of what engineering candidates are queued. Preserves the engineering-bias benefits of the S2896–S2899 streak while preventing the pattern from silently supplanting the sweep-pace substrate-arc gate.

**Four consecutive Option-C picks now (S2896 + S2897 + S2898 + S2899).** Chris has picked engineering ships four sessions in a row. Now the substrate question is due for explicit resolution — either commit to Option A, commit to Option B, or re-ratify Option C with eyes-open acknowledgement that the pattern is the strategy.

Same three options carried forward:

- **Option A (Rigby lean) — Open a dedicated substrate arc.** Auto-harness build + family-doc template extraction + low-signal tool audit. Slows sweep pace short-term; expected to close remaining Slice 1-5 scope in ~10-15 sessions instead of ~50.
- **Option B — Push through Slice 1 close-out (~4-5 more current-shape sessions), THEN re-evaluate.** Closes Slice 1.5b (`autopilot_tool` mutations) + 4 doc/unknown/partial ops tools.
- **Option C — Another engineering session.** Do NOT open without explicit re-ratification given the four-consecutive-C-picks pattern. If Chris re-ratifies, priority candidates listed in Step 2 below.

**Do not skip Step 1. Do not present Step 2 candidates until Chris ratifies a Step 1 option.**

### Step 2 — Net-new engineering candidates (ONLY if Chris re-ratifies Option C after Step 1)

Priority order for S2900 if Option C:

1. **DBZ enforcement doc-clarity annotation** — `enforcement_report` output should include hysteresis-oscillation shape so operators reading multiple downgrade_set/cleared pairs don't misread as "enforcer flapping". (S2895 T2 revised discussion.)
2. **Continue S2894 Ledger rows** — `messaging_tool.send` action (or in-thread-pattern schema note), `zoom_out_tool.record_fold` action (or JSONL→workspace-deliverable mirror).
3. **PLAYBOOK-3.2.3/3.2.4 compliance sweep** — carried from S2891.
4. **New Ledger Row #27 arc trigger watch** — batched-items structural fix (per-item lead expansion). Deferred until operator/customer signals batched-lead triage ambiguity.
5. **Rows #28/#30 arc trigger watch** — applicability metadata pattern (fold to broader integrity substrate) + ingest-vs-pipeline separation (embedding-pipeline health dashboard). Triggered when next integrity detector added or embedding lag becomes chronic.

### What's forbidden at S2900 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — Chris pivoted to the sweep at S2892. If character-os side pings, stand by per pre-S2892 protocol.
- **Testing Discipline chapter candidacy** — ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — ledger row 159. Unchanged.
- **2-tier evidence template promotion** — ledger row 160. Triggers after 1-2 more large-surface sweeps adopt cleanly.
- **Sweep-arc pace sustainability substrate arc** — ledger row 161. **Decision point at S2900 open (see Step 1 above); MANDATORY, not deferrable.**
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
- **S2899 (this session):** engineering ship (Row #29 Phase 2 lookback cap mitigated).
- **All 3 S2895-surfaced Ledger rows + one deferred zoom-out row now closed.**
- **Remainder:** Slice 1.5b (autopilot_tool mutations, ~1 session) + 4 doc/unknown/partial ops tools (`agent_introspection_tool`, `kb_tool`, `search_docs`, `ops_tool`, ~1-2 sessions)

**Slice 2 — `td_handlers_agents` (25 tools, ~7 sessions):** queued
**Slice 3 — `td_handlers_core` (22 tools, ~6 sessions):** queued
**Slice 4 — `td_handlers_gateway` (17 tools, ~5 sessions):** queued
**Slice 5 — `tool_dispatcher` (14 tools, ~4 sessions):** queued

**Total remaining tools to close (before Row 161 substrate arc):** 76 (or ~104 counting partials + doc-unknowns).
**Estimated total sessions remaining at current-shape pace:** ~50 (Row 161 triggers this concern — decision MANDATORY at S2900 open).

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2899 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2899: zero A4 spend — pure engineering.** A1 shipping spend was the Row #29 fix PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2899)

See:
- **S2899 handoff (current):** `docs/handoffs/SESSION_2899_EMBEDDING_BASELINE_LOOKBACK_CAP.md`
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
