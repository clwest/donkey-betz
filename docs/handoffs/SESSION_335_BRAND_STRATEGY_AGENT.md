# Session 335: BrandStrategyAgent - Research-Based Brand Strategy

**Date:** December 3, 2025
**Branch:** `feature/session-52-ai-assistant`

---

## Overview

This session created the **BrandStrategyAgent** - a new business research agent that produces comprehensive brand strategy reports by reading existing project research (competitor analysis, customer research) and synthesizing it into actionable brand recommendations.

This follows the vision: **"All agents should work like CompetitorAnalysisAgent and CustomerResearchAgent - producing rich research reports that build on existing project research."**

---

## Problem Solved

Previously, when a user said "Create a brand identity" from within a project:
- The `brand_identity_package` workflow would just generate logos
- No connection to existing project research
- Output was generic, not strategic
- No rich analysis like the business research agents produce

Now:
- `BrandStrategyAgent` produces comprehensive brand strategy RESEARCH
- Reads existing competitor and customer research from the project
- Synthesizes findings into positioning, messaging, visual direction
- Saves to `BusinessResearchResult` for project learning
- Users can THEN use ImageAgent for visual assets based on the strategy

---

## Implementation Details

### New Agent: `BrandStrategyAgent`

Location: `core/agents/business/brand_strategy_agent.py`

**Tools Available:**
1. `get_project_research` - Fetches existing competitor/customer research from project
2. `spider_query` - Searches spider network for brand-related trends
3. `web_search` - Searches web for brand best practices
4. `synthesize_brand_strategy` - Creates the comprehensive brand strategy report

**Output Sections:**
1. **Brand Positioning** - Market position, differentiation strategy
2. **Target Audience Summary** - Synthesized from customer research
3. **Brand Messaging Framework** - Taglines, value propositions, key messages
4. **Visual Direction** - Colors, typography, imagery guidance
5. **Competitive Differentiation** - How to stand out from competitors
6. **Actionable Next Steps** - Specific recommendations

### Tool Definition

Location: `core/assistant/tool_definitions.py:713-745`

```python
def _get_brand_strategy_agent_definition() -> Dict:
    return {
        "type": "function",
        "name": "brand_strategy_agent",
        "parameters": {
            "properties": {
                "project_id": {"type": "string", "description": "REQUIRED: Project ID to read existing research from"},
                "brand_name": {"type": "string", "description": "Optional brand name"},
                "focus_areas": {"type": "array", "description": "Optional focus areas"},
                "user_context": {"type": "string", "description": "Additional context"}
            },
            "required": ["project_id"]
        }
    }
```

### Handler Method

Location: `core/personal_ai_assistant_enhanced.py:3471-3578`

```python
def _handle_brand_strategy_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    # Imports BrandStrategyAgent
    # Gets project context
    # Executes agent with task and context
    # Returns structured response for frontend
```

### Routing

Location: `core/views_image.py:7905-7912`

```python
elif tool_name == 'brand_strategy_agent':
    from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
    assistant = EnhancedPersonalAIAssistant(user=request.user)
    if project:
        assistant.project = project
        parameters['project_id'] = str(project.id)
    result = assistant._handle_brand_strategy_agent(parameters)
```

---

## Testing

### Prerequisites
1. A project with existing research (e.g., "Donkey Betz Podcast" with competitor + customer research)

### Steps
1. Go to http://localhost:8000/ai-studio/
2. Click on a project with research
3. In the project assistant, say "Create a brand strategy" or "What should our brand positioning be?"
4. Watch for comprehensive brand strategy report with 6 sections

### Verification Script
```python
from core.agents.business import BrandStrategyAgent
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

agent = BrandStrategyAgent(user=user)
result = agent.execute(
    task="Create brand strategy for Donkey Betz Podcast",
    context={'project_id': '27ebd338-8fa3-415e-a87a-fe95a068f8d5'},
    scifi_context={},
    spider_context={}
)

print(f'Success: {result.success}')
print(f'Message: {result.message[:200]}...')
```

---

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/business/brand_strategy_agent.py` | **NEW** - Complete BrandStrategyAgent implementation (~500 lines) |
| `core/agents/business/__init__.py` | Added BrandStrategyAgent export |
| `core/assistant/tool_definitions.py` | Added `_get_brand_strategy_agent_definition()` function |
| `core/prompts/tool_descriptions.py` | Added `brand_strategy_agent` description |
| `core/personal_ai_assistant_enhanced.py` | Added `_handle_brand_strategy_agent()` method |
| `core/views_image.py` | Added routing for `brand_strategy_agent` tool |

---

## Key Principle

**"Agents produce research that builds on existing project research"**

This is the vision for a "true self-learning project" where:
1. CompetitorAnalysisAgent produces market intelligence
2. CustomerResearchAgent produces persona and pain point analysis
3. **BrandStrategyAgent** synthesizes both into brand strategy
4. ImageAgent/VideoAgent can then create visuals based on the strategy

Each agent contributes research that enhances the project's collective intelligence.

---

## Next Steps

1. **Test the agent** - Verify brand strategy flow works within projects
2. **Apply pattern to more agents** - ContentStrategyAgent, SEOOptimizerAgent could follow same pattern
3. **Frontend enhancements** - Add "+ Create Brand Strategy" button after competitor/customer research
4. **Action buttons** - Add "Generate Logos from Strategy" button in brand strategy output

---

## Architecture Pattern

```
User Request: "Create a brand identity"
         ↓
BrandStrategyAgent (Session 335)
         ↓
    ┌────────────────┐
    │ get_project_research │ → Reads existing research
    └────────────────┘
         ↓
    ┌────────────────┐
    │ spider_query   │ → Gets brand trends from spider network
    └────────────────┘
         ↓
    ┌────────────────┐
    │ web_search     │ → Gets best practices from web
    └────────────────┘
         ↓
    ┌────────────────┐
    │ synthesize_brand_strategy │ → GPT synthesizes comprehensive report
    └────────────────┘
         ↓
    BusinessResearchResult (saved to project)
         ↓
    Rich brand strategy report displayed to user
```

---

**Status:** Session 335 COMPLETE. BrandStrategyAgent ready for testing!
