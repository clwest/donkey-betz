# Agent 1.2: Agents Discovery

**Date:** December 21, 2025
**Status:** Complete
**Total Agents Discovered:** 64+ agent classes

---

## Summary

Discovered **64+ agent classes** across 2 main locations:
- `core/agents/` - **53 active agents** (canonical location)
- `agents/` - **35 legacy agents** (many duplicates, some deprecated)

**CRITICAL GAP:** Only **1 agent** (ContentWriterAgent) uses the intelligent prompting system!

---

## 1. Routable Agents (AGENT_MAP) - 42 Total

These agents are registered in `core/agent_router.py` and can be called via the router:

### Creation Agents (4)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| ImageAgent | Image generation (logos, banners) | Yes | No |
| VideoAgent | Video generation (text-to-video) | Yes | No |
| AudioAgent | Audio generation (TTS, voiceovers) | Yes | No |
| ThreeDAgent | 3D model generation | Yes | No |

### Editing Agents (2)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| ImageEditingAgent | Image editing (upscale, remove bg) | Yes | No |
| VideoEditingAgent | Video editing (trim, effects) | Yes | No |

### Research Agents (1)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| ResearchAgent | Web search + spider network queries | Yes | No |

### Writing Agents (1)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| ContentWriterAgent | Blog posts, articles, podcasts | Yes | **YES** |

### Strategy Agents (4)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| ContentStrategyAgent | Content recommendations | Yes | No |
| BrandIdentityAgent | Brand consistency | Yes | No |
| SEOOptimizerAgent | Keywords, hashtags | Yes | No |
| SocialMediaAgent | Platform-specific strategy | Yes | No |

### Executive Agents (4)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| CTOAgent | Technical planning | Yes | No |
| COOAgent | Operations planning | Yes | No |
| CreativeDirectorAgent | Creative guidance | Yes | No |
| MeetingCoordinatorAgent | Agent-to-agent meetings | Yes | No |

### Analysis Agents (2)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| TrendAnalysisAgent | Spider intelligence analysis | Yes | No |
| OpportunityScoringAgent | Opportunity scoring | Yes | No |

### Training Agents (2)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| CharacterTrainingAgent | FLUX LoRA training | Yes | No |
| TrainedCreationAgent | LoRA image generation | Yes | No |

### Security Agents (2)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| MemoryIsolationAgent | Memory isolation | Yes | No |
| ContentAuditAgent | Content security audit | Yes | No |

### Business Research Agents (2)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| CompetitorAnalysisAgent | Competitor SWOT | Yes | No |
| CustomerResearchAgent | Customer personas | Yes | No |

### Legal Agents (1)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| LegalDocDrafterAgent | Legal document drafting | Yes | No |

### Development Agents (4)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| CodeGeneratorAgent | Generate code | Yes | No |
| FullStackDeveloperAgent | Full-stack features | Yes | No |
| CodeReviewAgent | Code review | Yes | No |
| DevOpsAgent | CI/CD, infrastructure | Yes | No |

### Blockchain Audit Agents (1 + 4 sub-agents)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| BlockchainAuditCoordinator | Orchestrates blockchain audits | Yes | No |
| SmartContractAuditorAgent | Solidity vulnerabilities | Yes | No |
| TransactionMonitorAgent | Transaction monitoring | Yes | No |
| WhaleWatcherAgent | Large token movements | Yes | No |
| ExploitDetectorAgent | Known exploit matching | Yes | No |

### Stock Audit Agents (1 + 5 sub-agents)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| StockAuditCoordinator | Orchestrates stock audits | Yes | No |
| BullCaseAgent | Bull case analysis | Yes | No |
| BearCaseAgent | Bear case analysis | Yes | No |
| StockAnalystAgent | Stock analysis | Yes | No |
| SignalScannerAgent | Signal scanning | Yes | No |
| InstitutionalWatcherAgent | Institutional activity | Yes | No |

### Content Studio Agents (4)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| AutonomousContentStudioCoordinator | 3-agent debates | Yes | No |
| TopicMinerAgent | Topic discovery | Yes | No |
| ContrarianAgent | Devil's advocate | Yes | No |
| PerformanceAnalystAgent | Content performance | Yes | No |

### Podcast Agents (4)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| PodcastCoordinatorAgent | Podcast orchestration | Yes | No |
| DebateAdvocateAgent | Advocate position | Yes | No |
| DebateSkepticAgent | Skeptic position | Yes | No |
| ModeratorAgent | Debate moderation | Yes | No |

### Rendering Agents (1)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| ResolveAgent | DaVinci Resolve rendering | Yes | No |

### AI Series Agents (1)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| AISeriesWorkflowAgent | Content series workflow | Yes | No |

### Orchestration Agents (2)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| WorkflowAgent | Multi-step workflows | Yes | No |
| CampaignOrchestratorAgent | Marketing campaigns | Yes | No |

### Entry Point (1)
| Agent | Purpose | Learning Hooks | Prompting System |
|-------|---------|----------------|------------------|
| PersonalAssistantAgent | Main user interaction | Yes | No |

---

## 2. Non-Routable Agents (In core/agents/ but NOT in AGENT_MAP)

These agents exist but are not registered in the router:

| Agent | Location | Purpose | In Router |
|-------|----------|---------|-----------|
| MarketIntelligenceAgent | analysis/ | SEC filings, stocks | **NO** |
| BrandStrategyAgent | business/ | Brand positioning | **NO** |
| MarketingStrategyAgent | business/ | Marketing channels | **NO** |
| BusinessContentStrategyAgent | business/ | Content pillars | **NO** |
| WorkflowOrchestrationAgent | core/agents/ | Workflow packages | **NO** |
| OpportunityPipelineAgent | core/agents/ | Opportunity pipeline | **NO** |
| ContentExecutorAgent | core/agents/ | Content generation | **NO** |
| NarrativeHistorianAgent | narrative/ | Narrative history | **NO** |
| TrendBreakDetectorAgent | narrative/ | Trend detection | **NO** |
| CulturalImpactAgent | narrative/ | Cultural analysis | **NO** |
| NarrativeDriftCoordinator | narrative/ | Narrative drift | **NO** |
| NarrativeMythologyValidator | narrative/ | Mythology validation | **NO** |

---

## 3. Legacy Agents (`agents/`)

The `agents/` directory contains legacy/deprecated agents. Many are duplicates:

### Active Legacy Agents (Used)
| Agent | Status | Notes |
|-------|--------|-------|
| base_agent.py | Active | Different from core/agents/base_agent.py |
| time_travel_mixin.py | Active | Used by core/agents/base_agent.py |
| bookmaker_agent.py | Active | Sports betting |
| creation_agent.py | Active | Generic creation |
| ai_project_builder.py | Active | AI project building |
| live_learning_orchestrator.py | Active | Live learning |
| content_executor.py | Active | Content execution |
| opportunity_pipeline_orchestrator.py | Active | Opportunity pipeline |

### Deprecated Legacy Agents (in `agents/_deprecated/`)
All have duplicates in `core/agents/`:
- image_agent.py
- video_agent.py
- audio_agent.py
- research_agent.py
- cto_agent.py
- coo_agent.py
- creative_director_agent.py
- brand_identity_agent.py
- content_strategy_agent.py
- seo_optimizer_agent.py
- social_media_agent.py
- opportunity_scoring_agent.py
- trend_analysis_agent.py
- character_training_agent.py
- trained_creation_agent.py
- three_d_generation_agent.py
- memory_isolation_agent.py
- meeting_coordinator_agent.py

---

## 4. Learning Hooks Analysis

### All 64 core/agents/ files have learning hooks
The base_agent.py provides:
- `_record_learning_outcome()` - Records execution outcomes
- Learning loop integration via `get_learning_loop_service()`
- Knowledge attribution tracking

**All agents inherit these hooks from BaseAgent.**

---

## 5. Prompting System Analysis (CRITICAL GAP!)

### Intelligent Prompting System Components:
- `DynamicPromptBuilder` - Context-aware prompts
- `PLATFORM_CONTEXT` - System capabilities
- Memory Palace integration
- Mood/Evolution influence
- User preferences

### Agents Using Intelligent Prompting:
| Agent | Status |
|-------|--------|
| ContentWriterAgent | **YES** (Session 523) |
| All other 41 routable agents | **NO** |

**GAP:** Only 1 out of 42 routable agents (2.4%) uses the intelligent prompting system!

---

## 6. Agent Registry (core/agents/registry.py)

The AgentRegistry provides:
- `get_agent(name)` - Get agent by name
- `list_agents()` - List all registered agents
- `find_best_agent(task)` - Semantic matching
- `execute_agent(name, task)` - Execute with context

---

## 7. Gaps and Issues Identified

### CRITICAL: Prompting System Disconnected
- **41 agents** are NOT using DynamicPromptBuilder
- They use hardcoded system prompts instead
- Missing: PLATFORM_CONTEXT, memory palace, mood, evolution, preferences

### Missing from Router (12 agents):
These agents exist but aren't in AGENT_MAP:
1. MarketIntelligenceAgent
2. BrandStrategyAgent
3. MarketingStrategyAgent
4. BusinessContentStrategyAgent
5. WorkflowOrchestrationAgent
6. OpportunityPipelineAgent
7. ContentExecutorAgent
8. NarrativeHistorianAgent
9. TrendBreakDetectorAgent
10. CulturalImpactAgent
11. NarrativeDriftCoordinator
12. NarrativeMythologyValidator

### Legacy Duplication:
- 18 agents in `agents/_deprecated/` duplicate `core/agents/`
- Should be fully migrated

---

## 8. Agent Counts Summary

| Category | Count |
|----------|-------|
| Routable agents (in AGENT_MAP) | 42 |
| Non-routable agents (core/agents/) | 12 |
| Deprecated agents (agents/_deprecated/) | 18 |
| Active legacy agents | 8 |
| **Total unique agent classes** | **54+** |

---

## 9. Recommendations

### P0 - Critical
1. **Wire prompting system to all agents** - Only ContentWriterAgent uses it
2. **Add missing agents to router** - 12 agents exist but aren't routable

### P1 - High
3. **Clean up legacy agents** - Remove agents/_deprecated/
4. **Document agent capabilities** - Some agents have overlapping purposes

### P2 - Medium
5. **Add semantic routing** - Already partially implemented in router
6. **Standardize tool access** - Verify each agent has correct tools

---

*Generated by Agent 1.2: Agents Discovery*
