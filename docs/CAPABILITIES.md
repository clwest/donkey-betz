<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_WHAT_IT_IS.md`](/docs/PLATFORM_WHAT_IT_IS.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

# Platform Capabilities

**Last Updated:** Session 858 (January 28, 2026) - Added User Context Injection for personalized agent responses

---

## System Overview (refreshed Session 1100, 2026-04-26)

| Component | Count | Details |
|-----------|-------|---------|
| **Total Agents** | **306** | 83 AGENT_MAP (73 enabled, 8 rerouted, 2 blocked) + 223 DB persona-eligible Agent rows |
| **Total Spiders** | **80** | All working; 41 categories |
| **PA Tools** | **101 schemas / 166 handlers** | 6 gateway tools, 8 enrichment services |
| **Database Models** | **570** | Concrete Django models across 23 apps (PostgreSQL + pgvector) |
| **Celery Tasks** | **365** | + 305 PeriodicTask rows (258 enabled, 47 disabled by Session 1089 governor) |
| **Services** | **~300 modules / 112 classes** | Module-count vs `*Service` class-count |
| **Discord Commands** | **144** | 96 `@*.command` + 48 `@app_commands.command` across 25 Cogs |
| **Advisors** | **32** | 10 named figures + 22 domain specialists |
| **Sci-Fi Features** | **14** | All active (Session 567 cleanup) |
| **HEART Service** | **2 models** | HeartBeat, ComponentStatus - monitors 6 body parts |
| **LUNGS Service** | **3 models** | Budget, BreathCycle, RespiratoryStatus - 6 default budgets |
| **SKIN Layer** | **3 models** | ProjectWorkspace, WorkspaceOperation, WorkspaceContext |
| **WORKSPACE_AWARE_AGENTS** | **20** | Development, Content, Strategy, Research, Analysis, Legal |
| **USER_CONTEXT_ENHANCED** | **4** | ContentWriter, Research, StockAnalyst, SportsOddsAnalyst (Session 858) |

---

## Quick Reference

| Category | Count | Status |
|----------|-------|--------|
| Image Generation Features | 13 | Production |
| Video Generation Features | 5 | Production |
| Audio Generation Features | 2 | Production |
| **AI Podcast Studio** | **4 Agents + TTS Audio** | **ACTIVE (Session 652) - 1 show, 1 episode** |
| **Campaign Orchestrator** | **Marketing Campaigns** | **ACTIVE (Session 652) - 1 campaign, 16 deliverables** |
| Video Editing Operations | 14 | Production |
| 3D Generation | Complete | Production |
| Character Training | 3 | Production |
| Workflows | 6 | Production |
| **Spiders** | **77** | **Active (72 working)** |
| **Agents** | **72** | **48 routable, 24 sub-agents** |
| Advisors | 25 | Production |
| Sci-Fi Features | 14 | All Active |
| Style Presets | 80+ | Built-in |
| Multi-Agent Orchestration | Yes | Production |
| Collective Intelligence Search | Yes | Production |
| **Legal Assistant** | **1** | **Production** |
| **Document Brain** | **1** | **Production** |
| **OCR PDF Support** | **Yes** | **Production** |
| **Document Threading** | **Yes** | **Production (Session 410)** |
| **Response Session UI** | **Yes** | **Production (Session 410)** |
| **Discord Integration** | **112 Commands + Voice AI** | **Production (Session 567)** |
| **Discord User Linking** | **Yes** | **Production (Session 429)** |
| **Discord Server Setup** | **3 Templates** | **Production (Session 431)** |
| **Discord Client Management** | **4 Commands** | **Production (Session 432)** |
| **Subscription Tiers** | **Free/Pro/Premium** | **Production (Session 438)** |
| **Stripe Integration** | **Subscription Billing** | **Production (Session 438)** |
| **Training Data Collection** | **14 Datasets** | **Production (Session 420)** |
| **Voice Marketplace** | **14 API Endpoints** | **Production (Session 440)** |
| **Content Pipeline** | **6 Tiers ($5-$50K)** | **Production (Session 440)** |
| **Voice Interview** | **Whisper Transcription** | **Production (Session 456)** |
| **User Certifications** | **File Upload + Display** | **Production (Session 457)** |
| **Voice Management UI** | **Add/Preview/Delete Voices** | **Production (Session 457)** |
| **Style Presets UI** | **80+ Organized Options** | **Production (Session 457)** |
| **AI Series Workflow** | **Multi-Episode Content Series** | **Production (Session 445)** |
| **Autonomous Loop** | **SEC + Jobs + Content Monitoring** | **Production (Session 460)** |
| **Blockchain Audit** | **5 Agents + Event Listener** | **Production (Session 461)** |
| **Stock Audit** | **9 Agents + Coordinator** | **Production (Session 461)** |
| **Market Intelligence Desk** | **5 Agents + TTS Briefs + Auto-scheduling** | **Production (Session 465)** |
| **Autonomous Content Studio** | **4 Agents + Internal Debate + Learning Loop** | **Production (Session 466)** |
| **Studio Discord Commands** | **7 Commands (+episode view)** | **Production (Session 469)** |
| **ML Scoring Engine** | **XGBoost + SHAP Explainability** | **Production (Session 470)** |
| **Narrative Drift Detector** | **30 Narratives, 8 Domains, 4 Agents** | **Production (Session 471)** |
| **Provenance & Compliance** | **Blockchain-style Hash Chain** | **Production (Session 472)** |
| **ROI Metrics** | **Conversion Funnel + Attribution** | **Production (Session 472)** |
| **Unified Intelligence Pipeline** | **All 3 Autonomous Systems Connected** | **Production (Session 474)** |
| **19 Autonomous Situations** | **ALL Domains (6) + Event-Driven** | **Production (Session 479-481)** |
| **Event-Driven Triggers** | **29 Types, 34 Defaults, Instant Reaction** | **Production (Session 481)** |
| **Situation Discord Commands** | **4 Commands (list/status/run/alerts)** | **Production (Session 480)** |
| **Celery Beat Schedules** | **53 Automated Tasks** | **Production (Session 567)** |
| **User Context Injection** | **All 74 Agents Personalized** | **Production (Session 858)** |
| **Auto Personal Workspaces** | **On-Demand Creation** | **Production (Session 858)** |
| **Learning Feedback Loop** | **Success Pattern Recording** | **Production (Session 858)** |
| **Betting Dashboard** | **8 Sub-tabs + Push Notifications** | **Production (Session 562)** |
| **Chief of Staff Layer** | **Pro/Con Review Documents** | **Production (Session 555)** |
| **System Intelligence Agent** | **Platform Health & Attention Monitoring** | **Production (Session 663)** |
| **PA Tools** | **82 Tools (+universal_agent_tool)** | **Production (Session 674)** |
| **Boardroom Noise Filter** | **-12% garbage decisions** | **Production (Session 586)** |
| **Pilot Readiness Gate** | **7 APIs + Risk Checklists + Pilot Execution** | **Production (Session 592)** |
| **SKIN Layer** | **Workspace Management + File Writing + Git** | **Production (Session 695)** |
| **HEART Service** | **System Health Monitoring (6 body parts)** | **Production (Session 701)** |
| **LUNGS Service** | **Resource & Capacity Management (6 budgets)** | **Production (Session 702)** |

---

## SKIN Layer - Project Execution System (Session 695)

**The "SKIN" where AI touches reality** - enables all 72 agents to write code and content to real project workspaces with full audit trail and rollback capability.

### Human Body Metaphor (Complete)

| Layer | Component | Purpose |
|-------|-----------|---------|
| **CONSCIOUSNESS** | Human Operator | The self, makes final decisions |
| **EYES/EARS/HANDS** | Human Interface Layer | Attention items, feedback, preferences |
| **BRAIN** | ThinkingAgent | Complex reasoning and evaluation |
| **HEART** | HeartMonitorService | Central health monitoring (Session 701) |
| **NERVOUS SYSTEM (LLM)** | AgentLLMRouter | Routes agents to optimal LLM providers |
| **NERVOUS SYSTEM (ML)** | Agent-Model Router | Routes tasks to ML models |
| **ORGANS** | 72 Specialized Agents | Each handles specific domain tasks |
| **SENSORY INPUTS** | 77 Spiders | Gather real-world data |
| **SKIN** | WorkspaceManager + workspace_tool | **Where AI touches reality** |

### Database Models

| Model | Fields | Purpose |
|-------|--------|---------|
| **ProjectWorkspace** | 23 | Target project directories agents work on |
| **WorkspaceOperation** | 27 | Audit trail of every file/command operation |
| **WorkspaceContext** | 15 | Cached understanding of project structure |

### workspace_tool (12 Actions)

| Action | Description |
|--------|-------------|
| `register` | Register a new project directory |
| `list` | List all user's workspaces |
| `set_active` | Switch active workspace |
| `status` | Get workspace status with tech stack |
| `scan` | Rescan and update workspace context |
| `write` | Write content to a file |
| `read` | Read a file from workspace |
| `git_status` | Get git status |
| `git_commit` | Commit changes with agent attribution |
| `git_branch` | Create a new branch |
| `operations` | View recent operations/audit trail |
| `rollback` | Rollback a specific operation |

### WORKSPACE_AWARE_AGENTS (22 Agents)

These agents are automatically enabled for workspace file writing via `universal_agent_tool`:

| Category | Agents |
|----------|--------|
| **Development** | FullStackDeveloperAgent, CodeGeneratorAgent, CodeReviewAgent, DevOpsAgent |
| **Content** | ContentWriterAgent, ContentStrategyAgent, TechnicalDocumentAgent |
| **Strategy** | BrandIdentityAgent, SEOOptimizerAgent, BrandStrategyAgent, MarketingStrategyAgent |
| **Research** | ResearchAgent, CompetitorAnalysisAgent, CustomerResearchAgent, TrendAnalysisAgent, MarketIntelligenceAgent |
| **Analysis** | StockAnalystAgent, OpportunityScoringAgent |
| **Legal** | LegalDocDrafterAgent |
| **System** | SystemIntelligenceAgent |

### Security Features

1. **Protected Paths** - `.env`, `secrets/`, credentials cannot be modified
2. **Permission Flags** - `allow_file_write`, `allow_file_delete`, `allow_command_execution`
3. **Human Review** - Optional `require_human_review` flag for sensitive operations
4. **Audit Trail** - Every operation logged with before/after content
5. **Rollback** - Any operation can be undone using stored content
6. **Agent Attribution** - Every change tracked to specific agent

### Usage Examples

**Register a workspace (via PA):**
```
User: "Register my project at /path/to/project"
PA uses workspace_tool with action="register", path="/path/to/project"
```

**Write code (via agent):**
```python
from core.agents.fullstack_developer_agent import FullStackDeveloperAgent

agent = FullStackDeveloperAgent(user=user)
result = agent.execute_with_workspace(
    task="Create a React component for user profile",
    context={},
    user=user,
    write_to_workspace=True,
    base_path="src/components"
)
# Files are automatically written to the workspace
```

### Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `core/models_skin_layer.py` | ~350 | 3 database models |
| `core/services/workspace_manager.py` | ~850 | Core SKIN services |
| `core/agents/base_agent.py` | +250 | Workspace methods for all agents |

---

## HEART Service - System Health Monitoring (Session 701)

The **HEART** (Health, Events, Activity, Real-time Telemetry) service is the central heartbeat of the AI body. It continuously monitors all system components every 60 seconds and provides health status through CLI, API, and Celery Beat.

### Components Monitored (6 Body Parts)

| Component | What It Checks | Healthy Threshold |
|-----------|----------------|-------------------|
| **Brain** | ThinkingAgent availability | Can import & instantiate |
| **Nervous System** | LLM Provider Registry | ≥1 provider active |
| **Organs** | 72 Agents in database | ≥50 agents registered |
| **Sensory** | 77 Spiders in registry | ≥50 spiders registered |
| **Skin** | Workspace Manager | Module importable |
| **Memory** | Database + Redis connectivity | Both respond to ping |

### Health Status Levels

| Status | Score Range | Meaning |
|--------|-------------|---------|
| **HEALTHY** | 80-100% | All systems operational |
| **DEGRADED** | 50-79% | Some components have issues |
| **CRITICAL** | 0-49% | Major systems failing (Discord alert sent) |

### Usage

```bash
# CLI Commands
python manage.py heart_check              # Full health check
python manage.py heart_check brain        # Check specific component
python manage.py heart_check --watch      # Continuous monitoring (60s)
python manage.py heart_check --history    # Show heartbeat history
python manage.py heart_check --json       # JSON output

# API Endpoints
GET /api/heart/pulse/                     # Run full check now
GET /api/heart/status/                    # Get cached vitals
GET /api/heart/history/                   # Get heartbeat history
GET /api/heart/component/<name>/          # Component detail
GET /api/heart/alive/                     # Quick alive check
```

### Database Models

| Model | Fields | Purpose |
|-------|--------|---------|
| **HeartBeat** | 10 | Time-series health records |
| **ComponentStatus** | 15 | Current status cache per component |

### Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `core/models_heart.py` | ~200 | Database models |
| `core/services/heart.py` | ~500 | HeartMonitorService |
| `core/views_heart.py` | ~180 | 5 API endpoints |
| `core/management/commands/heart_check.py` | ~240 | CLI command |

---

## LUNGS Service - Resource & Capacity Management (Session 702)

The **LUNGS** (Limits, Usage, Notifications, Governance, Spending) service manages "breathing" - token consumption across all LLM providers. It tracks usage against budgets, sends alerts when thresholds are crossed, and provides spending forecasts.

### Human Body Metaphor

| Breathing Concept | Technical Equivalent |
|-------------------|---------------------|
| **Inhale** | Budget allocation (credits available) |
| **Exhale** | Token consumption (usage) |
| **Oxygen Level** | Remaining budget % |
| **Hyperventilation** | Overspending alert |
| **Respiratory Rate** | Calls per minute |

### Default Budgets (6)

| Budget | Scope | Period | Cost Limit |
|--------|-------|--------|------------|
| System Daily | system | daily | $50.00 |
| System Monthly | system | monthly | $500.00 |
| OpenAI Daily | provider/openai | daily | $30.00 |
| Anthropic Daily | provider/anthropic | daily | $20.00 |
| Together AI Daily | provider/together_ai | daily | $10.00 |
| DeepSeek Daily | provider/deepseek | daily | $10.00 |

### Status Levels

| Oxygen Level | Status | Visual |
|--------------|--------|--------|
| 80-100% | `normal` | Green |
| 50-79% | `elevated` | Yellow |
| 20-49% | `hyperventilating` | Red |
| 0-19% | `holding` | Critical alert |

### Usage

```bash
# CLI Commands
python manage.py lungs_check              # Full breathing check
python manage.py lungs_check --oxygen     # Just oxygen levels
python manage.py lungs_check --forecast   # Spending forecast
python manage.py lungs_check --velocity   # Spending velocity
python manage.py lungs_check --budgets    # List all budgets
python manage.py lungs_check --watch      # Continuous monitoring (15m)
python manage.py lungs_check --json       # JSON output

# API Endpoints
GET /api/lungs/breathe/                   # Run full check
GET /api/lungs/status/                    # Cached respiratory status
GET /api/lungs/oxygen/                    # Remaining budget %
GET /api/lungs/budgets/                   # List all budgets
GET /api/lungs/forecast/                  # Spending forecast
GET /api/lungs/history/                   # Breath cycle history
GET /api/lungs/can-breathe/               # Check if call allowed
GET /api/lungs/alive/                     # Quick alive check
```

### Database Models

| Model | Fields | Purpose |
|-------|--------|---------|
| **Budget** | 12 | Budget configurations per scope/period |
| **BreathCycle** | 18 | Time-series consumption records |
| **RespiratoryStatus** | 12 | Current breathing status cache |

### Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `core/models_lungs.py` | ~250 | Database models |
| `core/services/lungs.py` | ~450 | LungsCapacityService |
| `core/views_lungs.py` | ~350 | 9 API endpoints |
| `core/management/commands/lungs_check.py` | ~443 | CLI command |

---

## User Context Injection (Session 858)

All 74 agents now receive personalized user context for tailored responses. The system learns what works for each user and applies that knowledge to future interactions.

### How It Works

```
User Request → AgentRouter._get_user_context()
                      │
                      ├─► AgentContextMiddleware (profile data)
                      ├─► MemoryContextService (preferences, patterns)
                      └─► Injection Policy (category filtering)
                      │
                      ▼
              context['user'] = user_context
                      │
                      ▼
              Agent.execute() → Personalized Response
                      │
                      ▼
              _record_user_learning() → UserMemoryContext
```

### Injection Policy by Agent Category

| Category | Agents | Data Injected |
|----------|--------|---------------|
| **career** | OpportunityPipelineAgent, CustomerResearchAgent | skills, job_preferences, salary_range, success_patterns |
| **content** | ContentWriterAgent, SEOOptimizerAgent | communication_style, tone_preferences, goals |
| **financial** | StockAnalystAgent, SportsOddsAnalyst | risk_tolerance, betting_preferences, investment_goals |
| **development** | CodeGeneratorAgent, DevOpsAgent | skills, tech_stack, github_username |
| **research** | ResearchAgent, TrendAnalysisAgent | interests, learning_goals, preferred_topics |
| **default** | All other agents | name, goals, communication_style |

### Enhanced Agents (4 Active)

| Agent | Personalization |
|-------|----------------|
| **ContentWriterAgent** | Uses user's communication style as default tone, adds name/goals to system prompt |
| **ResearchAgent** | Enhances task with research interests and memory patterns |
| **StockAnalystAgent** | Adds investor profile (risk tolerance, investment goals) |
| **SportsOddsAnalyst** | Adds bettor profile (favorite sports, bankroll, risk level) |

### Auto Personal Workspaces

Every user now gets a personal workspace auto-created at `generated_content/users/{username}/` when they first use an agent. This eliminates "No active workspace" errors.

### Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `core/agent_router.py` | +288 | `_get_user_context()`, injection policy |
| `core/agent_context_middleware.py` | ~500 | Profile data extraction |
| `core/services/memory_context_service.py` | ~200 | Memory/preference building |
| `core/services/workspace_manager.py` | +61 | `_ensure_personal_workspace()` |

---

## Enhanced Nervous System - LLM Routing (Session 697)

Multi-model LLM routing enables agents to use specialized LLMs for different tasks. Coding agents use Together AI (Llama 70B), creative agents use Claude, fast routing uses GPT-5-mini.

### LLM Providers (6 Configured)

| Provider | Models | Status | Use Case |
|----------|--------|--------|----------|
| **OpenAI** | GPT-5-mini, GPT-5.1, GPT-5.2 | ✅ Active | Reasoning, general tasks |
| **Anthropic** | Claude 3.5 Sonnet/Haiku/Opus | ✅ Active | Creative writing, analysis |
| **Together AI** | Llama 3.1 70B/8B, Mixtral | ✅ Active | Coding (cheap + fast) |
| **Ollama** | Llama 3.1, CodeLlama, Mistral | ✅ Active | Local/private tasks |
| **DeepSeek** | DeepSeek Coder, Chat | ⚠️ Needs key | Coding alternative |
| **Gemini** | Gemini 2.0 Flash/Pro | ⚠️ Needs lib | Long context |

### Agent → Model Routing (75 Configured)

| Agent Category | Primary Model | Fallback | Cost/1M tokens |
|----------------|---------------|----------|----------------|
| **Development** (CodeGenerator, FullStack, DevOps) | Together AI Llama 70B | Claude 4 Sonnet | $0.88 |
| **Content** (ContentWriter, Strategy, Brand) | Claude 4 Sonnet | GPT-5.1 | $3.00 |
| **Research** (Research, TrendAnalysis, Market) | GPT-5.1 | Claude 4 Sonnet | $1.25 |
| **Reasoning** (ThinkingAgent) | Claude 4 Opus | GPT-5.2 | $15.00 |
| **Fast/Routing** (PersonalAssistant, Orchestration) | GPT-5-mini | GPT-5.1 | $0.15 |
| **Coordinators** (BlockchainAudit, StockAudit, etc.) | GPT-5-mini | GPT-5.1 | $0.15 |
| **Betting** (ArbitrageDetector, SportsOddsAnalyst) | GPT-5.1 | GPT-5-mini | $1.25 |
| **Business** (CompetitorAnalysis, BrandStrategy) | Claude 4 Sonnet | GPT-5.1 | $3.00 |

### Database Models (4)

| Model | Purpose |
|-------|---------|
| `LLMProvider` | Provider configs (API keys, base URLs, capabilities) |
| `LLMModel` | Individual models with cost, context window, specializations |
| `AgentLLMConfig` | Maps agents to primary/fallback models |
| `LLMCallLog` | Audit log for cost tracking, performance analysis |

### Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `core/models_llm_routing.py` | ~750 | 4 database models + default configs |
| `core/services/llm_provider_registry.py` | ~1050 | 6 provider implementations |
| `core/services/agent_llm_router.py` | ~400 | Routing service |
| `core/agents/base_agent.py` | +80 | `_call_llm_routed()` method |

### Usage

```python
# Route through agent config
from core.services.agent_llm_router import route_agent_completion

response = route_agent_completion(
    agent_name='CodeGeneratorAgent',  # Routes to Together AI Llama 70B
    prompt='Write a Python function...',
    system_prompt='You are a code generator.'
)
print(response.content)  # Generated code
print(response.cost)     # $0.0001

# Check routing status
python manage.py setup_llm_routing --check
```

### LLM Routing API Endpoints (7 endpoints - Session 699)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/llm-routing/status/` | GET | Public | Overall system status |
| `/api/v1/llm-routing/providers/` | GET | Public | List all 6 LLM providers |
| `/api/v1/llm-routing/models/` | GET | Public | List all 16 models with costs |
| `/api/v1/llm-routing/agent-configs/` | GET | Public | 75 agent-model mappings |
| `/api/v1/llm-routing/logs/` | GET | Public | Call logs with filtering |
| `/api/v1/llm-routing/cost-analytics/` | GET | Public | Cost analytics dashboard |
| `/api/v1/llm-routing/agent-configs/<agent>/` | POST | Auth | Update agent config |

**Key File:** `core/views_llm_routing.py` (~450 lines)

---

## Personal Assistant Tools (83 Total)

Session 586 brought PA tools to 77, covering sports, betting, content, agents, spiders, legal, and more.

### Tool Categories

| Category | Tools | Examples |
|----------|-------|----------|
| **Sports & Betting** | 8 | `get_sports_data`, `query_live_odds`, `query_arbitrage`, `query_futures` |
| **Content & Media** | 6 | `create_content`, `generate_image`, `generate_video`, `schedule_content` |
| **Agent Intelligence** | 8 | `delegate_to_agent`, `query_agent_data`, `query_dreams`, `query_conversations` |
| **System Status** | 6 | `get_system_status`, `query_system_health`, `run_diagnostics`, `query_activity_metrics` |
| **Boardroom & Decisions** | 4 | `promote_boardroom_decision`, `reject_boardroom_decision`, `create_boardroom_decision` |
| **Spider Network** | 2 | `get_spider_intelligence`, `execute_spider` |
| **Workflows** | 5 | `execute_workflow`, `manage_team_workflows`, `manage_workflow_templates` |
| **Learning & Memory** | 6 | `search_knowledge`, `query_learning`, `time_travel_memory`, `manage_memory_palace` |
| **Analytics** | 6 | `query_analytics`, `query_workflow_analytics`, `query_video_analytics`, `query_model_analytics` |
| **Collaboration** | 4 | `manage_collaboration`, `query_collaboration`, `manage_project_collaboration` |
| **Notifications** | 2 | `manage_notifications`, `manage_push_notifications` |
| **Legal** | 1 | `query_legal` |
| **Revenue** | 2 | `query_revenue_metrics`, `manage_bankroll` |
| **Predictions** | 3 | `query_prediction_markets`, `manage_predictions`, `query_performance` |
| **Voice & Relationships** | 2 | `manage_voice_marketplace`, `query_agent_relationships` |
| **Evolution** | 2 | `query_agent_evolution`, `manage_team_workflows` |
| **Other** | 10 | Exports, scheduler, favorites, semantic search, etc. |

### Phase History

| Session | Phase | Tools Added | Total |
|---------|-------|-------------|-------|
| 575-579 | 1-6 | 26 | 26 |
| 580 | 7-8 | 12 | 38 |
| 581 | 9-10 | 11 | 49 |
| 582 | 11-13 | 6 | 55 |
| 583 | 14-18 | 10 | 65 |
| 584 | 19-20 | 6 | 71 |
| 585 | 21 | 2 | 73 |
| 586 | 22-23 | 4 | 77 |

---

## Image Generation (Stability AI)

### Generation Modes

| Mode | Resolution | Best For |
|------|------------|----------|
| Core | 1024x1024 | Fast drafts |
| SDXL | 1024x1024 | High quality |
| SD3 | 1024x1024 | Latest quality |
| Ultra | 1024x1024 | Maximum quality |

### Editing Operations

| Operation | Description |
|-----------|-------------|
| Upscale | 4x resolution increase |
| Remove Background | Transparent PNG output |
| Search & Replace | Replace objects in image |
| Search & Recolor | Change object colors |
| Outpaint | Extend image boundaries |
| Inpaint | Edit specific regions |
| Erase Object | Remove objects seamlessly |
| Create Variations | Generate similar images |
| Style Transfer | Apply artistic styles |
| Sketch to Image | Convert sketches |
| Structure Control | Maintain composition |
| Control Sketch | Detailed sketch control |
| 3D Character | Generate 3D-style characters |

---

## Video Generation (Runway ML)

| Feature | Model | Description |
|---------|-------|-------------|
| Text-to-Video | veo3.1 / veo3.1_fast | Generate video from text prompt |
| Image-to-Video | gen4_turbo | Animate still images |
| **Video-to-Video** | **gen4_aleph** | **Transform existing videos with AI** |
| Video Extension | gen4_aleph | Extend existing videos seamlessly |
| Lip Sync | gen4_turbo | Sync video to audio |
| Video Chaining | - | Concatenate multiple clips |

### Video-to-Video Capabilities (Gen-4 Aleph)
- **Scene Transformation** - "Make it winter", "Add fog", "Change to night"
- **Object Manipulation** - Add, remove, or replace objects
- **Shot Continuation** - Seamlessly extend video narrative
- **Style Transfer** - Apply new visual styles with reference images
- **Novel Camera Angles** - Generate new perspectives

### Available Models
| Model | Type | Best For |
|-------|------|----------|
| veo3.1 | Text-to-Video | High quality generation |
| veo3.1_fast | Text-to-Video | Fast drafts |
| gen4_turbo | Image-to-Video | Animating images |
| gen4_aleph | Video-to-Video | Transformations & extensions |
| *gen4.5* | *Coming Soon* | *Next-gen quality (API pending)* |

### Supported Resolutions
- 1280x720 (720p)
- 1920x1080 (1080p)
- 960x960 (Square)
- 1584x672 (Cinematic)

### Duration Options
- 4-10 seconds per generation
- Extended via chaining or gen4_aleph continuation

---

## Audio Generation (ElevenLabs)

| Feature | Description |
|---------|-------------|
| Text-to-Speech | Multiple voice options |
| Voiceover | Add narration to video |

### Voice Options
- 10+ built-in voices
- Custom voice training (coming)

---

## AI Podcast Studio (Session 496, Activated Session 652)

**Full podcast generation with multi-agent debates and TTS audio.**

**Status:** ACTIVE - 1 show ("AI Debates Weekly"), 1 complete episode (22,484 char script)

### Features

| Feature | Description |
|---------|-------------|
| Script Generation | Multi-speaker debate scripts with GPT |
| Voice Synthesis | ElevenLabs TTS for all speakers |
| Audio Concatenation | Seamless podcast assembly with pydub |
| Progress Tracking | Real-time status updates |

### Podcast Agents (4)

| Agent | Role | Voice |
|-------|------|-------|
| PodcastCoordinatorAgent | Orchestrates debates, generates scripts | - |
| ModeratorAgent | Hosts discussions, asks follow-ups | Antoni |
| DebateAdvocateAgent | Argues FOR topics with evidence | Rachel |
| DebateSkepticAgent | Challenges topics with critical analysis | Clyde |

### Voice Mapping

| Speaker | Voice | Style |
|---------|-------|-------|
| HOST / MODERATOR | Antoni | Warm, professional |
| ADVOCATE | Rachel | Enthusiastic, persuasive |
| SKEPTIC | Clyde | Authoritative, probing |
| ANALYST | Paul | Calm, data-driven |

### Discord Commands

| Command | Description |
|---------|-------------|
| `/podcast-create` | Create new podcast episode with optional audio |
| `/podcast-status` | Check episode generation progress |
| `/podcast-list` | List recent podcast episodes |
| `/podcast-episode` | View episode script and details |

### Audio Service

**File:** `core/services/podcast_audio_service.py`

- `parse_podcast_script()` - Parse script into speaker segments
- `generate_segment_audio()` - Generate TTS for each segment
- `concatenate_audio_segments()` - Combine with pauses
- `generate_podcast_audio()` - Main orchestrator

---

## Campaign Orchestrator (Session 652)

**Complete marketing campaign generation with research, strategy, and content creation.**

**Status:** ACTIVE - 1 campaign complete with 16 deliverables

### Features

| Feature | Description |
|---------|-------------|
| Research Phase | Market trends, competitor analysis via SmartTrendingService |
| Strategy Phase | Content strategy, SEO keywords, brand direction |
| Creation Phase | Ad copy, social posts, email sequences |
| Budget Tiers | 4 tiers from $500 to $10,000 |

### Budget Tiers

| Tier | Price | Deliverables |
|------|-------|--------------|
| Starter | $500 | Ad copy, basic images, social posts |
| Pro | $2,000 | Everything in Starter + email sequence, banners |
| Enterprise | $5,000 | Everything in Pro + video, voiceover |
| Premium | $10,000 | Full brand package with 3 videos and brand guide |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/campaigns/` | GET | List campaigns |
| `/api/campaigns/create/` | POST | Create campaign |
| `/api/campaigns/<id>/start/` | POST | Start execution |
| `/api/campaigns/<id>/status/` | GET | Check progress |
| `/api/campaigns/<id>/deliverables/` | GET | Get deliverables |
| `/api/campaigns/budget-tiers/` | GET | Get tier options |

### Agent

| Agent | Role |
|-------|------|
| CampaignOrchestratorAgent | Orchestrates all phases, coordinates sub-agents |

---

## Video Editing

| Operation | Description |
|-----------|-------------|
| Trim | Cut video start/end |
| Crop | Change frame dimensions |
| Add Text | Overlay text/titles |
| Add Effects | Visual effects |
| Color Grading | Adjust colors |
| Speed Change | Slow-mo/fast-forward |
| Concatenate | Join multiple videos |
| Extract Frame | Get still from video |
| Add Audio | Overlay audio track |
| Add Voiceover | TTS voiceover |
| Auto-Caption | Generate subtitles |
| ProRes Render | Professional output |
| DNxHD Render | Broadcast quality |
| GIF Export | Animated GIF output |

---

## 3D Generation (Replicate)

| Feature | Description |
|---------|-------------|
| Image-to-3D | Convert 2D image to 3D model |
| 3D Scene | Generate complete scenes |

### Output Formats
- GLB
- OBJ
- GLTF

---

## Character Training (LoRA)

| Feature | Description |
|---------|-------------|
| Train Character | Create custom LoRA |
| Generate with LoRA | Use trained character |
| Style Consistency | Maintain character across images |

### Training Requirements
- 10-20 reference images
- ~30 minute training time

---

## Built-in Style Presets (80+)

### Animation Styles
```
pixar, disney, dreamworks, south_park, simpsons, family_guy,
ghibli, anime, manga, looney_tunes, rick_and_morty, archer,
adventure_time, gravity_falls, bojack, cartoon, chibi
```

### Art Styles
```
watercolor, oil_painting, pencil, charcoal, pastel,
impressionist, surreal, cubist, pop_art, art_deco,
minimalist, abstract, geometric, vintage, retro
```

### Genre Styles
```
cyberpunk, steampunk, fantasy, scifi, gothic, horror,
noir, western, medieval, futuristic, post_apocalyptic
```

### Photography Styles
```
portrait, landscape, macro, street, product,
fashion, food, architecture, nature, studio
```

**Usage:** Just mention the style name - "Create a cyberpunk cityscape"

---

## Workflows (Multi-Step)

| Workflow | Steps |
|----------|-------|
| `research_and_create_logos` | Research trends + Generate logos (1024x1024) |
| `youtube_thumbnail_package` | Research + Thumbnails (1280x720) |
| `brand_identity_package` | Research + Full brand kit |
| `product_photography_kit` | Research + Product photos |
| `video_thumbnail_series` | Consistent thumbnail series |
| `logo_to_video` | Animate logo into video |

---

## Spider Network (historical detail — canonical = 80; see PLATFORM_INVENTORY)

### Data Sources by Category

| Category | Count | Real Sources |
|----------|-------|--------------|
| Tech News | 9 | HackerNews, TechCrunch, DevTo, Wired, MIT Tech Review, Axios, The Verge |
| Financial | 8 | CoinGecko API, Yahoo Finance API, SeekingAlpha |
| Jobs | 7 | RemoteOK (JSON), WeWorkRemotely (RSS), Adzuna API, FlexJobs |
| Creative | 5 | Dribbble, Behance, Unsplash API, ProductHunt |
| AI Tools | 4 | HuggingFace, Midjourney, Civitai, RunwayML |
| Digital Products | 5 | Gumroad, Etsy, LemonSqueezy, AppSumo, Sellfy |
| Content | 3 | Medium, Substack, Patreon |
| Education | 3 | Teachable, Udemy, Skillshare |
| Legal | 4 | CourtListener, Justia, FindLaw, LII |
| Community | 1 | Reddit (20+ subreddits) |
| + 10 more... | | |

### Topic Filters

Filter spider results by topic:
- `ai` - AI/ML, machine learning, neural networks
- `web` - Web development, JavaScript, React, CSS
- `security` - Cybersecurity, encryption, privacy
- `cloud` - AWS, Azure, Kubernetes, DevOps
- `design` - UI/UX, graphic design, typography

---

## Clean Agent Architecture (17 Agents)

| Agent | Purpose | Isolated Tools |
|-------|---------|----------------|
| PersonalAssistantAgent | Routes requests | delegate_to_agent |
| ImageAgent | Image generation | generate_image |
| VideoAgent | Video generation | generate_video, animate_image |
| AudioAgent | Audio generation | generate_voice, generate_sfx |
| ThreeDAgent | 3D generation | convert_to_3d |
| ImageEditingAgent | Image editing | upscale, remove_bg, etc. |
| VideoEditingAgent | Video editing | trim, add_text, etc. |
| ResearchAgent | Web + spider search | web_search, spider_query |
| WorkflowAgent | Multi-step orchestration | delegate_to_agent |
| CompetitorAnalysisAgent | Competitive intelligence | web_search, spider_query, analyze |
| CustomerResearchAgent | Customer personas | web_search, build_persona |
| LegalDocDrafterAgent | Legal document assistance | draft_motion, analyze_motion |
| **CodeGeneratorAgent** | Code generation | generate_code, explain_code |
| **FullStackDeveloperAgent** | Full-stack features | design_feature, implement_* |
| **CodeReviewAgent** | Code review | review_code, check_security |
| **DevOpsAgent** | CI/CD, Docker, K8s | create_dockerfile, create_pipeline |

---

## Development Agents (Session 436)

Four new agents for software development tasks:

| Agent | Purpose | Key Tools |
|-------|---------|-----------|
| CodeGeneratorAgent | Generate code from specs | `generate_code`, `explain_code`, `refactor_code` |
| FullStackDeveloperAgent | Build complete features | `design_feature`, `implement_backend`, `implement_frontend` |
| CodeReviewAgent | Review code quality | `review_code`, `check_security`, `check_performance` |
| DevOpsAgent | Infrastructure automation | `create_dockerfile`, `create_pipeline`, `create_k8s_manifests` |

### Supported Languages
Python, JavaScript, TypeScript, Go, Rust, Java, C#, PHP, Ruby

### Supported Platforms
- Docker, Docker Compose
- Kubernetes (deployment, service, ingress)
- GitHub Actions, GitLab CI, Jenkins
- AWS (ECS, EKS), GCP (Cloud Run, GKE)

---

## 15 Sci-Fi Features

| Feature | Purpose |
|---------|---------|
| Agent Learning | Agents learn from each other |
| Agent Conversations | Real-time AI-to-AI chat |
| Agent Dreams | Creative thoughts when idle |
| Hive Mind Mode | Collective intelligence |
| Memory Palace | Persistent agent memory |
| Mood System | Emotional states affect behavior |
| Rivalries/Alliances | Agent relationships |
| Evolution System | XP, levels, progression |
| Time Travel Debug | Replay agent decisions |
| Personality Profiles | Distinct agent personalities |
| Memory Clusters | Grouped related memories |
| Prophecies | Agent predictions |
| Time Capsules | Messages to future selves |
| Conversation Contract | Quality scoring |
| Spider Integration | Real-time data feed |

---

## API Access

All capabilities accessible via REST API:

```bash
# Main chat endpoint (Clean Architecture)
POST /api/super-platform/process/
{"message": "Create a cyberpunk logo"}

# System status
GET /api/super-platform/status/

# Image generation
POST /api/generate/image/

# Video generation
POST /api/generate/video/

# Spider data
GET /api/spiders/trending/
GET /api/spiders/search/?q=AI

# Document ingestion (Session 402)
GET /api/documents/
POST /api/documents/ingest-url/
GET /api/documents/<uuid>/
DELETE /api/documents/<uuid>/delete/
```

---

## Document Ingestion & RAG (Session 402)

Build your knowledge base by ingesting documents from multiple sources.

### Supported Sources

| Source | Method | Features |
|--------|--------|----------|
| YouTube Videos | URL paste | Transcript extraction with timestamps |
| Web Pages | URL paste | Playwright-powered JS rendering |
| PDF Documents | File upload | Text extraction |
| Text/Markdown | File upload | Direct processing |

### Processing Pipeline

1. **URL Detection** - Automatically detects YouTube vs web pages
2. **Content Extraction** - Uses requests (fast) or Playwright (JS-rendered)
3. **Text Processing** - Cleans HTML, extracts main content
4. **Embedding Generation** - Creates vector embeddings for RAG search

### Playwright Integration

For JavaScript-rendered SPAs:
- Automatically falls back to Playwright when content is insufficient
- Launches headless Chromium browser
- Waits for network idle + JS rendering
- Attempts to dismiss cookie banners
- Extracts fully rendered content

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/documents/` | GET | List all documents with stats |
| `/api/documents/ingest-url/` | POST | Ingest YouTube or web page |
| `/api/documents/<id>/` | GET | Get document with full content |
| `/api/documents/<id>/delete/` | DELETE | Delete document and embeddings |

### UI Location

Intelligence Tab → Documents sub-tab

---

## Pro Se Legal Assistant (Session 403, Enhanced 404F + Patch 4C)

AI-powered legal document assistant for Colorado family law self-represented litigants.

### Features

| Feature | Description |
|---------|-------------|
| Legal Guidance | General legal information for Colorado family law |
| Motion Templates | Generate motion templates (continuance, modify parenting time, etc.) |
| Meet-and-Confer Emails | Professional correspondence templates |
| Declaration Templates | Sworn statement templates |
| Procedure Explanations | Step-by-step guides for common procedures |
| JDF Form Reference | Colorado Judicial Department form information |
| **Case File Upload** | Upload PDFs, DOC, TXT for AI analysis |
| **Document Analysis** | AI identifies issues and recommends corrections |
| **Corrective Filing Generation** | Generate properly formatted refilings |
| **Motion Rewriter (404)** | Transform denied motion into correct JDF format |
| **Non-Party Detection (404)** | Warn when relief sought against non-parties |
| **Evidence Checklist (404)** | Motion-type specific exhibit requirements |
| **Statutory Alignment (404)** | Map facts to criteria categories (no statute citations) |
| **County/State Inference (404F)** | Auto-detects jurisdiction from court address |
| **Incident Normalization (Patch 4C)** | Clean numbered allegations from messy PDF text |

### Session 404 Motion Rewriting Tools

| Tool | Purpose |
|------|---------|
| `analyze_denied_motion` | Identify all deficiencies in denied motion |
| `rewrite_motion` | Generate corrected motion with affidavit + proposed order |
| `generate_evidence_checklist` | Create motion-type specific exhibit checklist |
| `check_non_party_issues` | Detect/correct non-party relief requests |

### Session 404F - County/State Inference

When a court address is extracted but county/state fields are blank, the system now:
- Parses city name from address (e.g., "Fort Collins, CO 80521")
- Maps Colorado cities to counties (Fort Collins → LARIMER)
- Expands state abbreviations (CO → COLORADO)

### Session 404 Patch 4C - Incident & Enumeration Normalization

Completely rewrote fact extraction for court-ready output:

| Problem | Solution |
|---------|----------|
| Inline semicolon lists ("1. Today...; 2. Aug 29...") | Split into separate numbered allegations |
| Raw PDF numbering fragments ("1." "2.") | Filtered out, only complete sentences kept |
| Subheadings in facts ("Today's Incident –") | Stripped from output |
| Missing impact summary | Allegation 4 auto-generated from petitioner's language |
| Content verification | PART 5: Full Restatement with 1:1 mapping log |

**Output Format (Patch 4C):**
```
SPECIFIC FACTUAL ALLEGATIONS:
1. On [DATE], [INCIDENT DESCRIPTION].
2. On [DATE], [INCIDENT DESCRIPTION].
3. On [DATE], [INCIDENT DESCRIPTION].
4. [IMPACT PARAGRAPH - pattern/harm summary using petitioner's language]
```

### JDF Form Mapping

| Relief Type | Primary Form |
|-------------|--------------|
| Emergency Parenting | Motion and Affidavit for Emergency Orders |
| Restrict Parenting | JDF 1220 (Motion to Modify) |
| Modify Parenting Time | JDF 1220 + JDF 1221 (Affidavit) |
| Enforce Order | Motion for Citation for Contempt |
| Modify Child Support | JDF 1820 or JDF 1821 |

### Document Types Supported

| Type | Use Case |
|------|----------|
| Court Order / Ruling | Analyze orders and understand requirements |
| Denied Motion | Understand why motion was denied, get correction guidance |
| Filed Motion | Review filed motions |
| Correspondence | Opposing party communications |
| Opposing Filing | Analyze other party's filings |
| Financial Document | Support worksheets, disclosures |
| Evidence / Exhibit | Supporting documents |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/legal/case-files/` | GET | List uploaded legal documents |
| `/api/legal/case-files/upload/` | POST | Upload and process document |
| `/api/legal/case-files/<id>/` | GET | Get document details |
| `/api/legal/case-files/<id>/analyze/` | POST | AI-powered document analysis |
| `/api/legal/case-files/<id>/delete/` | DELETE | Delete document |

### UI Location

Legal Assistant Tab → My Case Files sub-tab

### Important Notes

- Provides **general legal information only**, NOT legal advice
- Does NOT create an attorney-client relationship
- Users should consult a licensed Colorado attorney
- Generated documents are **templates** requiring review
- Court-ready output contains NO AI disclaimers (Session 404E removed them)

---

## Discord Integration (Sessions 419-432)

Real-time notifications to Discord when agents are active, plus interactive bot commands. Full Discord-First platform with server setup, client management, and content delivery.

### Discord Channels

| Channel | Purpose | Color |
|---------|---------|-------|
| `#agent-dreams` | Agent dream notifications | Purple |
| `#agent-conversations` | HiveMind sessions + knowledge sharing | Pink/Blue |
| `#system-status` | System health and status updates | Variable |
| `#gallery` | Auto-delivery of created images (Phase 1) | - |
| `#client-*` | Per-client delivery channels (Phase 3) | - |
| `#stock-agents` | Stock audit alerts (Session 461) | Severity-based |
| `#blockchain-agents` | Blockchain audit alerts (Session 461) | Severity-based |

### Discord Bot Commands (50 Total - Sessions 426-465)

| Command | Description | Phase |
|---------|-------------|-------|
| `/status` | System health check | Core |
| `/agents [limit]` | List active agents with stats | Core |
| `/agent <name>` | Get details for a specific agent | Core |
| `/trending [category]` | Get trending topics from spider data | Core |
| `/spiders` | Spider network stats | Core |
| `/ask <question>` | Ask the Personal Assistant (remembers context!) | Core |
| `/create <prompt>` | Generate an image with AI | Core |
| `/research <topic>` | Search spider data | Core |
| `/clear` | Clear conversation history | Core |
| `/sessions [action]` | View/manage sessions across web + Discord | Session 455 |
| `/link <code>` | Link Discord to web account | Core |
| `/unlink` | Check link status | Core |
| `/gallery [count]` | View your recent images (#320, #321...) | Phase 1 |
| `/profile` | View your AI Studio profile and stats | Phase 1 |
| `/opportunities [count]` | Browse matching income opportunities | Phase 1 |
| `/setup [template]` | Set up AI Studio channels in your server | Phase 2 |
| `/server-info` | View your server's configuration | Phase 2 |
| `/client-add <name> [email]` | Create client with dedicated channel | Phase 3 |
| `/client-list` | List all your clients with stats | Phase 3 |
| `/client-deliver <client> <id>` | Send deliverable to client (uploads image!) | Phase 3 |
| `/client-invite <client>` | Generate 7-day invite link for client | Phase 3 |
| `/apply <id> [message]` | Apply to an income opportunity | Phase 4 |
| `/track [status]` | Track your job applications | Phase 4 |
| `/agent-list [category]` | List agents by category | Phase 5 |
| `/agent-task <name> <task>` | Execute any agent directly | Phase 5 |
| `/advisors` | List 25 legendary advisors | Phase 5 |
| `/consult <advisor> <question>` | Get advice from Warren Buffett, Elon Musk, etc. | Phase 5 |
| `/workflow-list` | Show available multi-step workflows | Phase 5 |
| `/workflow-run <name> <input>` | Execute workflow with input | Phase 5 |
| `/subscribe [tier]` | Subscribe to Pro/Premium tier | Monetization |
| `/tier` | View current subscription tier | Monetization |
| `/cancel` | Cancel subscription | Monetization |
| `/billing` | View billing history | Monetization |
| `/voice` | List available AI voices | Voice |
| `/speak <text> [voice]` | Generate voice audio | Voice |
| `/ask-voice <question> [voice]` | Ask with spoken response | Voice |
| `/voice-ask <question> [agent] [voice]` | Ask any agent, hear response in your cloned voice | Voice (S442) |
| `/voice-chat [duration] [agent]` | Speak your question, hear AI respond (Whisper + TTS) | Voice (S444) |
| `/voice-market [action]` | Browse/search voice marketplace | Voice (S440) |
| `/voice-clone [action]` | Clone your voice | Voice (S440) |
| `/create-content <tier> <prompt>` | AI Content Factory - create packages | Content (S440) |
| `/content-status [id]` | Check content generation progress | Content (S440) |
| `/showroom [category] [tier]` | Browse content marketplace | Content (S440) |
| `/audit-contract <address> [quick]` | Full smart contract security audit | Blockchain (S461) |
| `/blockchain-status` | Check blockchain monitoring status | Blockchain (S461) |
| `/brief-feedback <rating> [comment]` | Rate Market Intelligence Brief (helpful/not-helpful) | Learning (S464) |
| `/action <action> <ticker> [reason]` | Record trading action (buy/sell/hold/research/ignore) | Learning (S464) |
| `/series-create <type> <episodes> <prompt>` | Create multi-episode AI content series (1-5 episodes) | Series (S445) |
| `/series-status [id]` | Check series generation progress and episode status | Series (S445) |
| `/series-list` | List your AI content series with pagination | Series (S445) |
| `/help` | Show all commands | Core |

### Discord-First Platform Phases

| Phase | Focus | Status |
|-------|-------|--------|
| 1. Content Delivery | `/gallery`, `/profile`, `/opportunities`, auto-delivery | ✅ Done (Session 430) |
| 2. Server Setup | `/setup`, `/server-info`, 3 templates | ✅ Done (Session 431) |
| 3. Client Management | `/client-add`, `/client-list`, `/client-deliver`, `/client-invite` | ✅ Done (Session 432) |
| 4. Income Pipeline | `/apply`, `/track`, user-friendly opportunity IDs | ✅ Done (Session 433) |
| 5. Full Agent Access | `/agent-task`, `/consult`, `/workflow-run` | ✅ Done (Session 434) |
| 6. Automation | Proactive notifications, daily digests | Pending |

### Server Setup Templates (Phase 2)

| Template | Description | Channels Created |
|----------|-------------|------------------|
| Solo Creator | Personal workspace | #creations, #research, #assistant, #dashboard |
| Freelancer | With client management | + CLIENTS category for per-client channels |
| Agency | Team + clients | + TEAM category with #general, #projects, #resources |

### Client Management (Phase 3)

Freelancers and agencies can manage clients directly via Discord:

1. **Add Client:** `/client-add "Acme Corp" contact@acme.com`
   - Creates `#client-acme-corp` channel
   - Sends welcome message to client

2. **View Clients:** `/client-list`
   - Shows all clients with status, deliverables count, revenue

3. **Send Deliverable:** `/client-deliver "Acme Corp" 320`
   - Uses image ID from `/gallery` (e.g., #320)
   - Uploads image directly to client's channel
   - Tracks delivery in database

4. **Invite Client:** `/client-invite "Acme Corp"`
   - Generates 7-day, single-use invite link

### Discord User Linking (Session 429)

Link your Discord account to your AI Studio web account so images created via `/create` appear in your personal gallery.

**How to Link:**
1. Go to AI Studio → Preferences tab → Discord Integration
2. Click "Generate Link Code" to get a 6-character code (e.g., `ABC123`)
3. In Discord, type `/link ABC123`
4. Account linked! Images now save to your gallery

**API Endpoints:**
- `POST /api/discord/generate-link-code/` - Generate temp code for linking
- `GET /api/discord/status/` - Check if Discord is linked
- `POST /api/discord/unlink/` - Remove Discord link
- `POST /api/discord/verify-link-code/` - Bot calls this to verify & link

### Cross-Platform Session Continuity (Session 455)

Resume conversations seamlessly between web app and Discord. Start a conversation on web, continue on Discord mobile, finish on web.

**How It Works:**
1. All conversations stored in database with platform tracking
2. Linked accounts share sessions across platforms
3. 24-hour session expiry (extended from 2 hours)
4. Auto-generated session titles for easy identification

**Discord Commands:**
- `/sessions list` - Show active sessions from both web and Discord
- `/sessions info` - Show current session details
- `/sessions resume` - Instructions for resuming sessions

**Session API Endpoints:**
- `GET /api/sessions/active/` - List all active sessions
- `GET /api/sessions/<id>/` - Get session details and history
- `POST /api/sessions/resume/` - Resume session from another platform
- `POST /api/sessions/end/` - End a session (mark inactive)
- `GET /api/sessions/status/` - Cross-platform sync status

**Database Fields (ChatConversation):**
- `platform` - Where message originated (web, discord, api)
- `discord_user_id` - Discord user for unlinked users
- `session_title` - Auto-generated from first message
- `session_active` - Whether session can be resumed

### Notification Types

| Type | Channel | Trigger |
|------|---------|---------|
| Agent Dreams | `#agent-dreams` | When agents dream (creative_idea, what_if, prediction, observation) |
| HiveMind Sessions | `#agent-conversations` | When multi-agent conversations complete |
| Knowledge Sharing | `#agent-conversations` | When agents share learned knowledge |
| System Status | `#system-status` | System health updates, spider activity |

### Usage

```python
from core.services.discord_notifications import discord_notify

# Send a dream notification
discord_notify.send_dream(
    agent_name="Research Agent",
    dream_title="Future of AI",
    dream_content="What if AI could dream?",
    dream_type="what_if",
    vividness=0.85
)

# Send a conversation notification
discord_notify.send_conversation(
    participants=["Image Agent", "Video Agent"],
    topic="Content optimization strategies",
    synthesis="Agreed on new approach...",
    mode="brainstorm"
)

# Send a status notification
discord_notify.send_status(
    title="System Online",
    message="All services running",
    status_type="success"  # info, success, warning, error
)

# Test connection to all channels
results = discord_notify.test_connection()
```

### Configuration

Requires `DISCORD_BOT_TOKEN` environment variable. When set, all agent activity automatically posts to Discord.

### Integration Points

- `core/tasks.py` - `generate_agent_dreams()` posts to Discord
- `force_agent_cycle` command - Posts dreams, conversations, knowledge to Discord
- `core/services/discord_notifications.py` - Main notification service
- `core/services/discord_bot.py` - Interactive bot with slash commands
- `core/views_discord.py` - User linking API endpoints

---

## Voice Interview with Whisper (Session 456)

Voice input for the Profile Interview using OpenAI Whisper for speech-to-text transcription.

### Features

| Feature | Description |
|---------|-------------|
| Voice Recording | Browser MediaRecorder captures audio (webm format) |
| Whisper Transcription | OpenAI Whisper API converts speech to text |
| Interview Processing | Transcribed text processed through interview state machine |
| Progress Tracking | Accurate progress based on 9 steps (name + 8 topics) |

### Interview Flow (8 Topics)

```
1. Name → 2. Professional Situation → 3. Time Availability → 4. Skills
→ 5. Background → 6. Income Goals → 7. Work Preferences → 8. Hidden Talents
→ 9. Commitment → COMPLETE!
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/interview/voice/` | POST | Submit audio, get transcription + next question |
| `/api/transcribe/` | POST | Transcribe audio only (no interview processing) |
| `/api/interview/start/` | POST | Start new interview session |
| `/api/interview/respond/` | POST | Submit text response to current question |
| `/api/interview/status/` | GET | Get current interview status |

### Key Files

- `intelligence/personal_assistant_interviewer.py` - Interview state machine
- `core/views_personal_assistant.py` - Voice/interview endpoints
- `ai_core/templates/ai_image_studio.html` - Voice recording UI (microphone button)

---

## Voice Marketplace (Sessions 440, 442, 443)

AI voice cloning and marketplace for buying/selling custom voices.

### Features

| Feature | Description |
|---------|-------------|
| Voice Cloning | Clone your voice via Discord recording |
| Voice Listings | List voices in marketplace for others to use |
| Revenue Sharing | 70% to voice owner, 30% platform |
| Voice Search | Browse and search available voices |

### API Endpoints (14 Total)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/voice-marketplace/voices/` | GET | List all available voices |
| `/api/voice-marketplace/voices/` | POST | Create new voice listing |
| `/api/voice-marketplace/voices/<id>/` | GET | Get voice details |
| `/api/voice-marketplace/voices/my/` | GET | List user's voices |
| `/api/voice-marketplace/voices/<id>/purchase/` | POST | Purchase voice usage |
| `/api/voice-marketplace/voices/<id>/generate/` | POST | Generate audio with voice |
| `/api/voice-marketplace/clone/start/` | POST | Start voice cloning session |
| `/api/voice-marketplace/clone/status/` | GET | Check cloning progress |
| `/api/voice-marketplace/earnings/` | GET | View voice earnings |
| `/api/voice-marketplace/purchases/` | GET | View purchase history |

### Discord Commands

| Command | Description | Session |
|---------|-------------|---------|
| `/voice-market browse` | Browse available voices | 440 |
| `/voice-market search <query>` | Search for voices | 440 |
| `/voice-market my-voices` | View your voices | 440 |
| `/voice-market earnings` | View your earnings | 440 |
| `/voice-market publish <voice>` | Make voice public in marketplace | 443 |
| `/voice-market unpublish <voice>` | Make voice private | 443 |
| `/voice-market preview <voice>` | Hear voice sample (TTS demo) | 443 |
| `/voice-clone start` | Start recording to clone | 440 |
| `/voice-clone stop <name>` | Stop recording & create voice clone | 442 |
| `/voice-clone status` | Check clone progress | 440 |
| `/voice-ask <question> [agent] [voice]` | Ask agent, hear response in your voice | 442 |

### Session 442: Voice Cloning Pipeline Complete

Full Discord voice cloning implementation:
- Join voice channel → bot records audio
- ffmpeg compression for large files (>8MB)
- ElevenLabs IVC API integration
- `voices_write` permission required
- `/voice-ask` - Ask agents, hear responses in your cloned voice
- GPT converts raw data to natural speech (no URLs read aloud!)

### Session 443: Publish & Preview

Marketplace publishing controls:
- Publish/unpublish voices (toggle `is_public` flag)
- Voice preview generation (TTS sample with voice details)
- Complete marketplace flow: Record → Clone → Publish → Browse → Preview

### Session 444: Voice Chat (Whisper Integration)

Full voice conversation loop:
- Join voice channel → speak your question
- Whisper transcribes speech to text
- Agent processes question
- TTS responds in your cloned voice
- Complete speech-to-speech interaction

**Command:** `/voice-chat [duration] [agent]`

### Key Files

- `core/models_voice_marketplace.py` - Database models
- `core/views_voice_marketplace.py` - API endpoints
- `core/services/discord_bot.py` - Voice recording, cloning, chat commands

---

## Content Pipeline (Session 440)

AI Content Factory - generate complete content packages from $5 to $50,000.

### Content Tiers

| Tier | Price Range | What You Get | Production Cost |
|------|-------------|--------------|-----------------|
| **Quick** | $5-29 | Birthday messages, simple content | ~$0.17 |
| **Ad** | $29-99 | Small business ads (15s, 30s, 60s) | ~$0.80 |
| **Brand** | $99-499 | Full brand packages (logos, videos) | ~$2.90 |
| **Series** | $499-2999 | Multi-episode content series | ~$14.00 |
| **Pitch** | $2999-9999 | Series/movie pitch packages | ~$70.00 |
| **Production** | $9999+ | Full 10-episode productions | ~$700.00 |

**Profit Margins:** 98-99%+

### Pipeline Stages

```
1. Research (Spiders) → Trending styles, competitor analysis
2. Script (GPT) → Ad copy, taglines, voiceover text
3. Character (Stability AI) → Mascots, logos, characters
4. Voice (ElevenLabs) → Voiceovers, multiple options
5. Video (Runway ML) → Animated content, ads
6. Package → Bundle, price, publish to showroom
```

### Discord Commands

| Command | Description |
|---------|-------------|
| `/create-content <tier> <prompt>` | Generate complete package |
| `/content-status [id]` | Check generation progress |
| `/showroom [category] [tier]` | Browse content marketplace |

### Example Usage

```
/create-content ad "Tony's Pizza, Brooklyn, $2 Tuesdays"

Result:
- 3 mascot images (pizza character in different poses)
- 3 voiceover options (different styles)
- 3 video ads (15s, 30s, 60s)
- All bundled and ready to sell
```

### Key Files

- `core/models_content_pipeline.py` - Database models
- `core/services/content_pipeline.py` - Pipeline orchestration
- `docs/UNIFIED_CONTENT_PIPELINE.md` - Master documentation

---

## Blockchain Audit System (Session 461)

Autonomous blockchain security monitoring with 24/7 surveillance and real-time event listening.

### Agents

| Agent | Purpose |
|-------|---------|
| SmartContractAuditorAgent | Audit Solidity code for vulnerabilities |
| TransactionMonitorAgent | Watch for suspicious tx patterns |
| WhaleWatcherAgent | Track large token movements (100+ ETH) |
| ExploitDetectorAgent | Pattern match known exploits |
| BlockchainAuditCoordinator | Orchestrate all blockchain agents |

### Blockchain Event Listener

Real-time monitoring service with background polling (15s intervals):

| Event Type | Description |
|------------|-------------|
| WHALE_TRANSFER | Large ETH movements (100+ ETH) |
| CONTRACT_DEPLOY | New contract deployments |
| SUSPICIOUS_TX | Unusual transaction patterns |
| EXPLOIT_SIGNATURE | Known exploit pattern detection |

### Contract Audit by Address

Audit any verified smart contract by Ethereum address:

```python
from core.services.blockchain_event_listener import audit_contract_by_address

result = audit_contract_by_address("0xdAC17F958D2ee523a2206206994597C13D831ec7")
# Returns: contract source, risk analysis, GPT-powered audit
```

### Discord Commands

| Command | Description |
|---------|-------------|
| `/audit-contract <address> [quick]` | Full smart contract audit by address |
| `/blockchain-status` | Check monitoring status and API health |

### Spiders

| Spider | Source | Data |
|--------|--------|------|
| EtherscanAPISpider | Etherscan API V2 | Real-time transactions, contract source |
| DefiLlamaSpider | DeFi Llama | TVL, protocol health |
| RektNewsSpider | Rekt.news | Known exploits |

### Alert Types

| Severity | Trigger | Discord Channel |
|----------|---------|-----------------|
| CRITICAL | Active exploit detected | #blockchain-agents |
| HIGH | Suspicious transaction pattern | #blockchain-agents |
| MEDIUM | Vulnerability in popular contract | #blockchain-agents |
| LOW | Informational (new deployments) | #blockchain-agents |

### Integration

- Wired into AutonomousIntelligenceLoop (15-min checks)
- Discord `#blockchain-agents` channel (ID: 1450589795058192465)
- Real-time event listener with handler registration
- Etherscan API V2 (V1 deprecated Dec 2025)

---

## Stock Audit System (Session 461)

Autonomous stock market monitoring with multi-agent analysis and correlation detection.

### Agents

| Agent | Purpose |
|-------|---------|
| StockAnalystAgent | SEC filings, fundamentals, valuations |
| MarketMovementMonitorAgent | Price/volume spike detection |
| InstitutionalWatcherAgent | Insider trading & 13F filings |
| MarketAnomalyDetectorAgent | Pump & dump, manipulation patterns |
| StockAuditCoordinator | Orchestrate and correlate findings |

### Detection Thresholds

| Type | Threshold |
|------|-----------|
| Volume Spike | 2x average volume |
| Price Change (Critical) | 20% change |
| Price Change (High) | 10% change |
| Pump & Dump | 50% price + 10x volume |
| Large Transaction | $1M+ value |

### Correlated Alerts

When multiple agents flag the same ticker, severity is automatically upgraded:
- 2+ agents flagging same stock → CORRELATED alert
- HIGH alert with correlation → upgraded to CRITICAL

### Alert Types

| Severity | Trigger | Discord Channel |
|----------|---------|-----------------|
| CRITICAL | Multiple agents flag same ticker | #stock-agents |
| HIGH | Significant price/volume anomaly | #stock-agents |
| MEDIUM | Insider trading activity | #stock-agents |
| LOW | Unusual but explainable activity | #stock-agents |

### Integration

- Celery Beat: Every 30 min during market hours (9am-4pm M-F)
- Discord `#stock-agents` channel (ID: 1450589539562426418)
- Wired into AutonomousIntelligenceLoop
- Data from SEC Edgar + Yahoo Finance spiders

---

## Market Intelligence Desk (Session 465)

**Status:** 100% Complete (18/18 components)
**First Tier 1 Autonomous Situation**

A fully autonomous market intelligence system that generates daily market briefs with bull/bear debates, technical signals, and risk alerts.

### Agents

| Agent | Purpose |
|-------|---------|
| BullCaseAgent | Arguments for price appreciation |
| BearCaseAgent | Arguments for price depreciation |
| SignalScannerAgent | Technical patterns & trading signals |
| StockAuditCoordinator | Risk signals & anomalies |
| MarketIntelligenceCoordinator | Synthesizes debate into actionable brief |

### SignalScannerAgent Tools

- `scan_patterns` - Detect chart patterns (breakouts, reversals, continuations)
- `volume_analysis` - Find unusual volume activity
- `momentum_scan` - Identify momentum shifts (RSI, MACD, Stochastic)
- `options_flow` - Detect unusual options activity (smart money)

### Autonomous Features

| Feature | Implementation |
|---------|----------------|
| Persistent Context | Yesterday's brief loaded from DB |
| Incoming Signals | Spider network, price data, SEC filings |
| Internal Disagreement | Bull vs Bear debate creates alpha |
| Outputs with Consequences | Discord + spoken briefs, tracked for learning |
| Self-Renewal | Scheduled 6:30 AM + event-driven re-runs |

### Delivery Channels

| Channel | Implementation |
|---------|----------------|
| Discord | Text brief with structured sections (#market-intelligence) |
| Voice (TTS) | ElevenLabs professional narration (Drew voice) |
| Web Dashboard | MarketIntelligenceBrief model |

### Scheduling

- **Daily Brief:** 6:30 AM Mon-Fri (before market open)
- **Event Monitoring:** Every 30 min during market hours (9 AM - 4 PM)
- **Outcome Tracking:** 6 PM daily (after market close)
- **Accuracy Calculation:** Sunday 8 PM weekly

### Event-Driven Re-runs

Automatically triggers new brief when:
- Large price movements (>5% change in watchlist stocks)
- High-impact SEC filings (8-K material events, M&A, earnings)
- 2+ high severity events detected

### Learning Loop Integration (Session 464)

**Automated Celery Tasks:**
- **Track Prediction Outcomes** - Daily at 6 PM (after market close)
  - Finds predictions from 7 days ago and 30 days ago
  - Fetches current prices and calculates accuracy
  - Updates PredictionOutcome records with results
- **Calculate Agent Accuracy** - Weekly on Sundays at 8 PM
  - Analyzes last 30 days of predictions per agent
  - Calculates accuracy rates, conviction calibration, market regime performance
  - Updates confidence multipliers (0.5x-1.5x based on performance)

**Flow:**
1. Bull/Bear agents make predictions → PredictionOutcome records
2. Track outcomes (7-day, 30-day) → Compare to actual moves
3. Calculate agent accuracy → AgentAccuracyMetrics
4. Adjust confidence multipliers (0.5x-1.5x) → Better predictions over time

**User Feedback (Discord):**
- `/brief-feedback` - Rate briefs as helpful/not-helpful
- `/action` - Record trading actions (buy/sell/hold/research/ignore)
- Feedback tracked in UserBriefFeedback model
- System learns which recommendations users actually follow

### Brief Structure

1. **Executive Summary** - Top opportunities and market thesis
2. **High Conviction** - Stocks with strong bull/bear agreement
3. **Debate Zone** - Stocks with conflicting signals
4. **Risk Alerts** - Items requiring attention
5. **What Changed** - Key differences from yesterday

### Spoken Brief Features

- Natural-sounding script optimized for audio delivery
- Professional "Drew" voice (male narrator)
- Highest quality model (eleven_multilingual_v2)
- Concise summary (top 3 opportunities, top 2 debates)
- Audio saved to Cloudinary for public access

**Example Script:**
```
"Good morning. Here's your market intelligence brief."
[Executive Summary]
"High conviction opportunities: We found 3 stocks with strong agreement."
[Top 3 opportunities with ticker, direction, conviction]
"Debate zone: 2 stocks with significant disagreement between bull and bear cases."
[Top 2 debates with conflicting signals]
"Risk alerts: 1 item requires attention."
"End of brief. Markets never sleep, and neither do we."
```

---

## Autonomous Content Studio (Session 466)

**Status:** 100% Complete (Tier 1 Autonomous Situation #3)

A fully autonomous content generation system that runs forever, creating content for channels through agent debates and learning from performance.

### The 5 Autonomous Properties

| Property | Implementation |
|----------|----------------|
| **1. Persistent Context** | ContentChannel stores config, performance history, TopicPerformance tracks what works |
| **2. Incoming Signals** | Spider network provides trending topics, platform APIs deliver metrics |
| **3. Internal Disagreement** | TopicMiner vs Contrarian vs PerformanceAnalyst debate before each episode |
| **4. Outputs with Consequences** | ChannelEpisodes tracked for views/retention, impacts future topic selection |
| **5. Self-Renewal** | Auto-schedules next cycle based on frequency (daily/weekly/monthly) |

### Agents

| Agent | Role in Debate |
|-------|---------------|
| AutonomousContentStudioCoordinator | Orchestrates the entire autonomous system |
| TopicMinerAgent | Argues FOR trending topics (finds popular content) |
| ContrarianAgent | Argues AGAINST oversaturated topics (seeks unique angles) |
| PerformanceAnalystAgent | Argues from EVIDENCE (historical performance data) |

### Database Models

| Model | Purpose |
|-------|---------|
| ContentChannel | Stores channel config, schedule, performance stats |
| ChannelEpisode | Individual content pieces with metrics (views, retention, etc.) |
| TopicPerformance | Aggregated learning data about successful topics |
| ContentDebate | Records all agent positions for transparency |

### TopicMinerAgent Tools

- `query_spider_trends` - Query spider network for trending topics
- `score_topic_potential` - Score topics based on mentions, recency, relevance
- `detect_trending_gaps` - Find trending topics NOT yet covered by channel

### ContrarianAgent Tools

- `check_topic_saturation` - Detect oversaturated topics (warns against following crowd)
- `suggest_unique_angles` - Generate contrarian angles (opposite perspective, beginner/advanced splits, etc.)
- `find_rising_topics` - Find topics that are RISING but not yet saturated

### PerformanceAnalystAgent Tools

- `get_topic_performance_history` - Get historical performance for similar topics
- `predict_topic_performance` - Predict performance based on exact match, similar topics, or channel average
- `get_success_patterns` - Identify patterns in most successful content
- `calculate_confidence_score` - Calculate confidence based on historical data availability

### Autonomous Operation

**Celery Tasks:**
- `run_autonomous_content_studio` - Main loop (every 4 hours)
  - Checks which channels are due for content (next_content_due <= now)
  - Triggers content generation for each due channel
- `generate_content_for_channel` - Worker task per channel
  - Initiates agent debate (TopicMiner vs Contrarian vs PerformanceAnalyst)
  - Uses winning topic to trigger AISeriesWorkflowAgent
  - Creates ChannelEpisode and links to ContentDebate
  - Calls schedule_next_content() for self-renewal
- `track_content_performance` - Daily at 8 PM
  - Fetches metrics from publishing platforms (YouTube API, etc.)
  - Updates ChannelEpisode performance fields
  - Updates TopicPerformance aggregates
  - Adjusts channel confidence multipliers (0.5x-1.5x based on results)

### Learning Loop

The system LEARNS from performance:

1. **TopicPerformance Tracking:** Every published episode updates aggregated topic data
2. **Confidence Multipliers:** Channels get 0.5x-1.5x multiplier based on recent performance
   - 0-30 score → decrease confidence (0.5x-0.9x)
   - 30-50 score → maintain confidence (0.9x-1.1x)
   - 50-100 score → increase confidence (1.1x-1.5x)
3. **Topic Prediction:** PerformanceAnalystAgent uses historical data for predictions
   - EXACT_MATCH: High confidence (0.9) if topic done before
   - SIMILAR_TOPICS: Moderate confidence (0.6) if related topics exist
   - CHANNEL_AVERAGE: Low confidence (0.3) if no historical data

### Discord Commands

| Command | Purpose |
|---------|---------|
| `/studio-create` | Create new autonomous channel (name, domain, frequency, audience, style) |
| `/studio-list` | List all active channels with stats (episodes, views, retention, confidence) |
| `/studio-status` | Detailed channel status (recent episodes, top topics, schedule) |
| `/studio-pause` | Pause autonomous generation for a channel |
| `/studio-resume` | Resume autonomous generation for a channel |
| `/studio-performance` | Detailed analytics (overall metrics, learning metrics, top 5 topics) |

### Content Debate Process

For each piece of content, agents debate:

1. **TopicMinerAgent:** "This topic is trending! 47 mentions in last 3 days, high potential"
2. **ContrarianAgent:** "WARNING - Saturation level HIGH. Everyone's covering this. Suggest unique angle"
3. **PerformanceAnalystAgent:** "Historical data shows similar topics get 15K views avg. Confidence: 0.7"
4. **Coordinator:** Synthesizes debate into final decision, creates ContentDebate record
5. **AISeriesWorkflowAgent:** Creates actual content based on winning topic
6. **ChannelEpisode:** Created to track performance of this decision

### Channel Types Supported

- **Daily:** Content every 24 hours (news, market updates)
- **Weekly:** Content every 7 days (in-depth analysis, tutorials)
- **Monthly:** Content every 30 days (comprehensive reports)

### Why This is Tier 1 Autonomous

Unlike simpler systems, this NEVER needs intervention:

- ✅ Runs indefinitely (Property #5: Self-Renewal)
- ✅ Improves from outcomes (Learning Loop)
- ✅ Debates before acting (Property #3: Internal Disagreement)
- ✅ Tracks consequences (Property #4: Performance metrics)
- ✅ Persists knowledge (Property #1: TopicPerformance, ContentChannel)

**It's a synthetic organization that runs forever and gets smarter over time.**

---

## ML Scoring Engine (Session 470)

**Status:** Phase 1 Complete

An XGBoost-based machine learning scoring system with SHAP explainability for opportunity scoring.

### Architecture

| Component | Description |
|-----------|-------------|
| MLScoringEngine | XGBoost model + SHAP for explainable predictions (~500 lines) |
| MLModelVersion | Tracks model versions, metrics, feature importance |
| ScoringExplanation | Stores SHAP values for each scored opportunity |

### Hybrid Scoring Formula

```
final_score = (0.6 * ml_score) + (0.4 * rule_based_score)
```

### Feature Extraction (15 features)

The ML model extracts these features from SpiderData:
1. Title length
2. Content length
3. Source authority score
4. Freshness (hours since discovery)
5. Category match score
6. Keyword relevance
7. Has URL (boolean)
8. Content quality indicators
9. Source reliability history
10. Time of day discovered
11. Day of week discovered
12. Topic trending score
13. Competition saturation
14. Historical performance (similar topics)
15. User preference alignment

### SHAP Explainability

Every scored opportunity includes feature contributions explaining WHY:
```json
{
  "score": 78.5,
  "explanation": {
    "source_authority": +12.3,
    "freshness": +8.7,
    "keyword_relevance": +6.2,
    "competition_saturation": -4.1
  }
}
```

### Auto-Training

- **Trigger:** 100+ OpportunityOutcome records
- **Schedule:** Weekly (Sunday 3:30 AM)
- **Evaluation:** Daily (6:30 AM) - checks accuracy, triggers retraining if degraded

### Celery Tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| `train_ml_scoring_model` | Sunday 3:30 AM | Retrain XGBoost model |
| `evaluate_ml_model_performance` | Daily 6:30 AM | Check accuracy, trigger retraining if needed |

### Database Models

```python
# MLModelVersion - Tracks model versions
class MLModelVersion(models.Model):
    version = models.CharField(max_length=50)
    model_type = models.CharField(max_length=50)  # 'xgboost', 'lightgbm'
    trained_at = models.DateTimeField()
    training_samples = models.IntegerField()
    accuracy = models.DecimalField()
    precision = models.DecimalField()
    recall = models.DecimalField()
    f1_score = models.DecimalField()
    feature_importance = models.JSONField()
    is_active = models.BooleanField(default=False)
    model_path = models.CharField()

# ScoringExplanation - Stores SHAP values
class ScoringExplanation(models.Model):
    opportunity = models.ForeignKey('Opportunity')
    model_version = models.ForeignKey('MLModelVersion')
    ml_score = models.DecimalField()
    rule_score = models.DecimalField()
    final_score = models.DecimalField()
    shap_values = models.JSONField()
    created_at = models.DateTimeField()
```

### Current State

| Component | Status |
|-----------|--------|
| ML Model | Not yet trained (needs OpportunityOutcome data) |
| Scoring | Using rule-based fallback with hybrid structure |
| Ready For | Auto-training when 100+ outcomes exist |

### Usage

```python
from core.services.ml_scoring_engine import MLScoringEngine
from core.models import SpiderData

engine = MLScoringEngine()
spider_data = SpiderData.objects.first()
result = engine.score_opportunity(spider_data)
print(f"Score: {result['score']}")
print(f"Explanation: {result['explanation']}")
```

---

## Agent-Model Router (Sessions 677-683)

**Status:** COMPLETE (All 6 Phases + GPT Integration)

Intelligent ML model routing with auto-selection, connecting specialized ML models to agents and GPT assistant.

### Architecture (6 Phases)

| Phase | Session | Focus | Tests |
|-------|---------|-------|-------|
| 1 | 677 | Foundation (Registry, Router) | 30 |
| 2 | 678 | Time-Series (LSTM, Prophet) | 29 |
| 3 | 679 | Anomaly Detection (VAE) | 28 |
| 4 | 680 | Reinforcement Learning | 35 |
| 5 | 681 | Graph Neural Networks | 37 |
| 6 | 682 | Model Auto-Selection | 59 |
| **Total** | | | **218** |

### ML Models Available (17)

| Model | Task Type | Use Case |
|-------|-----------|----------|
| lstm | TIME_SERIES | Price forecasting, trend analysis |
| prophet | TIME_SERIES | Seasonal pattern detection |
| gnn | GRAPH | Network analysis, relationship detection |
| autoencoder | ANOMALY | Outlier detection |
| rl_dqn | DECISION | Strategy optimization |
| rl_ppo | DECISION | Policy learning |
| distilbert | TEXT | NLP, sentiment analysis |
| xgboost | CLASSIFICATION | Tabular data classification |
| lightgbm | CLASSIFICATION | Fast gradient boosting |

### GPT Integration (Session 683)

**New Tool:** `ml_analysis` - GPT can invoke ML models for data analysis

```python
# GPT tool call
{
    "name": "ml_analysis",
    "parameters": {
        "data": {"timestamp": ["2024-01-01"], "price": [100]},
        "task_type": "auto",  # auto-detects from data
        "analysis_goal": "predict next price"
    }
}
```

### Agent Integration (Session 683)

| Agent | ML Model | Use Case |
|-------|----------|----------|
| MarketIntelligenceAgent | GNN | Market entity relationship analysis |
| StockAnalystAgent | LSTM | Price trend forecasting |
| WhaleWatcherAgent | GNN | Wallet transaction network analysis |
| OpportunityScoringAgent | RL | Opportunity ranking optimization |

### Usage

```python
from core.services.agent_model_router import get_agent_model_router
from ml.auto_selection import TaskType

router = get_agent_model_router()

# Auto-select models based on data
result = router.auto_route({"timestamp": [...], "price": [...]})
print(f"Task: {result.auto_selection['task_type']}")  # 'time_series'
print(f"Models: {result.models_used}")  # ['lstm', 'prophet']

# With task hint
result = router.auto_route(data, task_hint=TaskType.GRAPH)
```

---

## Narrative Drift Detector (Session 471)

**Status:** COMPLETE (Tier 1 Autonomous Situation #2)

Monitors public narratives across 8 domains and detects when the conversation is shifting.

### Architecture

| Component | Description |
|-----------|-------------|
| 30 Narratives | Tracked statements across 8 domains |
| 8 Domains | tech, markets, politics, culture, geopolitics, crypto, climate, health |
| 4 Agents | Historian, TrendBreak, CulturalImpact, Coordinator |
| 5 Statuses | emerging, dominant, shifting, fading, dead |

### Key Models

| Model | Purpose |
|-------|---------|
| `Narrative` | Core narrative statements with keywords |
| `NarrativeEvidence` | Spider data matching narratives |
| `NarrativeShift` | Detected shift with confidence/importance |
| `NarrativeAlert` | Notifications for significant shifts |

### Agents

1. **NarrativeHistorianAgent** - Historical context for narratives
2. **TrendBreakDetectorAgent** - Identifies why shifts are happening
3. **CulturalImpactAnalystAgent** - Predicts downstream effects
4. **NarrativeDriftCoordinator** - Orchestrates the autonomous cycle

---

## Provenance & Compliance (Session 472)

**Status:** COMPLETE (Market Intelligence Phase 5)

Blockchain-style data lineage tracking with cryptographic integrity verification.

### Architecture

| Component | Description |
|-----------|-------------|
| DataProvenance | Entity lineage with hash chains |
| AuditLog | Immutable append-only audit trail |
| ComplianceCheck | Rule evaluation records |
| ComplianceRule | Configurable compliance definitions |

### Data Lineage Chain

```
SpiderData → Opportunity → Score → Validation → Outcome
     ↓
NarrativeEvidence → NarrativeShift → ContentEpisode
```

### Cryptographic Integrity

- **Content Hash:** SHA-256 of entity content
- **Chain Hash:** Previous record's hash (blockchain-style)
- **Verification:** Full chain integrity checking

### API Endpoints (11)

| Endpoint | Purpose |
|----------|---------|
| `/api/mi/lineage/<entity_type>/<entity_id>/` | Get lineage chain |
| `/api/mi/provenance/<id>/verify/` | Verify integrity |
| `/api/mi/compliance/summary/` | Compliance statistics |
| `/api/mi/audit/trail/` | Query audit logs |

---

## ROI Metrics (Session 472)

**Status:** COMPLETE (Market Intelligence Phase 6)

Revenue attribution and conversion tracking with multi-touch attribution.

### Conversion Funnel

```
view → click → apply → submit → interview → offer → convert → revenue
```

### Attribution Models

| Model | Description |
|-------|-------------|
| first_touch | First interaction gets full credit |
| last_touch | Last interaction gets full credit |
| linear | Equal credit to all touchpoints |
| time_decay | Recent touchpoints get more credit |
| position_based | 40% first, 40% last, 20% middle |

### Key Models

| Model | Purpose |
|-------|---------|
| `ConversionEvent` | Track funnel events |
| `ROIMetric` | Aggregated ROI statistics |
| `AttributionPath` | Multi-touch attribution chains |
| `WeeklyIntelligenceBrief` | Auto-generated summaries |

### API Endpoints (15)

| Endpoint | Purpose |
|----------|---------|
| `/api/mi/roi/summary/` | ROI summary |
| `/api/mi/roi/dashboard/` | Dashboard overview |
| `/api/mi/conversion/record/` | Record event |
| `/api/mi/funnel/` | Funnel metrics |
| `/api/mi/attribution/by-source/` | By spider source |
| `/api/mi/briefs/generate/` | Generate weekly brief |

---

## Unified Intelligence Pipeline (Session 474)

**Status:** COMPLETE (All 3 Tier 1 Autonomous Situations Connected)

Orchestrates all three autonomous systems as ONE unified pipeline.

### Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  Spider Network → ML Score → Narrative Check → Content Gen → Track │
└─────────────────────────────────────────────────────────────────────┘
```

### 6-Phase Pipeline

| Phase | Description |
|-------|-------------|
| 1. Spider Data | Check recent crawls |
| 2. ML Scoring | Score unscored opportunities |
| 3. Narrative Drift | Run autonomous cycle |
| 4. Content Generation | Create shift reports |
| 5. Provenance | Collect lineage stats |
| 6. Revenue | Track outcome revenue |

### Celery Tasks

| Task | Schedule |
|------|----------|
| `unified_pipeline.run_complete_cycle` | Every 12 hours |
| `unified_pipeline.health_check` | Every 2 hours |

### Provenance Chain

Full data lineage tracking from spider to content:
- `create_narrative_evidence_provenance()`
- `create_narrative_shift_provenance()`
- `create_content_episode_provenance()`

### System Metrics

| Metric | Value |
|--------|-------|
| Total Spiders | 67 |
| Narratives Tracked | 30 |
| Domains | 8 |
| Agents | 53 |
| Autonomous Systems | 3 (all connected) |

---

## 19 Autonomous Situations (Sessions 479-481)

**Status:** COMPLETE - ALL 19 Situations Fully Automated + Event-Driven

The platform now operates 19 autonomous intelligence situations across 6 domains, all with event-driven triggers that react in SECONDS instead of waiting for scheduled runs.

### All 19 Situations

| # | Situation | Domain | Schedule |
|---|-----------|--------|----------|
| 1 | Autonomous Content Studio | Content | Every 4h + Events |
| 2 | Narrative Drift Detector | Content | Every 4h + Events |
| 3 | Market Intelligence Desk | Financial | Daily + Events |
| 4 | Blockchain Security Alerts | Financial | Every 2h + Events |
| 5 | Stock Market Intelligence | Financial | Every 4h + Events |
| 6 | SEC Filing Analyzer | Financial | Every 2h + Events |
| 7 | Crypto Sentiment Monitor | Financial | Every 2h + Events |
| 8 | Earnings Surprise Predictor | Financial | Twice daily + Events |
| 9 | Design Trends Monitor | Creative | Every 6h + Events |
| 10 | Viral Content Predictor | Creative | Every 4h + Events |
| 11 | Thumbnail A/B Optimizer | Creative | Every 6h + Events |
| 12 | Job Match Intelligence | Income | Every 2h + Events |
| 13 | Freelance Opportunity Scout | Income | Every 4h + Events |
| 14 | Side Hustle Detector | Income | Every 8h + Events |
| 15 | Tech Stack Evolution Tracker | Research | Every 6h + Events |
| 16 | AI Model Release Monitor | Research | Every 4h + Events |
| 17 | Course & Skill Gap Analyzer | Research | Twice daily + Events |
| 18 | Case Law Monitor | Legal | Every 6h + Events |
| 19 | Regulatory Change Detector | Legal | Every 8h + Events |

### Event-Driven Trigger System (Session 481)

| Component | Count |
|-----------|-------|
| TriggerType choices | 29 |
| SituationType choices | 20 |
| DEFAULT_TRIGGERS | 34 |
| Celery Beat Schedules | 49 |

### Trigger Types by Domain

| Domain | Trigger Types |
|--------|---------------|
| **Financial** | `whale_movement`, `price_crash`, `price_surge`, `volume_spike`, `exploit_keyword`, `crypto_sentiment`, `stock_mover`, `sec_filing`, `breaking_news`, `earnings_surprise`, `institutional_filing`, `market_intelligence` |
| **Content** | `content_trend`, `narrative_drift`, `viral_content` |
| **Creative** | `design_trend`, `visual_trend`, `creative_opportunity` |
| **Income** | `job_match`, `freelance_opportunity`, `side_hustle`, `high_paying_gig` |
| **Research** | `tech_stack_change`, `ai_model_release`, `skill_gap`, `tech_breakthrough` |
| **Legal** | `case_law_update`, `regulatory_change`, `legal_precedent` |

### Data Flow

```
Spider Data → post_save Signal → Evaluate 34 Triggers → Fire Task → Instant Analysis!
```

### Discord Commands (Session 480)

| Command | Description |
|---------|-------------|
| `/situation-list [domain]` | List all 19 situations |
| `/situation-status <situation>` | Detailed status and stats |
| `/situation-run <situation>` | Manually trigger any situation |
| `/situation-alerts <situation>` | Configure alert thresholds |

### Key Files

| File | Purpose |
|------|---------|
| `core/models_situation_triggers.py` | Trigger types, situation types, defaults |
| `core/tasks.py` (14607-14652) | SITUATION_TASK_MAP + event handler |
| `core/services/discord_bot.py` (10631-10803) | SituationCommands Cog |
| `core/signals/trigger_signals.py` | post_save signal handler |

---

## Intelligence Command Center (Sessions 536-538)

**Status:** COMPLETE - All 3 Detail Panels Working

The Command Center tab in AI Studio provides a unified view of the platform's intelligence network with real-time data and clickable detail panels.

### Three Detail Panels

| Panel | API Endpoint | Shows |
|-------|--------------|-------|
| **Spider Detail** | `/api/spider-intelligence/detail/<name>/` | Actual articles with clickable links, metadata |
| **Agent Detail** | ~~`/api/agent-intelligence/detail/<name>/`~~ | Removed Session 1009 |
| **Situation Detail** | `/api/situation-intelligence/detail/<type>/` | Triggers, total fires, recent events |

### Features

| Feature | Status | Session |
|---------|--------|---------|
| Spider List by Category | ✅ Collapsible | 537 |
| Agent Roster (55 agents) | ✅ Clickable | 537 |
| Situation List (19 situations) | ✅ Clickable | 537 |
| Detail Panel Overlay | ✅ Fixed position | 537 |
| Public APIs (no auth) | ✅ | 538 |

### APIs (All Public)

```
GET /api/spider-intelligence/dashboard-stats/
GET /api/spider-intelligence/detail/<spider_name>/
# GET /api/agent-intelligence/detail/<agent_name>/  # Removed Session 1009
GET /api/situation-intelligence/detail/<situation_type>/
GET /api/intelligence/cross-references/
```

### Key Files

| File | Purpose |
|------|---------|
| `ai_core/templates/partials/js/intelligence_command_center.html` | Frontend JavaScript |
| `ai_core/templates/components/panels/intelligence_command_center.html` | UI layout |
| `core/views_spider_intelligence.py` | API endpoints |
| `core/auth_middleware.py` | PUBLIC_PATHS config |

---

## Pilot Readiness Gate (Sessions 590-593)

**Status:** COMPLETE - Full Workflow + Auto-Gate Creation

The Pilot Readiness Gate system bridges the gap between Boardroom decisions and actual execution, ensuring safety-sensitive work proceeds with appropriate governance.

### Auto-Gate Creation (Session 593)

Gates are now automatically created for safety-sensitive decisions:

| Decision Criteria | Risk Level | Checklist Items |
|-------------------|------------|-----------------|
| `impact_area='security'` | HIGH | 6 items |
| `decision_type='policy'` | MEDIUM | 3 items |
| Other decisions | None | No gate |

**Integration Points:**
- DecisionExtractor (AgentConversation + HiveMindSession decisions)
- WorkflowAgent (PA-initiated Boardroom decisions)

### Workflow

```
Dream → Boardroom Decision → [PILOT READINESS GATE] → Pilot Execution → Full Implementation
```

### Gate Status Flow

```
not_started → in_progress → ready → approved → [pilot running] → [pilot completed]
                              ↓
                           blocked / waived
```

### Risk Levels & Auto-Generated Checklists

| Risk Level | Required Items |
|------------|----------------|
| **Low** | Basic Review (optional) |
| **Medium** | Threat Model, Rollback Procedure, Success Metrics |
| **High** | Threat Model, Consent Lifecycle, Encryption Choice, Adversarial Test, Kill Switch, Rollback |
| **Critical** | All High items + Executive Approval, Legal Review |

### API Endpoints (7 Total)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/pilot-gates/` | GET | List all gates with status counts |
| `/api/pilot-gates/<gate_id>/` | GET | Get gate detail with checklist |
| `/api/pilot-gates/<gate_id>/status/` | POST | Update status (start/ready/approve/block/waive) |
| `/api/pilot-gates/<gate_id>/items/<item_id>/` | POST | Update checklist item |
| `/api/pilot-gates/create/<decision_id>/` | POST | Create gate for decision |
| `/api/pilot-gates/<gate_id>/pilot/` | POST | Start pilot execution |
| `/api/pilot-gates/<gate_id>/pilot/<pilot_id>/complete/` | POST | Complete pilot |

### Pilot Outcomes

| Outcome | Meaning |
|---------|---------|
| `success` | Proceed to full implementation |
| `partial` | Iterate and re-pilot |
| `failure` | Do not proceed |
| `inconclusive` | Need more data |

### Latency Metrics Tracked

- Decision → Readiness start time
- Readiness duration (checklist completion)
- Approval wait time
- Total gate time
- Pilot execution duration

### UI Location

**Path:** AI Studio → Intelligence Command Center → Pilot Readiness Gates panel

### Key Files

| File | Purpose |
|------|---------|
| `core/models_pilot_readiness.py` | Gate, Checklist, Execution, Experiment models |
| `core/views_agent_learning.py:2218+` | API endpoints |
| `core/urls.py:2702-2734` | URL routes |
| `ai_core/templates/ai_image_studio.html:7130+` | ICC tab UI |

### AI-Powered Governance (Session 594)

Two-layer automatic pilot management:

| Layer | Task | Schedule | Purpose |
|-------|------|----------|---------|
| **A** | `auto_complete_pilots` | Every 4h | Auto-SUCCESS after 24h with no issues |
| **B** | `evaluate_pilots_with_thinking_agent` | Every 6h | AI suggests outcome with reasoning |

**AI Content Generation:** Checklist items can be auto-generated with AI content via "Generate Content" button.

### Pilot Dashboard (Session 595)

**API:** `GET /api/pilots/dashboard/`

Dedicated dashboard showing:
- Running pilots with auto-complete countdown
- Completed pilots with outcomes and learnings
- Success rate metrics

### Experiment Tracking Registry (Session 596)

Connects pilots to formal experiments with KPI ownership:

| API Endpoint | Method | Description |
|--------------|--------|-------------|
| `/api/experiments/` | GET | List all experiments |
| `/api/experiments/portfolio/` | GET | Portfolio metrics & KPI owners |
| `/api/experiments/<id>/update-kpi/` | POST | Update current KPI value |
| `/api/experiments/<id>/complete/` | POST | Mark experiment complete |

**Experiment Model:**
- Auto-created when pilot starts
- Extracts KPIs from AI-generated success_metrics
- Tracks: kpi_owner, primary_kpi, target_value, current_value
- Status: running, success, failure, inconclusive

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [AGENTS.md](AGENTS.md) - Agent reference
- [SPIDERS.md](SPIDERS.md) - Spider network
- [SCIFI_FEATURES.md](SCIFI_FEATURES.md) - Sci-fi features
