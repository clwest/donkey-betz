# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2913 CLOSE → S2913 shipped **3 accelerated batches** in Slice 3 (`td_handlers_core`), closing 12 tools in one session. **S2914 OPENS WITH SLICE 3 BATCH 4** (10 tools remain) — D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2913 close).** First triple-batch session of the accelerated post-substrate sweep. Slice 3 opened at S2913 and reached 12/22 tools shipped in a single session, matching S1218-style triple-ship cadence. Batches 1+2+3 all used the scoped-to-READ_ONLY-subset shape ratified at batch 1 T0 SIGN. Rigby joint SIGN 3 substantive cycles (0 rubber-stamp), including 1 Claude course-correction on `conversation_tool.search` LLM cost (batch 2) and 4 verify-before-commit flags all verified via direct handler read (batch 3).

**PRs shipped this session:**
- u-d-b PR [#3453](https://github.com/clwest/donkey-betz-platform/pull/3453) — Slice 3 batch 1 (4 tools), merged at `00fcb352f`.
- u-d-b PR [#3454](https://github.com/clwest/donkey-betz-platform/pull/3454) — Slice 3 batch 2 (4 tools), merged at `b2a2ae0e5`.
- u-d-b PR [#3455](https://github.com/clwest/donkey-betz-platform/pull/3455) — Slice 3 batch 3 (4 tools) + session close batch, merged at `d6fc0480c`.
- u-d-b PR `<TBD>` — S2913 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Tools shipped (12):**
- Batch 1: `paid_interest_status`, `platform_awareness_tool`, `persona_tool`, `platform_config_tool`
- Batch 2: `active_repo_tool`, `db_health_tool`, `conversation_tool`, `remember_tool`
- Batch 3: `messaging_tool`, `learning_tool`, `dream_tool`, `governance_tool`

**Rigby joint SIGN (3 substantive cycles this session, zero rubber-stamp):**
- Batch 1 T0 SIGN AGREE-with-edits (9 repo_tool probes, tool-grounded).
- Batch 2 T1 SIGN AGREE-with-edits — **Claude course-correction on `conversation_tool.search`**: Rigby V1 assumed pure ORM; Claude direct handler read caught `EmbeddingService.create_embedding(query)` at :2038 (LLM cost). Reclassified as MUTATION per `feedback_verify_rigby_tool_runs_before_trusting_sign`.
- Batch 3 T1 SIGN AGREE-with-edits — 4 verify-before-commit flags all verified: messaging read-receipt (NO writes on unread_count), messaging send_message (schema-hidden defense-in-depth per Session 1253 PR 4), governance decision_create naming (clean), no LLM on any covered read action.

**Sweep progress (post-S2913):**
- Slice 3 (`td_handlers_core`): **12/22 shipped; 10 remaining.**
- Total corpus untested: 69 → **57** (-12). Gap map: 32 → **44 full** + 8 partial + 57 untested.
- Session cumulative pace: 12 tools / 3 batches / 1 session — first S1218-cadence session of the accelerated sweep.

**Concern C — Slice 3 schema↔doc drift count reaches 3:**
`platform_awareness_tool` + `platform_config_tool` (batch 1) + `governance_tool` (batch 3) all flagged `actions_not_mentioned_in_description`. Fold candidate promotion evaluated at Slice 3 CLOSE, NOT mid-slice (D6 moratorium — no substrate arc opens).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- 3 clean recycles: batch 1 `sha=00fcb352f16b`, batch 2 `sha=b2a2ae0e5434`, batch 3 `sha=d6fc0480c089`. Surviving=none in all 3.

Full session context: `docs/handoffs/SESSION_2913_SLICE_3_BATCHES_1_2_3.md`.

---

## S2914 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 3 batch 4

**No blocking Chris D-verdict.** S2913 shipped 3 PRs cleanly; batch shape proven across 3 batches; sweep-arc pace accelerating.

**Remaining Slice 3 corpus (10 tools):**
- **Network-suspect (defer to network-focused batch):** `fleet_health`, `http_smoke_test`, `signal_studio_judge_stats` (all direct HTTP).
- **Celery/async-suspect (defer to MUTATION-coverage batch):** `studio_tool`, `workflow_run_tool` (both have `apply_async`).
- **Row-create-suspect:** `competitor_comparison_tool` (`.create` at :2761), `research_and_create_tool`, `task_breakdown_tool`.
- **Pure-ORM read candidates:** `work_tool` (16 actions with clear R/M split), `intelligence_tool` (20+ actions, mostly R).

**S2914 T0 SIGN questions to route to Rigby:**
- **Q1 Batch composition:** continue pure-ORM opener shape with 3-4 more tools (work_tool as centerpiece is the highest-leverage remaining pick), OR pivot to a network-focused batch to close fleet_health / http_smoke_test / signal_studio_judge_stats trio in one dedicated batch?
- **Q2 Substrate observation:** 3 batches proven the shape; consider closing Slice 3 sweep at 15/22 tools + 7 deferred to a dedicated MUTATION-coverage batch across Slices 3+4+5, OR push to close Slice 3 fully via more targeted per-tool investigation?
- **Q3 zoom-out ask (required per feedback_zoom_out_ask_per_rigby_sign):** at 3 batches shipped in one session, what does the pattern *fail* to teach us that batch 4 T0 should target? What's the highest-risk assumption in the sweep-continues-unchanged posture?

### Alternative Step 1 candidates (unchanged from S2912/S2913 open)

- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.

### What's forbidden at S2914 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.** v2 is frozen at S2909 close.
- No new gate/lint proposals.
- No agent-substrate validation arc.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.**
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.**
- **No "schema-drift-fix Fold promotion" without 2nd confirmed instance.**
- **No `dry_run` infrastructure arc for mutation-class dispatchers without explicit Chris directive.**
- **No Concern C schema↔doc drift substrate arc mid-slice.** 3 instances in Slice 3 batches 1+3; evaluated at Slice 3 CLOSE per Rigby T0 Q4 threshold + D6 moratorium.
- **No `post_save signal cascade` substrate arc without explicit Chris directive.** `dream_tool.approve` is a candidate class-example (S2913 batch 3); forward-carry ledger observation only.
- **No harness-level soft_error accounting substrate arc without explicit Chris directive.** S2913 batches 2+3 observed harness soft_error counts don't distinguish structured `_handler_error` (S2886) from inline `{error}` (drift); forward-carry ledger observation.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — Ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged.
- **2-tier evidence template promotion** — Ledger row 160. Unchanged.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. **CLOSED at S2904.** S2913 sustained accelerated pace with 3-batch session.
- **Response-level introspection field creep** — Ledger row 162. Unchanged.
- **S2905 metadata-pattern-selection lint** — batches 1+2+3 used per-action (via TOOL_ACTION_METADATA for mixed) + TOOL_DEFAULTS for actionless; no shadowing. Counter unchanged.
- **S2906/S2907/S2908 Ledger candidates** — unchanged.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate: `obs_tool_validation.md` §6.1** — unchanged.
- **S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action** — unchanged.
- **S2909 FT-1 through FT-5** — unchanged; FT-5 (`minimal_safe_args_v2`) still tracked as candidate arc.
- **S2910 FT-1 (Ledger #33) — Entrypoint-side context-injection test coverage gap** — unchanged.
- **S2910 FT-2 (Ledger #34) — Doc-pointer-verification lint candidate** — unchanged.
- **S2911 Ledger #35 — Envelope-shape inconsistency on `opportunity_manager.delete` + `task_manager.delete`** — unchanged.
- **S2911 Ledger #36 — Candidate Fold Trigger #1 (schema-drift-fix)** — NOT corroborated at S2913 batches 1+2+3.
- **S2911 Ledger #37 — HIDDEN MUTATION planner-safety pattern** — unchanged.
- **S2912 §5a mitigation note — `dry_run` add-flag pattern for actionless mutation-class dispatchers** — unchanged.
- **NEW S2913 batch 2 Ledger candidate — envelope drift on `active_repo_tool.set/clear` + `conversation_tool.get` inline `{ok: False, error}` on missing-arg paths** — forward-carry; MUTATION-skipped this session.
- **NEW S2913 batch 3 Ledger candidate — `dream_tool.dream_type` schema description ('creative_idea') vs handler ('user_request') default drift** — minor; forward-carry.
- **NEW S2913 batch 3 Ledger candidate — `messaging_tool.send_message` schema-hidden defense-in-depth pattern (Session 1253 PR 4)** — pattern worth watching if more schema-hidden handler paths surface in Slice 3+4+5. Forward-carry.
- **NEW S2913 batch 3 Ledger candidate — `dream_tool.approve` post_save signal cascade** (promote_to_initiative + execute_single_dream.delay) as class-example. Forward-carry.
- **NEW S2913 batches 2+3 Ledger candidate — harness `soft_error` accounting doesn't distinguish S2886 `_handler_error` structured envelope from inline `{error}` drift.** Forward-carry harness-substrate observation; D6 moratorium.
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
- **S2913 batch 1: 4 tools ✓** (paid_interest_status, platform_awareness_tool, persona_tool, platform_config_tool). Actionless+scoped-to-READ_ONLY-subset opener.
- **S2913 batch 2: 4 tools ✓** (active_repo_tool, db_health_tool, conversation_tool, remember_tool). Continuation shape.
- **S2913 batch 3: 4 tools ✓** (messaging_tool, learning_tool, dream_tool, governance_tool). Session close batch.
- **Remainder: 10 tools untested.** Fleet_health / http_smoke_test / signal_studio_judge_stats (network trio) + studio_tool / workflow_run_tool (async trio) + competitor_comparison_tool / research_and_create_tool / task_breakdown_tool (row-create trio) + work_tool / intelligence_tool (large-action pure-ORM candidates).

**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix).

**Total remaining tools to close:** ~57. Post-substrate sweep pace at S2905-S2913 = 4/4/3/4/4/4/1/4/4/4 tools/batch. Extrapolated remaining ~10 sessions at accelerated pace with trustworthy harness.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2913 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2913: zero A4 spend — pure sweep-batch engineering (3 batches shipped).** A1 shipping spend was 3 PRs + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2913)

See:
- **S2913 handoff (current):** `docs/handoffs/SESSION_2913_SLICE_3_BATCHES_1_2_3.md`
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
- **S2913 per-tool validation docs (this session's 12):** at `docs/research/tools/validation/`
  - `paid_interest_status_validation.md`, `platform_awareness_tool_validation.md`, `persona_tool_validation.md`, `platform_config_tool_validation.md` (batch 1)
  - `active_repo_tool_validation.md`, `db_health_tool_validation.md`, `conversation_tool_validation.md`, `remember_tool_validation.md` (batch 2)
  - `messaging_tool_validation.md`, `learning_tool_validation.md`, `dream_tool_validation.md`, `governance_tool_validation.md` (batch 3)
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 55 non-substrate post-S2913)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (unchanged from S2911).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
