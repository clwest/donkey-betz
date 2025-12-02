# Session 309: Test Learning Infrastructure

**Date:** December 1, 2025
**Previous Session:** 308 - Wired 5 high-value deprecated agents with learning hooks
**Branch:** `feature/session-52-ai-assistant`

---

## Context

Sessions 305-308 wired **14 deprecated agents** with learning infrastructure:
- Learning Loop integration (`_record_learning_outcome`)
- Memory creation (`_create_execution_memory`)
- Knowledge sharing (`_share_knowledge`)
- Knowledge retrieval (`_get_shared_knowledge`)

**Session 308 specifically wired these 5 high-value agents:**
- BrandIdentityAgent - Color palette and style pattern learning
- SEOOptimizerAgent - Hashtag and platform optimization learning
- TrendAnalysisAgent - Trend and opportunity pattern learning
- ContentStrategyAgent - Content recommendation learning
- SocialMediaAgent - Platform-specific content learning

**Now we need to verify it all works!**

---

## Session 309 Goals

### 1. Test Knowledge Flow Between Agents

Verify agents can share and retrieve knowledge from each other:

```python
# Example test flow:
from agents._deprecated.brand_identity_agent import BrandIdentityAgent
from agents._deprecated.seo_optimizer_agent import SEOOptimizerAgent

# Brand agent shares color palette knowledge
brand = BrandIdentityAgent()
brand.set_brand_colors(primary='#FF5733')

# SEO agent retrieves brand knowledge
seo = SEOOptimizerAgent()
shared = seo._get_shared_knowledge(title_contains='Brand colors')
# Should return the color palette shared by BrandIdentityAgent
```

### 2. Monitor Memory Creation

Check that agent executions create memories in the database:

```python
from core.models_unified_system import AgentMemory

# Before running agent
before_count = AgentMemory.objects.count()

# Run an agent
from agents._deprecated.trend_analysis_agent import TrendAnalysisAgent
agent = TrendAnalysisAgent()
agent.generate_daily_briefing()

# After running agent
after_count = AgentMemory.objects.count()
# Should have increased
```

### 3. Verify Learning Loop Recording

Check execution outcomes are recorded:

```python
from core.models_unified_system import ExecutionOutcome  # or similar model

# Run agent and check if outcome was recorded
```

### 4. Test Cross-Agent Knowledge Sharing

Create a test that exercises the full loop:
1. TrendAnalysisAgent finds trends → shares as knowledge
2. ContentStrategyAgent reads trend knowledge → makes recommendations
3. SocialMediaAgent reads content recommendations → creates calendar
4. SEOOptimizerAgent optimizes content → shares hashtag patterns
5. BrandIdentityAgent applies consistent styling

---

## Quick Test Commands

```bash
# Start the platform
make start
make celery

# Run a quick Django shell test
.venv/bin/python manage.py shell
```

```python
# In Django shell:
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

# Test 1: Agent imports work
from agents._deprecated.brand_identity_agent import BrandIdentityAgent
from agents._deprecated.seo_optimizer_agent import SEOOptimizerAgent
from agents._deprecated.trend_analysis_agent import TrendAnalysisAgent
from agents._deprecated.content_strategy_agent import ContentStrategyAgent
from agents._deprecated.social_media_agent import SocialMediaAgent
print("All 5 agents imported successfully!")

# Test 2: Knowledge sharing works
brand = BrandIdentityAgent()
result = brand.set_brand_colors(primary='#3498DB', secondary='#2ECC71')
print(f"Brand colors set: {result['success']}")

# Test 3: Check if AgentKnowledgeSource was created
from core.models_unified_system import AgentKnowledgeSource
knowledge = AgentKnowledgeSource.objects.filter(agent__name='BrandIdentityAgent').first()
print(f"Knowledge shared: {knowledge.title if knowledge else 'None'}")

# Test 4: Cross-agent retrieval
seo = SEOOptimizerAgent()
shared = seo._get_shared_knowledge(from_agents=['BrandIdentityAgent'])
print(f"Retrieved {len(shared)} knowledge items from BrandIdentityAgent")
```

---

## Files to Review

| File | Purpose |
|------|---------|
| `docs/handoffs/SESSION_308_HIGH_VALUE_AGENT_LEARNING_EXPANSION.md` | Details of what was wired |
| `docs/DEPRECATED_AGENTS_INVENTORY.md` | Status of all 18 deprecated agents |
| `agents/_deprecated/brand_identity_agent.py` | Example of wired agent |
| `core/models_unified_system.py` | Database models for Agent, AgentKnowledgeSource, AgentMemory |

---

## Potential Issues to Watch For

1. **Agent model not created** - First run should auto-create Agent records
2. **Memory service unavailable** - Check if MemoryEmbeddingService is properly initialized
3. **Learning loop not connected** - Verify LearningLoopService is available
4. **Knowledge not persisting** - Check database connections

---

## Success Criteria

- [ ] All 5 agents create Agent records in database on first use
- [ ] Knowledge sharing creates AgentKnowledgeSource records
- [ ] Memory creation works (AgentMemory records created)
- [ ] Cross-agent knowledge retrieval returns shared data
- [ ] Learning outcomes are recorded (if LearningLoopService available)

---

## Commands Reference

```bash
# Check Agent records
.venv/bin/python manage.py shell -c "
from core.models_unified_system import Agent
print('Agents:', list(Agent.objects.filter(agent_type='deprecated').values_list('name', flat=True)))
"

# Check Knowledge records
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentKnowledgeSource
for k in AgentKnowledgeSource.objects.all()[:10]:
    print(f'{k.agent.name}: {k.title} ({k.knowledge_type})')
"

# Check Memory records
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentMemory
print(f'Total memories: {AgentMemory.objects.count()}')
"
```

---

## Platform Stats (Post-Session 308)

```
CODEBASE HEALTH
├── Frontend: 22,605 lines (60% smaller)
├── Spiders: 74/74 working (100%)
├── Agents: 11 clean + 22 legacy (24 in router)
├── Tests: 83 agent tests passing
├── Spider Data: 3,017 entries
├── Database Audit: COMPLETE
├── Unified Intelligence: COMPLETE
├── Agent Audit: COMPLETE
├── Learning Infrastructure: FULLY OPERATIONAL! ✅
│   ├── Clean Agents (11): ALL CONNECTED
│   ├── Legacy Agents (BaseContentAgent): WorkflowOrchestrationAgent CONNECTED
│   ├── Standalone Agents (3): BookmakerAgent, CreationAgent, OPO CONNECTED
│   ├── Deprecated Agents (14/18): CONNECTED ✅
│   │   ├── Session 305: AudioAgent
│   │   ├── Session 306: PromptEngineering, CTO, COO, Meeting, Character, Trained, Memory, Creative
│   │   ├── Session 307: OpportunityScoring
│   │   └── Session 308: BrandIdentity, SEO, Trend, ContentStrategy, SocialMedia ✅
│   ├── Remaining 4: Have clean replacements (Image, Video, Research, 3D)
│   ├── AgentKnowledgeSource: 6+ records
│   └── AgentMemory: 3+ records
├── AudioHistory Model: CREATED & INTEGRATED!
├── Workflow Engine: FULLY WORKING!
├── DaVinci Bridge: FULLY WORKING!
└── Direct API: Create Project bypasses GPT (instant!)
```

---

## Services Status

| Service | Port | Command |
|---------|------|---------|
| Django/Daphne | 8000 | `make start` |
| Redis | 6379 | (started by make start) |
| Celery Worker | - | `make celery` |
| Celery Beat | - | `make celery` |
| DaVinci Bridge | 9090 | `make davinci-bridge` |

---

**Read `CLAUDE.md` for full system context, then test the learning infrastructure!**
