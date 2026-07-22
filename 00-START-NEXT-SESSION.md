# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2893 CLOSE → PA tools sweep Slice 1 Batch 2 shipped (4 validation docs, `untested`→`validated_full`) + Chris Option-C reslate deferred `autopilot_tool` to dedicated Slice 1.5 + zoom-out fold row 158 persisted (2026-07-22; picks up as S2894) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2893 close).** S2893 shipped Batch 2 of Slice 1 (`td_handlers_ops`). Chris ratified Option C at Turn 2: reslate `autopilot_tool` (~130 actions) to its own dedicated Slice 1.5 rather than trying to fit it in a normal 4-tool batch. Batch 2 became governor_tool + ops_digest_tool + scheduled_tasks_tool + spider_status_tool (last one pulled forward from Batch 3). 15 live actions dispatched by Rigby; 14 PASS + 1 canary-excluded (governor_tool.reset_breaker — no breakers tripped). 3 substantive Ledger candidates surfaced.

**PRs shipped this session:**
- u-d-b PR `<TBD>` — S2893 Slice 1 batch 2 (4 validation docs + PA_TOOL_AUDIT.md regen + PA_TOOLS_GAP_MAP.md regen + zoom-out fold row 158 + handoff)
- u-d-b PR `<TBD>` — S2893 close cascade (wrapper pin bump)

**Gap-map ratchet (before → after this session):**
```
validated_full:   7 → 11 (+4: governor_tool, ops_digest_tool, scheduled_tasks_tool, spider_status_tool)
untested:       100 → 96 (-4)
per_tool_docs:   16 → 20
per_tool_docs_with_covered_actions:  8 → 12
```

**Ledger candidates routed to Rigby at close (Rigby Tool Gap Ledger deliverable `5c84e75a-…`):**
1. `governor_tool.status` intermittent inconsistency with `.coverage` on `circuit_breakers_tripped` — cache / eventual-consistency artifact confirmed by Rigby re-check.
2. `governor_tool` `reason="aligned"` conflates mission-match vs fail-open — 80 agents show `matched via fail_open: None` in detail; no way to distinguish genuinely-governed from merely-permitted.
3. `ops_digest_tool.generate` missing staleness heuristic on `autopilot.last_cycle` — 15-day-stale timestamp surfaced raw, not flagged in `degraded_fields`.

**Marginal/pattern-matching (folded into existing S2892 Ledger #1 rather than new rows):** schema-vs-handler required-arg drift on governor_tool.test/reset_breaker, ops_digest_tool.post, spider_status_tool.history/search/detail.

**Zoom-out fold row 158** — `pa_tools_sweep_batch_cadence_outcome_gate`, `future_trigger`. Trigger: 2 consecutive future batches ship pure docs with zero engineering payload (zero Ledger candidates, zero schema fixes, zero observability deltas). If that fires, promote the per-batch outcome gate to the sweep methodology explicitly.

Full session context: `docs/handoffs/SESSION_2893_PA_TOOLS_SWEEP_SLICE_1_BATCH_2.md`.

---

## S2894 open sequence

### Step 1 (FIRST THING) — PA tools sweep: Slice 1 batch 3 of `td_handlers_ops`

**Path B is the ratified multi-week arc.** Slice 1 (`td_handlers_ops`) opened at S2892; Batches 1 + 2 shipped. Batch 3 opens at S2894.

**Batch 3 lineup:** `workspace_budget_tool` + 2-3 more from the remaining `td_handlers_ops` untested set. Do NOT include `autopilot_tool` — it is reserved for dedicated Slice 1.5 (S2895 or later, 2 sessions estimated).

Pick the additional tools by re-reading `docs/audits/PA_TOOLS_GAP_MAP.md` "td_handlers_ops" triage slice at S2894 open.

**Execution shape (repeat of S2892/S2893 pattern):**
1. Enumerate schemas + register sites for the 3-4 selected tools.
2. Joint SIGN with Rigby before dispatch — pressure-test on which actions are mutating, what state each requires, whether any need a canary agent / workspace / anything.
3. Rigby exercises every action live. Report tool_runs.
4. Claude writes validation docs (S2796 shape with bare `## Covered actions` heading + §5a Mutation containment section per S2893 evolution).
5. Regenerate `docs/PA_TOOL_AUDIT.md` + `docs/audits/PA_TOOLS_GAP_MAP.md`.
6. Ship PR.

### Step 2 — Net-new engineering candidates (per feedback_engineering_bias_over_audit)

**Path B does NOT preempt engineering-bias.** Still surface 1-3 net-new candidates at any natural pause. Priority order for S2894 (unchanged from S2893):

1. **`diagnostics_tool.schema_handler_diff` placeholder → implementation** — Rigby self-introspection tool. Would let her answer "what's the current schema-handler drift?" from chat, closes S2892 Ledger candidate #4.
2. **Ship one S2893 Ledger row** — pick between: (a) `governor_tool.status` cache/consistency fix (single-file, small), (b) `governor_tool.reason` fail-open surfacing (small), (c) `ops_digest_tool` autopilot staleness heuristic (small). Any of these would satisfy fold-158 outcome-gate for S2894.
3. **Ship one S2892 Ledger row** — `agent_memory_tool` schema tightening or `agent_control_tool.audit_log` rename/history model. Still open.
4. **PLAYBOOK-3.2.3/3.2.4 compliance sweep** — carried from S2891.

### What's forbidden at S2894 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — Chris pivoted to the sweep. If character-os side pings, stand by per pre-S2892 protocol.
- **Testing Discipline chapter candidacy** — ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — ledger row 158 (new this session). Trigger: 2 consecutive batches ship pure docs with zero engineering payload.
- **R1 fleet reject-mode flip** — deferred.
- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind sweep.
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits (`requested_model_id`, `was_policy_reroute`) — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.

---

## Sweep progress tracker (Path B ratified S2892, reslated S2893)

**Slice 1 — `td_handlers_ops` (10 tools total):**
- Batch 1 (S2892): agent_control_tool, agent_memory_tool, heartbeat_history_tool, infra_health_tool ✓
- Batch 2 (S2893, this session): governor_tool, ops_digest_tool, scheduled_tasks_tool, spider_status_tool ✓
- Batch 3 (S2894): workspace_budget_tool + 2-3 more (pick from remaining `td_handlers_ops` untested set; DO NOT include autopilot_tool)
- Slice 1.5 (post-Slice-1 close): autopilot_tool read-only sweep + autopilot_tool mutations sweep (2 sessions estimated)

**Slice 2 — `td_handlers_agents` (25 tools, ~7 sessions):** queued
**Slice 3 — `td_handlers_core` (22 tools, ~6 sessions):** queued
**Slice 4 — `td_handlers_gateway` (17 tools, ~5 sessions):** queued
**Slice 5 — `tool_dispatcher` (14 tools, ~4 sessions):** queued

**Total remaining tools to close:** 92 after this batch.
**Estimated total sessions remaining in arc:** ~25 (was ~24; +1 for autopilot reslate to Slice 1.5).

**Informative per-batch outcome check (S2893 fold-158 hybrid — Rigby SIGN Path C):** In each batch, sanity-check that the sweep produced at least one concrete outcome (Ledger candidate / schema fix / observability delta). If not, tighten scope or reslate next batch to avoid ceremony drift. Informative, not enforcement — row 158 remains `future_trigger`.

---

## Autopilot Slice 1.5 pre-commit note (per S2893 Rigby SIGN zoom-out #4)

When `autopilot_tool` is eventually swept, the template MUST differ from the batch shape used through Slice 1:

1. **Read-only first sweep** — exercise ~110 read-only actions (all `_report`, `_queue`, `_forecast`, `_scan`, `status`, `history`, `dry_run_report`). Ship `validated_partial`.
2. **Sandboxed / explicitly gated mutations second sweep** — exercise ~20 mutating actions with extra scrutiny on `dry_run` + `confirm` two-factor gating (already present on `security_containment_plan` per S1228 PR-A), audit trails, `ttl_hours` expiries.

Do NOT try to sweep both categories in one session.

---

## Two-Claude concurrency safety envelope (still active from S2889)

Rulebook: `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`.

- Each terminal uses its own Rigby conversation pin — no state collision.
- Different repos, different branches — no git collision.
- **Watch:** character-os Docker postgres previously captured u-d-b's `:5433` via IPv6 wildcard (S2885). `USE_PGBOUNCER=0` still in force in both `.env` files. If character-os side runs `docker compose up`, verify port ownership before restarting u-d-b.
- Shared u-d-b PA endpoint (`http://localhost:8000`) — both Claudes may drive it; surface handles concurrent conversations.

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2893 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2893: zero A4 spend — pure engineering + governance.** A1 shipping spend was the sweep PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2893)

See:
- **S2893 handoff (current):** `docs/handoffs/SESSION_2893_PA_TOOLS_SWEEP_SLICE_1_BATCH_2.md`
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
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated)

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
