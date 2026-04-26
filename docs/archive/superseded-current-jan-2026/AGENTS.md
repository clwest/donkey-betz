<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Agent inventory snapshot
>
> **Where to look now:**
> - [docs/AGENTS.md](/docs/AGENTS.md)
> - [docs/topics/agent-system.md](/docs/topics/agent-system.md)
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Agents Documentation

**Total Agents:** 71
**Routable Agents:** 68 (in AgentRouter)
**Non-Routable Sub-Agents:** 3 (used internally by coordinators)
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Agent Architecture](#agent-architecture)
3. [Agent Categories](#agent-categories)
4. [Complete Agent List](#complete-agent-list)
5. [Coordinator Teams](#coordinator-teams)
6. [Usage Examples](#usage-examples)

---

## Overview

All agents inherit from `BaseAgent` which provides:
- **TimeTravelMixin** - Decision replay and debugging
- **Learning Hooks** - Connected to collective intelligence
- **Memory Creation** - Automatic memory persistence
- **Sci-Fi Features** - Mood, evolution, relationships

### Agent Location
All agents are in `core/agents/` with subdirectories for categories:
```
core/agents/
├── base_agent.py              # Base class
├── personal_assistant_agent.py # Entry point
├── image_agent.py             # Creation
├── video_agent.py
├── audio_agent.py
├── three_d_agent.py
├── image_editing_agent.py     # Editing
├── video_editing_agent.py
├── research_agent.py          # Research
├── content_writer_agent.py    # Writing
├── workflow_agent.py          # Orchestration
├── resolve_agent.py           # Rendering
├── thinking_agent.py          # Special
├── technical_document_agent.py
├── strategy/                  # Strategy agents (4)
├── executive/                 # Executive agents (4)
├── analysis/                  # Analysis agents (3)
├── training/                  # Training agents (2)
├── security/                  # Security agents (2)
├── business/                  # Business agents (4)
├── legal/                     # Legal agents (1)
├── stocks/                    # Stock agents (9)
├── blockchain/                # Blockchain agents (5)
├── narrative/                 # Narrative agents (4)
├── content/                   # Content studio agents (3)
├── podcast/                   # Podcast agents (4)
└── markets/                   # Markets agents (3)
```

---

## Agent Architecture

### Routing Flow
```
User Request
     │
     ▼
PersonalAssistantAgent (Entry Point)
     │
     ▼
AgentRouter (Deterministic Lookup)
     │
     ▼
Specialized Agent (68 options)
     │
     ├── Tools Execution
     ├── Spider Context Injection
     ├── Sci-Fi Features (Mood, Memory, etc.)
     └── Learning Loop Recording
     │
     ▼
AgentResult Response
```

### Base Agent Features
```python
class BaseAgent:
    # Inherited by all agents
    - execute(task, context, scifi_context, spider_context)
    - create_memory(content, importance)
    - record_learning(outcome, details)
    - get_mood_modifier()
    - apply_xp_gain(amount)
```

---

## Agent Categories

### Creation Agents (4)

| Agent | Purpose | Tools |
|-------|---------|-------|
| **ImageAgent** | Generate images (logos, banners, illustrations) | Stability AI, DALL-E |
| **VideoAgent** | Generate videos (text-to-video, animations) | Runway ML |
| **AudioAgent** | Generate audio (TTS, voiceovers) | ElevenLabs |
| **ThreeDAgent** | Generate 3D models | Replicate |

### Editing Agents (2)

| Agent | Purpose | Operations |
|-------|---------|------------|
| **ImageEditingAgent** | Edit images | Upscale, remove bg, inpaint, outpaint, variations, style transfer |
| **VideoEditingAgent** | Edit videos | Trim, effects, text overlay, transitions |

### Strategy Agents (4)

| Agent | Purpose | Output |
|-------|---------|--------|
| **ContentStrategyAgent** | Content recommendations based on trends | Strategy documents |
| **BrandIdentityAgent** | Brand consistency management | Brand guidelines |
| **SEOOptimizerAgent** | Hashtags, keywords, metadata | SEO recommendations |
| **SocialMediaAgent** | Platform-specific strategy | Platform-optimized content plans |

### Executive Agents (4)

| Agent | Purpose | Specialization |
|-------|---------|----------------|
| **CTOAgent** | Technical planning and analysis | Architecture, tech stack |
| **COOAgent** | Operations planning and risk | Process, efficiency |
| **CreativeDirectorAgent** | Creative guidance | Visual direction, style |
| **MeetingCoordinatorAgent** | Coordinate agent meetings | Multi-agent sessions |

### Analysis Agents (3)

| Agent | Purpose | Data Sources |
|-------|---------|--------------|
| **TrendAnalysisAgent** | Spider intelligence analysis | All 77 spiders |
| **OpportunityScoringAgent** | ML-based opportunity scoring | XGBoost + SHAP |
| **MarketIntelligenceAgent** | Market research and analysis | Financial spiders |

### Training Agents (2)

| Agent | Purpose | Technology |
|-------|---------|------------|
| **CharacterTrainingAgent** | FLUX LoRA character training | Replicate |
| **TrainedCreationAgent** | LoRA-based image generation | Custom models |

### Security Agents (2)

| Agent | Purpose | Features |
|-------|---------|----------|
| **MemoryIsolationAgent** | Memory isolation and security | Access control |
| **ContentAuditAgent** | Content compliance checking | Policy enforcement |

### Business Agents (4)

| Agent | Purpose | Output |
|-------|---------|--------|
| **CompetitorAnalysisAgent** | Competitor analysis, SWOT | Competitive reports |
| **CustomerResearchAgent** | Customer personas, pain points | User research |
| **BrandStrategyAgent** | Brand positioning | Strategy documents |
| **MarketingStrategyAgent** | Marketing campaigns | Campaign plans |

### Legal Agents (1)

| Agent | Purpose | Specialization |
|-------|---------|----------------|
| **LegalDocDrafterAgent** | Legal document drafting | Colorado family law |

### Development Agents (4)

| Agent | Purpose | Languages |
|-------|---------|-----------|
| **CodeGeneratorAgent** | Code generation | Python, JS, TS, Go, Rust |
| **FullStackDeveloperAgent** | Full-stack development | React, Django, Node |
| **CodeReviewAgent** | Code review and suggestions | All languages |
| **DevOpsAgent** | DevOps and CI/CD | Docker, K8s, GitHub Actions |

### Stock Audit Agents (9)

| Agent | Purpose | Role |
|-------|---------|------|
| **StockAuditCoordinator** | Coordinates stock analysis team | Coordinator |
| **StockAnalystAgent** | Fundamental analysis | Sub-agent |
| **MarketMovementMonitorAgent** | Price/volume monitoring | Sub-agent |
| **InstitutionalWatcherAgent** | Institutional activity | Sub-agent |
| **MarketAnomalyDetectorAgent** | Anomaly detection | Sub-agent |
| **BullCaseAgent** | Bullish arguments | Debate agent |
| **BearCaseAgent** | Bearish arguments | Debate agent |
| **SignalScannerAgent** | Signal detection | Sub-agent |
| **MarketIntelligenceCoordinator** | Daily briefings | Coordinator |

### Blockchain Audit Agents (5)

| Agent | Purpose | Focus |
|-------|---------|-------|
| **BlockchainAuditCoordinator** | Coordinates blockchain team | Coordinator |
| **SmartContractAuditorAgent** | Contract security auditing | Ethereum |
| **TransactionMonitorAgent** | Transaction monitoring | On-chain |
| **WhaleWatcherAgent** | Large holder tracking | Whale movements |
| **ExploitDetectorAgent** | Exploit detection | Security |

### Narrative Agents (4)

| Agent | Purpose | Tracks |
|-------|---------|--------|
| **NarrativeDriftCoordinator** | Coordinates narrative tracking | 30 narratives |
| **NarrativeHistorianAgent** | Historical context | Story arcs |
| **TrendBreakDetectorAgent** | Trend break detection | Shifts |
| **CulturalImpactAgent** | Cultural impact analysis | 8 domains |

### Content Studio Agents (4)

| Agent | Purpose | Role |
|-------|---------|------|
| **AutonomousContentStudioCoordinator** | Orchestrates content creation | Coordinator |
| **TopicMinerAgent** | Argues FOR trending topics | Debate agent |
| **ContrarianAgent** | Argues AGAINST saturation | Debate agent |
| **PerformanceAnalystAgent** | Historical data analysis | Data agent |

### Podcast Agents (4)

| Agent | Purpose | Voice |
|-------|---------|-------|
| **PodcastCoordinatorAgent** | Orchestrates podcast creation | - |
| **ModeratorAgent** | Moderates debates | Antoni |
| **DebateAdvocateAgent** | Argues for positions | Rachel |
| **DebateSkepticAgent** | Argues against positions | Clyde |

### Markets Agents (3)

| Agent | Purpose | Data Source |
|-------|---------|-------------|
| **PredictionMarketAnalyst** | Prediction market analysis | Kalshi |
| **SportsOddsAnalyst** | Sports betting analysis | The Odds API |
| **ArbitrageDetector** | Cross-book arbitrage | Multiple books |

### Orchestration Agents (5)

| Agent | Purpose | Scope |
|-------|---------|-------|
| **WorkflowAgent** | Multi-step workflow coordination | General |
| **WorkflowOrchestrationAgent** | Complex workflow management | Enterprise |
| **OpportunityPipelineAgent** | Opportunity processing | Income |
| **ContentExecutorAgent** | Content workflow execution | Content |
| **CampaignOrchestratorAgent** | Marketing campaigns | Marketing |

### Special Agents (3)

| Agent | Purpose | Features |
|-------|---------|----------|
| **ThinkingAgent** | Deep reasoning and evaluation | Extended thinking |
| **TechnicalDocumentAgent** | Technical documentation | Structured docs |
| **PersonalAssistantAgent** | Entry point, delegation | 77 tools |

### Rendering Agents (1)

| Agent | Purpose | Integration |
|-------|---------|-------------|
| **ResolveAgent** | Professional video rendering | DaVinci Resolve |

### Series Agents (1)

| Agent | Purpose | Output |
|-------|---------|--------|
| **AISeriesWorkflowAgent** | Multi-episode content series | Episode packages |

---

## Complete Agent List (71)

### Routable Agents (68)

```
1.  ImageAgent
2.  VideoAgent
3.  AudioAgent
4.  ThreeDAgent
5.  ImageEditingAgent
6.  VideoEditingAgent
7.  ResearchAgent
8.  ContentWriterAgent
9.  ContentStrategyAgent
10. BrandIdentityAgent
11. SEOOptimizerAgent
12. SocialMediaAgent
13. CTOAgent
14. COOAgent
15. CreativeDirectorAgent
16. MeetingCoordinatorAgent
17. TrendAnalysisAgent
18. OpportunityScoringAgent
19. MarketIntelligenceAgent
20. CharacterTrainingAgent
21. TrainedCreationAgent
22. MemoryIsolationAgent
23. ContentAuditAgent
24. CompetitorAnalysisAgent
25. CustomerResearchAgent
26. BrandStrategyAgent
27. MarketingStrategyAgent
28. LegalDocDrafterAgent
29. CodeGeneratorAgent
30. FullStackDeveloperAgent
31. CodeReviewAgent
32. DevOpsAgent
33. StockAuditCoordinator
34. StockAnalystAgent
35. MarketMovementMonitorAgent
36. InstitutionalWatcherAgent
37. MarketAnomalyDetectorAgent
38. BullCaseAgent
39. BearCaseAgent
40. SignalScannerAgent
41. MarketIntelligenceCoordinator
42. BlockchainAuditCoordinator
43. SmartContractAuditorAgent
44. TransactionMonitorAgent
45. WhaleWatcherAgent
46. ExploitDetectorAgent
47. NarrativeDriftCoordinator
48. NarrativeHistorianAgent
49. TrendBreakDetectorAgent
50. CulturalImpactAgent
51. AutonomousContentStudioCoordinator
52. TopicMinerAgent
53. ContrarianAgent
54. PerformanceAnalystAgent
55. PodcastCoordinatorAgent
56. ModeratorAgent
57. DebateAdvocateAgent
58. DebateSkepticAgent
59. PredictionMarketAnalyst
60. SportsOddsAnalyst
61. ArbitrageDetector
62. WorkflowAgent
63. WorkflowOrchestrationAgent
64. OpportunityPipelineAgent
65. ContentExecutorAgent
66. CampaignOrchestratorAgent
67. ThinkingAgent
68. TechnicalDocumentAgent
69. PersonalAssistantAgent
70. ResolveAgent
71. AISeriesWorkflowAgent
```

### Non-Routable Sub-Agents (3)

These are used internally by coordinators and not directly routable:
```
- TopicMinerAgent (used by AutonomousContentStudioCoordinator)
- ContrarianAgent (used by AutonomousContentStudioCoordinator)
- PerformanceAnalystAgent (used by AutonomousContentStudioCoordinator)
```

---

## Coordinator Teams

### 1. Stock Audit Team
**Coordinator:** StockAuditCoordinator
**Team:** StockAnalyst, MarketMovementMonitor, InstitutionalWatcher, MarketAnomalyDetector, BullCase, BearCase, SignalScanner

### 2. Blockchain Audit Team
**Coordinator:** BlockchainAuditCoordinator
**Team:** SmartContractAuditor, TransactionMonitor, WhaleWatcher, ExploitDetector

### 3. Narrative Drift Team
**Coordinator:** NarrativeDriftCoordinator
**Team:** NarrativeHistorian, TrendBreakDetector, CulturalImpact

### 4. Content Studio Team
**Coordinator:** AutonomousContentStudioCoordinator
**Team:** TopicMiner, Contrarian, PerformanceAnalyst

### 5. Market Intelligence Team
**Coordinator:** MarketIntelligenceCoordinator
**Team:** BullCase, BearCase, SignalScanner (shared with Stock Audit)

---

## Usage Examples

### Python - Direct Agent Use
```python
from core.agents import get_image_agent

agent = get_image_agent(user)
result = agent.execute(
    task="Create a cyberpunk logo for TechCorp",
    context={'style': 'neon', 'size': '1024x1024'},
    scifi_context={},
    spider_context={}
)
```

### Python - Via Router
```python
from core.agent_router import AgentRouter

router = AgentRouter(user=request.user)
result = router.route(
    "ImageAgent",
    "Create a minimalist logo",
    context={'style': 'minimal'}
)
```

### Python - Via Personal Assistant
```python
from core.agents.personal_assistant_agent import PersonalAssistantAgent

pa = PersonalAssistantAgent(user=request.user)
result = pa.execute(
    task="Research current AI trends and create a summary",
    context={},
    scifi_context={},
    spider_context={}
)
# PA will delegate to ResearchAgent automatically
```

### Discord
```
/agent-task agent:ImageAgent task:"Create a logo for my startup"
/agent-list
/ask Create a cyberpunk image
```

---

## Agent Development Guide

### Creating a New Agent

1. Create file in appropriate category directory
2. Inherit from `BaseAgent`
3. Define `tools` list with GPT function schemas
4. Implement tool handler methods
5. Register in `AgentRouter.AGENT_MAP`
6. Add to `core/agents/__init__.py` exports

```python
# core/agents/my_agent.py
from core.agents.base_agent import BaseAgent, AgentResult

class MyAgent(BaseAgent):
    name = "MyAgent"
    description = "Does something useful"

    tools = [
        {
            "type": "function",
            "function": {
                "name": "my_tool",
                "description": "Does the thing",
                "parameters": {...}
            }
        }
    ]

    def _my_tool(self, **kwargs) -> dict:
        # Implementation
        return {"result": "success"}
```

---

## Related Documentation

- [SERVICES.md](SERVICES.md) - Services that agents use
- [AUTONOMOUS_SYSTEMS.md](AUTONOMOUS_SYSTEMS.md) - Autonomous agent situations
- [SCIFI_FEATURES.md](SCIFI_FEATURES.md) - Agent sci-fi capabilities
