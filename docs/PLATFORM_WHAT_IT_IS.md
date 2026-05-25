---
title: "Donkey Betz Platform — What It Actually Is"
status: active
session: 1141
generated: 2026-05-24
last_reviewed: 2026-05-24
companion_doc: PLATFORM_INVENTORY.md
---

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
> at time of writing (Session 1099 audit, 2026-04-18); regenerate the
> inventory for a fresh snapshot.

---

## TL;DR — One Sentence

You've built an autonomous multi-agent intelligence platform that ingests real-time data from **80 spiders**, clusters it into signals, routes signals through **83 specialized AI agents** deliberating in multi-reviewer pipelines with full citation provenance, surfaces everything through a GPT-5.2-powered personal assistant (**Rigby**) with **101 tools** and **8 enrichment services**, monitors itself via a **9-system "body" health metaphor**, and audits its own documentation against runtime reality.

**Scale:** ~919K lines of app Python (core/ + ai_core/). 570 database tables. 365 Celery tasks. One conversational interface to all of it.

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

Below the code agents: DB persona rows via `DynamicPersonaAgent` fallback give you long-tail specialists. Plus **32 advisors** (10 named figures — Warren Buffett, Cathie Wood, Ray Dalio, Sam Altman, Elon Musk, Gary Vaynerchuk, Mr Beast, Chris Voss, Billy Beane, Haralabos Voulgaris — and 22 domain specialists) accessible through `AdvisorContextBuilder`.

**Router entry point:** `AgentRouter.route(agent_name, task, context)` performs parallel context gathering (11 workers × 10s timeout each) before dispatching to the agent. See `core/agent_router.py:738-1264`.

### Layer 4 — Personal Assistant (Rigby)

The single conversational entry point. `UnifiedPAEntrypoint` in `core/services/unified_pa_entrypoint.py`.

**Inventory:**
- **101 tool schemas** visible to GPT-5.2 via OpenAI function calling
- **166 tool handlers** in `ToolDispatcher` (`core/services/tool_dispatcher.py`)
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
- 365 user-defined Celery tasks (excludes `celery.*` internals)
- `core/celery.py` is the primary static source of beat definitions; `django-celery-beat` stores the 305 runtime `PeriodicTask` rows (258 enabled, 47 disabled)
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

**Routes** — 60 `<Route>` entries in `App.tsx`. Key routes:
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

**570 concrete Django models across 23 apps.** Key model families:

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

### 5. Self-Aware System (Session 1099)
The doc-vs-reality verifier + `PLATFORM_INVENTORY.md` means the platform now knows when its docs disagree with its code. It can audit itself. 65 claims registered, 45 drifts currently tracked, one command to regenerate the inventory.

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

### Working well (as of Session 1099)

- Personal Assistant (Rigby) — 101 tools, GPT-5.2 function calling, local + prod both operational
- Celery beat governor — 47 noise tasks disabled, budget gating live; schedule definitions primarily live in `core/celery.py` and are materialized or repaired into `PeriodicTask` rows by sync/bootstrap commands
- DeliverableAppend canary (Session 1098) — green after Plan A injection, 24h observation window in progress
- Content autonomy loop with EditorAgent repairs
- Body systems monitoring — Railway health at 90-100%
- Factory clients — all OpenAI + Anthropic clients migrated to proper factory wrappers
- CTO diagnostic agent (Session 1093) + scheduled-agent-as-monitor primitive generalized (1094)
- Mythology anti-spam safety rails (Session 1096) — severity escalation, daily post caps, HAI bridge
- Governance redesign canary (Session 1098) — DeliverableAppend path working end-to-end

### Stale or drifting (tonight's audit found)

Out of 65 registered doc claims across 24 docs, **45 drift from reality**:

| Drift | Biggest offenders |
|---|---|
| Stale stats tables | CAPABILITIES.md (Jan 28), AGENTS.md (Feb 8), SERVICES.md (Feb 7), docs/current/* (Jan 2026) |
| Contradictions | PA tool count claimed as 77/85+/86/89/231 across docs — actual 101 |
| Architectural drift | topics/frontend.md claims 9 workspace tabs — code has 5 primary |
| Scheduling drift | topics/agent-system.md claims 4 Intelligence Desks run daily — only 1 actually does |

See `python manage.py verify_doc_claims --only-drift` for the live list.

### Known issues queued for follow-up

- **Stock agent rotation**: 4/5 failed on 2026-04-17 18:46 rotation (StockAnalyst, BullCase, BearCase, MarketIntelligenceCoordinator) — not blocking but needs root-cause.
- **Session 1098 canary test artifacts**: Deliverable `c7f4c940` + blog `b8a2b6a3` intentionally live until 24h observation window closes.
- **Phase-2 initiative guard test**: validate `expected_initiative_id` mismatch handling on a blog with an initiative.
- **SpiderData embedding coverage**: only 20.1% of spider data is embedded (memory is 97.6%) — semantic search is partial for spider intelligence.
- **Dormant agents**: many agent records have zero executions in the last 30 days. Either wire them to real tasks or remove.
- **0 Initiatives completed**: pipeline creates but doesn't finish work items. Fast Track auto-progression stalls at Stage 2.

---

## How to Navigate the Platform

### The six docs to know

1. **[`docs/PLATFORM_INVENTORY.md`](PLATFORM_INVENTORY.md)** — runtime truth. Regenerable. Single source of truth when other docs disagree.
2. **[`docs/PLATFORM_WHAT_IT_IS.md`](PLATFORM_WHAT_IT_IS.md)** — this doc. Conceptual narrative.
3. **[`CLAUDE.md`](../CLAUDE.md)** — AI session entry point + design intent. (Several stats drift; verifier catches those.)
4. **[`00-START-NEXT-SESSION.md`](../00-START-NEXT-SESSION.md)** — current priorities per session.
5. **[`docs/topics/`](topics/)** — 14 subsystem deep-dives (PA, content pipeline, body systems, etc.).
6. **[`docs/audit-2026/`](audit-2026/)** — 13 subsystem dossiers with verified runtime evidence.

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

```bash
# Continuous conversation since Session 1094 (LOCAL)
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-donkeyking-token> \
.venv/bin/python tools/pa_chat.py "your question" --conversation pa-3c7ddc058db1
```

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
| **Advisor** | A "personality-infused" advisor (Warren Buffett-style, Cathie Wood-style, etc.) injected into prompts via `AdvisorContextBuilder`. 25 total. |
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
| **HiveMindSession** | A multi-agent debate session with full participant tracking. |
| **Initiative** | A platform project. Has 5 stages + provenance back to signals. |
| **LUNGS budget** | Per-provider/per-agent token budget tracking. |
| **PA / Rigby** | The Personal Assistant — `UnifiedPAEntrypoint`. Your single conversational interface. |
| **PeriodicTask** | A django-celery-beat scheduled task row. 305 total, 258 enabled. |
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

*Last revised: Session 1099 (2026-04-18). When this doc drifts from reality,
regenerate `PLATFORM_INVENTORY.md` first — that's always authoritative.*
