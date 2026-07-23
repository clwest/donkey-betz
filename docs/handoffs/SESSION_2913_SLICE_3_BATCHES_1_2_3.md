# Session 2913 — Slice 3 batches 1+2+3 (td_handlers_core sweep opens + accelerates)

**Session:** S2913
**Date:** 2026-07-23
**Closed at HEAD:** `d6fc0480c`
**Wrapper pin at open:** `pa-02a01c6f2a754e53` (bumps to next-session pin at close via `session_lifecycle close`)
**Session cumulative:** 3 batches shipped × 4 tools = **12 tools closed** in Slice 3

---

## READ THIS FIRST

S2913 opened the `td_handlers_core` sweep (Slice 3, 22 tools) after Slice 2 closed at S2912. Session shipped **3 accelerated batches** matching S1218-style triple-ship cadence. All batches used the scoped-to-READ_ONLY-subset shape ratified at batch 1 T0 SIGN — unsafe siblings pinned MUTATION/IRREVERSIBLE via per-action `TOOL_ACTION_METADATA` records, harness `resolve_safety()` skips at dispatch.

## PRs shipped this session

- u-d-b PR [#3453](https://github.com/clwest/donkey-betz-platform/pull/3453) — Slice 3 batch 1 (4 tools), merged at `00fcb352f`.
- u-d-b PR [#3454](https://github.com/clwest/donkey-betz-platform/pull/3454) — Slice 3 batch 2 (4 tools), merged at `b2a2ae0e5`.
- u-d-b PR [#3455](https://github.com/clwest/donkey-betz-platform/pull/3455) — Slice 3 batch 3 (4 tools) + session close batch, merged at `d6fc0480c`.
- u-d-b PR `<TBD>` — S2913 close cascade (handoff + 00-START refresh + wrapper pin bump).

## Batches shipped

### Batch 1 (PR #3453) — actionless + scoped-to-READ_ONLY-subset opener

- `paid_interest_status` (actionless — TOOL_DEFAULTS shape)
- `platform_awareness_tool` (7 actions: 6R + `verify_deploy` MUTATION excluded — HTTP)
- `persona_tool` (2 actions: `list` R + `invoke` MUTATION excluded — LLM)
- `platform_config_tool` (5 actions: 4R + `web_config` MUTATION excluded — HTTP)

Rigby T0 SIGN AGREE-with-edits (9 repo_tool probes, tool-grounded). Rigby T1 SIGN AGREE-with-edits (V2 explicit action-pinning applied to defend against default-drift risk).

### Batch 2 (PR #3454) — scoped-to-READ_ONLY-subset continuation

- `active_repo_tool` (3 actions: `get` R + `set`/`clear` MUTATION excluded — cache writes)
- `db_health_tool` (7 actions ALL READ_ONLY at env='local' default; env='prod' urllib RPC escalation documented-not-tested per Rigby V2/V4)
- `conversation_tool` (5 actions: `get`+`recent` R + `search`/`summary`/`pin_memory` MUTATION excluded)
- `remember_tool` (4 actions: `list`+`search` R + `save` MUTATION + `delete` IRREVERSIBLE excluded)

**Notable Claude course-correction:** Rigby T1 V1 assumed `conversation_tool.search` was pure ORM. Claude direct handler read caught `EmbeddingService.create_embedding(query)` at handler line 2038 (LLM cost per invocation). Reclassified as MUTATION unilaterally per `feedback_verify_rigby_tool_runs_before_trusting_sign`. Documented in doc §5a.

### Batch 3 (PR #3455) — session close batch

- `messaging_tool` (3 schema-enum actions ALL R + `send_message` schema-hidden defense-in-depth MUTATION classified in metadata for completeness)
- `learning_tool` (6 actions: `list_candidates`/`list_approved`/`list_expired`/`stats` R + `approve`/`reject` MUTATION excluded)
- `dream_tool` (6 actions: `list_top`/`details`/`stats` R + `approve`/`dismiss`/`create` MUTATION excluded)
- `governance_tool` (17 actions gateway: 11R + 6M — largest metadata block this session)

**Rigby T1 SIGN verify-before-commit flags — all 4 verified via direct handler read:**
1. Messaging read-receipt concern: NO writes on `unread_count` in any covered read path.
2. Messaging `send_message`: NOT in schema enum but handler exists (settings-gated `MESSAGING_TOOL_ALLOW_SEND=False` per Session 1253 PR 4); added as MUTATION metadata for defense-in-depth documentation.
3. Governance `decision_create` naming: clean (schema singular; handler `DECISIONS_MAP` at :3767 maps to underlying `'create'`).
4. No LLM cost on any covered read action: verified (learning/dream/governance all pure ORM or gateway forwarding to pure ORM).

**Notable async cascade:** `dream_tool.approve` fires `post_save` signal → `promote_to_initiative() + execute_single_dream.delay()` (Celery cascade — widest MUTATION blast radius in batch 3). Documented in doc §5a.

## Sweep progress (post-S2913)

- **Slice 3 (`td_handlers_core`):** 3 batches × 4 tools = **12/22 shipped; 10 remaining.**
- Total corpus untested: 69 → **57** (-12).
- Gap map: 32 → **44 full** + 8 partial + 57 untested.
- Session cumulative pace: **12 tools / 3 batches / 1 session** — matches S1218 triple-ship cadence.
- Full corpus close estimate at accelerated pace: ~4-6 more sessions.

## Concern C — Slice 3 schema↔doc drift count reaches 3

Per Rigby T0 SIGN Q4 Concern C threshold (batch 1 open): schema `description` field does not enumerate all discrete `action` enum values on 3 batch tools this session:
1. `platform_awareness_tool` (batch 1) — 7 actions, description mentions action-families.
2. `platform_config_tool` (batch 1) — 5 actions, description mentions action-families.
3. `governance_tool` (batch 3) — 17 actions, description mentions 5 action-families.

**Fold candidate promotion evaluated at Slice 3 CLOSE, NOT mid-slice** per D6 moratorium (no substrate arc opens). Watch remaining 10 Slice 3 tools for further instances. If pattern persists across ≥5 core tools by Slice 3 close, propose "action-enum appendix" or auto-doc extract as future substrate arc via explicit Chris directive.

## Rigby joint SIGN cycles (3 substantive this session, zero rubber-stamp)

- **Batch 1 T0 SIGN:** AGREE-with-edits (9 `repo_tool` probes). Q1 (c)→(b) grep-first→actionless-only opener + Q2(a) bridge-suspect confirmation (fleet_health / db_health(prod) / http_smoke_test all direct HTTP, not S2909 bridge — excluded) + Q2(b) preflight-envelope not required + Q3 TOOL_DEFAULTS for actionless + explicit read-action pinning for mixed + Q4 zoom-out concerns A/B same-PR, C/E forward-carry.
- **Batch 2 T1 SIGN:** AGREE-with-edits — V1 with Claude course-correction on `conversation_tool.search` LLM cost + V2 db_health env='local' vs env='prod' classification defensible + V3 Concern C count stays at 2 + V4 db_health env='prod' documented-not-tested.
- **Batch 3 T1 SIGN:** AGREE-with-edits — 4 verify-before-commit flags all verified via direct handler read.

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

- `make recycle-all` after each of 3 PRs. All 3 recycles clean:
  - Batch 1: `sha=00fcb352f16b, surviving=none`
  - Batch 2: `sha=b2a2ae0e5434, surviving=none`
  - Batch 3: `sha=d6fc0480c089, surviving=none`

## S2914 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 3 batch 4

**No blocking Chris D-verdict.** S2913 shipped 3 PRs cleanly; harness trustworthy post-S2909 arc; batch shape proven across 3 batches; sweep-arc pace accelerating.

**Remaining Slice 3 corpus (10 tools):**
- Network-suspect (defer to network-focused batch): `fleet_health`, `http_smoke_test`, `signal_studio_judge_stats` (all direct HTTP).
- Celery/async-suspect (defer to MUTATION-coverage batch): `studio_tool`, `workflow_run_tool` (both have `apply_async`).
- Row-create-suspect: `competitor_comparison_tool` (`.create` at :2761), `research_and_create_tool`, `task_breakdown_tool`.
- Pure-ORM read candidates: `work_tool` (16 actions with clear R/M split), `intelligence_tool` (20+ actions, mostly R).

**S2914 T0 SIGN questions to route to Rigby:**
- **Q1 Batch composition:** continue pure-ORM opener shape with 3-4 more tools (work_tool as centerpiece is the highest-leverage remaining pick), OR pivot to a network-focused batch to close fleet_health / http_smoke_test / signal_studio_judge_stats trio in one dedicated batch?
- **Q2 Substrate observation:** 3 batches proven the shape; consider closing Slice 3 sweep at 15/22 tools + 7 deferred to a dedicated MUTATION-coverage batch across Slices 3+4+5, OR push to close Slice 3 fully via more targeted per-tool investigation?
- **Q3 zoom-out ask:** at 3 batches shipped, what does the pattern *fail* to teach us that batch 4 T0 should target?

### Alternative Step 1 candidates (unchanged from S2913 open)

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
- **No Concern C schema↔doc drift substrate arc mid-slice.** 3 instances in Slice 3 batch 1+3; evaluated at Slice 3 CLOSE per Rigby T0 Q4 threshold + D6 moratorium.
- **No `post_save signal cascade` substrate arc without explicit Chris directive.** `dream_tool.approve` is a candidate class-example; forward-carry ledger observation only.
- **No harness-level soft_error accounting substrate arc without explicit Chris directive.** Slice 3 batch 2+3 observed harness soft_error counts don't distinguish structured `_handler_error` (S2886) from inline `{error}` (drift); forward-carry ledger observation.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — unchanged.
- **Bridge call observability rename-risk** — unchanged.
- **Close-ceremony ledger-staleness gate** — unchanged.
- **Sweep shape doc-only defers semantic assertions** — unchanged.
- **Sweep batch cadence outcome gate** — unchanged.
- **Mutation-heavy single-tool batch pattern** — unchanged.
- **2-tier evidence template promotion** — unchanged.
- **Sweep-arc pace sustainability substrate arc** — CLOSED at S2904.
- **Response-level introspection field creep** — unchanged.
- **S2905 metadata-pattern-selection lint** — batch 1 used per-action (via TOOL_ACTION_METADATA for mixed) + TOOL_DEFAULTS for actionless; no shadowing. Batch 2+3 same shape.
- **S2906/S2907/S2908 Ledger candidates** — unchanged.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate: `obs_tool_validation.md` §6.1 conflates OBS_DISABLED vs BRIDGE_UNREACHABLE** — unchanged.
- **S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action** — unchanged.
- **S2909 FT-1 through FT-5** — unchanged; FT-5 (`minimal_safe_args_v2`) still tracked as candidate arc.
- **S2910 FT-1 (Ledger #33) — Entrypoint-side context-injection test coverage gap** — unchanged.
- **S2910 FT-2 (Ledger #34) — Doc-pointer-verification lint candidate** — unchanged.
- **S2911 Ledger #35 — Envelope-shape inconsistency on opportunity_manager.delete + task_manager.delete** — unchanged.
- **S2911 Ledger #36 — Candidate Fold Trigger #1 (schema-drift-fix)** — NOT corroborated at S2913 batches 1+2+3.
- **S2911 Ledger #37 — HIDDEN MUTATION planner-safety pattern** — unchanged.
- **S2912 §5a mitigation note — `dry_run` add-flag pattern for actionless mutation-class dispatchers** — unchanged.
- **S2913 batch 2 Ledger candidate — envelope drift on `active_repo_tool.set/clear` fail-loud + `conversation_tool.get` missing-arg** — inline `{ok: False, error}` envelope drift class. Not urgent (MUTATION-skipped or fail-loud). Forward-carry.
- **S2913 batch 3 Ledger candidate — dream_tool `dream_type` schema description ('creative_idea') vs handler ('user_request') default drift** — minor; forward-carry.
- **S2913 batch 3 Ledger candidate — messaging_tool `send_message` schema-hidden defense-in-depth pattern (Session 1253 PR 4)** — pattern worth watching if more schema-hidden handler paths surface in Slice 3+4+5. Forward-carry.
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

**Substrate arcs CLOSED:** S2900-S2904 + S2909 + S2911.

**Total remaining tools to close:** ~57. Post-substrate sweep pace at S2905-S2913 = 4/4/3/4/4/4/1/4/4/4 tools/batch. Extrapolated remaining ~10 sessions at accelerated pace.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2913)

See:
- **S2913 handoff (current):** this file
- **S2912 handoff:** `docs/handoffs/SESSION_2912_SLICE_2_CLOSE.md`
- **S2911 handoff:** `docs/handoffs/SESSION_2911_SLICE_2_BATCH_6A_PLUS_DRIFT_FIX.md`
- **S2910 handoff:** `docs/handoffs/SESSION_2910_SLICE_2_BATCH_5_MIXED_COMPOSITION_SWEEP.md`
- **S2913 per-tool validation docs (this session's 12):** at `docs/research/tools/validation/`
  - `paid_interest_status_validation.md`
  - `platform_awareness_tool_validation.md`
  - `persona_tool_validation.md`
  - `platform_config_tool_validation.md`
  - `active_repo_tool_validation.md`
  - `db_health_tool_validation.md`
  - `conversation_tool_validation.md`
  - `remember_tool_validation.md`
  - `messaging_tool_validation.md`
  - `learning_tool_validation.md`
  - `dream_tool_validation.md`
  - `governance_tool_validation.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 55 non-substrate post-S2913)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (unchanged from S2911).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
