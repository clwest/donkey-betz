# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2915 CLOSE → S2915 shipped **Slice 3 batch 5** (row-create trio, 3 tools) + introduced §5b first-hop dependency proof shape + formally closed Slice 3 core surface at 14/22. **S2916 OPENS WITH BATCH 6 = NETWORK TRIO (`fleet_health` + `http_smoke_test` + `signal_studio_judge_stats`) applying §5b shape to the network-preflight test pattern** — D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2915 close).** First batch to introduce the §5b "first-hop dependency proof" shape per Rigby T0 SIGN Q4 verdict. Closes the S2914 gap — explicit action allowlist doesn't prove those actions have no hidden network/LLM/write cost via delegated helpers. Second actionless-MUTATION `TOOL_DEFAULTS` entry (`research_and_create_tool` after S2910 `legal_doc_drafter_agent`). Second IRREVERSIBLE-classified action (`competitor_comparison_tool.delete` after S2908 `media_tool.delete`). Rigby post-merge verify clean — zero critical flags.

**PRs shipped this session:**
- u-d-b PR [#3460](https://github.com/clwest/donkey-betz-platform/pull/3460) — Slice 3 batch 5 (row-create trio + §5b shape), merged at `0ced0a1b3`.
- u-d-b PR `<TBD>` — S2915 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Tools shipped (3):**
- Batch 5: `task_breakdown_tool` (2 R), `research_and_create_tool` (actionless MUTATION via TOOL_DEFAULTS), `competitor_comparison_tool` (3 R + 4 M + 1 IRREVERSIBLE).

**Rigby joint SIGN (1 substantive T0 + 1 post-merge verify, zero rubber-stamp):**
- Batch 5 T0 SIGN 4-turn cycle (14+ tool-grounded probes). Q1/Q2/Q3/Q4 verdicts with file+line citations from actual handler-body reads.
- Batch 5 post-merge verify: 2 live READ_ONLY dispatches clean (25ms + 4ms latency), 1 code-verified BLOCKED check on research_and_create_tool. Zero flags.

**Sweep progress (post-S2915):**
- Slice 3 (`td_handlers_core`): **17/22 shipped; 5 remaining. Slice 3 FORMALLY CLOSED at 14/22 core surface.**
- Total corpus untested: 55 → **52** (batch 5 flipped 3 untested → 1 full + 2 partial).
- Gap map: **41 full + 10 partial + 55 untested.**
- Session cumulative pace: 3 tools / 1 batch / 1 session (with in-depth SIGN + post-merge verify).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3460 recycled clean at `sha=0ced0a1b3`: 5 fresh workers, zero surviving old PIDs.

Full session context: `docs/handoffs/SESSION_2915_SLICE_3_BATCH_5.md`.

---

## S2916 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Batch 6 = network trio T0 SIGN routing

**No blocking Chris D-verdict.** Batch 5 established Slice 3 CLOSE + the §5b first-hop dependency proof shape. Batch 6 applies §5b to the network-preflight test pattern.

**S2916 T0 SIGN questions to route to Rigby:**

- **Q1 network trio composition:** Ship all 3 network tools together (`fleet_health` + `http_smoke_test` + `signal_studio_judge_stats`)? These are the highest network-density tools in Slice 3 remainder. All three are declared network-active by handler-read at S2915 T0 SIGN. Signal Studio judge_stats is auth-less; http_smoke_test uses fleet HMAC; fleet_health delegates to mgmt command `probe_fleet`.

- **Q2 §5b shape stress test on network-preflight:** The §5b shape treats direct callees as read/network/etc. But for a network-preflight tool, the "callee" IS the network. Does the §5b shape need a **network-preflight extension** (e.g., "declares which fleet endpoints get probed" + "declares HMAC signing requirement" + "declares timeout envelope") to be meaningful for network tools? Or is the S2915 shape sufficient?

- **Q3 network-batch safety class:** Should these tools be READ_ONLY (they don't write) or a new `NETWORK_READ` class distinct from ORM read? At batch 5, the read/network split in §5b was per-callee classification. Should the tool-level `safety_class` reflect the same distinction, or is READ_ONLY + notes-field sufficient?

- **Q4 zoom-out ask (required per feedback_zoom_out_ask_per_rigby_sign):** The S2915 §5b shape works for handlers where the callee list is small + firm. For the async duo (batch 7 candidate: `studio_tool` + `workflow_run_tool`), the callee list is fan-out via Celery apply_async into agents/spiders/LLMs. Does §5b need to evolve for the async duo, or does the current "opaque, revisit trigger" escape valve handle it? What coupling/risk is accreting that we're not naming?

### Alternative Step 1 candidates (unchanged from prior sessions)

- **Batch 7 async duo first:** ship `studio_tool` + `workflow_run_tool` before network trio (accepts higher §5b stress but validates the async fan-out shape earlier).
- **Slice 4 open:** pivot to `td_handlers_gateway` (17 tools) and leave the 5 as backlog.
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.

### What's forbidden at S2916 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.**
- No new gate/lint proposals.
- No agent-substrate validation arc.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.**
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.**
- **No "schema-drift-fix Fold promotion" without 2nd confirmed instance.**
- **No `dry_run` infrastructure arc for mutation-class dispatchers without explicit Chris directive.**
- **No Concern C schema↔doc drift substrate arc.** 5 instances observed at Slice 3 CLOSE; framing (a) recommended for future post-D6 ratification.
- **No `post_save signal cascade` substrate arc without explicit Chris directive.**
- **No harness-level soft_error accounting substrate arc without explicit Chris directive.**
- **No "metadata-classification-as-runtime-gate" substrate arc without explicit Chris directive.**
- **No "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd confirmed instance.** S2913 batch 2 `conversation_tool.search` (LLM) + S2914 batch 4 `intelligence_tool.search` (network) = 2 instances. 3rd would trigger Fold candidate evaluation.
- **No "cascade audit companion doc" pattern promotion without 2nd instance.** S2915 `competitor_comparison_tool.delete` = 1st instance (FK cascade behavior opaque at model-file layer).
- **No "IRREVERSIBLE dry_run flag harness lint" Fold promotion without 3rd instance.** S2908 `media_tool.delete` + S2915 `competitor_comparison_tool.delete` = 2 instances. 3rd would trigger evaluation.
- **No `NEXT_HEADING_RE` parser fix without Chris directive or 3rd instance.** S2914 + S2915 = 2 instances of `###`-subsection breaking parity extraction; batch 5 workaround = flatten to bulleted list with inline class prefix.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — Ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged.
- **2-tier evidence template promotion** — Ledger row 160. Unchanged.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. **CLOSED at S2904.** S2915 sustained decoupled pace (batch 5 was 3 tools + verify cycle).
- **Response-level introspection field creep** — Ledger row 162. Unchanged.
- **S2905 metadata-pattern-selection lint** — batch 5 used TOOL_DEFAULTS for research_and_create_tool + per-action for task_breakdown_tool + competitor_comparison_tool. Zero shadowing; no lint counter increment.
- **S2906/S2907/S2908 Ledger candidates** — unchanged.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate: `obs_tool_validation.md` §6.1** — unchanged.
- **S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action** — **CORROBORATED at S2915** (`competitor_comparison_tool.delete`). 2/3 instances toward Fold candidate evaluation.
- **S2909 FT-1 through FT-5** — unchanged; FT-5 (`minimal_safe_args_v2`) still tracked as candidate arc.
- **S2910 FT-1 (Ledger #33)** — unchanged.
- **S2910 FT-2 (Ledger #34)** — unchanged.
- **S2911 Ledger #35** — unchanged.
- **S2911 Ledger #36 — Candidate Fold Trigger #1 (schema-drift-fix)** — unchanged.
- **S2911 Ledger #37 — HIDDEN MUTATION planner-safety pattern** — unchanged.
- **S2912 §5a mitigation note — `dry_run` add-flag pattern for actionless mutation-class dispatchers** — unchanged.
- **S2913 batch 2 Ledger candidate — envelope drift on `active_repo_tool.set/clear` + `conversation_tool.get`** — unchanged.
- **S2913 batch 3 Ledger candidates** — unchanged.
- **S2914 batch 4 Ledger candidate — metadata-classification descriptive vs runtime-gate distinction** — unchanged; no recurrence in batch 5 (validation docs correctly framed classification as audit metadata).
- **S2914 batch 4 Ledger candidate — "hidden network/LLM in read-shaped gateway" pattern reaches 2nd instance** — unchanged; not corroborated at batch 5. Watch batch 6-7 (network + async).
- **S2914 batch 4 Ledger candidate — intelligence_tool 10 delegate/composite documented-not-verified** — unchanged.
- **NEW S2915 batch 5 Ledger candidate — second actionless-MUTATION `TOOL_DEFAULTS` entry.** `research_and_create_tool` after S2910 `legal_doc_drafter_agent`. 3rd instance would trigger "actionless side-effecting chain" pattern naming.
- **NEW S2915 batch 5 Ledger candidate — opaque callee trust-downgrade pattern first substantial use.** 7 total opaques recorded across research_and_create + competitor_comparison. Watch discipline across batches 6-7 for opaque-forever creep.
- **NEW S2915 batch 5 Ledger candidate — model-file cascade audit gap.** `competitor_comparison_tool.delete` firm at handler layer, opaque at cascade layer. Forward-carry cascade audit companion doc pattern proposal at next Slice close or 2nd instance.
- **NEW S2915 batch 5 Ledger candidate — `NEXT_HEADING_RE` breaks parity on `###` subsections.** S2914 `intelligence_tool_validation.md` + S2915 `competitor_comparison_tool_validation.md` = 2 instances. Workaround = flatten to bulleted list with inline class prefix. Parser fix deferred; 3rd instance triggers evaluation.
- **NEW S2915 batch 5 Ledger candidate — second IRREVERSIBLE action.** `competitor_comparison_tool.delete` after S2908 `media_tool.delete`. 2/3 instances toward "IRREVERSIBLE actions require dry_run flag" harness-side lint Fold candidate.
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

**Slice 3 — `td_handlers_core` (22 tools):** **CLOSED at S2915 at 14/22 core surface** per Rigby T0 SIGN Q1 AGREE.
- **S2913 batch 1: 4 tools ✓** (paid_interest_status, platform_awareness_tool, persona_tool, platform_config_tool).
- **S2913 batch 2: 4 tools ✓** (active_repo_tool, db_health_tool, conversation_tool, remember_tool).
- **S2913 batch 3: 4 tools ✓** (messaging_tool, learning_tool, dream_tool, governance_tool).
- **S2914 batch 4: 2 tools ✓** (work_tool, intelligence_tool). Explicit allowlist + transitive exclusions shape.
- **S2915 batch 5: 3 tools ✓** (task_breakdown_tool, research_and_create_tool, competitor_comparison_tool). Row-create trio + §5b first-hop dependency proof shape.
- **Remaining: 5 tools untested.** Network trio (batch 6): `fleet_health` + `http_smoke_test` + `signal_studio_judge_stats`. Async duo (batch 7): `studio_tool` + `workflow_run_tool`.

**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix).

**Total remaining tools to close:** ~52. Post-S2915 pace: 3 tools this session with in-depth SIGN + post-merge verify cycle. If S2916 ships network trio, sweep is at 20/22 with 2 remaining (async duo).

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2915 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2915: zero A4 spend — pure sweep-batch engineering (1 batch).** A1 shipping spend was 1 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2915)

See:
- **S2915 handoff (current):** `docs/handoffs/SESSION_2915_SLICE_3_BATCH_5.md`
- **S2914 handoff:** `docs/handoffs/SESSION_2914_SLICE_3_BATCH_4.md`
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
- **S2915 per-tool validation docs (this session's 3):** at `docs/research/tools/validation/`
  - `task_breakdown_tool_validation.md`, `research_and_create_tool_validation.md`, `competitor_comparison_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 60 non-substrate post-S2915)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (unchanged from S2911).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
