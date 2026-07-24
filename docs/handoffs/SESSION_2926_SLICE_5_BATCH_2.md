# Session 2926 — Slice 5 batch 2 (quartet — advances Slice 5 to 8/14) + heartbeat wrong-model fix

**Session:** S2926
**Date:** 2026-07-23
**HEAD at open:** `a28953a7c` (S2925 close cascade)
**HEAD at close:** `12ca8848c` (+ close cascade PR to follow)
**Fresh pin at open:** `pa-7e17133240eb4c44` (minted at S2925 close; wrapper freshly rewritten — zero mint work at S2926 open)
**Fresh pin at close:** _TBD_ (minted by `session_lifecycle close`)
**PRs shipped:** 3 (#3484 heartbeat wrong-model fix + #3485 Slice 5 batch 2 quartet + close cascade PR)

---

## Overview

S2926 continued Slice 5 (`tool_dispatcher.py` — 14 tools) with batch 2 authoring. Session opened cleanly — S2925 close cascade had already committed the wrapper pin bump so no S2843-style pin-management debt to unwind at open.

Two substantive PRs shipped:
1. **PR #3484** — `AgentTaskExecution` heartbeat wrong-model fix at `core/tasks_agents.py:2481`. Bug discovered mid-turn-2 SIGN cycle when Rigby's `execution_history_tool` verify surfaced worker-log warnings from S2925 batch 1 dispatches.
2. **PR #3485** — Slice 5 batch 2 quartet (`create_brand_video` + `video_editing_agent` + `three_d_generation_agent` + `character_training_agent`).

Additionally: Rigby filed a workspace-deliverable engineering item (`5703a6c8-9bfa-4b11-81cc-baff7c90b3d5`) documenting a **CompetitorAnalysisAgent content-shape FAIL** surfaced during batch 1 completion-verify carry-forward — the agent runs cleanly (`status='completed'`) but returns a generic "concept too vague" note with no competitor list and no SWOT structure. Explicitly scoped OUT of this session per Chris D-verdict; future targeted engineering slate.

Session outcome:
- 4 Slice 5 tools moved to `validated_full` (gap map `73/10/7/26 → 77/10/7/22`).
- 2 completion-verify representatives (Rigby Q5(i) hold at 2/batch): `create_brand_video` (WorkflowAgent, distinct tool_name from batch 1's `create_project_from_research`) + `character_training_agent` (media-family, Replicate FLUX LoRA).
- 1 latent-bug fix (heartbeat) shipped as sibling PR.
- 1 engineering-item filed for future work (CompetitorAnalysisAgent).

---

## Rigby SIGN cycle arc (turn 1 → turn 2 → joint recommendation)

**Turn 1** (pin `pa-7e17133240eb4c44`, task `c10d2e91-...`):
- 10+ `repo_tool` receipts (non-empty tool_runs — real SIGN, not rubber-stamp).
- Q1 quartet proposal accepted as-authored (grounded in `_tool_to_agent_name` mapping + `tool_dispatcher.py` register lines).
- Q4 heartbeat drift → recommended standalone PR (governance-level, no code evidence pulled yet).
- Q5(i) push-back accepted: hold completion-verify quota at 2/batch until Q2 + Q4 close the loop.
- Q2 + Q3 F-BLOCKING — Rigby correctly refused to answer without additional grounding (celery_task_ids for Q2; WorkflowAgent code branching for Q3).

**Turn 2** (task `12dd02d7-...`, 11+ tool receipts including `execution_history_tool.detail` + `orm_inspect_tool` allowlist-blocked probe + `repo_tool`):
- **Q2 CompetitorAnalysisAgent content-FAIL** (biggest finding of the session — see next section).
- **Q3 WorkflowOrchestrationAgent mapping-vs-class asymmetry** confirmed; verdict: cover ONE (`create_brand_video`), defer `workflow_orchestration_agent` to batch 3.
- **Q4 code-verdict** returned as F-BLOCKING (Rigby hadn't pulled the heartbeat write site yet); Claude closed via direct Grep — `AgentTaskExecution.objects.filter(...).update(last_heartbeat_at=...)` at `tasks_agents.py:2481` writes to a model that has no `last_heartbeat_at` field (`core/models/agents_registry/models.py:434`); exception caught + logged (silent to callers, non-silent in worker log).

**Joint recommendation → Chris:** batch 2 quartet + heartbeat fix standalone PR + CompetitorAnalysisAgent finding as separate engineering item. Chris D-verdict: **"yes to all three"**.

---

## Q2 CompetitorAnalysisAgent content-shape FAIL discovery

Rigby's turn 2 `execution_history_tool.detail id=759198d5-259c-4cc5-966a-f167d4102125` on the S2925 batch 1 `competitor_analysis_agent` execution surfaced:

- `output_data.message` verbatim: `"⚠️ Note: Concept is too vague to fully evaluate but could be viable if 'test dispatch' is sharpened into a specific, addressable service (e.g., medical sample logistics, software test orchestration, or home-test kit fulfillment) with a clear customer segment and business model.\n\nCompetitive analysis completed with 2 data sources"`
- **NO competitor list. NO SWOT. Two spider_query hits — both mostly-unrelated to the concept (Palantir article, etc.).**
- Contrast: BrandStrategyAgent on the same `"test dispatch"` input produced explicit `"BRAND POSITIONING ANALYSIS"` + `"TARGET AUDIENCE ALIGNMENT"` sections (Q2.1 PASS).

**Implication:** the agent runs to `status='completed'` and returns SOMETHING, but that something violates the expected output schema. Would ship as false PASS in any receipt-verify-only sweep.

**Suspected causes (not verified this session):** (a) prompt template doesn't enforce competitor-list + SWOT output schema; (b) vague input triggered early bail-out via the "concept too vague" template; (c) downstream JSON-parsing step exists but was bypassed.

**Filed as workspace deliverable `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5`** by Rigby (Donkey Betz workspace `b4503364-...`, `deliverable_type='engineering_backlog'`, `category='agent_quality'`, status='ready' — Rigby noted the deliverable_tool doesn't accept `status='open'`; open-backlog semantics encoded via tags instead).

**Session-scope decision (Chris D-verdict):** file as separate engineering item, do NOT fold into batch 2 sweep PR. Future targeted engineering slate.

---

## PR #3484 — AgentTaskExecution heartbeat wrong-model fix

**Bug:** `core/tasks_agents.py:2481` inside `_impl_execute_agent_task`'s heartbeat thread was writing:

```python
rowcount = AgentTaskExecution.objects.filter(id=_hb_execution_id).update(last_heartbeat_at=timezone.now())
```

`AgentTaskExecution` (from `core.models.agents_registry`, imported module-level at :27) has NO `last_heartbeat_at` field. Django's `.update()` raised `FieldError: AgentTaskExecution has no field named 'last_heartbeat_at'` every tick. The exception was caught by `logger.exception(...)` at :2499 — worker-log visible but caller-invisible. Result: heartbeat never advanced → cleanup watchdog would eventually mark long-running executions stale despite the row being live.

**Fix:** switch to `AgentExecution` (from `core.models_unified_system`, imported at function scope :2121, has `last_heartbeat_at` + a `touch_heartbeat()` helper at `models_unified_system.py:1018`). `execution_record` (created at :2318/:2322) is already an `AgentExecution` instance. This matches the sister heartbeat write at `agent_router.py:2989`.

Preserved the rowcount observability signal (:2485–2491) so the "row disappeared" warning still fires.

**Discovery mechanism:** S2926 turn 2 SIGN — the wrong-model bug had been latent since Session 1100 (the heartbeat field addition per audit doc `docs/research/domains/observability/1703_observability_cat_c_agent_execution_audit.md:176`). S2925 batch 1 CustomerResearchAgent execution `b7681140-...` was the first observed instance in the handoff record.

**Shipped as standalone PR** ahead of batch 2 quartet per Q4 verdict — enables clean heartbeat advancement during batch 2 completion-verify.

Post-merge sha=`cea3f9215`, `make recycle-all` clean (zero surviving old PIDs).

---

## PR #3485 — Slice 5 batch 2 quartet

### Composition + rationale

Per Rigby Q1 verdict (grounded in `_tool_to_agent_name` mapping + register lines):

| Tool | Mapped agent | Family | Role in batch |
|---|---|---|---|
| `create_brand_video` | `WorkflowAgent` | Orchestration | **WorkflowAgent-family completion-verify representative** (distinct tool_name from batch 1's `create_project_from_research`) |
| `video_editing_agent` | `VideoEditingAgent` | Media Creation & Editing | Receipt-verify only |
| `three_d_generation_agent` | `ThreeDAgent` | Media Creation & Editing | Receipt-verify only |
| `character_training_agent` | `CharacterTrainingAgent` | Media Creation & Editing | **Media-family completion-verify representative** (test-dispatch scoped to `create_character` — no billable Replicate compute) |

Rationale: 1 WorkflowAgent entry point (create_brand_video) + 3 Media Creation & Editing tools — completes the "sample every agent-family present in Slice 5" pattern before batch 3.

### Q3 workflow_orchestration_agent mapping-vs-class-file asymmetry (discovery, not shipped)

Rigby confirmed via `repo_tool` inspection:
- `td_handlers_agents.py:123–127` maps `'workflow_orchestration_agent'` → `'WorkflowAgent'`
- `core/agents/workflow_orchestration_agent.py:105+` defines a real `WorkflowOrchestrationAgent(BaseAgent)` class (25278 bytes, 580 lines) with 16+ built-in workflow templates (research_and_create_logos, youtube_thumbnail_package, etc.)
- Cross-check: 10 files reference `WorkflowOrchestrationAgent` — including `core/services/workflow_builder.py:378` which imports and uses it. So the CLASS is actively consumed, but the TOOL name routes elsewhere.

**Not corrected this session.** Documented in `create_brand_video_validation.md` §Related. Deferred to batch 3 investigation — needs to decide whether this is intentional wrapper strategy or stale mapping to fix.

### §5a distribution table (batch 2 slice — end-to-end classification)

| Tool | End-to-end tier | Notes |
|---|---|---|
| create_brand_video | `external` (**amplified**) | WorkflowAgent recursive fanout (2nd corroborating instance; still gated per S2925 forbidden entry until 3rd) |
| video_editing_agent | `external` | Wrapper + LLM + media provider (ffmpeg/Cloudinary/Replicate) |
| three_d_generation_agent | `external` | Wrapper + LLM + Replicate (long-running 3D compute) |
| character_training_agent | `external` (with out-of-band tail) | Wrapper + LLM + Replicate FLUX LoRA (billable, out-of-band training persists beyond parent AgentExecution) |

All 4 filled Appendix A (Async-Fanout). The `character_training_agent` doc adds a note about **third-tier identifier surface** (Replicate prediction id in AgentResult, beyond AgentExecution / celery_task_id) — first exercise this ship; documented as authoring detail.

### Semantic-alias contract for WorkflowAgent-mapped tools (create_brand_video vs create_project_from_research)

Q3 payoff: since `_handle_agent_tool` does not propagate the originating tool_name to WorkflowAgent (WorkflowAgent receives only the caller's `task` string + `context` dict), the ONLY differentiator between `create_brand_video`, `create_project_from_research`, and `workflow_orchestration_agent` behavior is caller-shaped task text. If the LLM caller (Rigby) shapes different task strings per tool_name, behavior differs; if not, they are semantic aliases at the platform layer.

Post-merge verify (§6 step 4 of `create_brand_video_validation.md`) exercises this — compares planner `tool_calls` from `create_brand_video` dispatch vs the S2925 `create_project_from_research` execution `9035879f-c816-4689-95d0-146db6eeb642`.

### Post-merge live-verify at sha `12ca8848c` (per PLAYBOOK-7.4.4)

**`make recycle-all` clean:** sha=`12ca8848c10e`, zero surviving old PIDs, 5 fresh workers + beat.

**Rigby receipt-verify (task `52d3492f-...`):** 4/4 PASS.

| Tool | task_id | agent | envelope shape |
|---|---|---|---|
| create_brand_video | `39d44f0a-...` | `WorkflowAgent` | ✅ |
| video_editing_agent | `cf108119-...` | `VideoEditingAgent` | ✅ |
| three_d_generation_agent | `5661edd7-...` | `ThreeDAgent` | ✅ |
| character_training_agent | `e7a1fcaf-...` | `CharacterTrainingAgent` | ✅ |

**Rigby completion-verify (2nd-round dispatches at task_ids `7c7067c8-...` create_brand_video + `8e773972-...` character_training_agent):** Claude polled `AgentExecution` ORM directly (via `manage.py shell`) — **see § "Completion-verify outcome" below** (background ORM poll running as this handoff is drafted).

---

## Completion-verify outcome

**Both completion-verify targets landed successfully via direct `AgentExecution` ORM poll (Claude self-executed via `manage.py shell` after Rigby's dispatches returned STARTED/PENDING).**

### character_training_agent (task_id `8e773972-...`) — **PASS**

- **status:** `completed`
- **exec_ms:** 29,410 (~30s — fast path as expected; no Replicate compute)
- **output_data top-level keys:** `data`, `error`, `content`, `message`, `metadata`, `warnings`, `artifacts`, `agent_name`, `latency_ms`, `run_status`, `tool_calls`, `completed_at`, `error_message`, `result_preview`, `error_signature`
- **tool_calls[0]:** `{"tool": "create_character", "result": {"error": "At least 5 training images are required", "success": false}, "arguments": {"name": "test_dispatch_char", "image_urls": [], "auto_submit": false, "description": "Test dispatch character placeholder for pipeline validation. No training submission requested.", "trigger_word": "TDC", "training_steps": 1000}}`
- **`has_replicate_id_mention: False`** — confirms NO `submit_training` triggered → **zero billable Replicate compute** as scoped
- **Agent LLM planner correctly parsed the test-dispatch scope** — `auto_submit=False` in the tool_call arguments, matches the "Do not submit training" instruction verbatim
- The `create_character` sub-tool's fail-loud on `"At least 5 training images are required"` is **expected behavior** per the `character_training_agent_validation.md` §5 documented empty-state pattern — not a bug

### create_brand_video (task_id `7c7067c8-...`, WorkflowAgent) — **in_progress at close** (same as batch 1's create_project_from_research)

- **status:** `in_progress` at ~10 min post-dispatch (creation timestamp `2026-07-24 05:02:59Z`)
- **`heartbeat_advancing: TRUE`** — `last_heartbeat_at` = `2026-07-24 05:09:29Z`; **seconds_since_heartbeat: 16s** vs **seconds_since_created: 406s** → heartbeat is actively writing (~2min tick interval matches `_HB_TICK_S = 120`).
- **This is the first-ever positive verification that PR #3484 landed cleanly.** The heartbeat write now targets the correct `AgentExecution` model with the `last_heartbeat_at` field; the row's timestamp advances instead of freezing at creation. Pre-fix behavior (from S2925 batch 1's CustomerResearchAgent execution `b7681140-...`) was silent-log `FieldError` + frozen `last_heartbeat_at`.
- Recursive fanout ongoing — planner tool_calls not yet observable via `output_data` (empty at in_progress). Full semantic-alias comparison (§6 step 4 of `create_brand_video_validation.md`) deferred to next-session cross-check when this execution reaches `completed`.

### Cross-cutting outcome

- **Heartbeat fix (PR #3484) confirmed live-verified.** Fix landed cleanly; long-running agents in Slice 5 now have accurate `last_heartbeat_at` tracking. Cleanup watchdog will no longer mis-flag in-progress agents as stale.
- **CharacterTrainingAgent test-dispatch protocol works as documented.** Media-family completion-verify pattern established for batches 3+.
- **create_brand_video WorkflowAgent recursive fanout** proceeding as batch 1 pattern predicted. Completion-detail comparison for the semantic-alias contract deferred to next-session ORM poll.

---

## Rigby Tool Gap Ledger updates this session

No new entries appended to Rigby Tool Gap Ledger (`5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`).

Adjacent workspace deliverable filed (Donkey Betz workspace, not Rigby Tool Gap Ledger, per Rigby's own workflow guidance that agent-quality issues ≠ tool-surface limitations):
- **`5703a6c8-9bfa-4b11-81cc-baff7c90b3d5`** — CompetitorAnalysisAgent content-shape FAIL engineering-backlog item. `category='agent_quality'`, `status='ready'`.

**Rigby self-flagged tool-surface limitation observed:**
- `deliverable_tool.create` accepts `status='ready'` but not `status='open'` → workaround was tags for open-backlog semantics. Minor Rigby Tool Gap candidate — not appended this session (Rigby's discretion).
- `orm_inspect_tool` allowlist blocks `AgentExecution` (returned `error_code='legacy_error'` — the 22nd corroborated legacy_error instance, still post-D6 gated per S2925 forbidden entry). Rigby worked around by using `execution_history_tool` — the intended read surface for AgentExecution. This is the same Ledger #31 orm_inspect_tool allowlist expansion candidate (MEDIUM; ~1-2 hours); recurrence documented but not promoted to Fold.

---

## Sweep progress tracker (Path B ratified S2892)

- **Slice 1 (`td_handlers_ops`, 17 tools):** UNCHANGED.
- **Slice 2 (`td_handlers_agents`, 25 tools):** **CLOSED at S2912.**
- **Slice 3 (`td_handlers_core`, 22 tools):** **CLOSED at S2917 (22/22).**
- **Slice 4 (`td_handlers_gateway`, 17 tools):** **CLOSED at S2924 (17/17).**
- **Slice 5 (`tool_dispatcher`, 14 tools):** **OPEN — 8/14 at S2926 close.** 6 remaining: `content_strategy_agent`, `content_writer_agent`, `marketing_strategy_agent`, `strategic_review`, `image_editing_agent`, `workflow_orchestration_agent`.

**Total remaining tools to close:** ~22 (post-S2926 sweep-scope estimate).

**Session cumulative pace:** 2 substantive PRs + close cascade PR in 1 session — matches recent pace (S2924 shipped 2 substantive + close; S2925 shipped 3 substantive + close).

---

## Forbidden entries carried forward (unchanged from S2925 unless noted)

D6 STRATEGIC DISCOVERY MORATORIUM remains in force. All S2925 forbidden entries carry forward.

### Corroborating triggers observed this session (advancing counters — NOT promoting)

- **"Recursive fanout dispatch topology proof"** — 2nd corroborating instance (create_brand_video, this session). S2925 was 1st (create_project_from_research). Still gated per S2925 forbidden entry until 3rd instance.
- **"Undocumented envelope field (`error_code: 'legacy_error'`)"** — S2926 turn 2 surfaced 22nd instance (`orm_inspect_tool` allowlist rejection during Rigby's Q2 verify). Unchanged D6-gate status.
- **"Migration-history-marks-applied-but-table-deleted-downstream"** — no new instances this session; still 1st (Ledger #33 at S2925). PR #3484 is NOT this pattern (different bug class — wrong-model reference not migration drift).

### NEW S2926 forbidden entries

- **No "wrong-model reference to sister model in same registry" Fold promotion without 2nd instance.** 1st (PR #3484 `AgentTaskExecution` vs `AgentExecution` heartbeat write). Root shape: file imports two Model classes with overlapping names; a write site uses the wrong one; wrong class lacks the field; caught by exception log; symptom-invisible to callers. Requires 2nd instance for promotion.
- **No "content-shape FAIL surfaces only under completion-verify, not receipt-verify" Fold promotion without 2nd instance.** 1st (CompetitorAnalysisAgent, Q2 discovery). Root shape: agent runs cleanly to `status='completed'` + returns AgentResult, but output_data.message fails an expected content schema (e.g., missing structured competitor list / SWOT). Receipt-verify passes; completion-verify without content-shape check also passes. Requires 2nd instance for promotion of the diagnostic pattern.
- **No "third-tier identifier surface in AgentResult (external-provider id beyond AgentExecution + celery_task_id)" Fold promotion without 2nd instance.** 1st (`character_training_agent` Replicate prediction id documented in the validation doc). Requires 2nd instance for pattern promotion.
- **No "media provider egress as distinct §5a downstream axis" Fold promotion without 2nd instance.** 1st (batch 2 media agents' Cloudinary/ffmpeg/Replicate egress documented as an addition to the LLM-provider egress axis). Requires 2nd instance for promotion.
- **No "semantic-alias contract for shared-agent tool_names" Fold promotion without corroboration.** 1st exercise (`create_brand_video` vs `create_project_from_research` in the same WorkflowAgent). Documented as an authoring convention in `create_brand_video_validation.md` §Related; requires 2nd instance for pattern promotion.

---

## What's queued for S2927

**S2927 first-action candidate:** Slice 5 batch 3 quartet SIGN cycle. Ledger candidates:
- Cover `workflow_orchestration_agent` (with the mapping-vs-class-file asymmetry investigation as a first-order §6 discovery)
- Cover 2–3 content-strategy tier tools (`content_strategy_agent`, `content_writer_agent`, `marketing_strategy_agent`, `strategic_review`) — new agent-family class
- Optionally: cover `image_editing_agent` (last remaining media-family tool)

**Alternative Step 1 candidates:**
- Ledger #34 broader stale-model sweep (multi-hour engineering)
- CompetitorAnalysisAgent content-shape FAIL remediation (deliverable `5703a6c8-...`)
- WorkflowOrchestrationAgent mapping fix (~30-60 min investigation + fix)

**Still-deferred (from S2925 close list, unchanged):**
- Rigby Tool Gap Ledger #31 orm_inspect_tool allowlist expansion
- Bundled dev-env drift slate
- Phase 0 heading fixes (8 tools)
- Slice 1.5b autopilot mutations
- Docs restructuring arc

---

## Twin-pointer docs card (per feedback_twin_pointer_docs_at_boundaries)

**Repo `/docs/` tree — current S2926 batch 2 substrate:**
- `docs/research/tools/validation/create_brand_video_validation.md`
- `docs/research/tools/validation/video_editing_agent_validation.md`
- `docs/research/tools/validation/three_d_generation_agent_validation.md`
- `docs/research/tools/validation/character_training_agent_validation.md`
- `docs/audits/PA_TOOLS_GAP_MAP.md` (regenerated; 77/10/7/22)
- `docs/PA_TOOL_AUDIT.md` (regenerated; validation-xref refreshed)

**Workspace UI `/workspaces` — current S2926 substrate:**
- Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` — CompetitorAnalysisAgent content-FAIL engineering item `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5`
- Architecture & Research workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` — no S2926 ratification records this session (no methodology changes)
- Rigby Tool Gap Ledger deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` — no S2926 appends (Rigby self-noted deliverable_tool `status='open'` limitation but did not append)

---

## Session close checklist

- [x] PR #3484 heartbeat fix merged (`cea3f9215`) + recycled clean.
- [x] PR #3485 batch 2 quartet merged (`12ca8848c`) + recycled clean.
- [x] Rigby engineering item filed (`5703a6c8-...`).
- [x] Rigby receipt-verify 4/4 PASS.
- [x] Completion-verify outcome logged (character_training_agent PASS + create_brand_video in_progress with heartbeat advancing — PR #3484 live-verified).
- [x] `00-START-NEXT-SESSION.md` refreshed for S2927.
- [ ] `session_lifecycle close --label s2926-slice-5-batch-2-plus-heartbeat-fix` — mints S2927 pin + rewrites wrapper.
- [ ] Close cascade PR merged + wrapper diff committed (per `feedback_commit_wrapper_pin_bump_at_close`).
