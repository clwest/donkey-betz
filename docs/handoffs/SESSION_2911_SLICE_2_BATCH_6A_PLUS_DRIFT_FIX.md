# SESSION 2911 — Slice 2 batch 6a + reasoning_engine drift-fix (2-PR session)

**Closed:** 2026-07-23
**HEAD at close:** `547fba978`
**Wrapper pin retired:** `pa-5b657e2f37f548b9` (label: s2910-slice2-batch5 → in-session-used for s2911-slice2-batch6a-plus-drift-fix)
**PRs shipped:**
- [#3448](https://github.com/clwest/donkey-betz-platform/pull/3448) — S2911 Slice 2 batch 6a (4 tools scoped-to-READ_ONLY subset) — merged at `a35ebd5c5`.
- [#3449](https://github.com/clwest/donkey-betz-platform/pull/3449) — S2911 reasoning_engine_tool drift-fix (pre-req for batch 6b) — merged at `547fba978`.
- Close cascade PR — this handoff + 00-START refresh + wrapper pin bump.

---

## What shipped

### PR #3448 — Slice 2 batch 6a (4 tools)

Fourth accelerated PA-tools sweep batch in Slice 2 post-S2909 substrate cleanup. First scoped-to-READ_ONLY-subset batch of the remaining Slice 2 tools — write actions excluded via per-action `TOOL_ACTION_METADATA` seeds (harness `resolve_safety()` skips MUTATION + IRREVERSIBLE at dispatch).

**Batch composition (all pure ORM — no bridge dependencies):**
- **`opportunity_manager_tool`** — 6 actions: 3R covered (`list`/`stats` success + `get` clean `error_captured` on missing opportunity_id); 2 MUTATION + 1 IRREVERSIBLE (`delete` cascade-to-OpportunityTask) skipped.
- **`task_manager_tool`** — 6 actions: 2R covered; 3 MUTATION + 1 IRREVERSIBLE skipped. **HIDDEN MUTATION on `create`** when `opportunity_id` absent — implicit standalone `Opportunity` creation; schema description now warns planner at dispatch time (Q4a same-PR mitigation per Rigby AGREE).
- **`pipeline_orchestrator_tool`** — 1 action (`status`; Initiative aggregate reads); fully covered.
- **`video_history_tool`** — 7 actions: 5R covered (1 success + 4 clean `error_captured` on missing required args); 2 MUTATION (async Celery dispatch of `transcribe_video_task` + `generate_video_content_pack_task`) skipped.

**Aggregate:** 11 READ_ONLY dispatched, 8 MUTATION skipped, 2 IRREVERSIBLE skipped, 0 soft_error, 0 bridge_unreachable, 0 skipped_metadata_missing.

**Post-merge live-dispatch verified** (per PLAYBOOK-7.4.4): all 4 tools' primary READ_ONLY action returned expected envelope shapes. Real data snapshot:
- opportunity_manager.stats: 47 opportunities ($138K total potential, all `expired`, 46 freelance_services + 1 task).
- task_manager.stats: 0 tasks.
- pipeline_orchestrator.status: 62 initiatives (5 ACTIVE / 13 COMPLETED / 6 TRIAGE / 38 ARCHIVED); all 62 sitting at stage_1.
- video_history.list: 0 completed videos.

### PR #3449 — reasoning_engine drift-fix (pre-req for batch 6b)

Closes **1st confirmed instance of the schema↔handler drift class** Rigby flagged at S2911 T0 SIGN Q4 zoom-out. Direction chosen: **schema→handler** (handler had real dispatch logic; schema params were dead — never referenced anywhere in handler code, confirmed via repo-wide grep in Rigby T1 SIGN).

**Changes:**
- **Schema alignment** (`pa_tool_schemas.py:294-315`): removed dead params (`query`, `reasoning_type`); added `action` enum `[status, thoughts, trigger]` matching handler dispatch branches.
- **Latent handler bug-fix** (`td_handlers_agents.py:5388`): `AgentExecution.objects.filter(agent_name='ThinkingAgent')` → `.filter(agent__name='ThinkingAgent')` (FK traversal; `agent_name` was not a field). Also corrected `.values('success')` → `.values('status')`. Both bugs would have failed every `thoughts` dispatch with `FieldError`; only invisible pre-fix because callers passed `{query}` and fell into `action='status'` default, never hitting `thoughts` branch.
- **Metadata seed** (3 per-action records) + **NEW validation doc**.

**Post-merge live-dispatch verified:** `reasoning_engine_tool action=thoughts limit=3` returned 3 real completed ThinkingAgent executions with proper shape `{id, task, status, created_at}`. `status` still works.

---

## Rigby joint SIGN cycles (3 substantive, zero rubber-stamp)

- **Batch 6a T0 SIGN AGREE-with-edits** — 4-tool composition + scoped-to-READ_ONLY subset shape ratified; Q4 zoom-out surfaced 4 concerns (see Ledger candidates below).
- **Batch 6a T1 SIGN AGREE-with-edits** — 8+ handler/doc tool_runs cross-checks; Q3 additional catch: `opportunity_manager.delete` has same inline `{success: False}` envelope drift on unknown-id path at handler line 1366 (same class as `task_manager.delete` + S2907 `orm_inspect_tool` FT-5 candidate). Q4 same-PR mitigations: task_manager schema description warning applied (Rigby AGREE — description-only, contract-clarity edit); reasoning_engine drift deferred to separate pre-req PR before batch 6b opens (Rigby AGREE — preserve ratified batch boundary + risk-class separation).
- **Drift-fix T1 SIGN AGREE** — 4 repo tool_runs. Q1 direction ratified (`reasoning_type` has zero references outside metadata comments). Q2 formalized rule of thumb: *"latent-bug fixes can stay in-scope when required to make the newly-aligned contract actually work, and you prove it with harness output in the PR description."* Q3 Candidate Fold — Trigger #1: *"when fixing schema drift, always exercise every action branch, not just the previously-callable ones."*

---

## Sweep progress (post-S2911)

- **Slice 2** (`td_handlers_agents`): 6 batches × 4/4/3/4/4/4 tools + drift-fix reasoning_engine = **24/25 shipped**; 1 remaining (`universal_agent_tool` for batch 6b).
- **Total corpus untested:** 71 → 70 (-1 from batch 6b drift-fix reasoning_engine upgrade). Gap map: 31 full + 8 partial + 70 untested.
- **Extrapolated remaining:** ~8-11 sessions at accelerated pace with trustworthy harness.

---

## New Ledger candidates surfaced this session

### Rigby Tool Gap Ledger candidates (unchanged from S2910 close inventory unless noted)

- **S2911 Ledger #35 (NEW)** — Envelope-shape inconsistency on `opportunity_manager.delete` + `task_manager.delete` unknown-id paths: both return inline `{success: False, error}` instead of raising. Same class as S2907 FT-5 candidate (`orm_inspect_tool` residual `soft_error`). Not urgent (both IRREVERSIBLE-skipped this ship); track for future MUTATION-coverage batch.
- **S2911 Ledger #36 (NEW)** — **Candidate Fold — Trigger #1**: *"when fixing schema drift, always exercise every action branch, not just the previously-callable ones."* Evidence: reasoning_engine `thoughts` FieldError was latent for the entire S2841→S2911 arc because pre-fix schema advertised `{query, reasoning_type}` so callers never hit the `thoughts` branch. Drift-fix harness sweep surfaced it immediately. Rigby T1 SIGN Q3 verdict: forward-carry, promote on 2nd independent instance.
- **S2911 Ledger #37 (NEW)** — HIDDEN MUTATION planner-safety pattern: `task_manager.create` implicitly creates a standalone `Opportunity` row when `opportunity_id` is omitted. This ship added a schema description warning to surface the hazard at dispatch-plan time. Track for other tools that may have similar hidden implicit-parent-row creation patterns.

### Forward-carry Fold candidates (from prior sessions, unchanged)

- All prior Ledger rows (#1–#34 per S2910 handoff) unchanged. See `docs/handoffs/SESSION_2910_SLICE_2_BATCH_5_MIXED_COMPOSITION_SWEEP.md`.

---

## Rigby SIGN Q4 zoom-out concerns surfaced this session (tracked, not acted)

From batch 6a T0 SIGN Q4 zoom-out (4 concerns):
1. **Review fatigue on last 20% of tools** — highest-risk tools (agent-invocation / dispatch / budget / outbound class) tend to land late; fatigue increases miss-rate on subtle side effects. Batch 6b substrate now has reasoning_engine pre-fix; universal_agent_tool remains.
2. **Read-only-by-convention vs read-only-by-schema-contract drift** — sweep drifting into "read-only by convention" across many batches. Countered this ship by choosing scoped-schema-subset over intent-only.
3. **Schema↔handler drift accumulation** — reasoning_engine 1st confirmed instance. Now closed. Watch for 2nd instance → propose grep-verifier lint.
4. **Coupling between local ORM tools + dispatch tools** — reasoning_engine batching decision (deferred to 6b) is the batch-boundary choice that manages this. Rigby AGREE with the coupling-management shape.

---

## S2912 opens with

**Batch 6b — 1 tool remaining in Slice 2:** `universal_agent_tool`.

Batch 6b substrate is now clean:
- reasoning_engine_tool drift closed + `thoughts` bug fixed + validation doc shipped.
- universal_agent_tool remains the last Slice 2 tool.

**Recommended S2912 T0 SIGN questions to Rigby:**
- Batch 6b single-tool composition (universal_agent_tool alone, or add another as-yet-unaudited tool from another slice?)
- Shape recommendation: TOOL_DEFAULTS MUTATION conditional (actionless, LLM-cost surface) vs per-action metadata.
- Handler audit: universal_agent_tool at `td_handlers_agents.py:1771` — what side effects on the "context" param? What agents are auto-routable vs blocked?
- Q4 zoom-out ask (required per feedback_zoom_out_ask_per_rigby_sign).

**D6 MORATORIUM still in force** — no new strategic discovery arcs.

---

## Files changed this session (aggregate)

**PR #3448:**
- MODIFIED: `core/services/pa_tool_schemas.py` (+10 lines — task_manager description warning + opportunity_id param description)
- MODIFIED: `core/services/tool_action_metadata.py` (+180 lines — 20 per-action records)
- MODIFIED: 5 auto-regenerated artifacts (gap map + PA_TOOL_AUDIT + 4 harness output JSONs + summary)
- NEW: 4 validation docs at `docs/research/tools/validation/`

**PR #3449:**
- MODIFIED: `core/services/pa_tool_schemas.py` (schema alignment)
- MODIFIED: `core/services/td_handlers_agents.py` (handler bug-fix at line 5388)
- MODIFIED: `core/services/tool_action_metadata.py` (+3 per-action records)
- MODIFIED: 3 auto-regenerated artifacts (gap map + PA_TOOL_AUDIT + reasoning_engine harness JSON + summary)
- NEW: `docs/research/tools/validation/reasoning_engine_tool_validation.md`

**Close cascade PR:** this handoff + 00-START refresh + wrapper pin bump.
