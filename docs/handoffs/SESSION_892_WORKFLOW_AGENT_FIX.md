---
originating_session: 892
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 892 - WorkflowAgent Multi-Step Orchestration Fix

**Date:** January 31, 2026
**Focus:** Fix multi-agent orchestration - "Research X and create a business plan" workflows
**Status:** Complete

---

## Problem Statement

User reported that the Main Assistant wasn't working well with Agents for complex multi-step requests like:
- "Research X company and create a business plan"
- "Create a brand package with logo, colors, and business model"
- Complex workflows that should research → strategize → create content → generate images

**Root Cause:** The `WorkflowAgent` only had **20 agents** in its `delegate_to_agent` tool enum, while the system has **76+ agents**. Critical agents were missing:
- `ContentWriterAgent` - can't create business plans!
- `BrandIdentityAgent` - can't create color palettes!
- `LegalDocDrafterAgent`, `SportsOddsAnalyst`, development agents, etc.

---

## Solution

### 1. Updated WorkflowAgent's Agent List (20 → 36 agents)

**File:** `core/agents/workflow_agent.py`

Added missing agents to both the `system_prompt` and the `delegate_to_agent` tool enum:

| Category | New Agents Added |
|----------|------------------|
| Writing & Content | ContentWriterAgent, PodcastCoordinatorAgent |
| Strategy & Branding | BrandIdentityAgent |
| Development | CodeGeneratorAgent, CodeReviewAgent, FullStackDeveloperAgent, DevOpsAgent |
| Sports & Betting | SportsOddsAnalyst, PredictionMarketAnalyst, ArbitrageDetector |
| Analysis & Audit | StockAuditCoordinator, BlockchainAuditCoordinator |
| Specialized | LegalDocDrafterAgent, OpportunityScoringAgent, MeetingCoordinatorAgent |

### 2. Added New Example Workflow

Added explicit example for business plan creation:
```
Example workflow: "Research X company and create a business plan with logo and colors"
1. delegate_to_agent("CompetitorAnalysisAgent", "research X company market, competitors, and positioning")
2. delegate_to_agent("ContentWriterAgent", "write a comprehensive business plan based on [research results]")
3. delegate_to_agent("BrandIdentityAgent", "create brand colors, typography, and visual guidelines")
4. delegate_to_agent("ImageAgent", "create a logo that reflects the brand identity")
5. Return combined business package
```

### 3. Updated PersonalAssistantAgent Routing

**File:** `core/agents/personal_assistant_agent.py`

Expanded workflow patterns in `_detect_agent()` to catch more business creation requests:
- "business plan", "create a business", "write a business plan"
- "business model", "startup plan", "go to market plan"
- "with logo", "with colors", "with branding"
- "full package", "complete branding", "brand and logo"
- "research and write", "analyze and create", "analyze and write"

---

## How Multi-Step Orchestration Works

**Two Paths for Multi-Agent Workflows:**

### Path A: WorkflowAgent (Direct Delegation)
```
User → PersonalAssistant → WorkflowAgent → delegate_to_agent(Agent1, Agent2, ...)
```
- WorkflowAgent uses `delegate_to_agent` tool to call specialists sequentially
- Combines results from each delegation
- Best for explicit "research X and create Y" requests

### Path B: Conversation-Based Orchestration
```
User → PersonalAssistant → ConversationOrchestrator →
    DecisionSummary → ConversationActionDispatcher → Celery Tasks
```
- Two agents debate approach
- Produces DecisionSummary with next_steps
- Tasks dispatched via Celery
- Best for complex decisions needing discussion

---

## Testing

```bash
# Test multi-step workflow routing
python manage.py shell -c "
from core.agents.personal_assistant_agent import PersonalAssistantAgent
pa = PersonalAssistantAgent()
test_tasks = [
    'Research Tesla and create a business plan',
    'Create a brand package with logo and colors',
    'Analyze the market and write a strategy document',
]
for task in test_tasks:
    agent = pa._detect_agent(task)
    print(f'{task[:50]:50} -> {agent}')
"

# Verify WorkflowAgent can delegate
python manage.py shell -c "
from core.agents.workflow_agent import WorkflowAgent
agents = WorkflowAgent.tools[0]['function']['parameters']['properties']['agent_name']['enum']
print(f'WorkflowAgent can delegate to {len(agents)} agents:')
for agent in sorted(agents):
    print(f'  - {agent}')
"
```

---

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/workflow_agent.py` | Expanded delegate_to_agent enum (20→36 agents), updated system_prompt, added business plan workflow example |
| `core/agents/personal_assistant_agent.py` | Added more workflow patterns for business creation |

---

## Impact

| Metric | Before | After |
|--------|--------|-------|
| WorkflowAgent delegation options | 20 agents | 36 agents |
| Business plan creation support | Broken | Working |
| Brand package workflows | Limited | Full support |
| Cross-agent orchestration | Missing key agents | Complete |

---

## Example Workflows Now Supported

1. **"Research X company and create a business plan"**
   - CompetitorAnalysisAgent → ContentWriterAgent

2. **"Create a brand package with logo, colors, and style guide"**
   - BrandIdentityAgent → ImageAgent

3. **"Analyze market trends and write a strategy document"**
   - TrendAnalysisAgent → ContentWriterAgent

4. **"Research competitors and create a pitch deck"**
   - CompetitorAnalysisAgent → ContentWriterAgent → ImageAgent

5. **"Build a complete startup package with business model, branding, and marketing plan"**
   - ResearchAgent → CompetitorAnalysisAgent → ContentWriterAgent → BrandIdentityAgent → ImageAgent → ContentStrategyAgent

---

**Session 892 Complete. WorkflowAgent can now orchestrate 36 agents for complex multi-step workflows.**
