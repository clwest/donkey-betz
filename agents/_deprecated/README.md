# Deprecated Agents

**Session 281:** These legacy agents have been migrated to clean architecture.

## DO NOT USE THESE FILES

Import from `core.agents` instead:

```python
# OLD (deprecated):
from agents.image_agent import ImageAgent

# NEW (correct):
from core.agents import ImageAgent
from core.agents.strategy import ContentStrategyAgent
from core.agents.executive import CTOAgent
from core.agents.analysis import TrendAnalysisAgent
from core.agents.training import CharacterTrainingAgent
from core.agents.security import MemoryIsolationAgent
```

## Migration Map

| Legacy File | Clean Location |
|-------------|----------------|
| audio_agent.py | core/agents/audio_agent.py |
| brand_identity_agent.py | core/agents/strategy/brand_identity_agent.py |
| character_training_agent.py | core/agents/training/character_training_agent.py |
| content_strategy_agent.py | core/agents/strategy/content_strategy_agent.py |
| coo_agent.py | core/agents/executive/coo_agent.py |
| creative_director_agent.py | core/agents/executive/creative_director_agent.py |
| cto_agent.py | core/agents/executive/cto_agent.py |
| image_agent.py | core/agents/image_agent.py |
| meeting_coordinator_agent.py | core/agents/executive/meeting_coordinator_agent.py |
| memory_isolation_agent.py | core/agents/security/memory_isolation_agent.py |
| opportunity_scoring_agent.py | core/agents/analysis/opportunity_scoring_agent.py |
| research_agent.py | core/agents/research_agent.py |
| seo_optimizer_agent.py | core/agents/strategy/seo_optimizer_agent.py |
| social_media_agent.py | core/agents/strategy/social_media_agent.py |
| three_d_generation_agent.py | core/agents/three_d_agent.py |
| trained_creation_agent.py | core/agents/training/trained_creation_agent.py |
| trend_analysis_agent.py | core/agents/analysis/trend_analysis_agent.py |
| video_agent.py | core/agents/video_agent.py |

## Why Keep These?

These files are kept for reference only. They will be deleted in a future session after confirming all imports have been migrated.
