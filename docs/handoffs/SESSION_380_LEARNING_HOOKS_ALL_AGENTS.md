# Session 380: Learning Hooks Added to All Agents

## Summary
Added learning hooks (`_record_learning_outcome()` and `_create_execution_memory()`) to all 12 agents that were missing them. Now all 21 agents (9 with execution history + 12 newly connected) participate in the collective learning system.

## Agents Updated

### Strategy Agents (4)
1. **BrandIdentityAgent** - Brand colors, styles, consistency
2. **ContentStrategyAgent** - Content recommendations from trends
3. **SEOOptimizerAgent** - Hashtags, metadata, keywords
4. **SocialMediaAgent** - Platform-specific content strategy

### Executive Agents (4)
5. **COOAgent** - Operations planning and risk analysis
6. **CTOAgent** - Technical planning and analysis
7. **CreativeDirectorAgent** - Creative guidance and prompt enhancement
8. **MeetingCoordinatorAgent** - Coordinates meetings between agents

### Analysis Agents (2)
9. **OpportunityScoringAgent** - Opportunity scoring engine
10. **TrendAnalysisAgent** - Spider intelligence analysis

### Training Agents (2)
11. **CharacterTrainingAgent** - FLUX LoRA character training
12. **TrainedCreationAgent** - LoRA image generation

## Pattern Applied

Each agent's `execute()` method was updated to:

1. **Store result in variable** instead of returning directly
2. **Call learning hooks** before returning:
   ```python
   # Session 380: Learning hooks for collective intelligence
   self._record_learning_outcome(
       result=result,
       task=task,
       context=context,
       spider_data_used=bool(spider_context),
       scifi_context_used=bool(scifi_context)
   )
   self._create_execution_memory(
       result=result,
       task=task,
       memory_type="success",  # or "failure" for error paths
       importance=0.7  # 0.6 for conversations, 0.8 for failures
   )
   ```
3. **Return result** after recording

### Files Modified
- `core/agents/strategy/brand_identity_agent.py`
- `core/agents/strategy/content_strategy_agent.py`
- `core/agents/strategy/seo_optimizer_agent.py`
- `core/agents/strategy/social_media_agent.py`
- `core/agents/executive/coo_agent.py`
- `core/agents/executive/cto_agent.py`
- `core/agents/executive/creative_director_agent.py`
- `core/agents/executive/meeting_coordinator_agent.py`
- `core/agents/analysis/opportunity_scoring_agent.py`
- `core/agents/analysis/trend_analysis_agent.py`
- `core/agents/training/character_training_agent.py`
- `core/agents/training/trained_creation_agent.py`

## Importance Values Used

| Outcome Type | Importance | Reasoning |
|--------------|------------|-----------|
| Tool call success | 0.7 | Standard successful operations |
| Conversation success | 0.6 | Less critical but still valuable |
| Failure/Error | 0.8 | Important to learn from failures |

## Result

**Before Session 380:**
- 9 agents with execution history (learning connected)
- 12 agents with code but NO learning hooks
- 8 agents without code implementations

**After Session 380:**
- 21 agents now connected to learning system
- All core/agents implementations now participate in collective intelligence
- Agents record outcomes to `CoordinatorOutcome` table
- Agents create execution memories for future context

## Verification

```bash
# All imports work
.venv/bin/python -c "
from core.agents.strategy.brand_identity_agent import BrandIdentityAgent
from core.agents.executive.coo_agent import COOAgent
# ... etc
print('All agents imported successfully!')
"

# BaseAgent has learning methods
.venv/bin/python -c "
from core.agents.base_agent import BaseAgent
print(f'Has _record_learning_outcome: {hasattr(BaseAgent, \"_record_learning_outcome\")}')
print(f'Has _create_execution_memory: {hasattr(BaseAgent, \"_create_execution_memory\")}')
"
```

## Next Steps

1. **Monitor Learning Data** - Run some agent executions and verify data appears in CoordinatorOutcome table
2. **Consider remaining 8 agents** - These don't have code implementations:
   - PersonalAssistantAgent, ImageEditingAgent, VideoEditingAgent, MemoryIsolationAgent
   - CompetitorAnalysisAgent, CustomerResearchAgent (in business/)
   - ResearchAgent, WorkflowAgent

   Some may already have learning via different code paths (views, legacy agents)

3. **Update Agent model counters** - The learning_loop.py now updates Agent.total_executions via _update_agent_execution_counts()
