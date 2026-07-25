# SESSION 2952 — Pre-A1 Capability Triage (Brainstorm Honesty + MarketIntel Routing + agent_job_status UX)

**Date:** 2026-07-25
**Status:** CLOSED — PR #3545 merged, workers recycled, three fixes live-verified post-merge.
**HEAD at close:** `9a0aceba6`
**Merge commit:** squash `9a0aceba6` (PR #3545)
**Twin mirrors:**
- Content mirror: `24b5e6c1-f6d6-4b11-b470-117f3a14182a` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`, `initiative_phase_doc`, `category='engineering'`, diagnostic cleared via ORM — S2909 Ledger #16 re-hit 4th time)
- Ratification envelope: `e625e0f5-a3a8-4f7d-9cdf-1484b802f679` (Architecture & Research workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`, `ratification_record`, `category='governance'`, diagnostic already null)

---

## What shipped

**S2952** — Chris opened with the correct instinct: *"the last session we had some Agents not returning data we thought they should of been and I think that the brainstorm or something didn't work properly. I think we need to address those before we dive into this."* Session pivoted from A1 Phase 1 implementation start to capability-first triage; Rigby SIGN + Chris ratification produced a joint triage plan that expanded scope once the MarketIntel investigation surfaced a real silent-no-op bug.

### Session shape

1. **Session opened targeting A1 Phase 1 implementation start** per S2951 close-out — Chris intervened before Phase 1 code opened, redirecting to fix S2951 capability holes first.
2. **Claude proposed three-item triage** (brainstorm rename + MarketIntel investigation + CompetitorAgent defer) grounded in S2951 handoff evidence + code inspection.
3. **Rigby SIGN with zoom-out ask** returned AGREE/AGREE/AGREE plus a Q4 zoom-out surfacing two items I underweighted:
   - **Schema/handler drift is the real wedge-killer**, not just brainstorm — every A1-facing tool needs schema↔handler invariants.
   - **`agent_job_status` legacy_error UX is a customer-facing trust papercut** — polling before AgentExecution row materialization returned `unknown/legacy_error`, which reads as flakiness.
4. **Chris ratified S2952 scope:** brainstorm honest + MarketIntel investigate + Competitor defer + agent_job_status UX. Drift scanner (Rigby elevate #1) deferred to S2953.
5. **Task 2 investigation surfaced a real bug** — `market_intelligence_agent` silent no-op via missing `_tool_to_agent_name` mapping + broken fallback formatter. Chris ratified scope expansion to fix (Task 5).
6. **PR #3545 shipped** three fixes + regression tests. Post-merge recycle + E2E verify confirmed all three work live; MarketIntelligenceAgent completed a real 25.5s substantive output run (`f10b35c9`), closing the loop on the S2951 finding.

## Real capability findings surfaced this session

1. **`brainstorm_tool.create` naming lie** — FIXED in PR #3545. Schema now honest about single-agent ThinkingAgent reality.
2. **`market_intelligence_agent` silent no-op** — FIXED in PR #3545. Root cause was `_tool_to_agent_name` mapping gap + fallback formatter using `.title()` (which leaves underscores between words). Cascaded into `Agent.objects.filter(name=...)` returning None so no `AgentExecution` row materialized while Celery task still returned SUCCESS in ~50ms. This is exactly the "your tool claims success while doing nothing" bug class the Reliability Audit wedge would surface for a customer.
3. **`agent_job_status` legacy_error UX** — FIXED in PR #3545. Celery `AsyncResult` fallback returns `{ok: True, status: 'pending', celery_state, message}` when the AgentExecution row hasn't materialized yet.
4. **Rigby's own tool surface false negative** — `execution_history_tool.by_agent('Market_IntelligenceAgent')` returned count=0 because the dispatch response was echoing the broken fallback-formatted name. She verified via ORM per `feedback_verify_at_raw_orm_before_trusting_tool_no_data` — MarketIntelligenceAgent (no underscore) had 15+ real historical executions all along. Ledger candidate: dispatch response should echo the CORRECT resolved agent name, not the broken fallback string.
5. **Schema/handler drift is a broader wedge-killer** (Rigby zoom-out) — 9 tools already have schema-declared actions not covered by handlers (see `test_pa_tool_schema_drift` — failure pre-exists at HEAD). Small "tool contract drift scanner" candidate for S2953.

## PRs shipped this session

- u-d-b PR **#3545** — S2952 pre-A1 capability triage: brainstorm honesty + MarketIntel routing + agent_job_status pending UX (3 files, +129/-8, 4 new regression tests green).

## Files shipped this session

- **MODIFIED** `core/services/pa_tool_schemas.py` (+30/-7) — `brainstorm_tool` schema rescoped to reflect single-agent create reality.
- **MODIFIED** `core/services/td_handlers_agents.py` (+38/-1) — `_tool_to_agent_name` mapping added `market_intelligence_agent`; fallback rewritten to split-and-capitalize (no more underscore-leaking `.title()`); `_handle_agent_job_status` gained Celery AsyncResult pending-state fallback.
- **MODIFIED** `core/tests/test_agent_introspection_run_agent_validation_2728.py` (+61) — new `ToolToAgentNameResolutionTest` class with 4 regression cases (explicit mapping guard + fallback strips underscores + single-word fallback + invariant: no fallback ever emits underscore).

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

Recycled after PR #3545 merge (`make celery-recycle`). Verified via Rigby dispatch:

- **Fix 1 (brainstorm honesty):** tool description confirmed reading *"Search historical brainstorm/panel/discussion conversations, OR dispatch a single-agent async reasoning pass on a topic."* — panel/debate claim removed from `create`-action framing.
- **Fix 2 (MarketIntel routing):** dispatch returned `agent='MarketIntelligenceAgent'` (correct CamelCase, no underscore); `execution_history_tool.by_agent('MarketIntelligenceAgent')` returned count=2 (pre-merge E2E `f10b35c9` completed 25.5s substantive + post-merge verify `921359b3` also completed).
- **Fix 3 (agent_job_status UX):** poll immediately after dispatch returned `ok=True, execution_id, status='in_progress'` — no more `legacy_error/unknown` error envelope.

## Governance

- **Three capability fixes ratified by Chris** and shipped via PR #3545. Scope expansion (Task 5) also ratified inline when investigation surfaced the silent no-op.
- **Twin mirrors** dispatched via Rigby in close cascade (IDs filled in at close).

## Rigby Tool Gap Ledger updates (deliverable `5c84e75a`, Donkey Betz workspace)

- **RESOLVED:** `brainstorm_tool.create` naming lie (S2951 candidate) — PR #3545.
- **RESOLVED:** `MarketIntelligenceCoordinator` misrouting / `market_intelligence_agent` silent no-op (S2951 candidate, expanded during S2952 investigation) — PR #3545.
- **REMAINS OPEN:** CompetitorAnalysisAgent spider coverage gap. Phase 1 audit template will explicitly EXCLUDE competitive-intel to prevent mid-demo hard-fail; deep fix (LangSmith/Langfuse/Helicone/Arize spider sources) still on backlog.
- **NEW candidate:** `agent_job_status` design gap — PARTIAL FIX shipped (Celery pending-state surfaces cleanly), but underlying two-phase dispatch→AgentExecution gap remains. Harder fix: reserve `AgentExecution` row synchronously at dispatch time (before Celery hand-off). Candidate for A1 Phase 1 "coverage assertions" rulebook.
- **NEW candidate (Rigby zoom-out):** schema↔handler drift scanner — 9 tools currently have schema-declared actions not covered by handlers (pre-existing at HEAD `9a0aceba6`; failure list in `test_pa_tool_schema_drift`). Small contract-test suite candidate to prevent regression in A1-facing tools.

## A1 Phase 1 scope refinement (this session)

**Phase 1 Reliability Audit template MUST NOT include competitive-intel section** until CompetitorAnalysisAgent spider gap is closed. This scope decision protects customer-facing demos from mid-run hard-fail. Recorded here + surfaced in `00-START-NEXT-SESSION.md` `S2953 open` guidance so Phase 1 code opens on the refined scope.

## Next session (S2953) opens

**A1 Phase 1 first-slice implementation** with the S2952-refined scope (competitive-intel excluded). Chris's 4 open questions from scoping deliverable `7870eca9` remain outstanding — route to Rigby SIGN before opening Phase 1 code.

**Also queued for S2953+:**

- Schema/handler drift scanner (Rigby zoom-out elevate — small tool contract test suite).
- `agent_job_status` design gap harder fix (reserve AgentExecution row synchronously at dispatch time).
- Signal-dispatch A11 6th rule (from S2951 carry-forward).
- All prior S2951-carry-forward deferred items unchanged.

## For fuller context (S2846 → S2952)

See:
- **S2952 handoff (current):** `docs/handoffs/SESSION_2952_PRE_A1_CAPABILITY_FIXES.md`
- **S2952 shipped code:**
  - `core/services/pa_tool_schemas.py:53-108` — brainstorm_tool schema rescoped
  - `core/services/td_handlers_agents.py:137-138` — market_intelligence_agent explicit mapping
  - `core/services/td_handlers_agents.py:163-176` — fallback formatter rewritten (split+capitalize, no more `.title()` underscore leak)
  - `core/services/td_handlers_agents.py:6652-6681` — agent_job_status Celery AsyncResult pending-state fallback
  - `core/tests/test_agent_introspection_run_agent_validation_2728.py:301-364` — ToolToAgentNameResolutionTest (4 regression cases)
- **S2951 handoff:** `docs/handoffs/SESSION_2951_A1_INFRA_AND_WEDGE_RATIFIED.md`
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
