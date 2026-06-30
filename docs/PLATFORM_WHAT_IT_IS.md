---
title: "Donkey Betz Platform — What It Actually Is"
status: active
session: 1223
generated: 2026-05-24
last_reviewed: 2026-06-30
companion_doc: PLATFORM_INVENTORY.md
---

> **Anchor refresh — Session 1223 close (2026-06-23):** narrative body
> reviewed against handoffs SESSION_1142 → SESSION_1223 (81 sessions).
> Count drift in the existing body reconciled in this refresh (PA tools
> 101→109 schemas + 166→152 handlers; models 570→588; Celery tasks
> 365→409; PeriodicTasks 305→92 after the noise-task cleanup arc;
> frontend routes 60→61). No conceptual narrative changes — the platform
> shape is unchanged. New since Session 1141:
> - **1142-1160** — context-kit pattern formalized (`DOC_LIFECYCLE`, narrative anchors, runtime evidence), doc-claim verifier hardened, audit framework established
> - **1161-1183** — primitives + opt-in apply-list pattern for new infra (canonical locks, retry policies, factories), `make celery` PID-cache fix, multiple worker-restart triggers documented
> - **1184-1213** — PA tool maturity: conversation hygiene (`session_tool.create_fresh`), deliverable-tool large-payload pattern, agent fail-loud rules, fail-open helpers verified E2E
> - **1214-1216** — **OpenAI caller alignment arc** (3 single-day sessions, 16 PRs, ~30 call sites, spec deliverable `2b9aa447-…` `completed`). See "OpenAI hardening" subsection under Current State Honesty for the full close.
> - **1217-1222** — self-directed audit experiment (15-finding deliverable `bec077ed-…`), most-leverage picks shipped, both CI lints flipped to enforce mode (`check-llm-sdk.yml` + `check-reasoning-contract.yml`), 6-session continuous PA conversation thread
> - **1219-1221** — watchdog/timeout arc (Tier 1 total-request bound at `BaseAgent._call_openai` PR #2519, Tier 2 `LLMCallEvent` cleanup watchdog PR #2520) — closes the `httpx.Timeout(read=90s)` per-chunk loophole
> - **1223** — audit #8 close (seed baseline drift, PR #2534) — accepted 89 as canonical Agent table count; zero documented drift on agent counts for the first time since the audit framework existed
>
> Live runtime counts always come from `PLATFORM_INVENTORY.md`. All
> count updates in this refresh derived from the autoblock + verifier;
> any disagreement, the inventory wins.

> **Anchor refresh — Session 1141 close (2026-05-24):** narrative body
> reviewed against handoffs SESSION_1134 → SESSION_1141. No material
> drift in the subsystem narrative below. Session arc summary:
> - **1134** — capability specs anchored to Atlas (FLEET_CAPABILITY_MANIFEST + BUSINESS v3, β-scoped to Phase 1 reality)
> - **1135** — final close on per-app discovery + 54 open decisions
> - **1136** — context-kit ops view parked at Jessica user-test
> - **1137** — Jessica ratification of 22 strategic decisions across pricing/GTM/cost/legal axes + 4 deliverables (F1-F4) shipped
> - **1138** — F1 paid-interest demand-gate live (`FleetPaidInterest` + HMAC POST + `paid_interest_status` PA tool)
> - **1139** — entity-token clusterer behind `cluster_method` discriminator
> - **1140** — judge-stats endpoint + `signal_studio_judge_stats` PA tool + action-card pre-generation vertical slice (3 PRs); pgvector blocker closed via #2172
> - **1141** — Chris ratification of Jessica's 22 decisions (17 accept-as-written + 3 ratify-shipped + 2 clarifications back to Jessica); F5 PitchDeckForge style audit found Angel + Strategic don't map to existing code templates
>
> All session work extends existing subsystems — no platform-internal
> narrative changes below. Live runtime counts always come from
> `PLATFORM_INVENTORY.md`.

> **Anchor refresh — Session 1133 close (2026-05-23):** narrative body
> reviewed against handoffs SESSION_1099 → SESSION_1133. No material
> drift in the subsystem narrative. Session 1131-1133 arc added the
> signal-studio vertical slice (Phase 1 pull endpoint + Phase 2
> SignalCuratorAgent + 1132 (C) live SSE refresh + 1132 (B-scaffold)
> PA-chat warn-only audit + 1133 FLEET_* env back-prop to remaining
> 5 fleet repos) — extends the existing fleet-network plumbing, no
> change to platform-internal narrative below. Live runtime counts
> always come from `PLATFORM_INVENTORY.md`.

# Donkey Betz Platform — What It Actually Is

> **Read-order note:** this doc is the conceptual/narrative companion to
> [`PLATFORM_INVENTORY.md`](PLATFORM_INVENTORY.md). The inventory is
> runtime-derived and regenerable (via `python manage.py generate_platform_inventory`)
> — it tells you *what exists right now*. This doc tells you *what it all is,
> why it exists, and how it fits together*. Numbers cited here are accurate
> at time of writing (Session 1223 refresh, 2026-06-23); regenerate the
> inventory for a fresh snapshot.

---

## TL;DR — One Sentence

You've built an autonomous multi-agent intelligence platform that ingests real-time data from **80 spiders**, clusters it into signals, routes signals through **83 specialized AI agents** deliberating in multi-reviewer pipelines with full citation provenance, surfaces everything through a GPT-5.2-powered personal assistant (**Rigby**) with **109 tool schemas** and **8 enrichment services**, monitors itself via a **9-system "body" health metaphor**, and audits its own documentation against runtime reality.

**Scale:** ~919K lines of app Python (core/ + ai_core/). 588 database tables. 409 Celery tasks. One conversational interface to all of it.

---

## Table of Contents

1. [The Core Idea](#the-core-idea)
2. [The Layered Architecture](#the-layered-architecture)
3. [The Unique Stuff (The IP)](#the-unique-stuff-the-ip)
4. [Current State Honesty](#current-state-honesty)
5. [How to Navigate the Platform](#how-to-navigate-the-platform)
6. [Glossary](#glossary)

---

## The Core Idea

At its core, this is a **multi-agent autonomous intelligence platform** that combines six distinct capabilities:

1. **A real-time data gathering network** — 80 spiders
2. **A reasoning layer** — 83 code agents plus DB persona rows + 6 LLM providers
3. **A workflow pipeline** — initiatives, content deliberation, publishing
4. **A single conversational interface** — Rigby, the Personal Assistant
5. **A health-monitoring nervous system** — modeled on human anatomy
6. **A self-audit loop** — doc-vs-reality verifier + platform inventory

It's not one app. It's an ecosystem of coordinated subsystems that together turn raw internet/market data into validated content, decisions, stock briefs, sports bets, and code — with humans in the loop via a chat-first UX.

The platform can operate autonomously (scheduled Celery tasks continuously run spiders, cluster signals, spawn initiatives, generate content) or on-demand (the user asks Rigby anything and she routes to the right agent/subsystem).

---

## The Layered Architecture

### Layer 1 — Data Ingestion (Spiders)

**80 spiders across 41 categories** feed the platform's "sensory system":

| Category | Examples |
|---|---|
| News & Media | TechCrunch, The Verge, BBC, CNN, NPR, Axios, Reuters, Google News, NewsAPI |
| Financial & Crypto | CoinGecko, Yahoo Finance, Polygon.io, Finnhub, Etherscan, Kalshi, SEC EDGAR |
| Sports Betting | The Odds API (40+ bookmakers), ESPN |
| Tech & Dev | Hacker News, GitHub, Dev.to |
| Blockchain | Etherscan V2 |
| Plus many more | SEC filings, legislation, jobs, Kickstarter, Indiegogo... |

Each spider:
- Runs on a schedule via Celery (or on-demand via orchestrators)
- Writes rows into `SpiderData` (fields: `spider_name`, `source_url`, `data_type`, `raw_data`, `processed_data`, `embedding_text`)
- Deduplicates via `SpiderItemHash` (~1.14M hashes tracked; live counter, grows continuously)
- Gets embedded with OpenAI `text-embedding-3-small` and landed in pgvector

**Registry:** `ai_core/spiders/spider_registry.py`.

### Layer 2 — Signal Intelligence

Spider output feeds `SignalAggregationService` (`core/services/signal_aggregation_service.py`), which clusters signals by keyword/topic with a minimum cluster size of 3 items, and classifies clusters into **10 pattern types**:

`demand_spike`, `trend_emergence`, `sentiment_shift`, `opportunity_window`, `knowledge_gap`, `competitive_signal`, `market_movement`, `skill_demand`, `content_gap`, `user_need`

Clusters with enough strength/confidence/novelty trigger:

```
SignalCluster (pattern detected)
  → generate_auto_topics()
    → AutoTopic (with rationale)
      → trigger_signal_driven_conversation()
        → HiveMindSession (multi-agent debate)
          → Initiative (with full provenance chain)
```

**Every Initiative can be traced back through HiveMindSession → AutoTopic → SignalCluster → SpiderData rows.** "Why does this project exist?" has a database answer.

### Layer 3 — Agents

**83 agents in `AGENT_MAP`** (`core/agent_router.py`), with this live taxonomy:

| Status | Count | Meaning |
|---|---|---|
| Fully enabled | 73 | Tasks executed directly |
| Rerouted | 8 | Tasks redirected to specialists (CTO, COO, Workflow, Video, DevOps, FullStackDev, CodeReview, ContentDistribution) |
| Blocked | 2 | Tasks rejected (CodeGenerator, Audio) |

Agent categories (partial): Creation, Editing, Research, Content Writing, Strategy, Executive, Analysis, Training, Security, Business, Development, Blockchain, Legal, Narrative, Content Studio, Podcast, Rendering, Orchestration, Campaign, Stocks, Markets, Entry Point, Special, Decision, Content Review.

Every agent inherits from `BaseAgent` (`core/agents/base_agent.py`) which provides:

- **Workspace file-write ability** (SKIN layer) — 20 agents are explicitly `WORKSPACE_AWARE_AGENTS` and can write to user workspaces with audit trail
- **Learned-knowledge injection** at prompt time — semantic search of `AgentKnowledgeSource`, fallback to keyword match
- **Tool-call loop** — agents can invoke `delegate_to_specialist` (recursive routing), `web_search`, `spider_query`, and agent-specific tools
- **Post-execution outcome recording** — `AgentExecution` (status/tokens/cost), `AgentMemory` (safety-classified memories), `AgentLearning` (XP + pattern detection), `AgentKnowledgeSource` (shared knowledge)
- **Provenance tracking** — 29 agents explicitly wire `build_provenance()` into their output (data sources, timestamps, validation)

Below the code agents: DB persona rows via `DynamicPersonaAgent` fallback give you long-tail specialists. Plus **30 advisors** — functional domain specialists across investment strategy, AI/ML, content/creator economy, sports analytics, negotiation, healthcare, cybersecurity, education, operations, IP counsel, leadership coaching, regulatory compliance — accessible through `AdvisorContextBuilder`. All advisor identities are functional (no real-person names); see [`ADVISOR_AUDIT.md`](ADVISOR_AUDIT.md).

**Router entry point:** `AgentRouter.route(agent_name, task, context)` performs parallel context gathering (11 workers × 10s timeout each) before dispatching to the agent. See `core/agent_router.py:738-1264`.

### Layer 3.5 — Employee OS (MissionRunner)

**Employee OS is a primitive-reuse pattern, not a new subsystem.** It composes existing primitives — `AIEmployee` + `JobContract` (frozen dataclasses in `core/employees/jobs.py`), `MissionRunner` (orchestrator in `core/employees/mission_runner.py`), `OpsRun(domain='mission')` + `OpsRunEvent` (audit), `emit_mission_verdict()` (terminal verdict), `Deliverable(publish_intent='publish_candidate')` (escalation), `DirectMessage` (shift report), and `employee_tool` (PA read surface) — into deterministic, audit-trail-emitting AI workers.

As of Session 1258, **3 production employees** run through MissionRunner with full evidence trail:

| Employee | Job | Cadence | Verdict surface |
|---|---|---|---|
| Rigby (Documentation Manager) | `docs_manager` | Daily 06:30 MDT, Mon-Fri | `emit_mission_verdict()` → `verdict_issued:certified\|rejected\|deferred` |
| Platform Auditor | `platform_audit` | On-demand `employee_tool action=run_now` | same |
| Chief of Staff | `morning_brief` | Daily 07:00 MDT | same |

**MissionRunner owns lifecycle policy** (preflight → ordered steps → postflight → verdict emission → escalation with dedupe) but not domain logic — the job module's step functions supply that. Trust ratio is *derived on read* by `employee_tool action=status`; it is never persisted (no `TrustScore` model).

Adding a new employee means **registering a JobContract and writing a thin Celery facade**, not building new models, queues, admin UIs, or PA tools. The 14-row anti-duplication matrix in [`EMPLOYEE_OS_PRIMITIVES.md`](EMPLOYEE_OS_PRIMITIVES.md) §2 names every wrong instinct that has cost operator hours in prior sessions. **Read it before adding Employee #4.**

- **Canonical reference:** [`EMPLOYEE_OS_PRIMITIVES.md`](EMPLOYEE_OS_PRIMITIVES.md)
- **Orientation topic file:** [`topics/employee-os.md`](topics/employee-os.md)

### Layer 4 — Personal Assistant (Rigby)

The single conversational entry point. `UnifiedPAEntrypoint` in `core/services/unified_pa_entrypoint.py`.

**Inventory:**
- **109 tool schemas** visible to GPT-5.2 via OpenAI function calling
- **152 registered tool handlers** in `ToolDispatcher` (`core/services/tool_dispatcher.py`)
- **6 gateway tools** consolidated in Session 1079:
  - `governance_tool` (boardroom, attention items, decisions, triage)
  - `work_tool` (initiatives, stages, action items)
  - `content_tool` (review, blog gen, deliverables)
  - `intelligence_tool` (stocks, sports, legislation, RAG/KB, spiders)
  - `ops_tool` (SLO, failure signatures, migration)
  - `studio_tool` (media management)
- **8 enrichment services** inject context before LLM generation:
  | Service | Purpose |
  |---|---|
  | PAIntelligenceEnricher | work_tool, governance_tool, ops_tool, reasoning |
  | BlogPerformanceContextBuilder | content_tool |
  | DomainContentContextBuilder | 9 domains (finance, crypto, sports, betting, ai_tech, legal, career, health, education) |
  | SpiderContextBuilder | content/opportunities/predictions/intelligence |
  | AdvisorContextBuilder | 32 advisors (10 named + 22 domain) for opportunities + reasoning |
  | StrategicMemoryService | work_tool, governance_tool, reasoning |
  | ProactiveIntelligenceService | content, opportunities, intelligence, system_overview |
  | PlatformIntelligenceBriefingService | system_overview, execution_history |

**Runtime pattern (function calling):**

```
message → _build_context() [profile, knowledge, stats, docs — 5s timeouts each]
        → _build_messages_array() [system prompt + history + user msg]
        → GPT-5.2 Responses API with 101 tool schemas
           → if tool_call(s): execute via ToolDispatcher → feed result back → loop (max 5 iter)
           → if text response: done
        → enrichment (intent inferred from tool names)
        → return PAResponse
```

**Async backing:** Heavy tools dispatch to Celery and return `{task_id}` immediately. Celery `pa` queue has a dedicated worker (`celery-pa`) with 300s time limit so Railway's 30s proxy timeout doesn't cut requests.

**Memory:** DB-backed `ChatConversation` survives Celery worker recycling. `tool_calls` + `response_id` stored in metadata for multi-turn GPT-5.2 `previous_response_id` caching (90% cached input discount).

### Layer 5 — Workflow Pipelines

#### Content Pipeline

```
SpiderData (72h window) + SignalClusters (active)
  → ClaimsPack (deterministic C-xxxxxxxxxx IDs, max 20 claims)
    → ContentWriterAgent (draft with mandatory citations)
      → 3-Reviewer Panel
         • SkepticReviewer (always)
         • FactCheckReviewer (always)
         • DomainPersonaReviewer (conditional: domain confidence ≥ 0.2)
      → DecisionEnforcer (PUBLISH / REVISE / KILL)
        → Rewrite via EditorAgent (if REVISE)
          → PublishGate (quality/novelty/structure scoring)
            → SelfBlog (with stats_snapshot['deliberation'])
```

Every factual assertion in a published piece has a `C-xxxxxxxx` ID that traces back to a specific spider row with URL + timestamp. Citations are verifiable.

#### Initiative Pipeline (5 stages)

| Stage | Type | Purpose | Auto-Dispatch |
|---|---|---|---|
| 1 | research | External research, produces findings | no |
| 2 | planning | Architecture/prototype plan | no |
| 3 | evaluation | Go/no-go gate with criteria | no |
| 4 | specification | Technical detail + action items | yes |
| 5 | execution | Pilot execution + results | yes |

Two tracks:
- **Fast Track** (stages 1-2 only, stalls at approval) — default for quick experiments
- **Institutional Track** (full 5-stage) — triggered by `external_data`, `user_data`, `public_publishing`, `legal_compliance`, `financial`, `irreversible` flags

Circuit breaker: blocks new initiative creation when backlog ≥ 20 active+triage initiatives.

#### Deliberation Pipeline

`HiveMindSession` records a multi-agent debate: participants (stored as JSONField of dicts), conclusion, and full provenance back to originating signals.

### Layer 6 — Body Systems (The Nervous System)

**9 body systems** mirror human anatomy for health monitoring. Each has a service singleton, a health-check method, a status model, and a health-level enum.

| System | Method | Monitors |
|---|---|---|
| HEART | `pulse()` | All components, overall health |
| BRAIN | `think()` | LLM calls, active conversations, RAG queries, tokens |
| LUNGS | `breathe()` | Budget tracking, token consumption, cost forecasting |
| NERVOUS | `feel()` | WebSocket connections, Redis channel layer, message throughput |
| CIRCULATORY | `circulate()` | Redis queues, Celery queues, WebSocket channels |
| DIGESTIVE | `digest()` | Spider data ingestion (4 stages) |
| IMMUNE | `scan()` | Security threats, quarantined entities, rate limiting |
| MUSCULAR | `flex()` | Agent execution success rates by category |
| SKIN | `feel()` | Workspace file operations, rollbacks, agent activity |
| SPINE | `align()` | API routing, request throughput, per-route latency |

**BodyCoordinator** is an autonomic reflex layer — automatic cross-system responses to 27 event types:
- LUNGS exhausted → throttle LLM calls
- DIGESTIVE blocked → pause spider network
- MUSCULAR strained → scale down agents
- IMMUNE threat high → alert admins
- CIRCULATORY congested → clear caches

Overall health = weighted average (HEART 2×, SKIN 0.5×).

### Layer 7 — Execution Plumbing (Celery + Redis)

**Celery topology:**
- 409 user-defined Celery tasks (excludes `celery.*` internals)
- `core/celery.py` is the primary static source of beat definitions; `django-celery-beat` stores 92 runtime `PeriodicTask` rows (88 enabled, 4 disabled — down from 305 in Session 1099 after the Session 1142+ noise-task cleanup and Session 1222 B2 disabled-task classification arc)
- `sync_celery_schedules`, `sync_celery_beat`, `add_critical_celery_tasks`, `setup_workspace_autopilot`, and `sync_task_queues` bridge or repair those definitions into database-backed runtime state
- 11 Procfile entries: `release` + `web`, `celery-worker`, `celery-pa`, `celery-content`, `celery-long-running`, `celery-long-running-2`, `celery-broadcast`, `celery-beat`, `code-worker`, `resolve-node`
- Per-task RSS memory telemetry (`CeleryTaskEvent.rss_delta_mb` with `[MEMORY] SPIKE` log markers at 50/100 MB thresholds)
- Dedicated `pa` queue for Personal Assistant workloads (300s time limit)

**Redis DBs:**
| DB | Purpose |
|---|---|
| 0 | Channels (ASGI) |
| 1 | Cache |
| 2 | Broker |
| 3 | Results |

**Beat governor (Session 1089):** gates task dispatch by daily budget:
- Content pipeline: 8/day
- Intelligence desks: 15/day
- Revenue agents: 5/day

**Priority router (Session 1087):** `ActivePriority` model + router class + semaphores + 32 bypass migrations = observer-mode priority gating, rolling out gradually.

### Layer 8 — Monetization + Revenue

| Product | How it works |
|---|---|
| Stock Intelligence | Daily briefs, alerts, predictions, SEC filings, 7-tab dashboard at `/stocks` |
| Sports Betting | TheOdds spider + ESPN + MLPrediction → 9-tab betting dashboard at `/betting` with arbitrage calculator |
| Content Publishing | SelfBlog → claims-based deliberated content, 6-tier pricing ($5-$50K) |
| Podcast Studio | 4 agents (script writer, advocate, skeptic, producer) + TTS audio |
| Video Studio | RunwayML + DaVinci Resolve automation via `resolve-node` |
| Image Studio | DALL-E 3 / Flux / Stability, 80+ style presets |
| Legal Doc Drafter | Colorado family law docs, OCR + PDF support |
| AI Series Workflow | Multi-episode content series |
| Voice Marketplace | 14 API endpoints for voice clones |
| Stripe subscriptions | Free / Pro / Premium tiers |
| Gumroad integration | Pay-per-product |

### Layer 9 — Frontend (React + TypeScript + Vite + Tailwind)

**Routes** — 61 `<Route>` entries in `App.tsx`. Key routes:
- `/` — Command Center (home, PA chat)
- `/workspace` — 5-tab modular workspace (home, work, build, intelligence, system)
- `/stocks` — Stock Intelligence dashboard
- `/betting` — Betting Dashboard (9 tabs)
- `/image-studio`, `/video-studio`, `/documents`

**Command Center "Now" Hub** — 3-panel strip:
- Attention Queue — `HumanAttentionItem`s needing review
- Active Work — Currently running agent tasks
- System Pulse — Body system health

**Intelligence Desks Panel** (Session 1000) — 4-card grid:
- Stocks (green) | Sports (amber) | Blockchain (cyan) | Narrative (purple)

**PA Integration:**
- `GlobalPADock` — floating overlay, accessible from any page
- `CommandCenterPage` — full-width PA chat with conversation sidebar
- `AssistantPage` — dedicated PA page
- Telemetry via `usePageTracking()` → Redis counters

### Layer 10 — Discord Integration

- **96 `@*.command` decorators + 48 `@app_commands.command`** in `discord_bot.py` (11,676 lines)
- **25 Cog classes** grouping commands (Status, Agent, Spider, Interactive, Content, Voice, VoiceMarketplace, + 18 more)
- **12 notification channels** (agent dreams, spider summaries, market/blockchain alerts)
- Voice AI — TTS, STT, voice cloning, voice chat
- Mobile-friendly actions — `/bet`, `/apply`, `/digest`, `/consult`, `/create`
- 3 server templates + subscription tier management

### Layer 11 — Storage (PostgreSQL + pgvector)

**588 concrete Django models across 23 apps.** Key model families:

| Family | Key Models | Location |
|---|---|---|
| Agents | Agent, AgentExecution, AgentMemory, AgentLearning, AgentKnowledgeSource, AgentControlEntry, ToolCallRecord | `core.models_unified_system` |
| Content | SelfBlog, Deliverable, DeliverableAppend, ClaimsPack, DeliberationSession | `core.models_deliverables`, `core.models_unified_system`, `core.models_deliberation` |
| Initiatives | Initiative, InitiativeStage, SignalCluster, AutoTopic, HiveMindSession | `core.models`, `core.models_document_registry`, `core.models_signal_intelligence` |
| Body systems | HeartBeat, ComponentStatus, BreathCycle, RespiratoryStatus | `core.models_heart`, `core.models_lungs`, `core.models_nervous` |
| Spiders | SpiderData, SpiderExecutionLog, SpiderItemHash | `core.models`, `core.models_unified_system` |
| Monetization | PlacedWager, MLPrediction, Subscription | `core.models` + Stripe integration |

All models inherit `UnifiedBaseModel` — UUID primary keys + audit timestamps.

---

## The Unique Stuff (The IP)

This is **not** "just a bunch of agents." What makes the platform distinctive:

### 1. Claims-Based Content Pipeline
Every factual statement in published content has a deterministic `C-xxxxxxxx` ID that traces back to a specific spider row with URL + timestamp. Citations are verifiable, not hallucinated. Deduplication by normalized URL. Max 20 claims per pack, sorted by freshness.

### 2. Multi-Reviewer Deliberation with Synthetic-FAIL Fallback
3-reviewer panel on every piece of content. Reviewer failures **don't skip** — they generate a synthetic FAIL verdict so `DecisionEnforcer` always sees issues. No silent passes.

### 3. Full Signal Provenance Chain
Every Initiative traces back to originating SpiderData rows via `HiveMindSession → AutoTopic → SignalCluster → SpiderData`. "Why does this project exist?" is a database query.

### 4. Learning Loop + XP Budget
Agents track `AgentLearning`, accumulate XP, get performance feedback injected into their next prompt. `CoordinatorOutcome` has 17,500+ rows locally (live counter). The platform gets smarter at specific agents over time.

### 5. Self-Aware System (Session 1099, hardened through Session 1223)
The doc-vs-reality verifier + `PLATFORM_INVENTORY.md` means the platform now knows when its docs disagree with its code. It can audit itself. 73 claims registered across 34 source files, **0 drifts** as of Session 1223 — the original Session 1099 audit flagged 45/65, and sustained closing-the-loop work across Sessions 1100→1223 brought that to zero (and held it there through the audit-framework expansion). One command to regenerate the inventory.

### 6. Body-Systems Health Metaphor
The autonomic reflex layer is genuinely novel. No other Django platform models itself as human anatomy with autonomic responses.

### 7. Rigby as Single Conversational Brain
101 tool schemas + function calling + async enrichment means Rigby can reach into every subsystem through natural conversation. One message can cluster signals, run three agents in parallel, read the boardroom, and post to Discord.

### 8. Autonomous Content Studio (Session 466)
AI podcast generation + campaign orchestration + content distribution + 6 content production flows (blog, podcast, video, newsletter, social campaign, etc.) — all coordinated through `AutonomousContentStudioCoordinator`.

### 9. Blockchain + Stock + Market Audits
9 stock agents + 5 blockchain agents + multiple market agents all feeding dedicated audit coordinators. Provenance-tracked, budget-governed.

### 10. Beat Governor + Priority Router
Session 1087/1089 added a cost-governed dispatcher that throttles low-priority tasks when the daily budget fills, plus a priority router with observer-mode gating for graceful rollout.

---

## Current State Honesty

### Working well (as of Session 1223)

- Personal Assistant (Rigby) — 109 tool schemas, GPT-5.2 function calling, local + prod both operational. Continuous 6-session conversation thread (`pa-58737666f25741dc`, Sessions 1217-1222) held cleanly before voluntary retirement at the `strongly_recommend_fresh` health signal — `session_tool.health_check` working as designed.
- Celery beat governor — noise tasks classified and disabled (305→92 PeriodicTask rows), budget gating live; schedule definitions primarily live in `core/celery.py` and are materialized or repaired into `PeriodicTask` rows by sync/bootstrap commands. Both CI lints (`check-llm-sdk.yml` + `check-reasoning-contract.yml`) now in enforce mode after the Session 1222 P3 + P5 promotions.
- Content autonomy loop with EditorAgent repairs.
- Body systems monitoring — Railway health at 90-100%.
- Factory clients — all OpenAI + Anthropic clients on proper factory wrappers (`get_openai_client()`, `get_async_openai_client()`, `get_anthropic_client()`). 600s default-timeout footguns eliminated.
- CTO diagnostic agent (Session 1093) + scheduled-agent-as-monitor primitive generalized (1094).
- Mythology anti-spam safety rails (Session 1096) — severity escalation, daily post caps, HAI bridge.
- Governance redesign canary (Session 1098) — DeliverableAppend path working end-to-end.
- Self-directed audit framework (Session 1217 → 1222) — 15-finding deliverable `bec077ed-…` drove 12 closures across 6 sessions; remaining 3 are M-effort docs-track.

### OpenAI hardening — Sessions 1214-1216 + 1221

A four-session arc closed the platform's "direct OpenAI SDK usage" surface end-to-end. Single spec, single catalog deliverable maintained throughout, three single-day sessions then a separate follow-on for the zombie loophole.

**Phase A+B — factory adoption + dead-code removal (Session 1214, 8 PRs)**
- Audited 74 → 21 truly bare `OpenAI()` / `AsyncOpenAI()` no-arg instantiations across 6 active files
- 6 factory swaps (`OpenAI()` → `get_openai_client()`) + 15 dead-code removals (vestigial async clients whose `client` variable was never invoked — dispatch routes through `agent_llm_integration.generate_for_agent`) + 1 central swap (`OpenAIProvider.__init__`)
- New `get_async_openai_client()` factory infrastructure (PR #2490) — mirrors sync factory, isolated `_ASYNC_CLIENT_CACHE`, same 20/90/60/60s timeouts, same forbidden-kwargs guard
- Net: 22 × 600s SDK timeout footguns eliminated, 50+ lines of vestigial dead code gone

**Phase C+D — reasoning-contract fixes (Session 1215, 3 PRs)**
- Scoping correction: raw `\bmax_tokens\s*=` grep returned 158 matches across 77 files, but `LLMRequest.max_tokens` is correctly abstracted by `llm_provider_registry.py` — most matches route through the registry abstraction and are NOT Phase C/D targets. Actual scope: 3 files, 8 sites.
- **Top-impact win:** `content/ai_providers.py` was making 2 API round-trips on every gpt-5-mini call (try-with-wrong-params → fail → catch → retry-without-token-limit) — PR #2495 eliminated the wasted round-trip
- `core/views_ai_learning_api.py` 3-site fix (PR #2496) — silent backend 500s replaced with correct calls
- `agents/executors/base_executor.py` conditional `temperature` strip for gpt-5.x (PR #2497) — preserves sampling control for non-reasoning callers

**Phase E — runtime guard + CI lint (Session 1216, 2 PRs)**
- `apply_reasoning_guard()` + `ReasoningGuardViolation` + `_install_reasoning_guard()` in `core/services/openai_client_factory.py` — factory-returned clients have their `chat.completions.create` method wrapped at construction time, mode env-gated via `OPENAI_REASONING_GUARD={warn,strip,error}` (default `warn`)
- AST-based `tools/check_reasoning_contract.py` + `.github/workflows/check-reasoning-contract.yml` — AST parsing avoids docstring false positives the regex lint produces. Shipped `--warn-only` (Phase C+D close left zero violations on main); flipped to enforce mode in Session 1222 P3 (PR #2525)
- Spec deliverable `2b9aa447-…` flipped to `completed` via `content_tool.content_complete`

**Tier 1 + Tier 2 — zombie LLM-call close (Session 1221, 2 PRs)**
- Driven by Session 1220 P2 investigation deliverable `7ae61cf7-…` — `httpx.Timeout(read=90s)` only bounds per-chunk silence, not total request wall-clock; long-running streaming responses could go zombie indefinitely
- **Tier 1** (PR #2519): total-request bound on `BaseAgent._call_openai` via `_run_openai_create_with_total_cap()` helper. Cap formula: `max(180.0, llm_timeout * 2.5)` per-agent. Floor of 180s sits above observed legitimate `ContentWriterAgent` 102.7s SUCCESS max.
- **Tier 2** (PR #2520): `LLMCallEvent` cleanup watchdog (`cleanup-stuck-llm-calls` beat task, `*/10` minute cadence) catches zombies from non-`BaseAgent` paths. Mirror of the existing `_impl_cleanup_stale_agent_executions`.

**Cumulative impact:** 16 PRs across Sessions 1214-1216 + 2 PRs in Session 1221 = **~30 call sites aligned, runtime guard + CI lint in place at both the contract layer (Phase E) and the total-wall-clock layer (Tier 1/2)**. Catalog deliverable `bb775acb-…` (Platform Capability Audit category, pinned in Donkey Betz workspace) grew from 6.3KB seed → 17,068 chars final, with per-callsite + per-PR provenance entries.

### Doc-claim verifier state (Session 1223, 2026-06-23)

Out of **73 registered claims across 34 source files**, **0 drift from reality** as of this refresh. Session 1099 (the original audit cited below) flagged 45/65 — sustained closing-the-loop work across sessions 1100→1142 brought that to zero, and the Sessions 1142→1223 expansion of the audit framework (Runtime Evidence promotion, narratives layer, EDITING_GUARDRAILS, patents README) held it there. Session 1223 audit #8 close (PR #2534) is what made the agent-count subset drift-clean for the first time.

| Class of drift | Status |
|---|---|
| Numeric claims (counts, schedules, registries) | Clean — all 73 match runtime |
| Header staleness (`Last Updated: Session N`) | **Not covered** by `verify_doc_claims`; tracked by `check_doc_headers` (Session 1142) |
| Frozen docs (Category B) | Triage queued — `docs/AUTONOMOUS_SYSTEMS.md`, `INTELLIGENCE_SYSTEMS.md`, `MODELS.md`, `ERROR_TRACKING.md`, `DEPLOYMENT_GUIDE.md`, `PERSONA_AGENTS.md` untouched since Session 484-901; decide archive vs refresh in a separate pass |

Re-run anytime with `python manage.py verify_doc_claims --only-drift` (numeric claims) or `python manage.py check_doc_headers` (header recency).

#### Historical snapshot — Session 1099 audit

Original drift survey (preserved for context):

| Drift class | Then-biggest offenders |
|---|---|
| Stale stats tables | CAPABILITIES.md (Jan 28), AGENTS.md (Feb 8), SERVICES.md (Feb 7), docs/current/* (Jan 2026) |
| Contradictions | PA tool count claimed as 77/85+/86/89/231 across docs |
| Architectural drift | topics/frontend.md claims 9 workspace tabs — code has 5 primary |
| Scheduling drift | topics/agent-system.md claims 4 Intelligence Desks run daily — only 1 actually does |

### Known issues queued for follow-up (Session 1223 active tail)

Audit deliverable `bec077ed-…` (Session 1217 self-directed, 15 findings) — **closed 12/15, 3 open**:

- **#4 — Critical hub markers / gates** (M): reliability work — flag critical-path files for extra review, extend PR template + add CODEOWNERS / path-pattern gate
- **#9 — Core orientation doc staleness** (M): _this doc_ — addressed in Session 1223 refresh (the one you're reading)
- **#10 — Atlas fleet capabilities positioning** (M): narrow Phase 1 "fleet integration" claims in `docs/24_7_GLOBAL_AI_APP_ATLAS.md` to match runtime reality

Historical follow-ups from Session 1099 (preserved for context — most have aged out):

- **Stock agent rotation**: 4/5 failed on 2026-04-17 18:46 rotation (StockAnalyst, BullCase, BearCase, MarketIntelligenceCoordinator) — not blocking; resolution status unclear.
- **Session 1098 canary test artifacts**: 24h observation window has long closed; canary path validated and shipped.
- **Dormant agents**: addressed via Session 1217 audit B2 (4 keep-disabled with operator-readable reasons + 1 re-enabled with `dry_run=True` for 2-Friday burn-in per PR #2530).
- **SpiderData embedding coverage** (originally 20.1%): unchanged status; still partial for spider intelligence semantic search.
- **0 Initiatives completed**: pipeline creates but doesn't finish work items. Fast Track auto-progression stalls at Stage 2. Still true; not on the active arc.

---

## How to Navigate the Platform

### The six docs to know

1. **[`docs/PLATFORM_INVENTORY.md`](PLATFORM_INVENTORY.md)** — runtime truth. Regenerable. Single source of truth when other docs disagree.
2. **[`docs/PLATFORM_WHAT_IT_IS.md`](PLATFORM_WHAT_IT_IS.md)** — this doc. Conceptual narrative.
3. **[`CLAUDE.md`](../CLAUDE.md)** — AI session entry point + design intent. (Several stats drift; verifier catches those.)
4. **[`00-START-NEXT-SESSION.md`](../00-START-NEXT-SESSION.md)** — current priorities per session.
5. **[`docs/topics/`](topics/)** — 19 subsystem deep-dives (PA, content pipeline, body systems, etc.).
6. **[`docs/audit-2026/`](audit-2026/)** — 15 subsystem dossiers with verified runtime evidence.

### The three commands to remember

```bash
# Regenerate the platform inventory (runtime truth snapshot)
python manage.py generate_platform_inventory

# Check which docs disagree with reality
python manage.py verify_doc_claims --only-drift

# Rebuild the docs search/embedding index (run after any doc change)
python manage.py build_docs_index
```

### Asking Rigby

Use the local wrapper — it hardcodes the right token + active conversation:

```bash
./tools/pa_local.sh "your question"
```

Or call directly if you want explicit env override (the script defaults to PROD — see Session 1184 trap in `00-START-NEXT-SESSION.md` "READ THIS FIRST"):

```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-donkeyking-token> \
.venv/bin/python tools/pa_chat.py "your question" --conversation <conversation-id>
```

Conversation IDs rotate per session arc — current pin lives in `tools/pa_local.sh`. Health-check with `session_tool.health_check` before continuing a multi-session thread; pin gets retired when score reaches `strongly_recommend_fresh`.

### Restarting the platform

```bash
# Local — full restart
pkill -f daphne; pkill -f redis; pkill -f celery
rm -f .daphne.pid .celery.pid .celery-beat.pid
make start && make celery

# Access the web UI
open http://localhost:8000/ai-studio/
```

---

## Glossary

| Term | Meaning |
|---|---|
| **Agent** | A specialized AI worker. Code agents are Python classes in `core/agents/`; persona agents are DB rows routed through `DynamicPersonaAgent`. |
| **AGENT_MAP** | Dictionary in `core/agent_router.py` mapping agent names → agent classes. Current size: 83. |
| **Advisor** | A functional domain-specialist advisor (Value Investing Strategist, Innovation Investment Strategist, Macro Economic Strategist, Sports Analytics Pioneer, etc.) injected into prompts via `AdvisorContextBuilder`. 30 total. Identities are functional, not modeled on real-world figures. |
| **AIEmployee** | A frozen dataclass in `core/employees/jobs.py` carrying an Employee OS identity (handle, display_name, runs_as_username, primary_chat_id, notes). Three exist as of Session 1258: Documentation Manager (Rigby), Platform Auditor, Chief of Staff. No DB model — identity is policy-as-code. |
| **AgentMemory** | A specific memory of one agent execution. Safety-classified (`test_only`/`exploratory`/`candidate`/`approved`). |
| **AutoTopic** | A topic auto-generated from a signal cluster, ready to drive initiative creation. |
| **BaseAgent** | The 5,575-line base class every code agent inherits from. |
| **Beat Governor** | Cost-governed Celery Beat dispatcher (Session 1089). |
| **Body Systems** | 9 anatomical health monitors (HEART, LUNGS, BRAIN, etc.). |
| **ClaimsPack** | A deduplicated, capped collection of factual claims (max 20) extracted from SpiderData + SignalClusters. |
| **CoordinatorOutcome** | Record of a multi-agent debate/deliberation outcome. 17,500+ rows locally (live counter). |
| **Deliberation** | Multi-reviewer review of draft content. 3 reviewers. |
| **DeliverableAppend** | Canary path (Session 1098) for appending agent output to an existing Deliverable instead of creating a new one. |
| **DynamicPersonaAgent** | Fallback agent that hydrates a persona from a DB row. Available as DB-backed persona rows. |
| **Employee OS** | The primitive-reuse pattern that composes `AIEmployee` + `JobContract` + `MissionRunner` + `OpsRun(domain='mission')` + verdict + escalation + shift report into deterministic AI workers. Three production employees as of Session 1258. Canonical primitives and anti-duplication rules in [`EMPLOYEE_OS_PRIMITIVES.md`](EMPLOYEE_OS_PRIMITIVES.md). |
| **HiveMindSession** | A multi-agent debate session with full participant tracking. |
| **JobContract** | A frozen dataclass in `core/employees/jobs.py` carrying an Employee OS job's policy: mission, responsibilities, triggers, daily routine, authority, prohibited_actions, escalation rules, dedupe rule, evidence contract. Git-versioned, PR-reviewable. No admin UI, no migration. |
| **Initiative** | A platform project. Has 5 stages + provenance back to signals. |
| **LUNGS budget** | Per-provider/per-agent token budget tracking. |
| **MissionRunner** | The Employee OS orchestrator (`core/employees/mission_runner.py`). Owns lifecycle policy — preflight → ordered steps → postflight → verdict emission → escalation with dedupe. Does *not* own domain logic; job modules supply step functions. Stable infrastructure as of Session 1258. |
| **OpsRun** | A Django model row (`core/models_ops_runs.py`) representing one execution of an ops or mission task. `domain='mission'` + `run_kind=<job-key>` distinguishes Employee OS mission rows from generic ops rows — added in Session 1250 specifically to avoid building a separate `MissionRun` model. |
| **PA / Rigby** | The Personal Assistant — `UnifiedPAEntrypoint`. Your single conversational interface. |
| **PeriodicTask** | A django-celery-beat scheduled task row. 92 total, 88 enabled (down from 305 in Session 1099 after the noise-task cleanup arc through Session 1222). |
| **PlatformInventory** | The Session 1099 runtime-derived master doc. Companion to this one. |
| **Priority Router** | Observer-mode priority gating system (Session 1087). |
| **Provenance** | The full chain of evidence backing an agent's output — data sources, timestamps, validation. |
| **SelfBlog** | The platform's blog content model, output of the content pipeline. |
| **Signal** | A pattern detected in spider data. 10 pattern types. |
| **SKIN layer** | The filesystem-write subsystem. Agents → WorkspaceManager → files with audit trail. |
| **Spider** | A data-ingestion worker. 80 registered. |
| **SpiderData** | Normalized rows of raw data from spiders. Core sensory table. |
| **Verifier** | Doc-vs-reality verifier (Session 1099). `python manage.py verify_doc_claims`. |

---

*Last revised: Session 1223 (2026-06-23). When this doc drifts from reality,
regenerate `PLATFORM_INVENTORY.md` first — that's always authoritative.*
