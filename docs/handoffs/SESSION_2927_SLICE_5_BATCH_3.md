# Session 2927 — Slice 5 batch 3 (quartet — advances Slice 5 to 12/14) + workflow_orchestration_agent mapping fix

**Session:** S2927
**Date:** 2026-07-23
**HEAD at open:** `7a9aa3133` (S2926 close cascade)
**HEAD at close:** `c06bf7e57` (+ close cascade PR to follow)
**Fresh pin at open:** `pa-e0278fe5d2dd4e98` (minted at S2926 close; wrapper freshly rewritten — zero mint work at S2927 open)
**Fresh pin at close:** _TBD_ (minted by `session_lifecycle close`)
**PRs shipped:** 3 (#3487 workflow_orchestration_agent mapping fix + #3488 Slice 5 batch 3 quartet + close cascade PR)

---

## Overview

S2927 continued Slice 5 (`tool_dispatcher.py` — 14 tools) with batch 3 authoring. Session opened cleanly — S2926 close cascade had already committed the wrapper pin bump, so no pin-management debt to unwind at open. Followed the established close-cascade → session-open discipline.

Two substantive PRs shipped:
1. **PR #3487** — `_tool_to_agent_name` mapping fix at `core/services/td_handlers_agents.py:123`. `workflow_orchestration_agent` was routing to `WorkflowAgent` (delegate coordinator) instead of `WorkflowOrchestrationAgent` (template-based orchestrator with 16+ predefined workflows). Latent since the mapping's introduction; surfaced during S2927 T0 SIGN Q2 investigation as ratified from S2926's deferred item. Sweep across `_tool_to_agent_name` produced 0 additional bugs — 3 other asymmetries (`security_agent`, `strategic_review`, `create_brand_video`/`create_project_from_research`) verified as intentional/legacy aliases.
2. **PR #3488** — Slice 5 batch 3 quartet (`workflow_orchestration_agent` + `content_strategy_agent` + `marketing_strategy_agent` + `strategic_review`).

Session outcome:
- 4 Slice 5 tools moved to `validated_full` (gap map `77/10/7/22 → 81/11/7/17`).
- 1 completion-verify representative in flight (`workflow_orchestration_agent`, `business_research` template) — background poll running through session close. Receipt-verify PASS for all 4 tools. **PR #3487 mapping fix validated end-to-end at both envelope layer and ORM parent execution layer.**
- 1 latent-bug fix (mapping) shipped as prerequisite sibling PR + 3-test regression suite.
- 0 new engineering-item deliverables filed this session.

---

## Rigby SIGN cycle arc (turn 1 → Chris D-verdict)

**Turn 1** (pin `pa-e0278fe5d2dd4e98`, task `4a02ec6f-70f6-4d32-9bf8-30a59d88fc52`):
- 10+ `repo_tool` receipts (non-empty tool_runs — real SIGN, not rubber-stamp).
- Q1 quartet proposal (`workflow_orchestration_agent` + `content_strategy_agent` + `marketing_strategy_agent` + `strategic_review`) — accepted as-authored (grounded in `_tool_to_agent_name` mapping + `tool_dispatcher.py` register lines + `agent_router.AGENT_MAP` verification).
- **Q2 verdict (c) BUG** — `workflow_orchestration_agent → WorkflowAgent` mapping is a bug, not intentional. Evidence: (1) `td_handlers_agents.py:123` mapping; (2) both `WorkflowAgent` (`agent_router.py:437`) and `WorkflowOrchestrationAgent` (`:454`) registered distinctly in `AGENT_MAP`; (3) `WorkflowAgent.docstring` = delegate coordinator ("the ONLY agent that can call other agents"); (4) `WorkflowOrchestrationAgent.docstring` = wrapper preserving 3,120-line legacy orchestrator with 16+ templates; (5) 10 files reference `WorkflowOrchestrationAgent` (real consumers, not dead code). Implication: mapping fix PR should ship BEFORE batch 3 doc authoring or batch 3's completion-verify signal is invalid.
- **Q3 preview Fold shape** — if batch 3 completion-verify yields 3rd instance of recursive fanout, draft `recursive_fanout_topology__workflowagent_family__third_instance_confirmed`. Evidence pointer sketch: instance 1 (S2925 `create_project_from_research`) + instance 2 (S2926 `create_brand_video`) + instance 3 (S2927 `workflow_orchestration_agent` completion-verify). **Post-Q2 verdict, Q3 was reclassified**: template-driven fanout via `WorkflowOrchestrationAgent` is a NEW-EVIDENCE-CLASS (distinct fanout shape) — not a 3rd instance of the existing LLM-planner Fold candidate. Fold stays at 2/3.
- **Q4 verdict: pick 0** (batch 3 only, no bundled remediations). Rationale: D6 moratorium + Q2 mapping fix already touches a high-risk surface; bundling additional remediations risks confounding the verification signal.
- **Q5 zoom-out concerns:**
  - (A) Content-shape false-PASS diagnostic helper shape sketch — `assert_tool_result_shape(tool_name, result)` at live-dispatch boundary; checks success flag + normalized deliverable pointer + required keys / per-tool schema (warn-tier initially).
  - (B) If Q2 (c) mapping fix ships: grep `_tool_to_agent_name` FIRST for other tool_name↔class_name asymmetries before shipping to avoid follow-up sweep PR. Flagged specific candidates: `strategic_review → ContentStrategyAgent`; `create_brand_video`/`create_project_from_research → WorkflowAgent`.
  - (C) Structural risk of continuing doc-only sweep with inconsistent mapping: false confidence in completion-verifies + verification debt accreting under later fixes.

**Turn 2 (verdict re-request):** Chat pipe truncated turn 1 output at the tool_runs section; requested plain-text re-summary. Rigby delivered structured verdict per question with evidence pointers (no additional tool_runs needed — verdict already grounded from turn 1).

**Joint recommendation → Chris:** two-PR plan — (PR-A) mapping fix + regression test + grep sweep for other asymmetries; (PR-B) batch 3 quartet doc authoring after PR-A merges. Chris D-verdict: **"yes, ship PR-A first then batch 3"**.

---

## PR #3487 — workflow_orchestration_agent mapping fix

**Bug:** `_tool_to_agent_name` at `core/services/td_handlers_agents.py:83` routed the `workflow_orchestration_agent` tool to `WorkflowAgent` (delegate coordinator) instead of `WorkflowOrchestrationAgent` (template-based orchestrator with 16+ predefined workflows). Latent since introduction. Task receipts pass either way; completion outputs came from the wrong class.

**Fix:** one-line mapping change at `:123`:
```python
# BEFORE
'workflow_orchestration_agent': 'WorkflowAgent',

# AFTER
# WorkflowOrchestrationAgent (template-based, 16+ workflows) is
# distinct from WorkflowAgent (delegate coordinator); both are
# registered separately in AGENT_MAP.
'workflow_orchestration_agent': 'WorkflowOrchestrationAgent',
```

**Regression suite:** new file `core/tests/test_tool_to_agent_name_mapping.py` — 3 tests:
1. `test_workflow_orchestration_agent_routes_to_orchestration_class` — direct fix guard.
2. `test_workflow_agent_and_orchestration_agent_are_distinct_in_AGENT_MAP` — guards the semantic distinction; if a future refactor consolidates the classes, the fix guard loses meaning silently.
3. `test_every_mapped_class_exists_in_AGENT_MAP` — introspects the mapping dict + AGENT_MAP; catches future renames/removals that would silently break dispatch.

**Sweep result (Q5(B)):** 0 additional bugs. 4 asymmetries surfaced; 3 confirmed intentional/legacy (documented in commit message):
- `create_brand_video → WorkflowAgent` — intentional; NOT in `WorkflowOrchestrationAgent.AVAILABLE_WORKFLOWS`; delegate pattern documented in S2926 batch 2 doc.
- `create_project_from_research → WorkflowAgent` — intentional; same rationale; documented in S2925 batch 1 doc.
- `security_agent → MemoryIsolationAgent` — legacy alias, comment at `:155-156`.
- `strategic_review → ContentStrategyAgent` — legacy alias, Session 1068 comment ("StrategyAgent doesn't exist"). Documented in batch 3 `strategic_review_validation.md`.

**Sweep tool used:** Python + regex diff of RHS class names against `AgentRouter.AGENT_MAP` — 0 missing references; 4 semantic asymmetries via loose-overlap check.

**PR merged:** #3487 at `389c048b0`. Post-merge `make recycle-all` — clean recycle, sha match `389c048b0a04`, zero surviving old PIDs.

---

## PR #3488 — Slice 5 batch 3 quartet

**Tools shipped (all `validated_full`):**

1. **`workflow_orchestration_agent`** — WorkflowOrchestrationAgent-family **completion-verify representative**. Validates PR #3487 mapping fix end-to-end. Documents new-evidence-class fanout shape (template-driven, bounded) — distinct from the LLM-planner-driven unbounded fanout via WorkflowAgent (S2925/S2926, 2/3 instances of the existing Fold-candidate).
2. **`content_strategy_agent`** — content-strategy tier tool #1. `BaseAgent` subclass, strategy-only recommender. Non-amplified end-to-end `external` classification.
3. **`marketing_strategy_agent`** — content-strategy tier tool #2. Inherits `BaseBusinessResearchAgent` — SAME base class as CompetitorAnalysisAgent (the S2926 content-shape FAIL surface, deliverable `5703a6c8-...`). Doc flags high content-shape FAIL 2nd-instance candidacy for future completion-verify follow-up. Auto-Deliverable INSERT via `create_deliverable_on_schedule = True` (Session 1077 fix).
4. **`strategic_review`** — content-strategy tier tool #3. Legacy alias routing to ContentStrategyAgent (Session 1068). 2nd documented instance of multi-tool-single-class pattern (1st = `content_strategy_agent` doc §Related). Alias semantic-mismatch risk documented as intentional, not a bug.

**All 4 dispatch through shared handler `_handle_agent_tool` at `tool_dispatcher.py:1196`** (same as batches 1+2). Async receipt shape: `{task_id, mode: 'async', agent, auto_followup, follow_up_will_fire, message}`. Queue: `long_running`.

**PR merged:** #3488 at `c06bf7e57`. Post-merge `make recycle-all` — clean recycle, sha match `c06bf7e57f76`, zero surviving old PIDs.

---

## Post-merge live-dispatch verify (per PLAYBOOK-7.4.4)

**Rigby dispatch (task `622440db-...`) — 4/4 receipt PASS:**

| Tool | task_id | envelope.agent | Status |
|---|---|---|---|
| `workflow_orchestration_agent` | `58d165dd-46b2-4f52-b647-0439b3b6ecdc` | `WorkflowOrchestrationAgent` | **PASS — critical PR #3487 fix validation** |
| `content_strategy_agent` | `b2af49ff-bb1a-4838-82d6-b125ceba4416` | `ContentStrategyAgent` | PASS |
| `marketing_strategy_agent` | `d70e38de-6d42-4ef4-aacf-468cdf7a3e83` | `MarketingStrategyAgent` | PASS |
| `strategic_review` | `dcb12206-4230-4532-8324-2ec7ffd3edaa` | `ContentStrategyAgent` | **PASS — critical alias validation** |

**Completion-verify (workflow_orchestration_agent):**
- Parent AgentExecution `20ad3024-e9b8-4905-be0c-99e7e72f3819` observed via `ops_tool.execution_detail`. `agent_name = 'WorkflowOrchestrationAgent'` — **matches envelope + validates PR #3487 mapping fix at ORM parent-execution layer**. Pre-PR-A this would have been `'WorkflowAgent'`.
- Status: `in_progress` at close (16-20s heartbeat cadence — healthy). `output_data = {}` (not yet populated).
- Sub-agent enumeration deferred (parent still in-flight at close). Background poll running through session close — same pattern as S2926's `create_brand_video` completion-verify.

**PR #3487 end-to-end validation: COMPLETE at envelope + parent-execution layer.** Template-driven fanout shape enumeration (Q3 new-evidence-class datapoint) deferred to follow-up ORM check.

---

## Q1–Q5 disposition summary

| Q | Question | Disposition |
|---|---|---|
| Q1 | Batch 3 quartet composition | ✅ `workflow_orchestration_agent` + `content_strategy_agent` + `marketing_strategy_agent` + `strategic_review` |
| Q2 | workflow_orchestration_agent asymmetry | ✅ Verdict (c) BUG → PR #3487 shipped as prerequisite |
| Q3 | Recursive fanout 3rd-instance trigger | ⏸️ Reclassified post-Q2: template fanout = new-evidence-class, not 3rd instance. Fold stays at 2/3. |
| Q4 | Deferred item pickup | ✅ Pick 0 (batch 3 only, no bundled remediations) |
| Q5(A) | Content-shape FAIL 2nd-instance watch | ⏸️ Flagged in `marketing_strategy_agent` doc §5 + §6 for future completion-verify — batch 3 completion-verify representative was `workflow_orchestration_agent`, not a `BaseBusinessResearchAgent` tool |
| Q5(B) | Grep other asymmetries FIRST | ✅ Executed in PR #3487 sweep — 3 legacy aliases documented as intentional; 0 additional bugs |
| Q5(C) | Verification-debt structural risk | ✅ Eliminated by PR-A → PR-B sequencing |

---

## Sweep progress (post-S2927, gap-map regen at close)

- **Slice 1 (`td_handlers_ops`):** unchanged.
- **Slice 2 (`td_handlers_agents`):** CLOSED at S2912.
- **Slice 3 (`td_handlers_core`):** CLOSED at S2917.
- **Slice 4 (`td_handlers_gateway`):** CLOSED at S2924 (17/17).
- **Slice 5 (`tool_dispatcher`, 14 tools):** **OPEN at 12/14 post-S2927.** 2 remaining: `content_writer_agent`, `image_editing_agent`.
- Total corpus untested: **17** post-batch-3 (from 22 pre-S2927; net -5 = 4 batch-3 tools moved to full + 1 additional to partial per gap-map).
- Gap map: **81 full · 11 partial · 7 unknown · 17 untested** (verified via `python manage.py build_pa_tool_audit --gap-only`).
- Session cumulative pace: 2 substantive PRs + close cascade in 1 session — matches S2926 pace.

---

## S2927 new forbidden entries (all 1st-instance — require corroborating trigger before promotion)

- **No "template-driven bounded fanout via WorkflowOrchestrationAgent" Fold promotion without 2nd instance.** 1st (S2927 `workflow_orchestration_agent` completion-verify — new-evidence-class distinct from LLM-planner unbounded fanout via WorkflowAgent). Watch for 2nd template-driven fanout instance (e.g. via a future template-based tool or new template registration).
- **No "PR-A prerequisite → PR-B pattern-shape" Fold promotion without recurrence.** 1st (S2927 PR #3487 → PR #3488 sequencing where PR-A fixes a runtime mapping that PR-B's completion-verify signal depends on). This is a specific instance of the more general "grep-before-claim" pattern but with the additional axis of "prerequisite-fix-before-observation-signal". Watch for a 2nd instance where a sweep-batch's evidence would be invalidated without a prerequisite fix.
- **No "multi-tool-single-class asymmetry doc-authoring pattern" Fold promotion without 3rd instance.** 2nd this session (`content_strategy_agent` + `strategic_review` → same `ContentStrategyAgent`). 1st documented was implicit prior to this session; explicitly logged in `content_strategy_agent_validation.md` §Related. 3rd instance = potential `security_agent → MemoryIsolationAgent` when that tool validates in a future batch.

**S2926 forbidden entries carried forward** (see S2926 handoff §Forbidden entries — 5 new entries at S2926 close). None promoted this session. Notable: content-shape FAIL still at 1st instance (`marketing_strategy_agent` batch 3 doc flags candidacy for the natural 2nd-instance test in a future completion-verify).

**S2925 + prior forbidden entries carried forward** — full list in S2926 00-START Forbidden section. D6 STRATEGIC DISCOVERY MORATORIUM still in force. No R1a-shaped proposals; no v2 → v3 harness schema bump; no new gate/lint proposals; etc.

---

## Notable evidence markers

- **PR #3487 confirmed to have been a latent bug of unknown age.** Not introduced this session; mapping traced to `td_handlers_agents.py:123` with no session/PR history annotation. Bug went unnoticed because task receipts succeeded regardless of which registered class the tool_name resolved to.
- **PR #3487 regression suite adds 3 tests where 0 existed before.** `_tool_to_agent_name` was previously untested at the mapping-integrity level. The `test_every_mapped_class_exists_in_AGENT_MAP` test catches an entire class of future silent breakage (rename/removal of any registered agent without updating the map).
- **All 4 batch 3 docs use bare `## Covered actions` heading** (T1b lint recommended form). Gap map regen confirmed lint pass.
- **`marketing_strategy_agent` doc explicitly names itself as content-shape FAIL 2nd-instance candidate** in §5 + §6 — active hook for future targeted completion-verify. If content-shape FAIL is going to promote to Fold, this is the highest-signal next test.

---

## New Ledger candidates from S2927

_(none new this session — S2927 delivered pure sweep-batch engineering + 1 latent-bug fix. Post-PR-A sweep confirmed 3 legacy-alias asymmetries as intentional; none require Ledger promotion.)_

Ledger candidates carried forward from prior sessions — no additions.

---

## Files touched (S2927 total)

**PR #3487 (mapping fix):**
- `core/services/td_handlers_agents.py` (+5 / -1)
- `core/tests/test_tool_to_agent_name_mapping.py` (+80, new)

**PR #3488 (batch 3 quartet):**
- `docs/audits/PA_TOOLS_GAP_MAP.md` (regen)
- `docs/research/tools/validation/workflow_orchestration_agent_validation.md` (+132, new)
- `docs/research/tools/validation/content_strategy_agent_validation.md` (+118, new)
- `docs/research/tools/validation/marketing_strategy_agent_validation.md` (+122, new)
- `docs/research/tools/validation/strategic_review_validation.md` (+109, new)

**PR close cascade (TBD):**
- `docs/handoffs/SESSION_2927_SLICE_5_BATCH_3.md` (this file, new)
- `00-START-NEXT-SESSION.md` (rewrite for S2928)
- `tools/pa_local.sh` (wrapper pin bump on `session_lifecycle close`)

---

## Next session (S2928) suggested open

Slice 5 has 2 remaining tools: `content_writer_agent` + `image_editing_agent`. Batch 4 (final Slice 5 batch) composition candidate:
- Both tools → validated_full. Slice 5 CLOSE at 14/14.
- Optional: pair with a follow-up completion-verify against `marketing_strategy_agent` (Q5(A) 2nd-instance content-shape FAIL test) — bundled dispatch, not a separate doc ship.
- Optional: enumerate the sub-agent AgentExecution tree from S2927's `workflow_orchestration_agent` completion-verify to complete the new-evidence-class fanout shape datapoint.

Alternative Step 1 candidates (all deferred; do NOT open unless Chris directs):
- CompetitorAnalysisAgent content-FAIL remediation (deliverable `5703a6c8-...`) — targeted engineering slate.
- Ledger #34 broader stale-model sweep — multi-hour.
- AgentTaskExecution pre-existing pyright drift bundled slate.
- Docs restructuring arc.
- R1 fleet reject-mode flip.

See `00-START-NEXT-SESSION.md` for the full S2928 open sequence.
