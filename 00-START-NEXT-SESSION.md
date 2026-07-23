# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2895 CLOSE → PA tools sweep Slice 1.5a shipped (autopilot_tool read-only, `untested`→`validated_partial`) + 2-tier evidence template landed + 3 Ledger candidates + 2 zoom-out folds (rows 160/161) (2026-07-22; picks up as S2896) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2895 close).** S2895 shipped Slice 1.5a of `td_handlers_ops` — the `autopilot_tool` read-only sweep. 76 read-only actions exercised live across 5 Rigby-executed batches (A–E); all successful; median latency ~15ms; p95 ~300ms; max 1252ms (`dry_run_report`). All ~29 mutation actions documented in §5a + explicitly deferred to Slice 1.5b (staged-enforcement session). The ship adopted a **new 2-tier evidence template** per Rigby S2895 T1 SIGN Q5 zoom-out — becomes the reference shape for future large-surface tool sweeps.

**PRs shipped this session:**
- u-d-b PR [#3415](https://github.com/clwest/donkey-betz-platform/pull/3415) — S2895 Slice 1.5a (`autopilot_tool_validation.md` 399 lines/47KB + gap-map regen), merged at `7891ee9c3`
- u-d-b PR `<TBD>` — S2895 close cascade (handoff + 00-START refresh + wrapper pin bump)

**Gap-map ratchet:**
```
validated_partial: 2 → 3 (+1: autopilot_tool)
untested:         95 → 94 (-1)
validated_full:   12 → 12 (unchanged — mutations deferred to Slice 1.5b)
per_tool_docs:    21 → 22
per_tool_docs_with_covered_actions:  13 → 14
```

**Ledger candidates routed to Rigby at close (Rigby Tool Gap Ledger deliverable `5c84e75a-…`, 16 → 19 rows):**

1. **Row A — `prospecting_queue` empty titles.** All 6 leads returned had empty `title` fields (financial-spider sources: sec_edgar, finnhub, polygon_finance, etherscan, yahoo_finance, financial). Score 45 flat. Blocks operator triage because queue is unreadable without titles.
2. **Row B — `integrity_null_spike_scan` false-positive noise.** 96 critical spikes at `null_rate=1.0` for `processed_data` + `embedding_text` fields across ~20 spider families — likely "not-populated-by-design" fields. Needs applicability-rule or allowlist.
3. **Row C — `autopilot_tool.history selected_fields` silent longer-list wipe.** Rigby T2 live observation — 8-path list echoed as `[]`, 4-path retry worked. Wipe location upstream of the handler's per-item silent-ignore. Concrete operator footgun.

**Twin workspace deliverables created (per feedback_rigby_writes_workspace_deliverables + feedback_twin_deliverable_at_every_ratification):**
- Content mirror `bb032d62-0373-42a9-80dd-8416a99b3c4a` (initiative_phase_doc / research / Donkey Betz workspace)
- Ratification record `40f62eda-d245-40fe-894e-5086776f3e41` (ratification_record / governance / Donkey Betz workspace)
- ORM verified — no diagnostic misfire (S2753 issue absent)
- UI list verified — both at top of Donkey Betz deliverables

**Zoom-out folds appended to `logs/zoom_out_classifications.jsonl` (local-only, gitignored):**
- **Row 160 (`same_pr_mitigatable`) — 2-tier evidence template for large-surface tool sweeps.** Mitigation shipped in-doc (§6.1 Evidence Ledger + §6.2 family narrative + §7 raw appendix). Rigby T2 AGREE'd on classification. Future promotion trigger: 1-2 more large-surface (>30 action) sweeps adopt cleanly → promote to first-class sweep-methodology section OR Playbook §7 (Testing Discipline chapter candidacy) amendment.
- **Row 161 (`future_trigger`) — sweep-arc pace not sustainable at current shape.** Math: ~400-line docs × 76 remaining tools × 1-2 per session = ~50 sessions of validation before Slice 5 closes. Substrate is likely changing faster than validation completes. Rigby proposed 3 methodology shifts: (a) family-level substrate audits + shared templates + auto-generated action inventories, (b) delete/merge low-signal tools first, (c) lightweight auto-harness running all read-only actions nightly with machine-checkable ledger. Classified `future_trigger` — decision point at S2896 open (see below).

**Ledger Row A (S2894 DBZ enforcement/attribution divergence) revised at Rigby T2 SIGN:** history rows carry `result.reason: operator_cap_change_hysteresis` explicitly on the downgrade_set/cleared pairs. This cleanly explains the $3.07/$2.98 oscillations as normal hysteresis during operator cap changes, NOT enforcer-side PA-bypass. Bucket (a) is now the primary hypothesis. Bucket (e) [enforcer excludes PA critical-agents] deprioritized unless reproduced under stable-cap conditions. Full revised discussion in `docs/research/tools/validation/autopilot_tool_validation.md` §7.1.

Full session context: `docs/handoffs/SESSION_2895_PA_TOOLS_SWEEP_SLICE_1_5A_AUTOPILOT_READ_ONLY.md`.

---

## S2896 open sequence

### Step 1 (FIRST DECISION POINT) — Row 161 substrate-arc gate

Before running another sweep batch, decide among:

- **Option A (Rigby lean) — Open a dedicated substrate arc.** Auto-harness build + family-doc template extraction + low-signal tool audit. Slows sweep pace short-term; expected to close remaining Slice 1-5 scope in ~10-15 sessions instead of ~50. Requires methodology + tool-deletion authority scoping first.
- **Option B — Push through Slice 1 close-out (~4-5 more current-shape sessions), THEN re-evaluate.** Closes `autopilot_tool` mutations (Slice 1.5b) + 4 doc/unknown/partial ops tools. Gives hard data on low-signal-vs-high-signal tools before committing to substrate work.
- **Option C — Skip ahead to a Ledger-row-fix engineering session first** (autopilot_tool selected_fields batch-wipe fix OR prospecting_queue empty-titles). Small, concrete engineering shipments; sweep continues after.

**If Chris directs the substrate arc (Option A):** open as `s2896-pa-tools-sweep-substrate-arc` with 3 parallel workstreams — auto-harness spec, family-doc template extraction, low-signal-tool audit scoping. Deferred workshop candidate.

### Step 2 — Net-new engineering candidates (per feedback_engineering_bias_over_audit)

**Path B does NOT preempt engineering-bias.** Still surface 1-3 net-new candidates at any natural pause. Priority order for S2896:

1. **`autopilot_tool.history selected_fields` batch-wipe fix (S2895 Ledger Row C)** — small, concrete operator footgun; ~15-line fix likely in the schema-validation layer upstream of `td_handlers_ops.py:2521-2534`.
2. **`prospecting_queue` empty-titles investigation (S2895 Ledger Row A)** — either upstream lead-scoring path or response projection dropping titles for financial-spider sources.
3. **`integrity_null_spike_scan` applicability rule (S2895 Ledger Row B)** — allowlist or per-field applicability rule to filter out expected-null (spider, field) pairs.
4. **DBZ enforcement doc-clarity annotation** — `enforcement_report` output should include hysteresis-oscillation shape so operators reading multiple downgrade_set/cleared pairs don't misread as "enforcer flapping".
5. **Continue S2894 Ledger rows** — `messaging_tool.send` action (or in-thread-pattern schema note), `zoom_out_tool.record_fold` action (or JSONL→workspace-deliverable mirror).
6. **PLAYBOOK-3.2.3/3.2.4 compliance sweep** — carried from S2891.

### What's forbidden at S2896 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — Chris pivoted to the sweep. If character-os side pings, stand by per pre-S2892 protocol.
- **Testing Discipline chapter candidacy** — ledger row 154 `future_trigger`. Unchanged; may fuse with Row 160/161 promotion if trigger fires together.
- **Bridge call observability rename-risk** — ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — ledger row 159 (S2894). Unchanged.
- **2-tier evidence template promotion** — ledger row 160 (S2895, this session). Triggers after 1-2 more large-surface sweeps adopt cleanly.
- **Sweep-arc pace sustainability substrate arc** — ledger row 161 (S2895, this session). Decision point at S2896 open (see Step 1).
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
- Batch 1 (S2892): agent_control_tool, agent_memory_tool, heartbeat_history_tool, infra_health_tool ✓
- Batch 2 (S2893): governor_tool, ops_digest_tool, scheduled_tasks_tool, spider_status_tool ✓
- Batch 3 (S2894): workspace_budget_tool ✓ (single-tool batch)
- Batch 4 = Slice 1.5a (S2895, this session): **autopilot_tool read-only ✓** (single-tool batch, `validated_partial`)
- **Remainder:** Slice 1.5b (autopilot_tool mutations, ~1 session) + 4 doc/unknown/partial ops tools (`agent_introspection_tool`, `kb_tool`, `search_docs`, `ops_tool`, ~1-2 sessions)

**Slice 2 — `td_handlers_agents` (25 tools, ~7 sessions):** queued
**Slice 3 — `td_handlers_core` (22 tools, ~6 sessions):** queued
**Slice 4 — `td_handlers_gateway` (17 tools, ~5 sessions):** queued
**Slice 5 — `tool_dispatcher` (14 tools, ~4 sessions):** queued

**Total remaining tools to close (before Row 161 substrate arc):** 76 (or ~104 counting partials + doc-unknowns).
**Estimated total sessions remaining at current-shape pace:** ~50 (Row 161 triggers this concern).

**Informative per-batch outcome check (S2893 fold-158 hybrid):** S2895 met the check naturally — 3 substantive Ledger candidates surfaced. Rows 158 + 159 unchanged. Rows 160 + 161 new this session.

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2895 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2895: zero A4 spend — pure engineering + governance.** A1 shipping spend was the sweep PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2895)

See:
- **S2895 handoff (current):** `docs/handoffs/SESSION_2895_PA_TOOLS_SWEEP_SLICE_1_5A_AUTOPILOT_READ_ONLY.md`
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
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 22 total after this session)

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
