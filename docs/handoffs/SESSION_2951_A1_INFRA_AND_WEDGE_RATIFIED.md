# SESSION 2951 — A1 Wedge Ratified (Reliability Audit) + Enabling Infra Shipped

**Date:** 2026-07-24
**Status:** CLOSED — PR #3543 merged, workers recycled, wedge scoping deliverable created
**HEAD at close:** `047e3b419`
**Merge commit:** squash `047e3b419` (PR #3543)
**Twin mirrors (Architecture & Research workspace):**
- Content mirror: `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6` (`initiative_phase_doc`) — A1 Wedge Scoping — Reliability Audit v0 (in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`, diagnostic cleared via ORM)
- Ratification envelope: `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b` (`ratification_record`, `category='governance'`, in Architecture & Research workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`, diagnostic already null)
- Also referenced: A1 v2 orchestration deliverable `83ee227e-451e-40af-bc71-d04faf20dcee` (in Donkey Betz workspace, diagnostic cleared via ORM)

---

## What shipped

**S2951** — Two major outcomes: (a) **infrastructure that made live capability audit possible**, (b) **A1 wedge ratified by Chris = Reliability Audit paid engagement at $500–$2,500 tiered.**

### Session shape

Opened with Chris debating: "finish A11 (6th signal-dispatch rule) before wiring A1?" Claude + Rigby both DISAGREE — A11 produces platform-side data, doesn't unblock Rigby's product-shipping surface. Chris ratified A1-before-A11.

Then: "draft 2-3 wedge candidates" → Claude drafted C1 Ask Rigby / C2 Market Pulse / C3 Deliverable-on-demand. Rigby introduced stronger **C4 Fix-It Ticket**. Chris then made the pivotal ask: **"Rigby has the tools and Agents to do a true market research for where she would best fit, why doesn't she do that and let's see if that part even works!"** — simultaneously (a) market-fit research, (b) live capability audit.

**Live orchestration v0** (deliverable `bcf8ed72-2ea7-4a6b-b9b4-c3637cfa4c26`): TrendAnalysisAgent worked (89s substantive output). MarketIntelligenceCoordinator misrouted (Rigby picked the stock coordinator). Brainstorm panel failed with `SynchronousOnlyOperation`. Deliverable diagnostic flag re-hit.

**Chris directive:** "How hard is it to fix the two that failed and run everything again?" → **the "see it work" experiment.**

Two fixes engineered:
1. **`agent_job_status` PA tool** (per Rigby's request) — sibling to `schedule_followup`, same lookup shape, returns immediate status snapshot. Verified: 14ms poll returned full structured status.
2. **ThinkingAgent async-context fix** — took 4 iterations to find the real root cause. Initial `nest_asyncio` was wrong (ORM still detects outer loop). ThreadPoolExecutor was wrong (router already wraps in thread). Env-var-inside-thread was wrong (never reached async branch). **Correct fix: `DJANGO_ALLOW_ASYNC_UNSAFE=true` scoped around `asyncio.run(self.think(...))` in `_execute_sync`.** Refactored `execute()` to extract `_execute_sync()` for clarity. Verified: brainstorm panel completes in 52s clean.

Also added `market_intelligence_agent` to the `run_agent` enum + registered handler so Rigby stops routing general market-fit queries to the stock coordinator.

**Live orchestration v2** (deliverable `83ee227e-451e-40af-bc71-d04faf20dcee`): 7 specialists + brainstorm panel dispatched via full Rigby orchestration. All 7 specialists completed successfully. Rigby used `agent_job_status` (our new tool) to poll status of each. Real market research produced.

**Wedge finding — 5+ agents independently converged on:**
- **Positioning:** production-grade agent ops + governance layer (reliability, observability, auditability)
- **Primary wedge:** Reliability Audit at $500–$2,500 (tiered, evidence-grade artifact, natural upsell)
- **Target buyer:** Platform/ML/SRE + Security/compliance leaders
- **Buying triggers:** agent incidents, tool sprawl, "shipping agents faster than controls"
- **Key quote (ResearchAgent):** "Enterprises deployed AI agents ahead of the controls needed to manage them — knowingly." (VentureBeat E4)

**Chris D-verdict:** "Ship the Reliability Audit wedge." A1 wedge is now ratified.

**Rigby wedge scoping deliverable** (`7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`) — Reliability Audit v0 scoping doc with:
- 6-step audit methodology (Scope card → Snapshot metrics → Failure signatures → Tool reliability matrix → Governance review → Scenario drills → Remediation plan)
- 3-tier concrete definition ($500 Snapshot 8-10 pages / $1,500 Standard 12-16 pages / $2,500 Deep-Dive 16-20 pages + 30-day roadmap)
- 9-gate wedge-critical vs deferrable mapping
- Smallest shippable Phase-1 slice with concierge fallback for deferrable gates
- 4 open questions for Chris
- Zoom-out concern: "audit what you can evidence"

## Real capability findings surfaced this session

1. **ThinkingAgent async-context bug** — FIXED in PR #3543. Root cause: sync ORM calls inside `think()` fail when invoked via `asyncio.run()`.
2. **`brainstorm_tool.create` naming lie** — claims "panel with participants" but actually dispatches ThinkingAgent alone. Rigby Tool Gap Ledger candidate.
3. **MarketIntelligenceCoordinator misrouting** — was stock-only despite generic name. Fix: added general `MarketIntelligenceAgent` to enum. But **Rigby still didn't dispatch it in v2** — enum add didn't take effect for her, or she deliberately skipped. Investigation deferred.
4. **CompetitorAnalysisAgent spider coverage gap** — hit "insufficient data" (2/3 minimum). Needs LangSmith/Langfuse/Helicone/Arize sources.
5. **`deliverable_tool.create` diagnostic-flag bug** — re-hit 3x this session. Rigby Tool Gap Ledger entry #31, ORM workaround still needed.

## PRs shipped this session

- u-d-b PR **#3543** — S2951 A1 infra: agent_job_status + ThinkingAgent async fix + market_intelligence_agent enum (4 files, +143/-9, drift tests pass).

## Files shipped this session

- **MODIFIED** `core/agents/thinking_agent.py` (+53/-9) — refactor `execute()` to extract `_execute_sync()`, add `DJANGO_ALLOW_ASYNC_UNSAFE` scoped around `asyncio.run(think())`.
- **MODIFIED** `core/services/pa_tool_schemas.py` (+30) — new `agent_job_status` schema + `market_intelligence_agent` enum entry.
- **MODIFIED** `core/services/td_handlers_agents.py` (+58) — new `_handle_agent_job_status` method.
- **MODIFIED** `core/services/tool_dispatcher.py` (+2) — register `agent_job_status` + `market_intelligence_agent` handlers.

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

Recycled after PR #3543 merge (`make celery-recycle`). Verified:
- `agent_job_status` still in Rigby's tool list.
- Brainstorm dispatch returns `in_progress` (no immediate async failure).
- `market_intelligence_agent` in enum.

## Governance

- **A1 wedge choice ratified by Chris** — Reliability Audit. Content mirror: `7870eca9`. Ratification envelope: dispatched in background at close.

## Rigby Tool Gap Ledger updates

- **NEW candidate:** `brainstorm_tool.create` claims multi-agent panel debate, actually dispatches single ThinkingAgent. Naming/behavior mismatch.
- **NEW candidate:** `MarketIntelligenceCoordinator` is stock-only despite generic name — should be renamed `StockMarketIntelligenceCoordinator` OR route general market queries elsewhere.
- **RE-HIT:** `deliverable_tool.create` diagnostic-flag bug (S2909 Ledger #31) — hit 3x this session (v0 deliverable, v2 deliverable, scoping deliverable). All cleared via ORM workaround.

## Next session (S2952) opens

**A1 Phase 1 first-slice implementation.** No more scoping — Rigby's scoping deliverable (`7870eca9`) has the concrete methodology, tier definitions, and gate map. Chris to answer 4 open questions from the scoping doc, then implementation begins on wedge-critical gates (Access, Isolation, Value-moment, Onboarding, Legal-Trust) with concierge fallback for deferrable gates (Rigby-tool-subset, Payment, Cost-cap, Support).
