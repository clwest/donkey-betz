# Unified Prompting System 🎯

A comprehensive prompt management system that unifies prompts across Assistant → Agents → Memory → Embeddings → UKF → Knowledge Base → Learning Intelligence → Mythology detection.

**Status**: FULLY IMPLEMENTED ✅  
**Integration**: Complete with all major systems  
**Last Updated**: July 17, 2025

## Overview

The Unified Prompting System is a centralized framework for managing, optimizing, and evolving prompts across the entire Donkey Betz platform. It provides:

- **Dynamic Prompt Composition** - Assembles prompts from reusable components
- **Context Enhancement** - Integrates Memory Palace, UKF, and user data
- **Mythology Prevention** - Detects and prevents AI folklore patterns
- **Learning & Evolution** - Prompts improve based on performance data
- **Agent Optimization** - Each agent gets personalized, optimized prompts

## Key Features

### 1. Dynamic Prompt Composition
- Component-based architecture for reusability
- Context-aware assembly based on task requirements
- Conditional component inclusion
- Template versioning with rollback capability

### 2. Context Integration
- **Memory Palace**: Injects relevant conversation history
- **UKF System**: Adds knowledge from 2,200 documents
- **Agent Profiles**: Considers agent performance and preferences
- **User Context**: Personalizes based on user profile

### 3. Mythology Detection & Prevention
- Real-time pattern detection (numeric inflation, false authority, etc.)
- Automatic injection of anti-mythology instructions
- Response validation with correction suggestions
- Tracks mythology incidents per template/agent

### 4. Learning Intelligence
- Tracks every prompt execution
- Analyzes performance metrics (quality, time, tokens)
- Identifies successful patterns
- Suggests and applies optimizations
- Creates evolved prompt versions

### 5. Agent Integration
- Seamless integration with 25 existing agents
- Backward compatible through prompting bridge
- Agent-specific prompt profiles
- Performance tracking per agent

## Installation

The system is already integrated into the Django project:

```python
# In settings.py
INSTALLED_APPS = [
    ...
    'prompting_system',
]

# In urls.py
urlpatterns = [
    ...
    path("api/prompting/", include("prompting_system.urls")),
]
```

Initialize the system:
```bash
python manage.py initialize_prompting_system --migrate-agents
```

## Usage

### Basic Prompt Composition

```python
from prompting_system.services.prompt_composer import DynamicPromptComposer

composer = DynamicPromptComposer()
result = composer.compose_prompt(
    template_name='research_agent_prompt',
    context={
        'task': 'Analyze market trends for AI assistants',
        'needs_memory': True,
        'needs_knowledge': True
    },
    user_id=user.id,
    agent_id=agent.id
)

# Result contains:
# - prompt: The composed prompt with all enhancements
# - mythology_risk: Risk score (0-1)
# - components_used: List of components applied
# - execution_id: For tracking
```

### Agent Integration

```python
from prompting_system.services.agent_integration import AgentPromptIntegration

integration = AgentPromptIntegration()
result = integration.get_agent_prompt(
    agent_name='Research Agent',
    task='Find competitor analysis for Palantir',
    context={'focus': 'financial_data'},
    user_id=user.id
)
```

### Mythology Validation

```python
from prompting_system.services.mythology_guard import MythologyGuardService

guard = MythologyGuardService()

# Validate prompt before sending
validated = guard.validate_and_guard_prompt(
    prompt="Analyze our 350 deployments",  # Known mythology pattern
    template_id=template.id
)

# Validate response after generation
validation = guard.validate_response(
    response="We have successfully deployed 350 times",
    original_prompt=prompt,
    execution_id=execution.id
)
```

### Using the Bridge (for Agent Orchestra)

```python
from agent_orchestra.prompting_bridge import prompt_bridge

# Get enhanced prompt
enhanced_prompt = prompt_bridge.get_enhanced_prompt(
    agent_name='Business Agent',
    base_prompt=agent.system_prompt_template,
    task='Create financial projections',
    context={'industry': 'SaaS'},
    user_id=user.id
)

# Track execution
prompt_bridge.track_execution(
    agent_name='Business Agent',
    prompt=enhanced_prompt,
    response=agent_response,
    execution_time=15.3,
    success=True,
    user_id=user.id
)
```

## API Endpoints

### Template Management
- `GET /api/prompting/templates/` - List all templates
- `POST /api/prompting/templates/` - Create new template
- `GET /api/prompting/templates/{id}/` - Get specific template
- `POST /api/prompting/templates/{id}/compose/` - Compose using template
- `GET /api/prompting/templates/{id}/performance/` - Get performance metrics
- `POST /api/prompting/templates/{id}/evolve/` - Create evolved version

### Component Management
- `GET /api/prompting/components/` - List all components
- `POST /api/prompting/components/` - Create new component
- `GET /api/prompting/components/by_type/` - Get components by type

### Prompt Operations
- `POST /api/prompting/compose/` - Compose prompt dynamically
- `POST /api/prompting/validate/` - Validate prompt for mythology
- `POST /api/prompting/validate/response/` - Validate response
- `POST /api/prompting/analyze/` - Analyze performance
- `POST /api/prompting/evolve/{id}/` - Evolve specific prompt

### Agent Operations
- `POST /api/prompting/agent/` - Get agent-optimized prompt
- `GET /api/prompting/agent/analytics/` - Get agent analytics

### Analytics & Optimization
- `GET /api/prompting/patterns/` - View discovered patterns
- `POST /api/prompting/patterns/discover/` - Trigger pattern discovery
- `GET /api/prompting/optimizations/` - View suggested optimizations
- `GET /api/prompting/analytics/summary/` - Get system analytics

## Models

### Core Models
- **PromptTemplate** - Base templates with versioning
- **PromptComponent** - Reusable prompt parts
- **ComposedPrompt** - Dynamically composed prompts
- **PromptExecution** - Execution tracking for learning

### Learning Models
- **PromptOptimization** - Suggested improvements
- **PromptPattern** - Discovered successful patterns
- **AgentPromptProfile** - Agent-specific preferences

### Protection Models
- **PromptMythologyGuard** - Mythology prevention rules
- **PromptAnalytics** - Aggregated performance data

## Mythology Patterns Detected

The system actively detects and prevents:

1. **Numeric Inflation** - "350 deployments", "thousands of users"
2. **False Authority** - "Studies show", "Experts confirm"
3. **Context Loss** - Important details lost in summaries
4. **Capability Exaggeration** - "Can do anything", "Perfect accuracy"
5. **Temporal Distortion** - Vague time references

## Learning & Evolution

The system continuously improves prompts by:

1. Tracking execution metrics (quality, time, tokens)
2. Identifying high-performing patterns
3. Suggesting optimizations based on data
4. Creating evolved versions of prompts
5. A/B testing variations (coming soon)

## Integration Status

✅ **Fully Integrated With:**
- Agent Orchestra (25 agents)
- Memory Palace (conversation history)
- UKF System (2,200 documents)
- Learning Intelligence (pattern recognition)
- Mythology Lab (folklore detection)
- Security Framework (PII protection)

## Performance Metrics

Target improvements:
- Prompt quality: +25%
- Mythology incidents: -90%
- Response time: -15%
- Token efficiency: +20%

## Future Enhancements

- [ ] A/B testing framework
- [ ] Real-time prompt adaptation
- [ ] Cross-agent prompt sharing
- [ ] Visual prompt builder UI
- [ ] Automated prompt generation
- [ ] Multi-language support

## Contributing

To add new prompt patterns or mythology guards:

1. Create pattern in `PromptPattern` model
2. Add detection logic in `MythologyGuardService`
3. Update component library
4. Test with various agents
5. Monitor performance metrics

## License

Part of the Donkey Betz platform - see main project license.