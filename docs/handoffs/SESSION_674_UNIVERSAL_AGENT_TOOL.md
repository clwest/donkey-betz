# Session 674: Universal Agent Tool

**Date:** January 5, 2026
**Focus:** Connect PA (Brain) to ALL Agents (Organs) with One Tool

## Overview

Session 673 connected the PA to the ML Pipeline with 4 new tools (77 → 81). However, analysis revealed that only 30 of 72 agents (42%) were accessible via PA tools. This session adds the `universal_agent_tool` which connects the remaining 42 agents with a single, flexible tool.

## Before vs After

| Metric | Before (Session 673) | After (Session 674) |
|--------|---------------------|---------------------|
| Agents with PA tools | 30 (42%) | **72 (100%)** |
| PA Tool count | 81 | **82** |
| Agent categories accessible | 8 | **13** |

## The Universal Agent Tool

### How It Works

```python
# User: "Analyze NVDA stock for me"
# PA calls:
universal_agent_tool(
    agent_name="StockAnalystAgent",
    task="Analyze NVDA stock performance and provide recommendations",
    context={"symbol": "NVDA", "timeframe": "1M"}
)

# User: "Audit this smart contract for vulnerabilities"
# PA calls:
universal_agent_tool(
    agent_name="SmartContractAuditorAgent",
    task="Audit smart contract for security vulnerabilities",
    context={"contract_address": "0x..."}
)

# User: "Create a podcast debate about AI regulation"
# PA calls:
universal_agent_tool(
    agent_name="PodcastCoordinatorAgent",
    task="Create a podcast debate about AI regulation in 2026",
    context={"topic": "AI regulation"}
)
```

### Newly Accessible Agent Categories

| Category | Agents | Count |
|----------|--------|-------|
| **Blockchain** | BlockchainAuditCoordinator, SmartContractAuditorAgent, TransactionMonitorAgent, WhaleWatcherAgent, ExploitDetectorAgent | 5 |
| **Stocks** | StockAuditCoordinator, StockAnalystAgent, MarketMovementMonitorAgent, InstitutionalWatcherAgent, MarketAnomalyDetectorAgent, BullCaseAgent, BearCaseAgent, SignalScannerAgent, MarketIntelligenceCoordinator | 9 |
| **Development** | CodeGeneratorAgent, FullStackDeveloperAgent, CodeReviewAgent, DevOpsAgent | 4 |
| **Podcast** | PodcastCoordinatorAgent, DebateAdvocateAgent, DebateSkepticAgent, ModeratorAgent | 4 |
| **Markets** | PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector | 3 |
| **Narrative** | NarrativeDriftCoordinator, NarrativeHistorianAgent, TrendBreakDetectorAgent, CulturalImpactAgent | 4 |
| **Content Studio** | AutonomousContentStudioCoordinator, TopicMinerAgent, ContrarianAgent, PerformanceAnalystAgent | 4 |
| **Rendering** | ResolveAgent | 1 |
| **System** | SystemIntelligenceAgent, ThinkingAgent | 2 |
| **Campaign** | CampaignOrchestratorAgent, AISeriesWorkflowAgent | 2 |
| **Security** | MemoryIsolationAgent, ContentAuditAgent | 2 |
| **Legal** | LegalDocDrafterAgent | 1 |
| **Market Intelligence** | MarketIntelligenceAgent | 1 |
| **TOTAL** | | **42** |

## Files Modified

| File | Changes |
|------|---------|
| `core/prompts/tool_descriptions.py` | +55 lines - comprehensive tool description |
| `core/assistant/tool_definitions.py` | +78 lines - tool schema with 46-agent enum |
| `core/personal_ai_assistant_enhanced.py` | +85 lines - handler using AgentRouter |
| `CLAUDE.md` | Updated stats (82 PA tools) |
| `docs/CAPABILITIES.md` | Updated PA Tools entry |
| `docs/current/ASSISTANT_SYSTEM.md` | Added Universal Agent Tool section |

## Implementation Details

### Tool Definition

```python
{
    "type": "function",
    "name": "universal_agent_tool",
    "parameters": {
        "properties": {
            "agent_name": {
                "type": "string",
                "enum": [46 agent names],  # Explicitly enumerated
                "description": "Name of the agent to invoke"
            },
            "task": {
                "type": "string",
                "description": "The task for the agent"
            },
            "context": {
                "type": "object",
                "description": "Optional context (symbol, contract_address, topic, etc.)"
            }
        },
        "required": ["agent_name", "task"]
    }
}
```

### Handler Flow

```
universal_agent_tool(agent_name, task, context)
    ↓
_handle_universal_agent_tool()
    ↓
AgentRouter(user=self.user)
    ↓
router.route(agent_name, task, context)
    ↓
Agent.execute(task, context, scifi_context, spider_context)
    ↓
AgentResult → Dict response
```

## Brain-Organ Architecture Complete

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERSONAL ASSISTANT (BRAIN)                    │
│                                                                  │
│  82 PA Tools                                                     │
│  ├── Creation Tools (6): image, video, audio, 3d, editing       │
│  ├── Strategy Tools (4): brand, seo, trend, social              │
│  ├── Business Tools (5): competitor, customer, brand, marketing │
│  ├── Executive Tools (6): cto, coo, creative, meeting           │
│  ├── ML Pipeline Tools (4): opportunities, tasks, pipeline, rev │
│  └── Universal Agent Tool (1): ALL OTHER AGENTS                 │
│                              ↓                                   │
│              ┌───────────────┴───────────────┐                   │
│              │      AgentRouter.route()      │                   │
│              └───────────────┬───────────────┘                   │
└──────────────────────────────┼──────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────┐
│                        72 AGENTS (ORGANS)                         │
│                                                                   │
│  Blockchain (5)  │  Stocks (9)    │  Development (4) │ Podcast(4)│
│  Markets (3)     │  Narrative (4) │  Content (4)     │ Render(1) │
│  System (2)      │  Campaign (2)  │  Security (2)    │ Legal (1) │
│  + 30 agents already accessible via dedicated tools               │
└──────────────────────────────────────────────────────────────────┘
```

## Testing

```bash
# Verify handler exists
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
print('Handler:', hasattr(EnhancedPersonalAIAssistant, '_handle_universal_agent_tool'))
"
# Output: Handler: True

# Verify tool definition
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
from core.assistant.tool_definitions import get_tool_definitions
tools = get_tool_definitions()
ut = next((t for t in tools if t['name'] == 'universal_agent_tool'), None)
print('Tool exists:', ut is not None)
print('Agents in enum:', len(ut['parameters']['properties']['agent_name']['enum']))
"
# Output: Tool exists: True, Agents in enum: 46
```

## Session 675 Recommendations

1. **Test End-to-End**: Test invoking various agents via the universal tool
2. **Add More Agents**: The enum has 46 agents, but AgentRouter has 72 - could expand
3. **Context Helpers**: Add smart context building based on agent type
4. **Usage Analytics**: Track which agents are invoked via universal tool
