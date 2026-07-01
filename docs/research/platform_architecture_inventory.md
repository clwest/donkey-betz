---
title: "Donkey Betz Platform Architecture Inventory — first whole-platform map"
status: draft
authority: research
session_added: 1273
last_verified: 2026-06-30
companion_anchors:
  - docs/PLATFORM_INVENTORY.md       # runtime anchor (counts source)
  - docs/PLATFORM_WHAT_IT_IS.md      # narrative anchor (glossary)
  - docs/EMPLOYEE_OS_PRIMITIVES.md   # canonical primitives + anti-duplication
  - docs/00-START-HERE/DOC_LIFECYCLE.md  # doc governance
  - docs/research/ARCHITECTURE_INDEX.md  # research library index (Employee OS slice)
  - docs/KNOWLEDGE_PIPELINE.md       # runtime flow map (partial)
  - docs/EVENT_SYSTEM_INVENTORY.md   # observability layers inventory
  - docs/AUDIT_FINDINGS.md           # canonical Celery deferred list
verifier_loop: |
  v2 (2026-06-30, S1273): Rigby SIGN-with-edits folded from fresh pin
  `pa-02cfd3206302352f` (Medium overall confidence). Substantive edits
  applied — (1) added missed Domain 32 Revenue / Outreach / Engagement
  Pipeline with dedicated §3.32 inventory (models: OutreachDraft,
  EngagementEvent, ClosePack, Meeting; services: opportunity_pipeline_
  orchestrator, ops_autopilot/revenue + outreach_generation +
  engagement; agents: OpportunityScoringAgent, OpportunityPipelineAgent,
  MeetingCoordinatorAgent); (2) added §4.9 cross-domain flow for the
  revenue pipeline (Spider → Opportunity → Outreach → Engagement →
  Meeting → ClosePack → Revenue); (3) downgraded §3.27 Auth /
  Permissions / Security maturity STABLE → PARTIAL with explicit
  trust-boundary enumeration (VIP viewer prompt-only, Fleet permissive
  fallback); (4) upgraded §3.7 LLM Provider Registry maturity WORKING
  → STABLE with explicit "core registry stable, failover/circuit-
  breaker + USD cost materialization missing" scope note; (5) tightened
  §1 Executive Summary count phrasing to autoblock-consistent language
  with as-of footnote; (6) added §3.31 separation-of-concerns paragraph
  distinguishing Event Bus from Observability layer. §2 Domain Map,
  §6 Maturity Matrix, §7 Coverage Map all updated for row 32 +
  re-rated rows 7 + 27. Two clarifications folded — External
  Integrations §3.26 and Auth §3.27 flagged as "compressed relative
  to blast radius" per Rigby weakest-part note.
  v1 draft (2026-06-30, S1273): six parallel Explore sub-agents produced
  independent domain sweeps (backend / AI-agent-employee / data-ingestion /
  knowledge-memory / human-interface / ops-governance). Parent agent
  (Claude) synthesized into 31 domains. Every domain row is grounded in
  either a direct file:line cite from the sub-agent reports OR an explicit
  "UNKNOWN" flag. Cross-domain flows were derived from the union of
  substrate-audit §3 (S1268), collaboration-patterns §3 (S1268),
  governance-authority §4 (S1269), symbol-mapping §5 (S1270),
  actor-identity §3 (S1271), and the six S1273 sweeps. No sub-agent
  finding is recorded here unless at least one file path or PLATFORM_
  INVENTORY row supports it; where two sweeps conflicted (e.g., agent
  counts 83 vs 90, PA tools 104 vs 113), inventory won per DOC_LIFECYCLE
  §2c.
owner: claude (drafted S1273; parallel-sweep evidence via 6 Explore sub-agents; Rigby SIGN-with-edits folded S1273)
---

# Donkey Betz Platform Architecture Inventory

> **What this is.** The first whole-platform architectural map of
> Donkey Betz. A Staff Engineer coming from another codebase should
> read this doc **before** deciding what to build, what to touch, or
> what to research next. It tells them what domains exist, what shape
> each is in, and where the load-bearing gaps are.
>
> **What this is not.** An Employee OS audit
> (`docs/research/ARCHITECTURE_INDEX.md` §1 is where that arc lives).
> A feature roadmap. An implementation plan. A cleanup proposal. Every
> claim here is evidence-first; every unknown is called out. When the
> next research mission is named in §9, it names what to **research**,
> not what to build.

---

## 1. Executive Summary

**What is Donkey Betz architecturally?**

Donkey Betz is a **multi-tenant, agent-driven autonomous intelligence
platform** unified through a single conversational surface (Rigby, the
PA). It combines four families that historically ship as separate
products:

1. An **AI Studio** stack — the deterministic agent framework
   (`core/agent_router.py:AGENT_MAP`), a large `BaseAgent`, 30
   advisors (`docs/ADVISOR_AUDIT.md`), a 3-reviewer content
   deliberation pipeline (`core/services/content_deliberation_runner.py`),
   deliverable + initiative surfaces.
2. A **DBAO** stack — sports/betting intelligence: TheOddsSpider
   (`ai_core/spiders/specialized/theodds_spider.py`) against 40+
   bookmakers × 60+ sport keys, `GamePredictor`
   (`core/agents/markets/game_predictor.py`), MLPrediction /
   PlacedWager settlement models (`core/models_betting.py`).
3. An **Employee OS** — three frozen `AIEmployee`s (Documentation
   Manager / Rigby, Platform Auditor, Chief of Staff) orchestrated by
   `MissionRunner` (`core/employees/mission_runner.py:1-1758`) with
   idempotent daily execution + OpsRun audit rows.
4. A **Revenue / Outreach / Engagement** pipeline (folded S1273 v2
   per Rigby review) — spider-sourced opportunities scored, drafted
   into outreach, engagement tracked, meetings scheduled, close packs
   assembled, revenue attributed. Dedicated models:
   `core/models_outreach.py:OutreachDraft`,
   `core/models_engagement.py:EngagementEvent`,
   `core/models_meeting.py:Meeting`,
   `core/models_close_pack.py:ClosePack`.

Under all four sits the same substrate: Django + PostgreSQL (with
pgvector), Redis (broker + cache + Channels), Celery (multi-queue
worker topology, 11 Procfile processes), Daphne ASGI, and a
React/Vite frontend. Exact runtime counts (agents, spiders, tasks,
models, routes) come from `docs/PLATFORM_INVENTORY.md` — regenerable
via `python manage.py generate_platform_inventory`; the CLAUDE.md
autoblock is the current source of truth (per DOC_LIFECYCLE §2c) and
should be consulted before quoting any number in a decision.

**What are the major domains?**

Thirty-two domains, grouped into nine layers:

- **Cognition & agents (7):** PA / Rigby, Traditional Agents,
  AgentRouter / Execution, Employee OS + MissionRunner, Claude Code
  Tooling, Boardroom / Advisors, LLM Provider Registry.
- **Data ingestion & intelligence (4):** Spider Framework, Signal /
  Intelligence Engine, Sports / Odds / DBAO, Body Systems +
  BodyCoordinator.
- **Content & workflow (2):** Content / Deliberation Pipeline,
  Initiative / Dream Pipeline.
- **Revenue & GTM (1):** Revenue / Outreach / Engagement Pipeline
  (added S1273 v2 per Rigby review).
- **Knowledge & memory (3):** Memory / Knowledge / Embeddings, RAG /
  Document Loading, Documentation / Research Knowledge System.
- **Human interface (6):** HumanAttention, Inbox / Messaging /
  Notifications, Frontend / Workspace UI, Mobile App, Discord Bot,
  Voice / Avatar Surfaces.
- **API & platform boundary (1):** REST + WebSocket API Layer.
- **Governance & ops (4):** Governance / Authority, Automation /
  Scheduler / Celery, Observability / Telemetry / SLOs, Event Bus /
  Streams.
- **Infrastructure & platform (4):** External Integrations, Auth /
  Permissions / Security, Configuration / Environment / Deployment,
  Data Models / Persistence / Infrastructure.

**Which domains are mature?**

CANONICAL or STABLE: Automation / Scheduler / Celery, Employee OS,
Configuration / Deployment, Infrastructure / Runtime, Auth /
Permissions, External Integrations (LLM providers), Documentation /
Research Knowledge System (research library specifically), Frontend
(Workspace 5-tab layout), Traditional Agent Framework, Spider
Framework.

**Which domains are under-researched?**

NONE / LIGHT coverage: Claude Code Tooling (design-doc gap despite
production use), Voice / Avatar Surfaces (HeyGen F2F is a stub), Mobile
App (models exist, wiring unknown), Event Bus / Streams (no producer /
consumer map documented), Sports / DBAO (integration bridge to Signal
/ Content pipeline missing), Boardroom / Advisors (in-memory state
only, no persistence contract).

**Which domains are risky?**

- **Governance / Authority** (PARTIAL maturity, HIGH drift risk):
  four planes exist and don't compose; KillSwitch has full write
  path and **zero enforcement readers**; symbol mapping is the
  unbuilt prerequisite for authority enforcement. Rigby's S1273
  review verdict: "the biggest architectural risk — multiple
  control planes that *appear* to provide safety, several are
  write-only or observation-only. Creates a dangerous false-sense-
  of-control failure mode during incidents or autonomy
  escalation."
- **Auth / Permissions / Security** (PARTIAL after S1273 v2 review,
  MEDIUM-HIGH drift risk): VIP demo enforcement is prompt-only (PA
  can ignore the "read-only" injection); Fleet signature has a
  permissive fallback (does NOT raise on missing/invalid).
  Downgraded from STABLE per Rigby S1273 review.
- **Observability / Telemetry** (WORKING, HIGH debt risk): 4–5
  parallel execution telemetry layers (`CeleryTaskEvent`,
  `LLMCallEvent`, `AgentExecution`, `ToolCallRecord`,
  `OpsRunEvent`) with no deduplication audit; the event system has
  14+ models and no central Rigby v0 intake surface
  (`RIGBY_EVENT_INTAKE_ENABLED=False`).
- **Sports / DBAO** (WORKING, MEDIUM debt risk): agents + models
  operational but pipeline into signal clustering / initiatives /
  deliverables is **not wired**; `sports_odds` is not a valid
  `SignalCluster` data_type track.
- **Beat schedule concentration** (STABLE domain, HIGH operational
  risk): 55 of 77 beat entries route to `default` queue; loss of
  `celery-worker` = half the platform stops ticking.

**Which domains should be researched next?**

Ranked recommendations in §9. Top three:

1. **Authority Enforcement Design Space** (already the recommended
   next research mission per `ARCHITECTURE_INDEX.md` §9 STAGE 2 —
   composes S1270 Symbol Mapping + S1271 Actor Identity).
2. **Observability Deduplication Audit** (5-layer trace of a single
   agent-tool-LLM execution; recommend rationalization).
3. **Sports / DBAO ↔ AI Studio Integration Sketch** (whether and how
   sports predictions should feed Signal / Initiative / Deliverable
   surfaces, or remain an intentional island).

---

## 2. Domain Map

Thirty-two domains (row 32 added S1273 v2 per Rigby review). Each row:
one-line purpose, maturity, research coverage, primary owner/subsystem
where known.

| # | Domain | One-line Purpose | Maturity | Coverage |
|---|--------|------------------|----------|----------|
| 1 | Personal Assistant (Rigby) | GPT-5.2 function-calling gateway; 8-service enrichment; 152 tool handlers | STABLE | MODERATE |
| 2 | Traditional Agent Framework | 83 agents in `AGENT_MAP`, `BaseAgent` (5,575 lines), 12-layer context injection | STABLE | DEEP |
| 3 | AgentRouter / Execution Surfaces | Deterministic + semantic routing; sync/async dispatch; follow-up subscriptions | WORKING | MODERATE |
| 4 | Employee OS + MissionRunner | 3 frozen employees; idempotent daily orchestration; OpsRun audit; anti-duplication matrix | STABLE | CANONICAL |
| 5 | Claude Code Tooling | Autonomous responder in PA convos; @claude-code pattern gating | WORKING | LIGHT |
| 6 | Boardroom / Advisors | 30 domain specialists; in-memory state; PA enrichment injection | EXPERIMENTAL | LIGHT |
| 7 | LLM Provider Registry | 6 providers (OpenAI/Anthropic/DeepSeek/Gemini/Together/Ollama); standard envelope + factories + guards | STABLE (core; failover missing) | LIGHT |
| 8 | Spider Framework | 80 spiders × 41 categories; registry + real-time collector; dedup + embed | STABLE | DEEP |
| 9 | Signal / Intelligence Engine | 10 pattern types; entity-token v1 clustering (S1139); 4-track scoring | WORKING | MODERATE |
| 10 | Sports / Odds / DBAO | TheOddsSpider + GamePredictor + BettingOutcomeVerifier; League/Team/Game/MLPrediction/PlacedWager | WORKING | LIGHT |
| 11 | Content / Deliberation Pipeline | ClaimsPack → ContentWriter → 3-reviewer → DecisionEnforcer → PublishGate → SelfBlog | WORKING | MODERATE |
| 12 | Initiative / Dream Pipeline | 5-stage lifecycle (discovery→validation→analysis→decision→execution); auto-progression with 24h age gate | WORKING | MODERATE |
| 13 | Memory / Knowledge / Embeddings | `AgentKnowledgeSource` + `AgentMemory` + `UserAgentLearning`; 14-day freshness; Redis + pgvector | STABLE | DEEP |
| 14 | RAG / Document Loading | Two lanes: `core/rag_integration.py` (pgvector, prod) vs `core/rag.py` (keyword, local Ollama) | WORKING | DEEP |
| 15 | Documentation / Research Knowledge System | `docs/` corpus + `verify_doc_claims` registry + `_index.json` + research library | STABLE | CANONICAL |
| 16 | Human Interface / HumanAttention | `HumanAttentionItem` decision surface; 8-state lifecycle; verification loop (S746) | WORKING | MODERATE |
| 17 | Inbox / Messaging / Notifications | `MessageThread` + `DirectMessage`; 3 notification systems (Web Push, Expo, Discord) | WORKING | MODERATE |
| 18 | Frontend / Workspace UI | React + Vite; 61 routes; 5-tab workspace (S1100); Command Center "Now" Hub (S931) | STABLE | DEEP |
| 19 | Mobile App | Expo scaffolding; `MobilePushToken` + `expo_push.py`; UI unknown | PARTIAL | LIGHT |
| 20 | Discord Bot | 96 commands / 48 slash + 48 prefix / 25 Cog classes in single 11,676-line file | WORKING | MODERATE |
| 21 | Voice / Avatar Surfaces | ElevenLabs TTS (prod), Runway (prod for image→video), HeyGen F2F (stub) | PARTIAL | LIGHT |
| 22 | API Layer (REST + WebSocket) | 1,857 URL patterns; 208 view files; ~51 WebSocket consumers; Fleet signature auth | STABLE | MODERATE |
| 23 | Governance / Authority | 4 planes (autonomy / authority / budget / human); 35 gates; symbol mapping unbuilt | PARTIAL | CANONICAL |
| 24 | Automation / Scheduler / Celery | 414 tasks / 91 enabled beat / 8 queues / 11 Procfile workers | STABLE | CANONICAL |
| 25 | Observability / Telemetry / SLOs | 14+ event models; 5-layer execution telemetry; SLO check ad-hoc | WORKING | DEEP |
| 26 | External Integrations | Stripe / GitHub / LLM providers / sports & financial APIs (SEC/Polygon/Kalshi/etc.) | STABLE | LIGHT |
| 27 | Auth / Permissions / Security | Token auth + staff/reviewer gates + Fleet HMAC (permissive fallback) + VIP demo (prompt-only) | PARTIAL | LIGHT |
| 28 | Configuration / Environment / Deployment | Railway 11 processes + Makefile + docker-compose; PG_APPLICATION_NAME tagging (S1166) | STABLE | MODERATE |
| 29 | Data Models / Persistence / Infrastructure | 585 concrete models / 23 apps / PostgreSQL 15 + pgvector / Redis 3 DBs / retention scattered | STABLE | LIGHT |
| 30 | Body Systems + BodyCoordinator | 9 systems (HEART/LUNGS/CIRCULATORY/SPINE/IMMUNE/DIGESTIVE/MUSCULAR/BRAIN/SKIN) via `run_all_systems_scan` every 10m | WORKING | MODERATE |
| 31 | Event Bus / Streams | 8 Redis Streams + DLQ (`core/services/event_bus.py`); consumer groups defined, producer/consumer map absent | EXPERIMENTAL | LIGHT |
| 32 | Revenue / Outreach / Engagement Pipeline | Opportunity → OutreachDraft → EngagementEvent → Meeting → ClosePack → Revenue attribution; dedicated models + `ops_autopilot/revenue.py` + orchestrator + 3 agents | WORKING | LIGHT (added S1273 v2 per Rigby review) |

Coverage legend: NONE / LIGHT / MODERATE / DEEP / CANONICAL. Maturity
legend: EXPERIMENTAL / PARTIAL / WORKING / STABLE / CANONICAL.

---

## 3. Domain Inventories

Format per §Core Deliverable spec. File:line cites where evidence is
firm; UNKNOWN where sub-agent evidence was insufficient. Where two
sweeps converged on the same claim, both cites are folded.

### 3.1 Personal Assistant (Rigby)

**Purpose.** Single conversational gateway (`UnifiedPAEntrypoint`)
that routes user queries via GPT-5.2 function calling through 8
enrichment services and 152 tool handlers.

**Canonical entry points.**
- `core/services/unified_pa_entrypoint.py:get_unified_pa(user)` —
  singleton factory + agentic loop (max 5 iterations/turn).
- `core/services/tool_dispatcher.py:ToolDispatcher` — 1,267 lines,
  9 mixin handler sets, 152 tool handlers (PLATFORM_INVENTORY count).
- `core/services/pa_tool_schemas.py` — 113 OpenAI function-calling
  schemas (PLATFORM_INVENTORY autoblock, `CLAUDE.md`).
- HTTP: `POST /api/pa/chat/` → dispatches `process_pa_chat_task` to
  dedicated `pa` Celery queue.
- Local invocation: `tools/pa_chat.py` (defaults to prod URL; use
  `tools/pa_local.sh` for local — memory rule).

**Major models.**
- `ChatConversation` (`core/models/conversations/models.py:59+`).
- `ConversationMemory` (`core/models/conversations/models.py:19`).
- `ExtendedUserProfile` (`core/models_assistant_profile.py`, per
  `CLAUDE.md`).

**Major services.**
- `PAIntelligenceEnricher` — work/governance/ops context.
- `BlogPerformanceContextBuilder`, `DomainContentContextBuilder`,
  `SpiderContextBuilder`, `AdvisorContextBuilder`,
  `StrategicMemoryService`, `ProactiveIntelligenceService`,
  `PlatformIntelligenceBriefingService` — 8-service enrichment
  pipeline per Agent 2 sweep.

**Major APIs.**
- 6 gateway tools (S1079): `governance_tool`, `work_tool`,
  `content_tool`, `intelligence_tool`, `ops_tool`, `studio_tool`.
- `run_agent` meta-tool with enum routing across 77 agents / 12
  domains.
- Async execution: `process_pa_chat_task` (Celery time_limit=300s,
  soft=280s).

**Major runtime flows.**
- **Sync (dev):** message → `_build_context` (profile/stats/docs w/ 5s
  timeouts) → `_build_messages_array` → GPT-5.2 loop → enrichment →
  `PAResponse`.
- **Async (Railway):** `POST /api/pa/chat/` → task dispatch → poll
  `GET /api/pa/chat/status/<task_id>/` every 2s (frontend) → Celery
  completion → result.
- **Silent-fallback detector (S1199):** flags LLM emitting tool-call
  JSON in text channel instead of function-call channel. S1220
  false-positive fix: only alarm if no tools actually ran (per Agent 2
  cite of `unified_pa_entrypoint.py:100-148`).

**Existing documentation.**
- `docs/topics/personal-assistant.md` (canonical topic).
- `docs/research/employee_os_communication_substrate_audit.md`
  (S1268 — comms primitives).
- Sessions 1199, 1220 handoffs (silent-fallback fix).

**Research coverage.** MODERATE. Routing, context building, enrichment
pipeline documented in topic file. Silent-fallback detection is
documented only in source comments + Session 1199 deliverable
(`c2bac9c0`). No research doc on enrichment gating logic (15% keyword
overlap rule per Agent 2).

**Architecture maturity.** STABLE. Function calling in prod; enrichment
services graceful-degradation via 5s timeouts; async processing has
dedicated queue + task time limits. Known constraint: Railway ~30s
proxy timeout forces explicit Celery dispatch.

**Known drift.**
- PLATFORM_INVENTORY count for tool schemas: 113 (auto-block, current)
  vs 104 (earlier snapshot in topic doc). Inventory wins.
- Silent-fallback detector not surfaced in public docs.

**Known technical debt.**
- Legacy keyword intent router (`_detect_intent_and_route`, 506 lines
  of if/elif) is fallback-only when function calling disabled;
  unmaintained.
- Enrichment cap changes (300–600 → 1500–2000 chars per section,
  S1006) not documented with rationale.
- No rate-limiting on PA tool calls; Redis metrics fire-and-forget
  with 60s log throttle.

### 3.2 Traditional Agent Framework

**Purpose.** Deterministic dictionary routing of 83 agents in
`AGENT_MAP` (74 enabled, 8 rerouted, 1 blocked; PLATFORM_INVENTORY §
Agents) with 12-layer context injection and automatic tool-call
recording.

**Canonical entry points.**
- `core/agent_router.py:AgentRouter.route(agent_name, task, context)` —
  main entry.
- `AGENT_MAP` dictionary — 83 mappings string → class.
- `core/agents/base_agent.py:BaseAgent` — 5,575 lines (Agent 2 sweep;
  PLATFORM_INVENTORY says 5,962; **UNKNOWN which is current** — resolve
  by fresh `wc -l`).
- HTTP: `POST /api/agents/execute/` → `agent_router.route()`.

**Major models.**
- `BaseAgent` (abstract; owns context, tool execution, LLM synthesis,
  shared tools: `web_search`, `spider_query`,
  `delegate_to_specialist`).
- 83 concrete agents in `core/agents/*.py`.
- `AgentResult` — structured envelope (success, output, trace_id,
  tool_runs).

**Major services.**
- `AgentLearningService` (`core/services/agent_learning_service.py`) —
  per-user + per-agent Redis preference models; injects
  `agent_learned_preferences` into user_context.
- `SpiderIntelligenceService` — query spider data + real-time trends.
- `PlatformIntegrationService` — `platform_tools_directive` injection
  (S992).
- Session 1029 agent health audit: 35 thriving, 6 bounded, 3 waste
  paths closed.

**Major APIs.**
- 12-layer context injection: `scifi_context`, `spider_context`,
  `learning_context`, `advisor_context`, `feedback_context`,
  `knowledge_context`, `workspace_context`, `docs_context`,
  `user_context`, `risk_context`, `platform_tools_directive`,
  `user_docs_context`.
- Shared tools: `web_search` (Tavily), `spider_query`,
  `delegate_to_specialist`.
- User document RAG (S1034): pgvector cosine, threshold 0.45, top 5
  chunks injected.
- Semantic routing (optional, S488): threshold 0.35, fallback keyword.

**Major runtime flows.**
- **Deterministic:** user → agent_name string → `AGENT_MAP` class →
  fresh instantiation → context injection → LLM execution → tool
  recording → `AgentResult`.
- **Learning loop:** every `route()` → `record_interaction()` → Redis
  preference model → next call injects learned prefs.

**Existing documentation.**
- `docs/topics/agent-system.md` (canonical).
- `docs/agents/AGENT_ECOSYSTEM_COMPLETE_GUIDE.md`.
- Session 1000 (Intelligence Desks), Session 1115 audit (on-demand
  only, no scheduled beats).

**Research coverage.** DEEP. Routing + context injection well
documented.

**Architecture maturity.** STABLE. Dictionary routing production-grade;
context injection layers proven; tool recording automatic.

**Known drift.**
- PLATFORM_INVENTORY: 83 in `AGENT_MAP` vs 90 rows in Agent table
  (autoblock). Diff explained as DynamicPersonaAgent fallback per
  `docs/topics/agent-system.md`, but the delta bounces on refresh —
  known drift item per S1223 baseline discussion.
- Intelligence Desk narrative previously claimed daily beat; S1115
  found it removed in commit `a88fb8e7`.

**Known technical debt.**
- `delegate_to_specialist` has no depth limit / cycle detection —
  theoretical infinite loop.
- Semantic routing threshold hardcoded; no observability on fallback
  rate.
- `AgentLearningService` Redis state has no expiration policy.
- User document RAG blocks agents without `self.user` set; no
  documented graceful degradation.

### 3.3 AgentRouter / Execution Surfaces

**Purpose.** Deterministic request → agent mapping with sync/async
execution, WebSocket status streaming, and follow-up subscription
tracking.

**Canonical entry points.**
- `core/agent_router.py:AgentRouter` — dispatcher.
- HTTP: `POST /api/agents/execute/`.
- WebSocket: `/ws/agent-execution/`.
- Celery tasks: `run_agent_async`, `execute_agent_task`.
- Follow-up subscriptions: `AgentFollowupSubscription`
  (`core/models_unified_system.py`).

**Major models.**
- `AgentRouter`, `ExecutionRun` (`core/models/executor/models.py`),
  `AgentFollowupSubscription`, `PredictionFollowUp`.

**Major services.**
- `ProperAgentExecutor` (sync wrapper).
- `OrchestrationStepExecutor`, `ExecutorDriver`,
  `AgentExecutionBridge` (`core/learning_bridges/`).

**Major runtime flows.**
- Sync: `POST /api/agents/execute/` → `route()` → `execute()` →
  `AgentResult`.
- Async: `?async=true` → dispatch `run_agent_async` → WebSocket status
  updates.
- Follow-up: on completion, check `AgentFollowupSubscription` →
  auto-enqueue next agent.

**Existing documentation.** `docs/topics/agent-system.md` (routing).
Follow-up model not documented in public docs.

**Research coverage.** MODERATE. Routing covered; follow-up
subscriptions exist in model layer but no doc.

**Architecture maturity.** WORKING. Router stable; `ExecutionRun`
models (S1074–S1075) still stabilizing.

**Known drift.** No count of follow-up subscriptions in
PLATFORM_INVENTORY.

**Known technical debt.**
- Follow-up subscriptions lack observability — no trigger
  success/failure metrics.
- `ExecutionRun` multi-tenant but no workspace scoping on queries;
  cross-tenant leak risk per Agent 2 sweep.
- Fresh-per-request instantiation prevents session-scoped tool caching
  (relevant for paid tools).

### 3.4 Employee OS + MissionRunner

**Purpose.** Deterministic, audit-trail-emitting AI worker lifecycle
using frozen contracts, standard mission orchestration, and reuse-only
primitives (no new models per anti-duplication matrix).

**Canonical entry points.**
- `core/employees/jobs.py:73-162` — `AIEmployee` + `JobContract`
  frozen dataclasses.
- `core/employees/mission_runner.py:1-1758` — lifecycle orchestrator.
- `core/tasks_documentation_manager.py`, `core/tasks_platform_audit.py`,
  `core/tasks_chief_of_staff.py` — 3 production task modules.
- `employee_tool` PA tool (`core/services/td_handlers_employee.py`):
  actions `describe / run_now / status / evidence_for_mission`.
- Beat schedule: `PeriodicTask` rows for daily/on-demand cadences.

**Major models.**
- `AIEmployee` (jobs.py:73-92) — handle, display_name,
  runs_as_username, primary_chat_id.
- `JobContract` (jobs.py:94+) — mission, responsibilities, authority
  dict (policy_string → `AuthorityLevel`), escalation_rules,
  evidence_contract.
- `OpsRun(domain='mission')` (`core/models_ops_runs.py`) — one row per
  employee mission execution.
- `OpsRunEvent` — one row per step boundary / verdict / escalation.
- `emit_mission_verdict()` (`core/employees/mission_verdict.py`) —
  terminal event + idempotency.
- `Deliverable(publish_intent='publish_candidate')` — escalation
  surface.
- `DirectMessage` + `MessageThread` — shift-report inbox.
- `post_shift_report()` (`core/employees/comms.py`) — canonical
  formatter.

**Major services.** `MissionRunner`, `MissionRunnerConfig` (frozen
identity + policy dataclass), `FailureContext`,
`EscalationDeliverableSpec`.

**Major APIs.** MissionRunner hook signatures: `preflight_fn`,
`postflight_fn(PostflightContext | passed, summary_dict)`,
`escalation_body_formatter(FailureContext → str)`,
`shift_report_fn(OpsRun → dict)`.

**Major runtime flows.**
- **I1 (daily idempotency):** two `.run()` calls same day, same
  `mission_run_kind` → one OpsRun row.
- **I5 (step cascade):** first failure halts; remaining emit
  `<name>_skipped`.
- **I7 (escalation dedupe):** key = `(failed_step, error_signature)`
  within `dedupe_window_hours`.
- **Shift report:** MissionRunner → `post_shift_report()` → persistent
  (employee, job) thread; idempotent.
- **I4 (verdict idempotency):** `get_or_create(run=mission,
  label=<label>)`; repeats no-op.

**Existing documentation.**
- `docs/EMPLOYEE_OS_PRIMITIVES.md` — CANONICAL primitives + 23-row
  anti-duplication matrix + lifecycle + quick-start (Rigby + Claude,
  S1253).
- `docs/topics/employee-os.md` — orientation pointer.
- `docs/handoffs/SESSION_1258_EMPLOYEE_OS_PR_3_3_MORNING_BRIEF_BEAT_MIGRATION.md`
  — latest prod state.
- `docs/research/employee_os_communication_substrate_audit.md`,
  `_communication_protocol_sketch.md`, `_collaboration_patterns.md`
  — Employee OS comms + collaboration canon.

**Research coverage.** CANONICAL. Primitives authoritative;
architecture research library (S1268–S1271) is the domain's specific
knowledge substrate.

**Architecture maturity.** STABLE. 3 production employees; MissionRunner
frozen as of S1258; lifecycle invariants I1–I9 covered by contract
tests; S1259 first-fires clean.

**Known drift.** NONE detected against inventory.

**Known technical debt.**
- Hook signatures (preflight/postflight/escalation/shift-report) mixed
  with `OpsRun` model fields; no static type guarantee.
- Postflight inspector-based signature detection (legacy
  `(passed, summary_acc)` vs new `PostflightContext`) is fragile.
- `dedupe_window_hours` global in config; no per-step override.
- `OpsRun.summary` dict is free-form; no schema; jobs must supply
  `required_summary_keys` and validate on read.

### 3.5 Claude Code Tooling

**Purpose.** Autonomous Claude Code agent that monitors PA
conversations, responds when addressed (`@claude-code`), coordinates
with Rigby in real-time collaborative sessions (3-way: Chris + Rigby +
Claude).

**Canonical entry points.**
- `core/services/claude_code_agent.py` — main autonomous responder.
- `core/services/claude_code_engineer.py` — specialized engineering
  execution.
- Message filtering: `CLAUDE_CODE_PATTERNS` regex + `SELF_SOURCES`
  dedup.
- Local: `tools/pa_chat.py` (from Claude Code sessions).

**Major services.** `ClaudeCodeAgent`, `ClaudeCodeEngineer`,
`get_conversation_history(conversation_id, limit=20)`.

**Major runtime flows.**
- Message arrives in PA conversation → Celery task checks
  `CLAUDE_CODE_PATTERNS` → match + not in `SELF_SOURCES` → load
  history → Anthropic call → format response → POST via store-only
  endpoint → WebSocket broadcast.
- No Rigby trigger from Claude Code posts (avoids loops).

**Existing documentation.**
- Source comments only.
- Session 1262 (task receipt reliability).
- Session 1263 (agent row consolidation).
- **No public design doc.**

**Research coverage.** LIGHT. Code exists + is used, but no
architectural rationale doc. S1262/S1263 handoffs are tactical.

**Architecture maturity.** WORKING. Deployed and responding.

**Known drift.** NONE (minimal public claims).

**Known technical debt.**
- System prompt hardcodes knowledge counts (83 agents, 77 spiders,
  etc.) — stale after platform changes; no auto-update.
- `CLAUDE_CODE_PATTERNS` regex maintained manually.
- History limit (20) hardcoded.
- LLM model version hardcoded in SDK init.
- **See project memory `project_employee_os_ux_gap_task_receipts.md`
  — S1257 PR #2745**: `claude_code_tool` dispatch returns "task_id"
  but Chat UI shows no receipt if dispatched task fails to post back.

### 3.6 Boardroom / Advisors / Decision Support

**Purpose.** 30 domain specialists (`docs/ADVISOR_AUDIT.md`) providing
strategic guidance, decision analysis, and enrichment-context injection.
Frontend Boardroom tab surfaces `HumanAttentionItem` decisions.

**Canonical entry points.**
- `advisors/registry.py:AdvisorRegistry` — singleton; ~920 lines;
  initialized with 25+ advisor profiles.
- `advisors/llm_advisor_system.py` — LLM-powered consultation.
- `core/services/advisor_context_builder.py` — PA enrichment injection.
- Frontend: `frontend/src/pages/workspace/tabs/BoardroomTab.tsx`,
  `frontend/src/pages/AdvisorsPage.tsx`.

**Major models.**
- `AdvisorRegistry` (in-memory singleton).
- `AdvisorProfile` — dataclass: id, name, title, domain,
  expertise_level, specializations, years_experience,
  consultation_types, decision_frameworks, performance metrics.
- `AdvisorDomain` enum — 20+ domains.
- `AdvisorExpertiseLevel` enum — specialist / expert / master / legend.
- `AdvisorConsultation` — request, recommendations, action_items,
  status.

**Major services.**
- `AdvisorContextBuilder` — PA enrichment: injects top-N advisors via
  `find_best_advisor()` scoring.
- `AdvisorNetwork` + `AdvisorNetworkService`
  (`intelligence/models/advisor_network.py`, `.../services/…`).
- `LLMAdvisorSystem`.

**Major APIs.**
- `AdvisorRegistry.list_advisors(domain, expertise_level,
  specializations)` — sorted by expertise + satisfaction.
- `find_best_advisor(topic, domain, specializations)` — scoring:
  specialization overlap × 2, domain match × 15, experience bonus,
  satisfaction × 2, success_rate × 3, response_time × 2.
- `request_consultation → get_consultation → complete_consultation` →
  metrics update.

**Existing documentation.**
- `docs/ADVISOR_AUDIT.md` (30 functional specialists inventoried).
- `advisors/registry.py` inline docstrings.
- **No architectural rationale doc.**

**Research coverage.** LIGHT. Scoring logic clear from source; no doc
on why `LEGEND` tier defined but not populated at init.

**Architecture maturity.** EXPERIMENTAL. Registry initialized fresh;
metrics (satisfaction_rating, total_consultations, success_rate)
mutable but **not persisted** in DB. `LLMAdvisorSystem` integration
with workflow unclear. No auto-scheduling — on-demand via enrichment.

**Known drift.**
- PLATFORM_INVENTORY autoblock says "30 domain specialists"; registry
  code shows 25+. Exact count requires init trace.

**Known technical debt.**
- Advisor metrics in-memory only; no DB backing.
- `find_best_advisor` deterministic heuristic; no feedback loop.
- No rate-limiting or quota per advisor.
- Consultation objects stored in-memory dict; no cross-restart
  persistence.

### 3.7 LLM Provider Registry

**Purpose.** Unified multi-provider interface abstracting 6 LLM
providers with standardized request/response envelopes and cost
tracking.

**Canonical entry points.**
- `core/services/llm_provider_registry.py:LLMProviderRegistry` —
  singleton, 2,000+ lines (Agent 2 sweep).
- `get_llm_provider_registry()` factory.
- Providers: OpenAI, Anthropic, DeepSeek, Gemini, Together, Ollama
  (PLATFORM_INVENTORY autoblock: 6).

**Major models.**
- `LLMRequest`, `LLMResponse` dataclasses (envelope contract).
- `BaseLLMProvider` abstract; concrete subclasses per provider.

**Major services.**
- Per-provider `complete()` implementations.
- Session 1084 (round 51): shared `openai_client_factory` for
  timeout/retry consistency.
- Session 1200: `BaseAgent` uses explicit GPT-5.2 via registry.

**Major APIs.**
- `LLMProviderRegistry.complete(request, provider='auto',
  model_id='auto')`.
- `health_check_all()` → per-provider availability + latency_ms +
  error.
- `LLMCallEvent` telemetry per call (per S1098 wrapper — see §3.25).

**Existing documentation.** Inline docstrings only. No architectural
doc.

**Research coverage.** LIGHT (compressed relative to blast radius per
Rigby S1273 review — deserves a dedicated provider capability +
failover architecture doc).

**Architecture maturity.** **STABLE for the core registry
abstraction** (revised S1273 v2 per Rigby review — previously listed
as WORKING). The registry has standardized `LLMRequest` / `LLMResponse`
envelopes, per-provider `BaseLLMProvider` subclasses, shared client
factories (`openai_client_factory`, `anthropic_client_factory`) with
forbidden-kwargs guards, and health-check hooks. 6 providers registered
and in prod. **What's missing is not the abstraction — it's failover
+ circuit-breaking + USD cost materialization.** Do not treat this as
EXPERIMENTAL or PARTIAL; the core is stable, the peripherals are the
gap.

**Known drift.** None detected in core abstraction.

**Known technical debt.**
- `LLMResponse.cost` populated per call but no USD aggregation, no
  billing surface, no per-provider cost ceiling.
- Provider selection strategy ('auto') undocumented — inferred
  first-available or cost-based; needs a written contract.
- Tool-calling support varies by provider; no capability matrix.
- Timeout/retry shared via `openai_client_factory` but not visible to
  DeepSeek/Gemini/etc. — provider-specific defaults could diverge.
- **No circuit-breaker or auto-failover on repeated failures.**
  Health check exists but is not wired to a routing decision.

### 3.8 Spider Framework

**Purpose.** Distributed intelligence gathering across 80 spiders / 41
categories feeding agents, signals, content, and betting intelligence.

**Canonical entry points.**
- Beat: `intelligence.tasks.scan_spider_opportunities` (every 30
  min).
- `ai_core.spiders.spider_registry.SpiderRegistry`.
- `ai_core.spiders.real_data_collector.collect_spider_data_sync()`.
- `core.tasks.execute_single_spider()`
  (`core/tasks_spiders.py:109-200`).
- Management: `python manage.py activate_spiders`.

**Major models.**
- `LegacySpiderData` (`core/models_unified_system.py`) — raw output +
  pgvector 1536D embedding; `data_type` enum; `relevance_score`
  (0-100); `is_processed`.
- `SpiderExecutionLog` — task tracking.
- `SpiderDataAnnotation` — human labels for training.

**Major services.**
- `SpiderIntelligenceService` (`core/services/spider_intelligence.py`)
  — pgvector KNN via `CosineDistance`, top 50 / min similarity 0.25
  (S1024).
- `SpiderDeduplicationService` (S616).
- `BaseIntelligenceSpider` — async base w/ rate limiting, caching,
  metrics.

**Major APIs.**
- Per-spider concrete classes: `TheOddsSpider`, `CombatSportsSpider`,
  etc.
- Real-time WebSocket publish (`ai_core/spiders/realtime_publisher.py`).
- 80 registered in `ai_core/spiders/specialized/` (PLATFORM_INVENTORY).

**Major runtime flows.**
1. Beat (30m): `scan_spider_opportunities` →
   `SpiderRegistry.get_spiders_by_category()` → spawn per-spider
   tasks.
2. Per-spider: `execute_single_spider()` → parse → deduplicate → save
   `LegacySpiderData`.
3. Signal trigger: `spider_data_router.route_data()` → check
   `data_type` → fan out to agents / deliberation / signals.
4. Embedding backfill: `backfill_spider_embeddings` (every 10 min,
   batch 500 — Agent 3 says 500, Agent 4 says batch 50; **UNKNOWN**
   which is current). OpenAI text-embedding-3-small via pgvector.

**Existing documentation.**
- `docs/topics/spider-network.md` — canonical (categories, flow,
  aggregation, embeddings).
- `docs/PLATFORM_INVENTORY.md` — 80 spiders, 0 placeholder.
- `docs/COMPREHENSIVE_DATA_SOURCES_2025.md`.
- `docs/archive/superseded-.../SPIDERS.md` — old 50-spider blueprint.

**Research coverage.** DEEP. Embedding coverage ~85%; dedup proven at
scale; semantic search proven (S1024); circuit breaker on API failures
(S1083).

**Architecture maturity.** STABLE / CANONICAL for framework itself.

**Known drift.**
- TheOddsSpider circuit breaker (S1083): once API key fails, no more
  calls that session.
- Entity-token clusterer (S1139) replaced legacy verb-keyword.
- Embedding backfill batch size discrepancy across Agent 3 vs Agent 4
  (500 vs 50) — **UNKNOWN which is current**.

**Known technical debt.**
- 41 granular categories vs 18 semantic groupings — no chosen
  taxonomy.
- Embedding backfill cadence at scale untuned.

### 3.9 Signal / Intelligence Engine

**Purpose.** Transform raw spider signals into pattern clusters, score
for reach/intent/replicability, enable auto-topic generation and
content/investment decisions.

**Canonical entry points.**
- `core/services/signal_aggregation_service.py:33-1161` —
  `SignalAggregationService.aggregate_signals()`.
- `core/services/content_scoring_service.py:63-85` —
  `ContentScoringService.score_cluster()`.
- `core/services/signal_curator_service.py`.
- `core/services/fleet_signals.py`.
- REST: `GET /api/fleet/signals/clusters?since=<seq>` — cursor
  replay via monotonic `SignalCluster.seq` (S1131, migration 0347).

**Major models.**
- `SignalCluster` (`core/models_signal_intelligence.py:29`):
  `pattern_type` enum (10 types: demand_spike, trend_emergence,
  sentiment_shift, opportunity_window, knowledge_gap,
  competitive_signal, market_movement, skill_demand, content_gap,
  user_need — PLATFORM_INVENTORY autoblock); scoring: `strength`,
  `confidence`, `novelty` (24h decay), `urgency`; S1025 scoring:
  `reach_score`, `intent_score`, `replicability_score`,
  `source_confidence`, `track` (attention|intent|unclassified);
  `spider_data_ids[]`, `keywords[]`, `sample_signals[]`;
  `cluster_method` enum (legacy vs `entity_token_v1` from S1139);
  monotonic `seq` (BigIntegerField w/ Postgres sequence).
- `AutoTopic` — generated topic from cluster with rationale +
  suggested_agents + trigger conditions.

**Major services.**
- `SignalAggregationService` — `MIN_CLUSTER_SIZE=3` (raised from 2
  in S1139); entity-token clusterer (v1): groups by shared
  Title-case nouns (≥4 chars), min 2 tokens per pair; legacy
  verb-keyword clusterer with 10 `PATTERN_TYPE_KEYWORDS`; env
  `SIGNAL_CLUSTERER_METHOD` (default `entity_token_v1`).
- `ContentScoringService` — 4-score heuristics; source-tier
  confidence (T1 = Reuters/BBC/TechCrunch/Nature → 1.0;
  T2 = HackerNews/Reddit/Medium → 0.6; T3 → 0.2); no LLM calls.
- `SignalCuratorService`, `FleetSignals`.

**Major Celery tasks.**
- `scan_spider_opportunities` (30m beat, 15m soft limit).
- `process_spider_actions`
  (`core/tasks_spiders.py:_impl_process_spider_actions`) —
  classifies: opportunity → Initiative, threat → HumanAttentionItem,
  trend → SignalCluster, content_idea → Dream.

**Existing documentation.**
- `docs/topics/spider-network.md:44-102` — signal aggregation flow,
  pattern types, clustering v1 vs legacy, entity-token logic.
- `docs/topics/content-pipeline.md` — signal → AutoTopic →
  HiveMindSession.

**Research coverage.** MODERATE (–DEEP). Pattern types defined and
documented (10 types). Clustering algorithm rewrite in progress
(S1139). Scoring contract locked (S1025).

**Architecture maturity.** WORKING → STABLE. Three-tier source
confidence working. Clustering migration in flight (entity_token_v1
opt-in, legacy decay).

**Known drift.**
- Pre-S1139 clusters (`cluster_method='legacy'`) marked as such;
  85.5% rejection rate by LLM judges (per Agent 3 sweep).
- News boilerplate token denylist added S1139.

**Known technical debt.**
- Legacy clusters persist in DB (non-blocking); no cleanup.
- Scoring service source tiers hardcoded; not DB-driven.

### 3.10 Sports / Odds / Betting Intelligence (DBAO)

**Purpose.** Odds ingestion from 40+ bookmakers × 60+ sport keys, game
outcome prediction, sharp-action detection, arbitrage, betting
recommendations, wager settlement.

**Canonical entry points.**
- `ai_core/spiders/specialized/theodds_spider.py:TheOddsSpider` —
  `fetch_data()` (line 193), `fetch_scores(sport_key, days_from=3)`
  (line 200+, S995/S998B).
- `core/agents/markets/game_predictor.py:GamePredictor.execute()`
  (line 67) — LLM-analyzed prediction from odds consensus;
  `_store_predictions()` (line 114+).
- `core/services/betting_outcome_verifier.py:BettingOutcomeVerifier.settle_wagers()`.
- `SharpActionDetector.detect_signals()` (S1012).
- REST: `GET /api/odds-sports/todays-games/` (S1012 — merges ESPN
  scoreboard into odds).
- `core/views_odds_sports.py`: `convert_odds`,
  `calculate_expected_value`, `get_todays_games`.

**Major models.**
- `sports/models.py`: `League` (line 101), `Team` (line 177),
  `Game` (200+), `MLPrediction`.
- `MLPrediction`: game FK, predicted_winner, home/away_win_prob,
  predicted_home/away_score, confidence, key_factors, agent FK.
  S1010: auto-created via `SPORT_KEY_LEAGUE` mapping (21 keys),
  fallback `SPORT_PREFIX_MAP`; filters >14 days out; S1012 dedup by
  `Max('id')` per game_id.
- `core/models_betting.py:PlacedWager` (line 13) — stake, odds
  (American), potential_payout, status (pending/won/lost/push/
  cancelled); `calculate_payout()`, `settle(won, push)`.
- `PlacedWagerLeg` (line 108) — parlay legs w/ event_id, market_type
  (h2h/spreads/totals/props/futures).
- `core/models_odds_history.py:GameLineHistory` (line 82) —
  time-series odds per bookmaker.

**Major services.** `BettingOutcomeVerifier`, `SportsContentContext`,
`SportsBettingCoordinator`.

**Major agents.** `GamePredictor`, `ArbitrageDetector`,
`SportsOddsAnalyst`.

**Major Celery tasks.** `execute_single_spider(theodds)`,
`run_game_predictor(sport_keys)`, `verify_betting_outcomes()`.

**Major REST endpoints.**
- `POST /api/odds-sports/convert-odds/`.
- `POST /api/odds-sports/expected-value/`.
- `GET /api/odds-sports/todays-games/`.
- `POST /api/odds-sports/kelly-criterion/`.
- `GET /api/odds-sports/ai-track-record/` (S1012 dedup).

**Major runtime flows.**
```
TheOddsSpider.fetch_data [40+ books, 60+ sports]
  → GamePredictor.execute() [consensus prob → score est → confidence]
  → MLPrediction row
  → TheOddsSpider.fetch_scores() [completed + live games]
  → BettingOutcomeVerifier.settle_wagers()
  → SharpActionDetector (odds divergence)
```

**Existing documentation.**
- `docs/topics/spider-network.md:91-119` — TheOddsSpider detail,
  S995/S998B/S1010/S1012.
- Scattered across agent examples + task comments.
- **No dedicated sports intelligence doc.**

**Research coverage.** LIGHT–MODERATE. Odds fetch, prediction,
settlement, sharp-action all working. Gap: no doc on how DBAO
integrates with broader platform decisions.

**Architecture maturity.** WORKING. Models defined; services
operational; **integration gap** — sports_odds is not a valid
`SignalCluster` data_type track; sports predictions do NOT auto-create
Initiatives; betting outcomes NOT fed to deliberation.

**Known drift.**
- S995 → S998B: `fetch_scores()` now returns completed AND
  in-progress games (previously filtered live out).
- S1012 dedup fix prevents duplicate pending predictions.

**Known technical debt.**
- `sports/` is a separate Django app; lacks tight integration with
  core agents/tasks.
- No sports→content pipeline (intentional isolation or oversight?).
- `PlacedWager` settlement could be async.
- `GameLineHistory` tracked but not actively queried in any service.

### 3.11 Content / Deliberation Pipeline

**Purpose.** Multi-agent deliberation: spider signals → claims
evidence → content draft → 3-reviewer panel → decision enforcement →
publish gate → blog + metadata.

**Canonical entry points.**
- `core/services/content_deliberation_runner.py:24:ContentDeliberationRunner.run_blog(topic, voice)`.
- `core/services/claims_pack_builder.py:ClaimsPackBuilder.build(topic)`.
- `core/agents/content_writer_agent.py:ContentWriterAgent`.
- 3-reviewer panel: `SkepticReviewer`, `FactCheckReviewer`,
  `DomainPersonaReviewer`.
- `DecisionEnforcer` — Prefrontal Cortex; forces PUBLISH/REVISE/KILL.
- `PublishGate` — quality/novelty/structure thresholds.

**Major models.**
- `ClaimsPack` — deterministic IDs
  `C-{sha256(normalize_url(url)+title)[:10]}`; sources: SpiderData
  (72h; description→0.7, title-only→0.3), SignalClusters
  (sample→0.4); max 20 claims, sorted by freshness.
- `Deliverable` (`core/models_content.py`) — title, content,
  deliverable_type (blog|newsletter|guide|analysis), category, tags,
  metadata, stats_snapshot; linked to Initiative + HiveMindSession;
  pgvector-embeddable.
- `ContentReview` / `ReviewDecision`.
- `SelfBlog` — published blog w/ `stats_snapshot['deliberation']`
  metadata.

**Major services.** `ContentDeliberationRunner`, `ClaimsPackBuilder`,
`ContentScoringService` (shared with §3.9), `PublishGate`.

**Major agents.**
- `ContentWriterAgent` — 3 prompt-construction methods (system,
  content, flagship injection); mandatory `[C-xxxxxxxxxx]` citations;
  evidence-first mode (S1103).
- `SkepticReviewer`, `FactCheckReviewer`, `DomainPersonaReviewer`
  (only if domain confidence ≥ 0.2).
- `DecisionEnforcer` — fallback: all PASS → PUBLISH, any FAIL →
  REVISE.

**Existing documentation.**
- `docs/topics/content-pipeline.md` — canonical (100+ lines: pipeline,
  ClaimsPack spec, ContentWriter prompts, reviewer architecture,
  PublishGate thresholds).
- `docs/PLATFORM_INVENTORY.md` — 3 reviewer classes, 9 content
  domains, `max_claims=20`.

**Research coverage.** MODERATE. Pipeline architecture well-documented;
reviewer classes defined; PublishGate thresholds specified.

**Architecture maturity.** WORKING. Claims dedup working; 3-reviewer
solid; `DecisionEnforcer` contract locked; evidence-first mode in
place.

**Known drift.**
- S1103 evidence-first suppression overwrites domain/flagship spider
  context when claims present.
- S988: reviewer LLM provider must use
  `registry.complete(provider='openai', model_id='gpt-4.1-mini')` —
  NOT `core.llm_providers` (doesn't exist).

**Known technical debt.**
- ContentWriter has 3 separate prompt-building methods — consolidate
  candidate.
- Evidence-first override logic could leak spider URLs via path 2
  (blog performance).
- Citation format `[C-xxxxxxxxxx]` magic string; no schema validation
  in review phase.
- No end-to-end test showing full flow (Spider → Signal → ClaimsPack →
  Blog published).

### 3.12 Initiative / Dream Pipeline

**Purpose.** 5-stage lifecycle (discovery → validation → analysis →
decision → execution) for autonomous work items. Dreams are unvalidated
opportunities; Initiatives are validated + prioritized.

**Canonical entry points.**
- `docs/DREAM_INITIATIVE_WORKFLOW.md` (per `CLAUDE.md`).
- `docs/topics/initiative-pipeline.md`.
- Auto-progression on stages 4/5 with 24h age gate
  (PLATFORM_INVENTORY).
- `HiveMindSession` — deliberation conversation.
- `AgentDecisionSummary` — Initiative reasoning.
- `AutoTopic → HiveMindSession → AgentDecisionSummary → Initiative`.

**Major models.**
- `Initiative` — linked to Signal via AutoTopic; linked to Deliverable
  via content decision.
- `Dream` — unvalidated opportunity.
- `HiveMindSession` — deliberation record.
- `AgentDecisionSummary`.

**Major runtime flows.**
- Spider → Signal → AutoTopic → HiveMindSession → decision →
  Initiative → execution.
- 24h age gate auto-approve on stages 4 & 5.

**Existing documentation.** `docs/topics/initiative-pipeline.md`,
`docs/DREAM_INITIATIVE_WORKFLOW.md`.

**Research coverage.** MODERATE. Linkage pattern defined;
auto-progression gated.

**Architecture maturity.** WORKING. Cursor-based signal replay working
(S1131). Autonomous→initiative auto-creation is **UNCERTAIN** per
S1268 collaboration-audit §10 Q2 (no creation task traced).

**Known drift.** None specific.

**Known technical debt.** Autonomous→Initiative wiring uncertain.

### 3.13 Memory / Knowledge / Embeddings

**Purpose.** Store and retrieve agent-learned knowledge, conversational
memories, and episodic facts with semantic search via embeddings;
enable cross-agent learning feedback loops and personalization.

**Canonical entry points.**
- `core/services/embedding_service.py` — centralized OpenAI
  text-embedding-3-small (1536D); Redis cache (7-day TTL); cost
  tracking to LLMCallLog.
- `core/services/agent_learning_service.py:122` —
  `AgentLearningService`; per-user + per-agent Redis preference
  models; `record_interaction()` on every route.
- `core/services/memory_promotion_service.py` — auto-save ops facts
  from PA execution; score-gated (≥7 auto-save); milestone /
  identifier / wiring pattern matching; secret-redacted.
- `core/services/feedback_loop_engine.py:26` — PA-to-Agent feedback
  closure; populates `spider_context['pa_content_feedback']`.
- `core/services/conversation_memory_service.py`.
- Management: `backfill_spider_embeddings` (~85% coverage).

**Major models.**
- `AgentKnowledgeSource` (`core/models_unified_system.py:521`) — cross-
  agent knowledge; agent, knowledge_type, spider_category, title,
  summary, confidence_score, freshness_score, expires_at,
  feedback_positive/negative.
- `UserAgentLearning` (`.py:3912`) — per-user per-agent adaptive
  learning; learning_domain, learning_content, confidence_score,
  validation_count.
- `AgentMemory` (`.py:10787`) — episodic memory (success/failure/
  feedback/technique); valence, importance_score, safety_class,
  poison_risk_score, tags.
- `ConversationMemory` (`core/models/conversations/models.py:19`) —
  user-agent conversation history w/ pgvector 1536D embedding
  (S729).

**Major services.** `EmbeddingService`, `AgentLearningService`,
`MemoryPromotionService`, `FeedbackLoopEngine`,
`ConversationMemoryService`, `RAGObservabilityService`,
`ScopedRetrievalService`.

**Major APIs.**
- REST: `GET /api/v1/embeddings/search`,
  `GET /api/v1/memories/personal`, `POST /api/v1/documents/embed`.
- PA tools: `kb_tool` (Document table), `search_docs` (S1142 —
  chunked retrieval; `lru_cache(1)` per process on
  originating_session filter — **restart workers after
  build_docs_provenance**).
- Agent API: `_get_relevant_knowledge_for_task(task, limit=5)`,
  `_get_fresh_spider_intelligence(categories, hours=24, limit=5)`,
  `_record_learning_outcome(result, task, context)`,
  `_share_knowledge(...)`.

**Major runtime flows.**
1. **Knowledge Pipeline (S400 foundational):** Spider Data →
   `EmbeddingService` → pgvector → `LearningBridge` →
   `AgentKnowledgeSource` → `_get_relevant_knowledge_for_task()` →
   `BaseAgent._build_prompt()` injection
   (`core/agents/base_agent.py:1435`).
2. **Production RAG retrieval (S1234 D12 pivot):** query text →
   `EmbeddingService.create_embedding()` → pgvector CosineDistance
   over `DocumentEmbedding` → D9/D10 filter pushdown (category,
   document_class, is_pinned, min_session) → cosine ≥ 0.4 →
   importance_score from retrieval_boost
   (`core/rag_integration.py:27`).
3. **Per-user agent learning (S991):** Agent `route()` →
   `AgentLearningService.record_interaction()` → Redis preference
   models → `_get_user_context()` injection.
4. **PA-to-Agent feedback closure (S990):** PA publish/archive/
   revise → `_record_content_feedback()` → `AgentMemory`
   (memory_type='feedback', valence=±) →
   `UserAgentLearning.record_success/failure()` →
   `FeedbackLoopEngine.get_feedback_for_agent()` →
   `spider_context['pa_content_feedback']` injection.
5. **Auto-save ops facts:** PA turn → extract patterns → score
   (≥7 auto-save, 5–6 pending, ≤4 ignore) → dedup by content hash
   → `AgentMemory` saved.

**Existing documentation.**
- `docs/narratives/KNOWLEDGE_RAG_MEMORY.md` (S1158) —
  comprehensive narrative.
- `docs/topics/local-askdocs.md` — dedicated topic doc for
  `core.rag` vs `core.rag_integration` boundary.
- `docs/topics/agent-system.md` — "Agent Knowledge &
  Conversations" §14-day freshness window.
- `docs/topics/content-pipeline.md` — PA-to-Agent feedback (S990).
- `docs/handoffs/SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md`.

**Research coverage.** DEEP. Narrative doc comprehensive and recent.
All major models have file:line cites. Two RAG paths clearly
demarcated.

**Architecture maturity.** STABLE for core knowledge pipeline (S400+).
WORKING for production RAG (S1234 D12 pivot). EXPERIMENTAL for
`MemoryPromotionService` (scoring criteria undocumented). PARTIAL for
per-user learning (live but no A/B data on behavioural impact).

**Known drift.**
- Document chunk coverage unknown. S1142 reported 852 / 14,149
  chunks. No monitoring dashboard.
- `MemoryPromotionService` scoring criteria opaque.
- `search_docs` `lru_cache(1)` per process — must restart workers
  after corpus regen.
- 14-day freshness window hardcoded (`ConversationOrchestrator`).
- `AgentLearningService` state lives in Redis — per-process; worker
  recycle can lose recent learning.
- Knowledge pipeline learning bridges (9 migrated to `LearningBridge`
  ABC, S1115) — pattern still maturing.
- Embeddings cost tracking to LLMCallLog but no quota/cap.

**Known technical debt.**
- Two RAG modules (`core.rag`, `core.rag_integration`) share names but
  no consumer overlap; confusion vector for onboarding.
- Local Ollama corpus keyword-scored only; quality lower than
  production; developers may misdiagnose prod RAG quality via
  `askdocs`.
- `Document.document_type` choices include specialized types
  (YOUTUBE, URL, SPORTS_DATA, AGENT_LOG); ingestion may not handle
  all consistently.
- `spider_context['pa_content_feedback']` populated by
  `FeedbackLoopEngine` — whether `ContentWriterAgent` prompt-builder
  **reads** this is **UNKNOWN** (open in KNOWLEDGE_RAG_MEMORY.md §6).
- No versioning on `AgentKnowledgeSource`; mutations untracked.
- `ConversationMemory` embedding generation opt-in; risk of DB row
  without embedding.

### 3.14 RAG / Document Loading

**Purpose.** Load, chunk, embed, index, and retrieve documents via
semantic search; two lanes (production pgvector + local Ollama
keyword).

**Canonical entry points.**
- Production: `core/rag_integration.py:465` — pgvector + `Document`
  table.
- Local: `core/rag.py:81` — `.rag/corpus.jsonl` keyword.
- Ingestion: `build_docs_index`, `sync_docs_index_to_documents
  [--embed]`, `embed_documents`, `build_rag_corpus`.
- Backfill: `backfill_spider_embeddings` (every 15 min, batch — see
  §3.8 discrepancy).

**Major models.**
- `Document` (`content/models.py:325`) — title, document_type,
  file_path, raw_content, processed_content, status, category, tags,
  parent_document.
- `DocumentEmbedding` (`content/models.py:707`) — chunk_index,
  chunk_text, embedding_vector (1536D OpenAI), embedding_model,
  source_type, ingested_via, HNSW index.

**Major retrieval functions.**

| Function | Location | Path |
|----------|----------|------|
| `search_embeddings()` | `rag_integration.py:27` | Production |
| `get_rag_context()` | `rag_integration.py:167` | Production |
| `search_personal_memories()` | `rag_integration.py:207` | Production |
| `top_k()` | `core/rag.py:39` | Local keyword |
| `build_docs_context()` | `core/rag.py:71` | Local keyword |

**Chunking.**
- Production: configurable chunk + overlap; fields `chunk_index`,
  `chunk_size`, `overlap_size`, `context_before`, `context_after`;
  HNSW on `embedding_vector`.
- Local: fixed 1200-char chunks (`build_rag_corpus --chunk-size`);
  JSONL; gitignored.

**Existing documentation.**
- `docs/topics/local-askdocs.md`.
- `docs/narratives/KNOWLEDGE_RAG_MEMORY.md`.
- `docs/KNOWLEDGE_PIPELINE.md` — flow map.

**Research coverage.** DEEP.

**Architecture maturity.** STABLE for production. PARTIAL for local
(keyword-only, no semantic signal). Embedding cadence for documents
**UNKNOWN**.

### 3.15 Documentation / Research Knowledge System

**Purpose.** Maintain `docs/` corpus as a living knowledge base;
auto-generate indices; verify claims against runtime; separate
research library governance.

**Canonical entry points.**
- `build_docs_index` — `docs/**/*.md` → `docs/_index.json` +
  `docs/INDEX.md`.
- `build_docs_provenance` — `docs/_index.json` →
  `docs/_provenance.json` (S1145).
- `verify_doc_claims [--only-drift]` (S1099) — registry-based; 7
  drifts found in agent-system audit at inception.
- 4-step cascade for search visibility (memory rule): (1)
  `build_docs_index`, (2) `build_rag_corpus`, (3)
  `sync_docs_index_to_documents`, (4)
  `sync_docs_index_to_documents --embed`.
- Research library governance: `docs/research/ARCHITECTURE_INDEX.md`
  (v3, S1271) — 7 research docs registered.
- Doc governance: `docs/00-START-HERE/DOC_LIFECYCLE.md` §2c
  (inventory-wins-on-conflict rule).

**Major surfaces.**
- `docs/` (primary), `docs/narratives/` (batch H narratives),
  `docs/handoffs/` (676 numbered files), `docs/archive/handoffs-pre-800/`,
  `docs/research/` (7 files — 6 research + 1 index).
- `docs/_index.json` — frontmatter (subsystems, decision_types,
  status, see_also, supersedes) + outbound/inbound cross-refs.
- `docs/INDEX.md` — human index (auto-generated).
- `docs/_provenance.json` — chunk provenance.

**Claim registry.** S1099 established `ClaimResult` +
`@register_claim` decorator. Severity: ok / skipped / low / medium /
high / critical / error.

**Existing documentation.** Meta: itself.

**Research coverage.** CANONICAL (specifically for the research
library governance layer; general docs coverage is uneven).

**Architecture maturity.** STABLE for research library governance.
WORKING for general docs. **Coverage unknown** — no metric on how
much of the codebase is documented.

**Known drift.** 7 drifts found in S1099 agent-system audit.

**Known technical debt.**
- Frontmatter (subsystems, decision_types, see_also) requires manual
  maintenance; no enforcement.
- Stale docs risk when narrative anchor stops being refreshed against
  inventory anchor (S1223 refresh was the last).

### 3.16 Human Interface / HumanAttention

**Purpose.** Route agent-generated items requiring human
decision-making (arbitrage signals, approvals, verification,
escalations) with attention queue, urgency levels, and verification
feedback loop for learning.

**Canonical entry points.**
- `core/models_human_interface.py:20-227:HumanAttentionItem`.
- `core/models_human_interface.py:230-266:HumanFeedbackRecord`.
- `core/models_human_interface.py:268-358:HumanPreference`.
- `core/services/human_attention_bridge.py:HumanAttentionBridge`
  (UNKNOWN implementation).
- `core/services/human_attention_lifecycle.py:HumanAttentionLifecycleService`
  (lines 36-728).
- Frontend surfaces: `CommandCenterPage.tsx` (Attention Queue
  sidebar), `BoardroomTab.tsx`.

**Major models.**
- `HumanAttentionItem` — UUID PK; source_type/source_id/source_agent;
  item_type; title/summary/payload; urgency (critical/high/medium/
  low); status (pending/viewed/acted/deferred/ignored/expired/
  watching/verified); decision (decision, decision_feedback,
  decided_at, time_to_decision_ms); ML context (ml_prediction,
  ml_confidence, ml_recommendation); verification (verification_
  outcome, verified_at, verification_profit, event_completed_at —
  S746). Indexes on (user, status), (user, urgency), (source_type),
  (created_at).
- `HumanFeedbackRecord` — HAI FK, decision + feedback_text +
  confidence; ML context snapshot; `fed_to_ml` flag.
- `HumanPreference` — per-user collab policy; `topic_weights` /
  `source_weights` — **NEVER POPULATED** (F5 finding, governance
  research §1.4).

**Major services.**
- `HumanAttentionLifecycleService` — auto-expire/dismiss/escalate/
  approve; beat: `process_human_attention_lifecycle` every 10 min;
  auto-escalate ladder LOW(72h) → MEDIUM(48h) → HIGH(24h) →
  CRITICAL(auto-dismiss 3d).
- `FeedbackProcessor` (`core/models_feedback_processing.py:122-180,
  216-330`) — classifies HumanFeedbackRecord positive/negative
  post_save → creates `AgentLearning` + `LearningInsight` (only
  round-trip with learning).
- `HumanInterfaceService`
  (`core/services/human_interface_service.py:295-353,738`) —
  `record_decision()` writes HAI + HumanFeedbackRecord + triggers
  ML feedback.

**Existing documentation.**
- `docs/narratives/FRONTEND.md` §"Command Center Now Hub".
- `docs/research/governance_authority_evolution.md` (S1269) — human
  plane inventory.
- Session 746 model docstring — DECISION_WATCH + verification.

**Research coverage.** MODERATE.

**Architecture maturity.** WORKING. Model + frontend surface exist;
decision recording works. Verification loop (S746) partial —
outcome tracking in place but trigger execution unclear.

**Known drift.**
- HumanPreference `topic_weights` / `source_weights` set locally in
  `update_learned_stats()` but **never saved** (F5 in governance
  research).
- `_broadcast_thread_update()` referenced in `views_inbox.py:177` —
  consumer not identified.

**Known technical debt.**
- Two-layer lifecycle (bridge + lifecycle service) not consolidated.
- Verification loop trigger points undocumented (who calls
  `record_verification`?).

### 3.17 Inbox / Messaging / Notifications

**Purpose.** User-to-user direct messaging, Rigby-routed messages,
and three notification surfaces (Web Push, mobile push via Expo,
Discord).

**Canonical entry points.**
- `core/models_messaging.py:21-141` — MessageThread + ThreadParticipant
  + DirectMessage.
- `core/views_inbox.py` — REST: `GET/POST /api/inbox/threads/`,
  `.../messages/`, `.../read/`, `.../unread-count/`.
- Frontend: `frontend/src/pages/InboxPage.tsx` → `/inbox`.
- `core/models_push_notifications.py` — PushSubscription (RFC 8030 +
  VAPID) + NotificationPreference.
- `core/models_mobile.py:MobilePushToken` +
  `core/services/expo_push.py`.
- `core/services/discord_notifications.py` (implementation UNKNOWN).

**Major models.**
- `MessageThread` (21-67): thread_type (dm/group/rigby_routed);
  participants M2M through ThreadParticipant; metadata JSON;
  is_archived.
- `ThreadParticipant` (69-97): last_read_at, is_muted, unread_count
  property.
- `DirectMessage` (99-141): sender (nullable FK), body, sender_type
  (user/rigby/system), metadata (routed_by, priority,
  original_prompt).
- `PushSubscription` (14-93): endpoint (unique RFC 8030), p256dh_key
  + auth_key (ECDH), browser/device_type/user_agent, is_active,
  failure tracking.
- `NotificationPreference` (95-150+): OneToOne user;
  notifications_enabled; arb_alerts_enabled + min_profit_pct + sports;
  line_movement_enabled + threshold; quiet_hours; max/hour.
- `MobilePushToken` (`core/models_mobile.py:9-34`): user FK, token
  (unique Expo), platform (ios/android), device_name, revoked_at.

**Major services.**
- `PushNotificationService`
  (`core/services/push_notification_service.py:20-150+`) —
  `send_notification()`, `send_arb_alert()`; pywebpush + VAPID;
  respects `NotificationPreference` per user; NotificationLog for
  rate limits; failure tracking.
- `expo_push.py` — Expo push wrap (UNKNOWN details).
- `discord_notifications.py` — Discord dispatch (UNKNOWN details).

**Major runtime flows.**
- **Direct messaging:** create thread w/ dedup (exact 2-user match) →
  send initial message → broadcast (WebSocket consumer UNKNOWN) →
  read tracking via `last_read_at`.
- **Rigby-routed:** thread_type='rigby_routed', metadata={routed_by:
  'rigby', original_prompt}.
- **Push notifications:** signal → `send_arb_alert()` → query
  PushSubscription (is_active) + join NotificationPreference → filter
  per user prefs → `webpush()` VAPID → 404/410 → mark_failed;
  success → mark_success.

**Existing documentation.**
- Model docstring: "Direct messaging between platform users, with
  Rigby as an optional routing intermediary."
- S562 comment in push notifications: RFC 8030 + VAPID.

**Research coverage.** MODERATE (–DEEP).

**Architecture maturity.** WORKING for messaging + Web Push. Expo +
Discord service exist; impl unknown.

**Known drift.**
- `_broadcast_thread_update()` WebSocket consumer unidentified.
- `NotificationLog` model referenced but not confirmed by grep.
- Mobile push (Expo) models present but no registration UI in React
  code observed.

**Known technical debt.**
- **Three notification systems** (Web Push, Expo, Discord) likely have
  different state machines / rate limiting / audit surfaces.
- No consolidated notification history/audit log.

### 3.18 Frontend / Workspace UI

**Purpose.** React + Vite SPA (bundle 2,253 KB, −26.5% since S1100).
Five primary workspace tabs (home/work/build/intelligence/system) with
nested sub-tabs. Command Center (/), Betting Dashboard (/betting),
Stocks Dashboard, studios (image/video), 61 total routes.

**Canonical entry points.**
- `frontend/src/App.tsx` — 61 routes via React Router v6.
- `frontend/src/pages/WorkspacePageNew.tsx` — 5-tab modular layout.
- `frontend/src/pages/CommandCenterPage.tsx` — Home page /; "Now"
  Hub; PA chat (70%); sidebar tabs.
- `frontend/src/pages/BettingPage.tsx` → `/betting` — 9-tab betting
  dashboard.
- `frontend/src/pages/InboxPage.tsx` → `/inbox`.
- `frontend/src/pages/StockIntelligencePage.tsx` → `/stocks`.

**Major TypeScript models.**
- `Workspace` (workspaceApi types).
- `WorkspaceTab` — primary tab ID.
- `Message` (CommandCenterPage.tsx:73-82) — role
  (user/assistant/tool/system), content, tools_used[], async_jobs[],
  feedback, source.
- `AsyncJob` (CommandCenterPage.tsx:63-71) — task_id, agent, status,
  timing, image_url.
- `MLPrediction` (backend) — game_id, prediction, confidence, odds.
- `PendingDecision` (CommandCenterPage.tsx:103-113) — id, title,
  urgency, ml_recommendation, ml_confidence.

**Major components.**
- **5-tab workspace (S1100):** `home`, `work` (queue/deliverables/
  initiatives/outreach), `build` (content/campaigns/voices/
  conceptforge), `intelligence` (dataintel/knowledge/consciousness),
  `system` (ops/incidents/alerts/boardroom/autopilot/cost/queues/
  config/audit/triggers/evaluation/files/git).
- Legacy mapping: 18 → 9 (S969b) → 5 (S1100). Adapter:
  `normalizeWorkspaceTab()` + `legacyTabToSubTab()` +
  `controlledSubTab` prop (4 tabs adopted).
- **Command Center "Now" Hub (S931):** header + 3 panels (Attention
  Queue, Active Work, System Pulse); Intelligence Desks Panel
  (S1000).
- **PA integration (3 surfaces):** `GlobalPADock`, `CommandCenterPage`,
  `AssistantPage`. All: `POST /api/pa/chat/` → poll every 2s.
- **Page telemetry:** `usePageTracking()` (`hooks/usePageTracking.ts`)
  → fire-and-forget `POST /api/v1/telemetry/page-view/` to Redis.
- **Zustand stores:** `paStore`, `workspaceStore`.

**Major runtime flows.**
1. **Command Center Load:** `/api/home/boot-data/` +
   `/api/human/attention-pending/` + `/api/home/active-work/` +
   `/api/home/system-pulse/`.
2. **PA Chat:** `POST` → `{task_id}` → poll `status/<id>/` every 2s
   → render.
3. **Workspace tab nav:** URL `?tab=work&sub=queue` → extraction →
   `legacyTabMapping` check → delegate component.
4. **Betting Dashboard:** odds today + sharp action + AI record
   (S1100 dedup fix).
5. **Page telemetry:** every route → fire-and-forget → Redis counters.

**Existing documentation.**
- `docs/narratives/FRONTEND.md` (S1158, 316 lines) — CANONICAL.
- `docs/topics/frontend.md` — companion.
- S1100 milestone (5-tab consolidation), S931 (Command Center
  unification), S1000 (Intelligence Desks).

**Research coverage.** DEEP.

**Architecture maturity.** STABLE.

**Known drift.**
- Tab count: PLATFORM_INVENTORY autoblock says "9 betting tabs" vs
  topic doc enumerates 12 (Hub/Overview/Today's/Top Plays/Sharp/Arb/
  Watching/Live Odds/Bankroll/My Wagers/Markets/AI Record). Probably
  "9 primary" vs "12 total".
- Bundle analysis missing.
- Frontend telemetry no documented retention policy on Redis.

**Known technical debt.**
- Two-layer tab mapping (18 legacy → 9 canonical → 5 primary)
  requires understanding both normalizer + sub-area mapping.
- `controlledSubTab` is convention, not enforcement.
- PA polling fixed at 2s (no backoff, no max-retries).

### 3.19 Mobile App

**Purpose.** Expo-based React Native mobile app for iOS/Android with
Expo push notification support.

**Canonical entry points.**
- `core/models_mobile.py:MobilePushToken` (line 9-34).
- `core/mobile_authentication.py` (UNKNOWN implementation).
- `core/views_mobile.py` (UNKNOWN endpoints).
- `core/services/expo_push.py`.
- Migration: `core/migrations/0257_mobile_push_token.py`.

**Major runtime flows.**
1. App launches → Expo.Notifications permission → get token.
2. `POST /api/mobile/register-token/` (likely) → create
   MobilePushToken.
3. Signal → Expo dispatch → 410 gone → `MobilePushToken.revoke()`.

**Existing documentation.** Model docstring only. No dedicated docs.

**Research coverage.** LIGHT.

**Architecture maturity.** PARTIAL.

**Known drift.**
- UNKNOWN if mobile app is actively used or planned-only.
- UNKNOWN if mobile auth uses Fleet or something different.
- UNKNOWN if mobile has own UI surfaces or mirrors web.

**Known technical debt.**
- Mobile auth strategy undocumented.
- Expo push failure handling (revoked_at) presumably in `expo_push.py`
  but logic not visible.
- No frontend/mobile code in this repo (likely separate Expo project).

### 3.20 Discord Bot

**Purpose.** Cross-platform command surface via Discord slash + prefix
commands (96 total / 48 slash + 48 prefix / 25 Cog classes in single
11,676-line `discord_bot.py`).

**Canonical entry points.**
- `core/services/discord_bot.py` — 11,676 lines; 25 Cog classes; 48
  `@app_commands.command` slash + 48 `@*.command` prefix.
- `docs/DISCORD_INTEGRATION.md` (per `CLAUDE.md`).
- `docs/DISCORD_AUDIT.md`.

**Command categories.**
- Status: `/status`, `/agents`, `/trending`.
- Interactive: `/ask` (PA query), `/create` (image gen), `/research`
  (spider), `/clear`, `/sessions`, `/link`, `/unlink`.
- Content: `/gallery`, `/profile`, `/opportunities`, `/apply`,
  `/track`, `/digest`, `/alerts`, `/subscribe`, `/tier`.
- Voice: `/voice join|leave|ask`, `/speak`, `/clone`.
- Sports: `/predictions`, `/odds`, `/arb`, `/bankroll`, `/bet`,
  `/resolve`, `/futures`, `/slip`.
- Content Pipeline: `/create-content`, `/content-status`.
- Series: `/series create|status|list|view`.
- Studio: `/studio create`.

**Cross-platform continuity.** S455: `DatabaseConversationHistory`
linking Discord conversations to `ChatConversation`.

**Existing documentation.**
- `docs/DISCORD_INTEGRATION.md` — canonical.
- `docs/DISCORD_AUDIT.md`.
- `docs/DISCORD_COMMANDS.md`.
- `docs/DISCORD_BOT_SETUP.md`.

**Research coverage.** MODERATE.

**Architecture maturity.** WORKING.

**Known drift.** Bot commands lag agent registry evolution; count
tables can drift.

**Known technical debt.**
- Single 11,676-line file with 25 Cog classes — refactor candidate.
- Rate limiter (lines 85-122) is per-command; no unified rate strategy
  with PA / API.

### 3.21 Voice / Avatar Surfaces

**Purpose.** Text-to-speech, image-to-video, and streaming avatar
integrations for PA chat, Discord voice, content voiceover, and
face-to-face demos.

**Canonical entry points.**
- `core/services/elevenlabs_tts_service.py` — TTS for PA chat, Discord
  `/ask-voice`, content voiceover.
- `core/assistant/video_tools.py` — combines TTS + Runway (image-to-
  video) + Lip Sync (Sync Labs).
- `core/services/realtime_avatar/heygen.py` — HeyGen streaming avatar
  (F2F.1 stub; F2F.3 planned).
- `core/models_voice_marketplace.py` +
  `core/services/content_voice_system.py` — voice selection (12+
  voices).

**Existing documentation.** Feedback memory notes on avatar
architecture split (`feedback_avatar_architecture_split.md`,
`feedback_runway_tool_descriptions_gate_selection_not_narration.md`).

**Research coverage.** LIGHT.

**Architecture maturity.** PARTIAL. ElevenLabs TTS + Runway image-
to-video working. HeyGen F2F **EXPERIMENTAL** — stub only, real
wiring in F2F.3 (not shipped).

**Known drift.** HeyGen F2F.1 is stub; constructor validates
`HEYGEN_API_KEY` but methods raise `NotImplementedError`.

**Known technical debt.** No voice/avatar architecture doc; roadmap
lives only in code comments.

### 3.22 API Layer (REST + WebSocket)

**Purpose.** Expose platform capabilities via REST endpoints
(1,857 URL patterns / 208 view files) and WebSocket (51 consumers +
patterns).

**Canonical entry points.**
- `core/urls.py`, `core/urls_unified.py`, `core/urls_real_data.py`.
- `core/routing.py` — WebSocket `websocket_urlpatterns`.
- `core/asgi.py` — Daphne + Channels.
- `core/services/fleet_auth_drf.py` — Fleet HMAC signed-request auth
  (S1129).

**Sample REST endpoints (by domain).**
- PA: `POST /api/pa/chat/`, `GET /api/pa/chat/status/<task_id>/`.
- Inbox: full CRUD + read/unread.
- Home: `/api/home/boot-data/`, `/api/human/attention-pending/`,
  `/api/home/trigger-desks/`, `/api/home/active-work/`,
  `/api/home/system-pulse/`.
- Betting/sports: `/api/odds/today/`, `/api/sharp-action/`,
  `/api/predictions/ai-record/`, `/api/odds/`, `/api/wagers/`.
- Telemetry: `/api/v1/telemetry/page-view/`.
- LLM routing (S699): `/api/v1/llm-routing/status|providers|models|
  agent-configs|logs|cost-analytics`.

**Sample WebSocket consumers.**
- `/ws/pa/conversations/<id>/` → `PAConversationConsumer`.
- `/ws/assistant/` → `PersonalAssistantV2Consumer`.
- `/ws/command-center/` → `CommandCenterAIConsumer`.
- `/ws/intelligence/` → `CommandCenterConsumer`.
- `/ws/decisions/` → `CommandCenterConsumer`
  (`core/routing.py:101` — decision command stream).
- `/ws/agents/`, `/ws/agent-monitor/`, `/ws/agent-platform/`,
  `/ws/orchestration/<id>/`.
- `/ws/sports/updates/`, `/ws/live-sports/`, `/ws/arbitrage/`.
- `/ws/dashboard/`, `/ws/activity/`, `/ws/consciousness/`,
  `/ws/control/`.

**Auth patterns.**
- Web: SessionAuthentication + TokenAuthentication.
- Mobile: UNKNOWN.
- Fleet (S1129): FleetSignatureAuthentication; hybrid routes
  (`/api/pa/chat/`) work with user auth or signed requests.

**Existing documentation.**
- `docs/API.md` (content not fully verified).
- `docs/API_PATH_POLICY.md`.
- `docs/archive/superseded-.../FRONTEND_INTEGRATION_NOTE.md` (S699
  LLM routing).

**Research coverage.** MODERATE. 1,857 routes; only ~10-20 traced in
sub-agent sweeps; sample-only.

**Architecture maturity.** STABLE for wired routes; MODERATE for full
coverage.

**Known drift.**
- LLM routing endpoints (S699) ready for frontend but no evidence of
  UI implementation.
- UNKNOWN: how many endpoints map to frontend vs internal-only.

**Known technical debt.**
- PA polling hardcoded 2s (no backoff / max-retries).
- 51 WebSocket consumers — high fragmentation; no unified consumer
  or message broker visible.
- Async job model on frontend duplicates Celery Task schema; no
  shared serialization layer.

### 3.23 Governance / Authority

**Purpose.** Runtime control of platform autonomy modes, emergency
kill switches, authority contracts for employee agents, human approval
gating, LLM cost enforcement.

**Canonical entry points (from S1269 canonical audit).**
- `core/models_governance.py:17-189` — GovernanceState + KillSwitch.
- `core/employees/jobs.py:41-162` — AuthorityLevel enum + JobContract.
- `core/services/ops_autopilot/governance.py:2159-2529` —
  GovernanceEngine.
- `core/services/pa_tool_schemas.py:3157-3219` +
  `core/services/td_handlers_ops.py:2760-3035` — `governance_tool`.
- `core/models_human_interface.py:20-358` — HumanAttentionItem +
  HumanFeedbackRecord + HumanPreference.
- `core/llm_enforcer.py:200-260` — LLMEnforcer freeze gate.
- `core/employees/mission_runner.py:835-900` —
  `_emit_authority_contract_event`.

**Major models.** GovernanceState, KillSwitch, JobContract,
AuthorityLevel enum, HumanAttentionItem, HumanFeedbackRecord,
HumanPreference, OpsRun+OpsRunEvent (authority_contract_observed),
OrchestrationApprovalGate.

**Major services.** GovernanceEngine, HumanAttentionLifecycleService,
FeedbackProcessor, HumanInterfaceService, MissionRunner (warn-mode
observer).

**Major APIs.**
- REST: `@permission_classes([IsAuthenticated])` gates 30+ PA
  endpoints; staff-required paths
  (`core/auth_middleware.py:610-614`); reviewer-blocked paths (615-
  623).
- PA tool `governance_tool` actions: `governance_status`, `_set_mode`,
  `_kill_switch`, `_deactivate_switch`, `_throttle_report`, `_audit`.
- Management: `run_<job>` (operator-gated), `employee_tool` (PA-gated).

**Major runtime flows (autonomy plane — partial enforcement).**
- Operator: `governance_tool.set_mode(mode='freeze', scope='global',
  ttl=3600)` → GovernanceState row → sync
  `budget_freeze_active=true` → SystemConfiguration.
- **4 active consumers:** spider network
  (`core/tasks_spiders.py:381-398`), signal aggregation (207-227,
  968-971), workspace pipeline
  (`workspace_pipeline_runner.py:43-49`), LLMEnforcer.
- **NOT enforced:** KillSwitch targets, throttle mode, per-(agent/
  desk) scopes, authority dict blocks.

**Authority observation (warn-mode).** MissionRunner writes one
`OpsRunEvent(label='authority_contract_observed')` per run; never
blocks.

**Existing documentation.**
- `docs/research/governance_authority_evolution.md` (S1269, CANONICAL).
- `docs/research/symbol_mapping_architecture.md` (S1270 — WHAT
  companion).
- `docs/research/actor_identity_attribution_architecture.md` (S1271 —
  WHO companion).
- `docs/PLATFORM_INVENTORY.md` §2.
- `docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`.
- `docs/governance_redesign.md`.

**Research coverage.** DEEP + CANONICAL.

**Architecture maturity.** PARTIAL. Four planes exist and don't
compose:
- Autonomy plane freeze/safe_mode wired at 4 consumers.
- Authority plane observation-only.
- Budget plane one-way sync.
- Human plane round-trip w/ learning working but topic_weights dead.

**Known drift.**
- F1 (authority observation-only): JobContract.authority zero
  runtime readers.
- F2 (KillSwitch write-only): 6 target_detail fields never read at
  dispatch.
- F5 (HumanPreference fields): topic_weights/source_weights never
  populated.
- F7 (throttle + per-scope): model supports, zero consumers.
- Q1 (approval gate auto-approve): `check_auto_approvals()` exists
  (`core/services/orchestration_approval.py:214-262`) but call site
  not in beat schedule or `tasks.py`.

**Known technical debt.**
- Symbol mapping unbuilt — required blocker for warn→enforce
  transition.
- Reverse-sync GovernanceState → LLMEnforcer missing.
- KillSwitch dead code.
- Multi-approver not supported (single human decision actor assumed).

### 3.24 Automation / Scheduler / Celery

**Purpose.** Distributed task execution, scheduled beat jobs,
queue-based routing, worker pool management.

**Canonical entry points.**
- Static: `core/celery.py:app.conf.beat_schedule` (77 entries;
  PLATFORM_INVENTORY autoblock says 91 enabled + 5 disabled = 96 DB
  rows).
- Topology: `Procfile` (11 entries).
- Registry: `core.celery.app.tasks` — 414 user-defined
  (PLATFORM_INVENTORY autoblock).
- Routing: `core.settings.CELERY_TASK_ROUTES` (8 queue types +
  globs).
- Observability: `core/celery_telemetry.py:74-177` (task_prerun/
  postrun/failure signal handlers).
- Beat DB: `django_celery_beat.PeriodicTask` (179 fixed in S1064).

**Major models.**
- `CeleryTaskEvent` (`core/models_celery_telemetry.py:17-100`) —
  task_id, task_name, queue, status, worker, times, RSS start/end/
  delta, error_type, error_message, agent_name (S1169, from prerun
  kwargs), priority_matched. **30-day retention.**
- `PeriodicTask` — runtime rows synced from celery.py. Queue field
  critical (overrides `CELERY_TASK_ROUTES` if set).

**Major services.**
- `CeleryHealthService` (`core/services/celery_health.py`) — worker
  ping + queue depth + task age (S1115 cap 34s → 1.5s).
- Signal handlers (`core/celery_telemetry.py:74-177`).

**Major APIs.**
- REST: `GET /api/celery/breakdown/?window=60m&limit=25`.
- PA tool: `task_breakdown_tool`.

**Worker topology (Procfile, Railway):**

| Worker | Queue(s) | Pool | Concurrency | Memory | Recycle | Purpose |
|--------|----------|------|-------------|--------|---------|---------|
| celery-worker | default, agents, sports | prefork | 1 | 150MB | 5 tasks | Lightweight DB-query tasks (~28) |
| celery-pa | pa | prefork | 1 | 200MB | 10 tasks | PA chat queries |
| celery-content | content | prefork | 1 | 250MB | 2 tasks | Blog gen, podcasts, initiatives (~19) |
| celery-long-running | long_running, ml | prefork | 2 | 150MB | 2 tasks | Agent exercises, LLM, embeddings, spiders (~52) |
| celery-long-running-2 | long_running, ml | prefork | 2 | 150MB | 2 tasks | Second worker for capacity |
| celery-broadcast | broadcast | threads | 3 | 200MB | 50 tasks | High-frequency status (~4) |
| celery-beat | (scheduler) | — | — | — | — | Drives 77 beat entries |
| code-worker | code_jobs | prefork | 1 | 400MB | 1 task | Code generation |

**OOM prevention history:** S1000C (60+ heavy tasks moved to
long_running), S1029 (5 more), S1043 (9 more), S1063 (46 unrouted
routed), S1064 (179 PeriodicTask.queue misroutes fixed via
`sync_task_queues`).

**Beat schedule categories:** diagnostics (3× daily 7:15/7:30/7:45
AM), spider network (2× 30m), content, sports (8 scheduled),
monitoring (3 every 10m via broadcast), cleanup (20+ daily).

**Existing documentation.**
- `docs/topics/celery-workers.md` — canonical.
- `docs/BEAT_AUDIT.md` — 77 entries, 100% resolve.
- `docs/CELERY_AUDIT.md` — 414 tasks, 391 with callers, 10 orphans.
- `docs/AUDIT_FINDINGS.md` §12-14 — canonical Celery deferred list
  (memory rule).
- `Makefile` — local pool workarounds.

**Research coverage.** DEEP + CANONICAL.

**Architecture maturity.** STABLE.

**Known drift.**
- Throttle mode + per-scope not consumed (F7 implicit).
- 10 orphan tasks (per CELERY_AUDIT.md); mostly intentional/deferred
  per AUDIT_FINDINGS §12.

**Known technical debt.**
- **55 of 77 beat entries route to `default` queue.** Celery-worker
  drop = half the platform stops ticking.
- `PeriodicTask` queue sync required on every deploy.
- `QueuePreservingScheduler` custom (`core/schedulers.py`) required.
- Docstring coverage: 220/414 tasks (55%) lack docstrings — audit
  relies on them.
- Three independent agent dispatch systems (S1029): `run_*_agents()`,
  `AGENT_WORKSPACE_REGISTRY`, `MetricsActionTrigger` — disabling one
  doesn't stop others.

### 3.25 Observability / Telemetry / SLOs

**Purpose.** Multi-layer event capture across task execution, LLM
calls, agent runs, mission steps, and body-system health.

**Canonical entry points.**
- Task: `core/models_celery_telemetry.py:CeleryTaskEvent` +
  `core/celery_telemetry.py:74-177`.
- LLM: `core/models_llm_telemetry.py:30-100:LLMCallEvent` +
  `core/services/llm_call_wrapper.py` (S1098).
- Ops runs: `core/models_ops_runs.py:11-117:OpsRun + OpsRunEvent`
  (domain='ops|mission', S1250 PR3).
- Agent exec: `intelligence/models/agent_execution.py` +
  `core/agent_execution_wrapper.py` +
  `core/services/execution_tracker.py`.
- Body: `core/services/body_vitals.py:run_all_systems_scan` +
  `core/models_heart.py:HeartBeat`.
- Ops autopilot: `core/services/ops_autopilot/` — CTO/COO/Trend
  daily diagnostics.
- SLO: `core/tasks.py:12492:check_learning_loop_slo` (daily 9 AM;
  usage_rate ≥ 5% over 24h).

**Major models (14+ event-shaped per EVENT_SYSTEM_INVENTORY.md).**
- **Live, wired:** CeleryTaskEvent, LLMCallEvent, ImpactEvent,
  DeliverableEvent, OpsRunEvent, TriggerEvent, FleetEvent.
- **Defined, unverified writers:** CockpitIncidentEvent,
  CockpitAutopilotEvent, EngagementEvent, ThreatEvent, ABTestEvent,
  ConversionEvent, BadContextEvent, RelationshipEvent,
  ToolCallRecord (S861).
- **Adjacent audit/log:** AuditLog, AuditReport/Finding/
  RemediationTask/VerificationRun (S819), CockpitAuditLog,
  NotificationLog, LLMCallLog, StageTransitionLog, SpiderExecutionLog,
  PerformanceLog, AutonomousActionLog, CodeJobLog,
  WebSocketConnectionLog, ResumeOptimizationLog.

**Major services.**
- Signal handlers (CeleryTaskEvent lifecycle).
- LLMCallWrapper (S1098): pre/post LLM call → LLMCallEvent w/
  execution_id correlation.
- BodyVitalsService: `run_all_systems_scan` every 10m via
  `run_heartbeat`; monitors 9 systems.
- OpsAutopilot diagnostics: CTO daily (reliability + failure spikes),
  COO daily (velocity drop + rework), Trend Analysis daily
  (volume drop + silent spider + concentration spike).
- DiagnosticPipelineService: runs all 3 + gate flags + posts to
  governance inbox.
- ToolCallRecord (`core/models_tool_calls.py:19`) — per-tool-call
  telemetry (S861); S1115 fixed dispatcher to write on all return
  paths.

**Major APIs.**
- REST: `GET /api/celery/breakdown/`, `GET /api/health/ping/`.
- Management: `check_learning_loop_slo`, `run_all_systems_scan`.
- PA tools: `task_breakdown_tool`, `celery_task_history`,
  `ops_run_tracker`, `system_health_tool`,
  `nervous_system_message_stats`.

**Existing documentation.**
- `docs/EVENT_SYSTEM_INVENTORY.md` — CANONICAL (14+ event models,
  40+ signal receivers, 57 WebSocket consumers, v0 intake surface
  recommended).
- `docs/topics/celery-workers.md` §Observability.
- `docs/BODY_SYSTEM_AUDIT.md`.
- `docs/handoffs/SESSION_983_CELERY_OBSERVABILITY_AND_SKIN_FIX.md`.

**Research coverage.** DEEP.

**Architecture maturity.** WORKING. Rich event system; **no central
Rigby v0 intake** yet (RIGBY_EVENT_INTAKE_ENABLED=False).

**Known drift.**
- 4-5 parallel execution telemetry layers exist; no dedup audit.
- Body systems "cold-start" issue: digestive + muscular report
  sluggish/paralyzed on fresh DB (AUDIT_FINDINGS §16).
- HeartBeat collection never exported — no dashboard/alerting.

**Known technical debt.**
- Observability deduplication needed.
- SLO check not systemic — one task-specific check; no meta-SLO
  framework.
- Body systems informational-only — no feedback loop to governance.
- AgentExecution cleanup vs LLMCallEvent retention decoupled; risk
  of detail loss.
- Event-to-action gap: DeliverableEvent exists but no Rigby decision
  logic reads it.

### 3.26 External Integrations

**Purpose.** Third-party API connectivity (Stripe, GitHub, LLM
providers, sports/financial data sources, spider registry).

**Canonical entry points.**
- Stripe: `core/services/stripe_subscription.py`,
  `core/services/stripe_voice_payments.py`.
- LLM providers: `core/services/openai_client_factory.py:98-196`,
  `core/services/anthropic_client_factory.py:74-94`.
- Sports/Financial APIs (via tasks): Alpha Vantage, Polygon.io, SEC
  Edgar, Coinbase, Etherscan, Kalshi, TheOdds.
- Spider network: 80 spiders across 41 categories
  (`ai_core/spiders/spider_registry.py`).

**Major services.**
- OpenAI factory: reasoning-model guard (gpt-5.x forbidden kwargs
  max_tokens/temperature); guard mode via `OPENAI_REASONING_GUARD`
  env (warn/strip/error).
- Anthropic factory: forbidden kwargs (timeout/max_retries/api_key).
- Stripe subscription + voice payments.
- Spider registry (80 spiders, priority + placeholder flag).

**Existing documentation.**
- `docs/COMPREHENSIVE_DATA_SOURCES_2025.md`.
- `docs/topics/spider-network.md`.
- `docs/archive/superseded-.../EXTERNAL_APIS.md`.
- `.env.example`.
- **Feedback memories:** `feedback_anthropic_client_factory.md`,
  `feedback_openai_client_factory.md`,
  `feedback_gpt5_max_completion_tokens_floor.md`.

**Research coverage.** LIGHT.

**Architecture maturity.** STABLE.

**Known drift.**
- No external API cost tracking. `LLMCallEvent` tracks tokens;
  `cost_usd` absent. Stripe metrics separate from platform
  telemetry.
- Spider placeholder flag exists (0/80) but never checked.
- Third-party retry/timeout audit missing.

**Known technical debt.**
- LLM cost not materialized in USD in `LLMCallEvent`.
- Stripe webhook signature validation edge cases not comprehensively
  mapped.
- Spider failure modes undocumented.

### 3.27 Auth / Permissions / Security

**Purpose.** Request-level authentication, RBAC, staff/reviewer gates,
fleet signature verification, VIP demo mode.

**Canonical entry points.**
- `core/auth_middleware.py:563-681` — UnifiedTokenAuthenticationMiddleware
  (~108 PUBLIC_PATHS).
- `.py:541-544,610-614` — STAFF_REQUIRED_PATHS.
- `.py:548-556,615-623` — REVIEWER_BLOCKED_PATHS.
- `core/services/fleet_auth_drf.py:65-150` — FleetSignatureAuthentication
  (HMAC X-Fleet-Signature; permissive fallback).
- `core/vip_middleware.py:50-105` — VIP demo (read-only +
  workspace-scope; **prompt-only** — no runtime gate).
- Service tokens: `PA_DB_HEALTH_RPC_TOKEN`, `PUBLIC_INTEL_TOKEN`.

**Major services.** UnifiedTokenAuthenticationMiddleware, staff/
reviewer path gates, FleetSignatureAuthentication, VIP demo
middleware.

**Existing documentation.**
- `docs/research/governance_authority_evolution.md` §2.5 (36-45
  primitives).
- `docs/EMPLOYEE_OS_PRIMITIVES.md`.

**Research coverage.** LIGHT (compressed relative to blast radius per
Rigby S1273 review — deserves a dedicated trust-boundary + threat-model
research doc alongside a proper architectural contract).

**Architecture maturity.** **PARTIAL** (revised S1273 v2 per Rigby
review — previously listed as STABLE). The token auth path itself
works; but two known **unsafe edges** disqualify STABLE:
1. **VIP demo enforcement is prompt-only** — PA can ignore the
   "read-only" injection; no runtime gate on write operations from a
   `vip_demo_viewer` role. This is a soft gate, not an enforcement
   boundary.
2. **Fleet signature permissive fallback** — `FleetSignatureAuthentication`
   does NOT raise on missing/invalid signature; it flags as unverified
   and defers to downstream `FleetCapabilityRequired`. Two-layer gate,
   but the first layer is soft.

**Trust boundaries (explicit enumeration, per Rigby S1273 review).**
- **VIP viewer** — soft (prompt-only). Should NOT be treated as a
  hard boundary against writes.
- **Fleet callers** — HMAC canonical signature verification, but
  fallback is permissive, so real gate is downstream capability
  check.
- **Internal service tokens** (`PA_DB_HEALTH_RPC_TOKEN`,
  `PUBLIC_INTEL_TOKEN`) — service-specific gates; `PUBLIC_INTEL_TOKEN`
  default-off (endpoint 404s when unset).
- **Staff / reviewer path lists** — hard runtime gates
  (`core/auth_middleware.py:610-614` for staff, `615-623` for
  reviewer-write block); no centralized registry, maintained as
  Python lists.
- **Standard user token auth** — DRF `TokenAuthentication`;
  battle-tested.

**Known drift.**
- VIP demo enforcement is prompt-only — persistent from initial ship
  through S1273; no runtime API-layer gate has been added.
- Fleet permissive fallback design intent is ambiguous — is soft
  fallback intentional (grace-period rollout) or debt?

**Known technical debt.**
- VIP demo not API-layer enforced.
- Staff/reviewer paths maintained as lists; no centralized registry.
- Service token default-off design vs feature flag — tradeoff
  unclear.
- No threat model / trust-boundary doc exists; §3.27 here is the
  closest thing (research-only inventory, not a contract).

### 3.28 Configuration / Environment / Deployment

**Purpose.** Environment variables, Django settings, Railway
deployment, local dev, feature flags, diagnostics scheduling.

**Canonical entry points.**
- `core/settings.py` — Django settings module (NOT
  `config.settings`).
- `.env.example` — canonical local defaults.
- `Procfile` — 11 entries; PG_APPLICATION_NAME per-role tagging
  (S1166, regex `^dbz:[a-z0-9\-]+$`).
- `docker-compose.yml` — pgvector:pg15, redis:7-alpine, daphne,
  celery, flower, pgadmin, redis-commander, mailhog.
- `Makefile` — start, celery, restart, health, mobile, davinci.
- Release command: `migrate → sync_celery_beat → sync_task_queues
  → setup_codebase_workspace → setup_pa_service_account`.
- Feature flags: `core/settings.py:111-140`
  (MESSAGING_TOOL_ALLOW_SEND, RIGBY_*, CTO_DIAGNOSTIC_*, etc.).
- Diagnostic flags: `.env.example:375-436`.

**Major services.**
- Railway detection: `os.environ.get('RAILWAY_ENVIRONMENT')`.
- Workspace path self-healing (S1034):
  `_get_workspace_for_skin_layer()` auto-detects stale macOS local
  paths.
- DB pool: `DB_CONN_MAX_AGE=60`, pool_size=20, max_overflow=30.
- Redis: 3 DBs (0 broker, 1 cache, 2 session; 3 channels).
- Celery: `CELERY_BEAT_SCHEDULER='core.schedulers:QueuePreservingScheduler'`.

**Major management commands.**
- `sync_celery_beat --apply --create-only --disable-missing`
- `sync_task_queues --apply`
- `setup_codebase_workspace`, `setup_pa_service_account`
- `generate_platform_inventory` — runtime snapshot.
- `build_celery_audit`, `build_beat_audit`, `build_capability_audit`.
- `verify_doc_claims --doc <name>`.
- `run_<job>` (operator-gated).

**Existing documentation.**
- `docs/topics/infrastructure.md` — canonical.
- `Procfile`, `Makefile`, `docker-compose.yml` inline.
- `.env.example`.
- `docs/DEPLOYMENT_GUIDE.md`, `docs/DEPLOYMENT_QUICKREF.md`.

**Research coverage.** MODERATE.

**Architecture maturity.** STABLE.

**Known drift.**
- Cost budget (S1034): $1,200 → $1,500/month.
- Health check timeout Railway: 600s for migration-heavy deploys.

**Known technical debt.**
- `core/settings.py` ~2000 lines; no TOC / grouped comments.
- Diagnostic thresholds scattered across `.env.example` comments.
- 12 feature flags scattered; no centralized FeatureFlag model /
  registry.
- Workspace path brittle even w/ auto-healing.

### 3.29 Data Models / Persistence / Infrastructure

**Purpose.** PostgreSQL 15 + pgvector (585 concrete models / 23
apps), Redis 7 (3 DB indices), Daphne ASGI, Railway container
orchestration (11 processes, 512MB per container).

**Canonical entry points.**
- Database: pgvector/pgvector:pg15 (Docker; S1140 swap). Retention:
  `enforce_db_retention` daily 11 AM.
- Cache/broker: Redis 7-alpine; AOF persistence; max_memory 512MB;
  LRU eviction.
- ASGI: Daphne 0.0.0.0:8000 (`core.asgi:application`); HTTP timeout
  120s.
- Container: Railway per-container 512MB; ephemeral filesystem.
- Observability: PG_APPLICATION_NAME tagging (S1166) per Procfile
  role.

**Major models.** 585 concrete Django models across 23 apps
(PLATFORM_INVENTORY autoblock). Core models in `core/models/`
package (`__init__.py` imports from `models_*.py`; `core/models.py`
file is dead code).

**Major services.**
- Railway runtime: Procfile-driven, 11 long-lived processes,
  blue-green deploys.
- pgAdmin (local: 5050), Redis Commander (local: 8082), Flower
  (local: 5555), Mailhog (local: 8025).
- `check_celery_health` (every 10m, broadcast queue).

**Major APIs.**
- `GET /health/ping/` — Daphne liveness.
- `python manage.py check --deploy` — docker-compose healthcheck.
- `celery -A core inspect ping` — celery healthcheck.

**Major runtime flows.**
- Migration on release; lock hang mitigation = remove migrate
  temporarily.
- Redis AOF persistence w/ RDB snapshots.
- PG_APPLICATION_NAME: `dbz:web`, `dbz:celery-worker`, `dbz:celery-pa`,
  etc.; enforced by `scripts/verify_repo_guardrails.py`.

**Existing documentation.**
- `docs/topics/infrastructure.md`.
- `docs/DEPLOYMENT_GUIDE.md`, `docs/DEPLOYMENT_QUICKREF.md`.
- `docker-compose.yml`, `Procfile`, `Makefile`.
- `docs/DATABASE_MODEL_REFERENCE.md` — per `CLAUDE.md` "which DB
  table for what".

**Research coverage.** LIGHT.

**Architecture maturity.** STABLE.

**Known drift.**
- Workspace writes fail between Railway deploys (ephemeral) — S1034
  self-healing mitigation.
- pgvector `VectorField` cols exist but query patterns / perf
  undocumented.

**Known technical debt.**
- 585 models across 23 apps; no central schema registry / data
  dictionary.
- Data lifecycle policies scattered (30-day CeleryTaskEvent, 168-hour
  spider embeddings, etc.).
- Connection pool tuning (`DB_CONN_POOL_SIZE=20`) ad-hoc.
- Health checks informational — no auto-remediation.

### 3.30 Body Systems + BodyCoordinator

**Purpose.** Nine "body systems" model platform health as biological
subsystems, running as autonomic reflex layer via
`run_all_systems_scan` every 10 min.

**Canonical entry points.**
- `core/services/body_vitals.py:run_all_systems_scan` — 10m beat
  via `run_heartbeat`.
- `core/services/body_coordinator.py:110-300+` — autonomic reflex
  layer per S1268 collaboration audit §3.6.
- `core/models_heart.py:HeartBeat` — per-body-system snapshot.
- Nine systems (PLATFORM_INVENTORY autoblock): HEART, LUNGS,
  CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN.

**Runtime flow.**
- `run_heartbeat` beat (10m, broadcast queue) → `run_all_systems_scan()`
  → query 9 states → create HeartBeat row.
- Systems: breathing (live agent count), circulation (task flow),
  digestion (content pipeline), immune (threat), muscular (agent exec),
  nervous (WebSocket), skeletal (infra), spine_alignment (DB
  integrity), skin (system health score).

**Existing documentation.**
- `docs/topics/body-systems.md` — canonical.
- `docs/BODY_SYSTEM_AUDIT.md`.
- `docs/PLATFORM_INVENTORY.md` §Body Systems.

**Research coverage.** MODERATE.

**Architecture maturity.** WORKING. Informational — no feedback loop
to governance or execution.

**Known drift.**
- Cold-start issue: digestive + muscular report sluggish/paralyzed
  on fresh DB (AUDIT_FINDINGS §16).
- HeartBeat rows stored but no dashboard/alert surface.

**Known technical debt.**
- Body systems side-effect-free; no autonomic responses (freeze,
  throttle) despite name suggesting reflex layer.
- Nine systems mapped to biological metaphors; onboarding cost.

### 3.31 Event Bus / Streams

**Purpose.** Redis Streams pub/sub for event-driven architecture
across spiders, signals, opportunities, and validation.

**Canonical entry points.**
- `core/services/event_bus.py:90:EventBus` — Redis Streams wrapper.
- 8 event streams (`event_bus.py:21-30`): SPIDER_DATA,
  OPPORTUNITY_CREATED, OPPORTUNITY_SCORED, VALIDATION_REQUIRED,
  VALIDATION_DECIDED, OUTCOME_RECORDED, MODEL_TRAINED, SYSTEM_ALERT.
- 1 dead-letter stream: `mi:dead_letter`.
- Consumer groups: `scoring_workers`, `validation_workers`,
  `analytics_workers`.

**Major classes.**
- `Event` (`event_bus.py:42`) — timestamp, priority (LOW/NORMAL/HIGH/
  CRITICAL), source, correlation_id.
- `ConsumerInfo` (`event_bus.py:81`) — name, group, handler callback,
  subscribed streams.

**Existing documentation.** None dedicated. Referenced in
`docs/EVENT_SYSTEM_INVENTORY.md` but distinct from CeleryTaskEvent
etc.

**Separation of concerns from Observability (§3.25) — critical
distinction, per Rigby S1273 review.** The two domains look
duplicative but are architecturally distinct:

- **Event Bus / Streams (§3.31, THIS domain)** — a live message-passing
  substrate. Publishers send events to Redis Streams; consumer groups
  pick them up asynchronously; DLQ catches unhandled. This is
  **runtime coordination** — the point is that consumer B reacts to
  producer A's action *at execution time*.
- **Observability / Telemetry (§3.25)** — a passive event capture
  layer. `CeleryTaskEvent`, `LLMCallEvent`, `OpsRunEvent`, etc. are
  audit rows written *after the fact*. Readers are dashboards,
  investigations, PA tools like `celery_task_history`. This is
  **evidence-after-the-fact**, not runtime coordination.

The two overlap semantically (both emit "events") but not
functionally. Event Bus is push-with-consumers. Telemetry is
write-and-query. If a future design needs both — a runtime reaction
AND an audit trail — it will write to Event Bus for the reaction
AND to the appropriate telemetry table for the audit. Keeping them
separate here is intentional; do not merge in future refactors
without a research doc reviewing whether the substrates should
actually converge.

**Research coverage.** LIGHT.

**Architecture maturity.** EXPERIMENTAL. Schema defined; consumer
group infra in place; **no documentation of which services actually
publish/consume**.

**Known drift.** Producer/consumer registry absent.

**Known technical debt.**
- Producer/consumer map missing — reuse decisions blocked without it.
- Some semantic surface overlap with WebSocket consumer message
  types (both broadcast realtime state); relationship undocumented.

### 3.32 Revenue / Outreach / Engagement Pipeline

*Added S1273 v2 per Rigby SIGN-with-edits review. Original 6-agent
sweep did not surface this as a distinct domain; Rigby caught the
gap.*

**Purpose.** Convert spider-sourced opportunities into revenue through
a discovery → outreach → engagement → meeting → close → attribution
lifecycle. Dedicated models + services + agents; touches Spider,
Signal, Content, Human Interface, and Observability domains.

**Canonical entry points.**
- Orchestrator:
  `core/services/opportunity_pipeline_orchestrator.py`.
- Ops Autopilot layer: `core/services/ops_autopilot/revenue.py`,
  `.../outreach_generation.py`, `.../engagement.py`,
  `.../impact.py`.
- Agents: `core/agents/analysis/opportunity_scoring_agent.py`,
  `core/agents/opportunity_pipeline_agent.py`,
  `core/agents/executive/meeting_coordinator_agent.py`.
- Intelligence bridges: `intelligence/spider_decision_bridge.py`,
  `intelligence/revenue_integration.py`.
- ML: `ml_pipeline/opportunity_categorizer.py`.

**Major models.**
- `OutreachDraft` (`core/models_outreach.py:18`) — outreach content
  drafted from opportunity data; sender / recipient / channel;
  drafted / sent / engaged status transitions.
- `EngagementEvent` (`core/models_engagement.py:18`) — inbound signal
  (email reply, meeting accept, LinkedIn interaction) tied back to
  the OutreachDraft or opportunity source.
- `Meeting` (`core/models_meeting.py:18`) — scheduled meeting;
  participants, time, agenda, outcome linkage.
- `ClosePack` (`core/models_close_pack.py:20`) — bundle of artifacts
  assembled at close (proposal, contract, invoicing hooks, revenue
  attribution).
- Opportunity records surface in `core/models_unified_system.py` +
  `persistence/models.py` (details **UNKNOWN** without deeper
  sweep — flag for §10.3).

**Major services.**
- `opportunity_pipeline_orchestrator.py` — top-level orchestration.
- `ops_autopilot/revenue.py` — revenue attribution + tracking.
- `ops_autopilot/outreach_generation.py` — LLM-driven outreach draft
  composition.
- `ops_autopilot/engagement.py` — engagement event ingestion.
- `ops_autopilot/impact.py` — impact scoring (surfaces `ImpactEvent`
  per §3.25).

**Major APIs.**
- REST endpoints: **UNKNOWN** exact paths — grep hits
  `core/urls.py`, `core/views_analytics.py`; needs dedicated sub-
  agent sweep to enumerate.
- PA tools: **UNKNOWN** whether outreach/opportunity have dedicated
  PA tools; `td_handlers_agents.py` and `td_handlers_ops.py` both
  reference outreach — mapping needs verification.
- Celery tasks in `core/celery.py` + `intelligence/tasks.py`.

**Major runtime flows.** See §4.9 for the cross-domain flow.

**Existing documentation.**
- `docs/architecture/partnership_model.md`.
- `docs/plans/MASTER_PLAN_CREATIVE_INTELLIGENCE_EMPIRE.md`
  (aspirational-heavy — treat as design context, not runtime).
- `docs/archive/handoffs-pre-800/SESSION_263_SUPER_PLATFORM_INTEGRATION_BLUEPRINT.md`.
- `docs/reports/DECISION_COMMAND_IMPLEMENTATION_REPORT.md`.
- `external-project-docs/ai-content-studio/architecture/BILLING_MONETIZATION_SYSTEM.md`
  (external companion project — verify current relevance).
- **No CANONICAL topic doc** for this pipeline.

**Research coverage.** LIGHT. Models + services + agents all exist
and are referenced in tests (`test_outreach_generation.py`,
`test_opportunity_task.py`, `test_phase_b_receipt_only_adopters.py`),
but no consolidated architectural narrative. Rigby flagged this as
the biggest missing domain in the S1273 review.

**Architecture maturity.** WORKING. Enough infrastructure exists that
tests reference the flow end-to-end; unclear whether the pipeline is
actively driving revenue in prod or is scaffolding awaiting
activation. Needs dedicated research mission (see §9 recommendation
#3 — bump proposed).

**Known drift.**
- Multiple aspirational docs (`MASTER_PLAN_CREATIVE_INTELLIGENCE_EMPIRE.md`,
  `BILLING_MONETIZATION_SYSTEM.md`) may overstate current state;
  need runtime verification.
- Revenue attribution logic in `ops_autopilot/revenue.py` — surface
  status **UNKNOWN**.

**Known technical debt.**
- No canonical domain doc.
- Overlap between Ops Autopilot layer (`ops_autopilot/revenue.py`,
  `.../outreach_generation.py`, `.../engagement.py`) and standalone
  services / agents needs de-duplication audit.
- Whether opportunity → Initiative → Deliverable is wired (§3.12
  Q for AutoTopic → Initiative auto-creation applies here too).
- ML pipeline (`ml_pipeline/opportunity_categorizer.py`) integration
  path — unclear whether trained model is served.

---

## 4. Cross-Domain Flows

Six flows traverse ≥2 domains. Sourced from S1268 substrate-audit §3,
collaboration-patterns §3, and the 6 S1273 sweeps.

### 4.1 Spider → Signal → Agent → Deliverable

```
LegacySpiderData
  → (LearningBridge + backfill_spider_embeddings, pgvector)
  → SignalAggregationService.aggregate_signals()
  → SignalCluster (10 pattern types, entity_token_v1 clusterer)
  → SignalCuratorService → AutoTopic
  → HiveMindSession (deliberation record)
  → ContentDeliberationRunner.run_blog(topic, voice)
    → ClaimsPack (deterministic C- ids from URL+title)
    → ContentWriterAgent (evidence-first draft w/ [C-xxx] cites)
    → 3-reviewer panel → DecisionEnforcer → PublishGate
  → SelfBlog + Deliverable (pgvector embeddable)
```

Domains: Spider (8), Signal (9), Content Pipeline (11), Initiative
(12), Memory/Knowledge (13).

### 4.2 Human → PA → Tool → Celery → Result → Chat

```
Human message → POST /api/pa/chat/ → dispatch process_pa_chat_task (pa queue)
  → UnifiedPAEntrypoint._build_context (5s timeouts × 8 enrichers)
  → GPT-5.2 function-calling loop (max 5 iterations)
    → tool call → ToolDispatcher.execute(tool_name, args)
      → tool handler (1 of 152) → possibly Celery async dispatch
      → ToolCallRecord written
    → LLM synthesis of tool results
  → PAResponse → poll GET /api/pa/chat/status/<task_id>/ (every 2s)
  → Chat UI renders content + tools_used + async_jobs
```

Domains: PA (1), AgentRouter (3), Automation/Celery (24),
Observability (25), API Layer (22), Frontend (18).

### 4.3 Employee → MissionRunner → OpsRun → Deliverable → Inbox

```
Beat schedule → run_<job> task → MissionRunner.run()
  → I1: OpsRun get_or_create(domain='mission', mission_run_kind)
  → preflight_fn → step[0..N] cascade (I5 skips remainder on fail)
  → postflight_fn (PostflightContext | passed, summary_dict)
  → verdict emit (I4: get_or_create dedupe)
  → I7: escalation dedupe on (failed_step, error_signature)
    → Deliverable(publish_intent='publish_candidate') or existing
  → shift_report_fn → post_shift_report → DirectMessage (thread dedup)
  → OpsRunEvent audit trail (authority_contract_observed warn-mode)
```

Domains: Employee OS (4), Automation/Celery (24), Content Pipeline
(11 — Deliverable), Inbox (17 — DirectMessage), Governance (23 —
authority observation).

### 4.4 Document Loader → Embeddings → Retrieval → PA

```
Author edits docs/*.md
  → build_docs_index → docs/_index.json + docs/INDEX.md
  → sync_docs_index_to_documents [--embed] → Document rows
  → embed_documents --all-unembedded → DocumentEmbedding chunks (HNSW)
    (parallel: build_rag_corpus → .rag/corpus.jsonl for local Ollama)
  → PA tool `search_docs` or `kb_tool` invoked
    → EmbeddingService.create_embedding(query)
    → rag_integration.search_embeddings (pgvector CosineDistance)
    → cosine ≥ 0.4, filters, importance_score → chunks
  → context injection into PA / agent prompt
```

Domains: Documentation Knowledge System (15), Memory/Embeddings (13),
RAG (14), PA (1), Traditional Agent (2 — user_docs_context injection),
Configuration (28 — management commands).

### 4.5 Scheduler → Celery → AgentExecution → Follow-up

```
django_celery_beat PeriodicTask (91 enabled + 5 disabled)
  → celery-beat (custom QueuePreservingScheduler)
  → routed by CELERY_TASK_ROUTES (8 queue types) → worker
  → task_prerun signal → CeleryTaskEvent(STARTED, RSS start, agent_name from kwargs)
  → task body → agent execution or spider or content pipeline
  → task_postrun signal → status=SUCCESS + duration + RSS delta
    → LLMCallEvent, OpsRunEvent, ToolCallRecord, AgentExecution (parallel telemetry)
  → AgentFollowupSubscription check → auto-enqueue next agent (if wired)
```

Domains: Automation/Celery (24), Observability (25), AgentRouter (3),
Traditional Agents (2), Configuration (28).

### 4.6 Governance → Tool Gate → Runtime Action (partial)

```
Operator: PA → governance_tool.set_mode(mode='freeze', scope='global', ttl=3600)
  → GovernanceState row (autonomy plane)
  → sync budget_freeze_active=true → SystemConfiguration (budget plane)
  → 4 active consumers gate:
    1. tasks_spiders.py:381-398 (spider tasks skip)
    2. signal_aggregation_service.py:207-227 (return empty)
    3. workspace_pipeline_runner.py:43-49 (cancel + error_message)
    4. llm_enforcer.py:200-260 (block non-critical LLM)
  → GAP: KillSwitch has no consumers
  → GAP: JobContract.authority observed via
         MissionRunner._emit_authority_contract_event but not enforced
```

Domains: Governance (23), PA (1 — tool surface), Spider (8), Signal
(9), Content Pipeline (11), LLM Provider Registry (7),
Employee OS (4 — authority observation).

### 4.7 Human → HumanAttentionItem → FeedbackProcessor → Learning

```
Agent creates HumanAttentionItem(urgency, ml_prediction, source_type)
  → Attention Queue on Command Center / Boardroom
  → User decision via POST /api/human/decisions/<id>/record/
  → HumanAttentionItem.record_decision(decision, feedback, confidence)
  → HumanInterfaceService writes HAI + HumanFeedbackRecord
  → post_save signal → FeedbackProcessor
    → classify positive/negative
    → create AgentLearning + LearningInsight (only round-trip w/ learning)
  → HumanPreference.update_learned_stats() — topic_weights modified LOCAL ONLY (NEVER SAVED, F5)
  → S746 verification loop: event completes → record_verification(outcome, profit)
```

Domains: HumanAttention (16), Frontend (18 — Boardroom + CommandCenter),
Memory/Knowledge (13 — AgentLearning), Governance (23 — human plane).

### 4.8 Sports → GamePredictor → MLPrediction → BettingOutcomeVerifier

```
TheOddsSpider.fetch_data() [40+ books × 60+ sports]
  → EventBus SPIDER_DATA stream (potential) OR direct model write
  → GamePredictor.execute() → LLM analysis of odds consensus
    → predicted_winner, home/away_win_prob, predicted_scores, confidence
  → MLPrediction row (SPORT_KEY_LEAGUE mapping; >14 day filter; Max(id) dedup)
  → TheOddsSpider.fetch_scores() (completed + live)
  → BettingOutcomeVerifier.settle_wagers()
    → PlacedWager status transition (pending → won/lost/push)
  → SharpActionDetector.detect_signals() (odds divergence)
```

Domains: Sports/DBAO (10), Spider Framework (8), Traditional Agents
(2), LLM Provider (7). **Missing bridge to Signal (9) + Content
Pipeline (11)** — see §5.

### 4.9 Spider → Opportunity → Outreach → Engagement → Meeting → ClosePack → Revenue

*Added S1273 v2 per Rigby SIGN-with-edits review.*

```
Spider (e.g., prospecting spider, tech-signal spider)
  → LegacySpiderData
  → intelligence/spider_decision_bridge.py
  → OpportunityScoringAgent (ml_pipeline/opportunity_categorizer.py assist)
  → Opportunity record (models_unified_system.py or persistence/models.py — UNKNOWN)
  → opportunity_pipeline_orchestrator.py
  → ops_autopilot/outreach_generation.py (LLM-driven draft)
  → OutreachDraft row (models_outreach.py:18)
  → (send via external channel; UNKNOWN which service; likely
     partner integrations under integrations/)
  → EngagementEvent (models_engagement.py:18) inbound
  → MeetingCoordinatorAgent → Meeting (models_meeting.py:18)
  → ClosePack (models_close_pack.py:20) assembled at conversion
  → ops_autopilot/revenue.py records revenue attribution
  → ImpactEvent (§3.25 telemetry surface)
```

Domains: Spider Framework (8), Signal Engine (9 — potentially),
Traditional Agents (2), Content Pipeline (11 — via
outreach_generation LLM path), Revenue Pipeline (32),
Inbox/Messaging (17 — for outbound channel), HumanAttention (16 —
for meeting scheduling escalation), Observability (25 — ImpactEvent).

**Load-bearing UNKNOWNs (flagged for §10.3):**
- Opportunity model exact location + schema.
- Outbound channel service (email? LinkedIn API? something else?).
- Whether close-pack conversion runs as an auto pipeline or requires
  human approval via `HumanAttentionItem`.
- Whether opportunity → Initiative auto-creation exists (relates to
  §3.12 open question about AutoTopic → Initiative wiring).

---

## 5. Duplicate / Overlapping Systems

Inventory only. No fixes proposed.

### 5.1 Multiple Orchestration Paths

Two **orthogonal durable orchestration paths** (per S1268
collaboration-patterns §3, Path E "orchestration reading path"):

- **Celery chain / group:** `ai_core/agents/hybrid_executor.py:244,351`.
- **MissionRunner step loop:** `core/employees/mission_runner.py`
  (S1258 close).

Plus:
- `WorkflowOrchestrationAgent` `ThreadPoolExecutor` fan-out variant
  (`core/agents/workflow_orchestration_agent.py:47,302`).

They do NOT compose today. Choose one based on durability needs; do
NOT mix (per S1268 audit recommendation).

### 5.2 Multiple Messaging / Notification Systems

- **Web Push** (`PushSubscription` + `NotificationPreference` +
  `PushNotificationService`, RFC 8030 + VAPID).
- **Mobile push** (`MobilePushToken` + `expo_push.py`).
- **Discord notifications** (`discord_notifications.py`).
- **In-app inbox** (`MessageThread` + `DirectMessage`).
- **HumanAttentionItem** (in-app decision queue, not strictly
  notification but attention-adjacent).

Three notification systems likely have different delivery guarantees,
rate-limiting, and state machines. No unified notification history.
Potential for same user to receive 3 copies of one alert.

### 5.3 Multiple Identity / Actor Concepts

Per S1271 actor-identity research: **19 actor identity concepts** and
**22 attribution surfaces** (13 Explicit / 2 Inferred / 4 Ambiguous /
1 Unreliable / 2 Missing). §1.7 F11 finding: a single "actor" label is
insufficient — enforcement-grade attribution requires at least
`executor_actor / sponsor_actor / principal_user` distinct roles.

### 5.4 Multiple Memory / Knowledge Stores

- `AgentKnowledgeSource` (cross-agent knowledge from spider data).
- `AgentMemory` (episodic — success/failure/feedback/technique).
- `UserAgentLearning` (per-user preference adaptation).
- `ConversationMemory` (user-agent conversation history w/
  pgvector).
- `MemoryPromotionService` auto-saved facts (writes to `AgentMemory`
  but with distinct scoring logic).
- **Two RAG lanes:** `core/rag_integration.py` (pgvector, prod) vs
  `core/rag.py` (keyword, local Ollama).

Rigby's memory is unified with agent knowledge (no separate PA-only
store per Agent 4 sweep) — but the split across 5+ tables is a
cognitive-load surface.

### 5.5 Multiple Governance Surfaces (S1269 Canonical)

Four planes exist and don't compose:

- **Autonomy plane:** `GovernanceState`, `KillSwitch` (write-only).
- **Authority plane:** `JobContract.authority` dict (observation-only).
- **Budget plane:** `SystemConfiguration.budget_freeze_active`
  (one-way sync from autonomy).
- **Human plane:** `HumanAttentionItem` + `HumanFeedbackRecord`
  (round-trip with learning; `HumanPreference` fields dead).

Enforcement blocked on symbol mapping prerequisite (S1270).

### 5.6 Multiple Content Pipelines

- **Content Deliberation Pipeline** (§3.11) — canonical, ships
  Deliverable + SelfBlog.
- **Initiative / Dream Pipeline** (§3.12) — 5-stage lifecycle,
  auto-progression.
- **Boardroom / Advisors flow** (§3.6) — decision consultation.

They intersect: `AutoTopic → HiveMindSession → Initiative →
Deliverable`. But whether an Initiative always produces a
Deliverable, or a Deliverable always requires an Initiative, is
**UNKNOWN** without deeper trace.

### 5.7 Multiple Task / Execution Logs (§3.25 core drift)

Five parallel execution telemetry layers:

1. `CeleryTaskEvent` — per-task (Celery signals).
2. `LLMCallEvent` — per-LLM-call (S1098 wrapper).
3. `AgentExecution` — per-agent-run (pruned by watchdog).
4. `ToolCallRecord` — per-tool-call (S861, S1115 dispatcher fix).
5. `OpsRunEvent` — per-step in mission/ops (S1250 PR3).

Plus adjacent audit/log tables (14+ per EVENT_SYSTEM_INVENTORY).

Whether necessary and non-overlapping or duplicate is the exact
question flagged by Agent 6.

### 5.8 Multiple Agent Dispatch Systems (S1029 finding)

Three independent agent dispatch systems:

- `run_*_agents()` (functions).
- `AGENT_WORKSPACE_REGISTRY`.
- `MetricsActionTrigger`.

Disabling one does NOT stop the others (S1029 audit — carried in
CELERY_AUDIT).

---

## 6. Architecture Maturity Matrix

| # | Domain | Coverage | Maturity | Operational Health | Drift Risk | Debt Risk | Recommended Next Research |
|---|--------|----------|----------|--------------------|-----------|-----------|---------------------------|
| 1 | PA (Rigby) | MODERATE | STABLE | GREEN | LOW | LOW | Enrichment gating logic doc |
| 2 | Traditional Agents | DEEP | STABLE | GREEN | LOW | MEDIUM | delegate_to_specialist depth-limit sketch |
| 3 | AgentRouter / Execution | MODERATE | WORKING | GREEN | MEDIUM | MEDIUM | Follow-up subscription observability audit |
| 4 | Employee OS + MissionRunner | CANONICAL | STABLE | GREEN | LOW | LOW | Continue library — Authority Enforcement Design Space (S1272 planned) |
| 5 | Claude Code Tooling | LIGHT | WORKING | GREEN | MEDIUM | MEDIUM | Design doc + receipts UX gap fix (memory: `project_employee_os_ux_gap_task_receipts.md`) |
| 6 | Boardroom / Advisors | LIGHT | EXPERIMENTAL | YELLOW | HIGH | HIGH | Persistence contract for advisor state + metrics |
| 7 | LLM Provider Registry | LIGHT | STABLE (core; failover missing) | GREEN | LOW | MEDIUM | Provider capability matrix + failover + USD cost materialization |
| 8 | Spider Framework | DEEP | STABLE | GREEN | LOW | LOW | 41→18 category consolidation study |
| 9 | Signal / Intelligence | MODERATE | WORKING | GREEN | MEDIUM | MEDIUM | Legacy cluster decay strategy |
| 10 | Sports / DBAO | LIGHT | WORKING | YELLOW | MEDIUM | HIGH | **Sports ↔ AI Studio integration sketch** |
| 11 | Content Pipeline | MODERATE | WORKING | GREEN | MEDIUM | MEDIUM | End-to-end test + evidence-first path audit |
| 12 | Initiative / Dream Pipeline | MODERATE | WORKING | YELLOW | MEDIUM | MEDIUM | AutoTopic → Initiative wiring verification |
| 13 | Memory / Knowledge / Embeddings | DEEP | STABLE | GREEN | LOW | MEDIUM | MemoryPromotionService scoring criteria doc |
| 14 | RAG / Document Loading | DEEP | WORKING | GREEN | LOW | LOW | Document backfill cadence + coverage dashboard |
| 15 | Documentation Knowledge System | CANONICAL | STABLE | GREEN | LOW | LOW | Coverage metric ("% of code paths documented") |
| 16 | HumanAttention | MODERATE | WORKING | YELLOW | MEDIUM | MEDIUM | Verification loop trigger point audit |
| 17 | Inbox / Notifications | MODERATE | WORKING | YELLOW | HIGH | HIGH | **Notification unification sketch** (3 systems) |
| 18 | Frontend / Workspace | DEEP | STABLE | GREEN | LOW | LOW | Bundle analysis + code splitting |
| 19 | Mobile | LIGHT | PARTIAL | UNKNOWN | UNKNOWN | UNKNOWN | Mobile scope determination (planned vs live) |
| 20 | Discord Bot | MODERATE | WORKING | GREEN | LOW | MEDIUM | 11,676-line file refactor plan (research only) |
| 21 | Voice / Avatar | LIGHT | PARTIAL | YELLOW | MEDIUM | MEDIUM | Avatar roadmap consolidation |
| 22 | API Layer | MODERATE | STABLE | GREEN | MEDIUM | MEDIUM | 1,857 endpoints — inventory-vs-frontend mapping |
| 23 | Governance / Authority | CANONICAL | PARTIAL | RED | HIGH | HIGH | **Authority Enforcement Design Space (S1272 planned)** |
| 24 | Automation / Celery | CANONICAL | STABLE | GREEN | LOW | HIGH (queue concentration) | Beat schedule rebalance study |
| 25 | Observability / Telemetry | DEEP | WORKING | YELLOW | MEDIUM | HIGH | **Observability deduplication audit** |
| 26 | External Integrations | LIGHT | STABLE | GREEN | LOW | MEDIUM | LLM cost tracking (USD materialization) |
| 27 | Auth / Permissions | LIGHT | PARTIAL | YELLOW | MEDIUM-HIGH | HIGH | Trust-boundary + threat-model doc + VIP demo API-layer enforcement plan |
| 28 | Configuration / Deployment | MODERATE | STABLE | GREEN | LOW | MEDIUM | Feature flag registry consolidation |
| 29 | Data Models / Persistence | LIGHT | STABLE | GREEN | LOW | MEDIUM | Data lifecycle policy centralization |
| 30 | Body Systems | MODERATE | WORKING | GREEN | LOW | MEDIUM | Autonomic-reflex activation study |
| 31 | Event Bus / Streams | LIGHT | EXPERIMENTAL | UNKNOWN | HIGH | HIGH | Producer/consumer map + relationship to CeleryTaskEvent |
| 32 | Revenue / Outreach / Engagement | LIGHT | WORKING | YELLOW | HIGH | HIGH | **Revenue pipeline canonical architecture doc** (models + services + agents + PA tools + outbound channel + attribution) |

Operational Health legend: GREEN = works in prod as documented;
YELLOW = works but gaps or drift; RED = known enforcement / correctness
gap; UNKNOWN = insufficient evidence.

---

## 7. Research Coverage Map

| Coverage | Domains |
|----------|---------|
| **CANONICAL** | Employee OS (§4), Documentation Knowledge System (§15), Automation/Celery (§24), Governance/Authority (§23) |
| **DEEP** | Traditional Agents (§2), Spider Framework (§8), Memory/Knowledge (§13), RAG (§14), Frontend (§18), Observability (§25) |
| **MODERATE** | PA (§1), AgentRouter (§3), Signal Engine (§9), Content Pipeline (§11), Initiative (§12), HumanAttention (§16), Inbox (§17), Discord (§20), API Layer (§22), Configuration (§28), Body Systems (§30) |
| **LIGHT** | Claude Code (§5), Boardroom/Advisors (§6), LLM Provider Registry (§7), Sports/DBAO (§10), Mobile (§19), Voice/Avatar (§21), External Integrations (§26), Auth (§27), Data Models (§29), Event Bus (§31), Revenue Pipeline (§32) |
| **NONE** | (none — every domain has at least code comments + one doc page) |

Governance/Authority is CANONICAL despite PARTIAL maturity because
the research library specifically covers it deeply (S1269 + S1270 +
S1271 all directly address).

Revenue Pipeline (§32, added S1273 v2 per Rigby review) is at LIGHT
despite being a full end-to-end platform subsystem — no canonical
topic doc, no research doc, aspirational docs scattered. Highest
research priority alongside Authority Enforcement.

---

## 8. Known Drift and Technical Debt (High-Confidence Items)

Grouped by domain. Do not fix; just inventory.

### High-priority drift

- **§3.23 F1:** `JobContract.authority` observation-only (zero
  enforcement readers).
- **§3.23 F2:** `KillSwitch` 6 target_detail fields never read at
  dispatch.
- **§3.23 F5:** `HumanPreference.topic_weights /
  source_weights` never populated.
- **§3.23 F7:** GovernanceState throttle + per-scope modes have zero
  consumers.
- **§3.25 event-to-action gap:** DeliverableEvent rows written; Rigby
  intake deferred (`RIGBY_EVENT_INTAKE_ENABLED=False`).
- **§3.24 queue concentration:** 55 of 77 beat entries on `default`
  queue; single-worker-drop = half the platform stops.
- **§3.10 sports pipeline break:** sports_odds not a valid
  SignalCluster data_type; sports predictions do NOT auto-create
  Initiatives; betting outcomes NOT fed to deliberation.
- **§3.17 notifications:** 3 parallel notification systems (Web Push,
  Expo, Discord) with different state machines; no unified audit.
- **§3.25 observability:** 5 parallel execution telemetry layers; no
  dedup audit.
- **§3.13 F consumer gap:** `spider_context['pa_content_feedback']`
  populated but ContentWriterAgent read is **UNKNOWN**.
- **§3.31 event bus:** producer/consumer map absent for 8 streams +
  DLQ.
- **§3.32 revenue pipeline docs drift:** aspirational docs
  (`MASTER_PLAN_CREATIVE_INTELLIGENCE_EMPIRE.md`, external
  `BILLING_MONETIZATION_SYSTEM.md`) may not reflect runtime state;
  no canonical topic doc for the pipeline.
- **§3.27 Auth VIP demo prompt-only:** persistent from initial
  ship; PA can ignore the "read-only" injection.
- **§3.27 Fleet permissive fallback:** design intent unclear —
  intentional grace period or debt?

### High-confidence technical debt

- **§3.6 advisor state:** in-memory only; satisfaction_rating +
  total_consultations + success_rate not persisted; lost on restart.
- **§3.21 HeyGen F2F.1:** stub only; F2F.3 planned but not shipped.
- **§3.7 LLM provider failover:** health_check exists; no
  auto-failover on repeated failures; no circuit-breaker.
- **§3.2 delegate_to_specialist:** no depth limit / cycle detection;
  theoretical infinite loop.
- **§3.13 AgentLearningService Redis:** unbounded growth; no
  expiration policy.
- **§3.20 discord_bot.py:** 11,676 lines single file, 25 Cog
  classes.
- **§3.28 core/settings.py:** ~2,000 lines; no TOC.
- **§3.24 orphan tasks:** 10 orphan Celery tasks
  (`debug_task`, `rag_retrieval_canary`, `assign_open_findings_to_agents`,
  `check_blocked_research_for_unblock`, `discover_and_import_audits`,
  `maintain_knowledge_freshness`, `post_ops_digest`,
  `run_ops_autopilot`, `send_weekly_kpi_summary`,
  `process_pending_action_plans`) — mostly intentional per
  AUDIT_FINDINGS §12.

### Load-bearing UNKNOWNs

- BaseAgent line count: 5,575 (Agent 2) vs 5,962 (PLATFORM_INVENTORY).
- Backfill batch size: 500 vs 50 (Agent 3 vs Agent 4).
- Document chunk coverage: 852/14,149 (S1142) — current unknown.
- Mobile app: whether actively used or planned-only.
- Automation → Initiative auto-creation flow (S1268 §10 Q2).
- **§3.32 Opportunity model location + schema.** Grep hits
  `core/models_unified_system.py` + `persistence/models.py`; needs
  dedicated sweep.
- **§3.32 outbound channel service.** Email? LinkedIn API?
  Something else? Untraced.
- **§3.32 close-pack conversion trigger.** Auto pipeline vs human
  approval via HumanAttentionItem — unknown.

---

## 9. Recommended Research Roadmap

Next 11 research missions (roadmap expanded from 10 to 11 in S1273 v2
per Rigby review — Revenue Pipeline elevated as #2), ranked by
architectural uncertainty reduced × risk reduced × reuse unlocked ×
decisions unblocked.

### 9.1 Employee OS continuation (S1272 already staged)

1. **Authority Enforcement Design Space** — CANONICAL follow-on to
   S1270 (Symbol Mapping) + S1271 (Actor Identity). Composes the
   WHAT + WHO into the ENFORCEMENT design space. Already named as
   §1.7 recommended next research mission and STAGE 2 in
   `ARCHITECTURE_INDEX.md` §9 roadmap. Unblocks: authority
   enforcement runtime shift from warn-mode to enforce-mode.

### 9.2 Platform-wide research (new)

2. **Revenue / Outreach / Engagement Pipeline canonical architecture
   doc** *(elevated per Rigby S1273 review — was missing entirely
   from the S1273 v1 draft)*. Enumerate models
   (OutreachDraft/EngagementEvent/Meeting/ClosePack/opportunity
   records), services (`opportunity_pipeline_orchestrator`,
   `ops_autopilot/revenue|outreach_generation|engagement|impact`),
   agents (OpportunityScoringAgent, OpportunityPipelineAgent,
   MeetingCoordinatorAgent), PA tools, outbound channel integration,
   revenue-attribution logic. Verify runtime state vs aspirational
   docs (`MASTER_PLAN_CREATIVE_INTELLIGENCE_EMPIRE.md`, external
   `BILLING_MONETIZATION_SYSTEM.md`). Unblocks: revenue-related
   feature work + resolves the domain's LIGHT coverage.

3. **Observability Deduplication Audit** — Trace a single "agent
   executes a tool that calls the LLM" scenario through all 5
   execution telemetry layers (CeleryTaskEvent, LLMCallEvent,
   AgentExecution, ToolCallRecord, OpsRunEvent) + adjacent audit
   tables. Recommend rationalization. Unblocks: telemetry design
   for future features.

4. **Sports/DBAO ↔ AI Studio Integration Sketch** — Whether and how
   MLPrediction / PlacedWager / SharpAction outcomes should feed
   Signal / Initiative / Deliverable surfaces. Alternative: document
   intentional island. Unblocks: content-pipeline decisions for
   sports content, betting-related deliberation.

5. **Notification Surface Unification Study** — 3 parallel systems
   (Web Push, Expo, Discord) + in-app Inbox + HumanAttentionItem.
   Trace one signal event through each. Recommend unified audit /
   rate-limit strategy. Unblocks: notification-related feature work.

6. **Event Bus Producer/Consumer Map** — Enumerate every publisher
   and subscriber for the 8 Redis Streams + DLQ. Relate to
   CeleryTaskEvent + WebSocket consumers. Recommend: keep, deprecate,
   or unify. Unblocks: any new event-driven feature.

7. **Rigby v0 Event Intake Activation Plan** — Design DeliverableEvent
   → Rigby decision → platform learning feedback loop.
   `RIGBY_EVENT_INTAKE_ENABLED=False` today. Model schema,
   escalation rules (normal/high/critical), decision API, telemetry
   capture. Unblocks: observability → action closure (currently 14+
   event models emit into a void).

8. **Advisor Persistence Contract** — Advisor state (satisfaction_
   rating, total_consultations, success_rate) is in-memory; lost on
   restart. Research: what should persist, what should recompute
   from scratch, what needs versioning. Unblocks: any advisor-metrics
   feature.

9. **Content ↔ Initiative Wiring Audit** — S1268 §10 Q2 flagged
   AutoTopic → Initiative auto-creation as UNCERTAIN. Trace every
   Initiative creation path; document whether AutoTopic is source-
   of-truth or dead-end. Unblocks: dream/initiative workflow
   decisions.

10. **LLM Provider Failover + Cost Tracking Sketch** — 6 providers
    registered; health_check exists; no auto-failover; `cost_usd`
    absent. Research: provider capability matrix (tool support per
    provider), circuit-breaker pattern, cost aggregation to
    LLMCallEvent. Unblocks: cost governance + reliability.

11. **Claude Code Tooling Design Doc** — Production code, no
    architectural doc, receipts-gap UX bug (memory
    `project_employee_os_ux_gap_task_receipts.md`). Research: how
    the 3-way agent should coordinate with Rigby, how tools should
    dispatch through the platform vs directly, how receipts should
    surface. Unblocks: multi-Claude-Code coordination (the exact
    situation encountered mid-S1273 with `pa-cbcc410b32714f60`
    context-crossing risk).

### Ordering rationale

- **1** is already staged (S1270+S1271 prereqs shipped).
- **2** was surfaced by Rigby's S1273 review — biggest single
  missing platform subsystem; LIGHT coverage on a full
  end-to-end domain is the highest-yield gap.
- **3** touches every future observability feature.
- **4** resolves one of the platform's structural questions
  ("what IS the Sports side to AI Studio?").
- **5** unblocks all notification-related features (Web Push,
  Expo, Discord).
- **6–11** are prioritized by risk × reuse.

---

## 10. Appendix

### 10.1 Files inspected (partial)

Per S1273 parallel sweep. Full evidence trail in sub-agent
transcripts.

- `CLAUDE.md`, `00-START-NEXT-SESSION.md`.
- `docs/PLATFORM_INVENTORY.md` (§Executive Summary, §Agents,
  §Spiders, §Celery Tasks, §Body Systems, §LLM Providers, §Signal
  Pattern Types).
- `docs/PLATFORM_WHAT_IT_IS.md`.
- `docs/research/ARCHITECTURE_INDEX.md` (v3).
- `docs/research/employee_os_communication_substrate_audit.md`.
- `docs/research/employee_os_communication_protocol_sketch.md`.
- `docs/research/employee_os_collaboration_patterns.md`.
- `docs/research/governance_authority_evolution.md`.
- `docs/research/symbol_mapping_architecture.md`.
- `docs/research/actor_identity_attribution_architecture.md`.
- `docs/EMPLOYEE_OS_PRIMITIVES.md`.
- `docs/KNOWLEDGE_PIPELINE.md`.
- `docs/EVENT_SYSTEM_INVENTORY.md`.
- `docs/AUDIT_FINDINGS.md` §12-14.
- `docs/topics/personal-assistant.md`, `.../agent-system.md`,
  `.../employee-os.md`, `.../content-pipeline.md`,
  `.../initiative-pipeline.md`, `.../celery-workers.md`,
  `.../body-systems.md`, `.../spider-network.md`,
  `.../stock-intelligence.md`, `.../frontend.md`,
  `.../infrastructure.md`, `.../local-askdocs.md`.
- `docs/narratives/KNOWLEDGE_RAG_MEMORY.md`,
  `.../FRONTEND.md`.
- `docs/handoffs/SESSION_1258_..._MORNING_BRIEF_BEAT_MIGRATION.md`,
  `SESSION_1264_AUTHORITY_WARN_MODE.md`,
  `SESSION_1267_EMPLOYEE_4_BUG_TRIAGE_SHIP.md`,
  `SESSION_1269_ARCHITECTURAL_RESEARCH_LIBRARY_ARC.md`.
- Source files (with cited line ranges throughout §3):
  `core/services/unified_pa_entrypoint.py`,
  `core/services/tool_dispatcher.py`,
  `core/services/pa_tool_schemas.py`,
  `core/services/llm_provider_registry.py`,
  `core/services/agent_learning_service.py`,
  `core/services/embedding_service.py`,
  `core/services/memory_promotion_service.py`,
  `core/services/feedback_loop_engine.py`,
  `core/services/signal_aggregation_service.py`,
  `core/services/content_deliberation_runner.py`,
  `core/services/content_scoring_service.py`,
  `core/services/betting_outcome_verifier.py`,
  `core/services/body_vitals.py`,
  `core/services/body_coordinator.py`,
  `core/services/event_bus.py`,
  `core/services/ops_autopilot/governance.py`,
  `core/services/human_attention_lifecycle.py`,
  `core/services/human_interface_service.py`,
  `core/services/celery_health.py`,
  `core/services/llm_call_wrapper.py`,
  `core/services/openai_client_factory.py`,
  `core/services/anthropic_client_factory.py`,
  `core/services/push_notification_service.py`,
  `core/services/expo_push.py`,
  `core/services/discord_notifications.py`,
  `core/services/discord_bot.py`,
  `core/services/claude_code_agent.py`,
  `core/services/claude_code_engineer.py`,
  `core/services/advisor_context_builder.py`,
  `core/services/execution_tracker.py`,
  `core/services/rag_observability_service.py`,
  `core/services/scoped_retrieval.py`,
  `core/services/orchestration_approval.py`,
  `core/services/fleet_auth_drf.py`,
  `core/services/spider_intelligence.py`,
  `core/services/spider_deduplication.py`,
  `core/agent_router.py`,
  `core/agents/base_agent.py`,
  `core/agents/markets/game_predictor.py`,
  `core/agents/content_writer_agent.py`,
  `core/employees/jobs.py`,
  `core/employees/mission_runner.py`,
  `core/employees/mission_verdict.py`,
  `core/employees/comms.py`,
  `core/employees/comms_docs_manager.py`,
  `core/agent_execution_wrapper.py`,
  `core/celery.py`, `core/celery_telemetry.py`,
  `core/settings.py`, `core/urls.py`, `core/routing.py`,
  `core/asgi.py`, `core/auth_middleware.py`,
  `core/vip_middleware.py`,
  `core/llm_enforcer.py`,
  `core/schedulers.py`,
  `core/models_governance.py`,
  `core/models_human_interface.py`,
  `core/models_signal_intelligence.py`,
  `core/models_ops_runs.py`,
  `core/models_llm_telemetry.py`,
  `core/models_celery_telemetry.py`,
  `core/models_messaging.py`,
  `core/models_push_notifications.py`,
  `core/models_mobile.py`,
  `core/models_betting.py`,
  `core/models_odds_history.py`,
  `core/models_heart.py`,
  `core/models_tool_calls.py`,
  `core/models_content.py`,
  `core/models_orchestration.py`,
  `core/models_unified_system.py`,
  `core/models_assistant_profile.py`,
  `core/models_feedback_processing.py`,
  `core/models_voice_marketplace.py`,
  `core/models/conversations/models.py`,
  `content/models.py`,
  `sports/models.py`,
  `advisors/registry.py`,
  `advisors/llm_advisor_system.py`,
  `intelligence/models/agent_execution.py`,
  `ai_core/spiders/spider_registry.py`,
  `ai_core/spiders/specialized/theodds_spider.py`,
  `ai_core/spiders/specialized/combat_sports_spider.py`,
  `ai_core/spiders/realtime_publisher.py`,
  `ai_core/spiders/base_spider.py`,
  `ai_core/spiders/real_data_collector.py`,
  `ai_core/agents/hybrid_executor.py`,
  `core/rag_integration.py`, `core/rag.py`,
  `frontend/src/App.tsx`,
  `frontend/src/pages/CommandCenterPage.tsx`,
  `frontend/src/pages/WorkspacePageNew.tsx`,
  `frontend/src/pages/BettingPage.tsx`,
  `frontend/src/pages/InboxPage.tsx`,
  `frontend/src/pages/StockIntelligencePage.tsx`,
  `frontend/src/pages/AdvisorsPage.tsx`,
  `frontend/src/pages/workspace/tabs/BoardroomTab.tsx`,
  `frontend/src/pages/workspace/tabs/OrchestrationTab.tsx`,
  `frontend/src/hooks/usePageTracking.ts`,
  `Procfile`, `Makefile`, `docker-compose.yml`, `.env.example`,
  `tools/pa_chat.py`, `tools/pa_local.sh`.

### 10.2 Commands / probes used

- `context-kit orient`.
- `Grep` and `Glob` across `core/`, `frontend/`, `ai_core/`,
  `intelligence/`, `sports/`, `advisors/`, `content/`, `docs/`.
- `Read` on cited file:line ranges.
- No ORM probes were run this session (research-only per mission
  spec).

### 10.3 Unresolved unknowns

- Backfill batch size discrepancy (500 vs 50).
- BaseAgent line count discrepancy (5,575 vs 5,962).
- Mobile app activation status.
- Document chunk coverage current value.
- `ContentWriterAgent` `pa_content_feedback` consumer.
- HeartBeat surface consumer.
- Advisor exact count (25+ vs 30 in PLATFORM_INVENTORY).
- PA polling backoff strategy.
- `_broadcast_thread_update()` WebSocket consumer.
- `check_auto_approvals()` call site (Q1 from S1269).
- Autonomous → Initiative auto-creation task (S1268 §10 Q2).

### 10.4 Conflicts between sources

- PLATFORM_INVENTORY vs earlier snapshots: PA tool schemas (113 vs
  104), Agent table row count (90 vs 87), etc. Per DOC_LIFECYCLE
  §2c: inventory wins on conflict; every count in §2/§3 should
  match the autoblock in `CLAUDE.md`.
- Agent 3 vs Agent 4: embedding backfill batch size — resolved as
  UNKNOWN, flagged in §10.3.
- Agent 2 vs PLATFORM_INVENTORY: BaseAgent line count — resolved
  as UNKNOWN, flagged in §10.3.

### 10.5 Verifier-loop corrections

**S1273 v2 (2026-06-30) — Rigby SIGN-with-edits folded.** Fresh pin
`pa-02cfd3206302352f` (not the shared S1270+ arc pin, per
context-isolation guardrail — Chris flagged another Claude Code was
on `pa-cbcc410b32714f60`). Rigby's structured verdict:

- **Overall confidence:** Medium.
- **Most accurate part:** Governance/Authority + Observability
  sections, and the "write paths exist but readers/enforcement are
  missing" framing (KillSwitch, authority warn-mode, multi-layer
  telemetry).
- **Weakest part:** External Integrations + Auth/Permissions/Security
  too compressed relative to blast radius; read like inventories,
  not architectural contracts (threat model, enforcement points,
  trust boundaries).
- **Missing domain:** Revenue / Outreach / Engagement Pipeline
  (Opportunity → OutreachDraft → EngagementEvent → Meeting →
  ClosePack → RevenueTracker). Folded as §3.32 + §4.9.
- **Overstated maturity:** Auth / Permissions / Security STABLE →
  PARTIAL. Two called-out unsafe edges disqualify STABLE.
- **Understated maturity:** LLM Provider Registry WORKING → STABLE.
  Core registry abstraction is stable; failover / circuit-breaker /
  USD cost materialization are the peripheral gaps.
- **Biggest architectural risk:** Governance / Authority composition
  + enforcement. "Multiple control planes that *appear* to provide
  safety, several are write-only or observation-only" — dangerous
  false-sense-of-control failure mode during incidents / autonomy
  escalation.
- **Most important next research mission:** Authority Enforcement
  Design Space (STAGE 2). Ordering validated.
- **Verdict:** SIGN-with-edits.

**Folded edits (S1273 v2):**
1. Added §3.32 Revenue / Outreach / Engagement Pipeline (missing
   domain). Evidence verified via grep hits on OutreachDraft,
   EngagementEvent, ClosePack, Meeting model classes.
2. Added §4.9 Spider → Opportunity → Outreach → Engagement →
   Meeting → ClosePack → Revenue cross-domain flow.
3. Downgraded §3.27 Auth / Permissions / Security maturity STABLE
   → PARTIAL, added explicit trust-boundary enumeration.
4. Upgraded §3.7 LLM Provider Registry maturity WORKING → STABLE
   (core; failover missing) with explicit scope note.
5. Tightened §1 Executive Summary count phrasing away from raw
   numbers toward autoblock-consistent language + "regenerate via
   generate_platform_inventory" footnote.
6. Added §3.31 Event Bus vs Observability separation-of-concerns
   paragraph (Rigby noted canonical readers would otherwise assume
   redundancy).
7. Updated §2 Domain Map row 32 + re-rated rows 7 + 27.
8. Updated §6 Architecture Maturity Matrix rows 7, 27, 32.
9. Updated §7 Research Coverage Map to include §32; noted Revenue
   Pipeline as LIGHT-with-high-priority.
10. Expanded §9 roadmap from 10 → 11 missions; Revenue Pipeline
    canonical architecture doc elevated to #2 (Rigby's implicit
    priority).
11. Updated §8 drift + debt with §3.32 items + §3.27 explicit
    entries.
12. Extended §10.3 UNKNOWNs with §3.32 open questions.

**Not folded (accepted as-is):**
- Rigby's "Consider merging/renaming Event Bus vs Observability"
  suggestion — resolved instead via separation-of-concerns paragraph
  per her own alternative "keeping them separate is defensible" note.

---

**End of draft. Status: research / draft — Rigby SIGN-with-edits
review folded S1273 v2. Not committed unless Chris explicitly asks.**
