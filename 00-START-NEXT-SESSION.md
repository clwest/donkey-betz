# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2914 CLOSE → S2914 shipped **Slice 3 batch 4** (2 tools) + a post-merge doc-fix PR. **S2915 OPENS WITH SLICE 3 CLOSE — evaluate Concern C at 5 instances (D6 moratorium blocks substrate arc; observation-only) then pivot to network trio batch OR queue Slice 4 open** — D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2914 close).** First batch to codify explicit READ-only allowlists + document transitive exclusions by name (Rigby Q3 zoom-out corrective: "gateway ambiguity debt" as the coupling risk accreting at accelerated pace). Rigby T0 SIGN CRITICAL CATCH: `intelligence_tool.search` reclassified READ_ONLY → MUTATION (hidden network via cross-file `_handle_web_search`) — second instance of the "hidden network/LLM in read-shaped gateway" pattern.

**PRs shipped this session:**
- u-d-b PR [#3457](https://github.com/clwest/donkey-betz-platform/pull/3457) — Slice 3 batch 4 (2 tools), merged at `3c8b00ffc`.
- u-d-b PR [#3458](https://github.com/clwest/donkey-betz-platform/pull/3458) — Batch 4 doc-fix (metadata classification = descriptive audit, NOT a runtime gate), merged at `a3ade5b43`.
- u-d-b PR `<TBD>` — S2914 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Tools shipped (2):**
- Batch 4: `work_tool` (7 R + 9 M), `intelligence_tool` (6 R in-scope + 10 documented-not-verified + 3 M)

**Rigby joint SIGN (1 substantive T0 + 1 post-merge verify, zero rubber-stamp):**
- Batch 4 T0 SIGN AGREE-with-edits (8+ repo_tool probes, tool-grounded). CRITICAL CATCH: `intelligence_tool.search` reclassified MUTATION (`_handle_web_search` at `td_handlers_agents.py:384`).
- Batch 4 post-merge verify: 4 in-scope READ dispatches clean; 1 excluded search dispatched and hit network (3052ms) — surfaced doc-language overstatement; doc-fix PR #3458 shipped.

**Sweep progress (post-S2914):**
- Slice 3 (`td_handlers_core`): **14/22 shipped; 8 remaining.**
- Total corpus untested: 55 → **55** (batch 4 was already counted). Gap map: **44 full + 10 partial + 55 untested.**
- Session cumulative pace: 2 tools / 1 batch / 1 session (with post-merge verify + doc-fix cycle).

**Concern C — Slice 3 schema↔doc drift count now at 5 (≥ threshold):**
`platform_awareness_tool` + `platform_config_tool` (S2913 batch 1) + `governance_tool` (S2913 batch 3) + `work_tool` + `intelligence_tool` (S2914 batch 4). Rigby's ≥5-core-tools threshold met. **Evaluate at Slice 3 CLOSE (S2915) per D6 moratorium (no substrate arc opens mid-sweep).**

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3457 recycled clean at `sha=3c8b00ffc`: 5 fresh workers, zero surviving old PIDs.
- PR #3458 doc-only — no recycle needed.

Full session context: `docs/handoffs/SESSION_2914_SLICE_3_BATCH_4.md`.

---

## S2915 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 3 CLOSE evaluation + next batch

**No blocking Chris D-verdict.** Slice 3 is at 14/22 with 8 tools remaining split by risk class. Rigby T0 SIGN Q2 at batch 4 recommended closing Slice 3 at ~14/22 and shipping the remaining 8 tools via 3 specialty batches.

**S2915 T0 SIGN questions to route to Rigby:**

- **Q1 Slice 3 CLOSE decision:** Formally close Slice 3 at 14/22 and route remaining 8 tools to specialty batches (network trio / async trio / row-create trio), OR keep Slice 3 open and continue the same shape (accepting each remaining tool's transitive verification cost as-is)?

- **Q2 Concern C evaluation at close threshold:** 5 Slice 3 tools now flag `actions_not_mentioned_in_description`. Three candidate framings — (a) auto-append action-enum appendix to schema description (generator-side); (b) doc-only lint that fails when enum values are not mentioned in description; (c) accept the drift as intrinsic to gateway-shaped tools where description names action-families rather than each action. **D6 moratorium blocks substrate arc open — observation + framing only.** Which framing does Rigby recommend Chris ratifies at some future post-moratorium session?

- **Q3 Next batch selection:** After Slice 3 close, first batch of the remaining 8 tools is:
  - **network trio** (`fleet_health` + `http_smoke_test` + `signal_studio_judge_stats`) — dedicated shape-break batch introducing network-preflight test pattern
  - **async trio** (`studio_tool` + `workflow_run_tool`) — dry_run + `apply_async` gating pattern
  - **row-create trio** (`competitor_comparison_tool` + `research_and_create_tool` + `task_breakdown_tool`) — first WRITE-path coverage batch
  - **pivot to Slice 4** (`td_handlers_gateway`, 17 tools) — leaves the 8 as backlog

- **Q4 zoom-out ask (required per feedback_zoom_out_ask_per_rigby_sign):** the S2914 batch 4 explicit-allowlist shape caught a second hidden network/LLM pattern (`intelligence_tool.search` → `_handle_web_search`). What does the S2914 shape *fail* to teach that batch 5 T0 should target? Should batch 5 introduce a **transitive-dependency proof** requirement (e.g., every delegated action requires a direct handler read + documented no-hidden-cost verdict), or would that slow the pace unhelpfully?

### Alternative Step 1 candidates (unchanged from prior sessions)

- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.

### What's forbidden at S2915 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.**
- No new gate/lint proposals.
- No agent-substrate validation arc.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.**
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.**
- **No "schema-drift-fix Fold promotion" without 2nd confirmed instance** (S2913 batch 3 `dream_tool.dream_type` was 1st; nothing new in S2914).
- **No `dry_run` infrastructure arc for mutation-class dispatchers without explicit Chris directive.**
- **No Concern C schema↔doc drift substrate arc mid-slice.** **5 instances observed; framing evaluated at Slice 3 CLOSE per D6 moratorium.**
- **No `post_save signal cascade` substrate arc without explicit Chris directive.**
- **No harness-level soft_error accounting substrate arc without explicit Chris directive.**
- **No "metadata-classification-as-runtime-gate" substrate arc without explicit Chris directive.** S2914 post-merge doc-fix corrected the descriptive-vs-enforcement framing. Watch for pattern recurrence; propose template guardrail at Slice 3 CLOSE if it recurs.
- **No "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd confirmed instance.** S2913 batch 2 `conversation_tool.search` (LLM) + S2914 batch 4 `intelligence_tool.search` (network) = 2 instances. 3rd would trigger Fold candidate evaluation.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — Ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged.
- **2-tier evidence template promotion** — Ledger row 160. Unchanged.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. **CLOSED at S2904.** S2914 sustained decoupled pace (batch 4 was 2 tools + verify cycle vs. S2913's 12 tools — both healthy).
- **Response-level introspection field creep** — Ledger row 162. Unchanged.
- **S2905 metadata-pattern-selection lint** — batch 4 used per-action (TOOL_ACTION_METADATA only) for both work_tool + intelligence_tool; no TOOL_DEFAULTS + no shadowing. Counter unchanged.
- **S2906/S2907/S2908 Ledger candidates** — unchanged.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate: `obs_tool_validation.md` §6.1** — unchanged.
- **S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action** — unchanged.
- **S2909 FT-1 through FT-5** — unchanged; FT-5 (`minimal_safe_args_v2`) still tracked as candidate arc.
- **S2910 FT-1 (Ledger #33)** — unchanged.
- **S2910 FT-2 (Ledger #34)** — unchanged.
- **S2911 Ledger #35** — unchanged.
- **S2911 Ledger #36 — Candidate Fold Trigger #1 (schema-drift-fix)** — NOT corroborated at S2914 batch 4.
- **S2911 Ledger #37 — HIDDEN MUTATION planner-safety pattern** — unchanged.
- **S2912 §5a mitigation note — `dry_run` add-flag pattern for actionless mutation-class dispatchers** — unchanged.
- **S2913 batch 2 Ledger candidate — envelope drift on `active_repo_tool.set/clear` + `conversation_tool.get`** — unchanged.
- **S2913 batch 3 Ledger candidates** — unchanged.
- **NEW S2914 batch 4 Ledger candidate — metadata-classification descriptive vs runtime-gate distinction.** Doc-fix in PR #3458 corrected the framing on batch 4 docs. Forward-carry: watch for the same overstatement pattern in future batch validation docs; propose shared "how to describe classification" boilerplate at Slice 3 CLOSE if it recurs.
- **NEW S2914 batch 4 Ledger candidate — "hidden network/LLM in read-shaped gateway" pattern reaches 2nd instance.** S2913 batch 2 (`conversation_tool.search` LLM) + S2914 batch 4 (`intelligence_tool.search` network). Forward-carry: if 3rd instance surfaces in Slice 3 batch 5 / Slice 4 / Slice 5, evaluate for Fold promotion per PLAYBOOK-6.10.
- **NEW S2914 batch 4 Ledger candidate — intelligence_tool 10 delegate/composite actions documented-but-not-verified.** Forward-carry: at Slice 3 CLOSE or a dedicated intelligence-delegates batch, read `_handle_stock_intelligence` / `_handle_sports_betting` / `_handle_legislation` / `_handle_rag_query` / `_handle_spider_data` handlers to confirm no hidden transitive network/LLM/write paths.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — unchanged.
- **Applicability metadata pattern (entry #28)** — unchanged.
- **Baseline lookback cap (entry #29)** — MITIGATED at PR #3423 (S2899).
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **R1 fleet reject-mode flip** — deferred.
- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind sweep.
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (17 registered tools):** UNCHANGED.
**Slice 2 — `td_handlers_agents` (25 tools):** **CLOSED at S2912.**

**Slice 3 — `td_handlers_core` (22 tools):**
- **S2913 batch 1: 4 tools ✓** (paid_interest_status, platform_awareness_tool, persona_tool, platform_config_tool).
- **S2913 batch 2: 4 tools ✓** (active_repo_tool, db_health_tool, conversation_tool, remember_tool).
- **S2913 batch 3: 4 tools ✓** (messaging_tool, learning_tool, dream_tool, governance_tool).
- **S2914 batch 4: 2 tools ✓** (work_tool, intelligence_tool). Explicit allowlist + transitive exclusions shape.
- **Remainder: 8 tools untested.** Network trio (`fleet_health` / `http_smoke_test` / `signal_studio_judge_stats`) + async trio (`studio_tool` / `workflow_run_tool`) + row-create trio (`competitor_comparison_tool` / `research_and_create_tool` / `task_breakdown_tool`).
- **Slice 3 CLOSE evaluation opens at S2915** per Rigby T0 SIGN Q2 AGREE at batch 4 — close at 14/22 with 8 deferred to specialty batches.

**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix).

**Total remaining tools to close:** ~55. Post-S2914 pace: 2 tools this session with in-depth SIGN + post-merge verify + doc-fix cycle. If S2915 ships Slice 3 close + network trio batch, sweep is at 17/22 with 5 remaining (async + row-create trios remain).

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2914 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2914: zero A4 spend — pure sweep-batch engineering (1 batch + 1 doc-fix).** A1 shipping spend was 2 PRs + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2914)

See:
- **S2914 handoff (current):** `docs/handoffs/SESSION_2914_SLICE_3_BATCH_4.md`
- **S2913 handoff:** `docs/handoffs/SESSION_2913_SLICE_3_BATCHES_1_2_3.md`
- **S2912 handoff:** `docs/handoffs/SESSION_2912_SLICE_2_CLOSE.md`
- **S2911 handoff:** `docs/handoffs/SESSION_2911_SLICE_2_BATCH_6A_PLUS_DRIFT_FIX.md`
- **S2910 handoff:** `docs/handoffs/SESSION_2910_SLICE_2_BATCH_5_MIXED_COMPOSITION_SWEEP.md`
- **S2909 handoff:** `docs/handoffs/SESSION_2909_SUBSTRATE_CLEANUP_ARC_T1_T2_SHIPPED.md`
- **S2909 arc scoping doc:** `docs/audits/pa_tools/substrate/S2909_substrate_cleanup_arc_scoping.md`
- **S2908 handoff:** `docs/handoffs/SESSION_2908_SLICE_2_BATCH_4_SHAPE_BREAK_SWEEP.md`
- **S2907 handoff:** `docs/handoffs/SESSION_2907_SLICE_2_BATCH_3_SMALL_ACTIONFUL_SWEEP.md`
- **S2906 handoff:** `docs/handoffs/SESSION_2906_SLICE_2_BATCH_2_ACTIONLESS_SWEEP.md`
- **S2905 handoff:** `docs/handoffs/SESSION_2905_SLICE_2_BATCH_1_ACCELERATED_SWEEP.md`
- **S2904 handoff:** `docs/handoffs/SESSION_2904_T1B_TEMPLATE_EXTRACTION.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2914 per-tool validation docs (this session's 2):** at `docs/research/tools/validation/`
  - `work_tool_validation.md`, `intelligence_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 57 non-substrate post-S2914)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (unchanged from S2911).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
