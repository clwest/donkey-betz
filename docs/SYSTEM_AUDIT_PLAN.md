# System Audit Plan - Complete Feature Discovery & Integration Verification

**Created:** December 21, 2025 (Session 523)
**Purpose:** Systematically discover, document, and verify ALL system features are properly connected and learning from each other.
**Approach:** Sequential agents (Option A) - safer, more thorough

---

## Why This Audit?

In Session 523, we discovered the **Intelligent Prompting System** (built in Sessions 264-266) existed but wasn't wired up to ContentWriterAgent. The sophisticated infrastructure was there but unused.

**How many other features exist but aren't connected?**

This audit will:
1. **Discover** every feature, service, agent, model, and capability
2. **Verify** each is properly connected to the rest of the system
3. **Check** learning loops - does it learn from outcomes?
4. **Identify** gaps, orphaned code, and integration opportunities

---

## Phase 1: Discovery Agents

Before we can audit, we need to FIND everything. Each agent creates a discovery document.

### Agent 1.1: Code Discovery - Backend Services
**Scope:** Find all Python services, utilities, and business logic
**Files to scan:**
```
core/services/*.py
core/super_platform/*.py
core/prompts/*.py
core/assistant/*.py
ai_core/spiders/*.py
```
**Output:** `docs/audits/discovery_backend_services.md`
**Questions to answer:**
- What services exist?
- What does each one do?
- What imports/uses each service?
- Are there services that nothing imports?

---

### Agent 1.2: Code Discovery - Agents
**Scope:** Find ALL agents (core, legacy, specialized)
**Files to scan:**
```
core/agents/**/*.py
agents/*.py (legacy)
core/agent_router.py
```
**Output:** `docs/audits/discovery_agents.md`
**Questions to answer:**
- Complete list of all agent classes
- Which are in the router? Which aren't?
- Which have learning hooks? Which don't?
- Which use the prompting system? Which don't?
- What tools does each agent have access to?

---

### Agent 1.3: Code Discovery - Database Models
**Scope:** Find ALL database models and their relationships
**Files to scan:**
```
core/models*.py
core/models/**/*.py
content/models.py
```
**Output:** `docs/audits/discovery_database_models.md`
**Questions to answer:**
- Complete list of all models
- Foreign key relationships (what connects to what?)
- Which models have no foreign keys pointing to them (orphaned)?
- Which models are never queried in views/services?

---

### Agent 1.4: Code Discovery - API Endpoints
**Scope:** Find ALL API endpoints and views
**Files to scan:**
```
core/urls.py
core/views*.py
ai_core/urls.py
```
**Output:** `docs/audits/discovery_api_endpoints.md`
**Questions to answer:**
- Complete list of all endpoints
- What view/function handles each?
- Which endpoints are called by frontend?
- Which endpoints have no frontend callers (dead)?

---

### Agent 1.5: Code Discovery - Celery Tasks
**Scope:** Find ALL background tasks and schedules
**Files to scan:**
```
core/tasks.py
core/celery.py
```
**Output:** `docs/audits/discovery_celery_tasks.md`
**Questions to answer:**
- Complete list of all @shared_task functions
- Which are in celery_beat schedule?
- Which are called manually only?
- Which have never run (check logs)?

---

### Agent 1.6: Code Discovery - Frontend Features
**Scope:** Find ALL frontend tabs, panels, and JavaScript functions
**Files to scan:**
```
ai_core/templates/ai_image_studio.html
ai_core/templates/components/**/*.html
static/js/*.js
```
**Output:** `docs/audits/discovery_frontend_features.md`
**Questions to answer:**
- All main tabs and sub-tabs
- All JavaScript functions and what they do
- Which API endpoints does each feature call?
- Which features show "coming soon" or mock data?

---

### Agent 1.7: Code Discovery - Discord Commands
**Scope:** Find ALL Discord bot commands
**Files to scan:**
```
core/services/discord_bot.py
```
**Output:** `docs/audits/discovery_discord_commands.md`
**Questions to answer:**
- Complete list of all slash commands
- What does each command do?
- Which commands call which backend services?
- Which commands are broken/incomplete?

---

### Agent 1.8: Code Discovery - External Integrations
**Scope:** Find ALL external API integrations
**Files to scan:**
```
core/services/*.py (look for API calls)
ai_core/spiders/**/*.py
content/image_generation.py
content/video_generation.py
```
**Output:** `docs/audits/discovery_external_integrations.md`
**Questions to answer:**
- Stability AI - what features?
- Runway ML - what features?
- ElevenLabs - what features?
- DaVinci Resolve - what features?
- OpenAI/GPT - where used?
- All spider data sources
- Any other external APIs?

---

## Phase 2: Feature Domain Audits

After discovery, we audit each feature domain for connectivity and learning.

### Agent 2.1: Prompting System Audit
**Scope:** Complete prompting infrastructure
**Components to verify:**
- [ ] `core/prompts/registry.py` - PLATFORM_CONTEXT, agent prompts
- [ ] `core/prompts/tool_descriptions.py` - tool routing
- [ ] `core/super_platform/prompt_builder.py` - DynamicPromptBuilder
- [ ] `core/super_platform/coordinator.py` - SuperPlatformCoordinator
- [ ] `core/super_platform/query_classifier.py` - intent classification
- [ ] `core/super_platform/context_aggregator.py` - multi-source context
**Output:** `docs/audits/audit_prompting_system.md`
**Verify:**
- Which agents use DynamicPromptBuilder?
- Which agents use PLATFORM_CONTEXT?
- Is SuperPlatformCoordinator used anywhere?
- Are all prompt sections being injected?

---

### Agent 2.2: Sci-Fi Features Audit
**Scope:** All 15 sci-fi features from Sessions 247-260
**Components to verify:**
- [ ] Memory Palace (persistent memory with retrieval)
- [ ] Mood System (emotional states affect behavior)
- [ ] Evolution System (XP, levels, progression)
- [ ] Time Travel Debugging (replay agent decisions)
- [ ] Agent Dreams (idle creative thoughts)
- [ ] Agent Conversations (real-time AI-to-AI chat)
- [ ] Hive Mind Mode (collective problem-solving)
- [ ] Rivalries/Alliances (agent relationships)
- [ ] Personality Profiles (distinct personalities)
- [ ] Memory Clusters (grouped memories)
- [ ] Prophecies/Predictions (outcome predictions)
- [ ] Time Capsules (messages to future selves)
- [ ] Agent Learning (knowledge sharing)
- [ ] Collective Intelligence (learning loops)
- [ ] Spider Integration (agents use spider data)
**Output:** `docs/audits/audit_scifi_features.md`
**Verify:**
- Does each feature have database models?
- Does each feature have API endpoints?
- Does each feature have frontend UI?
- Is each feature used by agents?
- Do features learn from outcomes?

---

### Agent 2.3: Content Creation Audit
**Scope:** All content generation capabilities
**Components to verify:**
- [ ] Image Generation (Stability AI - 13 features)
- [ ] Video Generation (Runway ML - 6 features, Gen-4 Aleph)
- [ ] Audio Generation (ElevenLabs - TTS, voiceovers)
- [ ] 3D Generation
- [ ] Character Training (FLUX LoRA)
- [ ] DaVinci Resolve (color grading, rendering)
- [ ] Voice Cloning Pipeline
- [ ] Voice Marketplace
- [ ] Podcast Generation
- [ ] AI Series Workflow
- [ ] Content Writer Agent
- [ ] 80+ style presets
**Output:** `docs/audits/audit_content_creation.md`
**Verify:**
- Does each capability work end-to-end?
- Is output tracked in database?
- Does it learn from user feedback?
- Is it connected to spider intelligence?
- Can it be triggered autonomously?

---

### Agent 2.4: Spider Network Audit
**Scope:** Complete spider data pipeline
**Components to verify:**
- [ ] 72 registered spiders
- [ ] Spider registry and categories
- [ ] Data fetching (Celery tasks)
- [ ] Raw data storage (SpiderData model)
- [ ] Embedding generation (SpiderDataEmbedding)
- [ ] Smart Trending Service
- [ ] Unified Intelligence Search
- [ ] Spider-to-agent data flow
- [ ] Topic filtering and relevance
**Output:** `docs/audits/audit_spider_network.md`
**Verify:**
- Which spiders actually fetch data?
- Which spiders are broken?
- Is embedding pipeline working?
- Do agents receive spider data?
- Is data fresh (< 72 hours)?

---

### Agent 2.5: Learning System Audit
**Scope:** All learning loops and bridges
**Components to verify:**
- [ ] 8 Learning Bridges (apps.py)
  - Agent Execution Bridge
  - Application Outcome Bridge
  - Revenue Attribution Bridge
  - Advisor Feedback Bridge
  - Collaboration Bridge
  - Personalization Bridge
  - Sports Betting Bridge
  - Spider Data Bridge
- [ ] Collective Intelligence service
- [ ] Knowledge sharing between agents
- [ ] Outcome tracking
- [ ] ML Scoring Engine (XGBoost + SHAP)
**Output:** `docs/audits/audit_learning_system.md`
**Verify:**
- Are signals firing for each bridge?
- Is outcome data being recorded?
- Do agents improve over time?
- Is ML model being trained?

---

### Agent 2.6: Autonomous Systems Audit
**Scope:** All autonomous/self-running features
**Components to verify:**
- [ ] Autonomous Content Studio (3-agent debates)
- [ ] 14 Autonomous Situations
- [ ] Situation Triggers
- [ ] Event-driven automation
- [ ] Celery Beat schedules
- [ ] Self-renewal (does it schedule next run?)
**Output:** `docs/audits/audit_autonomous_systems.md`
**Verify:**
- Does each situation actually run?
- Are debates happening?
- Is output being generated?
- Is performance tracked?
- Does it adapt based on outcomes?

---

### Agent 2.7: Legal Assistant Audit
**Scope:** Pro Se Legal Assistant features
**Components to verify:**
- [ ] Case Intake Form (CaseProfile, Party, Attorney, Child)
- [ ] Document Upload & OCR
- [ ] Motion Analysis
- [ ] Motion Rewriter (JDF format)
- [ ] Conferral Email Generation
- [ ] Mythology/Anti-Hallucination system
- [ ] 12 legal tools
- [ ] Document threading
- [ ] Response session UI
**Output:** `docs/audits/audit_legal_assistant.md`
**Verify:**
- Does mythology prevent hallucinations?
- Is case context properly loaded?
- Do conferral emails address correct parties?
- Is document threading working?

---

### Agent 2.8: Business Intelligence Audit
**Scope:** Business research and strategy features
**Components to verify:**
- [ ] Competitor Analysis Agent
- [ ] Customer Research Agent
- [ ] Brand Strategy Agent
- [ ] Marketing Strategy Agent
- [ ] Business Content Strategy Agent
- [ ] Campaign Orchestrator Agent
- [ ] Project creation from research
- [ ] Unified Intelligence Search
- [ ] Revenue tracking
- [ ] Opportunity scoring
**Output:** `docs/audits/audit_business_intelligence.md`
**Verify:**
- Do agents chain context properly?
- Is prior research injected?
- Are projects created from research?
- Is revenue attributed correctly?

---

### Agent 2.9: Revenue & Opportunity Audit
**Scope:** All 6 phases of Creative Intelligence Empire
**Components to verify:**
- [ ] Phase 1: Opportunity Engine (scoring)
- [ ] Phase 2: Revenue Reality (tracking)
- [ ] Phase 3: Team Power (multi-agent collab)
- [ ] Phase 4: Smart Distribution (where to sell)
- [ ] Phase 5: Learning Loop (improve from success)
- [ ] Phase 6: Proactive System (alerts)
- [ ] Opportunity model and scoring
- [ ] Revenue tracking
- [ ] A/B Testing framework
- [ ] Goal tracking
**Output:** `docs/audits/audit_revenue_opportunity.md`
**Verify:**
- Is opportunity scoring working?
- Is revenue being tracked?
- Are A/B tests running?
- Are goals being tracked?
- Does system learn from outcomes?

---

### Agent 2.10: User Experience Audit
**Scope:** User-facing features and personalization
**Components to verify:**
- [ ] User Profile System (interview, preferences)
- [ ] Personal Assistant Agent
- [ ] Preferences tab
- [ ] Project management (create, edit, export)
- [ ] Content export (4 formats)
- [ ] Content editing modal
- [ ] Gallery and history
- [ ] Agent profile viewing
**Output:** `docs/audits/audit_user_experience.md`
**Verify:**
- Is user profile complete?
- Are preferences used by agents?
- Is history properly tracked?
- Can users export their content?

---

### Agent 2.11: Development Agents Audit
**Scope:** Code generation and DevOps features
**Components to verify:**
- [ ] Code Generator Agent
- [ ] Full Stack Developer Agent
- [ ] Code Review Agent
- [ ] DevOps Agent
- [ ] Blockchain Audit Agents
- [ ] Stock Audit Agents
**Output:** `docs/audits/audit_development_agents.md`
**Verify:**
- Do agents generate working code?
- Is code review accurate?
- Are blockchain/stock audits running?

---

### Agent 2.12: Workflow Orchestration Audit
**Scope:** Multi-step workflow system
**Components to verify:**
- [ ] 6 defined workflows
  - research_and_create_logos
  - youtube_thumbnail_package
  - brand_identity_package
  - product_photography_kit
  - video_thumbnail_series
  - logo_to_video
- [ ] Workflow Agent
- [ ] Step execution
- [ ] Error handling
- [ ] Result aggregation
**Output:** `docs/audits/audit_workflow_orchestration.md`
**Verify:**
- Does each workflow complete end-to-end?
- Are intermediate results saved?
- Does it recover from failures?

---

## Phase 3: Integration Verification

After domain audits, verify cross-cutting concerns.

### Agent 3.1: Data Flow Verification
**Scope:** Trace data through entire system
**Traces to verify:**
1. Spider → Embedding → Agent Prompt → Output
2. User Input → Classification → Agent → Response
3. Content Creation → Project → Export
4. Opportunity → Application → Outcome → Learning
5. Agent Action → Learning Bridge → Collective Intelligence
**Output:** `docs/audits/verify_data_flows.md`

---

### Agent 3.2: Learning Loop Verification
**Scope:** Verify system learns from itself
**Loops to verify:**
1. Agent output → User feedback → Agent improvement
2. Spider data → Content → Performance → Spider priority
3. Opportunity → Application → Success/Fail → Scoring model
4. A/B Test → Winner → Apply to system
**Output:** `docs/audits/verify_learning_loops.md`

---

### Agent 3.3: Connectivity Matrix
**Scope:** Create matrix of what connects to what
**Output:** `docs/audits/connectivity_matrix.md`
**Format:**
| Component | Uses | Used By | Learning Hook |
|-----------|------|---------|---------------|
| ContentWriterAgent | SmartTrending, GPT | PersonalAssistant | Yes |
| etc. | | | |

---

## Phase 4: Gap Analysis & Action Plan

### Agent 4.1: Gap Analysis
**Scope:** Identify all gaps and issues found
**Output:** `docs/audits/gap_analysis.md`
**Categories:**
1. **Orphaned Features** - exist but nothing uses them
2. **Broken Connections** - should be connected but aren't
3. **Missing Learning** - no outcome tracking
4. **Dead Code** - never executed
5. **Mock Data** - showing fake data instead of real

---

### Agent 4.2: Integration Action Plan
**Scope:** Prioritized plan to fix all gaps
**Output:** `docs/audits/integration_action_plan.md`
**Format:**
| Priority | Gap | Fix | Effort | Impact |
|----------|-----|-----|--------|--------|
| P0 | Prompting not wired to X | Add import + call | 1 hour | High |
| etc. | | | | |

---

## Execution Instructions

### For Each Agent Session:

1. **Start fresh session** (clear context)
2. **Read this plan** and your specific agent scope
3. **Read CLAUDE.md** for system overview
4. **Execute discovery/audit** for your scope
5. **Create output document** in `docs/audits/`
6. **Update this plan** with completion status

### Agent Checklist Template:
```markdown
## Agent X.Y: [Name]
- [ ] Read scope and files
- [ ] Scan all relevant code
- [ ] Document findings
- [ ] Identify gaps
- [ ] Create output document
- [ ] Mark complete in this plan
```

### Completion Tracking:
| Agent | Status | Date | Findings Doc |
|-------|--------|------|--------------|
| 1.1 Backend Services | **Complete** | 2025-12-21 | discovery_backend_services.md |
| 1.2 Agents | **Complete** | 2025-12-21 | discovery_agents.md |
| 1.3 Database Models | **Complete** | 2025-12-21 | discovery_database_models.md |
| 1.4 API Endpoints | **Complete** | 2025-12-21 | discovery_api_endpoints.md |
| 1.5 Celery Tasks | **Complete** | 2025-12-21 | discovery_celery_tasks.md |
| 1.6 Frontend Features | **Complete** | 2025-12-21 | discovery_frontend_features.md |
| 1.7 Discord Commands | **Complete** | 2025-12-21 | discovery_discord_commands.md |
| 1.8 External Integrations | **Complete** | 2025-12-21 | discovery_external_integrations.md |
| 2.1 Prompting System | **Complete** | 2025-12-21 | audit_prompting_system.md |
| 2.2 Sci-Fi Features | Not Started | | |
| 2.3 Content Creation | Not Started | | |
| 2.4 Spider Network | Not Started | | |
| 2.5 Learning System | **Complete** | 2025-12-21 | audit_learning_system.md |
| 2.6 Autonomous Systems | **Complete** | 2025-12-21 | audit_autonomous_systems.md |
| 2.7 Legal Assistant | Not Started | | |
| 2.8 Business Intelligence | Not Started | | |
| 2.9 Revenue & Opportunity | Not Started | | |
| 2.10 User Experience | Not Started | | |
| 2.11 Development Agents | Not Started | | |
| 2.12 Workflow Orchestration | Not Started | | |
| 3.1 Data Flow Verification | Not Started | | |
| 3.2 Learning Loop Verification | Not Started | | |
| 3.3 Connectivity Matrix | Not Started | | |
| 4.1 Gap Analysis | Not Started | | |
| 4.2 Integration Action Plan | Not Started | | |

---

## Expected Outcomes

After completing all agents:

1. **Complete Feature Inventory** - Know EVERYTHING the system has
2. **Connectivity Map** - Know what connects to what
3. **Gap List** - Know what's broken/disconnected
4. **Action Plan** - Prioritized fixes
5. **Learning Verification** - Confirm system learns from itself

---

## Notes

- Each agent should take 1-2 hours
- Total estimated time: 25-30 hours across sessions
- Can parallelize Phase 1 agents (discovery)
- Phase 2+ should be sequential (builds on discovery)
- Update this document as you complete agents

---

*This audit will transform a collection of features into a unified, self-learning system.*
