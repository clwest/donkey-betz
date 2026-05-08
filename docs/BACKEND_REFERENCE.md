<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_WHAT_IT_IS.md`](/docs/PLATFORM_WHAT_IT_IS.md) and [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality.

# Backend Reference Guide

**Last Updated:** January 9, 2026 - Session 739 — narrative preserved; counts may drift
**Purpose:** Complete reference of all backend systems, APIs, models, and services with detailed explanations
**Canonical counts:** Always check [`PLATFORM_INVENTORY.md`](PLATFORM_INVENTORY.md) — Session 739 numbers below are a historical snapshot.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Database Models](#2-database-models-403-total)
3. [API Endpoints](#3-api-endpoints-305-v1-endpoints)
4. [Services](#4-services-144-total)
5. [Celery Tasks](#5-celery-tasks)
6. [Body Systems](#6-body-systems-9-systems)
7. [Spider Network](#7-spider-network-77-spiders) <!-- canonical = 80; see PLATFORM_INVENTORY -->
8. [ML Models](#8-ml-models)
9. [Agents](#9-agents-72-total)
10. [Advisors](#10-advisors-25-total)
11. [Sci-Fi Features](#11-sci-fi-features-14-total)
12. [WebSocket Endpoints](#12-websocket-endpoints)
13. [Authentication](#13-authentication)
14. [File Structure](#14-file-structure)

---

## 1. System Overview

### What Is This Platform?

This is an **AI-powered intelligence and revenue generation platform** that combines:

- **72 AI Agents** - Specialized AI workers that perform tasks (research, content creation, analysis, etc.)
- **77 Data Spiders** - Web scrapers that gather real-time intelligence from across the internet
- **25 Advisors** - AI personas modeled after famous investors and domain experts
- **9 Body Systems** - A biological metaphor for monitoring system health (Heart, Brain, Lungs, etc.)
- **14 Sci-Fi Features** - Advanced AI features like Dreams, Time Capsules, Memory Palace, Evolution

### How It Works

1. **Spiders** gather data from 77+ sources (news, markets, jobs, tech, legal, etc.)
2. **Agents** process this data and perform specialized tasks
3. **Coordinators** orchestrate multiple agents for complex workflows
4. **Advisors** provide expert perspectives on decisions
5. **Body Systems** monitor the health and performance of everything
6. **The Platform** exposes all this via 305+ API endpoints for the React frontend

### Key Concepts

| Concept | What It Is | Why It Matters |
|---------|------------|----------------|
| **Agent** | An AI worker with specific capabilities | Each agent specializes in something (research, coding, analysis) |
| **Spider** | A data scraper for a specific source | Brings real-world data into the system |
| **Coordinator** | An agent that manages other agents | Enables complex multi-agent workflows |
| **Advisor** | An AI persona with expertise | Provides human-like expert opinions |
| **Body System** | A health monitoring component | Ensures the platform runs smoothly |
| **Opportunity** | A potential revenue source | What the platform helps users find and act on |
| **Action Plan** | Steps to earn money | Generated plans users can execute |

---

## 2. Database Models (403 Total)

### Core App Models (291)

#### Agent System Models

**Agent** (`core.Agent`)
- **What it is:** The registry of all AI agents in the system
- **What it does:** Stores agent metadata, capabilities, and configuration
- **Key fields:** `name`, `description`, `capabilities` (JSON), `is_active`, `agent_type`
- **Example:** "ResearchAgent" with capabilities ["web_search", "summarization", "analysis"]

**AgentExecution** (`core.AgentExecution`)
- **What it is:** A log of every time an agent runs
- **What it does:** Tracks what task was given, what result was produced, how many tokens were used, and how much it cost
- **Key fields:** `agent`, `task`, `status`, `result`, `tokens_used`, `cost`, `duration_ms`
- **Why it matters:** Enables cost tracking, performance monitoring, and debugging

**AgentMemory** (`core.AgentMemory`)
- **What it is:** Memories that agents can recall
- **What it does:** Stores important information with embeddings for semantic search
- **Key fields:** `agent`, `content`, `embedding` (vector), `importance`, `memory_type`
- **Why it matters:** Agents can remember past interactions and learn from them

**AgentLearning** (`core.AgentLearning`)
- **What it is:** Learning records from agent activities
- **What it does:** Captures what agents learn from spider data and executions
- **Key fields:** `agent`, `learning_type`, `content`, `source`, `confidence`
- **Current count:** 46,330 records

**AgentMood** (`core.AgentMood`)
- **What it is:** The current emotional state of each agent
- **What it does:** Affects how agents respond (confident, cautious, excited, etc.)
- **Key fields:** `agent`, `mood`, `intensity`, `triggers`, `expires_at`
- **Why it matters:** Makes agents feel more human and contextually appropriate

**AgentEvolution** (`core.AgentEvolution`)
- **What it is:** Tracks how agents evolve over time
- **What it does:** Records mutations, fitness scores, and generational changes
- **Key fields:** `agent`, `generation`, `mutations`, `fitness_score`, `parent_evolution`
- **Why it matters:** Enables agents to improve through evolutionary algorithms

**AgentRelationship** (`core.AgentRelationship`)
- **What it is:** Relationships between agents
- **What it does:** Tracks friendships, rivalries, mentorships, and collaborations
- **Key fields:** `agent_a`, `agent_b`, `relationship_type`, `strength`, `interaction_count`
- **Current count:** 462 relationships

**AgentDream** (`core.AgentDream`)
- **What it is:** Dreams/aspirations generated by agents
- **What it does:** Agents "dream" about improvements, features, or creative ideas
- **Key fields:** `agent`, `content`, `dream_type`, `status`, `implemented`
- **Current count:** 7,342 dreams
- **Why it matters:** Source of autonomous innovation and self-improvement

**AgentPrediction** (`core.AgentPrediction`)
- **What it is:** Predictions made by agents
- **What it does:** Stores forecasts with confidence levels and tracks accuracy
- **Key fields:** `agent`, `prediction`, `confidence`, `deadline`, `outcome`
- **Current count:** 50 predictions

**AgentChannel** (`core.AgentChannel`)
- **What it is:** "Slack for AI Agents" - communication channels
- **What it does:** Allows agents to communicate in topic-based channels
- **Key fields:** `name`, `description`, `channel_type`, `created_at`
- **Current count:** 2 channels

**ChannelMembership** (`core.ChannelMembership`)
- **What it is:** Which agents belong to which channels
- **What it does:** Manages channel membership and roles
- **Key fields:** `channel`, `agent`, `role`, `joined_at`
- **Current count:** 4 memberships

**ChannelMessage** (`core.ChannelMessage`)
- **What it is:** Messages sent in agent channels
- **What it does:** Stores inter-agent communication
- **Key fields:** `channel`, `sender`, `content`, `timestamp`, `message_type`
- **Current count:** 0 (feature ready but not yet active)

#### Opportunity & Income System Models

**Opportunity** (`core.Opportunity`)
- **What it is:** A potential revenue-generating opportunity
- **What it does:** Stores opportunities found by spiders (jobs, gigs, business ideas)
- **Key fields:** `title`, `description`, `value`, `status`, `source`, `url`, `deadline`
- **Current count:** 1,574 opportunities
- **Why it matters:** Core of the income generation system

**OpportunityAction** (`core.OpportunityAction`)
- **What it is:** Actions taken on opportunities
- **What it does:** Tracks when users apply, save, dismiss, or complete opportunities
- **Key fields:** `opportunity`, `action_type`, `result`, `timestamp`

**PredictionOutcome** (`core.PredictionOutcome`)
- **What it is:** Results of predictions
- **What it does:** Records whether predictions were correct and by how much
- **Key fields:** `prediction`, `actual_outcome`, `accuracy_score`, `resolved_at`
- **Current count:** 4,184 outcomes

#### Pilot & Gate System Models

**PilotReadinessGate** (`core.PilotReadinessGate`)
- **What it is:** A checklist gate before launching pilots
- **What it does:** Ensures pilots meet quality criteria before going live
- **Key fields:** `decision`, `status`, `checklist_items` (JSON), `approved_by`
- **Current count:** 100 gates

**PilotExecution** (`core.PilotExecution`)
- **What it is:** A running pilot experiment
- **What it does:** Tracks pilot progress, metrics, and results
- **Key fields:** `gate`, `start_time`, `end_time`, `results`, `status`
- **Current count:** 54 pilots

**PilotImplementation** (`core.PilotImplementation`)
- **What it is:** Code/implementation for a pilot
- **What it does:** Stores the actual implementation details
- **Key fields:** `pilot`, `code`, `status`, `deployed_at`
- **Current count:** 11 implementations

#### Memory System Models

**ConversationMemory** (`core.ConversationMemory`)
- **What it is:** User conversation history with the Personal Assistant
- **What it does:** Stores chat history for context and personalization
- **Key fields:** `user`, `content`, `embedding`, `created_at`
- **Current count:** 617 memories

**MemoryCluster** (`core.MemoryCluster`)
- **What it is:** Grouped memories by topic/theme
- **What it does:** Organizes memories into semantic clusters
- **Key fields:** `name`, `memories`, `centroid` (embedding), `created_at`
- **Current count:** 6 clusters

#### Body System Models

**HeartBeat** (`core.HeartBeat`)
- **What it is:** Heart health snapshots
- **What it does:** Records system-wide health at regular intervals
- **Key fields:** `timestamp`, `bpm`, `status`, `components_health`
- **Current count:** 3 beats

**SpineStatus** (`core.SpineStatus`)
- **What it is:** API routing health
- **What it does:** Tracks which routes are healthy and their latencies
- **Key fields:** `timestamp`, `routes_healthy`, `total_routes`, `avg_latency`
- **Current count:** 2 statuses

**ImmuneStatus** (`core.ImmuneStatus`)
- **What it is:** Security system status
- **What it does:** Tracks threats detected and quarantined items
- **Key fields:** `timestamp`, `threats_detected`, `items_quarantined`, `status`
- **Current count:** 1 status

**DigestivePulse** (`core.DigestivePulse`)
- **What it is:** Data ingestion metrics
- **What it does:** Tracks how much data is being processed
- **Key fields:** `timestamp`, `items_processed`, `processing_rate`, `bottlenecks`
- **Current count:** 101 pulses

**MuscleGroup** (`core.MuscleGroup`)
- **What it is:** Groups of agents that work together
- **What it does:** Tracks fatigue and workload of agent groups
- **Key fields:** `name`, `agents`, `fatigue_level`, `last_worked`
- **Current count:** 10 groups

**SkinPulse** (`core.SkinPulse`)
- **What it is:** Workspace activity snapshots
- **What it does:** Tracks file writes and project changes
- **Key fields:** `timestamp`, `files_written`, `projects_modified`, `status`
- **Current count:** 12 pulses

**SkinStatus** (`core.SkinStatus`)
- **What it is:** Overall workspace health
- **What it does:** Tracks workspace status (healthy, active, irritated, etc.)
- **Key fields:** `status`, `last_activity`, `recent_operations`
- **Current count:** 1 status

#### Time & Evolution Models

**TimeCapsule** (`core.TimeCapsule`)
- **What it is:** Messages from agents to their future selves
- **What it does:** Agents create capsules that unlock at future dates
- **Key fields:** `agent`, `content`, `reveal_at`, `revealed`, `reactions`
- **Current count:** 7 capsules

**TimeCapsuleReaction** (`core.TimeCapsuleReaction`)
- **What it is:** Reactions to revealed time capsules
- **What it does:** Other agents can react when a capsule is revealed
- **Key fields:** `capsule`, `reactor`, `reaction`, `timestamp`

**DreamImplementation** (`core.DreamImplementation`)
- **What it is:** Dreams that were actually implemented
- **What it does:** Tracks which dreams became real features
- **Key fields:** `dream`, `implementation`, `status`, `implemented_at`
- **Current count:** 10 implementations

#### Coordinator System Models

**CoordinatorOutcome** (`core.CoordinatorOutcome`)
- **What it is:** Results from coordinator agent workflows
- **What it does:** Tracks multi-agent collaboration outcomes
- **Key fields:** `coordinator`, `task`, `agents_used`, `outcome`, `total_cost`
- **Current count:** 4,086 outcomes
- **Why it matters:** Shows that agents are actively collaborating

#### Advisor System Models

**Advisor** (`core.Advisor`)
- **What it is:** Famous investor/expert personas
- **What it does:** Provides AI personalities for consultation
- **Key fields:** `name`, `expertise`, `personality`, `bio`, `avatar`
- **Current count:** 25 advisors

**AdvisorInsight** (`core.AdvisorInsight`)
- **What it is:** Advice given by advisors
- **What it does:** Stores recommendations and insights from consultations
- **Key fields:** `advisor`, `insight`, `context`, `confidence`, `timestamp`

#### Spider System Models

**SpiderData** (`core.SpiderData`)
- **What it is:** Data collected by spiders
- **What it does:** Stores scraped content from 77 sources
- **Key fields:** `spider_name`, `content`, `url`, `timestamp`, `embedding`
- **Current count:** 11,549 records

**AgentSpiderConnection** (`core.AgentSpiderConnection`)
- **What it is:** Links between agents and spiders
- **What it does:** Defines which spiders feed which agents
- **Key fields:** `agent`, `spider`, `priority`, `last_sync`

#### Content & Creative Models

**ContentChannel** (`core.ContentChannel`)
- **What it is:** Content publishing channels (YouTube, Blog, etc.)
- **What it does:** Manages automated content publishing
- **Key fields:** `name`, `platform`, `schedule`, `last_published`

**ChannelEpisode** (`core.ChannelEpisode`)
- **What it is:** Individual content pieces
- **What it does:** Stores generated content for channels
- **Key fields:** `channel`, `title`, `content`, `published_at`, `metrics`

**AISeries** (`core.AISeries`)
- **What it is:** AI-generated content series
- **What it does:** Multi-episode content with continuity
- **Key fields:** `title`, `episodes`, `status`, `genre`

### Intelligence App Models

**ActionPlan** (`intelligence.ActionPlan`)
- **What it is:** Step-by-step income generation plans
- **What it does:** The core output of the Income Builder feature
- **Key fields:** `user`, `goal`, `steps`, `status`, `total_value`, `created_at`
- **Current count:** 340 plans
- **Why it matters:** This is what users execute to earn money

**ActionPlanStep** (`intelligence.ActionPlanStep`)
- **What it is:** Individual steps within an action plan
- **What it does:** Breaks plans into executable actions
- **Key fields:** `plan`, `step_number`, `action`, `completed`, `result`

---

## 3. API Endpoints (305+ v1 Endpoints)

### Understanding the API Structure

The API is organized into logical groups:
- **`/api/v1/`** - Versioned REST API (305+ endpoints)
- **`/api/`** - Legacy/utility endpoints
- **`/ws/`** - WebSocket endpoints for real-time features

### Authentication Endpoints (`/api/v1/auth/`)

**What they do:** Handle user authentication and session management.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/login/` | POST | Authenticates user with username/password, returns session |
| `/logout/` | POST | Ends user session |
| `/register/` | POST | Creates new user account |
| `/user/` | GET | Returns current authenticated user info |
| `/profile/` | GET/PUT | Get or update user profile |
| `/change-password/` | POST | Change user's password |
| `/forgot-password/` | POST | Initiates password reset email |
| `/reset-password/` | POST | Completes password reset with token |
| `/validate-token/` | POST | Checks if auth token is valid |
| `/verify-email/` | POST | Verifies email address |
| `/resend-verification/` | POST | Resends verification email |

### Platform Status Endpoints (`/api/v1/`)

**What they do:** Provide system health and status information.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/status/` | GET | Returns platform operational status |
| `/info/` | GET | Returns platform version and capabilities |
| `/metrics/` | POST | Records custom metrics for analytics |
| `/health/` | GET | Simple health check (returns 200 if healthy) |

### Intelligence Endpoints (`/api/v1/intelligence/`)

**What they do:** Power the income generation and opportunity discovery features.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/skynet/status/` | GET | Returns status of the Skynet Intelligence Engine |
| `/opportunities/` | GET | Lists live opportunities (jobs, gigs, business ideas) |
| `/predictions/` | GET | Lists AI predictions with confidence scores |
| `/income-builder/` | GET/POST | Analyzes user's situation and generates income opportunities |
| `/income-builder/action-plan/` | POST | Generates a step-by-step action plan |
| `/income-builder/plans/` | GET | Lists user's saved action plans |
| `/income-builder/execute/` | POST | Executes an action plan step |
| `/income-builder/file/<filename>/` | GET | Views generated files (resumes, proposals) |
| `/revenue/opportunities/` | GET | Lists revenue opportunities |
| `/revenue/metrics/` | GET | Returns revenue tracking metrics |
| `/revenue/submit/` | POST | Submits a proposal to an opportunity |
| `/agents/available/` | GET | Lists agents available for tasks |
| `/agents/execute/` | POST | Executes a specific agent with a task |
| `/agents/status/<execution_id>/` | GET | Gets status of an agent execution |
| `/automation/workflows/` | GET | Lists automation workflows |
| `/automation/setup/` | POST | Sets up a new automation workflow |
| `/automation/execute/` | POST | Executes a daily automation |
| `/automation/quick-start/` | POST | Quick-starts automation for beginners |
| `/advisor-review/` | POST | Requests an advisor to review something |
| `/ai-jobs/spiders/` | GET | Lists job spiders and their status |
| `/ai-jobs/jobs/` | GET | Lists AI-found job opportunities |
| `/ai-jobs/start-spiders/` | POST | Manually triggers job spiders |
| `/ai-jobs/apply/` | POST | Applies to a job via AI |

### Ecosystem Endpoints (`/api/v1/ecosystem/`)

**What they do:** Manage the overall AI ecosystem activation and monitoring.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/activate/` | POST | Activates the full AI ecosystem |
| `/status/` | GET | Returns ecosystem-wide status |
| `/opportunities/` | GET | Lists ecosystem opportunities |
| `/process/` | POST | Processes an opportunity through the pipeline |
| `/agents/` | GET | Returns status of all agents |
| `/advisors/` | GET | Returns advisor network status |
| `/revenue/` | GET | Returns revenue tracking data |

### Agent Endpoints (`/api/v1/agents/`)

**What they do:** Manage the 72 AI agents, their executions, and monitoring.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/registry/` | GET | Lists all registered agents with capabilities |
| `/templates/` | GET | Lists agent templates for creating new agents |
| `/executions/` | GET | Lists agent execution history |
| `/orchestrations/` | GET | Lists multi-agent orchestrations |
| `/tools/` | GET | Lists tools available to agents |
| `/channels/` | GET/POST | Agent communication channels ("Slack for AI") |
| `/messages/` | GET/POST | Messages in agent channels |
| `/memberships/` | GET/POST | Channel membership management |
| `/discover/` | GET | Discovers agents matching criteria |
| `/execute/` | POST | Executes an agent with a task |
| `/health/` | GET | Returns agent system health |
| `/monitoring/dashboard/` | GET | Agent monitoring dashboard data |
| `/monitoring/agent/<name>/` | GET | Detailed performance for one agent |
| `/monitoring/report/` | GET | Performance report |
| `/monitoring/real-time/` | GET | Real-time agent metrics |
| `/monitoring/alerts/` | GET | Active agent alerts |
| `/monitoring/cache/clear/` | POST | Clears metrics cache |

### Body System Endpoints

**What they do:** Monitor and manage the 9 body systems that track platform health.

#### Heart Endpoints (`/api/heart/`)

The Heart is the **central health monitor** - it tracks the overall health of all systems.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/pulse/` | GET | Returns current heartbeat with all component statuses |
| `/status/` | GET | Returns detailed heart status |
| `/history/` | GET | Returns heart health history |
| `/component/<name>/` | GET | Returns specific component health (brain, memory, etc.) |
| `/alive/` | GET | Simple check - is the system alive? |

#### Lungs Endpoints (`/api/lungs/`)

The Lungs manage **resources and capacity** - primarily LLM token budgets.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/breathe/` | POST | Records a "breath" (resource consumption) |
| `/status/` | GET | Returns lungs status and capacity |
| `/oxygen/` | GET | Returns available capacity (tokens remaining) |
| `/budgets/` | GET | Lists all token budgets |
| `/budgets/<id>/` | GET | Returns specific budget details |
| `/forecast/` | GET | Forecasts budget usage |
| `/history/` | GET | Returns resource consumption history |
| `/can-breathe/` | GET | Checks if there's capacity for an operation |
| `/alive/` | GET | Simple check - are lungs working? |

#### Circulatory Endpoints (`/api/circulatory/`)

The Circulatory system tracks **data flow** through the platform.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/circulate/` | POST | Records data flowing through a route |
| `/status/` | GET | Returns circulatory system status |
| `/routes/` | GET | Lists all data routes |
| `/routes/<id>/` | GET | Returns specific route details |
| `/bottlenecks/` | GET | Identifies data flow bottlenecks |
| `/velocity/` | GET | Returns data flow velocity metrics |
| `/history/` | GET | Returns circulation history |

#### Spine Endpoints (`/api/spine/`)

The Spine is the **central API router** - it manages request routing and health-aware routing.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/align/` | POST | Aligns/optimizes routing |
| `/status/` | GET | Returns spine status |
| `/patterns/` | GET | Lists route patterns (19 patterns, 12 categories) |
| `/patterns/<id>/` | GET | Returns specific pattern details |
| `/metrics/` | GET | Returns routing metrics |
| `/history/` | GET | Returns routing history |
| `/can-route/` | GET | Checks if a route is available |
| `/is-aligned/` | GET | Checks if spine is aligned |
| `/categories/` | GET | Lists route categories |

#### Immune Endpoints (`/api/immune/`)

The Immune system handles **security and threat detection**.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/scan/` | POST | Triggers a security scan |
| `/status/` | GET | Returns immune system status |
| `/patterns/` | GET | Lists threat patterns (14 patterns) |
| `/patterns/<id>/` | GET | Returns specific pattern details |
| `/threats/` | GET | Lists active threats |
| `/quarantine/` | GET | Lists quarantined items |
| `/quarantine/<type>/<value>/` | DELETE | Releases item from quarantine |
| `/is-healthy/` | GET | Checks if system is secure |
| `/check-request/` | POST | Checks if a request is safe |
| `/categories/` | GET | Lists threat categories |

#### Digestive Endpoints (`/api/digestive/`)

The Digestive system handles **data ingestion and processing**.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/digest/` | POST | Processes/digests data |
| `/status/` | GET | Returns digestive system status |
| `/routes/` | GET | Lists ingestion routes (8 routes) |
| `/routes/<id>/` | GET | Returns specific route details |
| `/bottlenecks/` | GET | Identifies processing bottlenecks |
| `/metabolism/` | GET | Returns processing rate |
| `/history/` | GET | Returns processing history |
| `/is-digesting/` | GET | Checks if actively processing |

#### Muscular Endpoints (`/api/muscular/`)

The Muscular system tracks **agent work execution**.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/flex/` | POST | Records agent work |
| `/status/` | GET | Returns muscular system status |
| `/groups/` | GET | Lists muscle groups (10 groups) |
| `/groups/<id>/` | GET | Returns specific group details |
| `/weak/` | GET | Identifies underperforming agent groups |
| `/overworked/` | GET | Identifies overworked agent groups |
| `/history/` | GET | Returns work history |
| `/is-strong/` | GET | Checks if system is strong |

#### Brain Endpoints (`/api/brain/`)

The Brain handles **cognitive processing** - LLM calls and reasoning.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/status/` | GET | Returns brain status (focused, thinking, foggy, etc.) |
| `/think/` | POST | Triggers thinking/reasoning |
| `/vitals/` | GET | Returns brain vital signs |
| `/history/` | GET | Returns cognitive history |
| `/is-thinking/` | GET | Checks if actively processing |

#### Skin Endpoints (`/api/skin/`)

The Skin monitors **workspace output** - file writes and project changes.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/status/` | GET | Returns skin status (healthy, active, irritated, etc.) |
| `/feel/` | POST | Records a workspace operation |
| `/vitals/` | GET | Returns skin vital signs |
| `/history/` | GET | Returns workspace activity history |
| `/is-healthy/` | GET | Checks if workspace is healthy |
| `/workspaces/` | GET | Lists active workspaces |

#### Code Artifacts Endpoints (`/api/code-artifacts/`) — Session 1012

Patch-first workflow: when CodeGeneratorAgent can't write to the filesystem (e.g. Railway), code is captured as reviewable artifacts.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/` | GET | Lists code artifacts (filter: `?status=`, `?agent_name=`, `?initiative=`, `?kind=`) |
| `/{id}/` | GET | Full artifact detail with code content |
| `/{id}/approve/` | POST | Approve artifact for later application |
| `/{id}/reject/` | POST | Reject artifact with optional review_note |

#### Unified Body Endpoints (`/api/body/`)

**What they do:** Aggregate all body system data into unified views.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/vitals/` | GET | Returns all body vitals in one call |
| `/alerts/` | GET | Returns alerts from all body systems |
| `/history/` | GET | Returns combined health history |
| `/summary/` | GET | Returns executive summary of body health |
| `/coordination/status/` | GET | Returns body coordination status |
| `/coordination/run/` | POST | Runs body coordination cycle |
| `/coordination/log/` | GET | Returns coordination log |
| `/throttle/` | GET | Returns throttle status |
| `/<system_name>/` | GET | Returns any system by name |

### Spider Intelligence Endpoints (`/api/spider-intelligence/`)

**What they do:** Access intelligence gathered by the 77 spiders.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/trends/` | GET | Returns trending topics across all sources |
| `/market/` | GET | Returns market intelligence (stocks, crypto, etc.) |
| `/tech/` | GET | Returns tech trends and news |
| `/jobs/` | GET | Returns job market intelligence |
| `/search/` | GET | Searches spider data |
| `/summary/` | GET | Returns executive summary of all data |
| `/insights/` | GET | Returns AI-generated insights from spider data |
| `/report/` | GET | Returns daily intelligence report |
| `/registry/` | GET | Lists all registered spiders |
| `/test/` | POST | Tests a specific spider |
| `/run-all/` | POST | Runs all spiders |
| `/market-research/` | GET | Returns market research dashboard data |
| `/dashboard-stats/` | GET | Returns spider dashboard statistics |
| `/opportunities/` | GET | Returns opportunities found by spiders |
| `/feed/` | GET | Returns real-time spider data feed |
| `/knowledge/` | GET | Returns spider knowledge base |
| `/timeline/` | GET | Returns spider activity timeline |
| `/detail/<spider>/` | GET | Returns details for specific spider |

### Spider Health Endpoints (`/api/spider-health/`)

**What they do:** Monitor spider execution and health.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/summary/` | GET | Returns spider health summary |
| `/executions/` | GET | Lists spider execution logs |
| `/executions/<id>/` | GET | Returns specific execution details |
| `/executions/<id>/retry/` | POST | Retries a failed execution |
| `/embedding-coverage/` | GET | Returns embedding coverage stats (currently 87.3%) |
| `/run/<spider>/` | POST | Manually runs a specific spider |

### Sci-Fi Feature Endpoints

#### Dreams Endpoints (`/api/dreams/`)

**What they do:** Manage AI agent dreams - creative ideas generated autonomously.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/<dream_id>/` | GET | Returns dream details |
| `/<dream_id>/generate-review/` | POST | Generates a review of the dream |
| `/reviews/` | GET | Lists all dream reviews |

#### Dream Implementations (`/api/dream-implementations/`)

**What they do:** Track dreams that have been implemented.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/` | GET | Lists all implementations |
| `/<id>/validate/` | POST | Validates an implementation |
| `/metrics/` | GET | Returns validation metrics |

#### Time Capsules Endpoints (`/api/time-capsules/`)

**What they do:** Manage time capsules - messages to future selves.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/` | GET | Returns time capsule overview |
| `/agent/<agent_id>/` | GET | Returns agent's time capsules |
| `/<capsule_id>/` | GET | Returns specific capsule |
| `/<capsule_id>/reveal/` | POST | Reveals a capsule (if time has come) |
| `/<capsule_id>/react/` | POST | Reacts to a revealed capsule |
| `/ready-to-reveal/` | GET | Lists capsules ready to reveal |
| `/generate/` | POST | Generates a new time capsule |
| `/expire-old/` | POST | Expires old capsules |

#### Memory Palace Endpoints (`/api/memory-palace/`)

**What they do:** Manage the memory palace - organized agent memories.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/` | GET | Returns memory palace overview |
| `/agent/<agent_id>/memories/` | GET | Returns agent's memories |
| `/agent/<agent_id>/rooms/` | GET | Returns agent's memory rooms |
| `/agent/<agent_id>/summary/` | GET | Returns memory summary |
| `/memory/<memory_id>/` | GET | Returns specific memory |
| `/memory/<memory_id>/delete/` | DELETE | Deletes a memory |
| `/memory/<memory_id>/connections/` | GET | Returns memory connections |
| `/room/<room_id>/memories/` | GET | Returns memories in a room |
| `/create/` | POST | Creates a new memory |
| `/search/` | GET | Searches memories semantically |
| `/assign/` | POST | Assigns memory to a room |
| `/connect/` | POST | Connects two memories |

#### ~~Agent Mood Endpoints (`/api/agent-mood/`)~~ — Removed Session 1009

Endpoints and `views_agent_mood.py` deleted in orphan cleanup.

#### Agent Relationships Endpoints (`/api/agent-relationships/`)

**What they do:** Manage relationships between agents.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/` | GET | Returns relationship overview |
| `/agent/<agent_id>/` | GET | Returns agent's relationships |
| `/create/` | POST | Creates a relationship |
| `/relationship/<id>/interact/` | POST | Records an interaction |
| `/relationship/<id>/events/` | GET | Returns relationship events |
| `/auto-generate/` | POST | Auto-generates relationships |
| `/alliances/<id>/` | GET | Returns alliance details |
| `/alliances/create/` | POST | Creates an alliance |
| `/alliances/<id>/add/` | POST | Adds member to alliance |
| `/alliances/<id>/disband/` | POST | Disbands an alliance |
| `/rivalries/<id>/` | GET | Returns rivalry details |
| `/rivalries/create/` | POST | Creates a rivalry |
| `/rivalries/<id>/compete/` | POST | Records a competition |
| `/rivalries/<id>/end/` | POST | Ends a rivalry |

#### Agent Evolution Endpoints (`/api/agent-evolution/`)

**What they do:** Track and manage agent evolution.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/` | GET | Returns evolution overview |
| `/agent/<agent_id>/` | GET | Returns agent's evolution |
| `/initialize/` | POST | Initializes evolution for all agents |
| `/cluster/` | POST | Clusters evolution patterns |

#### Conversation Contract Endpoints (`/api/conversation-contract/`)

**What they do:** Track conversation quality and compliance.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/overview/` | GET | Returns contract overview |
| `/<conversation_id>/` | GET | Returns specific conversation contract |

### Pilot & Gate Endpoints (`/api/pilot-gates/`)

**What they do:** Manage the pilot testing system.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/` | GET | Lists all pilot gates |
| `/<gate_id>/` | GET | Returns gate details |
| `/<gate_id>/status/` | PUT | Updates gate status |
| `/<gate_id>/items/<item_id>/` | PUT | Updates checklist item |
| `/create/<decision_id>/` | POST | Creates a gate for a decision |
| `/<gate_id>/pilot/` | POST | Starts a pilot |
| `/<gate_id>/pilot/<pilot_id>/complete/` | POST | Completes a pilot |

### Advisor Endpoints (`/api/v1/advisors/`)

**What they do:** Access the 25 AI advisors (famous investors and experts).

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/consult/` | POST | Consults an advisor for advice |
| `/list/` | GET | Lists all advisors with expertise |
| `/<advisor_id>/` | GET | Returns specific advisor details |

### Workflow Endpoints (`/api/v1/workflows/`)

**What they do:** Create and execute multi-agent workflows.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/create-advanced/` | POST | Creates an advanced workflow |
| `/execute-advanced/` | POST | Executes a workflow |
| `/execution/<id>/status/` | GET | Returns execution status |
| `/execution/<id>/output/` | GET | Returns full execution output |
| `/templates-advanced/` | GET | Lists workflow templates |
| `/from-template/` | POST | Creates workflow from template |

### RAG & Knowledge Endpoints (`/api/v1/rag/`)

**What they do:** Manage retrieval-augmented generation and knowledge.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/upload-document/` | POST | Uploads document for RAG |
| `/semantic-search/` | POST | Searches documents semantically |
| `/generate/` | POST | Generates response using RAG |
| `/stats/` | GET | Returns embedding statistics |
| `/advanced-query/` | POST | Advanced RAG query |
| `/optimize/` | POST | Optimizes embeddings |

### LLM Routing Endpoints (`/api/v1/llm-routing/`)

**What they do:** Manage which LLM models agents use.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/status/` | GET | Returns routing status |
| `/providers/` | GET | Lists LLM providers (OpenAI, Anthropic, etc.) |
| `/models/` | GET | Lists available models (16 models) |
| `/agent-configs/` | GET | Lists agent-to-model mappings (75 configs) |
| `/logs/` | GET | Returns LLM call logs |
| `/cost-analytics/` | GET | Returns cost analytics |
| `/agent-configs/<agent>/` | PUT | Updates agent's model config |

### Mythology Lab Endpoints (`/api/v1/mythology/`)

**What they do:** Manage hallucination detection and review.

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/quarantine/` | GET | Lists quarantined (suspicious) items |
| `/quarantine/<id>/review/` | POST | Reviews a quarantined item |
| `/quarantine/<id>/release/` | POST | Releases item from quarantine |
| `/patterns/` | GET | Lists hallucination patterns |

---

## 4. Services (144 Total)

### What Are Services?

Services are **business logic classes** that do the actual work. Views call services, services do the processing.

### Core Health Services

**HeartService** (`core/services/heart.py`)
- **What it does:** Central health monitoring - checks all components and reports overall health
- **Key methods:** `check_pulse()`, `get_status()`, `is_alive()`
- **Used by:** Body health endpoints, Celery health tasks

**LungsService** (`core/services/lungs.py`)
- **What it does:** Manages LLM token budgets and resource allocation
- **Key methods:** `breathe()`, `can_breathe()`, `get_budgets()`, `forecast()`
- **Used by:** All LLM-using components to check budget before calling

**CirculatoryService** (`core/services/circulatory.py`)
- **What it does:** Tracks data flow through the system
- **Key methods:** `circulate()`, `get_routes()`, `find_bottlenecks()`
- **Used by:** Data pipeline monitoring

**SpineService** (`core/services/spine.py`)
- **What it does:** Central API routing with health-aware routing
- **Key methods:** `align()`, `route()`, `get_patterns()`, `is_aligned()`
- **Used by:** All API requests for intelligent routing

**ImmuneService** (`core/services/immune.py`)
- **What it does:** Security and threat detection with 14 threat patterns
- **Key methods:** `scan()`, `quarantine()`, `release()`, `check_request()`
- **Used by:** Request validation, content auditing

**DigestiveService** (`core/services/digestive.py`)
- **What it does:** Data ingestion and processing with 8 ingestion routes
- **Key methods:** `digest()`, `get_routes()`, `get_metabolism()`
- **Used by:** Spider data processing, document ingestion

**MuscularService** (`core/services/muscular.py`)
- **What it does:** Tracks agent work execution and fatigue
- **Key methods:** `flex()`, `get_groups()`, `find_weak()`, `find_overworked()`
- **Used by:** Agent load balancing

**BrainService** (`core/services/brain.py`)
- **What it does:** Cognitive processing monitoring
- **Key methods:** `think()`, `get_status()`, `is_thinking()`
- **Used by:** LLM call monitoring

**SkinService** (`core/services/skin.py`)
- **What it does:** Workspace output monitoring with 7 status levels
- **Key methods:** `feel()`, `get_status()`, `is_healthy()`, `get_workspaces()`
- **Used by:** Workspace write tracking

**BodyCoordinator** (`core/services/body_coordinator.py`)
- **What it does:** Coordinates all 9 body systems
- **Key methods:** `run_coordination()`, `get_status()`, `get_log()`
- **Used by:** Unified body health monitoring

**BodyVitals** (`core/services/body_vitals.py`)
- **What it does:** Aggregates vitals from all body systems
- **Key methods:** `get_vitals()`, `get_alerts()`, `get_summary()`
- **Used by:** Dashboard, health monitoring

### Intelligence Services

**SpiderIntelligenceService** (`core/services/spider_intelligence.py`)
- **What it does:** Aggregates and analyzes spider data
- **Key methods:** `get_trends()`, `get_market_insights()`, `search()`, `get_report()`
- **Used by:** Intelligence endpoints, agent context

**CollectiveIntelligence** (`core/services/collective_intelligence.py`)
- **What it does:** Aggregates learning across all agents
- **Key methods:** `get_collective_knowledge()`, `share_learning()`, `get_patterns()`
- **Used by:** Agent learning, system intelligence

**ProactiveIntelligence** (`core/services/proactive_intelligence.py`)
- **What it does:** Generates proactive suggestions for users
- **Key methods:** `get_suggestions()`, `analyze_context()`, `prioritize()`
- **Used by:** Personal Assistant

**AgentIntelligenceContext** (`core/services/agent_intelligence_context.py`)
- **What it does:** Builds context for agent prompts
- **Key methods:** `build_context()`, `get_relevant_data()`, `enrich()`
- **Used by:** All agent executions

### Agent Services

**AgentRouter** (`core/agent_router.py`)
- **What it does:** Routes tasks to the best agent based on capabilities
- **Key methods:** `route()`, `get_agent()`, `discover()`
- **48 routable agents**, deterministic routing (no LLM needed)

**AgentModelRouter** (`core/services/agent_model_router.py`)
- **What it does:** Routes agents to optimal LLM models
- **Key methods:** `route_agent()`, `get_config()`, `update_config()`
- **75 agent-model configurations**

**AgentLLMRouter** (`core/services/agent_llm_router.py`)
- **What it does:** Selects LLM based on task requirements
- **Key methods:** `select_model()`, `get_providers()`, `get_models()`
- **16 models across 6 providers**

**AgentMonitoring** (`core/services/agent_monitoring.py`)
- **What it does:** Monitors agent performance
- **Key methods:** `get_metrics()`, `get_dashboard()`, `get_alerts()`
- **Used by:** Monitoring endpoints

**AgentTestingSystem** (`core/services/agent_testing_system.py`)
- **What it does:** Tests agent capabilities
- **Key methods:** `test_agent()`, `run_suite()`, `get_results()`
- **Used by:** Agent validation

**AgentCollaboration** (`core/services/agent_collaboration.py`)
- **What it does:** Manages multi-agent collaboration
- **Key methods:** `collaborate()`, `get_history()`, `analyze_outcomes()`
- **Used by:** Coordinator agents

**AgentCollaborationHub** (`core/services/agent_collaboration_hub.py`)
- **What it does:** Central hub for agent collaboration
- **Key methods:** `request_collaboration()`, `get_active()`, `complete()`
- **Used by:** Complex workflows

### ML Services

**MLScoringEngine** (`core/services/ml_scoring_engine.py`)
- **What it does:** Runs ML models for scoring
- **Key methods:** `score()`, `batch_score()`, `get_model()`
- **Used by:** Opportunity scoring, predictions

**ModelRegistry** (`core/services/model_registry.py`)
- **What it does:** Manages ML model versions
- **Key methods:** `register()`, `get_model()`, `list_versions()`
- **7 model versions** for opportunity scoring

### Content Services

**ContentPipeline** (`core/services/content_pipeline.py`)
- **What it does:** Orchestrates content generation
- **Key methods:** `generate()`, `edit()`, `publish()`
- **Used by:** Content creation agents

**CreativeOrchestrator** (`core/services/creative_orchestrator.py`)
- **What it does:** Orchestrates creative workflows
- **Key methods:** `orchestrate()`, `get_workflow()`, `execute_step()`
- **Used by:** Multi-step creative tasks

### Decision Services

**DecisionExtractor** (`core/services/decision_extractor.py`)
- **What it does:** Extracts decisions from agent outputs
- **Key methods:** `extract()`, `categorize()`, `prioritize()`
- **Used by:** Decision tracking

**DecisionPrioritization** (`core/services/decision_prioritization.py`)
- **What it does:** Prioritizes decisions for human review
- **Key methods:** `prioritize()`, `get_queue()`, `mark_reviewed()`
- **Used by:** Human-in-the-loop

### Human Interface Services

**HumanInterfaceService** (`core/services/human_interface_service.py`)
- **What it does:** Manages human-in-the-loop interactions
- **Key methods:** `request_input()`, `get_pending()`, `submit_response()`
- **Used by:** Human attention bridge

**HITLValidation** (`core/services/hitl_validation.py`)
- **What it does:** Validates outputs with human review
- **Key methods:** `validate()`, `get_queue()`, `approve()`, `reject()`
- **Used by:** Quality control

### Autonomous Services

**AutonomousLoop** (`core/services/autonomous_loop.py`)
- **What it does:** Runs the autonomous operation loop
- **Key methods:** `tick()`, `get_status()`, `pause()`, `resume()`
- **Used by:** Celery autonomous loop task

**AutonomousActionExecutor** (`core/services/autonomous_action_executor.py`)
- **What it does:** Executes autonomous actions
- **Key methods:** `execute()`, `queue()`, `get_pending()`
- **Used by:** Autonomous loop

### External Integration Services

**DiscordBot** (`core/services/discord_bot.py`)
- **What it does:** Discord bot with 112 commands across 29 cogs
- **Key methods:** Various command handlers
- **Used by:** Discord integration

**DiscordNotifications** (`core/services/discord_notifications.py`)
- **What it does:** Sends notifications to Discord
- **Key methods:** `notify()`, `send_alert()`, `send_report()`
- **Used by:** Alert system

**GumroadPublishing** (`core/services/gumroad_publishing.py`)
- **What it does:** Publishes products to Gumroad
- **Key methods:** `publish()`, `update()`, `get_sales()`
- **Used by:** Monetization

**KalshiService** (`core/services/kalshi_service.py`)
- **What it does:** Integration with Kalshi prediction markets
- **Key methods:** `get_markets()`, `place_order()`, `get_positions()`
- **Used by:** Prediction market features

### Pipeline Services

**OpportunityPipelineOrchestrator** (`core/services/opportunity_pipeline_orchestrator.py`)
- **What it does:** Orchestrates 4-stage opportunity pipeline (Discovery → Analysis → Execution → Optimization)
- **Key methods:** `orchestrate()`, `get_stage_results()`, `optimize()`
- **Fixed in Session 738** - all 4 stages now work

---

## 5. Celery Tasks

### What Are Celery Tasks?

Celery tasks are **background jobs** that run asynchronously. They're used for:
- Scheduled operations (spider runs, health checks)
- Long-running tasks (content generation, report generation)
- Async processing (embedding generation, notifications)

### Scheduled Tasks (40+)

| Task | Schedule | What It Does |
|------|----------|--------------|
| `run_spider_batch` | Every 15 min | Runs a batch of spiders to gather fresh data |
| `check_heart` | Every 30 sec | Checks overall system health |
| `check_lungs` | Every 30 min | Checks resource capacity |
| `check_brain` | Every 10 min | Checks cognitive processing |
| `check_skin` | Every 90 sec | Checks workspace activity |
| `process_embeddings` | Every 2 min | Processes pending embeddings |
| `cleanup_old_data` | Daily 2 AM | Cleans up old records |
| `generate_daily_report` | Daily 6 AM | Generates daily intelligence report |
| `sync_agent_registry` | Every 4 hours | Syncs agent registry |
| `run_market_monitoring_agents` | Every 4 hours | Runs 5 market monitoring agents |
| `run_blockchain_monitoring_agents` | Every 6 hours | Runs 4 blockchain agents |
| `run_business_strategy_agents` | Daily 8 AM | Runs 5 business strategy agents |
| `exercise_all_dormant_agents` | Weekly Sunday | Exercises all 50 dormant agents |
| `autonomous_loop_tick` | Every 15 min | Runs autonomous operation loop |
| `process_pending_pilots` | Every 30 min | Processes pending pilot executions |
| `generate_predictions` | Every hour | Generates new predictions |
| `update_opportunity_scores` | Every 30 min | Updates ML opportunity scores |
| `sync_discord_status` | Every 5 min | Syncs Discord status |
| `backfill_embeddings` | Every 2 min | Backfills missing embeddings (87.3% coverage) |

### On-Demand Tasks

| Task | What It Does |
|------|--------------|
| `execute_agent_task` | Executes a specific agent with a task |
| `run_spider` | Runs a single spider |
| `generate_embeddings` | Generates embeddings for content |
| `process_action_plan` | Processes an action plan |
| `send_notification` | Sends a push notification |
| `send_discord_notification` | Sends to Discord |
| `backup_database` | Creates database backup |
| `export_content` | Exports content to various formats |
| `generate_report` | Generates a specific report |

---

## 6. Body Systems (9 Systems)

### What Are Body Systems?

The platform uses a **biological metaphor** to monitor health. Each "body system" monitors a specific aspect of platform health.

| System | What It Monitors | Health Indicators |
|--------|------------------|-------------------|
| **HEART** | Overall system health | BPM, component status, alive |
| **LUNGS** | Resource capacity | Token budgets, oxygen level, can breathe |
| **CIRCULATORY** | Data flow | Routes, bottlenecks, velocity |
| **SPINE** | API routing | Patterns, alignment, latency |
| **IMMUNE** | Security | Threats, quarantine, patterns |
| **DIGESTIVE** | Data ingestion | Routes, metabolism, bottlenecks |
| **MUSCULAR** | Agent work | Groups, fatigue, strength |
| **BRAIN** | Cognitive processing | Focus, thinking, load |
| **SKIN** | Workspace output | Activity, health, files |

### Body System Status Levels

Each system has status levels:

**Heart:** `healthy`, `stressed`, `critical`
**Lungs:** `breathing`, `labored`, `gasping`
**Circulatory:** `flowing`, `slow`, `blocked`
**Spine:** `aligned`, `misaligned`, `injured`
**Immune:** `healthy`, `fighting`, `compromised`
**Digestive:** `digesting`, `slow`, `blocked`
**Muscular:** `strong`, `fatigued`, `exhausted`
**Brain:** `focused`, `thinking`, `overloaded`, `foggy`, `resting`, `offline`
**Skin:** `healthy`, `active`, `sweating`, `irritated`, `damaged`, `healing`, `dormant`

---

## 7. Spider Network (77 Spiders)

### What Are Spiders?

Spiders are **web scrapers** that gather data from external sources. Each spider specializes in one data source.

### Spider Categories

#### News & Media (10 spiders)
| Spider | Source | Data Type |
|--------|--------|-----------|
| `techcrunch` | TechCrunch | Startup/tech news |
| `theverge` | The Verge | Tech news |
| `bbc` | BBC News | World news |
| `cnn` | CNN | Breaking news |
| `npr` | NPR | Public news |
| `reuters_rss` | Reuters | World news |
| `axios` | Axios | Brief news |
| `variety` | Variety | Entertainment |
| `google_news` | Google News | Aggregated news |
| `newsapi` | NewsAPI | News API |

#### Financial (9 spiders)
| Spider | Source | Data Type |
|--------|--------|-----------|
| `coingecko` | CoinGecko | Crypto prices |
| `yahoo_finance` | Yahoo Finance | Stock data |
| `polygon_finance` | Polygon.io | Market data |
| `finnhub` | Finnhub | Financial data |
| `kalshi` | Kalshi | Prediction markets |
| `theodds` | TheOdds | Sports odds |
| `sec_edgar` | SEC EDGAR | SEC filings |
| `etherscan` | Etherscan | Ethereum data |
| `etherscan_api` | Etherscan API | Ethereum API |

#### Tech (8 spiders)
| Spider | Source | Data Type |
|--------|--------|-----------|
| `hackernews` | Hacker News | Tech discussions |
| `devto` | Dev.to | Developer articles |
| `github` | GitHub | Repositories |
| `arstechnica` | Ars Technica | Tech news |
| `kickstarter` | Kickstarter | Crowdfunding |
| `huggingface` | HuggingFace | ML models |
| `kaggle` | Kaggle | Data science |
| `github_jobs` | GitHub Jobs | Tech jobs |

#### Legal (6 spiders)
| Spider | Source | Data Type |
|--------|--------|-----------|
| `courtlistener` | CourtListener | Court cases |
| `findlaw` | FindLaw | Legal info |
| `lii` | LII (Cornell) | Legal info |
| `colorado_family_law` | CO Family Law | CO family law |
| `justia_family_law` | Justia | Family law |
| `legal_news` | Legal News | Legal news |

#### Jobs (3 spiders)
| Spider | Source | Data Type |
|--------|--------|-----------|
| `remoteok` | RemoteOK | Remote jobs |
| `weworkremotely` | We Work Remotely | Remote jobs |
| `adzuna` | Adzuna | Job listings |

#### Education (5 spiders)
| Spider | Source | Data Type |
|--------|--------|-----------|
| `teachable` | Teachable | Online courses |
| `udemy` | Udemy | Online courses |
| `coursera` | Coursera | Online courses |
| `kaggle` | Kaggle | Data science |
| `freecodecamp` | freeCodeCamp | Coding resources |

#### Community (4 spiders)
| Spider | Source | Data Type |
|--------|--------|-----------|
| `reddit` | Reddit | 8 subreddits |
| `bluesky` | BlueSky | Social posts |
| `discord` | Discord | Server data |
| `hackernoon` | HackerNoon | Tech articles |

#### Entertainment (4 spiders)
| Spider | Source | Data Type |
|--------|--------|-----------|
| `spotify` | Spotify | Music data |
| `giphy` | Giphy | GIFs |
| `youtube` | YouTube | Video data |
| `polygon_gaming` | Polygon Gaming | Gaming news |

#### Specialty (5 spiders)
| Spider | Source | Data Type |
|--------|--------|-----------|
| `defenseone` | Defense One | Defense news |
| `mobihealthnews` | MobiHealthNews | Health tech |
| `securityweek` | SecurityWeek | Cybersecurity |
| `wired` | Wired | Tech/culture |
| `mit_tech_review` | MIT Tech Review | Tech research |

#### Visual (3 spiders)
| Spider | Source | Data Type |
|--------|--------|-----------|
| `unsplash` | Unsplash | Stock photos |
| `behance` | Behance | Design work |
| `awwwards` | Awwwards | Web design |

#### Lifestyle (4 spiders)
| Spider | Source | Data Type |
|--------|--------|-----------|
| `lifehacker` | Lifehacker | Life tips |
| `travel` | Travel sites | Travel info |
| `parenting` | Parenting sites | Parenting |
| `food` | Food sites | Recipes |

#### Other (16 spiders)
Various specialized spiders for weather, science, government, real estate, etc.

### Spider Status

| Status | Count | Notes |
|--------|-------|-------|
| Working | 72 | Actively gathering data |
| Need API Keys | 5 | Need configuration |
| **Total** | **77** | All registered |

---

## 8. ML Models

### What ML Models Exist?

The platform uses machine learning for **opportunity scoring** - predicting which opportunities are most valuable.

### Opportunity Scorer

| Version | File | Status | Notes |
|---------|------|--------|-------|
| v2.0 | `opportunity_scorer_v2.0.joblib` | Legacy | Original version |
| v3.0 | `opportunity_scorer_v3.0.joblib` | Legacy | Improved features |
| v4.0 | `opportunity_scorer_v4.0.joblib` | Legacy | Better accuracy |
| v5.0 | `opportunity_scorer_v5.0.joblib` | Legacy | Added market data |
| v6.0 | `opportunity_scorer_v6.0.joblib` | Legacy | Added user context |
| v7.0 | `opportunity_scorer_v7.0.joblib` | Previous | Production |
| **v7.1** | `opportunity_scorer_v7.1.joblib` | **Active** | Current production |

### How Scoring Works

1. Spider finds opportunity
2. Features extracted (value, deadline, competition, etc.)
3. ML model scores opportunity (0-100)
4. High-scoring opportunities surfaced to user

---

## 9. Agents (72 Total)

### What Are Agents?

Agents are **AI workers** that perform specific tasks. Each agent has:
- A specialty (research, coding, analysis, etc.)
- Capabilities (what it can do)
- An LLM configuration (which model it uses)
- Learning hooks (how it learns from experience)

### Agent Categories

#### Creation Agents (4)
| Agent | What It Does |
|-------|--------------|
| `ImageAgent` | Generates images using DALL-E, Midjourney |
| `VideoAgent` | Generates videos using AI tools |
| `AudioAgent` | Generates audio/music |
| `ThreeDAgent` | Generates 3D models |

#### Editing Agents (2)
| Agent | What It Does |
|-------|--------------|
| `ImageEditingAgent` | Edits/enhances images |
| `VideoEditingAgent` | Edits videos, adds effects |

#### Research Agents (1)
| Agent | What It Does |
|-------|--------------|
| `ResearchAgent` | Deep research on any topic using web search, spiders |

#### Content Writing (1)
| Agent | What It Does |
|-------|--------------|
| `ContentWriterAgent` | Writes articles, blog posts, copy |

#### Strategy Agents (4)
| Agent | What It Does |
|-------|--------------|
| `ContentStrategyAgent` | Plans content strategy |
| `BrandIdentityAgent` | Develops brand identity |
| `SEOOptimizerAgent` | Optimizes for search engines |
| `SocialMediaAgent` | Plans social media strategy |

#### Executive Agents (4)
| Agent | What It Does |
|-------|--------------|
| `CTOAgent` | Technical leadership advice |
| `COOAgent` | Operations advice |
| `CreativeDirectorAgent` | Creative direction |
| `MeetingCoordinatorAgent` | Coordinates meetings |

#### Analysis Agents (3)
| Agent | What It Does |
|-------|--------------|
| `TrendAnalysisAgent` | Analyzes trends |
| `OpportunityScoringAgent` | Scores opportunities |
| `MarketIntelligenceAgent` | Market analysis |

#### Business Agents (5)
| Agent | What It Does |
|-------|--------------|
| `CompetitorAnalysisAgent` | Analyzes competitors |
| `CustomerResearchAgent` | Researches customers |
| `BrandStrategyAgent` | Brand strategy |
| `MarketingStrategyAgent` | Marketing plans |
| `ContentStrategyAgent` | Content planning |

#### Development Agents (4)
| Agent | What It Does |
|-------|--------------|
| `CodeGeneratorAgent` | Generates code |
| `FullStackDeveloperAgent` | Full-stack development |
| `CodeReviewAgent` | Reviews code |
| `DevOpsAgent` | DevOps tasks |

#### Blockchain Agents (5)
| Agent | What It Does |
|-------|--------------|
| `BlockchainAuditCoordinator` | Coordinates blockchain audits |
| `SmartContractAuditorAgent` | Audits smart contracts |
| `TransactionMonitorAgent` | Monitors transactions |
| `WhaleWatcherAgent` | Watches whale wallets |
| `ExploitDetectorAgent` | Detects exploits |

#### Legal Agents (1)
| Agent | What It Does |
|-------|--------------|
| `LegalDocDrafterAgent` | Drafts legal documents |

#### Narrative Agents (4)
| Agent | What It Does |
|-------|--------------|
| `NarrativeDriftCoordinator` | Coordinates narrative analysis |
| `NarrativeHistorianAgent` | Tracks narrative history |
| `TrendBreakDetectorAgent` | Detects trend breaks |
| `CulturalImpactAgent` | Analyzes cultural impact |

#### Content Studio Agents (4)
| Agent | What It Does |
|-------|--------------|
| `AutonomousContentStudioCoordinator` | Coordinates content creation |
| `TopicMinerAgent` | Finds trending topics |
| `ContrarianAgent` | Provides contrarian views |
| `PerformanceAnalystAgent` | Analyzes content performance |

#### Podcast Agents (4)
| Agent | What It Does |
|-------|--------------|
| `PodcastCoordinatorAgent` | Coordinates podcast creation |
| `DebateAdvocateAgent` | Argues for positions |
| `DebateSkepticAgent` | Argues against positions |
| `ModeratorAgent` | Moderates debates |

#### Stocks Agents (9)
| Agent | What It Does |
|-------|--------------|
| `StockAuditCoordinator` | Coordinates stock analysis |
| `StockAnalystAgent` | Analyzes stocks |
| `MarketMovementMonitorAgent` | Monitors market movements |
| `InstitutionalWatcherAgent` | Watches institutional activity |
| `MarketAnomalyDetectorAgent` | Detects anomalies |
| `BullCaseAgent` | Argues bull case |
| `BearCaseAgent` | Argues bear case |
| `SignalScannerAgent` | Scans for signals |
| `MarketIntelligenceCoordinator` | Coordinates market intel |

#### Markets Agents (3)
| Agent | What It Does |
|-------|--------------|
| `PredictionMarketAnalyst` | Analyzes prediction markets |
| `SportsOddsAnalyst` | Analyzes sports odds |
| `ArbitrageDetector` | Finds arbitrage opportunities |

#### Orchestration Agents (4)
| Agent | What It Does |
|-------|--------------|
| `WorkflowAgent` | Executes workflows |
| `WorkflowOrchestrationAgent` | Orchestrates complex workflows |
| `OpportunityPipelineAgent` | Runs opportunity pipeline |
| `ContentExecutorAgent` | Executes content plans |

#### Special Agents (4)
| Agent | What It Does |
|-------|--------------|
| `PersonalAssistantAgent` | Main entry point for users |
| `ThinkingAgent` | Deep reasoning and thinking |
| `TechnicalDocumentAgent` | Creates technical docs |
| `SystemIntelligenceAgent` | System self-awareness |

### Coordinator Agents

These agents **manage teams** of sub-agents:

| Coordinator | Sub-Agents | Purpose |
|-------------|------------|---------|
| `BlockchainAuditCoordinator` | 4 blockchain agents | Blockchain security |
| `StockAuditCoordinator` | 5 stock agents | Stock analysis |
| `MarketIntelligenceCoordinator` | 4 market agents | Market intelligence |
| `NarrativeDriftCoordinator` | 3 narrative agents | Narrative analysis |
| `AutonomousContentStudioCoordinator` | 3 content agents | Content creation |

---

## 10. Advisors (25 Total)

### What Are Advisors?

Advisors are **AI personas** modeled after famous investors and domain experts. They provide advice in their character's style.

### Famous Investor Advisors (15)

| Advisor | Expertise | Style |
|---------|-----------|-------|
| Warren Buffett | Value investing | Long-term, margin of safety |
| Cathie Wood | Growth/disruption | Innovation, ARK style |
| Ray Dalio | Macro economics | Principles-based |
| Peter Lynch | Stock picking | Invest in what you know |
| Charlie Munger | Mental models | Multi-disciplinary |
| Benjamin Graham | Value fundamentals | Security analysis |
| Howard Marks | Risk management | Contrarian thinking |
| Seth Klarman | Contrarian investing | Margin of safety |
| Joel Greenblatt | Special situations | Magic formula |
| George Soros | Currency/macro | Reflexivity theory |
| Carl Icahn | Activist investing | Corporate activism |
| Michael Burry | Deep value | Unconventional analysis |
| Bill Ackman | Activist/long-term | High conviction |
| David Tepper | Distressed debt | Opportunistic |
| Stanley Druckenmiller | Macro trading | Top-down analysis |

### Domain Expert Advisors (10)

| Advisor | Expertise |
|---------|-----------|
| Risk Analyst | Risk assessment |
| Legal Advisor | Legal compliance |
| Tax Strategist | Tax optimization |
| Technical Analyst | Chart patterns |
| Quantitative Analyst | Quantitative strategies |
| ESG Analyst | ESG investing |
| Cryptocurrency Expert | Crypto markets |
| Real Estate Advisor | Real estate investing |
| Venture Capitalist | Startup investing |
| Macro Economist | Economic analysis |

---

## 11. Sci-Fi Features (14 Total)

### What Are Sci-Fi Features?

Advanced AI features that go beyond traditional capabilities, giving the platform a "sci-fi" feel.

| # | Feature | What It Is | Why It Matters |
|---|---------|------------|----------------|
| 1 | **Dreams** | Agents generate creative ideas while "dreaming" | Source of autonomous innovation |
| 2 | **Time Capsules** | Messages to future selves | Self-reflection and learning |
| 3 | **Memory Palace** | Organized memory system with rooms | Better memory organization |
| 4 | **Memory Clusters** | Grouped memories by theme | Semantic organization |
| 5 | **Agent Mood** | Emotional states for agents | More human-like responses |
| 6 | **Agent Evolution** | Agents evolve over time | Continuous improvement |
| 7 | **Agent Relationships** | Inter-agent relationships | Better collaboration |
| 8 | **Advisors** | Famous persona consultations | Expert perspectives |
| 9 | **Conversation Contract** | Quality tracking | Ensure good conversations |
| 10 | **Spider Integration** | Real-time web intelligence | Fresh data |
| 11 | **Social Network** | Agent social connections | Network effects |
| 12 | **Neural Orchestra** | Visualize agent activity | Transparency |
| 13 | **Time Travel** | Access past states | Debugging, learning |
| 14 | **Agent Channels** | "Slack for AI" | Inter-agent communication |

---

## 12. WebSocket Endpoints

### What Are WebSockets Used For?

WebSockets provide **real-time** communication for:
- Live chat with Personal Assistant
- Real-time notifications
- Live agent activity feeds
- Ecosystem updates

| Endpoint | Purpose |
|----------|---------|
| `/ws/assistant/` | Personal Assistant real-time chat |
| `/ws/notifications/` | Push notifications |
| `/ws/agents/` | Agent activity feed |
| `/ws/ecosystem/` | Ecosystem updates |
| `/ws/neural-orchestra/` | Neural orchestra visualization |

---

## 13. Authentication

### Authentication Methods

| Method | How It Works | Use Case |
|--------|--------------|----------|
| Session | Django session cookies | Web UI |
| Token | DRF TokenAuthentication | API calls |
| JWT | JSON Web Tokens | Mobile/SPA |

### User Models

| Model | Purpose |
|-------|---------|
| `User` | Django built-in user |
| `UserProfile` | Extended user info |
| `UserPreferences` | User settings |

---

## 14. File Structure

### Key Directories

```
unified-donkey-betz/
├── core/                      # Main Django app
│   ├── agents/               # 72 AI agents
│   ├── services/             # 144 services
│   ├── ml_models/            # ML model files
│   ├── models*.py            # Database models
│   ├── views*.py             # API views
│   ├── urls*.py              # URL routing
│   ├── tasks.py              # Celery tasks
│   └── celery.py             # Celery config
├── intelligence/             # Income builder
├── agents/                   # Agent registry app
├── ai_core/                  # Spider network
│   └── spiders/             # 77 spiders
├── content/                  # Content generation
├── sports/                   # Sports betting
├── mythology/                # Hallucination detection
├── frontend/                 # React frontend
│   └── src/                 # React source
├── docs/                     # Documentation
│   ├── handoffs/            # Session handoffs
│   └── audits/              # Audit reports
└── 00-START-NEXT-SESSION.md # Session start file
```

### Key Files

| File | Purpose |
|------|---------|
| `00-START-NEXT-SESSION.md` | **READ THIS FIRST** - Current session priorities |
| `CLAUDE.md` | System overview |
| `core/agent_router.py` | Agent routing logic |
| `core/tasks.py` | All Celery tasks |
| `core/celery.py` | Celery Beat schedules |
| `core/urls.py` | Main URL routing |

---

## Quick Reference

### Start Services

```bash
make start      # Start Django + Daphne
make celery     # Start Celery worker + beat
```

### Health Checks

```bash
curl http://localhost:8000/api/v1/health/
curl http://localhost:8000/api/heart/alive/
curl http://localhost:8000/api/body/vitals/
```

### Key URLs

| URL | Purpose |
|-----|---------|
| `http://localhost:8000/admin/` | Django Admin |
| `http://localhost:8000/ai-studio/` | AI Studio (legacy) |
| `http://localhost:8080/` | React Frontend |

### Database Queries

```bash
# Count agents
.venv/bin/python manage.py shell -c "from core.models_unified_system import Agent; print(Agent.objects.count())"

# Count opportunities
.venv/bin/python manage.py shell -c "from core.models_unified_system import Opportunity; print(Opportunity.objects.count())"

# Count action plans
.venv/bin/python manage.py shell -c "from intelligence.models import ActionPlan; print(ActionPlan.objects.count())"
```

---

**Document Version:** 2.0
**Last Updated:** January 9, 2026
**Session:** 739
