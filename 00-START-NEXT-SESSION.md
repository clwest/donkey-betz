# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2892 CLOSE → PA tools systematic sweep (Path B) opened + Slice 1 batch 1 of `td_handlers_ops` shipped (4 validation docs, `untested`→`validated_full`) + zoom-out fold row 157 persisted (2026-07-22; picks up as S2893) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2892 close).** S2892 opened the systematic PA tools validation sweep (Path B) at Chris's direction. Slice 1 (`td_handlers_ops`, 10 untested tools) opened with batch 1: 4 tools exercised live via Rigby (14 total actions), 4 validation docs shipped, gap-map ratchet applied. Two Ledger-worthy gaps + one semantic-signal anomaly surfaced.

**PRs shipped this session:**
- u-d-b PR `<TBD>` — S2892 Slice 1 batch 1 (4 validation docs + PA_TOOL_AUDIT.md regen + PA_TOOLS_GAP_MAP.md regen + zoom-out fold row 157)
- u-d-b PR `<TBD>` — S2892 close cascade

**Gap-map ratchet (before → after this session):**
```
validated_full:   3 → 7  (+4: agent_control_tool, agent_memory_tool, heartbeat_history_tool, infra_health_tool)
untested:       104 → 100  (-4)
per_tool_docs:   12 → 16
per_tool_docs_with_covered_actions:  4 → 8
```

**Ledger candidates routed to Rigby at close (Ledger deliverable `5c84e75a-…`):**
1. `agent_memory_tool.list/.knowledge` require `agent_name` at handler; schema doesn't declare it required — invalid_params drift.
2. `agent_control_tool.audit_log` is misnamed — returns current state per agent, not append-only history. `AgentControlEntry` is update_or_create; block→unblock overwrites the row. Rename schema action to `recent` OR implement `AgentControlEventLog` append-only rows.
3. `agent_control_tool.block` doesn't validate `agent_name` against AGENT_MAP — silent-persist risk. Optional soft-check.
4. Inventory schema-count drift: inventory says 113 schemas + 156 handlers; live is 117 + 160. Regen cadence lapsed.
5. Latency reporting inconsistency across handlers.

**Semantic-signal candidates (NOT tool defects; operational-signal work):**
- Heartbeat score collapsed to 87.5 flat across 137 heartbeats/24h — one component perpetually degrades (7/8 = 87.5). Which component?
- Redis hit_rate_pct 59.5% (below 80%+ target).
- Postgres longest_query_secs 2302 (~38 min stuck query).
- Postgres cache_hit_ratio_pct 62.51% (below 90%+ target).
- Redis blocked_clients=5.

**Zoom-out fold row 157** — `sweep_shape_doc_only_defers_semantic_assertions`, `future_trigger`. Trigger: 2+ later validation docs prove to have missed a semantic defect a per-action assertion would have caught, OR Chris explicitly asks for semantic-correctness coverage (e.g. reacting to an incident).

Full session context: `docs/handoffs/SESSION_2892_PA_TOOLS_SWEEP_SLICE_1_BATCH_1.md`.

---

## S2893 open sequence

### Step 1 (FIRST THING) — PA tools sweep: Slice 1 batch 2 of `td_handlers_ops`

**Path B is the ratified multi-week arc.** Slice 1 (`td_handlers_ops`) has 3 batches total; batch 1 shipped this session. Batch 2 opens at S2893.

**Batch 2 lineup:** 4 tools, one session (matches S2892 pace).
1. `autopilot_tool` — schema at `pa_tool_schemas.py`, handler at `td_handlers_ops.py`
2. `governor_tool` — per-agent execution budget controls
3. `ops_digest_tool` — daily/weekly/hourly digest rollups
4. `scheduled_tasks_tool` — PeriodicTask surface

**Execution shape (repeat of S2892 T1 pattern):**
1. Enumerate schemas + register sites.
2. Joint SIGN with Rigby before dispatch — pressure-test on which actions are mutating, what state each requires, whether any of these need a canary agent / workspace / anything.
3. Rigby exercises every action live. Report tool_runs.
4. Claude writes 4 validation docs (S2796 shape with `## Covered actions` heading).
5. Regenerate `docs/PA_TOOL_AUDIT.md` + `docs/audits/PA_TOOLS_GAP_MAP.md`.
6. Ship PR.

### Step 2 — Net-new engineering candidates (per feedback_engineering_bias_over_audit)

**Path B does NOT preempt engineering-bias.** Still surface 1-3 net-new candidates at any natural pause. Priority order for S2893:

1. **`diagnostics_tool.schema_handler_diff` placeholder → implementation** — Rigby self-introspection tool. Would let her answer "what's the current schema-handler drift?" from chat, closes Ledger candidate #4 (inventory drift detection).
2. **Ledger row shipment from S2892 sweep candidates #1 + #2** — agent_memory_tool schema tightening + agent_control_tool.audit_log rename or history model. Small-scope engineering PRs.
3. **PLAYBOOK-3.2.3/3.2.4 compliance sweep** — carried from S2891, still open.
4. **Explicit `bridge_tool` marker on character-os side** — cross-repo; deferred pending character-os side pause.
5. **LLMCallLog cost join for bridge calls** — deferred, requires joinability verification.

### What's forbidden at S2893 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC). Rejected at S2887.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — Chris pivoted to the sweep. If character-os side pings, stand by per pre-S2892 protocol.
- **Testing Discipline chapter candidacy** — ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — ledger row 157 (new this session). Unchanged.
- **R1 fleet reject-mode flip** — deferred.
- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind sweep.
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits (`requested_model_id`, `was_policy_reroute`) — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (10 tools):**
- Batch 1 (this session): agent_control_tool, agent_memory_tool, heartbeat_history_tool, infra_health_tool ✓
- Batch 2 (next): autopilot_tool, governor_tool, ops_digest_tool, scheduled_tasks_tool
- Batch 3: spider_status_tool, workspace_budget_tool (+ 1 slack for surprises)

**Slice 2 — `td_handlers_agents` (25 tools, ~7 sessions):** queued
**Slice 3 — `td_handlers_core` (22 tools, ~6 sessions):** queued
**Slice 4 — `td_handlers_gateway` (17 tools, ~5 sessions):** queued
**Slice 5 — `tool_dispatcher` (14 tools, ~4 sessions):** queued

**Total remaining tools to close:** 96 after this batch.
**Estimated total sessions remaining in arc:** ~24.

---

## Two-Claude concurrency safety envelope (still active from S2889)

Rulebook: `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`.

- Each terminal uses its own Rigby conversation pin — no state collision.
- Different repos, different branches — no git collision.
- **Watch:** character-os Docker postgres previously captured u-d-b's `:5433` via IPv6 wildcard (S2885). `USE_PGBOUNCER=0` still in force in both `.env` files. If character-os side runs `docker compose up`, verify port ownership before restarting u-d-b.
- Shared u-d-b PA endpoint (`http://localhost:8000`) — both Claudes may drive it; surface handles concurrent conversations.

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2892 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2892: zero A4 spend — pure engineering + governance.** A1 shipping spend was the sweep PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2892)

See:
- **S2892 handoff (current):** `docs/handoffs/SESSION_2892_PA_TOOLS_SWEEP_SLICE_1_BATCH_1.md`
- **S2891 handoff:** `docs/handoffs/SESSION_2891_BRIDGE_ACTIVITY_DIGEST.md`
- **S2890 handoff:** `docs/handoffs/SESSION_2890_OPS_TOOL_RECENT_BRIDGE_CALLS.md`
- **S2889 handoff:** `docs/handoffs/SESSION_2889_PLAYBOOK_V0_9_0_RATIFIED.md`
- **S2888 handoff:** `docs/handoffs/SESSION_2888_TD_ERROR_EXTRACTION.md`
- **S2887 handoff + audit:** `docs/handoffs/SESSION_2887_S2887_SIDE_STEP_GTM_AUDIT.md`
- **S2886 handoff:** `docs/handoffs/SESSION_2886_CORE_CRITICALITY_FIRST_ERROR_ENVELOPE.md`
- **S2885 handoff:** `docs/handoffs/SESSION_2885_CONTENT_ERROR_ENVELOPE.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **Character-os UI → u-d-b reference sheet:** `/Users/donkeyking/Donkey_Betz/docs/2026-07-22_CHARACTER_OS_UI_TO_UDB_REFERENCE_SHEET.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated)

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
