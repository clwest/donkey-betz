# SESSION 2963 — Golden Evals arc close: canon_v2 ratification (5 folds + EvalRunContext)

**Date:** 2026-07-25
**Session:** S2963
**Arc:** Golden Evals (opened S2954; Tier-1 spec-authoring closed S2962; arc closed this session)
**HEAD at open:** `dc1ed658b`
**HEAD at arc-close doc merge:** `54bf92c27` (PR #3567)
**HEAD at close cascade:** filled at close cascade merge
**PRs shipped:**
- [#3567](https://github.com/clwest/donkey-betz-platform/pull/3567) — arc-close doc (+190 lines, spec-only)
- [#TBD](https://github.com/clwest/donkey-betz-platform) — close cascade (handoff + 00-START refresh + wrapper pin bump)

---

## What shipped

`docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md` — 190-line ratification doc closing the Golden Evals arc opened at S2954. Codifies 6 canon_v2 items binding the S2964 validator harness shape before harness code lands. All 6 doc-only this session; Item 1 opens as ~30-line code change (allowlist extension) at S2964 harness first commit.

**Companion doc:** `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md` (unchanged this session).

## Canon_v2 ratified items

| # | Source fold | Ratified form | Ship shape |
|---|-------------|---------------|------------|
| 1 | Fold P2 | Add `ChatConversation` + `ToolCallRecord` to `orm_inspect_tool._MODEL_POLICIES` (14→16; `LLMCallLog` already at lines 749-752). | Code at S2964 harness first commit |
| 2 | Fold S1 | Codify source-stratification as canon dimension for multi-source substrates (same `user_id` ≠ same eval class). | Doc-only |
| 3 | Fold U1 | Opt-in `latency_ms` evidence class (not universal `response_time_ms` promotion). | Doc-only; no retroactive slice updates |
| 4 | Fold P1 | Receipt-contamination filter canon-wide predicate: `NOT (parent_object_type='deliverable_factory' AND input_data.source='deliverable_factory.synthesized_pa_receipt')`. | Doc-only; harness utility at S2964 |
| 5 | Fold V1 | Fault-injection selector convention: `module.Class.method` (services) + `module.function` (module-level); handler-registry keys FORBIDDEN without adapter layer. Precedent: `evals/tier1/system_intelligence_agent.yaml:211`. | Doc-only; harness parser at S2964 |
| 6 | Rigby zoom-out | `EvalRunContext { substrate_type, primary_row_id, evidence_ledger_refs[], finalized_at, latency_ms? }` as canonical evidence abstraction before S2964 harness. | Doc-only shape ratification; concrete API at S2964 |

## Rigby SIGN cycle

**T1 (per-candidate SIGN, tool-grounded):** Rigby returned 10 `tool_runs` (read every referenced YAML + handoff + `td_handlers_agents.py` allowlist block). Verdicts:
- Candidate 1 → **REVISE** (LLMCallLog already present; delta is 14→16 not 14→17). Claude independently verified via block-parse.
- Candidate 2 → **AGREE**.
- Candidate 3 → **REVISE** (opt-in `latency_ms` class, not universal `response_time_ms` promotion).
- Candidate 4 → **AGREE**.
- Candidate 5 → **REVISE** (formal convention: `module.Class.method` + `module.function`; forbid handler-registry keys without adapter).

**T1 zoom-out fold (per S2771 rule):** Rigby surfaced 4 accreting risks beyond the 5 candidates — evidence-pointer join fragility, two-phase persistence lifecycle coupling, line-number anchor brittleness, canon-drift toward operational heuristics. Recommended `EvalRunContext` guardrail as one-shape mitigation. Became ratified Item 6.

**T2 (post-authoring verification):** 5 PASS + 1 FAIL on Item 4 predicate. Rigby flagged the OR-form predicate as "wrong boolean" and proposed `NOT (A AND B)` as the fix.

**T2b (reconciliation):** Claude verified via De Morgan proof + 3-row truth table that the OR form was logically identical to `NOT (A AND B)`. No correctness bug. However, the misread itself was a signal that OR form is easy to misparse. Doc rewritten to lead with `NOT (A AND B)` as the canonical intent statement; OR form + Django `.exclude(**kwargs)` listed as logically identical alternatives. Rigby T2b **PASS** on the rewrite.

**Zoom-out learning (T2 substrate signal):** Rigby's T2 FAIL was well-intentioned and tool-grounded but she made a De Morgan slip — noticed `A != … AND B != …` would be a different (wrong) predicate but didn't complete the transform to see `A != … OR B != …` is exactly `NOT (A AND B)`. Recorded as one trigger; not codifying separately yet. Watch for a second occurrence to see if "canon docs should always lead with intent form for complex booleans" is a real pattern or a one-off.

**Chris D-verdict:** `yes` via terminal 2026-07-25 (bundle: all 6 items). **7th consecutive terminal ratification S2957→S2963.**

## Twin mirrors shipped

- Content mirror: `e333f8f8-26fc-4d46-a6f0-4aa8c1516fb5` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`, `deliverable_type='initiative_phase_doc'`, `category='governance'`). **Ledger #16 RE-HIT — 16th cumulative** — fired `missing_initiative_id` on create; Rigby cleared via `deliverable_tool.clear_diagnostic` in same tool cycle (proactive-clear pattern held).
- Ratification envelope: `fc46527e-7ea3-4069-afea-33f273694cc6` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`, `deliverable_type='ratification_record'`, `category='governance'`, diagnostic-clean on create).

## Rigby Tool Gap Ledger updates

- **Ledger #19** (proposed candidate at S2962 arc-close, ratified as Item 1 this session) — status flip **CANDIDATE → RATIFIED**. Code fix opens with S2964 harness first commit (~30 lines: 2 model entries added to `_MODEL_POLICIES`).
- **Ledger #16 — 16th cumulative** — content mirror still fired `missing_initiative_id` on create (governance-scoped, no initiative_id by design). Rigby cleared proactively via `deliverable_tool.clear_diagnostic` in the same tool cycle. Ratification envelope diagnostic-clean on create. Proactive-clear pattern held for second consecutive session (S2962 was first). Underlying substrate bug not fixed yet, but Rigby's auto-clear compensates.
- **Ledger #17** — no change (Chris used terminal ratification path directly; 7th consecutive terminal ratification S2957→S2963).
- **Rigby T1/T2 discipline HELD** — 10 T1 tool_runs + 5 T2 tool_runs + 1 T2b tool_run, zero rubber-stamp verdicts. T2 FAIL on Item 4 caught by Rigby was itself a De Morgan slip; Claude verified + rewrote for clarity; Rigby T2b PASS.

## Files shipped this session (S2963)

- **NEW** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md` (190 lines, canon_v2 ratification doc, merged in PR #3567).
- **UPDATE** `00-START-NEXT-SESSION.md` (close cascade: S2964 first-action + canon_v2 items in force).
- **UPDATE** `tools/pa_local.sh` (wrapper pin bump: S2963 pin retired, S2964 pin minted).
- **NEW** `docs/handoffs/SESSION_2963_GOLDEN_EVALS_ARC_CLOSE_CANON_V2.md` (this file).

**Post-merge:** PR #3567 was doc-only (no code, no worker impact) → no `make celery-recycle` required per PLAYBOOK-7.4.4.

## Governance

Session held to the Claude-directs / Rigby-executes / Claude-verifies loop with the joint-agreement-before-Chris rule. Rigby SIGN discipline was substantive at both T1 and T2 (10 + 5 + 1 tool_runs). T2 FAIL on Item 4 forced a doc-clarity rewrite that Chris never saw — resolved between Claude+Rigby before terminal ratification per `feedback_claude_rigby_agree_first_chris_yes_no`. This is the intended shape.

## Arc-close status

**Golden Evals arc: CLOSED.**

- Tier-1 spec-authoring: 8/8 slices shipped (S2955–S2962).
- canon_v1 informative extensions: 15 items accumulated across slices (all preserved).
- canon_v2 ratified: 6 items (this session).
- Next: S2964 validator harness core (`run_golden_evals` mgmt cmd + `GoldenEvalRun` table + per-substrate adapter + JSON Schema executors + Pydantic acceptance-criteria runners). Dogfood against slice 8 (Rigby, ChatConversation) FIRST to force Item 1 allowlist fix + validate two-substrate adapter cleanly.

## Deferred queue

**Immediate (S2964 scope):**
- Item 1 allowlist code (~30 lines).
- Item 5 selector parser (harness component).
- Item 6 `EvalRunContext` concrete Python dataclass + per-substrate adapters.
- Dogfood against slice 8 first.

**Follow-up (S2964+ or later):**
- WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR (F1 from S2958) — unblocker for `workflow_orchestration_agent.yaml` v1.1 tightening.
- Nightly beat task + pass-rate drift dashboard (S2965+).
- Rigby-as-Claude-Code eval slice (post-S2964, per Item 2 canon).
- PA-turn AgentExecution eval slice (requires `PA_AGENT_EXECUTION_WRITE_ENABLED` flip + 2-4 weeks traffic).
- A1 Reliability Audit Phase 1 first-slice (Chris's 4 gating questions from scoping deliverable `7870eca9` still block Phase 1 code).

**Substrate signal to watch:**
- Complex-boolean-in-canon-doc misread pattern (Rigby T2 slip). One trigger; watch for second at S2964+ before codifying as canon guidance.

**Long-standing (unchanged from S2962):**
- Docs restructuring arc (Chris-ratified S2800, still queued).
- Slice 5-hardening executable invariants deferred at S2928.
- Tier 2 lint promotion.
- Content-append-vs-final content discrepancy investigation (Ledger candidate from S2962 T2).

## Limitations

- Nothing shipped this session is executable code. Verification that the S2964 harness actually consumes canon_v2 correctly happens at S2964 dogfood run. Local pass = shipped applies here (`feedback_local_truth_no_production`); doc renders correctly on GitHub is the local check.
- `EvalRunContext` (Item 6) is a shape ratification, not an interface contract. Concrete Python API lands at S2964 with implementation.
- 30d/all-time counts in the arc-close doc Section 2 table are snapshot values from prior sessions' handoffs; they drift. Authoritative counts live in individual slice YAMLs.
- The 6-item bundle was ratified in one D-verdict. If any individual item turns out to be harmful during S2964 harness implementation, expect an amendment PR to canon rather than a per-item rollback.
