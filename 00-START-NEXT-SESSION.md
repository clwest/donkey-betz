# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2894 CLOSE → PA tools sweep Slice 1 Batch 3 shipped (workspace_budget_tool single-tool batch per Chris D-verdict, `untested`→`validated_full`) + 3 Rigby Tool Gap Ledger candidates + zoom-out fold row 159 (2026-07-22; picks up as S2895) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2894 close).** S2894 shipped Batch 3 of Slice 1 (`td_handlers_ops`) as a single-tool batch per Chris D-verdict at Turn 1. Only `workspace_budget_tool` (11 actions, 7 mutations, 2 staff-only) — Rigby zoom-out §4 pushback flagged that mutation-heavy tools warrant single-tool batches, and Chris ratified after joint Claude+Rigby recommendation. 13 canary-safe actions dispatched by Rigby against Agent-Testing workspace (all PASS) + 2 read-only sharpening probes on Donkey Betz (Ledger #1). 3 substantive Rigby Tool Gap Ledger candidates surfaced.

**PRs shipped this session:**
- u-d-b PR `<TBD>` — S2894 Slice 1 batch 3 (1 validation doc + PA_TOOL_AUDIT.md regen + PA_TOOLS_GAP_MAP.md regen + zoom-out fold row 159 + handoff)
- u-d-b PR `<TBD>` — S2894 close cascade (wrapper pin bump)

**Gap-map ratchet (before → after this session):**
```
validated_full:   11 → 12 (+1: workspace_budget_tool)
untested:         96 → 95 (-1)
per_tool_docs:    20 → 21
per_tool_docs_with_covered_actions:  12 → 13
```

**Ledger candidates routed to Rigby at close (Rigby Tool Gap Ledger deliverable `5c84e75a-…`, 13 → 16 rows):**

1. **Row A — DBZ enforcement/attribution divergence (`workspace_budget_tool`).** Donkey Betz shows `daily_total=$12.52` vs explicit `cap=$5.00` (2.5× over) yet `is_frozen=false, is_downgraded=false`. 17 enforcement events in 7d (last 2026-07-20T20:35Z), current flags don't reflect. Discriminator needed: `AutopilotAction.evidence.daily_total` at decision time via `autopilot_tool.history` (Slice 1.5) OR direct ORM.
2. **Row B — `messaging_tool` lacks send surface.** Read-only (`list_threads`/`get`). Blocks Claude→Rigby→Chris async DM pattern; in-thread reply is the working path.
3. **Row C — Zoom-out fold canonical location not discoverable via PA tool surface.** Folds live at `logs/zoom_out_classifications.jsonl` (repo file); Rigby can't discover/read/append. Blocks Rigby closing SIGN loops autonomously.

**Zoom-out fold row 159** — `pa_tools_sweep_mutation_heavy_single_tool_batch`, `same_pr_mitigatable`. Rigby's SIGN §4 pushback: "action-count budgeting" trending toward batch-shape driver risks shallow mutation-gate validation. Mitigation shipped this PR: workspace_budget_tool §5a codifies canary+revert protocol with blast-radius classification table. Future promotion trigger: 1-2 more mutation-heavy tool corroborations → promote canary-revert to first-class sweep-methodology section.

Full session context: `docs/handoffs/SESSION_2894_PA_TOOLS_SWEEP_SLICE_1_BATCH_3.md`.

---

## S2895 open sequence

### Step 1 (FIRST THING) — decision point: Slice 1.5 vs Slice 1 cleanup vs Slice 2

Slice 1 (`td_handlers_ops`) is now 9/10 non-autopilot tools at `validated_full`. Three viable paths for S2895 (present these to Chris at open if not obvious):

- **Option A (recommended default) — open Slice 1.5 for `autopilot_tool` read-only sweep.** Per S2893 pre-commit note: ~110 read-only actions in one session, ship `validated_partial`; mutation sweep in a follow-on session. Closes the biggest remaining piece.
- **Option B — dedicated non-sweep session to upgrade 4 doc/unknown/partial ops tools first** (`agent_introspection_tool`, `kb_tool`, `search_docs`, `ops_tool` partial → full). Small doc-only work; fully closes `td_handlers_ops` proper before Slice 1.5.
- **Option C — skip ahead to Slice 2 (`td_handlers_agents`, 25 tools).** Leaves ops-slice cleanup for later.

**If Chris directs a Ledger-row-fix instead of continuing the sweep:** the DBZ enforcement gap (Row A) is the highest-priority ship candidate — customer-facing trust surface, small engineering scope. Discriminator: read the most recent `AutopilotAction` row for DBZ + verify which of buckets (b)/(c)/(e) fires.

### Step 2 — Net-new engineering candidates (per feedback_engineering_bias_over_audit)

**Path B does NOT preempt engineering-bias.** Still surface 1-3 net-new candidates at any natural pause. Priority order for S2895:

1. **DBZ enforcement gap fix (S2894 Ledger Row A)** — small, customer-facing trust surface. Discriminator work first.
2. **`messaging_tool.send` action or in-thread-pattern schema note (S2894 Ledger Row B)** — small; unblocks Rigby async DM routing.
3. **`zoom_out_tool.record_fold` action OR JSONL→workspace-deliverable mirror (S2894 Ledger Row C)** — closes Rigby's SIGN loop.
4. **`diagnostics_tool.schema_handler_diff` placeholder → implementation** — carried from S2893. Rigby self-introspection tool.
5. **Ship one S2893 Ledger row** — `governor_tool.status` cache/consistency fix, `governor_tool.reason` fail-open surfacing, or `ops_digest_tool` autopilot staleness heuristic.
6. **PLAYBOOK-3.2.3/3.2.4 compliance sweep** — carried from S2891.

### What's forbidden at S2895 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — Chris pivoted to the sweep. If character-os side pings, stand by per pre-S2892 protocol.
- **Testing Discipline chapter candidacy** — ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — ledger row 159 (new this session). Mitigation shipped in workspace_budget_tool §5a.
- **R1 fleet reject-mode flip** — deferred.
- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind sweep.
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits (`requested_model_id`, `was_policy_reroute`) — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (17 registered tools, 11 previously untested):**
- Batch 1 (S2892): agent_control_tool, agent_memory_tool, heartbeat_history_tool, infra_health_tool ✓
- Batch 2 (S2893): governor_tool, ops_digest_tool, scheduled_tasks_tool, spider_status_tool ✓
- Batch 3 (S2894, this session): **workspace_budget_tool ✓** (single-tool batch per Chris D-verdict)
- **Slice 1 non-full remainder:** agent_introspection_tool, kb_tool, search_docs (doc/unknown); ops_tool (partial) — Option B session material
- Slice 1.5 (post-Slice-1 close): autopilot_tool read-only sweep + autopilot_tool mutations sweep (2 sessions estimated)

**Slice 2 — `td_handlers_agents` (25 tools, ~7 sessions):** queued
**Slice 3 — `td_handlers_core` (22 tools, ~6 sessions):** queued
**Slice 4 — `td_handlers_gateway` (17 tools, ~5 sessions):** queued
**Slice 5 — `tool_dispatcher` (14 tools, ~4 sessions):** queued

**Total remaining tools to close:** 91 after this batch.
**Estimated total sessions remaining in arc:** ~25.

**Informative per-batch outcome check (S2893 fold-158 hybrid — Rigby SIGN Path C):** S2894 met the check naturally — 3 substantive Ledger candidates surfaced. Row 158 remains `future_trigger`; row 159 corroborates the mutation-heavy-single-tool pattern that fold-158 hedges against.

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2894 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2894: zero A4 spend — pure engineering + governance.** A1 shipping spend was the sweep PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2894)

See:
- **S2894 handoff (current):** `docs/handoffs/SESSION_2894_PA_TOOLS_SWEEP_SLICE_1_BATCH_3.md`
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
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated)

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
